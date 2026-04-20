import pandas as pd  # type: ignore
import numpy as np  # type: ignore
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
from sklearn.linear_model import LogisticRegression  # type: ignore
from sklearn.model_selection import train_test_split  # type: ignore
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix  # type: ignore

# Read Fake.csv and True.csv
print("Loading data...")
fake_df = pd.read_csv('Fake.csv')
true_df = pd.read_csv('True.csv')

print(f"Fake news articles: {len(fake_df)}")
print(f"Real news articles: {len(true_df)}")

# Add labels
fake_df['label'] = 0  # 0 = FAKE
true_df['label'] = 1  # 1 = REAL

# Concat and shuffle
df = pd.concat([fake_df, true_df], ignore_index=True)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Clean text and create content column
df['title'] = df['title'].fillna('').astype(str).str.lower()
df['text'] = df['text'].fillna('').astype(str).str.lower()
df['content'] = df['title'] + ' ' + df['text']

# Remove empty rows
df = df[df['content'].str.strip() != '']

print(f"Total articles after cleaning: {len(df)}")

# Prepare data
X = df['content']
y = df['label']

# Improved TfidfVectorizer
print("Vectorizing text...")
vectorizer = TfidfVectorizer(
    max_features=5000,           # Reduced from 10000 to focus on important features
    ngram_range=(1, 2),
    min_df=5,                    # Ignore terms in fewer than 5 documents
    max_df=0.8,                  # Ignore terms in more than 80% of documents
    stop_words='english',
    lowercase=True,
    sublinear_tf=True            # Use sublinear TF scaling
)
X_tfidf = vectorizer.fit_transform(X)

print(f"Vocabulary size: {len(vectorizer.get_feature_names_out())}")

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X_tfidf, y, test_size=0.2, random_state=42, stratify=y
)

# Train LogisticRegression with class weights to handle imbalance
print("Training model...")
model = LogisticRegression(
    max_iter=2000,              # Increased iterations
    C=1.0,                      # Regularization strength
    class_weight='balanced',    # Handle class imbalance
    random_state=42,
    solver='lbfgs'
)
model.fit(X_train, y_train)

# Evaluate
print("\n" + "="*50)
print("MODEL EVALUATION")
print("="*50)

y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)

print(f"\nAccuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"\nConfusion Matrix:\n{confusion_matrix(y_test, y_pred)}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['FAKE', 'REAL']))

# Feature importance
print("\n" + "="*50)
print("TOP FEATURES FOR REAL NEWS (weight > 0.5)")
print("="*50)
feature_names = vectorizer.get_feature_names_out()
coefficients = model.coef_[0]
top_features_real = sorted(zip(feature_names, coefficients), key=lambda x: x[1], reverse=True)[:15]
for feature, coef in top_features_real:
    print(f"{feature:20} : {coef:.4f}")

print("\n" + "="*50)
print("TOP FEATURES FOR FAKE NEWS (weight < -0.5)")
print("="*50)
top_features_fake = sorted(zip(feature_names, coefficients), key=lambda x: x[1])[:15]
for feature, coef in top_features_fake:
    print(f"{feature:20} : {coef:.4f}")

# Save model and vectorizer
print("\n" + "="*50)
print("SAVING MODEL...")
print("="*50)

with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)

print("✓ Model saved to model.pkl")
print("✓ Vectorizer saved to vectorizer.pkl")
print("\nModel training complete!")