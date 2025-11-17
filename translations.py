"""
Translations module for ClipBot V2
Supports Arabic and English
"""

TRANSLATIONS = {
    'ar': {
        # Welcome messages
        'welcome_title': '🎬 **مرحباً {name}!**',
        'welcome_intro': '''
أنا بوت تنزيل الفيديوهات والصور والأصوات من:
• يوتيوب 🎥
• تيك توك 🎵
• انستقرام 📸
''',
        'welcome_how_to': '''
**كيف تستخدمني؟**
فقط أرسل لي رابط الفيديو أو الصورة وسأقوم بتنزيله لك!
''',
        'welcome_commands': '''
**الأوامر المتاحة:**
/help - عرض المساعدة
/status - حالة حسابك وحدود التنزيل
/subscribe - الاشتراكات المدفوعة
/language - تغيير اللغة
''',
        'welcome_types': '''
**أنواع التنزيل:**
🎥 فيديو - أرسل الرابط مباشرة
🖼 صور - أرسل الرابط مباشرة
🎵 صوت - أرسل الرابط مع كلمة "صوت" أو "audio"

جرب الآن! 🚀
''',
        
        # Buttons
        'btn_help': '📖 المساعدة',
        'btn_status': '📊 حالتي',
        'btn_subscribe': '💎 الاشتراكات',
        'btn_home': '🏠 الرئيسية',
        'btn_back': '🔙 رجوع',
        'btn_language': '🌍 اللغة',
        
        # Help
        'help_title': '📖 **دليل الاستخدام**',
        'help_platforms': '''
**المنصات المدعومة:**
• يوتيوب (YouTube)
• تيك توك (TikTok)
• انستقرام (Instagram)
''',
        'help_video': '''
🎥 **تنزيل فيديو:**
فقط أرسل رابط الفيديو مباشرة

مثال:
`https://www.youtube.com/watch?v=xxxxx`
`https://www.tiktok.com/@user/video/xxxxx`
`https://www.instagram.com/p/xxxxx`
''',
        'help_images': '''
🖼 **تنزيل صور:**
أرسل رابط المنشور الذي يحتوي على صور
(تيك توك وانستقرام)
''',
        'help_audio': '''
🎵 **تنزيل صوت:**
أرسل الرابط مع كلمة "صوت" أو "audio"

مثال:
`https://www.youtube.com/watch?v=xxxxx صوت`
`audio https://www.tiktok.com/@user/video/xxxxx`
''',
        'help_commands': '''
**الأوامر:**
/start - البداية
/help - المساعدة
/status - حالة حسابك
/subscribe - الاشتراكات
/language - تغيير اللغة
''',
        'help_notes': '''
**ملاحظات:**
• الحد اليومي للتنزيل يعتمد على اشتراكك
• الجودة تعتمد على المصدر المتاح
• بعض الفيديوهات قد لا تكون متاحة للتنزيل

هل تحتاج مساعدة؟ تواصل مع الدعم! 💬
''',
        
        # Status
        'status_title': '📊 **حالة حسابك**',
        'status_user': '👤 **المستخدم:** {name}',
        'status_id': '🆔 **المعرف:** `{user_id}`',
        'status_subscription': '💎 **الاشتراك:** {tier}',
        'status_state': '📈 **الحالة:** {status}',
        'status_expires': '\nينتهي في: {days} يوم',
        'status_downloads': '📥 **التنزيلات اليوم:** {today} / {limit}',
        'status_remaining': '✨ **المتبقي:** {remaining} تنزيل',
        'status_features': '**المميزات الحالية:**',
        'status_upgrade': '\n💡 **ترقية اشتراكك للحصول على المزيد!**',
        'status_active': 'نشط ✅',
        'status_inactive': 'غير مشترك',
        
        # Subscribe
        'subscribe_title': '💎 **خطط الاشتراك**\n\nاختر الخطة المناسبة لك:',
        'subscribe_month': '/شهر',
        'subscribe_payment_title': '💳 **الدفع - {tier}**',
        'subscribe_price': 'السعر: ${price}/شهر',
        'subscribe_features': '**المميزات:**',
        'subscribe_payment_method': '''
**طريقة الدفع:**
سيتم إضافة PayPal قريباً!

في الوقت الحالي، يمكنك التواصل مع الإدارة للاشتراك.

شكراً لاهتمامك! 💙
''',
        
        # Language
        'language_title': '🌍 **اختر اللغة / Choose Language**',
        'language_changed': '✅ تم تغيير اللغة إلى العربية',
        'btn_arabic': '🇸🇦 العربية',
        'btn_english': '🇬🇧 English',
        
        # Errors
        'error_invalid_url': '❌ الرجاء إرسال رابط صحيح من يوتيوب، تيك توك، أو انستقرام.',
        'error_limit_reached': '⚠️ لقد وصلت إلى الحد اليومي ({limit} تنزيل).\n\nيمكنك الترقية لاشتراك أعلى للحصول على المزيد!\n/subscribe',
        'error_no_url': '❌ لم يتم العثور على رابط صحيح.',
        'error_download_failed': '❌ {error}',
        'error_admin_only': '❌ هذا الأمر متاح للمسؤولين فقط.',
        
        # Download
        'download_processing': '⏳ جاري المعالجة...',
        'download_sending_audio': '🎵 جاري إرسال الملف الصوتي...',
        'download_sending_video': '🎥 جاري إرسال الفيديو...',
        'download_sending_images': '🖼 جاري إرسال {count} صورة...',
        'download_success': '✅ تم التنزيل بنجاح!\n\nالمتبقي اليوم: {remaining} تنزيل',
        'download_from': 'تم التنزيل من {platform}',
        'download_image_count': '🖼 صورة {current}/{total} من {platform}',
        
        # Subscription tiers
        'tier_free': 'مجاني',
        'tier_basic': 'أساسي',
        'tier_professional': 'احترافي',
        'tier_advanced': 'متقدم',
        
        # Features
        'feature_daily_limit': '{limit} تنزيلات يومياً',
        'feature_quality_standard': 'جودة قياسية',
        'feature_quality_high': 'جودة عالية',
        'feature_quality_very_high': 'جودة عالية جداً',
        'feature_quality_best': 'أعلى جودة',
        'feature_all_platforms': 'جميع المنصات',
        'feature_priority': 'أولوية في المعالجة',
        'feature_instant': 'معالجة فورية',
        'feature_support': 'دعم أولوية',
        
        # Admin
        'admin_stats_title': '📊 **إحصائيات البوت**',
        'admin_users_title': '👥 **قائمة المستخدمين** ({count} مستخدم)',
        'admin_subs_title': '💎 **الاشتراكات** ({count} اشتراك)',
        'admin_downloads_title': '📥 **إحصائيات التنزيلات (آخر 7 أيام)**',
    },
    
    'en': {
        # Welcome messages
        'welcome_title': '🎬 **Welcome {name}!**',
        'welcome_intro': '''
I'm a bot for downloading videos, images, and audio from:
• YouTube 🎥
• TikTok 🎵
• Instagram 📸
''',
        'welcome_how_to': '''
**How to use me?**
Just send me a video or image link and I'll download it for you!
''',
        'welcome_commands': '''
**Available Commands:**
/help - Show help
/status - Your account status and download limits
/subscribe - Premium subscriptions
/language - Change language
''',
        'welcome_types': '''
**Download Types:**
🎥 Video - Send the link directly
🖼 Images - Send the link directly
🎵 Audio - Send the link with "audio" or "صوت"

Try it now! 🚀
''',
        
        # Buttons
        'btn_help': '📖 Help',
        'btn_status': '📊 My Status',
        'btn_subscribe': '💎 Subscriptions',
        'btn_home': '🏠 Home',
        'btn_back': '🔙 Back',
        'btn_language': '🌍 Language',
        
        # Help
        'help_title': '📖 **User Guide**',
        'help_platforms': '''
**Supported Platforms:**
• YouTube
• TikTok
• Instagram
''',
        'help_video': '''
🎥 **Download Video:**
Just send the video link directly

Example:
`https://www.youtube.com/watch?v=xxxxx`
`https://www.tiktok.com/@user/video/xxxxx`
`https://www.instagram.com/p/xxxxx`
''',
        'help_images': '''
🖼 **Download Images:**
Send the post link containing images
(TikTok and Instagram)
''',
        'help_audio': '''
🎵 **Download Audio:**
Send the link with "audio" or "صوت"

Example:
`https://www.youtube.com/watch?v=xxxxx audio`
`audio https://www.tiktok.com/@user/video/xxxxx`
''',
        'help_commands': '''
**Commands:**
/start - Start
/help - Help
/status - Your account status
/subscribe - Subscriptions
/language - Change language
''',
        'help_notes': '''
**Notes:**
• Daily download limit depends on your subscription
• Quality depends on available source
• Some videos may not be available for download

Need help? Contact support! 💬
''',
        
        # Status
        'status_title': '📊 **Your Account Status**',
        'status_user': '👤 **User:** {name}',
        'status_id': '🆔 **ID:** `{user_id}`',
        'status_subscription': '💎 **Subscription:** {tier}',
        'status_state': '📈 **Status:** {status}',
        'status_expires': '\nExpires in: {days} days',
        'status_downloads': '📥 **Downloads Today:** {today} / {limit}',
        'status_remaining': '✨ **Remaining:** {remaining} downloads',
        'status_features': '**Current Features:**',
        'status_upgrade': '\n💡 **Upgrade your subscription for more!**',
        'status_active': 'Active ✅',
        'status_inactive': 'Not subscribed',
        
        # Subscribe
        'subscribe_title': '💎 **Subscription Plans**\n\nChoose the plan that suits you:',
        'subscribe_month': '/month',
        'subscribe_payment_title': '💳 **Payment - {tier}**',
        'subscribe_price': 'Price: ${price}/month',
        'subscribe_features': '**Features:**',
        'subscribe_payment_method': '''
**Payment Method:**
PayPal will be added soon!

For now, you can contact admin to subscribe.

Thank you for your interest! 💙
''',
        
        # Language
        'language_title': '🌍 **Choose Language / اختر اللغة**',
        'language_changed': '✅ Language changed to English',
        'btn_arabic': '🇸🇦 العربية',
        'btn_english': '🇬🇧 English',
        
        # Errors
        'error_invalid_url': '❌ Please send a valid link from YouTube, TikTok, or Instagram.',
        'error_limit_reached': '⚠️ You have reached your daily limit ({limit} downloads).\n\nYou can upgrade to a higher subscription for more!\n/subscribe',
        'error_no_url': '❌ No valid link found.',
        'error_download_failed': '❌ {error}',
        'error_admin_only': '❌ This command is available for admins only.',
        
        # Download
        'download_processing': '⏳ Processing...',
        'download_sending_audio': '🎵 Sending audio file...',
        'download_sending_video': '🎥 Sending video...',
        'download_sending_images': '🖼 Sending {count} images...',
        'download_success': '✅ Downloaded successfully!\n\nRemaining today: {remaining} downloads',
        'download_from': 'Downloaded from {platform}',
        'download_image_count': '🖼 Image {current}/{total} from {platform}',
        
        # Subscription tiers
        'tier_free': 'Free',
        'tier_basic': 'Basic',
        'tier_professional': 'Professional',
        'tier_advanced': 'Advanced',
        
        # Features
        'feature_daily_limit': '{limit} daily downloads',
        'feature_quality_standard': 'Standard quality',
        'feature_quality_high': 'High quality',
        'feature_quality_very_high': 'Very high quality',
        'feature_quality_best': 'Best quality',
        'feature_all_platforms': 'All platforms',
        'feature_priority': 'Priority processing',
        'feature_instant': 'Instant processing',
        'feature_support': 'Priority support',
        
        # Admin
        'admin_stats_title': '📊 **Bot Statistics**',
        'admin_users_title': '👥 **Users List** ({count} users)',
        'admin_subs_title': '💎 **Subscriptions** ({count} subscriptions)',
        'admin_downloads_title': '📥 **Download Statistics (Last 7 Days)**',
    }
}

def get_text(lang: str, key: str, **kwargs) -> str:
    """
    Get translated text
    
    Args:
        lang: Language code ('ar' or 'en')
        key: Translation key
        **kwargs: Format parameters
    
    Returns:
        Translated and formatted text
    """
    # Default to Arabic if language not found
    if lang not in TRANSLATIONS:
        lang = 'ar'
    
    # Get translation
    text = TRANSLATIONS[lang].get(key, TRANSLATIONS['ar'].get(key, key))
    
    # Format with parameters
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    
    return text

def get_user_language(user_language_code: str = None) -> str:
    """
    Detect user language from Telegram language code
    
    Args:
        user_language_code: Telegram user language code
    
    Returns:
        'ar' or 'en'
    """
    if user_language_code:
        if user_language_code.startswith('ar'):
            return 'ar'
    return 'en'  # Default to English
