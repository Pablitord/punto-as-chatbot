# Chatbot de Reservas - Punto AS

Este proyecto consiste en un **chatbot conversacional con Inteligencia Artificial** que permite realizar reservas para canchas deportivas del **Punto AS** en **Manta, Ecuador**, a través de **WhatsApp**.

El chatbot utiliza un **modelo de lenguaje (DeepSeek)** para interpretar mensajes en **lenguaje natural**, guiar dinámicamente la conversación y extraer la información necesaria para completar una reserva.  
Las reservas se almacenan de forma **persistente** en una **base de datos MongoDB Atlas**.

El sistema está **desplegado en la nube con Vercel** y se integra con **WhatsApp mediante Twilio**.

## Requisitos:
1. **Python 3.x**
2. **Flask**
3. **Twilio** (WhatsApp Sandbox)
4. **MongoDB Atlas**
5. **DeepSeek API**
6. **Ngrok** (solo para pruebas locales)z


## Para probar directamente el chatbot:
Si deseas probar el chatbot sin configuraciones adicionales, simplemente sigue estos pasos:
1. **Accede al siguiente enlace o escanea el QR**:
   - [Iniciar chat con el bot en WhatsApp](https://wa.me/4155238886)
      - En caso de seguir el Link, enviar el mensaje **"join adult-agree"**
   - [Chatbot funcionando](./assets/QR-WhatsApp.jpeg)

2. **Escribe "hola"** para empezar la conversación.

3. El chatbot responderá utilizando **IA**, permitiendo frases libres como:
- “Quiero reservar una cancha de básquet mañana”
- “Me llamo Juan y quiero jugar vóley”



## Instalación y Configuración:

### 1. **Clonar el repositorio**:
   Si aún no has clonado el repositorio, hazlo con el siguiente comando:
   ```bash
   git clone https://github.com/Pablitord/punto-as-chatbot.git
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
### 4. Configurar variables de entorno (.env)
Configurar variables de entorno (.env)
   ```bash
   DEEPSEEK_API_KEY=tu_api_key_deepseek
MONGODB_URI=mongodb+srv://<usuario>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB=reservas_punto_as
MONGODB_COLLECTION=reservas

   ```

### 5. **Ejecutar Servidor (Localmente)**:
   Si deseas ejecutar el bot localmente antes de desplegarlo, puedes usar ngrok para exponer el servidor Flask:
- **Ejecuta el servidor Flask:**
Abre una nueva terminal y ejecuta:
   ```bash
   python app.py
   ```
- **Inicia ngrok para exponer el servidor**
Mientras se ejecuta **app.py**, abre una nueva terminal y ejecuta:

   ```bash
   ngrok http 5000
   ```
   - Copia la URL en el apartado **"Forwarding"**, ej: "https://unallotted-daxton-summonable.ngrok-free.dev"
   
### 6. **Configurar Twilio**:
- Regístrate en Twilio y configura el sandbox de WhatsApp.
   - Una Vez en **Twilio Console**, dirigirse a: Develop → Messaging → Try it out → Send a WhatsApp messege 

- En el apartado **Sandbox Settings**, dirigirse a  **"When a meesage comes in"**, Añade el webhook de Twilio con la URL dada por ngrok, agregando "/webhook" al final, EJ: "https://unallotted-daxton-summonable.ngrok-free.dev/webhook", ubicar el método **"Post"** y dar clic en **"Save"**

- Regresar al apartado **"Sandbox"**, escanear el QR o enviar el código al número indicado, ej: **"join adult-agree"**

### 7. **Probar el Bot**:
Una vez configurado todo, el flujo de la conversación iniciará enviando un mensaje dado por **Twilio**, seguido, enviando un mensaje **"hola**

El chatbot responderá usando IA, sin depender de opciones numéricas fijas.

## **Despliegue en Vercel**
El chatbot está desplegado en Vercel y puede ser accedido mediante la URL pública. Solo necesitas configurar el webhook en Twilio con la siguiente URL:
- **Url del Bot en Vercel:**
   https://punto-as-chatbot.vercel.app

### 1. **Configurar Webhook en Twilio:**
1. Dirígete a Twilio Console → Messaging → WhatsApp → Sandbox Settings.
2. En **"When a message comes in"**, coloca la URL pública de Vercel con /webhook al final, EJ: https://punto-as-chatbot.vercel.app/webhook
3. Regresar al apartado **"Sandbox"**, escanear el QR o enviar el código al número indicado, ej: **"join adult-agree"**

### 2.  **Probar el Bot**:
Una vez configurado todo, el flujo de la conversación iniciará ingresando el código dado por **Twilio**, seguido, enviando un mensaje **"hola**