#!/usr/bin/env python3
import pickle
from pathlib import Path

ml_dir = Path('ml')
with open(ml_dir / 'model.pkl', 'rb') as f:
    model = pickle.load(f)
with open(ml_dir / 'vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

# Test articles from test_model.py
fake_articles = [
    "BREAKING: President declares martial law and seizes power! All banks closed immediately. This is a military takeover. Chaos in the streets!",
    "Scientists SHOCKED: Vaccine causes permanent death in 99% of people! Government hiding truth! Wake up sheeple!",
    "PROOF: The moon landing was filmed in Hollywood! NASA admits it's all fake! Don't believe the lie!",
    "LOCAL: Woman grows tree with $100 bills! Neighbors HATE her! Click here for the secret!",
    "EXCLUSIVE: Celebrity caught eating children in underground bunker! Police covering it up!",
]

real_articles = [
    "The Federal Reserve announced interest rate changes today affecting mortgage rates across the nation. The decision came after reviewing recent economic data.",
    "Scientists at MIT published their latest research on renewable energy technologies in the Journal of Applied Physics today.",
    "Government officials meet to discuss infrastructure improvements in transportation systems across the country.",
    "New study shows benefits of exercise for cardiovascular health, according to researchers at Johns Hopkins University.",
    "Stock market closes up 0.5% as investors react to quarterly earnings reports from major corporations.",
]

print('Getting decision scores for actual test articles:')
print('Fake scores:')
fake_scores = []
for article in fake_articles:
    X = vectorizer.transform([article])
    score = model.decision_function(X)[0]
    fake_scores.append(score)
    print(f'  {score:.4f}')

print('Real scores:')
real_scores = []
for article in real_articles:
    X = vectorizer.transform([article])
    score = model.decision_function(X)[0]
    real_scores.append(score)
    print(f'  {score:.4f}')

print()
print(f'Fake: min={min(fake_scores):.4f}, max={max(fake_scores):.4f}')
print(f'Real: min={min(real_scores):.4f}, max={max(real_scores):.4f}')

# Find best threshold
print()
print('Testing thresholds (pred=1 if score < threshold else 0):')
best_acc = 0
best_thresh = 0
for threshold in [-3, -2.5, -2, -1.5, -1.2, -1.0, -0.8, -0.6, -0.4, -0.2, 0]:
    fake_correct = sum(1 for s in fake_scores if s < threshold)
    real_correct = sum(1 for s in real_scores if s >= threshold)
    acc = (fake_correct + real_correct) / 10
    print(f'  Threshold {threshold:5.1f}: Fake {fake_correct}/5, Real {real_correct}/5, Acc {acc*100:.0f}%')
    if acc > best_acc:
        best_acc = acc
        best_thresh = threshold

print()
print(f'Best threshold: {best_thresh} with {best_acc*100:.0f}% accuracy')
