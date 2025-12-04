import yt_dlp

def fetch_media(url: str) -> list[str]:
    """
    ترجع قائمة روابط وسائط (فيديو/صوت/صور) من أي منصة مدعومة مثل:
    - YouTube
    - TikTok
    - Instagram
    - Twitter
    وغيرها...

    تعتمد على مكتبة yt-dlp، وتستخدم وضع عدم التحميل (extract فقط).
    """
    try:
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "format": "best",
        }
        media_urls = []

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # لو المحتوى عبارة عن قائمة (playlist أو carousel)
            if "entries" in info:
                for entry in info["entries"]:
                    media_url = entry.get("url")
                    if media_url:
                        media_urls.append(media_url)
            else:
                media_url = info.get("url")
                if media_url:
                    media_urls.append(media_url)

        return media_urls

    except Exception as e:
        print(f"Error fetching media: {e}")
        return []
