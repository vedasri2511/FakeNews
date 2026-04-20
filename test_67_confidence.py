#!/usr/bin/env python3
"""Test that 67% REAL confidence now marks as REAL instead of UNVERIFIED"""

import requests
import time

# Start fresh test
print("=" * 60)
print("TESTING: 67% REAL Confidence Fix")
print("=" * 60)

# Test article - something commonly verified by news sources
test_article = """
Climate Scientists Release New Report on Global Temperature Trends

A comprehensive study by leading climate scientists has been published today detailing 
the latest findings on global temperature patterns over the past decade. The research 
team analyzed data from multiple sources including satellite measurements and ground stations. 
Their conclusions show consistent warming patterns across major regions of the world. 
Environmental agencies worldwide are beginning to respond to these findings with policy adjustments.
The study involved collaboration between universities in multiple countries and represents 
significant progress in climate science research methods.
"""

# Endpoint with minimum 20 chars requirement
payload = {
    "text": test_article
}

print("\nSending article with 67% expected REAL confidence...\n")

try:
    response = requests.post('http://localhost:5000/api/verify', json=payload)
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"ML Prediction: {result['mlPrediction']['label']}")
        print(f"ML Confidence: {result['mlPrediction']['confidence']:.1f}%")
        print(f"\n🎯 VERDICT: {result['verdict']}")
        print(f"Explanation: {result['explanation']}")
        print(f"Final Confidence: {result['confidence']}%")
        
        # Check the fix
        if result['mlPrediction']['label'] == 'REAL' and result['mlPrediction']['confidence'] >= 65:
            if result['verdict'] == 'REAL':
                print("\n✅ SUCCESS: 67% REAL confidence now marked as REAL (not UNVERIFIED)")
            else:
                print(f"\n❌ ISSUE: 67% REAL confidence marked as {result['verdict']} (expected REAL)")
        
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Failed to connect to backend: {e}")
    print("Make sure backend is running on port 5000")

print("\n" + "=" * 60)
