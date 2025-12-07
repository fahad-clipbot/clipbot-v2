import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

def set_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    response = requests.post(url, data={"url": WEBHOOK_URL})
    print("Webhook response:", response.json())

if __name__ == "__main__":
    set_webhook()
