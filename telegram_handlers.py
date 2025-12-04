from telegram import Bot
from telegram.constants import ParseMode
import os
from downloader import fetch_media

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

def send_text(chat_id: int, text: str):
    bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML)

def send_media(chat_id: int, media_url: str):
    # إرسال فيديو فقط حالياً، نقدر نوسع لاحقاً حسب نوع الرابط
    bot.send_video(chat_id=chat_id, video=media_url)

def handle_update(update: dict):
    message = update.get("message") or update.get("edited_message")
    if not message:
        return

    chat_id = message["chat"]["id"]
    text = (message.get("text") or "").strip()

    # أمر البداية
    if text == "/start":
        send_text(chat_id, "أرسل أي رابط من المنصات المدعومة (يوتيوب، تيك توك، تويتر، إنستغرام) وسأحمله لك مباشرة 🎬")
        return

    # لو المستخدم أرسل رابط
    if text.startswith("http://") or text.startswith("https://"):
        media_list = fetch_media(text)
        if not media_list:
            send_text(chat_id, "ما قدرت أجيب وسائط من الرابط. تأكد إنه مدعوم أو جرب رابط ثاني.")
            return

        for media_url in media_list:
            send_media(chat_id, media_url)
        return

    # لو المستخدم كتب شيء غير رابط
    send_text(chat_id, "أرسل رابط مدعوم (يوتيوب، تيك توك، تويتر، إنستغرام).")
