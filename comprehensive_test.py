#!/usr/bin/env python3
"""
Final comprehensive system test
"""
import requests
import csv
from pathlib import Path

def test_comprehensive():
    print("\n" + "="*70)
    print("COMPREHENSIVE FAKE NEWS DETECTION SYSTEM TEST")
    print("="*70)
    
    ml_dir = Path("ml")
    
    # Load more samples for comprehensive testing
    fake_samples = []
    real_samples = []
    
    try:
        with open(ml_dir / "Fake.csv", 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i < 10:  # First 10
                    fake_samples.append(row['text'])
    except Exception as e:
        print(f"Could not load Fake.csv: {e}")
    
    try:
        with open(ml_dir / "True.csv", 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i < 10:  # First 10
                    real_samples.append(row['text'])
    except Exception as e:
        print(f"Could not load True.csv: {e}")
    
    if not fake_samples or not real_samples:
        print("Could not load test data")
        return
    
    print(f"\nLoaded {len(fake_samples)} FAKE and {len(real_samples)} REAL articles for testing")
    
    # Test FAKE articles
    print("\n" + "-"*70)
    print(f"TESTING {len(fake_samples)} FAKE ARTICLES")
    print("-"*70)
    
    fake_correct = 0
    for i, text in enumerate(fake_samples, 1):
        try:
            response = requests.post(
                "http://localhost:5000/api/verify",
                json={"text": text[:1000]},  # Use first 1000 chars
                timeout=15
            )
            result = response.json()
            verdict = result.get('verdict')
            ml_pred = result.get('mlPrediction', {})
            
            is_correct = verdict in ["FAKE", "UNVERIFIED"]  # Accept FAKE or UNVERIFIED
            status = "✓" if is_correct else "✗"
            fake_correct += is_correct
            
            preview = text[:60].replace('\n', ' ')
            print(f"[{i:2d}] {preview:60} → {verdict:12} {status}")
        except Exception as e:
            print(f"[{i:2d}] Error: {e}")
    
    # Test REAL articles
    print("\n" + "-"*70)
    print(f"TESTING {len(real_samples)} REAL ARTICLES")
    print("-"*70)
    
    real_correct = 0
    for i, text in enumerate(real_samples, 1):
        try:
            response = requests.post(
                "http://localhost:5000/api/verify",
                json={"text": text[:1000]},
                timeout=15
            )
            result = response.json()
            verdict = result.get('verdict')
            ml_pred = result.get('mlPrediction', {})
            
            is_correct = verdict == "REAL"
            status = "✓" if is_correct else "✗"
            real_correct += is_correct
            
            preview = text[:60].replace('\n', ' ')
            print(f"[{i:2d}] {preview:60} → {verdict:12} {status}")
        except Exception as e:
            print(f"[{i:2d}] Error: {e}")
    
    # Summary
    total = len(fake_samples) + len(real_samples)
    correct = fake_correct + real_correct
    accuracy = 100 * correct / total if total > 0 else 0
    
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"FAKE Articles: {fake_correct}/{len(fake_samples)} Correct ({100*fake_correct/len(fake_samples):.1f}%)")
    print(f"REAL Articles: {real_correct}/{len(real_samples)} Correct ({100*real_correct/len(real_samples):.1f}%)")
    print(f"OVERALL:       {correct}/{total} Correct ({accuracy:.1f}%)")
    print("="*70)
    
    # Status
    if accuracy >= 90:
        print("\n🎉 SYSTEM PERFORMANCE: EXCELLENT (90%+ accuracy)")
    elif accuracy >= 80:
        print("\n✓ SYSTEM PERFORMANCE: GOOD (80%+ accuracy)")
    elif accuracy >= 70:
        print("\n⚠ SYSTEM PERFORMANCE: FAIR (70%+ accuracy)")
    else:
        print("\n❌ SYSTEM PERFORMANCE: NEEDS IMPROVEMENT (<70%)")
    
    print()

if __name__ == "__main__":
    test_comprehensive()
