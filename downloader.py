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

logger = logging.getLogger(__name__)

class MediaDownloader:
    def __init__(self):
        self.supported_platforms = [
            'youtube.com', 'youtu.be',
            'tiktok.com', 'vt.tiktok.com',
            'instagram.com'
        ]
    
    def is_supported(self, url: str) -> bool:
        """Check if URL is from a supported platform"""
        return any(platform in url.lower() for platform in self.supported_platforms)
    
    def download_video(self, url: str, output_path: str = None) -> dict:
        """
        Download video using yt-dlp
        
        Args:
            url: Video URL
            output_path: Optional output directory
            
        Returns:
            dict with status and file path or error
        """
        try:
            if not self.is_supported(url):
                return {
                    'success': False,
                    'error': 'Unsupported platform'
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
                    'error': 'Download failed'
                }
            
            # Get file path from output
            file_path = result.stdout.strip().split('\n')[-1]
            
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': 'File not found after download'
                }
            
            return {
                'success': True,
                'file_path': file_path,
                'filename': os.path.basename(file_path)
            }
            
        except subprocess.TimeoutExpired:
            logger.error("Download timeout")
            return {
                'success': False,
                'error': 'Download timeout'
            }
        except Exception as e:
            logger.error(f"Download error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def download_audio(self, url: str, output_path: str = None) -> dict:
        """
        Download audio only using yt-dlp
        
        Args:
            url: Video URL
            output_path: Optional output directory
            
        Returns:
            dict with status and file path or error
        """
        try:
            if not self.is_supported(url):
                return {
                    'success': False,
                    'error': 'Unsupported platform'
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
                    'error': 'Download failed'
                }
            
            # Get file path from output
            file_path = result.stdout.strip().split('\n')[-1]
            
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': 'File not found after download'
                }
            
            return {
                'success': True,
                'file_path': file_path,
                'filename': os.path.basename(file_path)
            }
            
        except subprocess.TimeoutExpired:
            logger.error("Download timeout")
            return {
                'success': False,
                'error': 'Download timeout'
            }
        except Exception as e:
            logger.error(f"Download error: {e}")
            return {
                'success': False,
                'error': str(e)
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
                'uploader': info.get('uploader', 'Unknown')
            }
            
        except Exception as e:
            logger.error(f"Get info error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
