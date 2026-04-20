#!/usr/bin/env python3
"""
IMPROVED FAKE NEWS DETECTION MODEL - V2
Enhanced training with better features, preprocessing, and validation
"""

import pandas as pd
import numpy as np
import pickle
import warnings
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    classification_report, accuracy_score, confusion_matrix, 
    roc_auc_score, precision_score, recall_score, f1_score
)
import re

warnings.filterwarnings('ignore')

print("="*80)
print("FAKE NEWS DETECTION MODEL - TRAINING V2")
print("="*80)

# ============================================================================
# STEP 1: LOAD AND PREPROCESS DATA
# ============================================================================
print("\n[1/7] Loading datasets...")
try:
    fake_df = pd.read_csv('Fake.csv')
    true_df = pd.read_csv('True.csv')
    print(f"  ✓ Fake news: {len(fake_df)} articles")
    print(f"  ✓ Real news: {len(true_df)} articles")
    print(f"  ✓ Total: {len(fake_df) + len(true_df)} articles")
except Exception as e:
    print(f"  ✗ Error loading data: {e}")
    exit(1)

# Add labels
fake_df['label'] = 0  # 0 = FAKE
true_df['label'] = 1  # 1 = REAL

# Combine and shuffle
df = pd.concat([fake_df, true_df], ignore_index=True)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"  ✓ Combined and shuffled")

# ============================================================================
# STEP 2: ADVANCED TEXT PREPROCESSING
# ============================================================================
print("\n[2/7] Advanced text preprocessing...")

def preprocess_text(text):
    """Enhanced text preprocessing"""
    if not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove special characters but keep important punctuation
    text = re.sub(r'[^a-z0-9\s\.\!\?\,\-]', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text

# Preprocess content
df['title'] = df['title'].fillna('').apply(preprocess_text)
df['text'] = df['text'].fillna('').apply(preprocess_text)
df['content'] = df['title'] + ' ' + df['text']

# Remove empty articles
initial_count = len(df)
df = df[df['content'].str.strip() != '']
print(f"  ✓ Processed {initial_count} articles -> {len(df)} (after cleaning)")

# ============================================================================
# STEP 3: VECTORIZATION WITH MULTIPLE FEATURES
# ============================================================================
print("\n[3/7] Feature extraction...")

X_text = df['content'].values
y = df['label'].values

# TF-IDF Vectorizer (OPTIMIZED)
print("  • TF-IDF features...")
tfidf = TfidfVectorizer(
    max_features=8000,          # Increase features
    ngram_range=(1, 3),         # Include trigrams
    min_df=2,                   # Lower threshold
    max_df=0.95,                # Higher threshold
    stop_words='english',
    lowercase=True,
    sublinear_tf=True,
    use_idf=True,
    norm='l2'
)
X_tfidf = tfidf.fit_transform(X_text)
print(f"    Features: {X_tfidf.shape[1]}")

# Save vectorizer
with open('vectorizer.pkl', 'wb') as f:
    pickle.dump(tfidf, f)
print(f"  ✓ Vectorizer saved")

# ============================================================================
# STEP 4: TRAIN/TEST SPLIT WITH STRATIFICATION
# ============================================================================
print("\n[4/7] Splitting data...")

X_train, X_test, y_train, y_test = train_test_split(
    X_tfidf, y, 
    test_size=0.2, 
    random_state=42, 
    stratify=y
)

print(f"  ✓ Training set: {X_train.shape[0]} samples")
print(f"  ✓ Test set: {X_test.shape[0]} samples")
print(f"  ✓ Class distribution (train): FAKE={np.sum(y_train==0)}, REAL={np.sum(y_train==1)}")
print(f"  ✓ Class distribution (test): FAKE={np.sum(y_test==0)}, REAL={np.sum(y_test==1)}")

# ============================================================================
# STEP 5: TRAIN MULTIPLE MODELS AND SELECT BEST
# ============================================================================
print("\n[5/7] Training models...")

models = {
    'Logistic Regression': LogisticRegression(
        max_iter=3000,
        C=0.5,
        class_weight='balanced',
        solver='lbfgs',
        random_state=42
    ),
    'SVM (Linear)': LinearSVC(
        max_iter=3000,
        C=0.8,
        class_weight='balanced',
        random_state=42,
        loss='squared_hinge'
    ),
    'Gradient Boosting': GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=5,
        subsample=0.8,
        random_state=42
    )
}

best_model = None
best_score = 0
best_name = None
model_scores = {}

for name, model in models.items():
    print(f"\n  Training {name}...")
    model.fit(X_train, y_train)
    
    # Predictions
    y_pred = model.predict(X_test)
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    model_scores[name] = {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }
    
    print(f"    Accuracy:  {accuracy:.4f}")
    print(f"    Precision: {precision:.4f}")
    print(f"    Recall:    {recall:.4f}")
    print(f"    F1-Score:  {f1:.4f}")
    
    # Select best model based on F1 score
    if f1 > best_score:
        best_score = f1
        best_model = model
        best_name = name

print(f"\n  ✓ Best Model: {best_name} (F1={best_score:.4f})")

# Save the best model
with open('model.pkl', 'wb') as f:
    pickle.dump(best_model, f)
print(f"  ✓ Model saved to model.pkl")

# ============================================================================
# STEP 6: DETAILED EVALUATION
# ============================================================================
print("\n[6/7] Detailed Evaluation on Test Set...")
print("="*80)

y_pred = best_model.predict(X_test)

print("\nCONFUSION MATRIX:")
cm = confusion_matrix(y_test, y_pred)
print(f"                Predicted")
print(f"                FAKE  REAL")
print(f"Actual FAKE     {cm[0,0]:4d}  {cm[0,1]:4d}")
print(f"       REAL     {cm[1,0]:4d}  {cm[1,1]:4d}")

print("\nCLASSIFICATION REPORT:")
print(classification_report(y_test, y_pred, target_names=['FAKE', 'REAL']))

# ============================================================================
# STEP 7: CROSS-VALIDATION
# ============================================================================
print("[7/7] Cross-Validation (5-fold)...")

cv_scores = cross_val_score(best_model, X_tfidf, y, cv=5, scoring='f1')
print(f"  Fold scores: {[f'{s:.4f}' for s in cv_scores]}")
print(f"  Mean CV F1-Score: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*80)
print("TRAINING COMPLETE - FINAL SUMMARY")
print("="*80)

y_pred_final = best_model.predict(X_test)
final_accuracy = accuracy_score(y_test, y_pred_final)

print(f"\n✓ Model: {best_name}")
print(f"✓ Test Accuracy: {final_accuracy:.4f} ({final_accuracy*100:.2f}%)")
print(f"✓ F1-Score: {best_score:.4f}")
print(f"✓ Model file: model.pkl")
print(f"✓ Vectorizer file: vectorizer.pkl")

print(f"\nModel is ready for production!")
print("="*80)
