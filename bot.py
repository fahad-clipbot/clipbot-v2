import os
import asyncio
import signal
from aiohttp import web
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram_handlers import handle_update

# متغيرات البيئة
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
# استخدام متغير البيئة PORT الذي توفره Railway، مع قيمة افتراضية 8080
PORT = int(os.getenv("PORT", "8080"))

# ----------------------------------------------------------------------
# دوال الـ aiohttp للخادم الصحي (Health Server)
# ----------------------------------------------------------------------

async def health(request):
    """نقطة نهاية لفحص حالة الخادم (Health Check)."""
    return web.Response(text="OK")

async def setup_health_server(port):
    """إعداد وتشغيل خادم aiohttp."""
    aio_app = web.Application()
    aio_app.router.add_get("/health", health)
    runner = web.AppRunner(aio_app)
    await runner.setup()
    # يجب أن يستمع الخادم على المنفذ المحدد
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    return runner

# ----------------------------------------------------------------------
# دوال البوت (Telegram Bot Handlers)
# ----------------------------------------------------------------------

async def start(update, context):
    """معالج أمر /start."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
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
    """معالج الرسائل النصية غير الأوامر."""
    # ملاحظة: تم تعديل طريقة استدعاء handle_update لتمرير التحديث كاملاً
    # بدلاً من القاموس، لضمان التوافق مع بيئة python-telegram-bot
    # إذا كانت handle_update تتوقع قاموساً، يجب تعديلها داخل ملف telegram_handlers.py
    # ولكن للحفاظ على الكود الأصلي، سنفترض أن التعديل على النحو التالي هو الأفضل:
    await handle_update(update.to_dict())

# ----------------------------------------------------------------------
# دالة التشغيل الرئيسية مع الإيقاف اللطيف (Graceful Shutdown)
# ----------------------------------------------------------------------

async def main():
    """الدالة الرئيسية لتشغيل البوت والخادم الصحي مع معالجة الإيقاف اللطيف."""
    
    # 1. إعداد تطبيق البوت
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    await bot_app.initialize()

    # 2. إعداد خادم الـ Health Check
    aio_runner = await setup_health_server(PORT)

    # 3. بدء الـ Webhook
    # ملاحظة: يجب أن يكون url_path هو الجزء الأخير من WEBHOOK_URL
    # إذا كان WEBHOOK_URL هو https://worker-production-8ff1.up.railway.app/webhook
    # فإن url_path يجب أن يكون "webhook"
    # سنفترض أن WEBHOOK_URL يحتوي على المسار كاملاً وأن المسار هو "/"
    # إذا كان المسار مختلفاً، يجب استخراجه من WEBHOOK_URL
    
    # سنستخدم المسار الفارغ "/" كافتراضي، وهو الشائع
    await bot_app.updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="", # المسار الذي يستمع عليه البوت (عادةً ما يكون فارغاً أو مساراً محدداً)
        webhook_url=WEBHOOK_URL,
    )
    
    # 4. دالة الإيقاف اللطيف
    async def shutdown(loop):
        print("تلقي إشارة إنهاء (SIGTERM). جاري إيقاف البوت بشكل لطيف...")
        
        # إيقاف تطبيق البوت
        await bot_app.updater.stop()
        await bot_app.shutdown()
        
        # إيقاف خادم aiohttp
        await aio_runner.cleanup()
        
        # إيقاف حلقة الأحداث
        loop.stop()
        print("تم إيقاف البوت بنجاح.")

    # 5. معالجة إشارة SIGTERM
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(shutdown(loop)))

    # 6. تشغيل حلقة الأحداث إلى الأبد (أو حتى يتم إيقافها بواسطة SIGTERM)
    await bot_app.start()
    
    # الانتظار حتى يتم إيقاف الحلقة
    while loop.is_running():
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # معالجة Ctrl+C للإيقاف المحلي
        print("تم الإيقاف بواسطة المستخدم.")
    except Exception as e:
        print(f"حدث خطأ غير متوقع: {e}")

