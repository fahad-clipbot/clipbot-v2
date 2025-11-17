# Quick Start Guide - ClipBot V2

Get your bot running in 5 minutes! ⚡

## Step 1: Get Bot Token (2 minutes)

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Choose a name: `My Download Bot`
4. Choose a username: `mydownloadbot` (must end with 'bot')
5. **Copy the token** - looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

## Step 2: Get Your User ID (1 minute)

1. Open Telegram and search for [@userinfobot](https://t.me/userinfobot)
2. Send `/start`
3. **Copy your ID** - looks like: `123456789`

## Step 3: Deploy on Railway (2 minutes)

### Option A: Deploy from GitHub

1. **Push code to GitHub:**
   ```bash
   cd /home/ubuntu/clipbot_v2
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Deploy on Railway:**
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Add environment variables:
     - `BOT_TOKEN`: Your bot token from Step 1
     - `ADMIN_USER_ID`: Your user ID from Step 2
   - Click "Deploy"

### Option B: Deploy with Railway CLI

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and deploy:**
   ```bash
   cd /home/ubuntu/clipbot_v2
   railway login
   railway init
   railway up
   ```

3. **Set environment variables:**
   ```bash
   railway variables set BOT_TOKEN=your_token_here
   railway variables set ADMIN_USER_ID=your_user_id_here
   ```

## Step 4: Test Your Bot! ✅

1. Open Telegram
2. Search for your bot username
3. Send `/start`
4. You should see the welcome message!

### Test Commands:

- `/start` - Welcome message
- `/help` - Help guide
- `/status` - Your account status
- `/language` - Change language
- Send a YouTube URL - Download video!

### Test Admin Commands:

- `/admin_stats` - Bot statistics
- `/admin_users` - User list
- `/admin_subs` - Subscriptions
- `/admin_downloads` - Download stats

## Common Issues

### Bot not responding?
- Check Railway logs for errors
- Verify `BOT_TOKEN` is correct
- Make sure bot is deployed and running

### Admin commands not working?
- Verify `ADMIN_USER_ID` matches your Telegram user ID
- Check if you copied the ID correctly (numbers only)

### Downloads failing?
- Some videos may not be available
- Cobalt API might be temporarily down
- Check bot logs for specific errors

## What's Next?

- ✅ Bot is running!
- 📱 Share with friends
- 💎 Set up PayPal for subscriptions (coming soon)
- 📊 Monitor usage with admin commands
- 🌍 Users can switch between Arabic/English

## File Structure

```
clipbot_v2/
├── bot.py              # Main bot (all commands and handlers)
├── database.py         # Database management
├── downloader.py       # Media downloader (Cobalt API)
├── translations.py     # Arabic & English translations
├── requirements.txt    # Python dependencies
├── Procfile           # Railway/Heroku deployment
├── .env.example       # Environment variables template
└── README.md          # Full documentation
```

## Support

Need help?
- Read the full [README.md](README.md)
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment guides
- Review Railway logs for errors

---

**Congratulations! Your bot is live! 🎉**

Now test it by sending a YouTube, TikTok, or Instagram link!
