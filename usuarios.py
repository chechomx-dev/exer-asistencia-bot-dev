from sheets import usuarios_sheet

def usuario_registrado(telegram_id):

    registros = usuarios_sheet.get_all_records()

    for fila in registros:

        if str(fila["Telegram ID"]) == str(telegram_id):

            if fila["Estatus"] == "ACTIVO":
                return True

    return False