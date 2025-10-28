"""
Sentiment Analysis for MedAI-Pro Chatbot
Emotion detection and urgency assessment in user messages
"""

from transformers import pipeline
from typing import Dict
from loguru import logger


class SentimentAnalyzer:
    """Analyze sentiment and emotions in medical conversations"""
    
    def __init__(self):
        # Load sentiment analysis pipeline
        try:
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            self.emotion_pipeline = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                top_k=None
            )
        except Exception as e:
            logger.warning(f"Could not load sentiment models: {e}")
            self.sentiment_pipeline = None
            self.emotion_pipeline = None
        
        # Emotion-urgency mapping
        self.emotion_urgency_map = {
            'fear': 'high',
            'anger': 'medium',
            'sadness': 'medium',
            'anxiety': 'high',
            'disgust': 'low',
            'joy': 'low',
            'neutral': 'low'
        }
        
        logger.info("✅ Sentiment Analyzer initialized")
    
    def analyze(self, text: str) -> Dict:
        """Analyze sentiment and emotion in text"""
        
        result = {
            'sentiment': 'neutral',
            'sentiment_score': 0.5,
            'emotion': 'neutral',
            'emotion_score': 0.5,
            'urgency_indicator': 'low',
            'emotional_state': 'calm'
        }
        
        if not text or len(text.strip()) < 3:
            return result
        
        # Sentiment analysis
        if self.sentiment_pipeline:
            try:
                sentiment_result = self.sentiment_pipeline(text[:512])[0]
                result['sentiment'] = sentiment_result['label'].lower()
                result['sentiment_score'] = sentiment_result['score']
            except Exception as e:
                logger.warning(f"Sentiment analysis failed: {e}")
        
        # Emotion detection
        if self.emotion_pipeline:
            try:
                emotion_results = self.emotion_pipeline(text[:512])[0]
                top_emotion = max(emotion_results, key=lambda x: x['score'])
                result['emotion'] = top_emotion['label']
                result['emotion_score'] = top_emotion['score']
                result['urgency_indicator'] = self.emotion_urgency_map.get(
                    top_emotion['label'], 'low'
                )
            except Exception as e:
                logger.warning(f"Emotion detection failed: {e}")
        
        # Determine emotional state
        result['emotional_state'] = self._determine_emotional_state(result)
        
        return result
    
    def _determine_emotional_state(self, analysis: Dict) -> str:
        """Determine overall emotional state"""
        emotion = analysis['emotion']
        sentiment = analysis['sentiment']
        
        if emotion in ['fear', 'anxiety']:
            return 'anxious'
        elif emotion == 'anger':
            return 'frustrated'
        elif emotion == 'sadness':
            return 'concerned'
        elif sentiment == 'negative':
            return 'distressed'
        elif emotion == 'joy':
            return 'positive'
        else:
            return 'calm'


if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    
    test_messages = [
        "I'm really worried about this chest pain",
        "Thank you so much for your help!",
        "I'm scared, the pain is getting worse"
    ]
    
    for msg in test_messages:
        result = analyzer.analyze(msg)
        print(f"\nMessage: {msg}")
        print(f"Sentiment: {result['sentiment']} ({result['sentiment_score']:.2f})")
        print(f"Emotion: {result['emotion']} ({result['emotion_score']:.2f})")
        print(f"State: {result['emotional_state']}")

