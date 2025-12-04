from telegram import Bot
from telegram.constants import ParseMode
import os
from downloader import fetch_media

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

async def send_text(chat_id: int, text: str):
    await bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML)

async def send_media(chat_id: int, media_url: str):
    # فلترة حسب نوع الوسائط
    if media_url.endswith(".mp4"):
        await bot.send_video(chat_id=chat_id, video=media_url)
    elif media_url.endswith(".jpg") or media_url.endswith(".png"):
        await bot.send_photo(chat_id=chat_id, photo=media_url)
    elif media_url.endswith(".mp3") or media_url.endswith(".m4a"):
        await bot.send_audio(chat_id=chat_id, audio=media_url)
    else:
        await bot.send_message(chat_id=chat_id, text=f"الرابط: {media_url}")

async def handle_update(update: dict):
    message = update.get("message") or update.get("edited_message")
    if not message:
        return

    chat_id = message["chat"]["id"]
    text = (message.get("text") or "").strip()

    if text == "/start":
        await send_text(chat_id, "أرسل أي رابط (يوتيوب، تيك توك، تويتر، إنستغرام) وسأحمله لك مباشرة 🎬")
        return

    if text.startswith("http://") or text.startswith("https://"):
        await send_text(chat_id, f"جاري تحميل الوسائط من الرابط...\n{text}")
        media_list = fetch_media(text)
        if not media_list:
            await send_text(chat_id, "ما قدرت أجيب وسائط من الرابط. تأكد إنه مدعوم أو جرب رابط ثاني.")
            return

        for media_url in media_list:
            await send_media(chat_id, media_url)
        return

    await send_text(chat_id, "أرسل رابط مدعوم (يوتيوب، تيك توك، تويتر، إنستغرام).")
