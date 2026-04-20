#!/usr/bin/env python3
"""
Test with actual articles from the training CSV files
to verify the model is working correctly.
"""

import pickle
import sys
import csv
from pathlib import Path

# Add ml directory to path
ml_dir = Path(__file__).parent / "ml"
sys.path.insert(0, str(ml_dir))

def load_models():
    """Load model and vectorizer"""
    model_path = ml_dir / "model.pkl"
    vectorizer_path = ml_dir / "vectorizer.pkl"
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    with open(vectorizer_path, 'rb') as f:
        vectorizer = pickle.load(f)
    
    return model, vectorizer

def load_sample_articles():
    """Load sample articles from training CSV files"""
    ml_path = Path(__file__).parent / "ml"
    fake_samples = []
    real_samples = []
    
    # Load FAKE articles
    try:
        with open(ml_path / "Fake.csv", 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i < 5:  # Get first 5
                    fake_samples.append(row['text'])
    except:
        pass
    
    # Load REAL articles
    try:
        with open(ml_path / "True.csv", 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i < 5:  # Get first 5
                    real_samples.append(row['text'])
    except:
        pass
    
    return fake_samples, real_samples

def predict_article(model, vectorizer, text):
    """Predict if article is FAKE or REAL"""
    try:
        if len(text) < 10:
            return {"error": "Text too short"}
        
        X = vectorizer.transform([text])
        pred_label = model.predict(X)[0]
        decision_score = model.decision_function(X)[0]
        
        # Confidence based on distance from decision boundary
        confidence = min(100, abs(float(decision_score)) * 25)
        
        # Use prediction directly
        label = "REAL" if int(pred_label) == 1 else "FAKE"
        
        return {
            "label": label,
            "confidence": round(confidence, 2),
            "decision_score": round(decision_score, 4)
        }
    except Exception as e:
        return {"error": str(e)}

def main():
    print("\n" + "="*70)
    print("TESTING WITH ACTUAL TRAINING DATA")
    print("="*70)
    
    # Load models
    print("\n[LOADING] Models...")
    try:
        model, vectorizer = load_models()
        print("✓ Models loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load models: {e}")
        return
    
    # Load sample articles from training data
    print("[LOADING] Sample articles from training data...")
    fake_samples, real_samples = load_sample_articles()
    
    if not fake_samples or not real_samples:
        print("✗ Could not load training data samples")
        return
    
    print(f"✓ Loaded {len(fake_samples)} FAKE and {len(real_samples)} REAL samples")
    
    # Test FAKE articles
    print("\n" + "-"*70)
    print(f"TESTING {len(fake_samples)} FAKE ARTICLES (Should predict: FAKE)")
    print("-"*70)
    
    fake_correct = 0
    for i, text in enumerate(fake_samples, 1):
        result = predict_article(model, vectorizer, text)
        
        if "error" in result:
            print(f"\n[FAKE {i}] Error: {result['error']}")
            continue
        
        is_correct = result.get("label") == "FAKE"
        status = "✓" if is_correct else "✗"
        fake_correct += is_correct
        
        preview = text[:70].replace('\n', ' ')
        print(f"\n[FAKE {i}] {preview}...")
        print(f"  → Verdict: {result['label']:5} | Confidence: {result['confidence']:5.1f}% | Score: {result['decision_score']:6.3f} {status}")
    
    # Test REAL articles
    print("\n" + "-"*70)
    print(f"TESTING {len(real_samples)} REAL ARTICLES (Should predict: REAL)")
    print("-"*70)
    
    real_correct = 0
    for i, text in enumerate(real_samples, 1):
        result = predict_article(model, vectorizer, text)
        
        if "error" in result:
            print(f"\n[REAL {i}] Error: {result['error']}")
            continue
        
        is_correct = result.get("label") == "REAL"
        status = "✓" if is_correct else "✗"
        real_correct += is_correct
        
        preview = text[:70].replace('\n', ' ')
        print(f"\n[REAL {i}] {preview}...")
        print(f"  → Verdict: {result['label']:5} | Confidence: {result['confidence']:5.1f}% | Score: {result['decision_score']:6.3f} {status}")
    
    # Summary
    total_tests = len(fake_samples) + len(real_samples)
    total_correct = fake_correct + real_correct
    accuracy = (total_correct / total_tests) * 100 if total_tests > 0 else 0
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"FAKE Correct:  {fake_correct}/{len(fake_samples)}")
    print(f"REAL Correct:  {real_correct}/{len(real_samples)}")
    print(f"Total Accuracy: {accuracy:.1f}% ({total_correct}/{total_tests})")
    print(f"Expected Model Accuracy: 99.69%")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
