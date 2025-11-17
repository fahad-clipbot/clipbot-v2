"""
Media downloader using yt-dlp
Supports YouTube, TikTok, Instagram, and more
"""

import logging
import subprocess
import json
import os
import tempfile
from pathlib import Path
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class MediaDownloader:
    def __init__(self):
        self.platform_domains = {
            'youtube': ['youtube.com', 'youtu.be'],
            'tiktok': ['tiktok.com', 'vt.tiktok.com'],
            'instagram': ['instagram.com']
        }
    
    def detect_platform(self, url: str) -> str:
        """Detect platform from URL"""
        try:
            domain = urlparse(url).netloc.lower()
            for platform, domains in self.platform_domains.items():
                if any(d in domain for d in domains):
                    return platform
            return 'unknown'
        except:
            return 'unknown'
    
    def is_supported(self, url: str) -> bool:
        """Check if URL is from a supported platform"""
        return self.detect_platform(url) != 'unknown'
    
    def download_video(self, url: str, output_path: str = None) -> dict:
        """
        Download video using yt-dlp
        
        Args:
            url: Video URL
            output_path: Optional output directory
            
        Returns:
            dict with status, platform, file_url and other info
        """
        try:
            platform = self.detect_platform(url)
            
            if not self.is_supported(url):
                return {
                    'success': False,
                    'error': 'Unsupported platform',
                    'platform': platform
                }
            
            # Create temp directory if no output path specified
            if output_path is None:
                output_path = tempfile.mkdtemp()
            
            # Output template
            output_template = os.path.join(output_path, '%(title)s.%(ext)s')
            
            # yt-dlp command
            cmd = [
                'yt-dlp',
                '--no-playlist',
                '--format', 'best[ext=mp4]/best',
                '--output', output_template,
                '--print', 'after_move:filepath',
                url
            ]
            
            # Run yt-dlp
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode != 0:
                logger.error(f"yt-dlp error: {result.stderr}")
                return {
                    'success': False,
                    'error': 'Download failed',
                    'platform': platform
                }
            
            # Get file path from output
            file_path = result.stdout.strip().split('\n')[-1]
            
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': 'File not found after download',
                    'platform': platform
                }
            
            return {
                'success': True,
                'file_path': file_path,
                'file_url': file_path,  # For compatibility with bot.py
                'filename': os.path.basename(file_path),
                'platform': platform,
                'media_type': 'video'
            }
            
        except subprocess.TimeoutExpired:
            logger.error("Download timeout")
            return {
                'success': False,
                'error': 'Download timeout',
                'platform': self.detect_platform(url)
            }
        except Exception as e:
            logger.error(f"Download error: {e}")
            return {
                'success': False,
                'error': str(e),
                'platform': self.detect_platform(url)
            }
    
    def download_audio(self, url: str, output_path: str = None) -> dict:
        """
        Download audio only using yt-dlp
        
        Args:
            url: Video URL
            output_path: Optional output directory
            
        Returns:
            dict with status, platform, file_url and other info
        """
        try:
            platform = self.detect_platform(url)
            
            if not self.is_supported(url):
                return {
                    'success': False,
                    'error': 'Unsupported platform',
                    'platform': platform
                }
            
            # Create temp directory if no output path specified
            if output_path is None:
                output_path = tempfile.mkdtemp()
            
            # Output template
            output_template = os.path.join(output_path, '%(title)s.%(ext)s')
            
            # yt-dlp command for audio
            cmd = [
                'yt-dlp',
                '--no-playlist',
                '--extract-audio',
                '--audio-format', 'mp3',
                '--audio-quality', '0',  # Best quality
                '--output', output_template,
                '--print', 'after_move:filepath',
                url
            ]
            
            # Run yt-dlp
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode != 0:
                logger.error(f"yt-dlp error: {result.stderr}")
                return {
                    'success': False,
                    'error': 'Download failed',
                    'platform': platform
                }
            
            # Get file path from output
            file_path = result.stdout.strip().split('\n')[-1]
            
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': 'File not found after download',
                    'platform': platform
                }
            
            return {
                'success': True,
                'file_path': file_path,
                'file_url': file_path,  # For compatibility with bot.py
                'filename': os.path.basename(file_path),
                'platform': platform,
                'media_type': 'audio'
            }
            
        except subprocess.TimeoutExpired:
            logger.error("Download timeout")
            return {
                'success': False,
                'error': 'Download timeout',
                'platform': self.detect_platform(url)
            }
        except Exception as e:
            logger.error(f"Download error: {e}")
            return {
                'success': False,
                'error': str(e),
                'platform': self.detect_platform(url)
            }
    
    def get_info(self, url: str) -> dict:
        """
        Get video information without downloading
        
        Args:
            url: Video URL
            
        Returns:
            dict with video info or error
        """
        try:
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-playlist',
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
                    'error': 'Failed to get info'
                }
            
            info = json.loads(result.stdout)
            
            return {
                'success': True,
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
                'uploader': info.get('uploader', 'Unknown'),
                'platform': self.detect_platform(url)
            }
            
        except Exception as e:
            logger.error(f"Get info error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
