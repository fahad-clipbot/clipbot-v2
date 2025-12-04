from downloader import fetch_media

def handle_update(update: dict):
    message = update.get("message") or update.get("edited_message")
    if not message:
        return

    chat_id = message["chat"]["id"]
    text = (message.get("text") or "").strip()

    if text == "/start":
        send_text(chat_id, "أرسل أي رابط (يوتيوب، تيك توك، تويتر، إنستغرام) وسأحمله لك مباشرة 🎬")
        return

    if text.startswith("http://") or text.startswith("https://"):
        media_list = fetch_media(text)
        if not media_list:
            send_text(chat_id, "ما قدرت أجيب وسائط من الرابط.")
            return
        for media in media_list:
            send_media(chat_id, media)
        return

    send_text(chat_id, "أرسل رابط مدعوم (يوتيوب، تيك توك، تويتر، إنستغرام).")
