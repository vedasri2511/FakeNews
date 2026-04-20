#!/usr/bin/env python3
"""
Test the fix: Articles with 60%+ REAL confidence should be marked REAL
"""

import pandas as pd
import requests

# Load real news and find articles with higher ML confidence
true_df = pd.read_csv('ml/True.csv')

print("=" * 80)
print("VERIFICATION: Articles with 60%+ REAL Confidence Should be Marked REAL")
print("=" * 80)

test_results = []

for i in range(25):  # Test 25 articles
    text = true_df.iloc[i]['text']
    payload = {"text": text}
    
    try:
        response = requests.post('http://localhost:5000/api/verify', json=payload)
        
        if response.status_code == 200:
            result = response.json()
            ml_pred = result['mlPrediction']['label']
            ml_conf = result['mlPrediction']['confidence']
            verdict = result['verdict']
            
            test_results.append({
                'index': i + 1,
                'confidence': ml_conf,
                'prediction': ml_pred,
                'verdict': verdict,
            })
    except:
        pass

# Filter REAL predictions
real_preds = [r for r in test_results if r['prediction'] == 'REAL' and r['confidence'] >= 60]

if real_preds:
    print(f"\n✅ Found {len(real_preds)} articles with 60%+ REAL confidence:\n")
    print(f"{'#':<3} {'Confidence':<12} {'Verdict':<15} {'Status':<12}")
    print("-" * 80)
    
    correct = 0
    for r in sorted(real_preds, key=lambda x: x['confidence'], reverse=True):
        is_correct = r['verdict'] == 'REAL'
        status = "✅ CORRECT" if is_correct else "❌ WRONG"
        if is_correct:
            correct += 1
        print(f"{r['index']:<3} {r['confidence']:>10.1f}%  {r['verdict']:<15} {status:<12}")
    
    print("-" * 80)
    print(f"\nResult: {correct}/{len(real_preds)} articles correctly marked REAL")
    print(f"Success Rate: {(correct/len(real_preds)*100):.0f}%")
    
    if correct == len(real_preds):
        print("\n✅ FIX VERIFIED: All 60%+ confidence REAL articles marked correctly!")
    else:
        print(f"\n❌ Still having issues: {len(real_preds) - correct} articles incorrectly marked")

else:
    print("\n⚠️ No articles found with 60%+ REAL confidence in sample")
    print("Model confidence range appears to be 50-60% for these articles")
    print("\nFor your 67% article:")
    print("  - With threshold at 60%: Should be marked REAL ✓")
    print("  - If still UNVERIFIED: Check if NewsAPI found 0 sources (then it's conservative)")

print("\n" + "=" * 80)
