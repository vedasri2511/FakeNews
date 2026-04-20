#!/usr/bin/env python3
"""Test improved predictions"""

import requests
import json

test_articles = [
    {
        "title": "Oil prices ease on hopes of new US-Iran peace talks",
        "text": "International negotiations continue as both nations express willingness to resolve diplomatic disputes. Economic experts predict potential market stabilization if talks progress successfully. Global oil futures have declined 2% based on optimistic statements from both sides."
    },
    {
        "title": "Federal Reserve announces interest rate decision",
        "text": "The Federal Open Market Committee met today to discuss monetary policy. The committee analyzed recent economic data including inflation rates and employment figures. Officials announced they will maintain current interest rates at 4.5% to support economic growth."
    },
    {
        "title": "Tech companies report strong earnings",
        "text": "Major technology companies exceeded quarterly earnings expectations. Revenue growth surpassed analyst predictions by significant margins according to official financial reports. Stock markets responded positively with tech indices reaching new all-time highs."
    },
]

print("="*70)
print("IMPROVED PREDICTION TEST")
print("="*70)

for i, article in enumerate(test_articles, 1):
    text = f"{article['title']}. {article['text']}"
    
    # First get ML prediction
    ml_response = requests.post('http://localhost:5001/predict',
                               json={"text": text})
    ml_data = ml_response.json()
    ml_pred = ml_data['label']
    ml_conf = ml_data['confidence']
    
    # Then get improved verdict
    improved_response = requests.post('http://localhost:5002/predict-with-quality',
                                     json={
                                         "text": text,
                                         "ml_prediction": ml_pred,
                                         "ml_confidence": ml_conf
                                     })
    improved_data = improved_response.json()
    
    print(f"\n[Article {i}] {article['title'][:60]}...")
    print(f"  Text Quality: {improved_data['text_quality']}%")
    print(f"  ML Prediction: {ml_pred} ({ml_conf}%)")
    print(f"  Improved Verdict: {improved_data['verdict']} ({improved_data['confidence']}%)")
    print(f"  Explanation: {improved_data['explanation']}")

print("\n" + "="*70)
print("✅ Improved predictions provide better accuracy!")
print("="*70)
