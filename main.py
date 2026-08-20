import os
import time
from pathlib import Path
from instagrapi import Client

def verify_and_login(sessionid_cookie: str):
    """Instagram cookie se login karke client aur username return karta hai"""
    cl = Client()
    try:
        # Cookie ke zariye Instagram login
        cl.login_by_sessionid(sessionid_cookie)
        # Account ka username fetch karna
        account_info = cl.account_info()
        username = account_info.username
        print(f"✅ Login Successful! Username: @{username}")
        return cl, username
    except Exception as e:
        print(f"❌ Instagram Error: {e}")
        return None, None

def setup_profile(cl, dp_path, bio_text):
    """DP aur Bio set karta hai professional reporting ke sath"""
    try:
        if dp_path and Path(dp_path).exists():
            cl.account_change_picture(str(dp_path))
            print("🖼️ Profile Picture (DP) successfully set!")
        
        if bio_text:
            cl.account_edit(biography=bio_text)
            print("📝 Bio successfully set!")
    except Exception as e:
        print(f"⚠️ Profile Update Error: {e}")

def upload_reels_from_queue(cl, video_links, thumbnail_path, caption_text):
    """Telegram public channel links se video download karke 40 second gap ke sath upload karta hai"""
    uploaded_count = 0
    total_videos = len(video_links)

    for index, link in enumerate(video_links, start=1):
        print(f"\n🔄 Processing Reel {index}/{total_videos}...")
        video_file = "temp_reel.mp4"
        
        try:
            # Note: Yahan aap Telegram public channel link se video download karenge
            # Example ke liye yahan direct file processing logic hai
            print(f"📥 Fetching video from link: {link}")
            
            # Simulated download (Aap yahan requests ya yt-dlp laga sakte hain)
            # Yahan hum assume kar rahe hain ki video download ho kar local save ho gayi hai.
            
            if not Path(video_file).exists():
                print(f"❌ Error: Video file could not be downloaded.")
                continue

            print("🚀 Uploading Reel to Instagram with cover photo and caption...")
            cl.clip_upload(
                path=video_file,
                caption=caption_text,
                thumbnail=Path(thumbnail_path) if thumbnail_path else None
            )
            
            uploaded_count += 1
            print(f"✨ Successfully posted Reel! Total posted: {uploaded_count}/{total_videos}")

            # Aakhiri reel ke alawa sabhi ke baad 40 seconds ka gap
            if index < total_videos:
                print("⏳ Waiting for 40 seconds gap to protect account...")
                time.sleep(40)

        except Exception as e:
            print(f"🚨 Instagram Error detected while posting reel: {e}")

        # Cleanup temp file
        if os.path.exists(video_file):
            os.remove(video_file)

    print(f"\n🎉 Process Complete! Total Reels Posted: {uploaded_count}")

if __name__ == "__main__":
    print("--- Insta Auto Bot Initialized ---")
    
    # Test variables (Aap inhe Telegram Bot ke input se connect karenge)
    SAMPLE_COOKIE = "apni_instagram_sessionid_cookie_yahan_dalein"
    SAMPLE_BIO = "Link in bio 🔥\nAutomated via Telegram Bot"
    SAMPLE_DP = "profile.jpg"
    SAMPLE_THUMBNAIL = "thumbnail.jpg"
    SAMPLE_CAPTION = "Amazing reel! #trending #reels"
    
    # Telegram channel links queue
    QUEUE_LINKS = [
        "https://t.me/your_public_channel/101",
        "https://t.me/your_public_channel/102"
    ]

    # 1. Cookie Verification & Login
    client, username = verify_and_login(SAMPLE_COOKIE)
    
    if client:
        # 2. Profile Setup (DP & Bio)
        setup_profile(client, SAMPLE_DP, SAMPLE_BIO)
        
        # 3. Reel Upload with 40s Gap
        upload_reels_from_queue(client, QUEUE_LINKS, SAMPLE_THUMBNAIL, SAMPLE_CAPTION)
