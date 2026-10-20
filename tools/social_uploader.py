import os
import sys
import argparse
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROFILE_DIR = os.path.abspath(".browser_session")

METADATA = {
    "4k-joker-curve": {
        "title": "The Only Sensible Way to Live (Joker) #Shorts",
        "caption": "See, I'm not a monster. I'm just ahead of the curve. Heath Ledger's Joker delivers one of the greatest psychological masterclasses in cinema history. 🃏🎬",
        "hashtags": ["#Shorts", "#TheDarkKnight", "#Joker", "#HeathLedger", "#Batman", "#MovieQuotes", "#Cinema", "#Trending"],
        "file": "outbox/4k-joker-curve-preset-a-minimal.mp4"
    },
    "4k-bane-darkness": {
        "title": "You Merely Adopted the Dark (Bane) #Shorts",
        "caption": "You think darkness is your ally? You merely adopted the dark. I was born in it, molded by it. Tom Hardy as Bane in Gotham's sewers. 🦇🔥",
        "hashtags": ["#Shorts", "#Bane", "#TheDarkKnightRises", "#Batman", "#TomHardy", "#MovieClips", "#Cinema", "#Trending"],
        "file": "outbox/4k-bane-darkness-preset-a-minimal.mp4"
    },
    "4k-interstellar-docking": {
        "title": "It's Not Possible. No, It's Necessary. #Shorts",
        "caption": "Cooper, what are you doing? - Docking. Pure adrenaline, Hans Zimmer's score, and Matthew McConaughey at peak tension. 🚀🌌",
        "hashtags": ["#Shorts", "#Interstellar", "#ChristopherNolan", "#MatthewMcConaughey", "#MovieClips", "#SciFi", "#Cinema", "#Trending"],
        "file": "outbox/4k-interstellar-docking-preset-a-minimal.mp4"
    },
    "4k-gladiator-maximus": {
        "title": "My Name is Maximus Decimus Meridius #Shorts",
        "caption": "Father to a murdered son, husband to a murdered wife. And I will have my vengeance, in this life or the next. Russell Crowe unmasking in the Colosseum. ⚔️🏛️",
        "hashtags": ["#Shorts", "#Gladiator", "#Maximus", "#RussellCrowe", "#Cinema", "#MovieQuotes", "#Epic"],
        "file": "outbox/4k-gladiator-maximus-preset-a-minimal.mp4"
    },
    "4k-wolf-not-leaving": {
        "title": "I'm Not Leaving! The Show Goes On! #Shorts",
        "caption": "They're gonna need a wrecking ball to take me out of here! Leonardo DiCaprio's most intense motivational chaos speech from The Wolf of Wall Street. 📈💼",
        "hashtags": ["#Shorts", "#WolfOfWallStreet", "#LeonardoDiCaprio", "#JordanBelfort", "#Motivation", "#Cinema", "#Viral"],
        "file": "outbox/4k-wolf-not-leaving-preset-a-minimal.mp4"
    }
}

def print_captions():
    print("=" * 65)
    print("VIRAL CAPTIONS & HASHTAGS READY FOR UPLOAD")
    print("=" * 65)
    for slug, data in METADATA.items():
        print(f"\n[{slug.upper()}]")
        print(f"File: {data['file']}")
        print(f"Title: {data['title']}")
        print(f"Caption: {data['caption']}")
        print(f"Hashtags: {' '.join(data['hashtags'])}")
        print("-" * 65)

def connect_accounts():
    """Opens Chrome in headed mode so user can log in to YouTube Studio and TikTok once."""
    print("\nLaunching Google Chrome with persistent session...")
    print(f"Session path: {PROFILE_DIR}")
    print("1. Log in to your YouTube Channel (studio.youtube.com).")
    print("2. Log in to your TikTok Account (@landercueto).")
    print("Once logged in, cookies will remain saved for automated uploads.")
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            channel="chrome",
            headless=False,
            args=["--start-maximized"],
            no_viewport=True
        )
        page1 = context.pages[0] if context.pages else context.new_page()
        page1.goto("https://studio.youtube.com/channel/UCuC16SCbns_CCw2F0s9Y-5Q/content?d=ud")
        
        page2 = context.new_page()
        page2.goto("https://www.tiktok.com/creator-center/upload")
        
        print("\nBrowser is open! Log into both accounts, then press ENTER in this terminal when finished.")
        try:
            input("Press ENTER to save session and close browser: ")
        except EOFError:
            time.sleep(30)
        context.close()
    print("Session saved successfully!")

def upload_youtube(slug):
    if slug not in METADATA:
        print(f"Unknown slug: {slug}. Choose from: {list(METADATA.keys())}")
        return
    meta = METADATA[slug]
    video_abs = os.path.abspath(meta["file"])
    if not os.path.exists(video_abs):
        print(f"Video file not found: {video_abs}")
        return
        
    print(f"\n[YouTube Upload] Starting upload for {slug}...")
    full_desc = f"{meta['caption']}\n\n{' '.join(meta['hashtags'])}"
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            channel="chrome",
            headless=False,
            no_viewport=True
        )
        page = context.new_page()
        print("Navigating to YouTube Studio Upload...")
        page.goto("https://studio.youtube.com/channel/UCuC16SCbns_CCw2F0s9Y-5Q/videos/upload?d=ud")
        
        # Check login
        if "accounts.google.com" in page.url or "signin" in page.url:
            print("Notice: You need to log in to YouTube Studio first. Please log in in the opened browser.")
            try:
                input("Press ENTER after completing login: ")
            except EOFError:
                time.sleep(20)
            page.goto("https://studio.youtube.com/channel/UCuC16SCbns_CCw2F0s9Y-5Q/videos/upload?d=ud")
            
        print("Uploading video file...")
        try:
            # File input selector in YouTube studio
            file_input = page.wait_for_selector("input[type='file']", timeout=15000)
            file_input.set_input_files(video_abs)
            print(f"File set: {video_abs}")
            
            # Wait for upload modal fields
            time.sleep(4)
            # Fill title
            title_box = page.wait_for_selector("#textbox[aria-label*='title' i], #title-textarea #textbox", timeout=15000)
            if title_box:
                title_box.fill("")
                title_box.type(meta["title"])
                print("Title filled.")
                
            # Fill description
            desc_box = page.query_selector("#description-textarea #textbox")
            if desc_box:
                desc_box.fill("")
                desc_box.type(full_desc)
                print("Description filled.")
                
            # Select "Not made for kids"
            not_for_kids = page.query_selector("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']")
            if not_for_kids:
                not_for_kids.click()
                print("Selected: 'Not made for kids'")
                
            print("\n[SUCCESS] Video details prepared in YouTube Studio!")
            print("Please review details on screen and select your desired Visibility (Public / Unlisted / Schedule).")
            try:
                input("Press ENTER when you are done to close browser: ")
            except EOFError:
                time.sleep(30)
        except Exception as e:
            print(f"Upload interaction step note: {e}")
            print("Leaving browser open for user manual completion...")
            try:
                input("Press ENTER to close browser: ")
            except EOFError:
                time.sleep(20)
        context.close()

def upload_tiktok(slug):
    if slug not in METADATA:
        print(f"Unknown slug: {slug}. Choose from: {list(METADATA.keys())}")
        return
    meta = METADATA[slug]
    video_abs = os.path.abspath(meta["file"])
    if not os.path.exists(video_abs):
        print(f"Video file not found: {video_abs}")
        return
        
    print(f"\n[TikTok Upload] Starting upload for {slug}...")
    caption_text = f"{meta['caption']} {' '.join(meta['hashtags'])}"
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            channel="chrome",
            headless=False,
            no_viewport=True
        )
        page = context.new_page()
        print("Navigating to TikTok Creator Center Upload...")
        page.goto("https://www.tiktok.com/creator-center/upload")
        
        if "login" in page.url:
            print("Notice: Please log in to your TikTok account in the browser window.")
            try:
                input("Press ENTER after completing login: ")
            except EOFError:
                time.sleep(20)
            page.goto("https://www.tiktok.com/creator-center/upload")
            
        print("Uploading video file to TikTok...")
        try:
            # TikTok file upload input
            file_input = page.wait_for_selector("input[type='file']", timeout=15000)
            file_input.set_input_files(video_abs)
            print(f"File set: {video_abs}")
            
            time.sleep(4)
            print("\n[SUCCESS] Video uploaded to TikTok Creator Center!")
            print(f"Suggested Caption & Hashtags:\n{caption_text}")
            print("\nReview on screen and click 'Post'.")
            try:
                input("Press ENTER when you are done to close browser: ")
            except EOFError:
                time.sleep(30)
        except Exception as e:
            print(f"TikTok upload note: {e}")
            print("Leaving browser open for user review...")
            try:
                input("Press ENTER to close browser: ")
            except EOFError:
                time.sleep(20)
        context.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated YouTube & TikTok Uploader")
    parser.add_argument("--connect", action="store_true", help="Connect and log into YouTube and TikTok")
    parser.add_argument("--captions", action="store_true", help="Print all catchy captions & hashtags")
    parser.add_argument("--upload-yt", type=str, help="Upload a clip to YouTube (e.g. 4k-joker-curve)")
    parser.add_argument("--upload-tiktok", type=str, help="Upload a clip to TikTok (e.g. 4k-joker-curve)")
    args = parser.parse_args()
    
    if args.connect:
        connect_accounts()
    elif args.upload_yt:
        upload_youtube(args.upload_yt)
    elif args.upload_tiktok:
        upload_tiktok(args.upload_tiktok)
    else:
        print_captions()
