#!/usr/bin/env python3
"""
Real ML Model Prediction Script
Loads trained model and makes predictions on articles
"""

import pickle
import json
import sys
import os

def predict(text):
    """Make prediction on article text using trained ML model"""
    try:
        # Get the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(script_dir, 'model.pkl')
        vectorizer_path = os.path.join(script_dir, 'vectorizer.pkl')
        
        # Check if model files exist
        if not os.path.exists(model_path):
            return {"error": f"Model file not found: {model_path}"}
        
        if not os.path.exists(vectorizer_path):
            return {"error": f"Vectorizer file not found: {vectorizer_path}"}
        
        # Load model and vectorizer
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        with open(vectorizer_path, 'rb') as f:
            vectorizer = pickle.load(f)
        
        # Vectorize the text
        X = vectorizer.transform([text.lower()])

        # Make prediction and get calibrated probability
        prediction = int(model.predict(X)[0])
        prob = model.predict_proba(X)[0]   # [prob_FAKE, prob_REAL]

        label = "REAL" if prediction == 1 else "FAKE"
        confidence = round(float(prob[prediction]) * 100, 1)

        return {
            "label": label,
            "prediction": prediction,
            "confidence": confidence,
            "prob_fake": round(float(prob[0]) * 100, 1),
            "prob_real": round(float(prob[1]) * 100, 1),
        }
    
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Get text from command line argument
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No text provided"}))
        sys.exit(1)
    
    text = sys.argv[1]
    result = predict(text)
    print(json.dumps(result))
