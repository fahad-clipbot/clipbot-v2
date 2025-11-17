FROM python:3.11-slim

WORKDIR /app

# Copy all files first
COPY . .

# Install dependencies
RUN pip install --no-cache-dir python-telegram-bot==20.7 requests==2.31.0

# Run the bot
CMD ["python", "bot.py"]
