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
from config import *
from sheets import sheet, usuarios_sheet, incidencias_sheet
from usuarios import (
    usuario_registrado,
    obtener_rol
)
from incidencias import registrar_salida_pendiente
from evidencias import photo_handler
from asistencia import (
    entrada,
    salida,
    descanso,
    regreso,
    estatus
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

# MEMORIA TEMPORAL
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
async def manejar_boton(update: Update, context: ContextTypes.DEFAULT_TYPE):

    texto = update.message.text

    if texto == "✅ Entrada":
        await entrada(update, context)
        return

    if texto == "🍽️ Descanso":
        await descanso(update, context)
        return

    if texto == "🔙 Regreso":
        await regreso(update, context)
        return

    if texto == "🚪 Salida":
        await salida(update, context)
        return

    if texto == "📋 Estatus":

        await estatus(update, context)
        return
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
# APP
application = ApplicationBuilder().token(TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("registro", registro))
application.add_handler(CommandHandler("entrada", entrada))
application.add_handler(CommandHandler("descanso", descanso))
application.add_handler(CommandHandler("regreso", regreso))
application.add_handler(CommandHandler("salida", salida))
application.add_handler(
    CommandHandler("estatus", estatus)
)
application.add_handler(
    MessageHandler(
        filters.Regex("^(✅ Entrada|🍽️ Descanso|🔙 Regreso|🚪 Salida|📋 Estatus)$"),
        manejar_boton
    )
)

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