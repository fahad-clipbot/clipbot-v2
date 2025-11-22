# bot_5.py
# ClipBot V2 (Bot 5) — Telegram bot with AI replies, internal storage, subscriptions, and download limits

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# Project modules (must exist in your repo)
from downloader import MediaDownloader
from translations import get_text, get_user_language as detect_lang_code
from ai_helper import ai_helper

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("ClipBotV2-Bot5")

# -----------------------------------------------------------------------------
# Internal storage (in-memory)
# -----------------------------------------------------------------------------
class Database:
    def __init__(self):
        # users: user_id -> dict
        self.users: Dict[int, Dict[str, Any]] = {}
        # downloads history (per-day count)
        self.downloads: Dict[int, List[datetime]] = {}
        # subscriptions: user_id -> dict(tier, expiry_date, status)
        self.subscriptions: Dict[int, Dict[str, Any]] = {}

    # Users
    def add_user(self, user_id: int, language_code: str, first_name: str = "", last_name: str = "", username: Optional[str] = None):
        if user_id not in self.users:
            self.users[user_id] = {
                "user_id": user_id,
                "language_code": language_code,
                "first_name": first_name or "",
                "last_name": last_name or "",
                "username": username or "",
                "tier": "free",
                "is_admin": False,
            }
            logger.info(f"New user added: {user_id}")
        else:
            # update basic fields
            self.users[user_id].update({
                "language_code": language_code,
                "first_name": first_name or self.users[user_id].get("first_name", ""),
                "last_name": last_name or self.users[user_id].get("last_name", ""),
                "username": username or self.users[user_id].get("username", ""),
            })

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self.users.get(user_id)

    def set_user_language(self, user_id: int, lang_code: str):
        if user_id in self.users:
            self.users[user_id]["language_code"] = lang_code

    def get_user_language(self, user_id: int) -> str:
        user = self.get_user(user_id)
        return user["language_code"] if user and user.get("language_code") else "ar"

    # Downloads
    def add_download(self, user_id: int):
        now = datetime.now()
        self.downloads.setdefault(user_id, []).append(now)

    def get_user_downloads_today(self, user_id: int) -> int:
        today = datetime.now().date()
        return sum(1 for t in self.downloads.get(user_id, []) if t.date() == today)

    # Subscriptions
    def set_subscription(self, user_id: int, tier: str, days: int = 30):
        expiry = datetime.now() + timedelta(days=days)
        self.subscriptions[user_id] = {
            "tier": tier,
            "expiry_date": expiry,
            "status": "active",
            "created_at": datetime.now(),
        }
        # reflect tier on user record
        if user_id in self.users:
            self.users[user_id]["tier"] = tier

    def get_active_subscription(self, user_id: int) -> Optional[Dict[str, Any]]:
        sub = self.subscriptions.get(user_id)
        if not sub:
            return None
        if sub.get("expiry_date") and sub["expiry_date"] < datetime.now():
            # auto mark inactive if expired
            sub["status"] = "expired"
            return None
        if sub.get("status") != "active":
            return None
        return sub

    # Admin helpers
    def get_all_users(self) -> List[Dict[str, Any]]:
        return list(self.users.values())

    def get_admin_stats(self) -> Dict[str, int]:
        total_users = len(self.users)
        active_subscriptions = sum(1 for s in self.subscriptions.values() if s.get("status") == "active")
        downloads_today = sum(self.get_user_downloads_today(u) for u in self.users)
        # Simple weekly/monthly approximations
        downloads_week = sum(1 for times in self.downloads.values() for t in times if (datetime.now() - t).days < 7)
        downloads_month = sum(1 for times in self.downloads.values() for t in times if (datetime.now() - t).days < 30)
        total_downloads = sum(len(times) for times in self.downloads.values())
        return {
            "total_users": total_users,
            "active_subscriptions": active_subscriptions,
            "downloads_today": downloads_today,
            "downloads_week": downloads_week,
            "downloads_month": downloads_month,
            "total_downloads": total_downloads,
        }

db = Database()
downloader = MediaDownloader()

# -----------------------------------------------------------------------------
# Subscription tiers
# -----------------------------------------------------------------------------
SUBSCRIPTION_TIERS = {
    "free": {
        "name": "Free",
        "price": 0,
        "daily_limit": 3,
        "quality": "standard",
        "priority": "normal",
        "support": "community",
        "features": ["Basic quality", "Up to 3 downloads/day"],
    },
    "basic": {
        "name": "Basic",
        "price": 5,
        "daily_limit": 10,
        "quality": "high",
        "priority": "higher",
        "support": "email",
        "features": ["High quality", "Up to 10 downloads/day", "Priority queue"],
    },
    "professional": {
        "name": "Professional",
        "price": 10,
        "daily_limit": 20,
        "quality": "very_high",
        "priority": "high",
        "support": "chat",
        "features": ["Very high quality", "Up to 20 downloads/day", "Priority support"],
    },
    "advanced": {
        "name": "Advanced",
        "price": 15,
        "daily_limit": 30,
        "quality": "best",
        "priority": "highest",
        "support": "dedicated",
        "features": ["Best quality", "Up to 30 downloads/day", "Dedicated support"],
    },
}

# -----------------------------------------------------------------------------
# Helpers: tier, limits, features
# -----------------------------------------------------------------------------
def get_user_tier(user_id: int) -> str:
    sub = db.get_active_subscription(user_id)
    if not sub:
        # fallback to user record tier or free
        user = db.get_user(user_id)
        tier = user["tier"] if user and user.get("tier") in SUBSCRIPTION_TIERS else "free"
        return tier
    # check expiry just in case
    if sub.get("expiry_date") and sub["expiry_date"] < datetime.now():
        return "free"
    return sub["tier"]

def check_download_limit(user_id: int) -> bool:
    tier = get_user_tier(user_id)
    if tier not in SUBSCRIPTION_TIERS:
        tier = "free"
    limit = SUBSCRIPTION_TIERS[tier]["daily_limit"]
    used = db.get_user_downloads_today(user_id)
    logger.info(f"User {user_id} tier={tier} used={used}/{limit}")
    return used < limit

def get_tier_features_text(tier_key: str, lang: str) -> str:
    info = SUBSCRIPTION_TIERS[tier_key]
    # If you have translation keys, map them; else use raw features
    lines = []
    lines.append(f"- {get_text(lang, 'feature_daily_limit')}: {info['daily_limit']}")
    lines.append(f"- {get_text(lang, 'feature_quality')}: {info['quality']}")
    lines.append(f"- {get_text(lang, 'feature_priority')}: {info['priority']}")
    lines.append(f"- {get_text(lang, 'feature_support')}: {info['support']}")
    # Extra features list
    for f in info.get("features", []):
        lines.append(f"- {f}")
    return "\n".join(lines)

# -----------------------------------------------------------------------------
# Command handlers
# -----------------------------------------------------------------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # detect language code from Telegram; convert to our supported key
    lang_code = detect_lang_code(user.language_code)
    db.add_user(
        user_id=user.id,
        language_code=lang_code,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
    )
    lang = db.get_user_language(user.id)

    welcome_text = (
        get_text(lang, "welcome_title", name=user.first_name) + "\n\n" +
        get_text(lang, "welcome_note") + "\n\n" +
        get_text(lang, "welcome_types")
    )
    keyboard = [
        [InlineKeyboardButton(get_text(lang, "btn_help"), callback_data="help")],
        [InlineKeyboardButton(get_text(lang, "btn_status"), callback_data="status")],
        [InlineKeyboardButton(get_text(lang, "btn_language"), callback_data="language")],
        [InlineKeyboardButton(get_text(lang, "btn_subscribe"), callback_data="subscribe")],
    ]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = db.get_user_language(user.id)
    text = (
        get_text(lang, "help_title") + "\n\n" +
        get_text(lang, "help_video") + "\n" +
        get_text(lang, "help_images") + "\n" +
        get_text(lang, "help_status") + "\n" +
        get_text(lang, "help_command")
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = db.get_user_language(user.id)

    tier = get_user_tier(user.id)
    downloads_today = db.get_user_downloads_today(user.id)
    limit = SUBSCRIPTION_TIERS.get(tier, SUBSCRIPTION_TIERS["free"])["daily_limit"]
    remaining = max(0, limit - downloads_today)

    sub = db.get_active_subscription(user.id)
    if sub:
        expiry_text = sub["expiry_date"].strftime("%Y-%m-%d %H:%M")
        status_text = (
            get_text(lang, "status_active") + "\n" +
            f"{get_text(lang, 'status_tier_info')}: {tier}\n" +
            f"{get_text(lang, 'status_expiry_info')}: {expiry_text}\n" +
            f"{get_text(lang, 'status_downloads_info')}: {downloads_today}\n" +
            f"{get_text(lang, 'status_limit_info')}: {limit}\n" +
            f"{get_text(lang, 'status_remaining_info')}: {remaining}"
        )
    else:
        status_text = (
            get_text(lang, "status_inactive") + "\n\n" +
            f"{get_text(lang, 'status_tier_info')}: {tier}\n" +
            f"{get_text(lang, 'status_downloads_info')}: {downloads_today}\n" +
            f"{get_text(lang, 'status_limit_info')}: {limit}\n" +
            f"{get_text(lang, 'status_remaining_info')}: {remaining}"
        )
    await update.message.reply_text(status_text, parse_mode="Markdown")

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = db.get_user_language(user.id)
    text = get_text(lang, "language_title")
    keyboard = [
        [InlineKeyboardButton(get_text(lang, "btn_lang_ar"), callback_data="lang_ar")],
        [InlineKeyboardButton(get_text(lang, "btn_lang_en"), callback_data="lang_en")],
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = db.get_user_language(user.id)

    text = get_text(lang, "subscribe_title") + "\n\n"
    keyboard = []
    for tier_key, info in SUBSCRIPTION_TIERS.items():
        if tier_key == "free":
            continue
        tier_name = info["name"]
        price = info["price"]
        keyboard.append([InlineKeyboardButton(f"{tier_name} - ${price}", callback_data=f"sub_{tier_key}")])

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# -----------------------------------------------------------------------------
# Callback query handler
# -----------------------------------------------------------------------------
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    lang = db.get_user_language(user.id)
    data = query.data

    try:
        if data == "help":
            await query.answer()
            await help_command(update, context)

        elif data == "status":
            await query.answer()
            await status_command(update, context)

        elif data == "language":
            await query.answer()
            # Show language options
            text = get_text(lang, "language_title")
            keyboard = [
                [InlineKeyboardButton(get_text(lang, "btn_lang_ar"), callback_data="lang_ar")],
                [InlineKeyboardButton(get_text(lang, "btn_lang_en"), callback_data="lang_en")],
            ]
            await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

        elif data.startswith("lang_"):
            await query.answer()
            new_lang = data.replace("lang_", "")
            db.set_user_language(user.id, new_lang)
            confirmation = get_text(new_lang, "language_changed")
            await query.message.edit_text(confirmation, parse_mode="Markdown")

        elif data == "subscribe":
            await query.answer()
            text = get_text(lang, "subscribe_title") + "\n\n"
            keyboard = []
            for tier_key, info in SUBSCRIPTION_TIERS.items():
                if tier_key == "free":
                    continue
                tier_name = info["name"]
                price = info["price"]
                keyboard.append([InlineKeyboardButton(f"{tier_name} - ${price}", callback_data=f"sub_{tier_key}")])
            await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

        elif data.startswith("sub_"):
            await query.answer()
            tier = data.replace("sub_", "")
            info = SUBSCRIPTION_TIERS.get(tier)
            if not info:
                await query.message.reply_text(get_text(lang, "error_invalid_tier"))
                return

            # For now, directly grant subscription (since internal storage, no payment)
            db.set_subscription(user.id, tier, days=30)
            features_text = get_tier_features_text(tier, lang)
            text = (
                get_text(lang, "subscribe_success", tier=tier, price=info["price"]) + "\n\n" +
                get_text(lang, "subscribe_payment_tier_features") + "\n" +
                features_text
            )
            await query.message.edit_text(text, parse_mode="Markdown")

        else:
            await query.answer()
            await query.message.reply_text(get_text(lang, "error_unknown_action"))

    except Exception as e:
        logger.exception(f"Error in callback: {e}")
        await query.message.reply_text(get_text(lang, "error_generic"))

# -----------------------------------------------------------------------------
# AI-powered message handler + downloads
# -----------------------------------------------------------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message
    if not message or not message.text:
        return

    # ensure user exists
    lang_code = detect_lang_code(user.language_code)
    db.add_user(user.id, lang_code, user.first_name, user.last_name, user.username)
    lang = db.get_user_language(user.id)

    text = message.text.strip()

    # AI analysis
    analysis = {}
    try:
        analysis = ai_helper.analyze_message(text, lang)
    except Exception as e:
        logger.warning(f"AI analyze failed: {e}")
        analysis = {"intent": "unknown", "just_urls": []}

    # Handle intents
    intent = analysis.get("intent")
    if intent == "greeting":
        await message.reply_text(get_text(lang, "welcome"))
        return
    elif intent == "help":
        await help_command(update, context)
        return
    elif intent == "question":
        try:
            smart = ai_helper.generate_smart_response(text, lang)
            if smart:
                await message.reply_text(smart)
                # continue to URL handling if any present
        except Exception as e:
            logger.warning(f"AI smart reply failed: {e}")

    # Extract URL(s)
    urls = analysis.get("just_urls") or []
    if not urls:
        # No URL: provide helpful hint
        await message.reply_text(get_text(lang, "hint_send_link"))
        return

    url = urls[0]

    # Check limits
    if not check_download_limit(user.id):
        tier = get_user_tier(user.id)
        limit = SUBSCRIPTION_TIERS[tier]["daily_limit"]
        await message.reply_text(get_text(lang, "error_limit", limit=limit))
        return

    # Processing message
    processing = await message.reply_text(get_text(lang, "download_processing"))

    # Download via downloader
    try:
        result = downloader.download(url, audio_only=False)
        if not result or not result.get("success"):
            await processing.edit_text(get_text(lang, "error_download_failed"))
            return

        platform = result.get("platform", "unknown")
        media_type = result.get("media_type", "video")
        file_path = result.get("file_path")

        # Record download
        db.add_download(user.id)

        # Send media
        if media_type == "audio":
            await processing.edit_text(get_text(lang, "download_done", platform=platform))
            await message.reply_audio(audio=open(file_path, "rb"), caption=get_text(lang, "download_from", platform=platform))
        elif media_type == "video":
            await processing.edit_text(get_text(lang, "download_done", platform=platform))
            await message.reply_video(video=open(file_path, "rb"), caption=get_text(lang, "download_from", platform=platform))
        elif media_type in ("image", "images"):
            await processing.edit_text(get_text(lang, "download_done", platform=platform))
            # if downloader returns multiple files, adjust accordingly
            if isinstance(file_path, list):
                for i, fp in enumerate(file_path):
                    await message.reply_photo(photo=open(fp, "rb"), caption=get_text(lang, "download_from", platform=platform) if i == 0 else "")
            else:
                await message.reply_photo(photo=open(file_path, "rb"), caption=get_text(lang, "download_from", platform=platform))
        else:
            # fallback: send as document
            await processing.edit_text(get_text(lang, "download_done", platform=platform))
            await message.reply_document(document=open(file_path, "rb"), caption=get_text(lang, "download_from", platform=platform))

        # Smart post-download suggestion
        try:
            tier = get_user_tier(user.id)
            used = db.get_user_downloads_today(user.id)
            limit = SUBSCRIPTION_TIERS[tier]["daily_limit"]
            if used >= limit - 1 and tier != "advanced":
                suggestion = ai_helper.get_smart_subscription(db.get_user(user.id))
                if suggestion:
                    await message.reply_text(suggestion)
        except Exception as e:
            logger.debug(f"Suggestion generation failed: {e}")

    except Exception as e:
        logger.exception(f"Error handling download: {e}")
        await processing.edit_text(get_text(lang, "error_generic"))

# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------
def build_application() -> Application:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN not found in environment variables.")
    app = Application.builder().token(token).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("language", language_command))
    app.add_handler(CommandHandler("subscribe", subscribe_command))

    # Callback buttons
    app.add_handler(CallbackQueryHandler(button_callback))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return app

if __name__ == "__main__":
    application = build_application()
    logger.info("Bot 5 starting...")
    application.run_polling()
