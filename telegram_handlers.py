def handle_update(update: dict):
    message = update.get("message") or update.get("edited_message")
    if not message:
        return

    chat_id = message["chat"]["id"]
    text = (message.get("text") or "").strip()

    # أمر البداية
    if text == "/start":
        send_text(chat_id, "أرسل أي رابط (تيك توك، إنستغرام، يوتيوب، تويتر) وسأحمله لك مباشرة 🎬")
        return

    # لو الرابط إنستغرام
    if "instagram.com" in text:
        media_list = fetch_instagram_media(text)
        for media in media_list:
            send_media(chat_id, media)
        return

    # لو الرابط تيك توك
    if "tiktok.com" in text:
        media_list = fetch_tiktok_media(text)
        for media in media_list:
            send_media(chat_id, media)
        return

    # لو الرابط يوتيوب
    if "youtube.com" in text or "youtu.be" in text:
        media_list = fetch_youtube_media(text)
        for media in media_list:
            send_media(chat_id, media)
        return

    # لو الرابط تويتر
    if "twitter.com" in text or "x.com" in text:
        media_list = fetch_twitter_media(text)
        for media in media_list:
            send_media(chat_id, media)
        return

    # لو مو رابط مدعوم
    send_text(chat_id, "الرابط غير مدعوم حالياً. جرب تيك توك، إنستغرام، يوتيوب أو تويتر.")
