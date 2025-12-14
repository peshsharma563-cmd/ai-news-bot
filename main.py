import feedparser
import requests
import time
from datetime import datetime, timedelta, timezone
from time import mktime
import os

# --- CONFIGURATION ---
CHANNEL_ID = "@AIGlobalUpdates" 

# --- CRITICAL SETTING FOR SPEED ---
# We will check for news that is up to 10 minutes old.
# This matches our schedule (running every 5-10 mins).
MAX_AGE_MINUTES = 15 

RSS_FEEDS = [
    "http://export.arxiv.org/rss/cs.AI",
    "https://openai.com/blog/rss.xml",
    "https://research.google/blog/rss/",
    "https://huggingface.co/blog/feed.xml",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://venturebeat.com/category/ai/feed/",
]

def post_to_telegram(bot_token, title, link, source):
    # Added "🔥" to show it is Breaking News
    message = f"🔥 **Just In: {source}**\n\n{title}\n\n🔗 [Read Article]({link})"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Failed to send: {e}")

def run_bot():
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    if not BOT_TOKEN:
        return

    # current time in UTC
    now = datetime.now(timezone.utc)
    
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            
            # Check the very latest post only (Speed optimization)
            if len(feed.entries) > 0:
                entry = feed.entries[0] 
                
                if hasattr(entry, 'published_parsed'):
                    post_time_struct = entry.published_parsed
                elif hasattr(entry, 'updated_parsed'):
                    post_time_struct = entry.updated_parsed
                else:
                    continue
                
                post_time = datetime.fromtimestamp(mktime(post_time_struct), timezone.utc)
                age = now - post_time
                
                # If the news came out in the last 15 minutes, POST IT.
                if age <= timedelta(minutes=MAX_AGE_MINUTES) and age > timedelta(seconds=0):
                    print(f"New fast update: {entry.title}")
                    source_name = feed.feed.get('title', 'AI News')
                    post_to_telegram(BOT_TOKEN, entry.title, entry.link, source_name)
                    
        except Exception as e:
            pass # Skip errors to keep it fast

if __name__ == "__main__":
    run_bot()
