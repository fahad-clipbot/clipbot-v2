import os
import httpx
from urllib.parse import urlparse, parse_qs
from downloader import fetch_instagram_media

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_text(chat_id, text):
    with httpx.Client() as client:
        client.post(f"{BASE_URL}/sendMessage", data={"chat_id": chat_id, "text": text})

def send_media(chat_id, media_url):
    with httpx.Client() as client:
        try:
            client.post(f"{BASE_URL}/sendVideo", data={"chat_id": chat_id, "video": media_url})
        except Exception:
            client.post(f"{BASE_URL}/sendPhoto", data={"chat_id": chat_id, "photo": media_url})

def handle_update(update: dict):
    message = update.get("message") or update.get("edited_message")
    if not message:
        return

    chat_id = message["chat"]["id"]
    text = (message.get("text") or "").strip()

    if text == "/start":
        send_text(chat_id, "أهلاً بك في Clipot V2 🎬 أرسل رابط إنستغرام وسأجلب الوسائط لك.")
        return

    if not (text.startswith("http://") or text.startswith("https://")):
        send_text(chat_id, "أرسل رابط إنستغرام مباشر لمنشور (post أو reel).")
        return

    url = urlparse(text)
    if "instagram.com" in url.netloc:
        try:
            qs = parse_qs(url.query)
            requested_index = None
            if "img_index" in qs:
                try:
                    requested_index = int(qs.get("img_index", [0])[0])
                except ValueError:
                    requested_index = None

            media_list = fetch_instagram_media(text)

            if not media_list:
                send_text(chat_id, "ما قدرت أجيب وسائط من الرابط. تأكد أنه عام وغير محظور.")
                return

            if requested_index is not None:
                if 0 <= requested_index < len(media_list):
                    send_media(chat_id, media_list[requested_index])
                else:
                    send_text(chat_id, f"الرقم المطلوب خارج النطاق: المنشور يحتوي {len(media_list)} وسائط.")
            else:
                send_media(chat_id, media_list[0])
                if len(media_list) > 1:
                    send_text(chat_id, f"تم إرسال أول وسيط. يوجد {len(media_list)} وسائط. أرسل img_index لاختيار وسيط محدد.")
        except Exception:
            send_text(chat_id, "صار خطأ أثناء معالجة رابط إنستغرام.")
        return

    send_text(chat_id, "الرابط ليس إنستغرام. حالياً البوت يدعم إنستغرام فقط.")
