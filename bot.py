import os
import time
import asyncio
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from instagrapi import Client as InstaClient

# --- Telegram Bot Configuration ---
# Apni Telegram Bot Token aur API credentials yahan dalein
API_ID = 12345678  # Apna Telegram api_id dalein
API_HASH = "your_telegram_api_hash"
BOT_TOKEN = "your_telegram_bot_token"

app = Client("insta_auto_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# In-memory database (Aap ise SQLite ya MongoDB se replace kar sakte hain)
USER_DB = {
    "accounts": {},      # {username: sessionid}
    "links_queue": [],   # List of Telegram post links
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

@app.on_callback_query(filters.regex("del_acc_"))
async def delete_account(client, callback_query):
    acc_to_remove = callback_query.data.replace("del_acc_", "")
    if acc_to_remove in USER_DB["accounts"]:
        del USER_DB["accounts"][acc_to_remove]
        await callback_query.answer(f"Account @{acc_to_remove} deleted successfully!", show_alert=True)
    await saved_logins_menu(client, callback_query)

@app.on_callback_query(filters.regex("start_posting"))
async def start_posting_process(client, callback_query):
    accounts = list(USER_DB["accounts"].keys())
    queue = USER_DB["links_queue"]

    if not accounts:
        await callback_query.answer("⚠️ Pehle koi Instagram account add karein (Cookie Login se)!", show_alert=True)
        return
    
    if not queue:
        await callback_query.answer("⚠️ Queue mein koi video links nahi hain!", show_alert=True)
        return

    await callback_query.message.edit_text("🚀 **Posting Started...**\nBot background mein reels post karna shuru kar raha hai.")

    # Active account (Example: pehla account)
    active_username = accounts[0]
    sessionid = USER_DB["accounts"][active_username]

    # Instagrapi Login
    cl = InstaClient()
    try:
        cl.login_by_sessionid(sessionid)
    except Exception as e:
        await callback_query.message.reply_text(f"🚨 **Instagram Auth Error:**\n`{str(e)}`")
        return

    # Set Profile (DP & Bio)
    settings = USER_DB["settings"]
    try:
        if settings["dp"] and Path(settings["dp"]).exists():
            cl.account_change_picture(settings["dp"])
        if settings["bio"]:
            cl.account_edit(biography=settings["bio"])
        await callback_query.message.reply_text("🛡️ **Profile Update Status:** DP and Bio successfully set/updated!")
    except Exception as e:
        await callback_query.message.reply_text(f"⚠️ **Profile Error:** `{str(e)}`")

    # Upload Reels with 40s Gap
    total_posted = 0
    total_links = len(queue)

    for index, link in enumerate(queue, start=1):
        try:
            await callback_query.message.reply_text(f"🔄 Processing Reel {index}/{total_links}\nLink: {link}")
            
            # Simulated video download from public channel link
            video_file = "temp_downloaded_reel.mp4"
            # Yahan aap requests ya yt-dlp use karke link se video download karenge
            
            # Uploading to Instagram
            cl.clip_upload(
                path=video_file,
                caption=settings["caption"],
                thumbnail=Path(settings["thumbnail"]) if settings["thumbnail"] else None
            )
            
            total_posted += 1
            await callback_query.message.reply_text(
                f"✅ **Reel Posted Successfully!**\n"
                f"• Total Posted: {total_posted}/{total_links}\n"
                f"• Account: @{active_username}"
            )

            # 40 seconds gap except for the last video
            if index < total_links:
                await callback_query.message.reply_text("⏳ Waiting for 40 seconds gap to protect account safety...")
                await asyncio.sleep(40)

        except Exception as e:
            # Professional raw error reporting from Instagram
            await callback_query.message.reply_text(
                f"🚨 **Instagram Error Detected:**\n`{str(e)}`\n"
                f"Posting paused or skipped for this item."
            )

    await callback_query.message.reply_text(f"🎉 **Batch Complete!** Total Reels Posted: {total_posted}")

@app.on_callback_query(filters.regex("menu_back"))
async def back_to_menu(client, callback_query):
    await start_command(client, callback_query.message)

if __name__ == "__main__":
    print("🤖 Telegram Bot is running...")
    app.run()
