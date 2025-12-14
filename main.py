import feedparser
import requests
import time
from datetime import datetime, timedelta, timezone
from time import mktime
import os

# --- CONFIGURATION ---
CHANNEL_ID = "@AIGlobalUpdates" 

# --- SAFETY SETTING ---
# We check for news from the last 25 minutes.
MAX_AGE_MINUTES = 25 

RSS_FEEDS = [
    # Top Tech & Research
    "http://export.arxiv.org/rss/cs.AI",
    "https://openai.com/blog/rss.xml",
    "https://research.google/blog/rss/",
    "https://huggingface.co/blog/feed.xml",
    "https://news.mit.edu/rss/topic/artificial-intelligence2",
    "https://news.microsoft.com/source/topics/ai/feed/",
    "https://intelligence.org/blog/feed/",
    "https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml",
    "https://www.marketingaiinstitute.com/blog/rss.xml",
    
    # Tech News Sites
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://venturebeat.com/category/ai/feed/",
    "https://www.wired.com/feed/tag/ai/latest/rss",
    "https://www.theguardian.com/technology/artificialintelligenceai/rss",
    "https://www.computerworld.com/artificial-intelligence/feed/",
    "https://www.fastcompany.com/section/artificial-intelligence/rss",
    "https://www.geekwire.com/tag/ai/feed/",
    "https://www.livemint.com/rss/AI",
    "https://rss.beehiiv.com/feeds/2R3C6Bt5wj.xml",
    "https://www.ft.com/artificial-intelligence?format=rss",
    "https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/spotlight/artificial-intelligence/rss.xml",
    
    # AI Specific Blogs
    "https://www.technologyreview.com/topic/artificial-intelligence/feed",
    "https://www.aitimejournal.com/feed/",
    "https://becominghuman.ai/feed",
    "https://topmarketingai.com/feed/",
    "https://medium.com/feed/ai-roadmap-institute",
    "https://analyticsindiamag.com/ai-news-updates/feed/",
    "https://www.marktechpost.com/feed/",
    "https://www.aiwire.net/feed/",
    "https://justainews.com/feed/",
    "https://insideainews.com/feed/",
    "https://news.crunchbase.com/sections/ai/feed/",
    "https://theconversation.com/topics/artificial-intelligence-ai-90/articles.atom",
    "https://indianexpress.com/section/technology/artificial-intelligence/feed/",
    "https://www.sciencenews.org/topic/artificial-intelligence/feed"
]

# --- THE LOGIC ---

def post_to_telegram(bot_token, title, link, source):
    # Using a "⚡" (Lightning) to show it is a Quick Update
    message = f"⚡ **Update: {source}**\n\n{title}\n\n🔗 [Read Article]({link})"
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
        print("Error: No Token Found")
        return

    now = datetime.now(timezone.utc)
    print(f"Checking {len(RSS_FEEDS)} feeds...")
    
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            
            # Check the top 3 newest items
            for entry in feed.entries[:3]:
                if hasattr(entry, 'published_parsed'):
                    post_time_struct = entry.published_parsed
                elif hasattr(entry, 'updated_parsed'):
                    post_time_struct = entry.updated_parsed
                else:
                    continue
                
                post_time = datetime.fromtimestamp(mktime(post_time_struct), timezone.utc)
                age = now - post_time
                
                # IF news is less than 25 minutes old -> POST IT
                if age <= timedelta(minutes=MAX_AGE_MINUTES) and age > timedelta(seconds=0):
                    print(f"New Update Found: {entry.title}")
                    source_name = feed.feed.get('title', 'AI News')
                    post_to_telegram(BOT_TOKEN, entry.title, entry.link, source_name)
                    
        except Exception as e:
            # If a link fails, skip it
            pass 

if __name__ == "__main__":
    run_bot()
