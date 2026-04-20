#!/usr/bin/env python3
"""
Fake News Detection Model - Pure Python Training (No Pandas)
Reads CSV data manually and trains model
"""

import csv
import pickle
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix

print("="*80)
print("FAKE NEWS DETECTION MODEL - PURE PYTHON TRAINING")
print("="*80)

# ============================================================================
# STEP 1: LOAD CSV DATA MANUALLY
# ============================================================================
print("\n[1] Loading data from CSV files...")

def read_csv(filename):
    """Read CSV and extract title and text"""
    articles = []
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row.get('title', '') or ''
                text = row.get('text', '') or ''
                articles.append(f"{title} {text}")
    except Exception as e:
        print(f"  Error reading {filename}: {e}")
    return articles

fake_news = read_csv('Fake.csv')
real_news = read_csv('True.csv')

print(f"  ✓ Fake articles: {len(fake_news)}")
print(f"  ✓ Real articles: {len(real_news)}")
print(f"  ✓ Total: {len(fake_news) + len(real_news)}")

# ============================================================================
# STEP 2: PREPROCESS TEXT
# ============================================================================
print("\n[2] Preprocessing text...")

def preprocess(text):
    """Clean and preprocess text"""
    if not text:
        return ""
    # Lowercase
    text = text.lower()
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    # Remove emails
    text = re.sub(r'\S+@\S+', '', text)
    # Remove special chars
    text = re.sub(r'[^a-z0-9\s\.\!\?\,\-]', '', text)
    # Clean whitespace
    text = ' '.join(text.split())
    return text

fake_news = [preprocess(text) for text in fake_news]
real_news = [preprocess(text) for text in real_news]

# Remove empty
fake_news = [t for t in fake_news if t.strip()]
real_news = [t for t in real_news if t.strip()]

print(f"  ✓ After cleaning: Fake={len(fake_news)}, Real={len(real_news)}")

# ============================================================================
# STEP 3: CREATE LABELS AND COMBINE
# ============================================================================
print("\n[3] Creating dataset...")

X_data = fake_news + real_news
y_data = [0]*len(fake_news) + [1]*len(real_news)

# Shuffle
import random
combined = list(zip(X_data, y_data))
random.shuffle(combined)
X_data = [x[0] for x in combined]
y_data = [x[1] for x in combined]

print(f"  ✓ Total articles: {len(X_data)}")

# ============================================================================
# STEP 4: VECTORIZATION
# ============================================================================
print("\n[4] Creating TF-IDF vectors...")

vectorizer = TfidfVectorizer(
    max_features=8000,
    ngram_range=(1, 3),
    min_df=2,
    max_df=0.95,
    stop_words='english',
    sublinear_tf=True
)

X_vectors = vectorizer.fit_transform(X_data)
print(f"  ✓ Vector shape: {X_vectors.shape}")
print(f"  ✓ Features: {X_vectors.shape[1]}")

# Save vectorizer
with open('vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)
print(f"  ✓ Vectorizer saved")

# ============================================================================
# STEP 5: TRAIN/TEST SPLIT
# ============================================================================
print("\n[5] Train/test split...")

X_train, X_test, y_train, y_test = train_test_split(
    X_vectors, y_data,
    test_size=0.2,
    random_state=42,
    stratify=y_data
)

print(f"  ✓ Training: {X_train.shape[0]} samples")
print(f"  ✓ Testing: {X_test.shape[0]} samples")

# ============================================================================
# STEP 6: TRAIN MODEL
# ============================================================================
print("\n[6] Training models...")

models = {
    'LogisticRegression': LogisticRegression(max_iter=3000, C=0.5, class_weight='balanced', random_state=42),
    'SVM': LinearSVC(max_iter=3000, C=0.8, class_weight='balanced', random_state=42),
    'GradientBoosting': GradientBoostingClassifier(n_estimators=200, learning_rate=0.1, random_state=42)
}

best_model = None
best_f1 = 0
best_name = None

for name, model in models.items():
    print(f"\n  {name}:")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    pre = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print(f"    Accuracy:  {acc:.4f}")
    print(f"    Precision: {pre:.4f}")
    print(f"    Recall:    {rec:.4f}")
    print(f"    F1:        {f1:.4f}")
    
    if f1 > best_f1:
        best_f1 = f1
        best_model = model
        best_name = name

# ============================================================================
# STEP 7: SAVE BEST MODEL
# ============================================================================
print(f"\n[7] Best model: {best_name} (F1={best_f1:.4f})")

with open('model.pkl', 'wb') as f:
    pickle.dump(best_model, f)
print(f"  ✓ Model saved")

# ============================================================================
# STEP 8: FINAL EVALUATION
# ============================================================================
print("\n" + "="*80)
print("FINAL EVALUATION")
print("="*80)

y_pred_final = best_model.predict(X_test)
final_acc = accuracy_score(y_test, y_pred_final)

print(f"\nTest Accuracy: {final_acc:.4f} ({final_acc*100:.2f}%)")
print(f"F1-Score: {best_f1:.4f}")

print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_pred_final)
print(f"          Pred FAKE  Pred REAL")
print(f"Act FAKE  {cm[0,0]:6d}    {cm[0,1]:6d}")
print(f"Act REAL  {cm[1,0]:6d}    {cm[1,1]:6d}")

print("\n" + classification_report(y_test, y_pred_final, target_names=['FAKE', 'REAL']))

print("="*80)
print("Training complete! Model and vectorizer saved.")
print("="*80)
