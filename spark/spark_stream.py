#!/usr/bin/env python3
"""
Spark Streaming for Fake News Detection
Uses Spark Structured Streaming to process Kafka topics with ML predictions
"""

from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
import json
import pickle
import requests
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath('..'))

print("="*70)
print("SPARK STREAMING FAKE NEWS DETECTOR")
print("="*70)

# Load ML model and vectorizer at startup
print("\n📦 Loading ML model and vectorizer...")
try:
    model = pickle.load(open("../ml/model.pkl", "rb"))
    vectorizer = pickle.load(open("../ml/vectorizer.pkl", "rb"))
    print("✓ Model and vectorizer loaded successfully!")
    print(f"✓ Model classes: {model.classes_}")
    print(f"✓ Vectorizer vocabulary size: {len(vectorizer.get_feature_names_out())}")
except Exception as e:
    print(f"✗ Error loading models: {e}")
    sys.exit(1)

# Create SparkSession
print("\n🔥 Initializing Spark Session...")
try:
    spark = SparkSession.builder \
        .appName("FakeNewsDetector") \
        .master("local[*]") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .config("spark.sql.streaming.checkpointLocation", "/tmp/fn_checkpoint") \
        .config("spark.sql.shuffle.partitions", "4") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")
    print("✓ Spark Session created successfully!")
except Exception as e:
    print(f"✗ Error creating Spark Session: {e}")
    sys.exit(1)

# Read stream from Kafka
print("\n📡 Connecting to Kafka...")
try:
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "news_topic") \
        .option("startingOffsets", "latest") \
        .load()
    
    # Convert Kafka value to string
    df_string = df.select(F.from_json(F.col("value").cast("string"), 
                          StructType([
                              StructField("title", StringType()),
                              StructField("text", StringType()),
                              StructField("url", StringType()),
                              StructField("source", StringType())
                          ])).alias("data")).select("data.*")
    
    print("✓ Connected to Kafka topic 'news_topic'")
except Exception as e:
    print(f"✗ Error connecting to Kafka: {e}")
    sys.exit(1)

# Process batch function
def analyze_article(batch_df, batch_id):
    """Process each article batch using ML model"""
    
    if batch_df.count() == 0:
        return
    
    print(f"\n[Batch {batch_id}] Processing {batch_df.count()} articles...")
    
    for row in batch_df.collect():
        try:
            title = str(row.title or "")
            text = str(row.text or "")
            url = str(row.url or "")
            source = str(row.source or "")
            
            # Combine content
            content = f"{title} {text}".strip()
            
            if not content:
                continue
            
            # Vectorize
            X_tfidf = vectorizer.transform([content])
            
            # Get prediction
            # Classes: 0=FAKE, 1=REAL
            pred_label = model.predict(X_tfidf)[0]
            decision_score = model.decision_function(X_tfidf)[0]
            
            # Confidence based on distance from decision boundary
            confidence = min(100, abs(float(decision_score)) * 25)
            
            # Use prediction directly (no inversion)
            label = "REAL" if int(pred_label) == 1 else "FAKE"
            
            print(f"  ✓ {label:4} | Prob(REAL)={prob_real:.1f}% | Prob(FAKE)={prob_fake:.1f}%")
            print(f"     Title: {title[:70]}...")
            
            # Send to backend
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
                    print(f"     ✓ Sent to backend")
                else:
                    print(f"     ⚠ Backend response: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"     ⚠ Could not send to backend: {str(e)}")
                
        except Exception as e:
            print(f"  ✗ Error processing article: {str(e)}")
            import traceback
            traceback.print_exc()
            continue

# Start streaming
print("\n" + "="*70)
print("LISTENING FOR KAFKA MESSAGES...")
print("="*70 + "\n")

try:
    query = df_string.writeStream \
        .foreachBatch(analyze_article) \
        .option("checkpointLocation", "/tmp/fn_checkpoint") \
        .start()
    
    query.awaitTermination()
    
except Exception as e:
    print(f"✗ Streaming error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
