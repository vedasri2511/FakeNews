#!/usr/bin/env python3
"""Find articles that predict as REAL and check their confidence levels"""

import requests

# These are phrases from actual TRUE news articles in the training dataset
real_articles = [
    {
        "name": "Breaking News Style",
        "text": "President meets with congressional leaders to discuss infrastructure bill. The meeting lasted three hours with major discussion points about funding mechanisms and timeline. Administration officials expect vote next week. Congressional leaders from both parties attended the session."
    },
    {
        "name": "Market Report",
        "text": "Stock markets close higher on positive earnings reports. Investors react to strong quarterly results from major technology companies. The S&P 500 gained two percent in today's trading session. Market analysts attribute gains to optimistic economic forecasts."
    },
    {
        "name": "Healthcare News",
        "text": "Major pharmaceutical company receives FDA approval for new treatment. The drug shows effectiveness in clinical trials with minimal side effects. Patients can expect availability within months. Medical professionals welcome the advancement in treatment options."
    },
    {
        "name": "Science Report",
        "text": "Researchers discover new species in deep ocean exploration. Scientists collected specimens during recent expedition using advanced submersibles. The discovery adds to biodiversity understanding in harsh environments. Research findings will be published in peer-reviewed journals."
    },
]

print("=" * 70)
print("CONFIDENCE RANGE ANALYSIS: REAL Predictions")
print("=" * 70)

real_count = 0
for article in real_articles:
    payload = {"text": article['text']}
    
    try:
        response = requests.post('http://localhost:5000/api/verify', json=payload)
        
        if response.status_code == 200:
            result = response.json()
            ml_pred = result['mlPrediction']['label']
            ml_conf = result['mlPrediction']['confidence']
            verdict = result['verdict']
            
            print(f"\n📰 {article['name']}")
            print(f"   ML: {ml_pred:5} ({ml_conf:5.1f}%) → Verdict: {verdict}")
            
            if ml_pred == "REAL":
                real_count += 1
                if 65 <= ml_conf <= 75:
                    print(f"   ⭐ TARGET RANGE (65-75%)")
                    if verdict == "REAL":
                        print(f"      ✅ Correctly marked REAL")
                    else:
                        print(f"      ❌ Should be REAL but marked {verdict}")
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Failed: {e}")

print(f"\n{'-' * 70}")
print(f"Found {real_count} articles predicting as REAL")
print("=" * 70)
