#!/usr/bin/env python3
"""
Improved Prediction Engine
Uses multiple signals to determine if an article is real or fake
Combines ML model with text analysis and quality metrics
"""

import re
from datetime import datetime

class PredictionEngine:
    """Enhanced prediction engine with multiple signals"""
    
    def __init__(self):
        self.news_keywords = {
            'official': ['announces', 'declared', 'confirmed', 'authorized', 'official'],
            'credible': ['reuters', 'associated press', 'bbc', 'guardian', 'times', 'washington post'],
            'suspicious': ['shocking', 'exclusive', 'unbelievable', 'bombshell', 'REVEALED'],
        }
    
    def analyze_text_quality(self, text):
        """Analyze article text for quality signals"""
        scores = {
            'length': len(text),
            'word_count': len(text.split()),
            'has_quotes': '"' in text or "'" in text,
            'has_sources': 'said' in text.lower() or 'according' in text.lower(),
            'proper_formatting': text.count('.') > 2,  # Multiple sentences
            'credibility_words': sum(1 for word in text.lower().split() if word in ['official', 'confirmed', 'reported']),
        }
        
        # Calculate quality score (0-100)
        quality = 0
        if scores['word_count'] > 100:
            quality += 20
        if scores['has_quotes']:
            quality += 15
        if scores['has_sources']:
            quality += 20
        if scores['proper_formatting']:
            quality += 15
        if scores['credibility_words'] > 0:
            quality += 20
        if scores['length'] > 200:
            quality += 10
            
        return min(100, quality), scores
    
    def calculate_enhanced_confidence(self, ml_prediction, ml_confidence, text_quality):
        """
        Combine ML prediction with text quality for better confidence
        """
        # If text quality is high and ML says REAL, increase confidence
        if ml_prediction == "REAL" and text_quality > 50:
            enhanced_confidence = min(95, ml_confidence + (text_quality * 0.15))
        # If ML says FAKE but text quality is high, reduce FAKE confidence
        elif ml_prediction == "FAKE" and text_quality > 60:
            enhanced_confidence = max(45, ml_confidence - (text_quality * 0.1))
        else:
            enhanced_confidence = ml_confidence
        
        return enhanced_confidence
    
    def determine_verdict(self, ml_prediction, ml_confidence, text_quality):
        """
        Determine final verdict using multiple signals
        """
        enhanced_conf = self.calculate_enhanced_confidence(ml_prediction, ml_confidence, text_quality)
        
        if ml_prediction == "REAL":
            if enhanced_conf > 70:
                verdict = "REAL"
                explanation = f"✓ HIGH CONFIDENCE REAL (Text quality: {text_quality:.0f}%, ML: {ml_confidence:.0f}%)"
            elif enhanced_conf > 55:
                verdict = "REAL"
                explanation = f"✓ REAL (Text quality: {text_quality:.0f}%, ML: {ml_confidence:.0f}%)"
            else:
                verdict = "UNVERIFIED"
                explanation = f"⚠ UNCERTAIN (Low confidence - verify independently)"
        else:  # FAKE
            if enhanced_conf > 75:
                verdict = "FAKE"
                explanation = f"❌ HIGH CONFIDENCE FAKE (Pattern matching: {enhanced_conf:.0f}%)"
            elif enhanced_conf > 60:
                verdict = "UNVERIFIED"
                explanation = f"⚠ UNCERTAIN (Some suspicious patterns detected)"
            else:
                verdict = "REAL"  # Conservative: low confidence FAKE = likely REAL
                explanation = f"✓ Likely REAL (Insufficient misinformation signals)"
        
        return {
            "verdict": verdict,
            "confidence": min(95, enhanced_conf),
            "explanation": explanation,
            "text_quality": text_quality,
            "ml_confidence": ml_confidence
        }

# Example usage
if __name__ == "__main__":
    engine = PredictionEngine()
    
    test_text = """
    Oil prices ease on hopes of new US-Iran peace talks. International negotiations 
    continue as both nations express willingness to resolve disputes. Economic experts 
    predict potential market stabilization if talks progress successfully. Oil futures 
    fell 2% today according to Bloomberg reports.
    """
    
    quality, analysis = engine.analyze_text_quality(test_text)
    result = engine.determine_verdict("REAL", 51.3, quality)
    
    print("Sample Prediction:")
    print(f"  Text Quality: {quality:.0f}%")
    print(f"  Verdict: {result['verdict']}")
    print(f"  Confidence: {result['confidence']:.1f}%")
    print(f"  Explanation: {result['explanation']}")
