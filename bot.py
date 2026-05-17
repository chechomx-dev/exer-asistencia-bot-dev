from flask import Flask
import threading
import os
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot activo"
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz

# TOKEN TELEGRAM
TOKEN = os.environ["TELEGRAM_TOKEN"]

# GOOGLE SHEETS
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

import json
import os
from oauth2client.service_account import ServiceAccountCredentials

google_creds = json.loads(os.environ["GOOGLE_CREDENTIALS"])

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    google_creds,
    scope
)

client = gspread.authorize(creds)

sheet = client.open("Asistencia Exer").sheet1

# MEMORIA TEMPORAL
movimientos = {}

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    nombre = f"{update.effective_user.first_name} {update.effective_user.last_name or ''}"

    await update.message.reply_text(
        f"Hola {nombre} 👋\n\n"
        "Bot de asistencia Exer activo ✅\n\n"
        "Usa:\n"
        "/entrada\n"
        "/salida"
    )

# ENTRADA
async def entrada(update: Update, context: ContextTypes.DEFAULT_TYPE):

    movimientos[update.effective_user.id] = "Entrada"

    keyboard = [
        [KeyboardButton("Compartir ubicación 📍", request_location=True)]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        "Compárteme tu ubicación para registrar tu ENTRADA 📍",
        reply_markup=reply_markup
    )

# SALIDA
async def salida(update: Update, context: ContextTypes.DEFAULT_TYPE):

    movimientos[update.effective_user.id] = "Salida"

    keyboard = [
        [KeyboardButton("Compartir ubicación 📍", request_location=True)]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        "Compárteme tu ubicación para registrar tu SALIDA 📍",
        reply_markup=reply_markup
    )

# UBICACIÓN
async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    location = update.message.location

        tipo = movimientos.get(user.id, "Desconocido")

    zona_mx = pytz.timezone("America/Mexico_City")
    ahora = datetime.now(zona_mx)

    fecha = ahora.strftime("%d/%m/%Y")
    hora = ahora.strftime("%H:%M:%S")

    telegram_id = user.id

    nombre = f"{user.first_name} {user.last_name or ''}"

    latitud = location.latitude
    longitud = location.longitude

    sheet.append_row([
        fecha,
        hora,
        telegram_id,
        nombre,
        tipo,
        latitud,
        longitud
    ])

    await update.message.reply_text(
        f"{tipo} registrada correctamente ✅"
    )

# APP
application = ApplicationBuilder().token(TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("entrada", entrada))
application.add_handler(CommandHandler("salida", salida))

application.add_handler(
    MessageHandler(filters.LOCATION, location_handler)
)

print("Bot ejecutándose...")
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()

application.run_polling()