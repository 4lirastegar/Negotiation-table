"""
Persona Manager
Manages persona integration with agent prompts
"""

from typing import Dict, List, Optional
from .persona_configs import PersonaConfigs


class PersonaManager:
    """Manages persona application to agent prompts"""
    
    def __init__(self):
        """Initialize the persona manager"""
        self.configs = PersonaConfigs()
    
    def get_persona(self, persona_name: str) -> Dict:
        """
        Get a persona configuration
        
        Args:
            persona_name: Name of the persona
            
        Returns:
            Persona dictionary
        """
        return self.configs.get_persona(persona_name)
    
    def list_personas(self) -> List[str]:
        """
        Get list of all available personas
        
        Returns:
            List of persona names
        """
        return self.configs.list_personas()
    
    def build_agent_prompt(
        self,
        persona_name: str,
        scenario_public_info: Dict,
        agent_secrets: Dict,
        conversation_history: List[Dict] = None,
        round_number: int = 1,
        agent_id: str = None,
        my_previous_offers: List[float] = None
    ) -> str:
        """
        Build a complete prompt for an agent with persona, scenario, and history
        
        Args:
            persona_name: Name of the persona to use
            scenario_public_info: Public information from scenario
            agent_secrets: Agent's private information
            conversation_history: List of previous messages (optional)
            round_number: Current round number
            
        Returns:
            Complete prompt string for the LLM
        """
        persona = self.get_persona(persona_name)
        if not persona:
            raise ValueError(f"Persona '{persona_name}' not found")
        
        # Build the prompt sections
        prompt_parts = []
        
        # 0. YOUR ROLE (most important - put first!)
        role = agent_secrets.get("role", "Unknown")
        prompt_parts.append("=" * 60)
        prompt_parts.append("⚠️ CRITICAL: YOUR ROLE ⚠️")
        prompt_parts.append("=" * 60)
        if role == "Seller":
            prompt_parts.append("YOU ARE THE SELLER.")
            prompt_parts.append("")
            prompt_parts.append("IMPORTANT RULES:")
            prompt_parts.append("- You want to SELL the item for the HIGHEST price possible")
            prompt_parts.append("- You START with a HIGH asking price (your ideal price)")
            prompt_parts.append("- You negotiate DOWNWARD only if the buyer won't accept your price")
            prompt_parts.append("- NEVER offer a price LOWER than what the buyer is offering")
            prompt_parts.append("- If buyer offers $650, you should counter with $700 or higher, NOT lower")
            prompt_parts.append("")
            prompt_parts.append("EXAMPLE: If buyer offers $650, you say: 'I can do $700' or 'How about $680'")
            prompt_parts.append("WRONG: If buyer offers $650, you say: 'I can do $500' (this is backwards!)")
        elif role == "Buyer":
            prompt_parts.append("YOU ARE THE BUYER.")
            prompt_parts.append("")
            prompt_parts.append("IMPORTANT RULES:")
            prompt_parts.append("- You want to BUY the item for the LOWEST price possible")
            prompt_parts.append("- You START with a LOW offer (below your ideal price)")
            prompt_parts.append("- You negotiate UPWARD only if the seller won't accept your price")
            prompt_parts.append("- NEVER offer a price HIGHER than what the seller is offering")
            prompt_parts.append("- If seller offers $700, you should counter with $600 or lower, NOT higher")
            prompt_parts.append("")
            prompt_parts.append("EXAMPLE: If seller offers $700, you say: 'I can do $600' or 'How about $650'")
            prompt_parts.append("WRONG: If seller offers $700, you say: 'I can do $800' (this is backwards!)")
        else:
            prompt_parts.append(f"You are the {role}.")
        prompt_parts.append("")
        prompt_parts.append("=" * 60)
        prompt_parts.append("")
        
        # 1. Persona instructions
        prompt_parts.append("=" * 60)
        prompt_parts.append("YOUR PERSONALITY AND NEGOTIATION STYLE:")
        prompt_parts.append("=" * 60)
        prompt_parts.append(persona.get("prompt_addition", ""))
        prompt_parts.append("")
        
        # 2. Scenario context
        prompt_parts.append("=" * 60)
        prompt_parts.append("NEGOTIATION SCENARIO:")
        prompt_parts.append("=" * 60)
        prompt_parts.append(self._format_public_info(scenario_public_info))
        prompt_parts.append("")
        
        # 3. Your private information
        prompt_parts.append("=" * 60)
        prompt_parts.append("YOUR PRIVATE INFORMATION (DO NOT REVEAL DIRECTLY):")
        prompt_parts.append("=" * 60)
        prompt_parts.append(self._format_agent_secrets(agent_secrets))
        prompt_parts.append("")
        prompt_parts.append("IMPORTANT: Use this information to guide your negotiation, but don't reveal it directly unless strategically beneficial.")
        prompt_parts.append("")
        
        # 4. YOUR PREVIOUS OFFERS (Track consistency!)
        if my_previous_offers and len(my_previous_offers) > 0:
            prompt_parts.append("=" * 60)
            prompt_parts.append("⚠️ YOUR PREVIOUS PRICE OFFERS ⚠️")
            prompt_parts.append("=" * 60)
            prompt_parts.append("You have made the following price offers in this negotiation:")
            for i, offer in enumerate(my_previous_offers, 1):
                prompt_parts.append(f"  Round {i}: ${offer:.2f}")
            prompt_parts.append("")
            prompt_parts.append("🚨 CRITICAL CONSISTENCY RULE 🚨")
            if role == "Seller":
                if my_previous_offers:
                    lowest_offer = min(my_previous_offers)
                    prompt_parts.append(f"You are the SELLER. Your lowest offer so far is ${lowest_offer:.2f}")
                    prompt_parts.append(f"You MUST NOT offer a price LOWER than ${lowest_offer:.2f}")
                    prompt_parts.append(f"You can only offer ${lowest_offer:.2f} or HIGHER")
                    prompt_parts.append(f"If you want to make a concession, offer between ${lowest_offer:.2f} and ${max(my_previous_offers):.2f}")
            elif role == "Buyer":
                if my_previous_offers:
                    highest_offer = max(my_previous_offers)
                    prompt_parts.append(f"You are the BUYER. Your highest offer so far is ${highest_offer:.2f}")
                    prompt_parts.append(f"You MUST NOT offer a price HIGHER than ${highest_offer:.2f}")
                    prompt_parts.append(f"You can only offer ${highest_offer:.2f} or LOWER")
                    prompt_parts.append(f"If you want to make a concession, offer between ${min(my_previous_offers):.2f} and ${highest_offer:.2f}")
            prompt_parts.append("")
            prompt_parts.append("=" * 60)
            prompt_parts.append("")
        
        # 5. Conversation history
        if conversation_history:
            prompt_parts.append("=" * 60)
            prompt_parts.append("⚠️ CONVERSATION HISTORY - READ THIS CAREFULLY ⚠️")
            prompt_parts.append("=" * 60)
            prompt_parts.append("The other party has been negotiating with you. You MUST respond to what they just said.")
            prompt_parts.append("Do NOT just repeat your own position - actually negotiate!")
            prompt_parts.append("")
            prompt_parts.append(self._format_conversation_history(conversation_history, current_agent_id=agent_id))
            prompt_parts.append("")
            prompt_parts.append("⚠️ IMPORTANT: Look at what the other party just said in the last message above.")
            prompt_parts.append("You MUST respond to their specific offer/statement, not just repeat your position.")
            prompt_parts.append("")
        
        # 6. Current instructions
        prompt_parts.append("=" * 60)
        prompt_parts.append("YOUR TASK:")
        prompt_parts.append("=" * 60)
        prompt_parts.append(f"This is round {round_number} of the negotiation.")
        prompt_parts.append("")
        if role == "Seller":
            prompt_parts.append("⚠️ REMINDER: You are the SELLER. You want HIGHER prices. If the buyer offers $650, you counter with $700 or higher, NOT lower!")
        elif role == "Buyer":
            prompt_parts.append("⚠️ REMINDER: You are the BUYER. You want LOWER prices. If the seller offers $700, you counter with $600 or lower, NOT higher!")
        prompt_parts.append("")
        if conversation_history:
            prompt_parts.append("⚠️ CRITICAL: The other party just made a statement/offer in the conversation above.")
            prompt_parts.append("You MUST:")
            prompt_parts.append("1. Acknowledge what they just said")
            prompt_parts.append("2. Respond to their specific offer/statement")
            prompt_parts.append("3. Make a NEW counter-offer (not just repeat your old position)")
            prompt_parts.append("4. Show you're actually negotiating (move your price, make a compromise)")
            prompt_parts.append("")
            prompt_parts.append("DO NOT just say 'I appreciate your offer but I'm sticking to $700' - that's not negotiating!")
            prompt_parts.append("Instead, say something like 'I appreciate your offer of $600. How about we meet at $650?'")
            prompt_parts.append("")
        prompt_parts.append("Generate your next message in the negotiation.")
        prompt_parts.append("Be true to your personality and negotiation style.")
        prompt_parts.append("Keep your message concise (1-3 sentences typically).")
        prompt_parts.append("Do NOT include 'Agent A:' or 'Agent B:' in your message - just write what you would say.")
        prompt_parts.append("")
        prompt_parts.append("Your message:")
        
        return "\n".join(prompt_parts)
    
    def _format_public_info(self, public_info: Dict) -> str:
        """Format public information for the prompt"""
        lines = []
        for key, value in public_info.items():
            if isinstance(value, list):
                lines.append(f"{key.replace('_', ' ').title()}:")
                for item in value:
                    if isinstance(item, dict):
                        item_str = ", ".join([f"{k}: {v}" for k, v in item.items()])
                        lines.append(f"  - {item_str}")
                    else:
                        lines.append(f"  - {item}")
            elif isinstance(value, dict):
                lines.append(f"{key.replace('_', ' ').title()}:")
                for k, v in value.items():
                    lines.append(f"  {k}: {v}")
            else:
                lines.append(f"{key.replace('_', ' ').title()}: {value}")
        return "\n".join(lines)
    
    def _format_agent_secrets(self, secrets: Dict) -> str:
        """Format agent secrets for the prompt"""
        lines = []
        for key, value in secrets.items():
            if key == "strategy":
                lines.append(f"\nStrategy: {value}")
            elif isinstance(value, dict):
                lines.append(f"\n{key.replace('_', ' ').title()}:")
                for k, v in value.items():
                    lines.append(f"  {k}: {v}")
            else:
                lines.append(f"{key.replace('_', ' ').title()}: {value}")
        return "\n".join(lines)
    
    def _format_conversation_history(self, history: List[Dict], current_agent_id: str = None) -> str:
        """Format conversation history for the prompt"""
        lines = []
        for i, message in enumerate(history, 1):
            agent = message.get("agent", "Unknown")
            text = message.get("message", "")
            
            # Make it clear who said what
            if current_agent_id and agent == current_agent_id:
                lines.append(f"Round {i}:")
                lines.append(f"  You said: {text}")
            else:
                lines.append(f"Round {i}:")
                lines.append(f"  The other party said: {text}")
            lines.append("")
        return "\n".join(lines)
    
    def get_persona_traits(self, persona_name: str) -> List[str]:
        """
        Get traits for a persona
        
        Args:
            persona_name: Name of the persona
            
        Returns:
            List of trait strings
        """
        persona = self.get_persona(persona_name)
        return persona.get("traits", [])
    
    def get_persona_description(self, persona_name: str) -> str:
        """
        Get description for a persona
        
        Args:
            persona_name: Name of the persona
            
        Returns:
            Description string
        """
        persona = self.get_persona(persona_name)
        return persona.get("description", "")
