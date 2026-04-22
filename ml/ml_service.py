#!/usr/bin/env python3
from flask import Flask, request, jsonify
import pickle
from pathlib import Path

app = Flask(__name__)

print("Loading ML model and vectorizer...")

try:
    script_dir = Path(__file__).parent
    model_path = script_dir / 'model.pkl'
    vectorizer_path = script_dir / 'vectorizer.pkl'

    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    with open(vectorizer_path, 'rb') as f:
        vectorizer = pickle.load(f)

    print("✓ Model loaded successfully")

except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None
    vectorizer = None


@app.route('/predict', methods=['POST'])
def predict():
    try:
        if not model or not vectorizer:
            return jsonify({"error": "Model not loaded"}), 500

        data = request.json
        text = data.get('text', '').strip()

        if not text:
            return jsonify({"error": "No text provided"}), 400

        # Preprocess
        text_clean = text.lower()

        # Vectorize
        X = vectorizer.transform([text_clean])

        # 🔥 CORRECT LOGIC (PROBABILITY BASED)
        probs = model.predict_proba(X)[0]

        prob_fake = probs[0]
        prob_real = probs[1]

        if prob_fake > prob_real:
            label = "FAKE"
            confidence = prob_fake * 100
        else:
            label = "REAL"
            confidence = prob_real * 100

        # 🔥 Handle uncertain predictions
        if confidence < 65:
            label = "UNCERTAIN"

        return jsonify({
            "label": label,
            "confidence": round(confidence, 2),
            "prob_fake": round(prob_fake * 100, 2),
            "prob_real": round(prob_real * 100, 2)
        })

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "running",
        "model_loaded": model is not None
    })


if __name__ == '__main__':
    print("ML SERVICE RUNNING ON http://localhost:5001")
    app.run(host='localhost', port=5001)