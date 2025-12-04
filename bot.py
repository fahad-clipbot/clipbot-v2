import os
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters
from telegram_handlers import handle_update

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # مثل https://dazzling-vitality.up.railway.app

async def start(update, context):
    chat_id = update.effective_chat.id
    await context.bot.send_message(
        chat_id=chat_id,
        text="أهلاً 👋\nأرسل أي رابط (يوتيوب، تيك توك، تويتر، إنستغرام) وسأحمله لك مباشرة 🎬"
    )

async def message_handler(update, context):
    await handle_update(update.to_dict())

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).webhook_url(WEBHOOK_URL).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    main()
