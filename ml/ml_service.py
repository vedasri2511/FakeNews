#!/usr/bin/env python3
"""
ML Prediction Service - Fake news classification using trained LogisticRegression model.
Serves predictions via HTTP API (port 5001).
"""

from flask import Flask, request, jsonify
import pickle
import os
from pathlib import Path

app = Flask(__name__)

# Load model and vectorizer at startup
print("Loading ML model and vectorizer...")
try:
    script_dir = Path(__file__).parent
    model_path = script_dir / 'model.pkl'
    vectorizer_path = script_dir / 'vectorizer.pkl'

    if not model_path.exists():
        raise FileNotFoundError(f"Model not found at {model_path}")
    if not vectorizer_path.exists():
        raise FileNotFoundError(f"Vectorizer not found at {vectorizer_path}")

    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    with open(vectorizer_path, 'rb') as f:
        vectorizer = pickle.load(f)

    print(f"✓ ML Model loaded: {type(model).__name__}")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None
    vectorizer = None


@app.route('/predict', methods=['POST'])
def predict():
    """
    Classify article as FAKE or REAL using the trained model.
    Request:  { "text": "article content" }
    Response: { "label": "FAKE"|"REAL", "confidence": 0-100 }
    """
    try:
        if not model or not vectorizer:
            return jsonify({"error": "Model not loaded"}), 500

        data = request.json
        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400

        text = data.get('text', '')
        if not text or not text.strip():
            return jsonify({"error": "No text provided"}), 400

        # Vectorize and predict
        X_tfidf = vectorizer.transform([text.lower()])
        prediction = int(model.predict(X_tfidf)[0])

        # Use calibrated probability for confidence (LogisticRegression)
        prob = model.predict_proba(X_tfidf)[0]   # [prob_FAKE, prob_REAL]
        label = "REAL" if prediction == 1 else "FAKE"
        confidence = round(float(prob[prediction]) * 100, 1)

        return jsonify({
            "label": label,
            "confidence": confidence,
            "prob_fake": round(float(prob[0]) * 100, 1),
            "prob_real": round(float(prob[1]) * 100, 1),
        }), 200

    except Exception as e:
        print(f"❌ Error in /predict: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "running",
        "model_loaded": model is not None,
        "vectorizer_loaded": vectorizer is not None,
        "model_type": type(model).__name__ if model else None,
    }), 200


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("ML PREDICTION SERVICE")
    print("=" * 60)
    print("✓ Running on http://localhost:5001")
    print("✓ Endpoint: POST /predict")
    print("✓ Health:   GET  /health")
    print("=" * 60 + "\n")
    app.run(host='localhost', port=5001, debug=False, threaded=True)
