from datetime import datetime
import pytz

from telegram import (
    ReplyKeyboardMarkup,
    KeyboardButton
)

from config import movimientos
from sheets import sheet
from usuarios import usuario_registrado
from incidencias import registrar_salida_pendiente


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

        zona_mx = pytz.timezone(
            "America/Mexico_City"
        )

        hoy = datetime.now(
            zona_mx
        ).strftime("%d/%m/%Y")


        if ultimo["Fecha"] != hoy:

            registrar_salida_pendiente(
                ultimo["Nombre"]
            )

            return "ANTERIOR"

        return "HOY"


    if ultimo["Tipo"] == "Salida":

        return False


    return False


async def entrada(update, context):

    user_id = update.effective_user.id

    if not usuario_registrado(user_id):

        await update.message.reply_text(
            "Debes registrarte primero usando /registro"
        )

        return


    resultado_entrada = entrada_abierta_anterior(
        user_id
    )


    if resultado_entrada == "HOY":

        await update.message.reply_text(
            "Ya tienes una entrada abierta hoy."
        )

        return


    if resultado_entrada == "ANTERIOR":

        await update.message.reply_text(
            "⚠️ Cuidado: olvidaste registrar tu salida anterior."
        )


    movimientos[user_id] = "Entrada"

    keyboard = [
        [KeyboardButton(
            "Compartir ubicación 📍",
            request_location=True
        )]
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


async def salida(update, context):

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


    if ultimo is None or ultimo["Tipo"] == "Salida":

        await update.message.reply_text(
            "No tienes una entrada abierta."
        )

        return


    movimientos[user_id] = "Salida"

    keyboard = [
        [KeyboardButton(
            "Compartir ubicación 📍",
            request_location=True
        )]
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


async def descanso(update, context):

    user_id = update.effective_user.id

    if not usuario_registrado(user_id):
        await update.message.reply_text(
            "Debes registrarte primero usando /registro"
        )
        return

    movimientos[user_id] = "Descanso"

    keyboard = [
        [KeyboardButton(
            "Compartir ubicación 📍",
            request_location=True
        )]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        "Compárteme tu ubicación para registrar tu DESCANSO 🍽️",
        reply_markup=reply_markup
    )


async def regreso(update, context):

    user_id = update.effective_user.id

    if not usuario_registrado(user_id):
        await update.message.reply_text(
            "Debes registrarte primero usando /registro"
        )
        return

    movimientos[user_id] = "Regreso"

    keyboard = [
        [KeyboardButton(
            "Compartir ubicación 📍",
            request_location=True
        )]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        "Compárteme tu ubicación para registrar tu REGRESO 🍽️",
        reply_markup=reply_markup
    )
    await update.message.reply_text("Debes registrarte primero usando /registro")
    return

    movimientos[user_id] = "Descanso"

    keyboard = [[KeyboardButton("Compartir ubicación 📍", request_location=True)]]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        "Compárteme tu ubicación para registrar tu DESCANSO 🍽️",
        reply_markup=reply_markup
    )


async def regreso(update, context):

    user_id = update.effective_user.id

    if not usuario_registrado(user_id):
        await update.message.reply_text("Debes registrarte primero usando /registro")
        return

    movimientos[user_id] = "Regreso"

    keyboard = [[KeyboardButton("Compartir ubicación 📍", request_location=True)]]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        "Compárteme tu ubicación para registrar tu REGRESO de descanso 🍽️",
        reply_markup=reply_markup
    )