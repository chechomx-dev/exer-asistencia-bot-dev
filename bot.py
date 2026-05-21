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

sheet = client.open("Asistencia Exer DEV").sheet1
usuarios_sheet = client.open("Asistencia Exer DEV").worksheet("Usuarios")
# MEMORIA TEMPORAL
movimientos = {}
registro_pendiente = {}
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
# REGISTRO
async def registro(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    registro_pendiente[user_id] = True

    await update.message.reply_text(
        "Ingresa tu número de empleado 🪪"
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
# VALIDAR EMPLEADO
async def validar_empleado(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    user_id = user.id

    if user_id not in registro_pendiente:
        return

    employ_id = update.message.text.strip()

    registros = usuarios_sheet.get_all_records()

    for fila in registros:

        if str(fila["Employ ID"]) == employ_id:

            if fila["Estatus"] != "ACTIVO":

                await update.message.reply_text(
                    "Usuario inactivo. Comunícate con RH."
                )

                registro_pendiente.pop(user_id, None)
                return

            if fila["Telegram ID"]:

                await update.message.reply_text(
                    "Este empleado ya tiene un dispositivo registrado. Comunícate con RH."
                )

                registro_pendiente.pop(user_id, None)
                return

            cell = usuarios_sheet.find(employ_id)

            usuarios_sheet.update_cell(
                cell.row,
                8,
                str(user_id)
            )

            await update.message.reply_text(
                "Registro completado correctamente ✅"
            )

            registro_pendiente.pop(user_id, None)
            return

    await update.message.reply_text(
        "Número de empleado no válido. Comunícate con RH."
    )

    registro_pendiente.pop(user_id, None)
# UBICACIÓN
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
application.add_handler(CommandHandler("registro", registro))
application.add_handler(CommandHandler("entrada", entrada))
application.add_handler(CommandHandler("salida", salida))
application.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        validar_empleado
    )
)
application.add_handler(
    MessageHandler(filters.LOCATION, location_handler)
)

print("Bot ejecutándose...")
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

print("Bot ejecutándose...")

application.run_polling(drop_pending_updates=True)