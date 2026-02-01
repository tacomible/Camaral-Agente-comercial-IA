from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
from openai import OpenAI
import os
import json
from datetime import datetime


# ------------------------
# Config OpenAI
# ------------------------

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# ------------------------
# App
# ------------------------

app = FastAPI(title="Camaral Assistant")

# ------------------------
# Static
# ------------------------

app.mount("/static", StaticFiles(directory="static"), name="static")


# ------------------------
# Models
# ------------------------

class Message(BaseModel):
    text: str


class Lead(BaseModel):
    name: str
    email: EmailStr
    whatsapp: str


# ------------------------
# Utils
# ------------------------

LEADS_FILE = "leads.json"


def save_lead_to_file(lead_data: dict):

    leads = []

    # Cargar si existe
    if os.path.exists(LEADS_FILE):
        with open(LEADS_FILE, "r", encoding="utf-8") as f:
            try:
                leads = json.load(f)
            except:
                leads = []

    leads.append(lead_data)

    # Guardar
    with open(LEADS_FILE, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)


# ------------------------
# Home
# ------------------------

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


# ------------------------
# Chat
# ------------------------

@app.post("/chat")
async def chat(message: Message):

    try:

        user_text = message.text.strip()

        if not user_text:
            return {"reply": "Por favor escribe un mensaje."}


        # PROMPT PROFESIONAL
        system_prompt = """
Eres el asistente comercial oficial de Camaral.

Objetivo:
- Explicar el producto claramente
- Detectar intención de compra
- Generar confianza
- Convertir leads

Estilo:
- Profesional
- Cercano
- Estratégico
- Nada genérico

Idioma: Español

Contexto:
Camaral ofrece avatares con IA para ventas, soporte y capacitación.
Automatiza atención, califica leads y mejora conversión.
"""


        # OPENAI NUEVO SDK
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            temperature=0.6,
            max_tokens=300
        )


        reply = completion.choices[0].message.content


        # Detectar intención comercial
        wants_price = any(word in user_text.lower() for word in [
            "precio", "costo", "valor", "plan", "tarifa",
            "demo", "prueba", "cita", "llamada", "reunión",
            "comprar", "contratar"
        ])


        return {
            "reply": reply,
            "lead": wants_price,
            "suggestions": []
        }


    except Exception as e:

        print("ERROR CHAT:", str(e))

        raise HTTPException(
            status_code=500,
            detail="Error interno"
        )



# ------------------------
# Leads
# ------------------------

@app.post("/lead")
async def save_lead(lead: Lead):

    try:

        lead_data = {
            "name": lead.name,
            "email": lead.email,
            "whatsapp": lead.whatsapp,
            "date": datetime.now().isoformat()
        }

        save_lead_to_file(lead_data)


        print("===== NUEVO LEAD =====")
        print(lead_data)
        print("======================")

        return {
            "status": "ok",
            "message": "Datos recibidos. Te contactaremos pronto."
        }


    except Exception as e:

        print("ERROR LEAD:", str(e))

        raise HTTPException(
            status_code=500,
            detail="Error guardando lead"
        )
