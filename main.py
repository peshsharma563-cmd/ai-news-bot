import feedparser
import requests
import time
from datetime import datetime, timedelta, timezone
from time import mktime
import os
import math

# --- CONFIGURATION ---
CHANNEL_ID = "@AIGlobalUpdates" 

# --- SAFETY SETTING ---
# We check for news from the last 20 minutes to avoid duplicates
MAX_AGE_MINUTES = 20

# --- DAILY CONCEPT SETTINGS ---
# 3:40 UTC is exactly 9:10 AM India Time.
CONCEPT_POST_HOUR = 3

# --- THE AI DICTIONARY (Data Source) ---
AI_CONCEPTS = [
    {"term": "Artificial Intelligence (AI)", "def": "Machines that mimic human intelligence to perform tasks like seeing, talking, acting, and reasoning."},
    {"term": "Machine Learning (ML)", "def": "A subset of AI where computers learn from data without being explicitly programmed for every rule."},
    {"term": "Deep Learning", "def": "A type of ML inspired by the human brain, using multi-layered 'neural networks' to learn from vast amounts of data."},
    {"term": "Neural Network", "def": "A computer system modeled on the human brain and nervous system, consisting of layers of nodes (neurons) that process data."},
    {"term": "Large Language Model (LLM)", "def": "A massive AI model (like GPT-4) trained on huge amounts of text to understand and generate human language."},
    {"term": "Generative AI", "def": "AI that can create NEW content—including text, images, audio, and video—rather than just analyzing existing data."},
    {"term": "Hallucination", "def": "When an AI confidently gives an answer that is grammatically correct but factually wrong or made up."},
    {"term": "Prompt Engineering", "def": "The art of crafting the perfect text inputs (prompts) to get the best possible result from an AI model."},
    {"term": "Transformer", "def": "The modern architecture behind ChatGPT and Google Gemini. It allows AI to pay attention to different parts of a sentence at once."},
    {"term": "Token", "def": "The basic unit of text for an LLM. A token is roughly 3/4 of a word (e.g., 'hamburger' might be 3 tokens)."},
    {"term": "Temperature", "def": "A setting that controls how 'creative' or 'random' the AI is. Low temp = focused; High temp = creative/random."},
    {"term": "Zero-Shot Learning", "def": "When an AI completes a task it was never specifically trained to do, just by using its general knowledge."},
    {"term": "Multimodal AI", "def": "AI that can understand and process different types of media at the same time (e.g., seeing an image AND reading text)."},
    {"term": "AGI (Artificial General Intelligence)", "def": "A theoretical future AI that can do ANY intellectual task a human can do. The 'Holy Grail' of AI research."},
    {"term": "Fine-Tuning", "def": "Taking a general AI model and training it further on a specific dataset (like medical records) to make it an expert in that field."},
    {"term": "RAG (Retrieval-Augmented Generation)", "def": "Connecting ChatGPT to your own private data (PDFs/Emails) so it can answer questions using facts it wasn't trained on."},
    {"term": "Parameters", "def": "The 'settings' or 'weights' inside an AI model. GPT-4 has nearly 1.8 trillion parameters. More parameters usually mean smarter AI."},
    {"term": "Inference", "def": "The moment you use a trained AI to make a prediction or generate text. It is 'inferring' the answer from what it learned."},
    {"term": "Bias", "def": "Errors in AI output caused by prejudiced data used during training. (e.g., an AI assuming all doctors are men)."},
    {"term": "Computer Vision", "def": "Teaching computers to 'see' and understand images and video (used in self-driving cars and FaceID)."},
    {"term": "NLP (Natural Language Processing)", "def": "The field of AI focused on helping computers understand, interpret, and manipulate human language."},
    {"term": "Reinforcement Learning", "def": "Teaching AI through trial and error, rewarding it when it does well (like training a dog with treats). Used in robotics."},
    {"term": "Supervised Learning", "def": "Training AI using labeled data (e.g., showing it pictures labeled 'Cat' or 'Dog' so it learns the difference)."},
    {"term": "Unsupervised Learning", "def": "Giving AI messy, unlabeled data and asking it to find patterns on its own (e.g., 'Group these customers by behavior')."},
    {"term": "Alignment", "def": "The challenge of ensuring AI systems have goals and behaviors that match human values and safety."},
    {"term": "Turing Test", "def": "A test to see if a machine can exhibit behavior indistinguishable from a human. If you can't tell it's a bot, it passes."},
    {"term": "Singularity", "def": "A hypothetical point in the future when technological growth becomes uncontrollable and irreversible, usually due to super-intelligent AI."},
    {"term": "Diffusion Model", "def": "The tech behind AI art (MidJourney). It learns by adding 'noise' (static) to an image until it is ruined, then reversing the process to create art."},
    {"term": "Embeddings", "def": "Turning words into numbers (vectors) so computers can measure how 'related' two concepts are (e.g., King - Man + Woman = Queen)."},
    {"term": "Copilot", "def": "An AI assistant that works alongside you to help with tasks (coding, writing, emails) rather than replacing you entirely."}
]

RSS_FEEDS = [
    "http://export.arxiv.org/rss/cs.AI",
    "https://openai.com/blog/rss.xml",
    "https://research.google/blog/rss/",
    "https://huggingface.co/blog/feed.xml",
    "https://news.mit.edu/rss/topic/artificial-intelligence2",
    "https://news.microsoft.com/source/topics/ai/feed/",
    "https://intelligence.org/blog/feed/",
    "https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml",
    "https://www.marketingaiinstitute.com/blog/rss.xml",
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

# --- FUNCTIONS ---

def send_message(bot_token, text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Failed to send: {e}")

def post_to_telegram_news(bot_token, title, link, source):
    # Standard News Post with Hashtags
    message = f"⚡ **Update: {source}**\n\n{title}\n\n🔗 [Read Article]({link})\n\n#AI #ArtificialIntelligence #TechNews #Innovation"
    send_message(bot_token, message)

def run_daily_concept(bot_token):
    # Check UTC Time (India is UTC+5:30)
    now = datetime.now(timezone.utc)
    
    # Logic: 
    # Your bot runs at UTC 3:00, 3:20, 3:40...
    # 3:40 UTC = 9:10 AM IST (EXACTLY what you want)
    # So we check if Hour is 3 AND Minute is greater than 35.
    
    if now.hour == CONCEPT_POST_HOUR and now.minute >= 35:
        print("🧠 It is Concept Time! Preparing daily post...")
        
        # Pick a concept based on Day of Year
        day_of_year = now.timetuple().tm_yday
        concept_index = day_of_year % len(AI_CONCEPTS)
        concept = AI_CONCEPTS[concept_index]
        
        message = (
            f"🧠 **DAILY AI CONCEPT** 🧠\n\n"
            f"📌 **Term:** {concept['term']}\n\n"
            f"📖 **Definition:**\n_{concept['def']}_\n\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"🤖 *Learn AI every day with {CHANNEL_ID}*"
        )
        
        send_message(bot_token, message)
        print(f"✅ Daily Concept Posted: {concept['term']}")
    else:
        print("⏳ Not concept time yet.")

def run_bot():
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    if not BOT_TOKEN:
        print("Error: No Token Found")
        return

    # --- JOB 1: DAILY CONCEPT ---
    run_daily_concept(BOT_TOKEN)

    # --- JOB 2: NEWS CHECKER ---
    now = datetime.now(timezone.utc)
    print(f"Checking {len(RSS_FEEDS)} feeds...")
    
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                if hasattr(entry, 'published_parsed'):
                    post_time_struct = entry.published_parsed
                elif hasattr(entry, 'updated_parsed'):
                    post_time_struct = entry.updated_parsed
                else:
                    continue
                
                post_time = datetime.fromtimestamp(mktime(post_time_struct), timezone.utc)
                age = now - post_time
                
                # Check 20 minute window
                if age <= timedelta(minutes=MAX_AGE_MINUTES) and age > timedelta(seconds=0):
                    print(f"New Update Found: {entry.title}")
                    source_name = feed.feed.get('title', 'AI News')
                    post_to_telegram_news(BOT_TOKEN, entry.title, entry.link, source_name)
                    
        except Exception as e:
            pass 

if __name__ == "__main__":
    run_bot()
