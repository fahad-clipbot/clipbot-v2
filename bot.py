import os
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters
from telegram_handlers import handle_update

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # مثل https://your-app-name.up.railway.app

async def start(update, context):
    chat_id = update.effective_chat.id
    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "👋 أهلاً بك في Clipot V2!\n\n"
            "📥 أرسل أي رابط من المنصات المدعومة:\n"
            "- يوتيوب\n- تيك توك\n- تويتر\n- إنستغرام\n\n"
            "🎬 سأرسل لك الفيديو أو الصورة أو الصوت مباشرة.\n"
            "💡 لا تحتاج للاشتراك، الخدمة مجانية حالياً.\n"
            "🛠 لو فيه مشكلة بالرابط، جرب رابط مباشر أو أرسل كلمة 'مساعدة'."
        )
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
