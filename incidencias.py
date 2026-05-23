from datetime import datetime
import pytz

from config import TIMEZONE
from sheets import incidencias_sheet


def registrar_salida_pendiente(nombre):

    zona_mx = pytz.timezone(TIMEZONE)
    hoy = datetime.now(zona_mx).strftime("%d/%m/%Y")

    incidencias_sheet.append_row([
        hoy,
        "",
        nombre,
        "Salida pendiente RH"
    ])