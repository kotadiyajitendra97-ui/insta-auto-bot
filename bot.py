import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread

# --- Dummy Flask Server for Render Web Service Port Binding ---
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is active and running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# --- Secure Environment Variables ---
API_ID = int(os.getenv("API_ID", "12345678"))
API_HASH = os.getenv("API_HASH", "your_telegram_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN environment variable is missing!")

app = Client("insta_auto_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    text = (
        "🤖 **InstaAuto Bot Dashboard**\n\n"
        "Welcome! Use the menu below to manage your accounts, "
        "configure profile, set queue links, and start posting reels."
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🍪 Cookie Login", callback_data="cookie_login"),
         InlineKeyboardButton("💾 Saved Logins", callback_data="saved_logins")],
        [InlineKeyboardButton("📥 Post Reels", callback_data="start_posting")],
        [InlineKeyboardButton("📦 Auto Videos", callback_data="auto_videos"),
         InlineKeyboardButton("✍️ Auto Caption", callback_data="auto_caption")],
        [InlineKeyboardButton("🖼️ Auto Thumbnail", callback_data="auto_thumbnail"),
         InlineKeyboardButton("🛡️ Auto Profile", callback_data="auto_profile")]
    ])
    await message.reply_text(text, reply_markup=keyboard)

if __name__ == "__main__":
    # Start Flask server in a separate thread so Render detects the port
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    print("🤖 Starting Telegram Bot securely...")
    app.run()
