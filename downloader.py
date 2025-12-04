import yt_dlp
import httpx

def resolve_redirect(url: str) -> str:
    """
    يفك أي رابط مختصر (redirect) ويرجعه كرابط مباشر.
    """
    try:
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(url)
            return str(response.url)
    except Exception as e:
        print(f"Redirect error: {e}")
        return url

def fetch_media(url: str) -> list[str]:
    """
    ترجع قائمة روابط وسائط (فيديو/صوت/صور) من أي منصة مدعومة.
    """
    try:
        # فك أي روابط مختصرة أولاً
        url = resolve_redirect(url)

        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "format": "best",
        }
        media_urls = []

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if "entries" in info:  # قائمة تشغيل أو carousel
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
