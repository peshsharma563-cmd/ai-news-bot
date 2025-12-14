import feedparser
import requests
import os

# --- CONFIGURATION ---
CHANNEL_ID = "@AIGlobalUpdates"  # <--- MAKE SURE THIS IS CORRECT
TEST_FEED = "https://techcrunch.com/category/artificial-intelligence/feed/"

def run_test():
    # 1. Get the Secret Password
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    if not BOT_TOKEN:
        print("❌ Error: I cannot find the BOT_TOKEN in Secrets!")
        return

    print("🤖 Waking up for a test...")

    # 2. Force-fetch the latest article (Ignore Time)
    feed = feedparser.parse(TEST_FEED)
    
    if len(feed.entries) == 0:
        print("❌ Error: Could not read the RSS feed.")
        return

    # Grab the very first entry
    latest_post = feed.entries[0]
    title = latest_post.title
    link = latest_post.link
    
    print(f"✅ Found an article: {title}")
    
    # 3. Try to Send to Telegram
    message = f"🧪 **TEST MESSAGE**\n\nThis is a test to prove the bot works.\n\n📰 {title}\n🔗 {link}"
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    response = requests.post(url, json=payload)
    
    # 4. Check if Telegram accepted it
    if response.status_code == 200:
        print("✅ SUCCESS! Message sent to channel.")
    else:
        print(f"❌ FAILED. Telegram said: {response.text}")

if __name__ == "__main__":
    run_test()
