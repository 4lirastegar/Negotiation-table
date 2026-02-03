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
        round_number: int = 1
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
        prompt_parts.append("YOUR ROLE:")
        prompt_parts.append("=" * 60)
        if role == "Seller":
            prompt_parts.append("You are the SELLER. You want to get the HIGHEST price possible.")
            prompt_parts.append("You start with a higher asking price and negotiate downward only if necessary.")
        elif role == "Buyer":
            prompt_parts.append("You are the BUYER. You want to get the LOWEST price possible.")
            prompt_parts.append("You start with a lower offer and negotiate upward only if necessary.")
        else:
            prompt_parts.append(f"You are the {role}.")
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
        
        # 4. Conversation history
        if conversation_history:
            prompt_parts.append("=" * 60)
            prompt_parts.append("CONVERSATION HISTORY:")
            prompt_parts.append("=" * 60)
            prompt_parts.append(self._format_conversation_history(conversation_history))
            prompt_parts.append("")
        
        # 5. Current instructions
        prompt_parts.append("=" * 60)
        prompt_parts.append("YOUR TASK:")
        prompt_parts.append("=" * 60)
        prompt_parts.append(f"This is round {round_number} of the negotiation.")
        prompt_parts.append(f"Remember: You are the {role}. Act accordingly.")
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
    
    def _format_conversation_history(self, history: List[Dict]) -> str:
        """Format conversation history for the prompt"""
        lines = []
        for i, message in enumerate(history, 1):
            agent = message.get("agent", "Unknown")
            text = message.get("message", "")
            lines.append(f"Round {i}:")
            lines.append(f"  {agent}: {text}")
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
