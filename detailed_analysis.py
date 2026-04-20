#!/usr/bin/env python3
"""Detailed analysis of REAL predictions and their verdicts"""

import pandas as pd
import requests

# Load real news
true_df = pd.read_csv('ml/True.csv')

print("=" * 80)
print("DETAILED ANALYSIS: Real News Article Verdicts")
print("=" * 80)

results = []

for i in range(20):  # Test first 20 real articles
    text = true_df.iloc[i]['text']
    
    payload = {"text": text}
    
    try:
        response = requests.post('http://localhost:5000/api/verify', json=payload)
        
        if response.status_code == 200:
            result = response.json()
            ml_pred = result['mlPrediction']['label']
            ml_conf = result['mlPrediction']['confidence']
            verdict = result['verdict']
            
            results.append({
                'index': i+1,
                'confidence': ml_conf,
                'prediction': ml_pred,
                'verdict': verdict,
                'correct': (ml_pred == 'REAL' and verdict == 'REAL')
            })
    except Exception as e:
        pass

# Analyze results
print("\nReal Articles (should all be marked REAL):\n")
print(f"{'#':<3} {'Conf%':<8} {'ML Pred':<8} {'Verdict':<12} {'Correct':<8}")
print("-" * 80)

real_articles = [r for r in results if r['prediction'] == 'REAL']

for r in sorted(real_articles, key=lambda x: x['confidence'], reverse=True):
    status = "✅ YES" if r['correct'] else "❌ NO"
    print(f"{r['index']:<3} {r['confidence']:>6.1f}%  {r['prediction']:<8} {r['verdict']:<12} {status:<8}")

print("\n" + "=" * 80)
print(f"Total Real Predictions: {len(real_articles)}")
correct = sum(1 for r in real_articles if r['correct'])
print(f"Correctly Marked REAL: {correct}/{len(real_articles)}")

if real_articles:
    conf_values = [r['confidence'] for r in real_articles]
    print(f"Confidence Range: {min(conf_values):.1f}% - {max(conf_values):.1f}%")
    print(f"Average Confidence: {sum(conf_values)/len(conf_values):.1f}%")
    
    # Find the boundary
    unverified_reals = [r for r in real_articles if r['verdict'] != 'REAL']
    if unverified_reals:
        max_unverified_conf = max(r['confidence'] for r in unverified_reals)
        print(f"\n⚠️  ISSUE: Real articles marked UNVERIFIED up to {max_unverified_conf:.1f}% confidence")
        print(f"   Recommendation: Lower threshold from 65% to 55-60%")

print("=" * 80)
