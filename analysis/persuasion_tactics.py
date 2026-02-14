"""
Persuasion Tactics Detection for Negotiation Analysis

This module uses zero-shot classification to detect negotiation tactics in messages.
No manual keyword lists - uses pre-trained transformer models for academic rigor.

Academic Reference:
Yin, W., Hay, J., & Roth, D. (2019). Benchmarking Zero-shot Text Classification:
Datasets, Evaluation and Entailment Approach. EMNLP 2019.
"""

from typing import List, Dict, Any
from transformers import pipeline
import numpy as np


class PersuasionTacticsAnalyzer:
    """
    Detects negotiation tactics using zero-shot classification.
    
    Tactics detected:
    - persuasion: Convincing arguments, highlighting benefits
    - cooperation: Collaborative language, seeking mutual benefit
    - deception: Potentially misleading claims
    - pressure: Urgency, alternatives, threats (soft)
    - compromise: Offering middle ground
    """
    
    # Define negotiation tactics with descriptive labels for better classification
    TACTICS = [
        "Persuasion: gives reasons or benefits to convince the other side",
        "Cooperation: emphasizes mutual benefit, collaboration, or shared goals",
        "Pressure: uses urgency, scarcity, deadlines, or implied alternatives",
        "Compromise: offers middle ground or makes explicit concessions",
        "Deception: makes unverifiable or misleading claims"
    ]
    
    # Map full labels back to short names
    TACTIC_NAMES = {
        "Persuasion: gives reasons or benefits to convince the other side": "persuasion",
        "Cooperation: emphasizes mutual benefit, collaboration, or shared goals": "cooperation",
        "Pressure: uses urgency, scarcity, deadlines, or implied alternatives": "pressure",
        "Compromise: offers middle ground or makes explicit concessions": "compromise",
        "Deception: makes unverifiable or misleading claims": "deception"
    }
    
    def __init__(self, model_name: str = "MoritzLaurer/deberta-v3-large-zeroshot-v2.0"):
        """
        Initialize the tactics analyzer.
        
        Args:
            model_name: Pre-trained model for zero-shot classification
                       Default: DeBERTa-v3-large-zeroshot (SOTA performance)
        """
        print(f"Loading persuasion tactics analyzer: {model_name}")
        self.classifier = pipeline(
            "zero-shot-classification",
            model=model_name,
            device=0  # CPU = -1, GPU=0
        )
        print("✅ Persuasion tactics analyzer loaded")
    
    def classify_message(self, message: str, threshold: float = 0.5) -> Dict[str, Any]:
        """
        Classify a single message to detect tactics using improved hypothesis template.
        
        Args:
            message: The negotiation message text
            threshold: Minimum confidence to consider a tactic detected (0.0-1.0)
                      Default: 0.5 for high-confidence classification
        
        Returns:
            Dict with detected tactics and scores
        """
        if not message or len(message.strip()) < 5:
            return {"tactics": [], "scores": {}, "dominant_tactic": None}
        
        
        result = self.classifier(
            message,
            candidate_labels=self.TACTICS,
            hypothesis_template="The speaker is using {}.",
            multi_label=False  
        )
        
        # Map full labels back to short names and extract tactics above threshold
        detected_tactics = []
        scores = {}
        
        for label, score in zip(result['labels'], result['scores']):
            short_name = self.TACTIC_NAMES[label]
            scores[short_name] = float(score)
            if score >= threshold:
                detected_tactics.append(short_name)
        
        # Dominant tactic is the highest scoring one
        dominant_label = result['labels'][0] if result['labels'] else None
        dominant_tactic = self.TACTIC_NAMES.get(dominant_label) if dominant_label else None
        
        return {
            "tactics": detected_tactics,
            "scores": scores,
            "dominant_tactic": dominant_tactic,
            "dominant_score": scores.get(dominant_tactic, 0.0) if dominant_tactic else 0.0
        }
    
    def analyze_negotiation(
        self,
        transcript: List[Dict[str, Any]],
        threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Analyze all messages in a negotiation transcript.
        
        Args:
            transcript: List of message dictionaries with 'agent' and 'message' keys
            threshold: Minimum confidence for tactic detection (default: 0.5)
        
        Returns:
            Dict with tactic counts and patterns for each agent
        """
        # Initialize counters for each agent (using short tactic names)
        short_tactics = ["persuasion", "cooperation", "deception", "pressure", "compromise"]
        agent_a_tactics = {tactic: 0 for tactic in short_tactics}
        agent_b_tactics = {tactic: 0 for tactic in short_tactics}
        
        agent_a_messages = []
        agent_b_messages = []
        
        # Process each message
        for msg in transcript:
            agent = msg.get('agent')
            message = msg.get('message', msg.get('content', ''))
            
            if not message:
                continue
            
            # Classify the message
            classification = self.classify_message(message, threshold)
            
            # Count tactics for the agent
            if agent == "Agent A":
                for tactic in classification['tactics']:
                    agent_a_tactics[tactic] += 1
                agent_a_messages.append({
                    "message": message,
                    "tactics": classification['tactics'],
                    "dominant": classification['dominant_tactic'],
                    "scores": classification['scores']
                })
            elif agent == "Agent B":
                for tactic in classification['tactics']:
                    agent_b_tactics[tactic] += 1
                agent_b_messages.append({
                    "message": message,
                    "tactics": classification['tactics'],
                    "dominant": classification['dominant_tactic'],
                    "scores": classification['scores']
                })
        
        # Calculate statistics
        agent_a_total = sum(agent_a_tactics.values())
        agent_b_total = sum(agent_b_tactics.values())
        
        return {
            "agent_a": {
                "tactic_counts": agent_a_tactics,
                "total_tactics_detected": agent_a_total,
                "dominant_tactic": max(agent_a_tactics, key=agent_a_tactics.get) if agent_a_total > 0 else None,
                "tactic_diversity": self._calculate_diversity(agent_a_tactics),
                "messages": agent_a_messages
            },
            "agent_b": {
                "tactic_counts": agent_b_tactics,
                "total_tactics_detected": agent_b_total,
                "dominant_tactic": max(agent_b_tactics, key=agent_b_tactics.get) if agent_b_total > 0 else None,
                "tactic_diversity": self._calculate_diversity(agent_b_tactics),
                "messages": agent_b_messages
            }
        }
    
    def _calculate_diversity(self, tactic_counts: Dict[str, int]) -> float:
        """
        Calculate Shannon entropy to measure tactical diversity.
        
        High diversity = Uses varied tactics (adaptive)
        Low diversity = Repetitive (scripted)
        
        Args:
            tactic_counts: Dictionary of tactic counts
        
        Returns:
            Diversity score (higher = more diverse)
        """
        total = sum(tactic_counts.values())
        if total == 0:
            return 0.0
        
        # Calculate probabilities
        probs = np.array([count / total for count in tactic_counts.values()])
        
        # Filter out zero probabilities
        probs = probs[probs > 0]
        
        # Calculate Shannon entropy
        entropy = -np.sum(probs * np.log2(probs))
        
        return float(entropy)


# Example usage and testing
if __name__ == "__main__":
    print("=" * 80)
    print("PERSUASION TACTICS ANALYZER - EXAMPLE")
    print("=" * 80)
    
    # Example transcript
    example_transcript = [
        {
            "agent": "Agent A",
            "message": "This car has excellent features and very low mileage, making it a great value at this price."
        },
        {
            "agent": "Agent B",
            "message": "I appreciate the information. Could we work together to find a price that works for both of us?"
        },
        {
            "agent": "Agent A",
            "message": "I have other interested buyers, so I need to make a decision soon."
        },
        {
            "agent": "Agent B",
            "message": "How about we meet in the middle at $750? That seems fair to both parties."
        }
    ]
    
    # Initialize analyzer
    analyzer = PersuasionTacticsAnalyzer()
    
    # Analyze
    results = analyzer.analyze_negotiation(example_transcript)
    
    print("\n📊 AGENT A:")
    print(f"   Tactic Counts: {results['agent_a']['tactic_counts']}")
    print(f"   Dominant Tactic: {results['agent_a']['dominant_tactic']}")
    print(f"   Diversity Score: {results['agent_a']['tactic_diversity']:.2f}")
    
    print("\n📊 AGENT B:")
    print(f"   Tactic Counts: {results['agent_b']['tactic_counts']}")
    print(f"   Dominant Tactic: {results['agent_b']['dominant_tactic']}")
    print(f"   Diversity Score: {results['agent_b']['tactic_diversity']:.2f}")
    
    print("\n" + "=" * 80)
    print("✅ Example complete!")
    print("=" * 80)
