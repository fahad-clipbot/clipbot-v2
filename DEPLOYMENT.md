# Deployment Guide - ClipBot V2

## Prerequisites

Before deploying, you need:

1. **Telegram Bot Token**
   - Go to [@BotFather](https://t.me/BotFather)
   - Send `/newbot`
   - Follow instructions to create your bot
   - Copy the bot token

2. **Your Telegram User ID**
   - Go to [@userinfobot](https://t.me/userinfobot)
   - Send `/start`
   - Copy your user ID (this will be ADMIN_USER_ID)

## Deployment Options

### Option 1: Railway (Recommended)

Railway is the easiest way to deploy your bot.

#### Steps:

1. **Create GitHub Repository**
   ```bash
   cd /home/ubuntu/clipbot_v2
   git init
   git add .
   git commit -m "Initial commit - ClipBot V2"
   git branch -M main
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Deploy on Railway**
   - Go to [railway.app](https://railway.app)
   - Sign in with GitHub
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your clipbot_v2 repository
   - Railway will auto-detect Python and deploy

3. **Add Environment Variables**
   - In Railway dashboard, go to your project
   - Click "Variables" tab
   - Add these variables:
     ```
     BOT_TOKEN=your_bot_token_here
     ADMIN_USER_ID=your_telegram_user_id
     ```

4. **Deploy**
   - Railway will automatically deploy
   - Check logs to ensure bot is running
   - Test your bot on Telegram!

### Option 2: Heroku

1. **Install Heroku CLI**
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku App**
   ```bash
   cd /home/ubuntu/clipbot_v2
   heroku create your-bot-name
   ```

4. **Add Procfile**
   ```bash
   echo "worker: python bot.py" > Procfile
   ```

5. **Set Environment Variables**
   ```bash
   heroku config:set BOT_TOKEN=your_bot_token_here
   heroku config:set ADMIN_USER_ID=your_telegram_user_id
   ```

6. **Deploy**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

7. **Scale Worker**
   ```bash
   heroku ps:scale worker=1
   ```

### Option 3: VPS (Ubuntu/Debian)

1. **Connect to your VPS**
   ```bash
   ssh user@your-server-ip
   ```

2. **Install Python and dependencies**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip git -y
   ```

3. **Clone repository**
   ```bash
   git clone YOUR_GITHUB_REPO_URL
   cd clipbot_v2
   ```

4. **Install Python packages**
   ```bash
   pip3 install -r requirements.txt
   ```

5. **Create .env file**
   ```bash
   nano .env
   ```
   Add:
   ```
   BOT_TOKEN=your_bot_token_here
   ADMIN_USER_ID=your_telegram_user_id
   ```

6. **Run bot with systemd**
   
   Create service file:
   ```bash
   sudo nano /etc/systemd/system/clipbot.service
   ```
   
   Add:
   ```ini
   [Unit]
   Description=ClipBot V2 Telegram Bot
   After=network.target

   [Service]
   Type=simple
   User=your_username
   WorkingDirectory=/home/your_username/clipbot_v2
   ExecStart=/usr/bin/python3 /home/your_username/clipbot_v2/bot.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

7. **Start service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable clipbot
   sudo systemctl start clipbot
   sudo systemctl status clipbot
   ```

8. **View logs**
   ```bash
   sudo journalctl -u clipbot -f
   ```

### Option 4: Docker

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   CMD ["python", "bot.py"]
   ```

2. **Create docker-compose.yml**
   ```yaml
   version: '3.8'

   services:
     bot:
       build: .
       restart: always
       environment:
         - BOT_TOKEN=${BOT_TOKEN}
         - ADMIN_USER_ID=${ADMIN_USER_ID}
       volumes:
         - ./clipbot.db:/app/clipbot.db
   ```

3. **Create .env file**
   ```
   BOT_TOKEN=your_bot_token_here
   ADMIN_USER_ID=your_telegram_user_id
   ```

4. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

5. **View logs**
   ```bash
   docker-compose logs -f
   ```

## Post-Deployment

### 1. Test the Bot

Send these commands to your bot:
- `/start` - Should show welcome message
- `/help` - Should show help
- `/status` - Should show your status
- `/language` - Should show language options
- Send a YouTube URL - Should download video

### 2. Test Admin Commands

As admin user:
- `/admin_stats` - Should show statistics
- `/admin_users` - Should show user list
- `/admin_subs` - Should show subscriptions
- `/admin_downloads` - Should show download stats

### 3. Monitor Logs

Check logs regularly to ensure bot is running smoothly:

**Railway**: Check logs in dashboard
**Heroku**: `heroku logs --tail`
**VPS**: `sudo journalctl -u clipbot -f`
**Docker**: `docker-compose logs -f`

## Troubleshooting

### Bot not responding
- Check if bot token is correct
- Check if bot is running (check logs)
- Restart the bot

### Database errors
- Ensure database file has write permissions
- Check if SQLite is installed

### Download errors
- Check internet connection
- Cobalt API might be down (temporary)
- Some videos may not be available

### Admin commands not working
- Verify ADMIN_USER_ID is correct
- Check if you're using your actual Telegram user ID

## Updating the Bot

### Railway/Heroku (Git-based)
```bash
git add .
git commit -m "Update bot"
git push origin main
```
Railway/Heroku will auto-deploy.

### VPS
```bash
cd clipbot_v2
git pull
sudo systemctl restart clipbot
```

### Docker
```bash
docker-compose down
docker-compose up -d --build
```

## Backup Database

The bot uses SQLite database (`clipbot.db`). Back it up regularly:

```bash
# Copy database
cp clipbot.db clipbot_backup_$(date +%Y%m%d).db

# Or use SQLite backup command
sqlite3 clipbot.db ".backup 'clipbot_backup.db'"
```

## Security Notes

1. **Never commit .env file** - It contains sensitive tokens
2. **Keep bot token secret** - Anyone with token can control your bot
3. **Regularly update dependencies** - `pip install -r requirements.txt --upgrade`
4. **Monitor admin access** - Only trusted users should be admin

## Support

If you encounter issues:
1. Check logs first
2. Verify environment variables
3. Test with simple commands
4. Check Cobalt API status
5. Review error messages

---

Good luck with your deployment! 🚀
