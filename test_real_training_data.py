#!/usr/bin/env python3
"""Test with actual real news samples from training data"""

import pandas as pd
import requests

# Load real news
true_df = pd.read_csv('ml/True.csv')

print("=" * 70)
print("TESTING: Actual Real News from Training Data")
print("=" * 70)

real_predictions = []

for i in range(15):  # Test first 15 real articles
    text = true_df.iloc[i]['text']
    
    payload = {"text": text}
    
    try:
        response = requests.post('http://localhost:5000/api/verify', json=payload)
        
        if response.status_code == 200:
            result = response.json()
            ml_pred = result['mlPrediction']['label']
            ml_conf = result['mlPrediction']['confidence']
            verdict = result['verdict']
            
            real_predictions.append({
                'confidence': ml_conf,
                'verdict': verdict,
                'prediction': ml_pred
            })
            
            # Show articles in 60-75% range
            if ml_pred == "REAL" and 60 <= ml_conf <= 75:
                preview = text[:100].replace('\n', ' ')
                print(f"\n⭐ ARTICLE {i+1}: {ml_conf:.1f}% REAL")
                print(f"   Preview: {preview}...")
                print(f"   Verdict: {verdict}")
                if verdict != "REAL":
                    print(f"   ❌ BUG: Should be REAL with confidence {ml_conf:.1f}%")
        
        else:
            print(f"Error on article {i}: {response.status_code}")
            
    except Exception as e:
        print(f"Failed on article {i}: {e}")

print(f"\n{'-' * 70}")
print("\nSTATISTICS:")
if real_predictions:
    preds_df = pd.DataFrame(real_predictions)
    real_only = preds_df[preds_df['prediction'] == 'REAL']
    
    if len(real_only) > 0:
        print(f"Articles predicting REAL: {len(real_only)}")
        print(f"  Confidence range: {real_only['confidence'].min():.1f}% - {real_only['confidence'].max():.1f}%")
        print(f"  Average confidence: {real_only['confidence'].mean():.1f}%")
        
        marked_real = (real_only['verdict'] == 'REAL').sum()
        print(f"  Marked as REAL: {marked_real}/{len(real_only)}")
    else:
        print("No articles predicted as REAL")

print("=" * 70)
