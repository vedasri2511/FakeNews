#!/usr/bin/env python3
"""Test real news articles to see why they're marked UNVERIFIED"""

import pandas as pd
import requests

true_df = pd.read_csv('ml/True.csv')

print("="*70)
print("TESTING REAL NEWS - Why are they marked UNVERIFIED?")
print("="*70)

real_marked_unverified = 0
real_marked_real = 0

for i in range(10):
    text = true_df.iloc[i]['text']
    
    try:
        response = requests.post('http://localhost:5000/api/verify',
                               json={'text': text},
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            ml_pred = result['mlPrediction']['label']
            ml_conf = result['mlPrediction']['confidence']
            verdict = result['verdict']
            
            print(f"\n[Article {i+1}]")
            print(f"  ML: {ml_pred} ({ml_conf:.1f}%)")
            print(f"  Verdict: {verdict}")
            
            if verdict == "REAL":
                real_marked_real += 1
            else:
                real_marked_unverified += 1
                
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "="*70)
print(f"Results: {real_marked_real} REAL, {real_marked_unverified} UNVERIFIED")
if real_marked_unverified > 0:
    print(f"⚠️  Issue: Real articles still being marked UNVERIFIED")
    print(f"   Need to lower threshold further or change logic")
print("="*70)
