import asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes
from telegram_handlers import handle_update

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def process_updates(app):
    updates = await app.bot.get_updates()
    for update in updates:
        await handle_update(update.to_dict())

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    await process_updates(app)

if __name__ == "__main__":
    asyncio.run(main())
