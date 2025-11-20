"""
ClipBot V2 - Clean Telegram Bot
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
from payment import PayPalHandler
from translations import get_text, get_user_language

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize
db = Database()
downloader = MediaDownloader()

# Subscription tiers with limits
SUBSCRIPTION_TIERS = {
    'free': {
        'daily_limit': 5,
        'price': 0,
    },
    'basic': {
        'daily_limit': 20,
        'price': 5,
    },
    'professional': {
        'daily_limit': 50,
        'price': 10,
    },
    'advanced': {
        'daily_limit': 100,
        'price': 15,
    }
}

# Admin user ID (from environment variable)
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '0'))

# Helper functions
def get_user_tier(user_id: int) -> str:
    """Get user's subscription tier"""
    subscription = db.get_active_subscription(user_id)
    if subscription:
        return subscription['tier']
    return 'free'

def get_daily_limit(user_id: int) -> int:
    """Get user's daily download limit"""
    tier = get_user_tier(user_id)
    return SUBSCRIPTION_TIERS[tier]['daily_limit']

def check_download_limit(user_id: int) -> bool:
    """Check if user has reached daily limit"""
    downloads_today = db.get_user_downloads_today(user_id)
    limit = get_daily_limit(user_id)
    return downloads_today < limit

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id == ADMIN_USER_ID

def get_tier_features(tier: str, lang: str) -> list:
    """Get tier features in user's language"""
    tier_info = SUBSCRIPTION_TIERS[tier]
    limit = tier_info['daily_limit']
    
    features = [
        get_text(lang, 'feature_daily_limit', limit=limit),
    ]
    
    if tier == 'free':
        features.extend([
            get_text(lang, 'feature_quality_standard'),
            get_text(lang, 'feature_all_platforms')
        ])
    elif tier == 'basic':
        features.extend([
            get_text(lang, 'feature_quality_high'),
            get_text(lang, 'feature_priority')
        ])
    elif tier == 'professional':
        features.extend([
            get_text(lang, 'feature_quality_very_high'),
            get_text(lang, 'feature_instant')
        ])
    elif tier == 'advanced':
        features.extend([
            get_text(lang, 'feature_quality_best'),
            get_text(lang, 'feature_support')
        ])
    
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
    
    # Check for payment callback
    if context.args:
        arg = context.args[0]
        if arg == 'payment_success':
            await handle_payment_success(update, context)
            return
        elif arg == 'payment_cancel':
            await handle_payment_cancel(update, context)
            return
    
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
    sub_status = get_text(lang, 'status_active') if subscription else get_text(lang, 'status_inactive')
    
    if subscription:
        end_date = datetime.fromisoformat(subscription['end_date'])
        days_left = (end_date - datetime.now()).days
        sub_info = get_text(lang, 'status_expires', days=days_left)
    else:
        sub_info = ""
    
    status_text = (
        get_text(lang, 'status_title') + '\n\n' +
        get_text(lang, 'status_user', name=user.first_name) + '\n' +
        get_text(lang, 'status_id', user_id=user.id) + '\n\n' +
        get_text(lang, 'status_subscription', tier=tier_name) + '\n' +
        get_text(lang, 'status_state', status=sub_status) + sub_info + '\n\n' +
        get_text(lang, 'status_downloads', today=downloads_today, limit=limit) + '\n' +
        get_text(lang, 'status_remaining', remaining=remaining) + '\n\n' +
        get_text(lang, 'status_features') + '\n'
    )
    
    features = get_tier_features(tier, lang)
    for feature in features:
        status_text += f"• {feature}\n"
    
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

async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    new_lang = query.data.replace('lang_', '')
    
    # Update user language
    db.set_user_language(user.id, new_lang)
    
    # Send confirmation
    confirmation = get_text(new_lang, 'language_changed')
    await query.message.reply_text(confirmation)
    
    # Show start menu in new language
    update.message = query.message
    update.effective_user = user
    await start_command(update, context)

async def handle_subscription_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle subscription tier selection"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
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
    
    payment_text += '\n' + get_text(lang, 'subscribe_payment_method')
    
    # Create PayPal payment
    paypal = PayPalHandler()
    payment_result = paypal.create_payment(tier, user.id, user.username)
    
    keyboard = []
    
    if payment_result['success']:
        # Add PayPal payment button
        keyboard.append([InlineKeyboardButton(
            "💳 " + get_text(lang, 'btn_pay_paypal'),
            url=payment_result['payment_url']
        )])
        # Store order_id for verification
        context.user_data['pending_order_id'] = payment_result['order_id']
        context.user_data['pending_tier'] = tier
    else:
        payment_text += '\n\n⚠️ ' + get_text(lang, 'error_payment_failed')
    
    keyboard.append([InlineKeyboardButton(get_text(lang, 'btn_back'), callback_data="subscribe")])
    keyboard.append([InlineKeyboardButton(get_text(lang, 'btn_home'), callback_data="start")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        payment_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def handle_payment_success(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle successful payment callback"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    # Check if there's a pending order
    if 'pending_order_id' not in context.user_data:
        await update.message.reply_text(get_text(lang, 'error_no_pending_payment'))
        return
    
    order_id = context.user_data['pending_order_id']
    tier = context.user_data['pending_tier']
    
    # Verify and capture payment
    paypal = PayPalHandler()
    capture_result = paypal.capture_payment(order_id)
    
    if capture_result['success']:
        # Activate subscription
        expiry_date = datetime.now() + timedelta(days=30)
        db.update_subscription(
            user_id=user.id,
            tier=tier,
            expiry_date=expiry_date
        )
        
        tier_name = get_text(lang, f'tier_{tier}')
        success_text = get_text(lang, 'payment_success', tier=tier_name)
        
        keyboard = [
            [InlineKeyboardButton(get_text(lang, 'btn_status'), callback_data="status")],
            [InlineKeyboardButton(get_text(lang, 'btn_home'), callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            success_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        # Clear pending data
        context.user_data.pop('pending_order_id', None)
        context.user_data.pop('pending_tier', None)
        
        # Log admin notification
        logger.info(f"Payment successful: User {user.id} subscribed to {tier}")
    else:
        await update.message.reply_text(get_text(lang, 'error_payment_verification'))

async def handle_payment_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle cancelled payment"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    cancel_text = get_text(lang, 'payment_cancelled')
    
    keyboard = [
        [InlineKeyboardButton(get_text(lang, 'btn_subscribe'), callback_data="subscribe")],
        [InlineKeyboardButton(get_text(lang, 'btn_home'), callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        cancel_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    
    # Clear pending data
    context.user_data.pop('pending_order_id', None)
    context.user_data.pop('pending_tier', None)

# Download handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages with URLs"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    message_text = update.message.text
    
    # Check if message contains URL
    if not ('http://' in message_text or 'https://' in message_text):
        await update.message.reply_text(get_text(lang, 'error_invalid_url'))
        return
    
    # Check download limit
    if not check_download_limit(user.id):
        tier = get_user_tier(user.id)
        limit = SUBSCRIPTION_TIERS[tier]['daily_limit']
        await update.message.reply_text(
            get_text(lang, 'error_limit_reached', limit=limit)
        )
        return
    
    # Extract URL
    url = None
    for word in message_text.split():
        if 'http://' in word or 'https://' in word:
            url = word
            break
    
    if not url:
        await update.message.reply_text(get_text(lang, 'error_no_url'))
        return
    
    # Detect download type
    is_audio = 'صوت' in message_text or 'audio' in message_text.lower()
    
    # Send processing message
    processing_msg = await update.message.reply_text(get_text(lang, 'download_processing'))
    
    try:
        # Download based on type
        if is_audio:
            result = downloader.download_audio(url)
            media_type = 'audio'
        else:
            result = downloader.download_video(url)
            media_type = result.get('media_type', 'video')
        
        if not result['success']:
            error_msg = result['error']
            await processing_msg.edit_text(get_text(lang, 'error_download_failed', error=error_msg))
            # Record failed download
            db.add_download(
                user_id=user.id,
                url=url,
                platform=result.get('platform', 'unknown'),
                media_type=media_type,
                success=False
            )
            return
        
        platform = result['platform']
        
        # Handle different media types
        if media_type == 'audio':
            await processing_msg.edit_text(get_text(lang, 'download_sending_audio'))
            await update.message.reply_audio(
                audio=result['file_url'],
                caption=get_text(lang, 'download_from', platform=platform.upper())
            )
        
        elif media_type == 'video':
            await processing_msg.edit_text(get_text(lang, 'download_sending_video'))
            await update.message.reply_video(
                video=result['file_url'],
                caption=get_text(lang, 'download_from', platform=platform.upper())
            )
        
        elif media_type in ['image', 'images']:
            # Handle images
            file_urls = result.get('file_urls', [result.get('file_url')])
            count = len(file_urls)
            
            await processing_msg.edit_text(get_text(lang, 'download_sending_images', count=count))
            
            for idx, img_url in enumerate(file_urls[:10], 1):  # Limit to 10 images
                try:
                    await update.message.reply_photo(
                        photo=img_url,
                        caption=get_text(lang, 'download_image_count', current=idx, total=count, platform=platform.upper())
                    )
                except Exception as e:
                    logger.error(f"Error sending image {idx}: {e}")
        
        # Record successful download
        db.add_download(
            user_id=user.id,
            url=url,
            platform=platform,
            media_type=media_type,
            success=True
        )
        
        # Delete processing message
        await processing_msg.delete()
        
        # Show remaining downloads
        downloads_today = db.get_user_downloads_today(user.id)
        limit = get_daily_limit(user.id)
        remaining = limit - downloads_today
        
        await update.message.reply_text(
            get_text(lang, 'download_success', remaining=remaining)
        )
        
    except Exception as e:
        logger.error(f"Error in download handler: {e}")
        await processing_msg.edit_text(
            get_text(lang, 'error_download_failed', error=str(e))
        )

# Admin commands
async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin_stats command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    if not is_admin(user.id):
        await update.message.reply_text(get_text(lang, 'error_admin_only'))
        return
    
    stats = db.get_total_stats()
    platform_stats = db.get_downloads_by_platform()
    type_stats = db.get_downloads_by_type()
    
    stats_text = f"""
{get_text(lang, 'admin_stats_title')}

👥 **Users:**
• Total users: {stats['total_users']}
• Active today: {stats['today_active_users']}

📥 **Downloads:**
• Total downloads: {stats['total_downloads']}
• Today's downloads: {stats['today_downloads']}

💎 **Subscriptions:**
• Active subscriptions: {stats['active_subscriptions']}

📱 **By Platform:**
"""
    
    for platform in platform_stats:
        stats_text += f"• {platform['platform'].upper()}: {platform['successful']} downloads\n"
    
    stats_text += "\n🎬 **By Type:**\n"
    for media_type in type_stats:
        stats_text += f"• {media_type['media_type']}: {media_type['successful']} downloads\n"
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')

async def admin_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin_users command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    if not is_admin(user.id):
        await update.message.reply_text(get_text(lang, 'error_admin_only'))
        return
    
    users = db.get_all_users()
    
    users_text = get_text(lang, 'admin_users_title', count=len(users)) + '\n\n'
    
    for idx, u in enumerate(users[:20], 1):  # Show first 20
        username = u['username'] or 'No username'
        users_text += f"{idx}. {u['first_name']} (@{username})\n"
        users_text += f"   ID: `{u['user_id']}`\n"
        users_text += f"   Joined: {u['created_at'][:10]}\n\n"
    
    if len(users) > 20:
        users_text += f"\n... and {len(users) - 20} more users"
    
    await update.message.reply_text(users_text, parse_mode='Markdown')

async def admin_subs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin_subs command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    if not is_admin(user.id):
        await update.message.reply_text(get_text(lang, 'error_admin_only'))
        return
    
    subscriptions = db.get_all_subscriptions()
    
    subs_text = get_text(lang, 'admin_subs_title', count=len(subscriptions)) + '\n\n'
    
    for idx, sub in enumerate(subscriptions[:20], 1):  # Show first 20
        username = sub.get('username', 'No username')
        tier_name = get_text(lang, f"tier_{sub['tier']}")
        status_emoji = "✅" if sub['status'] == 'active' else "❌"
        
        subs_text += f"{idx}. {sub['first_name']} (@{username})\n"
        subs_text += f"   Plan: {tier_name} {status_emoji}\n"
        subs_text += f"   From: {sub['start_date'][:10]}\n"
        subs_text += f"   To: {sub['end_date'][:10]}\n\n"
    
    if len(subscriptions) > 20:
        subs_text += f"\n... and {len(subscriptions) - 20} more subscriptions"
    
    await update.message.reply_text(subs_text, parse_mode='Markdown')

async def admin_downloads_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin_downloads command"""
    user = update.effective_user
    lang = db.get_user_language(user.id)
    
    if not is_admin(user.id):
        await update.message.reply_text(get_text(lang, 'error_admin_only'))
        return
    
    downloads = db.get_downloads_by_date(days=7)
    
    downloads_text = get_text(lang, 'admin_downloads_title') + '\n\n'
    
    for day in downloads:
        downloads_text += f"📅 **{day['date']}**\n"
        downloads_text += f"• Total: {day['total']}\n"
        downloads_text += f"• Successful: {day['successful']}\n"
        downloads_text += f"• Users: {day['unique_users']}\n\n"
    
    await update.message.reply_text(downloads_text, parse_mode='Markdown')

# Callback query handler
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    if callback_data == "start":
        # Simulate start command
        update.message = query.message
        update.effective_user = query.from_user
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
