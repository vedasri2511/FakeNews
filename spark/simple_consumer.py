#!/usr/bin/env python3
"""
Simple Kafka Consumer for Fake News Detection
Processes real-time news from Kafka topic and sends results to backend
"""

import json
import pickle
import requests
from kafka import KafkaConsumer
import sys

print("="*70)
print("KAFKA CONSUMER - FAKE NEWS DETECTOR")
print("="*70)

print("\n📦 Loading ML model and vectorizer...")
try:
    model = pickle.load(open("../ml/model.pkl", "rb"))
    vectorizer = pickle.load(open("../ml/vectorizer.pkl", "rb"))
    print("✓ Model and vectorizer loaded successfully!")
    print(f"✓ Model classes: {model.classes_}")
except Exception as e:
    print(f"✗ Error loading models: {e}")
    sys.exit(1)

print("\n📡 Connecting to Kafka broker...")
try:
    consumer = KafkaConsumer(
        'news_topic',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='latest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        consumer_timeout_ms=5000
    )
    print("✓ Connected to Kafka topic 'news_topic'")
except Exception as e:
    print(f"✗ Error connecting to Kafka: {e}")
    print("Make sure Kafka broker is running on localhost:9092")
    sys.exit(1)

print("\n" + "="*70)
print("LISTENING FOR ARTICLES...")
print("="*70 + "\n")

articles_processed = 0

try:
    for message in consumer:
        articles_processed += 1
        article = message.value
        
        try:
            # Extract content
            title = article.get('title', '')
            text = article.get('text', '')
            url = article.get('url', '')
            source = article.get('source', '')
            content = f"{title} {text}"
            
            if not content.strip():
                continue
            
            # Vectorize
            X_tfidf = vectorizer.transform([content])
            
            # Get prediction
            # Classes: 0=FAKE, 1=REAL
            pred_label = model.predict(X_tfidf)[0]
            decision_score = model.decision_function(X_tfidf)[0]
            
            # Confidence based on distance from decision boundary
            # Same formula as ML service: 50 + (abs(decision_score) * 6)
            confidence = min(100, 50 + (abs(float(decision_score)) * 6))
            
            # Use prediction directly (no inversion)
            label = "REAL" if int(pred_label) == 1 else "FAKE"
            
            print(f"\n[Article {articles_processed}]")
            print(f"  Verdict: {label} (Confidence: {confidence:.1f}%)")
            print(f"  Title: {title[:70]}...")
            print(f"  URL: {url[:60]}...")
            
            # Send to backend for storage and verification
            try:
                response = requests.post(
                    "http://localhost:5000/api/ingest",
                    json={
                        'article': {
                            'title': title,
                            'headline': title,
                            'text': text,
                            'url': url,
                            'source': source
                        },
                        'classification': label,
                        'confidence': round(confidence, 1)
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    print(f"  ✓ Sent to backend successfully")
                else:
                    print(f"  ⚠ Backend returned: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"  ⚠ Could not send to backend: {str(e)}")
                
        except Exception as e:
            print(f"✗ Error processing article: {str(e)}")
            import traceback
            traceback.print_exc()
            continue

except KeyboardInterrupt:
    print("\n\n✓ Consumer stopped by user")
except Exception as e:
    print(f"\n✗ Consumer error: {e}")
    import traceback
    traceback.print_exc()
finally:
    consumer.close()
    print(f"\nProcessed {articles_processed} articles total")
