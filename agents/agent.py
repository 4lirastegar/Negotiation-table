"""
Base Agent Class
Handles LLM integration and message generation for negotiation agents
"""

import os
import re
from typing import Dict, List, Optional, Any
from config.config import OPENAI_API_KEY, ANTHROPIC_API_KEY, LLM_PROVIDER, LLM_MODEL
from personas.persona_manager import PersonaManager


class Agent:
    """Base class for negotiation agents"""
    
    def __init__(
        self,
        agent_id: str,
        persona_name: str,
        scenario_public_info: Dict,
        agent_secrets: Dict,
        llm_provider: str = None,
        llm_model: str = None
    ):
        """
        Initialize an agent
        
        Args:
            agent_id: Unique identifier for the agent (e.g., "Agent A", "Agent B")
            persona_name: Name of the persona to use
            scenario_public_info: Public information from the scenario
            agent_secrets: Agent's private information
            llm_provider: LLM provider to use (openai or anthropic)
            llm_model: Model name to use
        """
        self.agent_id = agent_id
        self.persona_name = persona_name
        self.scenario_public_info = scenario_public_info
        self.agent_secrets = agent_secrets
        self.persona_manager = PersonaManager()
        
        # LLM configuration
        self.llm_provider = llm_provider or LLM_PROVIDER
        self.llm_model = llm_model or LLM_MODEL
        
        # Initialize LLM client
        self.llm_client = self._initialize_llm_client()
        
        # Conversation tracking
        self.conversation_history: List[Dict[str, str]] = []
        self.proposals_made: List[Any] = []
        self.round_count = 0
        self.my_price_offers: List[float] = []  # Track price offers for consistency
        self.last_prompt: str = ""  # Store the last prompt sent to LLM
        
        # Validate persona exists
        if not self.persona_manager.configs.persona_exists(persona_name):
            raise ValueError(f"Persona '{persona_name}' not found")
    
    def _initialize_llm_client(self):
        """Initialize the appropriate LLM client based on provider"""
        if self.llm_provider == "openai":
            try:
                from openai import OpenAI
                if not OPENAI_API_KEY:
                    raise ValueError("OPENAI_API_KEY not found in environment")
                return OpenAI(api_key=OPENAI_API_KEY)
            except ImportError:
                raise ImportError("openai package not installed. Run: pip install openai")
        
        elif self.llm_provider == "anthropic":
            try:
                from anthropic import Anthropic
                if not ANTHROPIC_API_KEY:
                    raise ValueError("ANTHROPIC_API_KEY not found in environment")
                return Anthropic(api_key=ANTHROPIC_API_KEY)
            except ImportError:
                raise ImportError("anthropic package not installed. Run: pip install anthropic")
        
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    def generate_message(self, conversation_history: List[Dict] = None) -> str:
        """
        Generate a negotiation message using the LLM
        
        Args:
            conversation_history: List of previous messages (optional, uses internal if not provided)
            
        Returns:
            Generated message string
        """
        # Use provided history or internal history
        history = conversation_history if conversation_history is not None else self.conversation_history
        
        # Build the prompt
        prompt = self.persona_manager.build_agent_prompt(
            persona_name=self.persona_name,
            scenario_public_info=self.scenario_public_info,
            agent_secrets=self.agent_secrets,
            conversation_history=history,
            round_number=len(history) + 1,
            agent_id=self.agent_id,
            my_previous_offers=self.my_price_offers
        )
        
        # Store the prompt for debugging/display
        self.last_prompt = prompt
        
        # Generate message using LLM
        message = self._call_llm(prompt)
        
        # Extract price offer from the message and track it
        price_offer = self._extract_price_from_message(message)
        if price_offer is not None:
            self.my_price_offers.append(price_offer)
        
        # Track the message
        self.round_count += 1
        self.conversation_history.append({
            "agent": self.agent_id,
            "message": message
        })
        
        return message
    
    def _call_llm(self, prompt: str) -> str:
        """
        Call the LLM API to generate a response
        
        Args:
            prompt: Complete prompt string
            
        Returns:
            Generated message
        """
        try:
            if self.llm_provider == "openai":
                response = self.llm_client.chat.completions.create(
                    model=self.llm_model,
                    messages=[
                        {"role": "system", "content": "You are a negotiation agent. Follow the instructions carefully and generate realistic negotiation messages."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=200
                )
                return response.choices[0].message.content.strip()
            
            elif self.llm_provider == "anthropic":
                response = self.llm_client.messages.create(
                    model=self.llm_model,
                    max_tokens=200,
                    temperature=0.7,
                    system="You are a negotiation agent. Follow the instructions carefully and generate realistic negotiation messages.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text.strip()
        
        except Exception as e:
            return f"[Error generating message: {str(e)}]"
    
    def add_message_to_history(self, agent_id: str, message: str):
        """
        Add a message from another agent to conversation history
        
        Args:
            agent_id: ID of the agent who sent the message
            message: Message content
        """
        self.conversation_history.append({
            "agent": agent_id,
            "message": message
        })
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the conversation history
        
        Returns:
            List of message dictionaries
        """
        return self.conversation_history.copy()
    
    def _extract_price_from_message(self, message: str) -> Optional[float]:
        """
        Extract a price value from a message
        
        Args:
            message: The message text
            
        Returns:
            Price as float, or None if no price found
        """
        # Look for price patterns like $700, $1,200, 700, etc.
        patterns = [
            r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $700, $1,200.50
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*dollars?',  # 700 dollars
            r'(?:at|for|offer|price|pay)\s+\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # at $700, for 700
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                # Clean and convert to float
                price_str = matches[0].replace(',', '')
                try:
                    return float(price_str)
                except ValueError:
                    continue
        
        return None
    
    def reset(self):
        """Reset agent state for a new negotiation"""
        self.conversation_history = []
        self.proposals_made = []
        self.round_count = 0
        self.my_price_offers = []
        self.last_prompt = ""
    
    def calculate_utility(self, agreement_terms: Dict) -> float:
        """
        Calculate utility score based on agreement terms
        
        Args:
            agreement_terms: Dictionary containing agreement details
            
        Returns:
            Utility score (0.0 to 1.0)
        """
        # This is a placeholder - will be implemented based on scenario type
        # For price negotiation scenarios, compare agreed price to ideal/minimum
        if "price" in agreement_terms:
            agreed_price = agreement_terms["price"]
            ideal_price = self.agent_secrets.get("ideal_price")
            min_price = self.agent_secrets.get("minimum_acceptable_price")
            max_price = self.agent_secrets.get("maximum_budget")
            
            if ideal_price is not None:
                if min_price is not None and max_price is not None:
                    # Normalize: 1.0 if at ideal, 0.0 if at min/max
                    if ideal_price == min_price:
                        if agreed_price >= ideal_price:
                            return 1.0
                        else:
                            return 0.0
                    else:
                        # Linear interpolation
                        if agreed_price >= ideal_price:
                            return 1.0
                        elif agreed_price <= min_price:
                            return 0.0
                        else:
                            return (agreed_price - min_price) / (ideal_price - min_price)
                else:
                    # Simple comparison to ideal
                    if ideal_price > 0:
                        return max(0.0, min(1.0, agreed_price / ideal_price))
        
        # Default: return 0.5 if we can't calculate
        return 0.5
    
    def get_info(self) -> Dict:
        """
        Get agent information
        
        Returns:
            Dictionary with agent details
        """
        return {
            "agent_id": self.agent_id,
            "persona": self.persona_name,
            "role": self.agent_secrets.get("role", "Unknown"),
            "round_count": self.round_count,
            "messages_sent": len([m for m in self.conversation_history if m["agent"] == self.agent_id])
        }
