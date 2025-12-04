import yt_dlp
import httpx

def resolve_redirect(url: str) -> str:
    try:
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(url)
            return str(response.url)
    except Exception as e:
        print(f"Redirect error: {e}")
        return url

def clean_instagram_url(url: str) -> str:
    if "instagram.com/p/" in url and "?img_index=" in url:
        url = url.split("?")[0]
    return url

def fetch_media(url: str) -> list[str]:
    try:
        url = resolve_redirect(url)
        url = clean_instagram_url(url)

        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "format": "best",
        }
        media_urls = []

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

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
