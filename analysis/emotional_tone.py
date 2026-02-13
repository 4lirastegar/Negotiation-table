"""
Emotional Tone Detection for Negotiation Analysis

This module uses pre-trained emotion classification to detect emotional patterns.
Reveals cooperation (positive), pressure (negative), and rational behavior (neutral).

Academic Reference:
Hartmann, J., Heitmann, M., Siebert, C., & Schamp, C. (2023).
More than a Feeling: Accuracy and Application of Sentiment Analysis.
International Journal of Research in Marketing.
"""

from typing import List, Dict, Any
from transformers import pipeline
import numpy as np


class EmotionalToneAnalyzer:
    """
    Detects emotional tone in negotiation messages.
    
    Emotions detected (based on model):
    - Positive emotions: joy, optimism, trust
    - Neutral: matter-of-fact, rational
    - Negative emotions: anger, sadness, fear
    """
    
    def __init__(self, model_name: str = "j-hartmann/emotion-english-distilroberta-base"):
        """
        Initialize the emotional tone analyzer.
        
        Args:
            model_name: Pre-trained emotion classification model
                       Default: emotion-english-distilroberta-base (7 emotions)
        """
        print(f"Loading emotional tone analyzer: {model_name}")
        self.classifier = pipeline(
            "text-classification",
            model=model_name,
            top_k=None,  # Get scores for all emotions
            device=-1  # CPU, use device=0 for GPU
        )
        print("✅ Emotional tone analyzer loaded")
        
        # Map emotions to categories
        self.emotion_categories = {
            "joy": "positive",
            "love": "positive",
            "surprise": "positive",
            "neutral": "neutral",
            "sadness": "negative",
            "anger": "negative",
            "fear": "negative"
        }
    
    def classify_message(self, message: str) -> Dict[str, Any]:
        """
        Classify emotional tone of a single message.
        
        Args:
            message: The negotiation message text
        
        Returns:
            Dict with emotion, category, and confidence
        """
        if not message or len(message.strip()) < 5:
            return {
                "emotion": "neutral",
                "category": "neutral",
                "confidence": 1.0,
                "all_scores": {}
            }
        
        # Run emotion classification
        result = self.classifier(message)[0]  # Returns list of dicts with all emotions
        
        # Extract all emotion scores
        all_scores = {item['label']: item['score'] for item in result}
        
        # Get dominant emotion
        dominant = max(result, key=lambda x: x['score'])
        emotion = dominant['label']
        confidence = dominant['score']
        
        # Categorize as positive/neutral/negative
        category = self.emotion_categories.get(emotion, "neutral")
        
        return {
            "emotion": emotion,
            "category": category,
            "confidence": float(confidence),
            "all_scores": {k: float(v) for k, v in all_scores.items()}
        }
    
    def analyze_negotiation(
        self,
        transcript: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze emotional tone across entire negotiation.
        
        Args:
            transcript: List of message dictionaries with 'agent' and 'message' keys
        
        Returns:
            Dict with emotional patterns for each agent
        """
        # Initialize counters
        agent_a_emotions = {"positive": 0, "neutral": 0, "negative": 0}
        agent_b_emotions = {"positive": 0, "neutral": 0, "negative": 0}
        
        agent_a_sequence = []
        agent_b_sequence = []
        
        # Process each message
        for msg in transcript:
            agent = msg.get('agent')
            message = msg.get('message', msg.get('content', ''))
            
            if not message:
                continue
            
            # Classify emotion
            classification = self.classify_message(message)
            
            if agent == "Agent A":
                agent_a_emotions[classification['category']] += 1
                agent_a_sequence.append(classification)
            elif agent == "Agent B":
                agent_b_emotions[classification['category']] += 1
                agent_b_sequence.append(classification)
        
        # Calculate statistics for Agent A
        agent_a_total = sum(agent_a_emotions.values())
        agent_a_distribution = {
            k: v / agent_a_total if agent_a_total > 0 else 0.0
            for k, v in agent_a_emotions.items()
        }
        
        # Calculate statistics for Agent B
        agent_b_total = sum(agent_b_emotions.values())
        agent_b_distribution = {
            k: v / agent_b_total if agent_b_total > 0 else 0.0
            for k, v in agent_b_emotions.items()
        }
        
        return {
            "agent_a": {
                "emotion_counts": agent_a_emotions,
                "emotion_distribution": agent_a_distribution,
                "dominant_tone": max(agent_a_emotions, key=agent_a_emotions.get) if agent_a_total > 0 else "neutral",
                "emotional_volatility": self._calculate_volatility(agent_a_sequence),
                "sequence": agent_a_sequence
            },
            "agent_b": {
                "emotion_counts": agent_b_emotions,
                "emotion_distribution": agent_b_distribution,
                "dominant_tone": max(agent_b_emotions, key=agent_b_emotions.get) if agent_b_total > 0 else "neutral",
                "emotional_volatility": self._calculate_volatility(agent_b_sequence),
                "sequence": agent_b_sequence
            },
            "emotional_correlation": self._calculate_correlation(agent_a_sequence, agent_b_sequence)
        }
    
    def _calculate_volatility(self, emotion_sequence: List[Dict]) -> float:
        """
        Calculate emotional volatility (how much emotions change).
        
        High volatility = Emotions change frequently (reactive/adaptive)
        Low volatility = Stable emotional tone (consistent)
        
        Args:
            emotion_sequence: List of emotion classifications
        
        Returns:
            Volatility score (0.0 to 1.0, higher = more volatile)
        """
        if len(emotion_sequence) < 2:
            return 0.0
        
        # Map categories to numbers: positive=1, neutral=0, negative=-1
        category_values = {"positive": 1, "neutral": 0, "negative": -1}
        
        values = [category_values[e['category']] for e in emotion_sequence]
        
        # Calculate standard deviation of changes
        changes = [abs(values[i] - values[i-1]) for i in range(1, len(values))]
        
        if not changes:
            return 0.0
        
        volatility = np.mean(changes)
        return float(volatility)
    
    def _calculate_correlation(
        self,
        agent_a_sequence: List[Dict],
        agent_b_sequence: List[Dict]
    ) -> float:
        """
        Calculate emotional correlation between agents.
        
        High correlation = Agents mirror each other's emotions (adaptive)
        Low correlation = Independent emotional patterns
        
        Args:
            agent_a_sequence: Agent A's emotion sequence
            agent_b_sequence: Agent B's emotion sequence
        
        Returns:
            Correlation coefficient (-1 to 1)
        """
        # Need at least 2 pairs of messages
        min_len = min(len(agent_a_sequence), len(agent_b_sequence))
        if min_len < 2:
            return 0.0
        
        # Map categories to numbers
        category_values = {"positive": 1, "neutral": 0, "negative": -1}
        
        a_values = [category_values[agent_a_sequence[i]['category']] for i in range(min_len)]
        b_values = [category_values[agent_b_sequence[i]['category']] for i in range(min_len)]
        
        # Calculate Pearson correlation
        if len(set(a_values)) == 1 or len(set(b_values)) == 1:
            # No variation in one of the sequences
            return 0.0
        
        correlation = np.corrcoef(a_values, b_values)[0, 1]
        
        # Return 0 if NaN
        return float(correlation) if not np.isnan(correlation) else 0.0


# Example usage and testing
if __name__ == "__main__":
    print("=" * 80)
    print("EMOTIONAL TONE ANALYZER - EXAMPLE")
    print("=" * 80)
    
    # Example transcript
    example_transcript = [
        {
            "agent": "Agent A",
            "message": "Hello! I'm excited to discuss this wonderful car with you."
        },
        {
            "agent": "Agent B",
            "message": "Thank you. Let's work together to find a fair price."
        },
        {
            "agent": "Agent A",
            "message": "I'm afraid that price is too low for me."
        },
        {
            "agent": "Agent B",
            "message": "I understand your concerns. Perhaps we can compromise?"
        }
    ]
    
    # Initialize analyzer
    analyzer = EmotionalToneAnalyzer()
    
    # Analyze
    results = analyzer.analyze_negotiation(example_transcript)
    
    print("\n📊 AGENT A:")
    print(f"   Emotion Counts: {results['agent_a']['emotion_counts']}")
    print(f"   Distribution: {results['agent_a']['emotion_distribution']}")
    print(f"   Dominant Tone: {results['agent_a']['dominant_tone']}")
    print(f"   Volatility: {results['agent_a']['emotional_volatility']:.2f}")
    
    print("\n📊 AGENT B:")
    print(f"   Emotion Counts: {results['agent_b']['emotion_counts']}")
    print(f"   Distribution: {results['agent_b']['emotion_distribution']}")
    print(f"   Dominant Tone: {results['agent_b']['dominant_tone']}")
    print(f"   Volatility: {results['agent_b']['emotional_volatility']:.2f}")
    
    print(f"\n🔗 Emotional Correlation: {results['emotional_correlation']:.2f}")
    
    print("\n" + "=" * 80)
    print("✅ Example complete!")
    print("=" * 80)
