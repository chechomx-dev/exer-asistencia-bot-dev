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
incidencias_sheet = client.open("Asistencia Exer DEV").worksheet("Incidencias")
# MEMORIA TEMPORAL
movimientos = {}
registro_pendiente = {}
ubicaciones_pendientes = {}
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
# VALIDAR ENTRADA ABIERTA
def entrada_abierta_anterior(telegram_id):

    registros = sheet.get_all_records()

    if not registros:
        return False

    ultimo = None

    for fila in registros:

        if str(fila["Telegram ID"]) == str(telegram_id):
            ultimo = fila

    if ultimo is None:
        return False

    if ultimo["Tipo"] == "Entrada":

    zona_mx = pytz.timezone("America/Mexico_City")
    hoy = datetime.now(zona_mx).strftime("%d/%m/%Y")

    if ultimo["Fecha"] != hoy:

        incidencias_sheet.append_row([

            hoy,
            "",
            ultimo["Nombre"],
            "Salida pendiente RH"

        ])

        return False

    return True


if ultimo["Tipo"] == "Salida":

    return False


return False
# VALIDAR USUARIO
def usuario_registrado(telegram_id):

    registros = usuarios_sheet.get_all_records()

    for fila in registros:

        if str(fila["Telegram ID"]) == str(telegram_id):

            if fila["Estatus"] == "ACTIVO":
                return True

    return False    
# ENTRADA
async def entrada(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if not usuario_registrado(user_id):

        await update.message.reply_text(
            "Debes registrarte primero usando /registro"
        )

        return


    if entrada_abierta_anterior(user_id):

        await update.message.reply_text(
            "Ya tienes una entrada abierta hoy."
        )

        return


    movimientos[user_id] = "Entrada"

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

    user_id = update.effective_user.id

    if not usuario_registrado(user_id):

        await update.message.reply_text(
            "Debes registrarte primero usando /registro"
        )

        return
registros = sheet.get_all_records()

ultimo = None

for fila in registros:

    if str(fila["Telegram ID"]) == str(user_id):

        ultimo = fila


if ultimo and ultimo["Tipo"] == "Salida":

    await update.message.reply_text(
        "No tienes una entrada abierta."
    )

    return
    movimientos[user_id] = "Salida"

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

    ubicaciones_pendientes[user.id] = {
        "fecha": fecha,
        "hora": hora,
        "telegram_id": telegram_id,
        "nombre": nombre,
        "tipo": tipo,
        "latitud": latitud,
        "longitud": longitud
    }

    await update.message.reply_text(
        "Ahora toma una foto de tu rostro 📸"
    )
# FOTO
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        user = update.effective_user

        if user.id not in ubicaciones_pendientes:

            await update.message.reply_text(
                "Primero registra ubicación 📍"
            )

            return

        datos = ubicaciones_pendientes[user.id]

        photo = update.message.photo[-1]

        telegram_file_id = photo.file_id

        sheet.append_row([

            datos["fecha"],
            datos["hora"],
            datos["telegram_id"],
            datos["nombre"],
            datos["tipo"],
            datos["latitud"],
            datos["longitud"],
            telegram_file_id

        ])

        ubicaciones_pendientes.pop(user.id, None)

        await update.message.reply_text(
            f'{datos["tipo"]} registrada correctamente ✅📸'
        )

    except Exception as e:

        print("ERROR EN PHOTO_HANDLER:", e)

        await update.message.reply_text(
            "Ocurrió un error al guardar evidencia."
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
application.add_handler(
    MessageHandler(filters.PHOTO, photo_handler)
)
print("Bot ejecutándose...")
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

print("Bot ejecutándose...")

application.run_polling(drop_pending_updates=True)