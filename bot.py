import os
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters
from telegram_handlers import handle_update

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update, context):
    chat_id = update.effective_chat.id
    await context.bot.send_message(
        chat_id=chat_id,
        text="أهلاً 👋\nأرسل أي رابط (يوتيوب، تيك توك، تويتر، إنستغرام) وسأحمله لك مباشرة 🎬"
    )

async def message_handler(update, context):
    # تحويل التحديث إلى dict وإرساله لـ handle_update
    await handle_update(update.to_dict())

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # أمر /start
    app.add_handler(CommandHandler("start", start))

    # أي رسالة نصية غير أمر
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # تشغيل البوت باستخدام Polling
    app.run_polling()

if __name__ == "__main__":
    main()
