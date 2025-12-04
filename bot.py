import os
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from telegram_handlers import handle_update

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def message_handler(update, context):
    await handle_update(update.to_dict())

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
