from sheets import sheet
from config import ubicaciones_pendientes


async def photo_handler(update, context):

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