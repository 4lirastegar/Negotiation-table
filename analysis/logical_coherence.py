"""
Logical Coherence Analysis for Negotiation

This module uses sentence embeddings to measure logical coherence in negotiations.
Reveals genuine reasoning (goal-coherent), pragmatic adaptation (context-coherent),
and scripted behavior (incoherent).

Academic Reference:
Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings
using Siamese BERT-Networks. EMNLP 2019.
"""

from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer, util
import numpy as np


class LogicalCoherenceAnalyzer:
    """
    Analyzes three types of coherence in negotiations:
    
    1. Context Coherence: Does agent respond relevantly to opponent?
    2. Self Coherence: Are agent's messages consistent with each other?
    3. Goal Coherence: Do messages align with agent's objectives?
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the coherence analyzer.
        
        Args:
            model_name: Sentence-BERT model for embeddings
                       Default: all-MiniLM-L6-v2 (fast, good quality)
        """
        print(f"Loading logical coherence analyzer: {model_name}")
        self.model = SentenceTransformer(model_name)
        print("✅ Logical coherence analyzer loaded")
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not text1 or not text2:
            return 0.0
        
        # Encode both texts
        emb1 = self.model.encode(text1, convert_to_tensor=True)
        emb2 = self.model.encode(text2, convert_to_tensor=True)
        
        # Calculate cosine similarity
        similarity = util.cos_sim(emb1, emb2)
        
        return float(similarity.item())
    
    def analyze_negotiation(
        self,
        transcript: List[Dict[str, Any]],
        agent_a_role: str = "seller",
        agent_b_role: str = "buyer"
    ) -> Dict[str, Any]:
        """
        Analyze logical coherence for both agents.
        
        Args:
            transcript: List of message dictionaries
            agent_a_role: Role of Agent A (for goal coherence)
            agent_b_role: Role of Agent B (for goal coherence)
        
        Returns:
            Dict with coherence scores for each agent
        """
        # Separate messages by agent
        agent_a_messages = []
        agent_b_messages = []
        
        for msg in transcript:
            agent = msg.get('agent')
            message = msg.get('message', msg.get('content', ''))
            
            if not message:
                continue
            
            if agent == "Agent A":
                agent_a_messages.append(message)
            elif agent == "Agent B":
                agent_b_messages.append(message)
        
        # Analyze Agent A
        agent_a_coherence = self._analyze_agent_coherence(
            agent_messages=agent_a_messages,
            opponent_messages=agent_b_messages,
            agent_role=agent_a_role
        )
        
        # Analyze Agent B
        agent_b_coherence = self._analyze_agent_coherence(
            agent_messages=agent_b_messages,
            opponent_messages=agent_a_messages,
            agent_role=agent_b_role
        )
        
        return {
            "agent_a": agent_a_coherence,
            "agent_b": agent_b_coherence
        }
    
    def _analyze_agent_coherence(
        self,
        agent_messages: List[str],
        opponent_messages: List[str],
        agent_role: str
    ) -> Dict[str, Any]:
        """
        Analyze coherence for a single agent.
        
        Args:
            agent_messages: List of agent's messages
            opponent_messages: List of opponent's messages
            agent_role: Agent's role (seller/buyer)
        
        Returns:
            Dict with three coherence scores
        """
        if not agent_messages:
            return {
                "context_coherence": 0.0,
                "self_coherence": 0.0,
                "goal_coherence": 0.0,
                "overall_coherence": 0.0
            }
        
        # 1. Context Coherence: How well does agent respond to opponent?
        context_coherence = self._calculate_context_coherence(
            agent_messages,
            opponent_messages
        )
        
        # 2. Self Coherence: Are agent's messages consistent?
        self_coherence = self._calculate_self_coherence(agent_messages)
        
        # 3. Goal Coherence: Do messages align with role objective?
        goal_coherence = self._calculate_goal_coherence(
            agent_messages,
            agent_role
        )
        
        # Overall coherence (average)
        overall_coherence = np.mean([context_coherence, self_coherence, goal_coherence])
        
        return {
            "context_coherence": float(context_coherence),
            "self_coherence": float(self_coherence),
            "goal_coherence": float(goal_coherence),
            "overall_coherence": float(overall_coherence)
        }
    
    def _calculate_context_coherence(
        self,
        agent_messages: List[str],
        opponent_messages: List[str]
    ) -> float:
        """
        Measure how well agent responds to opponent's messages.
        
        High score = Pragmatic adaptation (context-aware)
        Low score = Scripted (ignores opponent)
        
        Args:
            agent_messages: Agent's messages
            opponent_messages: Opponent's messages
        
        Returns:
            Context coherence score (0.0 to 1.0)
        """
        if len(agent_messages) < 2 or len(opponent_messages) < 1:
            return 0.0
        
        similarities = []
        
        # For each agent message (except first), compare to previous opponent message
        for i in range(1, len(agent_messages)):
            # Get agent's message
            agent_msg = agent_messages[i]
            
            # Get opponent's previous message (if it exists)
            if i - 1 < len(opponent_messages):
                opponent_msg = opponent_messages[i - 1]
                similarity = self.calculate_similarity(agent_msg, opponent_msg)
                similarities.append(similarity)
        
        return float(np.mean(similarities)) if similarities else 0.0
    
    def _calculate_self_coherence(self, messages: List[str]) -> float:
        """
        Measure consistency between agent's own messages.
        
        High score = Logically consistent (genuine reasoning)
        Low score = Contradictory (confused/inconsistent)
        
        Args:
            messages: List of agent's messages
        
        Returns:
            Self coherence score (0.0 to 1.0)
        """
        if len(messages) < 2:
            return 0.0
        
        similarities = []
        
        # Compare consecutive messages
        for i in range(1, len(messages)):
            similarity = self.calculate_similarity(messages[i-1], messages[i])
            similarities.append(similarity)
        
        return float(np.mean(similarities))
    
    def _calculate_goal_coherence(self, messages: List[str], role: str) -> float:
        """
        Measure alignment between messages and role objective.
        
        High score = Genuine reasoning (goal-directed)
        Low score = Aimless (not strategic)
        
        Args:
            messages: List of agent's messages
            role: Agent's role (seller/buyer)
        
        Returns:
            Goal coherence score (0.0 to 1.0)
        """
        if not messages:
            return 0.0
        
        # Define goal descriptions for each role
        goal_descriptions = {
            "seller": "negotiate to maximize the selling price and get the best deal",
            "buyer": "negotiate to minimize the purchase price and get the best deal"
        }
        
        goal_text = goal_descriptions.get(role, "negotiate effectively")
        
        # Calculate similarity of each message to the goal
        similarities = []
        for message in messages:
            similarity = self.calculate_similarity(message, goal_text)
            similarities.append(similarity)
        
        return float(np.mean(similarities))


# Example usage and testing
if __name__ == "__main__":
    print("=" * 80)
    print("LOGICAL COHERENCE ANALYZER - EXAMPLE")
    print("=" * 80)
    
    # Example transcript
    example_transcript = [
        {
            "agent": "Agent A",
            "message": "I'm selling this car for $900. It's in excellent condition with low mileage."
        },
        {
            "agent": "Agent B",
            "message": "Thank you for the information. Given the condition, would you consider $700?"
        },
        {
            "agent": "Agent A",
            "message": "I appreciate your offer. Considering the car's features, I could go down to $850."
        },
        {
            "agent": "Agent B",
            "message": "That's closer. Could we meet at $775? That would work for my budget."
        },
        {
            "agent": "Agent A",
            "message": "I understand your budget concerns. Let's agree on $800 - that's my final offer."
        },
        {
            "agent": "Agent B",
            "message": "That sounds fair. I accept $800. Let's finalize the deal."
        }
    ]
    
    # Initialize analyzer
    analyzer = LogicalCoherenceAnalyzer()
    
    # Analyze
    results = analyzer.analyze_negotiation(
        example_transcript,
        agent_a_role="seller",
        agent_b_role="buyer"
    )
    
    print("\n📊 AGENT A (Seller):")
    print(f"   Context Coherence: {results['agent_a']['context_coherence']:.2f}")
    print(f"   Self Coherence: {results['agent_a']['self_coherence']:.2f}")
    print(f"   Goal Coherence: {results['agent_a']['goal_coherence']:.2f}")
    print(f"   Overall Coherence: {results['agent_a']['overall_coherence']:.2f}")
    
    print("\n📊 AGENT B (Buyer):")
    print(f"   Context Coherence: {results['agent_b']['context_coherence']:.2f}")
    print(f"   Self Coherence: {results['agent_b']['self_coherence']:.2f}")
    print(f"   Goal Coherence: {results['agent_b']['goal_coherence']:.2f}")
    print(f"   Overall Coherence: {results['agent_b']['overall_coherence']:.2f}")
    
    print("\n💡 INTERPRETATION:")
    print("   Context Coherence > 0.6 → Pragmatic adaptation (responds to opponent)")
    print("   Self Coherence > 0.7 → Genuine reasoning (logically consistent)")
    print("   Goal Coherence > 0.6 → Genuine reasoning (strategic)")
    
    print("\n" + "=" * 80)
    print("✅ Example complete!")
    print("=" * 80)
