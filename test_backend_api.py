#!/usr/bin/env python3
"""
Test the backend API prediction endpoint
"""
import requests
import json
import time

def test_backend():
    print("\n" + "="*70)
    print("TESTING BACKEND PREDICTION API")
    print("="*70)
    
    # Test 1: Health check
    print("\n[TEST 1] Health Check")
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return
    
    # Test 2: Verify endpoint with text
    print("\n[TEST 2] Text Verification")
    test_text = "Breaking News: Scientists at MIT discovered new renewable energy technology that could revolutionize power generation"
    
    try:
        response = requests.post(
            "http://localhost:5000/api/verify",
            json={"text": test_text},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        
        print(f"Verdict: {result.get('verdict')}")
        print(f"Confidence: {result.get('confidence')}%")
        print(f"ML Prediction: {result.get('mlPrediction')}")
        print(f"Explanation: {result.get('explanation')}")
        
        if result.get('verdict'):
            print("✓ Prediction successful!")
        else:
            print("❌ No verdict returned")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 3: Another text example
    print("\n[TEST 3] FAKE News Detection")
    fake_text = "BREAKING: President declares martial law! Military takes control! Banks shutdown immediately!"
    
    try:
        response = requests.post(
            "http://localhost:5000/api/verify",
            json={"text": fake_text},
            timeout=10
        )
        result = response.json()
        
        print(f"Verdict: {result.get('verdict')}")
        print(f"Confidence: {result.get('confidence')}%")
        print(f"ML Prediction: {result.get('mlPrediction')}")
        
        if result.get('mlPrediction', {}).get('label') == 'FAKE':
            print("✓ Correctly detected fake news!")
        else:
            print("⚠ May need to verify detection")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    test_backend()
