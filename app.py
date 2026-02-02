import os
import json
from datetime import datetime, timezone

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

from pymongo import MongoClient
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

# -----------------------------
# Config
# -----------------------------
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
MONGODB_URI = os.getenv("MONGODB_URI", "").strip()
MONGODB_DB = os.getenv("MONGODB_DB", "reservas_punto_as").strip()
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "reservas").strip()

if not DEEPSEEK_API_KEY:
    raise RuntimeError("Falta DEEPSEEK_API_KEY en el .env")

if not MONGODB_URI:
    raise RuntimeError("Falta MONGODB_URI en el .env")

# DeepSeek client (OpenAI-compatible)
deepseek_client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# Mongo client
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client[MONGODB_DB]
reservas_col = db[MONGODB_COLLECTION]

# -----------------------------
# Helpers
# -----------------------------
def now_utc():
    return datetime.now(timezone.utc)

def normalize(text: str) -> str:
    return (text or "").strip()

def menu_text():
    return (
        "Bot Punto AS - Reservas\n\n"
        "Responde con una opción:\n"
        "1) Hacer una reserva\n"
        "2) Ver información\n"
        "3) Ayuda\n\n"
        "Escribe 0 para reiniciar."
    )

def info_text():
    return (
        "Información - Reserva de Canchas - PUNTO AS - Manta\n\n"
        "Canchas disponibles:\n"
        "A) Básquet 3x3\n"
        "B) Ecuavóley/Vóley sala\n\n"
        "Ubicación: Debajo del Puente (Zona Deportiva)\n\n"
        "Para reservar, escribe 1.\n"
        "Para volver al menú, escribe 0."
    )

def ayuda_text():
    return (
        "Ayuda:\n"
        "Este bot te ayuda a reservar canchas del Punto AS.\n\n"
        "Cómo reservar:\n"
        "1) Escribe 1 (reservar)\n"
        "2) Di tus datos cuando te los pida\n"
        "3) Al final confirma con 1 o cancela con 2\n\n"
        "Escribe 0 para reiniciar."
    )

# -----------------------------
# Mongo Session (persistente)
# -----------------------------
def get_session(user_id: str) -> dict:
    sess = db["sessions"].find_one({"_id": user_id})
    if not sess:
        sess = {"_id": user_id, "state": "MENU", "data": {}, "updated_at": now_utc()}
        db["sessions"].insert_one(sess)
    return sess

def save_session(user_id: str, state: str, data: dict):
    db["sessions"].update_one(
        {"_id": user_id},
        {"$set": {"state": state, "data": data, "updated_at": now_utc()}},
        upsert=True
    )

def reset_session(user_id: str):
    save_session(user_id, "MENU", {})

# -----------------------------
# AI: Extract reservation fields
# -----------------------------
AI_SYSTEM = """Eres un asistente de WhatsApp para reservas de canchas del Punto AS (Manta, Ecuador).
Tu tarea es ayudar a completar una reserva con los campos:
- nombre (string)
- cedula (string)
- telefono (string)
- cancha (string: "Básquet 3x3" o "Ecuavóley/Vóley sala")
- fecha (string en DD/MM/AAAA)
- hora (string, ejemplo "16h00-18h00")

Reglas:
1) Haz preguntas de una en una, de forma clara y corta.
2) Si el usuario da datos, extrae y completa campos.
3) Nunca inventes datos.
4) Cuando falten campos, pide el siguiente que falte.
5) Cuando estén todos los campos, muestra un resumen y pide confirmación:
   "Responde 1 para confirmar o 2 para cancelar".
6) Si el usuario pide info o ayuda, responde con información/ayuda.

IMPORTANTE: Siempre responde en JSON válido, sin texto extra.

Formato JSON:
{
  "intent": "reserve" | "info" | "help" | "menu" | "other",
  "reply": "texto para enviar al usuario",
  "fields": {
    "nombre": null|string,
    "cedula": null|string,
    "telefono": null|string,
    "cancha": null|string,
    "fecha": null|string,
    "hora": null|string
  },
  "ready_to_confirm": true|false
}
"""

def ai_next_message(user_text: str, current_state: str, current_data: dict) -> dict:
    # Mandamos el contexto actual al modelo para que continúe bien.
    user_payload = {
        "user_message": user_text,
        "current_state": current_state,
        "current_data": current_data
    }

    r = deepseek_client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": AI_SYSTEM},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
        ],
        temperature=0.3
    )

    content = (r.choices[0].message.content or "").strip()

    # A veces algunos modelos devuelven ```json ...```, lo limpiamos.
    if content.startswith("```"):
        content = content.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Fallback ultra seguro: si no devolvió JSON, respondemos con menú
        return {
            "intent": "menu",
            "reply": "Hubo un problema interpretando tu mensaje.\n\n" + menu_text(),
            "fields": {
                "nombre": None, "cedula": None, "telefono": None,
                "cancha": None, "fecha": None, "hora": None
            },
            "ready_to_confirm": False
        }

def merge_fields(existing: dict, new_fields: dict) -> dict:
    # No sobreescribimos con None / vacío
    merged = dict(existing or {})
    for k, v in (new_fields or {}).items():
        if v is None:
            continue
        v2 = str(v).strip()
        if v2:
            merged[k] = v2
    return merged

def is_complete(data: dict) -> bool:
    needed = ["nombre", "cedula", "telefono", "cancha", "fecha", "hora"]
    return all(str(data.get(k, "")).strip() for k in needed)

def reservation_summary(data: dict) -> str:
    return (
        "Confirma tu reserva:\n\n"
        f"Nombre: {data.get('nombre','')}\n"
        f"Cédula: {data.get('cedula','')}\n"
        f"Teléfono: {data.get('telefono','')}\n"
        f"Cancha: {data.get('cancha','')}\n"
        f"Fecha: {data.get('fecha','')}\n"
        f"Horario: {data.get('hora','')}\n\n"
        "Responde:\n"
        "1) Confirmar\n"
        "2) Cancelar\n\n"
        "Escribe 0 para reiniciar."
    )

def save_reserva_to_mongo(user_id: str, data: dict):
    doc = {
        "user_id": user_id,
        "nombre": data.get("nombre"),
        "cedula": data.get("cedula"),
        "telefono": data.get("telefono"),
        "cancha": data.get("cancha"),
        "fecha": data.get("fecha"),
        "hora": data.get("hora"),
        "created_at": now_utc()
    }
    reservas_col.insert_one(doc)

# -----------------------------
# Webhook
# -----------------------------
@app.post("/webhook")
def whatsapp_webhook():
    incoming_msg = normalize(request.values.get("Body"))
    user_id = normalize(request.values.get("From"))  # whatsapp:+593...

    resp = MessagingResponse()
    msg = resp.message()

    # Reset universal
    if incoming_msg == "0":
        reset_session(user_id)
        msg.body("Listo, reinicié el chat.\n\n" + menu_text())
        return str(resp)

    session = get_session(user_id)
    state = session.get("state", "MENU")
    data = session.get("data", {}) or {}

    # Si estamos en confirmación, manejamos 1/2 nosotros (sin IA)
    if state == "CONFIRM":
        if incoming_msg == "1":
            if is_complete(data):
                save_reserva_to_mongo(user_id, data)
                reset_session(user_id)
                msg.body("Reserva registrada.\n\n" + menu_text())
            else:
                # Si por alguna razón no está completo, volvemos a IA
                save_session(user_id, "CHAT", data)
                msg.body("Me falta información para confirmar.\nDime nuevamente los datos faltantes.")
        elif incoming_msg == "2":
            reset_session(user_id)
            msg.body("Reserva cancelada.\n\n" + menu_text())
        else:
            msg.body("Opción inválida. Responde 1 (Confirmar) o 2 (Cancelar).")
        return str(resp)

    # Atajos tipo menú (sin IA) para que sea más usable
    if incoming_msg in ["1", "reservar", "reserva"]:
        state = "CHAT"
        save_session(user_id, state, data)

    if incoming_msg in ["2", "info", "informacion", "información"]:
        msg.body(info_text())
        return str(resp)

    if incoming_msg in ["3", "ayuda", "help"]:
        msg.body(ayuda_text())
        return str(resp)

    if state == "MENU":
        # Si escribe cualquier cosa, lo atendemos con IA (más natural)
        state = "CHAT"
        save_session(user_id, state, data)

    # IA: decide siguiente mensaje y extrae campos
    ai = ai_next_message(incoming_msg, state, data)

    # Merge de campos extraídos por la IA con lo que ya tenemos
    data = merge_fields(data, ai.get("fields", {}))

    # Si ya está completo, forzamos confirmación
    if is_complete(data):
        save_session(user_id, "CONFIRM", data)
        msg.body(reservation_summary(data))
        return str(resp)

    # Si la IA dice listo para confirmar, igual validamos
    if ai.get("ready_to_confirm") is True and is_complete(data):
        save_session(user_id, "CONFIRM", data)
        msg.body(reservation_summary(data))
        return str(resp)

    # Caso normal: seguimos en chat
    save_session(user_id, "CHAT", data)
    reply = ai.get("reply") or "No entendí. " + menu_text()
    msg.body(reply)
    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
