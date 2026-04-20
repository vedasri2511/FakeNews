#!/usr/bin/env python3
"""Test multiple articles to find one with 65-70% REAL confidence"""

import requests
import time

test_articles = [
    {
        "name": "Typical Real News",
        "text": """
        US Federal Reserve announces interest rate decision today. The Federal Open Market Committee 
        met to discuss monetary policy. The decision came after weeks of economic data analysis. 
        Financial markets react to the announcement with updated stock valuations. Banks across the 
        country will implement the new rates within business days. This follows previous meetings 
        that established the current policy framework. Economic experts provide analysis of the implications.
        """
    },
    {
        "name": "Technology News",
        "text": """
        Tech giant announces new product line. The company held a press conference today to reveal 
        features and pricing. Analysts have provided initial reactions to the announcement. Pre-orders 
        begin next week with shipping expected by month end. The new product integrates with existing 
        services offered by the company. Competitors are expected to respond with their own announcements.
        """
    },
    {
        "name": "Sports News",
        "text": """
        Championship team wins major sporting event. The game was played before thousands of enthusiastic 
        fans. The winning team's star player scored crucial points late in the game. Postgame analysis 
        shows excellent defensive performance. The coach praised the team's preparation and execution. 
        Fans celebrated in the streets after the dramatic victory. The next championship game is scheduled.
        """
    },
]

print("=" * 70)
print("TESTING: Finding Articles with 65-75% REAL Confidence")
print("=" * 70)

for article in test_articles:
    print(f"\n📄 Testing: {article['name']}")
    print("-" * 70)
    
    payload = {"text": article['text']}
    
    try:
        response = requests.post('http://localhost:5000/api/verify', json=payload)
        
        if response.status_code == 200:
            result = response.json()
            ml_pred = result['mlPrediction']['label']
            ml_conf = result['mlPrediction']['confidence']
            verdict = result['verdict']
            
            print(f"ML Prediction: {ml_pred} ({ml_conf:.1f}%)")
            print(f"Verdict: {verdict}")
            
            # Highlight articles in the 65-75% range
            if ml_pred == "REAL" and 65 <= ml_conf <= 75:
                print(f"\n✅ FOUND! Article in 65-75% REAL confidence range")
                print(f"   Result: {verdict}")
                if verdict == "REAL":
                    print(f"   ✓ CORRECT: Now marked as REAL (fixed!)")
                else:
                    print(f"   ❌ STILL UNVERIFIED: Threshold may need adjustment")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Failed: {e}")

print("\n" + "=" * 70)
