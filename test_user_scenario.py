#!/usr/bin/env python3
"""Simulate the user's exact scenario: 67% REAL confidence article"""

import requests

# Use text relevant to actual news to increase REAL confidence
articles_to_test = [
    {
        "name": "Article likely to get 65-70% REAL",
        "text": """
        New Study Shows Positive Results in Medical Research

        Researchers announced findings from a major clinical study today. The research examined 
        treatment effectiveness across multiple hospitals. Results showed significant improvement 
        in patient outcomes. The study was led by renowned medical scientists from prestigious 
        institutions. Peer review process confirmed the validity of the findings. Medical journals 
        will publish the complete research. Healthcare providers are reviewing implications. 
        Patients eligible for the treatment will soon have access. The international medical 
        community praised the advancement. Future research will build on these discoveries. 
        Government health agencies are examining the data. Clinical applications expected within 
        months. Hospitals are preparing implementation protocols.
        """
    },
    {
        "name": "Federal Government Announcement",
        "text": """
        Federal Agency Announces Policy Changes

        The agency released a statement regarding new regulatory framework today. Officials 
        explained the rationale behind the policy shift. The changes affect multiple sectors 
        of the economy. Stakeholders from industry provided initial responses. The policy 
        takes effect next quarter. Compliance requirements are being clarified. Federal 
        agencies are coordinating implementation. State governments began preparations. 
        Businesses submitted feedback during comment periods. The regulation follows extensive 
        analysis. Congressional representatives received briefings. Economic impact reports 
        are being prepared. Public hearings will be held next month.
        """
    },
]

print("=" * 80)
print("SIMULATING USER'S SCENARIO: 67% REAL Confidence Article")
print("=" * 80)

for article in articles_to_test:
    print(f"\n📰 Test Case: {article['name']}")
    print("-" * 80)
    
    payload = {"text": article['text']}
    
    try:
        response = requests.post('http://localhost:5000/api/verify', json=payload)
        
        if response.status_code == 200:
            result = response.json()
            ml_pred = result['mlPrediction']['label']
            ml_conf = result['mlPrediction']['confidence']
            verdict = result['verdict']
            explanation = result['explanation']
            
            print(f"ML Prediction: {ml_pred}")
            print(f"ML Confidence: {ml_conf:.1f}%")
            print(f"Final Verdict: {verdict}")
            print(f"Explanation: {explanation}")
            
            # Check if it matches the 67% scenario
            if ml_conf >= 65 and ml_pred == "REAL":
                print(f"\n✅ SIMULATED 67% REAL case:")
                if verdict == "REAL":
                    print(f"   SUCCESS! Article marked as REAL (not UNVERIFIED)")
                    print(f"   The fix is working correctly! ✓")
                else:
                    print(f"   ISSUE: Article still marked as {verdict}")
                    print(f"   Threshold may need further adjustment")
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Failed: {e}")

print("\n" + "=" * 80)
print("ANALYSIS:")
print("  If article shows 65%+ REAL confidence → Should be marked REAL")
print("  If still marked UNVERIFIED → Need to lower threshold further")
print("=" * 80)
