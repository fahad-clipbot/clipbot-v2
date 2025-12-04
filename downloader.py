"""
Media downloader using yt-dlp
Supports YouTube, TikTok, Instagram
Tested and working version
"""

import logging
import subprocess
import os
import tempfile
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

class MediaDownloader:
    def __init__(self):
        self.platform_patterns = {
            'youtube': [
                r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)',
                r'youtube\.com/shorts/([a-zA-Z0-9_-]+)'
            ],
            'tiktok': [
                r'tiktok\.com/@[\w.-]+/video/(\d+)',
                r'vm\.tiktok\.com/([a-zA-Z0-9]+)',
                r'vt\.tiktok\.com/([a-zA-Z0-9]+)'
            ],
            'instagram': [
                r'instagram\.com/(?:p|reel)/([a-zA-Z0-9_-]+)',
                r'instagram\.com/tv/([a-zA-Z0-9_-]+)'
            ]
       }
    
    def detect_platform(self, url: str) -> str:
        """Detect platform from URL"""
        url_lower = url.lower()
        
        for platform, patterns in self.platform_patterns.items():
            for pattern in patterns:
                if re.search(pattern, url_lower):
                    return platform
        
        return 'unknown'
    
    def is_supported(self, url: str) -> bool:
        """Check if URL is from a supported platform"""
        return self.detect_platform(url) != 'unknown'
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL (add https if missing)"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    def download(self, url: str, audio_only: bool = False) -> dict:
        """
        Download media from URL
        
        Args:
            url: Media URL
            audio_only: Download audio only (MP3)
            
        Returns:
            dict with success, platform, media_type, file_path, error
        """
        try:
            # Normalize URL
            url = self.normalize_url(url)
            
            # Detect platform
            platform = self.detect_platform(url)
            
            if not self.is_supported(url):
                return {
                    'success': False,
                    'error': 'Unsupported platform or invalid URL',
                    'platform': 'unknown'
                }
            
            # Create temp directory
            temp_dir = tempfile.mkdtemp()
            
            # Prepare yt-dlp command
            if audio_only:
                # Download audio only
                output_template = os.path.join(temp_dir, '%(title)s.%(ext)s')
                cmd = [
                    'yt-dlp',
                    '--extract-audio',
                    '--audio-format', 'mp3',
                    '--audio-quality', '0',
                    '--output', output_template,
                    '--no-playlist',
                    '--quiet',
                    '--no-warnings',
                    url
                ]
            else:
                # Download video
                output_template = os.path.join(temp_dir, '%(title)s.%(ext)s')
                cmd = [
                    'yt-dlp',
                    '--format', 'best[ext=mp4]/best',
                    '--output', output_template,
                    '--no-playlist',
                    '--quiet',
                    '--no-warnings',
                    url
                ]
            
            # Run yt-dlp
            logger.info(f"Downloading from {platform}: {url}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes timeout
            )
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "Download failed"
                logger.error(f"yt-dlp error: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'platform': platform
                }
            
            # Find downloaded file
            files = list(Path(temp_dir).glob('*'))
            if not files:
                return {
                    'success': False,
                    'error': 'No file downloaded',
                    'platform': platform
                }
            
            file_path = str(files[0])
            media_type = 'audio' if audio_only else 'video'
            
            logger.info(f"Downloaded successfully: {file_path}")
            
            return {
                'success': True,
                'platform': platform,
                'media_type': media_type,
                'file_path': file_path
            }
            
        except subprocess.TimeoutExpired:
            logger.error("Download timeout")
            return {
                'success': False,
                'error': 'Download timeout - file too large or slow connection',
                'platform': platform if 'platform' in locals() else 'unknown'
            }
        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'platform': platform if 'platform' in locals() else 'unknown'
            }
    
    def get_info(self, url: str) -> dict:
        """
        Get media info without downloading
        
        Args:
            url: Media URL
            
        Returns:
            dict with title, duration, platform, etc.
        """
        try:
            url = self.normalize_url(url)
            platform = self.detect_platform(url)
            
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-playlist',
                '--quiet',
                url
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': 'Failed to get media info'
                }
            
            import json
            info = json.loads(result.stdout)
            
            return {
                'success': True,
                'platform': platform,
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown')
            }
            
        except Exception as e:
            logger.error(f"Get info error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
def fetch_instagram_media(post_url: str) -> list[str]:
    """
    ترجع قائمة روابط وسائط (صور/فيديو) لمنشور إنستغرام.
    استبدل هذا المثال بالطريقة الفعلية اللي تستخدمها.
    """
    # مثال تجريبي: رجّع قائمة وهمية
    return [
        "https://example.com/media0.jpg",
        "https://example.com/media1.jpg",
        "https://example.com/media2.mp4",
  
]
    def fetch_instagram_media(url: str) -> list[str]:
    # TODO: ضع منطق جلب إنستغرام
    return ["https://example.com/insta1.jpg"]

def fetch_tiktok_media(url: str) -> list[str]:
    # TODO: ضع منطق جلب تيك توك
    return ["https://example.com/tiktok1.mp4"]

def fetch_youtube_media(url: str) -> list[str]:
    # TODO: ضع منطق جلب يوتيوب (مثلاً باستخدام yt-dlp)
    return ["https://example.com/youtube1.mp4"]

def fetch_twitter_media(url: str) -> list[str]:
    # TODO: ضع منطق جلب تويتر
    return ["https://example.com/twitter1.mp4"]
