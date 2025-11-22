"""
ClipBot V2 - Clean Telegram Bot (Temporary version without PayPal)
Downloads videos, images, and audio from YouTube, TikTok, Instagram
With subscription system and admin dashboard
Supports Arabic and English
"""

import os
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from database import Database
from downloader import MediaDownloader
# TEMPORARY: Removed payment import until payment.py is uploaded
# from payment import PayPalHandler
from translations import get_text, get_user_language
from ai_helper import ai_helper

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database and downloader
db = Database()
downloader = MediaDownloader()

# Subscription tiers
SUBSCRIPTION_TIERS = {
    'free': {
        'name': 'Free',
        'price': 0,
        'daily_limit': 5,
        'quality': 'standard'
    },
    'basic': {
        'name': 'Basic',
        'price': 5,
        'daily_limit': 20,
        'quality': 'high'
    },
    'professional': {
        'name': 'Professional',
        'price': 10,
        'daily_limit': 50,
        'quality': 'very_high'
    },
    'advanced': {
        'name': 'Advanced',
        'price': 15,
        'daily_limit': 100,
        'quality': 'best'
    }
}

# Helper functions
def get_user_tier(user_id: int) -> str:
    """Get user's subscription tier"""
    subscription = db.get_active_subscription(user_id)
    if not subscription:
        return 'free'
    
    # Check if subscription is expired
    if subscription['expiry_date'] and subscription['expiry_date'] < datetime.now():
        return 'free'
    
    return subscription['tier']

def check_download_limit(user_id: int) -> bool:
    """Check if user has reached daily download limit"""
    tier = get_user_tier(user_id)
    limit = SUBSCRIPTION_TIERS[tier]['daily_limit']
    downloads_today = db.get_user_downloads_today(user_id)
    
    return downloads_today < limit

def get_tier_features(tier: str, lang: str) -> list:
    """Get list of features for a tier"""
    tier_info = SUBSCRIPTION_TIERS[tier]
    features = []
    
    # Daily limit
    features.append(
        get_text(lang, 'feature_daily_limit', limit=tier_info['daily_limit'])
    )
    
    # Quality
    quality_key = f"feature_quality_{tier_info['quality']}"
    features.append(get_text(lang, quality_key))
    
    # All platforms
    features.append(get_text(lang, 'feature_all_platforms'))
    
    # Additional features for paid tiers
    if tier == 'professional':
        features.append(get_text(lang, 'feature_priority'))
    elif tier == 'advanced':
        features.append(get_text(lang, 'feature_instant'))
        features.append(get_text(lang, 'feature_support'))
    
    return features

# Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    # Detect user language
    user_lang = get_user_language(user.language_code)
    
    # Add user to database
    db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code,
        preferred_language=user_lang
    )
    
    # Get user's preferred language
    lang = db.get_user_language(user.id)
    
    welcome_text = (
        get_text(lang, 'welcome_title', name=user.first_name) + '\n' +
        get_text(lang, 'welcome_intro') + '\n' +
        get_text(lang, 'welcome_how_to') + '\n' +
        get_text(lang, 'welcome_commands') + '\n' +
        get_text(lang, 'welcome_types')
    )
    
    keyboard = [
        [InlineKeyboardButton(get_text(lang, 'btn_help'), callback_data="help")],
        [InlineKeyboardButton(get_text(lang, 'btn_status'), callback_data="status")],
        [InlineKeyboardButton(get_text(lang, 'btn_subscribe'), callback_data="subscribe")],
        [InlineKeyboardButton(get_text(lang, 'btn_language'), callback_data="language")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    help_text = (
        get_text(lang, 'help_title') + '\n\n' +
        get_text(lang, 'help_platforms') + '\n' +
        get_text(lang, 'help_video') + '\n' +
        get_text(lang, 'help_images') + '\n' +
        get_text(lang, 'help_audio') + '\n' +
        get_text(lang, 'help_commands') + '\n' +
        get_text(lang, 'help_notes')
    )
    
    keyboard = [
        [InlineKeyboardButton(get_text(lang, 'btn_home'), callback_data="start")],
        [InlineKeyboardButton(get_text(lang, 'btn_status'), callback_data="status")],
        [InlineKeyboardButton(get_text(lang, 'btn_subscribe'), callback_data="subscribe")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Check if it's a callback query or command
    if update.callback_query:
        await update.callback_query.message.edit_text(
            help_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            help_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    # Get user info
    tier = get_user_tier(user.id)
    tier_name = get_text(lang, f'tier_{tier}')
    downloads_today = db.get_user_downloads_today(user.id)
    limit = SUBSCRIPTION_TIERS[tier]['daily_limit']
    remaining = limit - downloads_today
    
    # Get subscription info
    subscription = db.get_active_subscription(user.id)
    if subscription and subscription['expiry_date']:
        expiry_date = subscription['expiry_date'].strftime('%Y-%m-%d')
        status = get_text(lang, 'status_active')
    else:
        expiry_date = '-'
        status = get_text(lang, 'status_inactive')
    
    status_text = (
        get_text(lang, 'status_title') + '\n\n' +
        get_text(lang, 'status_tier', tier=tier_name) + '\n' +
        get_text(lang, 'status_downloads', used=downloads_today, limit=limit) + '\n' +
        get_text(lang, 'status_remaining', remaining=remaining) + '\n' +
        get_text(lang, 'status_expiry', date=expiry_date) + '\n' +
        get_text(lang, 'status_status', status=status)
    )
    
    if tier == 'free':
        status_text += get_text(lang, 'status_upgrade')
    
    keyboard = [
        [InlineKeyboardButton(get_text(lang, 'btn_home'), callback_data="start")],
        [InlineKeyboardButton(get_text(lang, 'btn_subscribe'), callback_data="subscribe")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Check if it's a callback query or command
    if update.callback_query:
        await update.callback_query.message.edit_text(
            status_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            status_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /subscribe command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    subscribe_text = get_text(lang, 'subscribe_title') + '\n'
    
    keyboard = []
    
    for tier_key, tier_info in SUBSCRIPTION_TIERS.items():
        if tier_key == 'free':
            continue
        
        tier_name = get_text(lang, f'tier_{tier_key}')
        tier_text = f"{tier_name} - ${tier_info['price']}{get_text(lang, 'subscribe_month')}"
        keyboard.append([InlineKeyboardButton(tier_text, callback_data=f"sub_{tier_key}")])
    
    keyboard.append([InlineKeyboardButton(get_text(lang, 'btn_home'), callback_data="start")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Add tier details
    for tier_key, tier_info in SUBSCRIPTION_TIERS.items():
        if tier_key == 'free':
            continue
        tier_name = get_text(lang, f'tier_{tier_key}')
        subscribe_text += f"\n**{tier_name} - ${tier_info['price']}{get_text(lang, 'subscribe_month')}**\n"
        features = get_tier_features(tier_key, lang)
        for feature in features:
            subscribe_text += f"• {feature}\n"
    
    # Check if it's a callback query or command
    if update.callback_query:
        await update.callback_query.message.edit_text(
            subscribe_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            subscribe_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /language command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    language_text = get_text(lang, 'language_title')
    
    keyboard = [
        [InlineKeyboardButton(get_text(lang, 'btn_arabic'), callback_data="lang_ar")],
        [InlineKeyboardButton(get_text(lang, 'btn_english'), callback_data="lang_en")],
        [InlineKeyboardButton(get_text(lang, 'btn_home'), callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Check if it's a callback query or command
    if update.callback_query:
        await update.callback_query.message.edit_text(
            language_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            language_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

# Callback handlers
async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    lang_code = query.data.replace('lang_', '')
    
    # Update user language
    db.set_user_language(user.id, lang_code)
    
    # Get confirmation message
    confirmation = get_text(lang_code, 'language_changed')
    
    await query.message.reply_text(confirmation)
    
    # Return to home
    await start_command(update, context)

async def handle_subscription_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle subscription tier selection"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    tier = query.data.replace('sub_', '')
    tier_info = SUBSCRIPTION_TIERS[tier]
    tier_name = get_text(lang, f'tier_{tier}')
    
    payment_text = (
        get_text(lang, 'subscribe_payment_title', tier=tier_name) + '\n\n' +
        get_text(lang, 'subscribe_price', price=tier_info['price']) + '\n\n' +
        get_text(lang, 'subscribe_features') + '\n'
    )
    
    features = get_tier_features(tier, lang)
    for feature in features:
        payment_text += f"• {feature}\n"
    
    # TEMPORARY: PayPal integration will be added soon
    payment_text += '\n\n' + '⏳ **نظام الدفع عبر PayPal سيتم إضافته قريباً!**\n\nفي الوقت الحالي، يمكنك التواصل مع الإدارة للاشتراك.'
    
    keyboard = [
        [InlineKeyboardButton(get_text(lang, 'btn_back'), callback_data="subscribe")],
        [InlineKeyboardButton(get_text(lang, 'btn_home'), callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        payment_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

# Download handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages with AI-powered understanding"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    message_text = update.message.text
    
    # Use AI to analyze message
    analysis = ai_helper.analyze_message(message_text, lang)
    
    # Handle different intents
    if analysis['intent'] == 'greeting':
        await update.message.reply_text(get_text(lang, 'welcome_title', name=user.first_name))
        return
    
    elif analysis['intent'] == 'help':
        await help_command(update, context)
        return
    
    elif analysis['intent'] == 'question':
        # Try to generate smart response
        tier = get_user_tier(user.id)
        downloads_today = db.get_user_downloads_today(user.id)
        limit = SUBSCRIPTION_TIERS[tier]['daily_limit']
        
        context_info = {
            'user_tier': tier,
            'downloads_today': downloads_today,
            'limit': limit
        }
        
        smart_response = ai_helper.generate_smart_response(message_text, context_info, lang)
        if smart_response:
            await update.message.reply_text(smart_response)
        else:
            await update.message.reply_text(get_text(lang, 'error_invalid_url'))
        return
    
    # Check if message contains URL (using AI extraction)
    urls = analysis['urls']
    if not urls:
        await update.message.reply_text(get_text(lang, 'error_invalid_url'))
        return
    
    # Validate URL
    url = urls[0]  # Use first URL found
    validation = ai_helper.validate_url(url)
    if not validation['valid']:
        await update.message.reply_text(validation['message'])
        return
    
    # Check download limit
    if not check_download_limit(user.id):
        tier = get_user_tier(user.id)
        limit = SUBSCRIPTION_TIERS[tier]['daily_limit']
        await update.message.reply_text(
            get_text(lang, 'error_limit_reached', limit=limit)
        )
        return
    
    # Send processing message
    processing_msg = await update.message.reply_text(
        get_text(lang, 'download_processing')
    )
    
    try:
        # Check if user wants audio (using AI detection)
        want_audio = analysis['wants_audio']
        
        # Download media
        result = downloader.download(message_text, audio_only=want_audio)
        
        if result['success']:
            platform = result['platform']
            media_type = result['media_type']
            
            # Record download
            db.add_download(
                user_id=user.id,
                url=message_text,
                platform=platform,
                media_type=media_type
            )
            
            # Send media based on type
            if media_type == 'audio':
                await processing_msg.edit_text(get_text(lang, 'download_sending_audio'))
                await update.message.reply_audio(
                    audio=open(result['file_path'], 'rb'),
                    caption=get_text(lang, 'download_from', platform=platform)
                )
            
            elif media_type == 'video':
                await processing_msg.edit_text(get_text(lang, 'download_sending_video'))
                await update.message.reply_video(
                    video=open(result['file_path'], 'rb'),
                    caption=get_text(lang, 'download_from', platform=platform)
                )
            
            elif media_type == 'images':
                count = len(result['file_paths'])
                await processing_msg.edit_text(
                    get_text(lang, 'download_sending_images', count=count)
                )
                
                for i, file_path in enumerate(result['file_paths'], 1):
                    await update.message.reply_photo(
                        photo=open(file_path, 'rb'),
                        caption=get_text(lang, 'download_image_count', 
                                       current=i, total=count, platform=platform)
                    )
            
            # Send success message with smart suggestions
            tier = get_user_tier(user.id)
            remaining = SUBSCRIPTION_TIERS[tier]['daily_limit'] - db.get_user_downloads_today(user.id)
            success_msg = get_text(lang, 'download_success', remaining=remaining)
            
            # Add smart subscription suggestion if applicable
            suggestion = ai_helper.suggest_subscription(db.get_user_downloads_today(user.id), 7, lang)
            if suggestion:
                success_msg += f"\n\n{suggestion}"
            
            await processing_msg.edit_text(success_msg)
            
        else:
            # Use AI to generate user-friendly error message
            error_msg = ai_helper.get_smart_error_message(result.get('error', 'Unknown error'), lang)
            await processing_msg.edit_text(error_msg)
    
    except Exception as e:
        logger.error(f"Error handling download: {e}")
        # Use AI to generate user-friendly error message
        error_msg = ai_helper.get_smart_error_message(str(e), lang)
        await processing_msg.edit_text(error_msg)

# Admin commands
async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin_stats command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    # Check if user is admin
    admin_id = int(os.getenv('ADMIN_USER_ID', 0))
    if user.id != admin_id:
        await update.message.reply_text(get_text(lang, 'error_admin_only'))
        return
    
    # Get stats
    stats = db.get_admin_stats()
    
    stats_text = (
        get_text(lang, 'admin_stats_title') + '\n\n' +
        f"👥 Total Users: {stats['total_users']}\n" +
        f"💎 Active Subscriptions: {stats['active_subscriptions']}\n" +
        f"📥 Downloads Today: {stats['downloads_today']}\n" +
        f"📊 Downloads This Week: {stats['downloads_week']}\n" +
        f"📈 Downloads This Month: {stats['downloads_month']}\n" +
        f"🎯 Total Downloads: {stats['total_downloads']}"
    )
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')

async def admin_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin_users command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    # Check if user is admin
    admin_id = int(os.getenv('ADMIN_USER_ID', 0))
    if user.id != admin_id:
        await update.message.reply_text(get_text(lang, 'error_admin_only'))
        return
    
    # Get users
    users = db.get_all_users()
    
    users_text = get_text(lang, 'admin_users_title', count=len(users)) + '\n\n'
    
    for u in users[:20]:  # Show first 20 users
        username = u['username'] or 'No username'
        tier = get_user_tier(u['user_id'])
        users_text += f"• @{username} - {tier}\n"
    
    if len(users) > 20:
        users_text += f"\n... and {len(users) - 20} more users"
    
    await update.message.reply_text(users_text, parse_mode='Markdown')

async def admin_subs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin_subs command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    # Check if user is admin
    admin_id = int(os.getenv('ADMIN_USER_ID', 0))
    if user.id != admin_id:
        await update.message.reply_text(get_text(lang, 'error_admin_only'))
        return
    
    # Get active subscriptions
    subscriptions = db.get_active_subscriptions()
    
    subs_text = get_text(lang, 'admin_subs_title', count=len(subscriptions)) + '\n\n'
    
    for sub in subscriptions:
        username = sub['username'] or 'No username'
        tier = sub['tier']
        expiry = sub['expiry_date'].strftime('%Y-%m-%d') if sub['expiry_date'] else 'N/A'
        subs_text += f"• @{username} - {tier} (expires: {expiry})\n"
    
    await update.message.reply_text(subs_text, parse_mode='Markdown')

async def admin_downloads_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin_downloads command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    # Check if user is admin
    admin_id = int(os.getenv('ADMIN_USER_ID', 0))
    if user.id != admin_id:
        await update.message.reply_text(get_text(lang, 'error_admin_only'))
        return
    
    # Get download stats
    downloads = db.get_download_stats(days=7)
    
    downloads_text = get_text(lang, 'admin_downloads_title') + '\n\n'
    
    for download in downloads:
        date = download['date']
        count = download['count']
        downloads_text += f"• {date}: {count} downloads\n"
    
    await update.message.reply_text(downloads_text, parse_mode='Markdown')

# Callback query handler
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    callback_data = query.data
    
    if callback_data == "start":
        await start_command(update, context)
    
    elif callback_data == "help":
        await help_command(update, context)
    
    elif callback_data == "status":
        await status_command(update, context)
    
    elif callback_data == "subscribe":
        await subscribe_command(update, context)
    
    elif callback_data == "language":
        await language_command(update, context)
    
    elif callback_data.startswith("lang_"):
        await handle_language_selection(update, context)
    
    elif callback_data.startswith("sub_"):
        await handle_subscription_selection(update, context)

# Main function
def main():
    """Start the bot"""
    # Get bot token from environment
    token = os.getenv('BOT_TOKEN')
    
    # Debug: Print all environment variables (without values)
    logger.info(f"Environment variables available: {', '.join(os.environ.keys())}")
    
    if not token:
        logger.error("BOT_TOKEN not found in environment variables!")
        logger.error("Please set BOT_TOKEN in Railway Variables")
        raise ValueError("BOT_TOKEN is required but not set")
    
    logger.info("BOT_TOKEN found successfully!")
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("subscribe", subscribe_command))
    application.add_handler(CommandHandler("language", language_command))
    
    # Admin commands
    application.add_handler(CommandHandler("admin_stats", admin_stats_command))
    application.add_handler(CommandHandler("admin_users", admin_users_command))
    application.add_handler(CommandHandler("admin_subs", admin_subs_command))
    application.add_handler(CommandHandler("admin_downloads", admin_downloads_command))
    
    # Message handler for URLs
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start bot
    logger.info("Bot started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
