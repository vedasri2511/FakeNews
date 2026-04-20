#!/usr/bin/env python3
"""Quick system test"""

import requests

article = """
Federal Reserve announces interest rate decision today. The decision came after weeks of economic data analysis. Financial markets react with updated stock valuations. Banks will implement the new rates within business days. This follows previous policy meetings. Economic experts provide analysis of the implications.
"""

print("="*70)
print("SYSTEM END-TO-END TEST")
print("="*70)

try:
    response = requests.post('http://localhost:5000/api/verify', 
                           json={'text': article},
                           timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ BACKEND RESPONDING")
        print(f"  ML Prediction: {result['mlPrediction']['label']} ({result['mlPrediction']['confidence']:.1f}%)")
        print(f"  Final Verdict: {result['verdict']}")
        print(f"  Explanation: {result['explanation']}")
        print(f"\n✅ SYSTEM WORKING - All services online!")
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"\n❌ Failed to connect: {e}")
    print("Make sure backend is running on port 5000")

print("="*70)
