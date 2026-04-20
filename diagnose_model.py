#!/usr/bin/env python3
"""
Diagnose model behavior - check if classes are inverted
"""
import pickle
from pathlib import Path

ml_dir = Path("ml")
model_path = ml_dir / "model.pkl"
vectorizer_path = ml_dir / "vectorizer.pkl"

# Load models
with open(model_path, 'rb') as f:
    model = pickle.load(f)

with open(vectorizer_path, 'rb') as f:
    vectorizer = pickle.load(f)

print("\n" + "="*70)
print("MODEL DIAGNOSTICS")
print("="*70)

print(f"\nModel Classes: {model.classes_}")
print(f"Model Type: {type(model).__name__}")

# Test with clear examples
test_cases = [
    ("FAKE: Trump declares martial law! President takes military control!", "FAKE"),
    ("WASHINGTON (Reuters) - President signs new infrastructure bill", "REAL"),
    ("BREAKING: Vaccine causes deaths! Government hiding truth!", "FAKE"),
    ("Scientists at MIT publish new research on climate change", "REAL"),
]

print("\n" + "-"*70)
print("TESTING PREDICTIONS")
print("-"*70)

for text, expected_label in test_cases:
    X = vectorizer.transform([text])
    pred = model.predict(X)[0]
    decision = model.decision_function(X)[0]
    
    # Try both interpretations
    label_normal = "REAL" if int(pred) == 1 else "FAKE"
    label_inverted = "FAKE" if int(pred) == 1 else "REAL"
    
    print(f"\nText: {text[:60]}...")
    print(f"Expected: {expected_label}")
    print(f"Raw Prediction: {int(pred)}")
    print(f"Decision Score: {decision:.4f}")
    print(f"  → Normal interpretation:   {label_normal}")
    print(f"  → Inverted interpretation: {label_inverted}")
    
    if label_normal == expected_label:
        print("  ✓ NORMAL IS CORRECT")
    elif label_inverted == expected_label:
        print("  ✓ INVERTED IS CORRECT")
    else:
        print("  ✗ NEITHER MATCHES")

print("\n" + "="*70 + "\n")
