"""
Downloader module using Cobalt API
Supports YouTube, TikTok, Instagram
Downloads videos, images, and audio
"""

import requests
import logging
from typing import Optional, Dict, List
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class MediaDownloader:
    def __init__(self):
        self.cobalt_api = "https://api.cobalt.tools/api/json"
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def detect_platform(self, url: str) -> Optional[str]:
        """Detect platform from URL"""
        try:
            domain = urlparse(url).netloc.lower()
            
            if 'youtube.com' in domain or 'youtu.be' in domain:
                return 'youtube'
            elif 'tiktok.com' in domain:
                return 'tiktok'
            elif 'instagram.com' in domain:
                return 'instagram'
            else:
                return None
        except Exception as e:
            logger.error(f"Error detecting platform: {e}")
            return None
    
    def download_video(self, url: str) -> Dict:
        """
        Download video from URL
        Returns dict with status, file_url, platform, media_type
        """
        try:
            platform = self.detect_platform(url)
            if not platform:
                return {
                    'success': False,
                    'error': 'منصة غير مدعومة. الرجاء استخدام روابط من يوتيوب، تيك توك، أو انستقرام.',
                    'platform': None
                }
            
            # Prepare request for Cobalt API
            payload = {
                "url": url,
                "videoQuality": "720",  # Default quality
                "filenameStyle": "basic",
                "downloadMode": "auto"
            }
            
            response = requests.post(
                self.cobalt_api,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Cobalt API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': 'فشل في الاتصال بخدمة التنزيل. حاول مرة أخرى.',
                    'platform': platform
                }
            
            data = response.json()
            
            # Handle different response statuses
            if data.get('status') == 'error':
                error_msg = data.get('text', 'حدث خطأ غير معروف')
                return {
                    'success': False,
                    'error': f'خطأ: {error_msg}',
                    'platform': platform
                }
            
            # Check for direct video URL
            if data.get('status') == 'redirect' or data.get('status') == 'stream':
                video_url = data.get('url')
                if video_url:
                    return {
                        'success': True,
                        'file_url': video_url,
                        'platform': platform,
                        'media_type': 'video',
                        'title': data.get('filename', 'video')
                    }
            
            # Check for picker (multiple files like TikTok images)
            if data.get('status') == 'picker':
                picker_items = data.get('picker', [])
                if picker_items:
                    # Return first item for now
                    return {
                        'success': True,
                        'file_url': picker_items[0].get('url'),
                        'platform': platform,
                        'media_type': 'image',
                        'picker': picker_items,  # Include all items
                        'title': data.get('filename', 'image')
                    }
            
            return {
                'success': False,
                'error': 'لم يتم العثور على ملف للتنزيل',
                'platform': platform
            }
            
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'انتهت مهلة الاتصال. حاول مرة أخرى.',
                'platform': platform if 'platform' in locals() else None
            }
        except Exception as e:
            logger.error(f"Download error: {e}")
            return {
                'success': False,
                'error': f'حدث خطأ: {str(e)}',
                'platform': platform if 'platform' in locals() else None
            }
    
    def download_audio(self, url: str) -> Dict:
        """
        Download audio from URL (YouTube, TikTok)
        Returns dict with status, file_url, platform, media_type
        """
        try:
            platform = self.detect_platform(url)
            if not platform:
                return {
                    'success': False,
                    'error': 'منصة غير مدعومة. الرجاء استخدام روابط من يوتيوب أو تيك توك.',
                    'platform': None
                }
            
            # Prepare request for audio download
            payload = {
                "url": url,
                "downloadMode": "audio",
                "filenameStyle": "basic",
                "audioFormat": "mp3"
            }
            
            response = requests.post(
                self.cobalt_api,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Cobalt API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': 'فشل في الاتصال بخدمة التنزيل. حاول مرة أخرى.',
                    'platform': platform
                }
            
            data = response.json()
            
            if data.get('status') == 'error':
                error_msg = data.get('text', 'حدث خطأ غير معروف')
                return {
                    'success': False,
                    'error': f'خطأ: {error_msg}',
                    'platform': platform
                }
            
            # Get audio URL
            if data.get('status') == 'redirect' or data.get('status') == 'stream':
                audio_url = data.get('url')
                if audio_url:
                    return {
                        'success': True,
                        'file_url': audio_url,
                        'platform': platform,
                        'media_type': 'audio',
                        'title': data.get('filename', 'audio')
                    }
            
            return {
                'success': False,
                'error': 'لم يتم العثور على ملف صوتي للتنزيل',
                'platform': platform
            }
            
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'انتهت مهلة الاتصال. حاول مرة أخرى.',
                'platform': platform if 'platform' in locals() else None
            }
        except Exception as e:
            logger.error(f"Audio download error: {e}")
            return {
                'success': False,
                'error': f'حدث خطأ: {str(e)}',
                'platform': platform if 'platform' in locals() else None
            }
    
    def download_images(self, url: str) -> Dict:
        """
        Download images from URL (TikTok, Instagram)
        Returns dict with status, file_urls (list), platform, media_type
        """
        try:
            platform = self.detect_platform(url)
            if not platform:
                return {
                    'success': False,
                    'error': 'منصة غير مدعومة. الرجاء استخدام روابط من تيك توك أو انستقرام.',
                    'platform': None
                }
            
            # Use the same endpoint - Cobalt will detect images
            payload = {
                "url": url,
                "downloadMode": "auto",
                "filenameStyle": "basic"
            }
            
            response = requests.post(
                self.cobalt_api,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Cobalt API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': 'فشل في الاتصال بخدمة التنزيل. حاول مرة أخرى.',
                    'platform': platform
                }
            
            data = response.json()
            
            if data.get('status') == 'error':
                error_msg = data.get('text', 'حدث خطأ غير معروف')
                return {
                    'success': False,
                    'error': f'خطأ: {error_msg}',
                    'platform': platform
                }
            
            # Check for picker (multiple images)
            if data.get('status') == 'picker':
                picker_items = data.get('picker', [])
                if picker_items:
                    image_urls = [item.get('url') for item in picker_items if item.get('url')]
                    return {
                        'success': True,
                        'file_urls': image_urls,
                        'platform': platform,
                        'media_type': 'images',
                        'count': len(image_urls),
                        'title': data.get('filename', 'images')
                    }
            
            # Single image
            if data.get('status') == 'redirect' or data.get('status') == 'stream':
                image_url = data.get('url')
                if image_url:
                    return {
                        'success': True,
                        'file_urls': [image_url],
                        'platform': platform,
                        'media_type': 'image',
                        'count': 1,
                        'title': data.get('filename', 'image')
                    }
            
            return {
                'success': False,
                'error': 'لم يتم العثور على صور للتنزيل',
                'platform': platform
            }
            
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'انتهت مهلة الاتصال. حاول مرة أخرى.',
                'platform': platform if 'platform' in locals() else None
            }
        except Exception as e:
            logger.error(f"Images download error: {e}")
            return {
                'success': False,
                'error': f'حدث خطأ: {str(e)}',
                'platform': platform if 'platform' in locals() else None
            }
