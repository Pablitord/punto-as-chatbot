# Chatbot de Reservas - Punto AS

Este proyecto consiste en un chatbot que permite realizar reservas para canchas en el **Punto AS** de **Manta, Ecuador**, utilizando un bot de **WhatsApp**. El chatbot permite interactuar con el usuario para hacer reservas de canchas de básquet 3x3 o ecuavóley/vóley sala. El bot está **desplegado en Vercel** y usa **Twilio** para la integración con WhatsApp.

## Requisitos:
1. **Python 3.x**
2. **Twilio** (para enviar mensajes de WhatsApp).
3. **Flask** (para el backend del chatbot).
4. **Ngrok** o cualquier herramienta para exponer el servidor local, si se ejecuta localmente (en el caso de Vercel no es necesario).
## Para probar directamente el chatbot:
Si deseas probar el chatbot sin configuraciones adicionales, simplemente sigue estos pasos:


## Instalación y Configuración:

### 1. **Clonar el repositorio**:
   Si aún no has clonado el repositorio, hazlo con el siguiente comando:
   ```bash
   git clone https://github.com/TU-USUARIO/punto-as-chatbot.git
   ```
### 2. **Crea un Entorno Virtual**:
   Navega hasta la carpeta del proyecto y crea un entorno virtual:
   ```bash
   python -m venv venv
   ```
   Luego, activa el entorno virtual:
   ```bash
   venv\Scripts\activate
   ```
### 3. **Instala las Dependencias**:
   Asegúrate de que las dependencias necesarias estén instaladas ejecutando:
   ```bash
   pip install -r requirements.txt
   ```
### 4. **Ejecutar Servidor (Localmente)**:
   Si deseas ejecutar el bot localmente antes de desplegarlo, puedes usar ngrok para exponer el servidor Flask:

- **Ejecuta el servidor Flask:**
Abre una nueva terminal y ejecuta:
   ```bash
   python app.py
   ```
- **Inicia ngrok para exponer el servidor**
Mientras se ejecuta app.py, abre una nueva terminar y ejecuta:
   ```bash
   ngrok http 5000
   ```
   Copiar la URL en el apartado "Forwarding", ej: "https://unallotted-daxton-summonable.ngrok-free.dev"
   
### 5. **Configurar Twilio**:
- Regístrate en Twilio y configura el sandbox de WhatsApp.
- Escanea el QR o manda un mensaje al número indicado en pantalla, una vez hecho ese proceso, dirigirse a **Sandbox settings**
- En el apartado **"When a meesage comes in"**, Añade el webhook de Twilio con la URL dada por ngrok, agregando "/webhook" al final, EJ: "https://unallotted-daxton-summonable.ngrok-free.dev/webhook", ubicar el método **"Post"** y dar clic en **"Save"**

### 6. **Probar el Bot**:
Una vez configurado todo, el flujo de la conversación iniciará enviando un mensaje dado por **Twilio**, seguido, enviando un mensaje **"hola**

## **Despliegue en Vercel**
El chatbot está desplegado en Vercel y puede ser accedido mediante la URL pública. Solo necesitas configurar el webhook en Twilio con la siguiente URL:
- **Url del Bot en Vercel:**
   https://punto-as-chatbot.vercel.app

### 1. **Configurar Webhook en Twilio:**
1. Dirígete a Twilio Console → Messaging → WhatsApp → Sandbox Settings.
2. En **"When a message comes in"**, coloca la URL pública de Vercel con /webhook al final, EJ: https://punto-as-chatbot.vercel.app/webhook

### 2.  **Probar el Bot**:
Una vez configurado todo, el flujo de la conversación iniciará con enviando un mensaje **"hola**

**Enlace para probar el Bot**

- https://wa.me/14155238886

**Número para probar el Bot**
- **+1 415 523 8886**
- Ingresa el codigo dado por Twilio
- Enviar Mensaje: **"hola"**
   



