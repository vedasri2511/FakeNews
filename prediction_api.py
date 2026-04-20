#!/usr/bin/env python3
"""
API endpoint wrapper for improved predictions
Can be called from Node.js backend
"""

from flask import Flask, request, jsonify
from prediction_engine import PredictionEngine
import sys

app = Flask(__name__)
engine = PredictionEngine()

@app.route('/predict-with-quality', methods=['POST'])
def predict_with_quality():
    """
    Enhanced prediction using text quality analysis
    Input: { "text": "article text", "ml_prediction": "REAL/FAKE", "ml_confidence": 53.2 }
    Output: { "verdict": "REAL/FAKE/UNVERIFIED", ...}
    """
    try:
        data = request.json
        text = data.get('text', '')
        ml_prediction = data.get('ml_prediction', 'UNVERIFIED')
        ml_confidence = float(data.get('ml_confidence', 50))
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Analyze text quality
        quality, analysis = engine.analyze_text_quality(text)
        
        # Determine verdict using improved logic
        result = engine.determine_verdict(ml_prediction, ml_confidence, quality)
        
        return jsonify({
            "verdict": result['verdict'],
            "confidence": round(result['confidence'], 1),
            "explanation": result['explanation'],
            "text_quality": round(quality, 1),
            "ml_confidence": round(ml_confidence, 1),
            "analysis": analysis
        }), 200
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "running", "service": "Prediction Engine"}), 200

if __name__ == '__main__':
    print("Starting enhanced prediction API on port 5002...")
    app.run(host='0.0.0.0', port=5002, debug=False)
