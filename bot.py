import os
from pyrogram import Client
from flask import Flask

# --- Flask Web Server (Render ke liye zaroori hai taaki port bind ho) ---
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is active and running!"

# --- Secure Environment Variables ---
API_ID = int(os.getenv("API_ID", "12345678"))
API_HASH = os.getenv("API_HASH", "your_telegram_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN environment variable is missing!")

# Telegram Bot Client
app = Client("insta_auto_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message()
async def start_command(client, message):
    if message.text == "/start":
        await message.reply_text("🤖 **InstaAuto Bot Dashboard**\n\nBot is running successfully on Render!")

if __name__ == "__main__":
    # Bot aur Flask ko ek sath start karne ka secure tareeqa
    import threading
    
    # Telegram bot ko background thread mein chalayein
    def run_bot():
        app.run()

    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # Flask server ko main thread par chalayein taaki Render port detect kar le
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host="0.0.0.0", port=port)
