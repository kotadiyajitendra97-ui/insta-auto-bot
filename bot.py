import os
import time
import asyncio
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from instagrapi import Client as InstaClient
from threading import Thread
from flask import Flask

# --- Dummy Flask Server for Free Web Service Port Binding ---
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is active and running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host="0.0.0.0", port=port)

# --- Secure Environment Variables ---
API_ID = int(os.getenv("API_ID", "12345678"))
API_HASH = os.getenv("API_HASH", "your_telegram_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN environment variable is missing!")

app = Client("insta_auto_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# In-memory database
USER_DB = {
    "accounts": {},      
    "links_queue": [],   
    "settings": {
        "caption": "Link in bio 🔥",
        "thumbnail": None,
        "dp": None,
        "bio": "Automated via Telegram Bot 🚀"
    }
}

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

@app.on_callback_query(filters.regex("saved_logins"))
async def saved_logins_menu(client, callback_query):
    accounts = list(USER_DB["accounts"].keys())
    
    if not accounts:
        await callback_query.message.edit_text(
            "💾 **Saved Logins**\n\nNo saved logins yet. Please login using cookies.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="menu_back")]])
        )
        return

    text = "💾 **Saved Logins**\n\nTap an account to remove or manage:\n"
    keyboard = []
    for idx, acc in enumerate(accounts, start=1):
        text += f"{idx}. @{acc}\n"
        keyboard.append([InlineKeyboardButton(f"❌ Remove @{acc}", callback_data=f"del_acc_{acc}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Menu", callback_data="menu_back")])
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

@app.on_callback_query(filters.regex("menu_back"))
async def back_to_menu(client, callback_query):
    await start_command(client, callback_query.message)

if __name__ == "__main__":
    # Start Flask server in background thread so Render detects the port
    t = Thread(target=run_flask)
    t.start()
    
    print("🤖 Telegram Bot & Web Server running securely...")
    app.run()
