from datetime import datetime
import pytz

from config import TIMEZONE
from sheets import incidencias_sheet, usuarios_sheet


def obtener_employ_id_por_telegram(telegram_id):

    registros = usuarios_sheet.get_all_records()

    for fila in registros:

        if str(fila["Telegram ID"]) == str(telegram_id):
            return fila["Employ ID"]

    return ""


def registrar_salida_pendiente(telegram_id, nombre):

    zona_mx = pytz.timezone(TIMEZONE)

    hoy = datetime.now(
        zona_mx
    ).strftime("%d/%m/%Y")

    employ_id = obtener_employ_id_por_telegram(
        telegram_id
    )

    incidencias_sheet.append_row([
        hoy,
        telegram_id,
        employ_id,
        nombre,
        "Salida pendiente RH"
    ])


def registrar_no_descanso(telegram_id, nombre):

    zona_mx = pytz.timezone(TIMEZONE)

    hoy = datetime.now(
        zona_mx
    ).strftime("%d/%m/%Y")

    employ_id = obtener_employ_id_por_telegram(
        telegram_id
    )

    incidencias_sheet.append_row([
        hoy,
        telegram_id,
        employ_id,
        nombre,
        "No registró descanso"
    ])