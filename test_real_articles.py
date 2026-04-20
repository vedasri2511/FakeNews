#!/usr/bin/env python3
"""
Test with real articles from training data
"""
import requests
import csv
from pathlib import  Path

def test_with_csv_articles():
    print("\n" + "="*70)
    print("TESTING WITH ACTUAL TRAINING DATA ARTICLES")
    print("="*70)
    
    ml_dir = Path("ml")
    
    # Load sample FAKE articles
    fake_samples = []
    try:
        with open(ml_dir / "Fake.csv", 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i < 3:  # First 3 articles
                    fake_samples.append(row['text'])
    except:
        print("Could not load Fake.csv")
    
    # Load sample REAL articles
    real_samples = []
    try:
        with open(ml_dir / "True.csv", 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i < 3:  # First 3 articles
                    real_samples.append(row['text'])
    except:
        print("Could not load True.csv")
    
    # Test FAKE articles
    print("\n[TESTING FAKE ARTICLES]")
    fake_correct = 0
    for i, text in enumerate(fake_samples, 1):
        try:
            response = requests.post(
                "http://localhost:5000/api/verify",
                json={"text": text},
                timeout=10
            )
            result = response.json()
            verdict = result.get('verdict')
            ml_pred = result.get('mlPrediction', {})
            
            is_correct = verdict == "FAKE"
            status = "✓" if is_correct else "✗"
            fake_correct += is_correct
            
            preview = text[:60].replace('\n', ' ')
            print(f"\n[FAKE {i}] {preview}...")
            print(f"   Verdict: {verdict:12} | ML: {ml_pred.get('label'):5} ({ml_pred.get('confidence', 0):.1f}%) {status}")
        except Exception as e:
            print(f"[FAKE {i}] Error: {e}")
    
    # Test REAL articles
    print("\n[TESTING REAL ARTICLES]")
    real_correct = 0
    for i, text in enumerate(real_samples, 1):
        try:
            response = requests.post(
                "http://localhost:5000/api/verify",
                json={"text": text},
                timeout=10
            )
            result = response.json()
            verdict = result.get('verdict')
            ml_pred = result.get('mlPrediction', {})
            
            is_correct = verdict == "REAL"
            status = "✓" if is_correct else "✗"
            real_correct += is_correct
            
            preview = text[:60].replace('\n', ' ')
            print(f"\n[REAL {i}] {preview}...")
            print(f"   Verdict: {verdict:12} | ML: {ml_pred.get('label'):5} ({ml_pred.get('confidence', 0):.1f}%) {status}")
        except Exception as e:
            print(f"[REAL {i}] Error: {e}")
    
    # Summary
    total = len(fake_samples) + len(real_samples)
    correct = fake_correct + real_correct
    
    print("\n" + "="*70)
    print(f"FAKE Correct: {fake_correct}/{len(fake_samples)}")
    print(f"REAL Correct: {real_correct}/{len(real_samples)}")
    print(f"Overall: {correct}/{total} ({100*correct/total:.1f}%)")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_with_csv_articles()
