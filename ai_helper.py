"""
AI Helper for ClipBot V2
Provides intelligent URL detection and smart responses
Uses OpenAI GPT for natural language understanding
"""

import os
import re
import logging
from typing import Dict, Optional, List
import openai

logger = logging.getLogger(__name__)

class AIHelper:
    def __init__(self):
        """Initialize AI Helper with OpenAI API"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
            self.enabled = True
            logger.info("AI Helper initialized successfully")
        else:
            self.enabled = False
            logger.warning("OPENAI_API_KEY not found. AI features disabled.")
    
    def extract_urls(self, text: str) -> List[str]:
        """
        Extract URLs from text using intelligent pattern matching
        Handles various URL formats including shortened URLs
        """
        urls = []
        
        # Pattern 1: Standard URLs with http/https
        standard_urls = re.findall(
            r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)',
            text
        )
        urls.extend(standard_urls)
        
        # Pattern 2: URLs without http/https
        domain_urls = re.findall(
            r'(?:www\.)?(?:tiktok|instagram|youtube|youtu\.be|vm\.tiktok|vt\.tiktok)\.(?:com|be)/[^\s]+',
            text,
            re.IGNORECASE
        )
        # Add https:// prefix
        urls.extend([f"https://{url}" if not url.startswith('http') else url for url in domain_urls])
        
        # Pattern 3: Shortened TikTok URLs (vm.tiktok.com, vt.tiktok.com)
        short_urls = re.findall(
            r'(?:vm|vt)\.tiktok\.com/[a-zA-Z0-9]+',
            text,
            re.IGNORECASE
        )
        urls.extend([f"https://{url}" if not url.startswith('http') else url for url in short_urls])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        return unique_urls
    
    def detect_platform(self, url: str) -> Optional[str]:
        """
        Detect the platform from URL
        Returns: 'tiktok', 'instagram', 'youtube', or None
        """
        url_lower = url.lower()
        
        if 'tiktok.com' in url_lower or 'vm.tiktok' in url_lower or 'vt.tiktok' in url_lower:
            return 'tiktok'
        elif 'instagram.com' in url_lower or 'instagr.am' in url_lower:
            return 'instagram'
        elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'youtube'
        
        return None
    
    def analyze_message(self, message: str, user_lang: str = 'ar') -> Dict:
        """
        Analyze user message to understand intent
        Returns: {
            'intent': 'download' | 'help' | 'question' | 'greeting' | 'unknown',
            'urls': List[str],
            'platform': str | None,
            'wants_audio': bool,
            'confidence': float
        }
        """
        message_lower = message.lower()
        
        # Extract URLs
        urls = self.extract_urls(message)
        
        # Detect platform
        platform = None
        if urls:
            platform = self.detect_platform(urls[0])
        
        # Detect if user wants audio
        audio_keywords_ar = ['صوت', 'اغنية', 'موسيقى', 'mp3', 'audio']
        audio_keywords_en = ['audio', 'music', 'song', 'mp3', 'sound']
        wants_audio = any(keyword in message_lower for keyword in audio_keywords_ar + audio_keywords_en)
        
        # Detect intent
        intent = 'unknown'
        confidence = 0.5
        
        if urls:
            intent = 'download'
            confidence = 0.9
        elif any(word in message_lower for word in ['مساعدة', 'help', 'كيف', 'how', 'ساعدني']):
            intent = 'help'
            confidence = 0.8
        elif any(word in message_lower for word in ['مرحبا', 'hello', 'hi', 'السلام', 'أهلا']):
            intent = 'greeting'
            confidence = 0.9
        elif '?' in message or any(word in message_lower for word in ['ماذا', 'what', 'لماذا', 'why', 'كيف', 'how']):
            intent = 'question'
            confidence = 0.7
        
        return {
            'intent': intent,
            'urls': urls,
            'platform': platform,
            'wants_audio': wants_audio,
            'confidence': confidence
        }
    
    def generate_smart_response(self, user_message: str, context: Dict, user_lang: str = 'ar') -> Optional[str]:
        """
        Generate intelligent response using GPT
        context: {
            'user_tier': str,
            'downloads_today': int,
            'limit': int,
            'last_error': str | None
        }
        """
        if not self.enabled:
            return None
        
        try:
            # Prepare system prompt
            system_prompt = f"""أنت مساعد ذكي لبوت تنزيل الفيديوهات من TikTok وInstagram وYouTube.
اسمك ClipBot V2.

معلومات المستخدم:
- الباقة: {context.get('user_tier', 'free')}
- التنزيلات اليوم: {context.get('downloads_today', 0)} من {context.get('limit', 5)}

قواعد الرد:
1. كن مختصراً ومفيداً
2. استخدم العربية إذا كان المستخدم يكتب بالعربية
3. اشرح بوضوح وبساطة
4. إذا كان السؤال عن كيفية الاستخدام، اشرح بخطوات بسيطة
5. إذا كان هناك خطأ، اقترح حلول
6. لا تتجاوز 3 أسطر في الرد

المنصات المدعومة:
- TikTok (فيديوهات وصور)
- Instagram (فيديوهات وصور)
- YouTube (فيديوهات وصوت)"""

            # Call GPT
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return None
    
    def suggest_subscription(self, downloads_today: int, days_active: int, user_lang: str = 'ar') -> Optional[str]:
        """
        Suggest appropriate subscription based on usage patterns
        """
        if downloads_today >= 5 and downloads_today < 20:
            if user_lang == 'ar':
                return "💡 **اقتراح:** يبدو أنك تستخدم البوت بشكل متكرر! باقة **Basic** ($5/شهر) ستمنحك 20 تنزيل يومياً بجودة عالية."
            else:
                return "💡 **Suggestion:** You're using the bot frequently! **Basic** plan ($5/month) gives you 20 daily downloads in high quality."
        
        elif downloads_today >= 20:
            if user_lang == 'ar':
                return "🔥 **اقتراح:** أنت مستخدم نشط جداً! باقة **Professional** ($10/شهر) أو **Advanced** ($15/شهر) ستناسبك أكثر مع حدود أعلى."
            else:
                return "🔥 **Suggestion:** You're a power user! **Professional** ($10/month) or **Advanced** ($15/month) plans offer higher limits."
        
        return None
    
    def validate_url(self, url: str) -> Dict:
        """
        Validate URL and provide feedback
        Returns: {
            'valid': bool,
            'platform': str | None,
            'message': str | None
        }
        """
        platform = self.detect_platform(url)
        
        if not platform:
            return {
                'valid': False,
                'platform': None,
                'message': 'الرابط غير مدعوم. يرجى استخدام روابط من TikTok أو Instagram أو YouTube.'
            }
        
        # Check URL format
        if platform == 'tiktok':
            if 'video' not in url and 'vm.tiktok' not in url and 'vt.tiktok' not in url and '@' not in url:
                return {
                    'valid': False,
                    'platform': platform,
                    'message': 'رابط TikTok غير صحيح. تأكد من أنه رابط فيديو أو ملف شخصي.'
                }
        
        return {
            'valid': True,
            'platform': platform,
            'message': None
        }
    
    def get_smart_error_message(self, error: str, user_lang: str = 'ar') -> str:
        """
        Generate user-friendly error message based on technical error
        """
        error_lower = error.lower()
        
        # Common errors and their user-friendly messages
        if 'network' in error_lower or 'connection' in error_lower or 'timeout' in error_lower:
            if user_lang == 'ar':
                return "⚠️ مشكلة في الاتصال بالإنترنت. يرجى المحاولة مرة أخرى بعد قليل."
            else:
                return "⚠️ Network connection issue. Please try again in a moment."
        
        elif 'not found' in error_lower or '404' in error_lower:
            if user_lang == 'ar':
                return "❌ الفيديو غير موجود أو تم حذفه. تأكد من الرابط."
            else:
                return "❌ Video not found or deleted. Please check the URL."
        
        elif 'private' in error_lower or 'unavailable' in error_lower:
            if user_lang == 'ar':
                return "🔒 هذا الفيديو خاص أو غير متاح للتنزيل."
            else:
                return "🔒 This video is private or unavailable for download."
        
        elif 'age' in error_lower or 'restricted' in error_lower:
            if user_lang == 'ar':
                return "⛔ هذا الفيديو محظور بسبب قيود العمر."
            else:
                return "⛔ This video is age-restricted."
        
        else:
            if user_lang == 'ar':
                return f"❌ حدث خطأ: {error}\n\nحاول مرة أخرى أو تواصل مع الدعم."
            else:
                return f"❌ Error: {error}\n\nTry again or contact support."

# Create singleton instance
ai_helper = AIHelper()
