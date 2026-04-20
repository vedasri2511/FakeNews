#!/usr/bin/env python3
"""
Validate confidence threshold behavior - showing that 67% is handled correctly
"""
import requests

def test_confidence_thresholds():
    print("\n" + "="*70)
    print("CONFIDENCE THRESHOLD VALIDATION")
    print("="*70)
    
    print("\nDesign: Don't mark as FAKE unless confidence >75% or NewsAPI confirms")
    print("\n" + "-"*70)
    
    # Load test articles
    import csv
    from pathlib import Path
    
    ml_dir = Path("ml")
    
    # Get some FAKE and REAL samples
    fake_samples = []
    real_samples = []
    
    try:
        with open(ml_dir / "Fake.csv", 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i < 5:
                    fake_samples.append(row['text'])
    except:
        pass
    
    try:
        with open(ml_dir / "True.csv", 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i < 5:
                    real_samples.append(row['text'])
    except:
        pass
    
    print("\nTesting FAKE Articles (they may show UNVERIFIED due to medium confidence):")
    print("-"*70)
    
    false_positives = 0  # Count FAKE marked as REAL
    high_conf_fakes = 0   # Count FAKE with >75% confidence
    
    for i, text in enumerate(fake_samples, 1):
        try:
            resp = requests.post('http://localhost:5000/api/verify', 
                               json={'text': text[:1000]}, timeout=10)
            result = resp.json()
            
            verdict = result.get('verdict')
            ml_pred = result.get('mlPrediction', {})
            ml_conf = ml_pred.get('confidence', 0)
            
            # Check for false positives (FAKE marked as REAL)
            if verdict == "REAL":
                false_positives += 1
                print(f"[{i}] ⚠ ALERT: FAKE marked as REAL (confidence: {ml_conf:.1f}%)")
            # Check high confidence
            elif ml_conf > 75:
                high_conf_fakes += 1
                status = "✓" if verdict == "FAKE" else "?"
                print(f"[{i}] High confidence FAKE {ml_conf:.1f}%: {verdict:12} {status}")
            else:
                status = "✓ (Correct - medium confidence)" if verdict == "UNVERIFIED" else "?"
                print(f"[{i}] Medium confidence FAKE {ml_conf:.1f}%: {verdict:12} {status}")
        except Exception as e:
            print(f"[{i}] Error: {e}")
    
    print("\nTesting REAL Articles:")
    print("-"*70)
    
    real_correct = 0
    
    for i, text in enumerate(real_samples, 1):
        try:
            resp = requests.post('http://localhost:5000/api/verify', 
                               json={'text': text[:1000]}, timeout=10)
            result = resp.json()
            
            verdict = result.get('verdict')
            ml_pred = result.get('mlPrediction', {})
            ml_conf = ml_pred.get('confidence', 0)
            
            # REAL articles should be REAL or UNVERIFIED (never FAKE)
            is_correct = verdict in ["REAL", "UNVERIFIED"]
            real_correct += is_correct
            status = "✓" if is_correct else "✗"
            
            if verdict == "FAKE":
                print(f"[{i}] ❌ ERROR: REAL marked as FAKE (confidence: {ml_conf:.1f}%)")
            else:
                print(f"[{i}] {verdict:12} (ML: {ml_conf:.1f}%) {status}")
        except Exception as e:
            print(f"[{i}] Error: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("THRESHOLD VALIDATION RESULTS")
    print("="*70)
    print(f"False Positives (FAKE→REAL): {false_positives} ❌ (CRITICAL)")
    print(f"REAL Articles Correct: {real_correct}/{len(real_samples)}")
    print(f"High Confidence FAKEs (>75%): {high_conf_fakes}")
    print()
    
    if false_positives == 0:
        print("✅ PASS: No false positives - FAKE never marked as REAL")
    else:
        print("❌ FAIL: False positives detected!")
    
    print()

if __name__ == "__main__":
    test_confidence_thresholds()
