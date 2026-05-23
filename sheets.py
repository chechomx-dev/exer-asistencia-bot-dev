import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import NOMBRE_SHEET

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

google_creds = json.loads(os.environ["GOOGLE_CREDENTIALS"])

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    google_creds,
    scope
)

client = gspread.authorize(creds)

sheet = client.open(NOMBRE_SHEET).sheet1
usuarios_sheet = client.open(NOMBRE_SHEET).worksheet("Usuarios")
incidencias_sheet = client.open(NOMBRE_SHEET).worksheet("Incidencias")