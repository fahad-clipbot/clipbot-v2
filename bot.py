import os
import asyncio
from aiohttp import web
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram_handlers import handle_update  # تأكد إن هذا الملف موجود ويحتوي على دالة handle_update

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # مثل https://worker-production-xxxx.up.railway.app
PORT = int(os.getenv("PORT", "8080"))

# نقطة فحص الصحة لـ Railway
async def health(request):
    return web.Response(text="OK")

# أمر /start
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

# أي رسالة نصية غير أمر
async def message_handler(update, context):
    await handle_update(update.to_dict())

# تشغيل البوت باستخدام Webhook
async def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    await app.initialize()
    await app.start()
    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
    )

# تشغيل سيرفر aiohttp الخارجي
async def run_health_server():
    app = web.Application()
    app.router.add_get("/health", health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

# تشغيل الاثنين معًا
async def main():
    await asyncio.gather(run_bot(), run_health_server())

if __name__ == "__main__":
    asyncio.run(main())
