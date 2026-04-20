#!/usr/bin/env python3
"""Quick validation of the retrained model on real-time style articles."""
import pickle

with open('model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

print("Model type:", type(model).__name__)
print()

tests = [
    ("BREAKING: Obama admits he was born in Kenya!!! Secret exposed by whistleblower", "FAKE"),
    ("Federal Reserve raises interest rates 0.25 percent amid inflation concerns said chairman", "REAL"),
    ("Scientists discover cure for cancer hidden by Big Pharma elites you wont believe", "FAKE"),
    ("Senate passes bipartisan infrastructure bill after months of negotiations said lawmakers", "REAL"),
    ("Trump secretly working with Russia to destroy America patriots must fight back now", "FAKE"),
    ("Washington reuters - President signed healthcare bill on wednesday said officials", "REAL"),
    ("SHOCKING Deep state plotting against American people wake up sheeple watch video", "FAKE"),
    ("Government announced new environmental regulations on thursday reuters reported", "REAL"),
]

correct = 0
print(f"{'RESULT':<8} {'EXPECTED':<8} {'GOT':<8} {'CONF':>6}  {'P_FAKE':>7}  {'P_REAL':>7}  ARTICLE")
print("-" * 100)
for text, expected in tests:
    X = vectorizer.transform([text.lower()])
    pred = int(model.predict(X)[0])
    prob = model.predict_proba(X)[0]
    label = "REAL" if pred == 1 else "FAKE"
    conf = round(prob[pred] * 100, 1)
    ok = label == expected
    if ok:
        correct += 1
    status = "OK" if ok else "WRONG"
    print(f"[{status:<5}] {expected:<8} {label:<8} {conf:>5.1f}%  {prob[0]*100:>6.1f}%  {prob[1]*100:>6.1f}%  {text[:55]}")

print()
print(f"Accuracy: {correct}/{len(tests)} ({correct/len(tests)*100:.0f}%)")
