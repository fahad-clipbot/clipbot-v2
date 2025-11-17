# ClipBot V2 - Telegram Media Downloader Bot

A clean, simple Telegram bot for downloading videos, images, and audio from YouTube, TikTok, and Instagram.

## Features

### User Features
- 📥 **Download Videos** from YouTube, TikTok, Instagram
- 🖼 **Download Images** from TikTok, Instagram
- 🎵 **Download Audio** from YouTube, TikTok
- 💎 **Subscription System** with 4 tiers (Free, Basic, Professional, Advanced)
- 🌍 **Multi-language Support** (Arabic & English)
- 📊 **Usage Statistics** and download limits

### Admin Features
- `/admin_stats` - Comprehensive bot statistics
- `/admin_users` - User list and details
- `/admin_subs` - Subscription management
- `/admin_downloads` - Download statistics by date

### Supported Platforms
- YouTube (videos, audio)
- TikTok (videos, images, audio)
- Instagram (videos, images)

## Installation

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd clipbot_v2
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables
```bash
cp .env.example .env
# Edit .env and add your credentials
```

Required environment variables:
- `BOT_TOKEN` - Your Telegram bot token from [@BotFather](https://t.me/BotFather)
- `ADMIN_USER_ID` - Your Telegram user ID (get it from [@userinfobot](https://t.me/userinfobot))

### 4. Run the bot
```bash
python bot.py
```

## Usage

### For Users

1. **Start the bot**: `/start`
2. **Send a link** to download:
   - For video: Just send the URL
   - For audio: Send URL with "audio" or "صوت"
   - For images: Just send the URL (TikTok/Instagram posts)

3. **Commands**:
   - `/help` - Show help and instructions
   - `/status` - Check your account status and limits
   - `/subscribe` - View subscription plans
   - `/language` - Change language (Arabic/English)

### For Admins

Admin commands (only available for ADMIN_USER_ID):
- `/admin_stats` - View bot statistics
- `/admin_users` - View all users
- `/admin_subs` - View all subscriptions
- `/admin_downloads` - View download statistics

## Subscription Tiers

| Tier | Daily Limit | Price | Features |
|------|-------------|-------|----------|
| Free | 5 downloads | $0 | Standard quality, All platforms |
| Basic | 20 downloads | $5/month | High quality, Priority processing |
| Professional | 50 downloads | $10/month | Very high quality, Instant processing |
| Advanced | 100 downloads | $15/month | Best quality, Priority support |

## Technology Stack

- **Python 3.11+**
- **python-telegram-bot** - Telegram Bot API wrapper
- **Cobalt API** - Media download service
- **SQLite** - Database for users, subscriptions, and statistics
- **requests** - HTTP library

## File Structure

```
clipbot_v2/
├── bot.py              # Main bot file with all handlers
├── database.py         # Database management
├── downloader.py       # Media downloader using Cobalt API
├── translations.py     # Multi-language support
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── README.md          # This file
└── todo.md            # Development checklist
```

## Deployment

### Railway

1. Create a new project on [Railway](https://railway.app)
2. Connect your GitHub repository
3. Add environment variables in Railway dashboard:
   - `BOT_TOKEN`
   - `ADMIN_USER_ID`
4. Deploy!

### Heroku

1. Create a new app on [Heroku](https://heroku.com)
2. Connect your GitHub repository
3. Add Config Vars in Heroku dashboard
4. Deploy from GitHub

## API Information

This bot uses the **Cobalt API** for downloading media:
- API Endpoint: `https://api.cobalt.tools/api/json`
- No API key required
- Supports YouTube, TikTok, Instagram
- Handles videos, images, and audio

## Language Support

The bot automatically detects user language from Telegram settings:
- Arabic users see Arabic interface
- English users see English interface
- Users can manually change language with `/language` command

## Database Schema

### Users Table
- user_id (PRIMARY KEY)
- username
- first_name
- last_name
- language_code
- preferred_language
- created_at
- last_active

### Subscriptions Table
- id (PRIMARY KEY)
- user_id (FOREIGN KEY)
- tier (free/basic/professional/advanced)
- start_date
- end_date
- payment_id
- status (active/expired)

### Downloads Table
- id (PRIMARY KEY)
- user_id (FOREIGN KEY)
- url
- platform (youtube/tiktok/instagram)
- media_type (video/image/audio)
- download_date
- success (boolean)

## Future Enhancements

- [ ] PayPal payment integration
- [ ] More platforms (Twitter, Facebook, etc.)
- [ ] Custom quality selection
- [ ] Batch downloads
- [ ] Download history
- [ ] User referral system

## License

MIT License

## Support

For issues or questions, contact the admin through the bot.

---

Made with ❤️ by ClipBot Team
