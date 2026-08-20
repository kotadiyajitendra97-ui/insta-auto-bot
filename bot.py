import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import threading

# --- Flask Web Server (Render ke liye zaroori hai) ---
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is active and running!"

# --- Environment Variables ---
API_ID = int(os.getenv("API_ID", "12345678"))
API_HASH = os.getenv("API_HASH", "your_telegram_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN environment variable is missing!")

# Telegram Bot Client
app = Client("insta_auto_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

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

# --- Button Click Handlers ---
@app.on_callback_query(filters.regex("saved_logins"))
async def saved_logins_menu(client, callback_query):
    accounts = list(USER_DB["accounts"].keys())
    if not accounts:
        await callback_query.message.edit_text(
            "💾 **Saved Logins**\n\nNo saved logins yet. Please login using cookies.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="menu_back")]])
        )
        return

    text = "💾 **Saved Logins**\n\nTap an account to manage:\n"
    keyboard = [[InlineKeyboardButton("🔙 Menu", callback_data="menu_back")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

@app.on_callback_query(filters.regex("cookie_login"))
async def cookie_login_menu(client, callback_query):
    await callback_query.message.edit_text(
        "🍪 **Cookie Login**\n\nPlease send your Instagram cookie file or text.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="menu_back")]])
    )

@app.on_callback_query(filters.regex("start_posting"))
async def start_posting_menu(client, callback_query):
    await callback_query.message.edit_text(
        "📥 **Post Reels**\n\nNo videos in queue. Add videos to start posting.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="menu_back")]])
    )

@app.on_callback_query(filters.regex("auto_videos"))
async def auto_videos_menu(client, callback_query):
    await callback_query.message.edit_text(
        "📦 **Auto Videos Settings**\n\nConfigure your video source here.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="menu_back")]])
    )

@app.on_callback_query(filters.regex("auto_caption"))
async def auto_caption_menu(client, callback_query):
    await callback_query.message.edit_text(
        "✍️ **Auto Caption Settings**\n\nCurrent Caption: " + USER_DB["settings"]["caption"],
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="menu_back")]])
    )

@app.on_callback_query(filters.regex("auto_thumbnail"))
async def auto_thumbnail_menu(client, callback_query):
    await callback_query.message.edit_text(
        "🖼️ **Auto Thumbnail Settings**\n\nManage your reels thumbnails here.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="menu_back")]])
    )

@app.on_callback_query(filters.regex("auto_profile"))
async def auto_profile_menu(client, callback_query):
    await callback_query.message.edit_text(
        "🛡️ **Auto Profile Settings**\n\nManage bio, DP, and profile details.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="menu_back")]])
    )

@app.on_callback_query(filters.regex("menu_back"))
async def back_to_menu(client, callback_query):
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
    await callback_query.message.edit_text(text, reply_markup=keyboard)

if __name__ == "__main__":
    def run_bot():
        app.run()

    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host="0.0.0.0", port=port)
