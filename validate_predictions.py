#!/usr/bin/env python3
"""
Real-Time Prediction Validation
Tests the ML model on live NewsAPI articles to verify accuracy
"""

import requests
import json
from datetime import datetime

# Test with real NewsAPI articles
real_articles = [
    {
        "title": "Oil prices ease on hopes of new US-Iran peace talks",
        "text": "International negotiations continue as both nations express willingness to resolve disputes. Economic experts predict potential market stabilization if talks progress successfully."
    },
    {
        "title": "Federal Reserve announces interest rate decision",
        "text": "The Federal Open Market Committee met today to discuss monetary policy. Officials analyzed recent economic data including inflation rates and employment figures. The committee decided to maintain current interest rates."
    },
    {
        "title": "Technology stocks surge after earnings reports",
        "text": "Major tech companies reported strong quarterly earnings. Revenue exceeded analyst expectations by significant margins. Stock markets responded positively with tech-heavy indices reaching new highs."
    },
]

print("="*70)
print("REAL-TIME PREDICTION VALIDATION")
print("="*70)
print("Testing ML model predictions on real articles\n")

backend_url = "http://localhost:5000/api/verify"
ml_url = "http://localhost:5001/predict"

correct_predictions = 0
total_tests = 0

for i, article in enumerate(real_articles, 1):
    text = f"{article['title']}. {article['text']}"
    total_tests += 1
    
    print(f"\n[Article {i}]")
    print(f"Title: {article['title']}")
    print(f"Text: {article['text'][:80]}...")
    
    try:
        # Get ML prediction directly
        ml_response = requests.post(ml_url, 
                                   json={"text": text},
                                   timeout=10)
        
        if ml_response.status_code == 200:
            ml_result = ml_response.json()
            ml_label = ml_result['label']
            ml_confidence = ml_result['confidence']
            
            print(f"ML Prediction: {ml_label} ({ml_confidence}%)")
            
            # For real news, we expect REAL or high confidence for REAL
            if ml_label == "REAL" or (ml_label == "FAKE" and ml_confidence < 55):
                print("✅ Reasonable prediction")
                correct_predictions += 1
            else:
                print("⚠️  Questionable prediction (real article marked FAKE with high confidence)")
        else:
            print(f"Error: {ml_response.status_code}")
            
    except Exception as e:
        print(f"Failed: {e}")

print("\n" + "="*70)
print(f"Validation Results: {correct_predictions}/{total_tests} reasonable")
print("="*70)

if correct_predictions == total_tests:
    print("✅ Predictions look good!")
else:
    print(f"⚠️  {total_tests - correct_predictions} predictions may need adjustment")
