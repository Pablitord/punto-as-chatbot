import os
from datetime import datetime
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

# Estados por usuario (para examen está bien en memoria)
# key = wa_id (número del usuario), value = {"state": "...", "data": {...}}
SESSIONS = {}

# Estados
STATE_MENU = "MENU"
STATE_NAME = "NAME"
STATE_CEDULA = "CEDULA"
STATE_PHONE = "PHONE"
STATE_CANCHA = "CANCHA"
STATE_FECHA = "FECHA"
STATE_HORA = "HORA"
STATE_CONFIRM = "CONFIRM"

def menu_text():
    return (
        "🏟️ *Bot Punto AS - Reservas*\n"
        "\nResponde con una opción:\n\n"
        "*1)* Hacer una reserva 📆\n"
        "*2)* Ver información ℹ️ \n"
        "*3)* Ayuda ❓\n\n"
        "Escribe 0 para reiniciar."
    )

def info_text():
    return (
        "ℹ️ *Información - Reseva de Canchas - PUNTO AS - Manta*\n"
        "- *Canchas disponibles:*\n"
        "\n *A*) Básquet 3x3 🏀\n"
        " *B*) Ecuavóley/Vóley sala 🏐\n\n"
        "📍 *Ubicación: Debajo del Puente (Zona Deportiva)*\n\n"
        "Para reservar, *escribe 1*.\n"
        "Para volver al menú, *escribe 0*."
    )

def ayuda_text():
    return (
        "❓ *Ayuda:*\n"
        "*Este bot te ayuda a reservar las canchas del Punto AS*\n\n"
        "*1)* Elige 1 para hacer una reserva.\n"
        "*2)* Responde cada pregunta.\n"
        "*3)* Confirma al final.\n\n"
        "Puedes escribir *0* en cualquier momento para reiniciar."
    )

def normalize(text: str) -> str:
    return (text or "").strip()

def get_session(user_id: str):
    if user_id not in SESSIONS:
        SESSIONS[user_id] = {"state": STATE_MENU, "data": {}}
    return SESSIONS[user_id]

def reset_session(user_id: str):
    SESSIONS[user_id] = {"state": STATE_MENU, "data": {}}

def save_reserva(data: dict):
    # Registro simple en archivo (para evidencia)
    line = (
        f"{datetime.now().isoformat(timespec='seconds')} | "
        f"{data.get('nombre','')} | {data.get('cedula','')} | {data.get('telefono','')} | "
        f"{data.get('cancha','')} | {data.get('fecha','')} | {data.get('hora','')}\n"
    )
    with open("reservas_punto_as.txt", "a", encoding="utf-8") as f:
        f.write(line)

@app.post("/webhook")
def whatsapp_webhook():
    incoming_msg = normalize(request.values.get("Body"))
    user_id = normalize(request.values.get("From"))  # ej: whatsapp:+593...
    resp = MessagingResponse()
    msg = resp.message()

    # Seguridad UX: reinicio universal
    if incoming_msg == "0":
        reset_session(user_id)
        msg.body("Listo, reinicié el chat.\n\n" + menu_text())
        return str(resp)

    session = get_session(user_id)
    state = session["state"]
    data = session["data"]

    # Si el usuario escribe "hola" o algo al inicio, lo llevamos al menú
    if state == STATE_MENU:
        if incoming_msg in ["1", "reservar", "reserva"]:
            session["state"] = STATE_NAME
            msg.body("Perfecto. Escribe tu *nombre completo*:")
        elif incoming_msg in ["2", "info", "informacion", "información"]:
            msg.body(info_text())
        elif incoming_msg in ["3", "ayuda", "help"]:
            msg.body(ayuda_text())
        else:
            msg.body("No entendí, Ingresa de Nuevo la opción\n\n" + menu_text())
        return str(resp)

    if state == STATE_NAME:
        if len(incoming_msg) < 3:
            msg.body("Tu nombre parece muy corto.\n\nEscribe tu *nombre completo*:")
            return str(resp)
        data["nombre"] = incoming_msg
        session["state"] = STATE_CEDULA
        msg.body("Escribe tu *cédula*:")
        return str(resp)

    if state == STATE_CEDULA:
        # Validación simple (solo longitud y dígitos)
        ced = incoming_msg.replace("-", "").replace(" ", "")
        if not ced.isdigit() or len(ced) < 8:
            msg.body("Cédula inválida.\n\n Escribe solo números (ej: 1234567890):")
            return str(resp)
        data["cedula"] = ced
        session["state"] = STATE_PHONE
        msg.body("Escribe tu *número de teléfono* (ej: 0999999999):")
        return str(resp)

    if state == STATE_PHONE:
        tel = incoming_msg.replace(" ", "").replace("-", "")
        if not tel.isdigit() or len(tel) < 8:
            msg.body("Teléfono inválido.\n\n Escribe solo números (ej: 0999999999):")
            return str(resp)
        data["telefono"] = tel
        session["state"] = STATE_CANCHA
        msg.body(
            "Selecciona la cancha:\n\n"
            "*A)* Básquet 3x3 🏀\n"
            "*B)* Ecuavóley/Vóley sala 🏐\n\n"
            "Responde con *A o B.*"
        )
        return str(resp)

    if state == STATE_CANCHA:
        opt = incoming_msg.lower()
        if opt in ["a", "basquet", "basket", "básquet"]:
            data["cancha"] = "Básquet 3x3"
        elif opt in ["b", "ecuavoley", "ecuavóley", "voley", "vóley"]:
            data["cancha"] = "Ecuavóley/Vóley sala"
        else:
            msg.body("Opción inválida. Responde con *A o B.*")
            return str(resp)

        session["state"] = STATE_FECHA
        msg.body("Ingresa la *fecha* (DD/MM/AAAA):")
        return str(resp)

    if state == STATE_FECHA:
        # Validación mínima de formato
        parts = incoming_msg.split("/")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            msg.body("Formato inválido.\n\n Usa *DD/MM/AAAA* (ej: 25/12/2025):")
            return str(resp)
        data["fecha"] = incoming_msg
        session["state"] = STATE_HORA
        msg.body("Ingresa el *horario* (ej: 16h00-18h00):")
        return str(resp)

    if state == STATE_HORA:
        if len(incoming_msg) < 3:
            msg.body("Horario inválido. Ejemplo: 16h00-18h00")
            return str(resp)
        data["hora"] = incoming_msg
        session["state"] = STATE_CONFIRM

        resumen = (
            "*Confirma tu reserva:* 📆\n\n"
            f"*Nombre:* {data['nombre']}\n"
            f"*Cédula:* {data['cedula']}\n"
            f"*Teléfono:* {data['telefono']}\n"
            f"*Cancha:* {data['cancha']}\n"
            f"*Fecha:* {data['fecha']}\n"
            f"*Horario:* {data['hora']}\n\n"
            "Responde:\n"
            "*1)* Confirmar\n"
            "*2)* Cancelar\n\n"
            "Escribe *0* para reiniciar."
        )
        msg.body(resumen)
        return str(resp)

    if state == STATE_CONFIRM:
        if incoming_msg == "1":
            save_reserva(data)
            reset_session(user_id)
            msg.body(
                "Reserva registrada. ✔️\n"
                "Gracias. Si quieres hacer otra reserva, escribe 1.\n\n" + menu_text()
            )
        elif incoming_msg == "2":
            reset_session(user_id)
            msg.body("Reserva cancelada. ❌\n\n" + menu_text())
        else:
            msg.body("Opción inválida. Responde 1 (Confirmar) o 2 (Cancelar).")
        return str(resp)

    # fallback
    reset_session(user_id)
    msg.body("Reinicié el chat por seguridad.\n\n" + menu_text())
    return str(resp)

if __name__ == "__main__":
    # Por defecto Flask corre en 5000
    app.run(host="0.0.0.0", port=5000, debug=True)
