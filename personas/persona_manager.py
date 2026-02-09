

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
        
        # Build the prompt sections - MINIMAL GOAL-ORIENTED APPROACH
        prompt_parts = []
        
        role = agent_secrets.get("role", "Unknown")
        
        # 1. Role and Goal (Clear but not prescriptive)
        prompt_parts.append("=" * 60)
        prompt_parts.append(f"YOUR ROLE: {role.upper()}")
        prompt_parts.append("=" * 60)
        
        if role == "Seller":
            prompt_parts.append("You are selling the item described below.")
            prompt_parts.append("Your goal: Sell for the HIGHEST price possible within your acceptable range.")
        elif role == "Buyer":
            prompt_parts.append("You are buying the item described below.")
            prompt_parts.append("Your goal: Buy for the LOWEST price possible within your acceptable range.")
        else:
            prompt_parts.append(f"You are the {role}.")
        prompt_parts.append("")
        
        # 2. Personality (minimal)
        if persona.get("prompt_addition"):
            prompt_parts.append(persona.get("prompt_addition"))
            prompt_parts.append("")
        
        # 3. Negotiation Context
        prompt_parts.append("=" * 60)
        prompt_parts.append("NEGOTIATION CONTEXT:")
        prompt_parts.append("=" * 60)
        prompt_parts.append(self._format_public_info(scenario_public_info))
        prompt_parts.append("")
        
        # 4. Your Constraints (private info)
        prompt_parts.append("=" * 60)
        prompt_parts.append("YOUR CONSTRAINTS:")
        prompt_parts.append("=" * 60)
        prompt_parts.append(self._format_agent_secrets(agent_secrets))
        prompt_parts.append("")
        prompt_parts.append("Note: Use this information strategically. You may choose whether to reveal it.")
        prompt_parts.append("")
        
        # 5. Conversation history
        if conversation_history:
            prompt_parts.append("=" * 60)
            prompt_parts.append(f"CONVERSATION HISTORY (Round {round_number}):")
            prompt_parts.append("=" * 60)
            prompt_parts.append(self._format_conversation_history(conversation_history, current_agent_id=agent_id))
        
        # 6. Task (simple and clear)
        prompt_parts.append("=" * 60)
        prompt_parts.append("YOUR TASK:")
        prompt_parts.append("=" * 60)
        if conversation_history:
            prompt_parts.append("Read the conversation above and respond to the other party's latest message.")
            prompt_parts.append("Continue negotiating toward an agreement that maximizes your outcome.")
        else:
            prompt_parts.append("Begin the negotiation. Make your opening statement.")
        prompt_parts.append("")
        prompt_parts.append("Your response (do not include labels like 'Agent A:' or 'Seller:'):")
        
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
