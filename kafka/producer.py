import requests
import json
import time
from kafka import KafkaProducer
from datetime import datetime

# API key for NewsAPI
API_KEY = "0cfeb24bb9df4c4880b9ae7f5ef7ab76"

# Kafka producer for real-time articles
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("="*70)
print("REAL-TIME NEWS PRODUCER - NewsAPI")
print("="*70)
print("✓ Fetching live articles from NewsAPI")
print("✓ No pre-trained dataset - REAL articles only")
print("✓ Multiple categories for diversity")
print("="*70 + "\n")

# Multiple categories to get diverse real-time data
CATEGORIES = ["general", "business", "technology", "science", "health", "sports"]
query_index = 0

while True:
    try:
        # Rotate through categories for diverse coverage
        category = CATEGORIES[query_index % len(CATEGORIES)]
        query_index += 1
        
        # ✅ Fetch live articles from NewsAPI
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": "us",
            "category": category,
            "apiKey": API_KEY,
            "pageSize": 10  # Get 10 articles per request
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get("status") != "ok":
            print(f"⚠️  API Error: {data.get('message')}")
            time.sleep(10)
            continue

        articles = data.get("articles", [])
        
        if not articles:
            print(f"⚠️  No articles in {category}")
            time.sleep(5)
            continue

        print(f"\n📰 [{datetime.now().strftime('%H:%M:%S')}] Fetching {category.upper()}: {len(articles)} articles")
        print("-" * 70)
        
        # ✅ Send REAL articles to Kafka
        for i, article in enumerate(articles, 1):
            # Extract full article content
            news = {
                "title": article.get("title", ""),
                "text": article.get("description", "") or article.get("content", ""),
                "url": article.get("url", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
                "author": article.get("author", ""),
                "publishedAt": article.get("publishedAt", ""),
                "imageUrl": article.get("urlToImage", ""),
                "content_type": "real_news"  # Mark as real article, not training data
            }
            
            # Only send if we have meaningful content
            if news["text"] and len(news["text"]) > 50:
                producer.send("news_topic", news)
                print(f"  [{i}] ✓ {news['title'][:60]}...")
            
        producer.flush()
        
        print(f"\n✅ Sent {len(articles)} REAL articles to Kafka")
        print(f"   Next update in 30 minutes (conserving free API quota)...")

        # NewsAPI free plan: 100 requests/day max.
        # Fetching 6 categories = 6 requests per cycle. 100/6 ≈ 16 cycles/day → sleep ~90 min.
        # Using 30 min to balance freshness vs quota.
        time.sleep(1800)

    except requests.exceptions.Timeout:
        print(f"❌ API Timeout - retrying in 10 seconds...")
        time.sleep(10)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print(f"   Retrying in 10 seconds...")
        time.sleep(10)