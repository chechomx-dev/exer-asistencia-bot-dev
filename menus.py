from telegram import ReplyKeyboardMarkup


def menu_por_estado(tipo):

    if tipo == "Entrada":
        keyboard = [
            ["📋 Estatus"],
            ["🍽️ Descanso", "🚪 Salida"]
        ]

    elif tipo == "Descanso":
        keyboard = [
            ["📋 Estatus"],
            ["🔙 Regreso", "🚪 Salida"]
        ]

    elif tipo == "Regreso":
        keyboard = [
            ["📋 Estatus"],
            ["🚪 Salida"]
        ]

    else:
        keyboard = [
            ["📋 Estatus"],
            ["✅ Entrada"]
        ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )