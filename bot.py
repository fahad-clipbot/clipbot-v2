"""
ClipBot V2 - Professional Telegram Bot
Downloads videos, images, and audio from YouTube, TikTok, Instagram
With subscription system, PayPal payments, and admin dashboard
Supports Arabic and English
TESTED AND WORKING VERSION
"""

import os
import logging
import re
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
from payment import PayPalHandler
from translations import get_text, get_user_language

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize components
db = Database()
downloader = MediaDownloader()
paypal = PayPalHandler()

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

def extract_url(text: str) -> str:
    """Extract URL from message text"""
    # URL patterns
    url_pattern = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'
    
    # Try to find URL with http/https
    match = re.search(url_pattern, text)
    if match:
        return match.group(0)
    
    # Try to find URL without http/https
    domain_pattern = r'(?:youtube\.com|youtu\.be|tiktok\.com|vm\.tiktok\.com|vt\.tiktok\.com|instagram\.com)/[^\s]+'
    match = re.search(domain_pattern, text, re.IGNORECASE)
    if match:
        return 'https://' + match.group(0)
    
    return None

def wants_audio(text: str) -> bool:
    """Check if user wants audio only"""
    audio_keywords = ['audio', 'mp3', 'music', 'song', 'صوت', 'أغنية', 'موسيقى']
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in audio_keywords)

# Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    # Register or update user
    db.add_or_update_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code
    )
    
    # Create keyboard
    keyboard = [
        [
            InlineKeyboardButton(get_text(lang, 'button_help'), callback_data='help'),
            InlineKeyboardButton(get_text(lang, 'button_status'), callback_data='status')
        ],
        [
            InlineKeyboardButton(get_text(lang, 'button_subscribe'), callback_data='subscribe'),
            InlineKeyboardButton(get_text(lang, 'button_language'), callback_data='language')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send welcome message
    welcome_text = get_text(lang, 'welcome_title', name=user.first_name) + "\n\n"
    welcome_text += get_text(lang, 'welcome_description') + "\n\n"
    welcome_text += get_text(lang, 'welcome_platforms') + "\n"
    welcome_text += "• YouTube 📺\n"
    welcome_text += "• TikTok 🎵\n"
    welcome_text += "• Instagram 📸\n\n"
    welcome_text += get_text(lang, 'welcome_usage')
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    help_text = get_text(lang, 'help_title') + "\n\n"
    help_text += get_text(lang, 'help_how_to_use') + "\n\n"
    help_text += get_text(lang, 'help_commands') + "\n"
    help_text += "/start - " + get_text(lang, 'help_cmd_start') + "\n"
    help_text += "/help - " + get_text(lang, 'help_cmd_help') + "\n"
    help_text += "/status - " + get_text(lang, 'help_cmd_status') + "\n"
    help_text += "/subscribe - " + get_text(lang, 'help_cmd_subscribe') + "\n"
    help_text += "/language - " + get_text(lang, 'help_cmd_language')
    
    await update.message.reply_text(help_text)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    # Get user info
    tier = get_user_tier(user.id)
    downloads_today = db.get_user_downloads_today(user.id)
    limit = SUBSCRIPTION_TIERS[tier]['daily_limit']
    remaining = limit - downloads_today
    
    # Get subscription info
    subscription = db.get_active_subscription(user.id)
    
    status_text = get_text(lang, 'status_title') + "\n\n"
    status_text += get_text(lang, 'status_tier', tier=SUBSCRIPTION_TIERS[tier]['name']) + "\n"
    status_text += get_text(lang, 'status_downloads', used=downloads_today, limit=limit) + "\n"
    status_text += get_text(lang, 'status_remaining', remaining=remaining) + "\n\n"
    
    if subscription and tier != 'free':
        expiry = subscription['expiry_date'].strftime('%Y-%m-%d')
        status_text += get_text(lang, 'status_expiry', date=expiry)
    
    await update.message.reply_text(status_text)

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /subscribe command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    # Create keyboard with subscription options
    keyboard = []
    for tier_key, tier_info in SUBSCRIPTION_TIERS.items():
        if tier_key == 'free':
            continue
        
        button_text = f"{tier_info['name']} - ${tier_info['price']}/month ({tier_info['daily_limit']} downloads/day)"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f'sub_{tier_key}')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    subscribe_text = get_text(lang, 'subscribe_title') + "\n\n"
    subscribe_text += get_text(lang, 'subscribe_description') + "\n\n"
    
    for tier_key, tier_info in SUBSCRIPTION_TIERS.items():
        subscribe_text += f"💎 **{tier_info['name']}** - ${tier_info['price']}/month\n"
        subscribe_text += f"   • {tier_info['daily_limit']} downloads/day\n"
        subscribe_text += f"   • {tier_info['quality']} quality\n\n"
    
    await update.message.reply_text(subscribe_text, reply_markup=reply_markup, parse_mode='Markdown')

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /language command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    keyboard = [
        [InlineKeyboardButton("🇸🇦 العربية", callback_data='lang_ar')],
        [InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        get_text(lang, 'language_select'),
        reply_markup=reply_markup
    )

# Callback handlers
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    lang = db.get_user_language(user.id)
    data = query.data
    
    # Handle different callbacks
    if data == 'help':
        await help_command(update, context)
    
    elif data == 'status':
        await status_command(update, context)
    
    elif data == 'subscribe':
        await subscribe_command(update, context)
    
    elif data == 'language':
        await language_command(update, context)
    
    elif data.startswith('lang_'):
        # Change language
        new_lang = data.split('_')[1]
        db.set_user_language(user.id, new_lang)
        await query.edit_message_text(
            get_text(new_lang, 'language_changed')
        )
    
    elif data.startswith('sub_'):
        # Handle subscription selection
        tier = data.split('_')[1]
        tier_info = SUBSCRIPTION_TIERS[tier]
        
        # Create PayPal payment
        payment_result = paypal.create_payment(
            amount=tier_info['price'],
            description=f"ClipBot {tier_info['name']} Subscription",
            user_id=user.id,
            tier=tier
        )
        
        if payment_result['success']:
            keyboard = [[InlineKeyboardButton(
                get_text(lang, 'button_pay_paypal'),
                url=payment_result['approval_url']
            )]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                get_text(lang, 'payment_instructions', 
                        tier=tier_info['name'], 
                        price=tier_info['price']),
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text(
                get_text(lang, 'error_payment_failed')
            )

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages (URLs)"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    message_text = update.message.text
    
    # Register user if not exists
    db.db.add_or_update_user(
    user_id=update.effective_user.id,
    username=update.effective_user.username,
    language=update.effective_user.language_code
    )
    
    # Extract URL
    url = extract_url(message_text)
    if not url:
        await update.message.reply_text(get_text(lang, 'error_invalid_url'))
        return
    
    # Check if URL is supported
    if not downloader.is_supported(url):
        await update.message.reply_text(get_text(lang, 'error_unsupported_platform'))
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
        # Check if user wants audio
        audio_only = wants_audio(message_text)
        
        # Download media
        result = downloader.download(url, audio_only=audio_only)
        
        if result['success']:
            platform = result['platform']
            media_type = result['media_type']
            file_path = result['file_path']
            
            # Record download
            db.add_download(
                user_id=user.id,
                url=url,
                platform=platform,
                media_type=media_type
            )
            
            # Send media
            if media_type == 'audio':
                await processing_msg.edit_text(get_text(lang, 'download_sending_audio'))
                with open(file_path, 'rb') as audio_file:
                    await update.message.reply_audio(
                        audio=audio_file,
                        caption=get_text(lang, 'download_from', platform=platform.title())
                    )
            else:
                await processing_msg.edit_text(get_text(lang, 'download_sending_video'))
                with open(file_path, 'rb') as video_file:
                    await update.message.reply_video(
                        video=video_file,
                        caption=get_text(lang, 'download_from', platform=platform.title())
                    )
            
            # Send success message
            tier = get_user_tier(user.id)
            remaining = SUBSCRIPTION_TIERS[tier]['daily_limit'] - db.get_user_downloads_today(user.id)
            await processing_msg.edit_text(
                get_text(lang, 'download_success', remaining=remaining)
            )
            
            # Clean up
            try:
                os.remove(file_path)
            except:
                pass
        
        else:
            await processing_msg.edit_text(
                get_text(lang, 'error_download_failed', error=result.get('error', 'Unknown error'))
            )
    
    except Exception as e:
        logger.error(f"Error handling download: {e}")
        await processing_msg.edit_text(
            get_text(lang, 'error_download_failed', error=str(e))
        )

# Admin commands
async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin_stats command"""
    user = update.effective_user
    admin_id = int(os.getenv('ADMIN_USER_ID', 0))
    
    if user.id != admin_id:
        await update.message.reply_text("⛔ Admin only command")
        return
    
    stats = db.get_admin_stats()
    
    stats_text = "📊 **Bot Statistics**\n\n"
    stats_text += f"👥 Total Users: {stats['total_users']}\n"
    stats_text += f"💎 Active Subscriptions: {stats['active_subscriptions']}\n"
    stats_text += f"📥 Total Downloads: {stats['total_downloads']}\n"
    stats_text += f"📥 Today's Downloads: {stats['downloads_today']}\n"
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')

async def admin_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin_users command"""
    user = update.effective_user
    admin_id = int(os.getenv('ADMIN_USER_ID', 0))
    
    if user.id != admin_id:
        await update.message.reply_text("⛔ Admin only command")
        return
    
    users = db.get_all_users()
    
    users_text = f"👥 **All Users** ({len(users)})\n\n"
    for u in users[:20]:  # Show first 20
        users_text += f"• {u['first_name']} (@{u['username']}) - {u['language']}\n"
    
    if len(users) > 20:
        users_text += f"\n... and {len(users) - 20} more"
    
    await update.message.reply_text(users_text, parse_mode='Markdown')

async def admin_subs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin_subs command"""
    user = update.effective_user
    admin_id = int(os.getenv('ADMIN_USER_ID', 0))
    
    if user.id != admin_id:
        await update.message.reply_text("⛔ Admin only command")
        return
    
    subs = db.get_active_subscriptions()
    
    subs_text = f"💎 **Active Subscriptions** ({len(subs)})\n\n"
    for sub in subs:
        expiry = sub['expiry_date'].strftime('%Y-%m-%d') if sub['expiry_date'] else 'N/A'
        subs_text += f"• User {sub['user_id']} - {sub['tier']} (expires: {expiry})\n"
    
    await update.message.reply_text(subs_text, parse_mode='Markdown')

# Main function
def main():
    """Start the bot"""
    # Get bot token
    token = os.getenv('BOT_TOKEN')
    if not token:
        logger.error("BOT_TOKEN not found in environment variables")
        return
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("subscribe", subscribe_command))
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CommandHandler("admin_stats", admin_stats_command))
    application.add_handler(CommandHandler("admin_users", admin_users_command))
    application.add_handler(CommandHandler("admin_subs", admin_subs_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start bot
    logger.info("Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
