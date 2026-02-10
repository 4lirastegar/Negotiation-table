"""
Persona Configurations
Defines different personality types for negotiation agents
"""

from typing import Dict, List


class PersonaConfigs:
    """Static class containing all persona definitions"""
    
    PERSONAS: Dict[str, Dict] = {
        "None": {
            "prompt_addition": ""  # No persona - pure emergent behavior
        },
        
        "Aggressive": {
            "prompt_addition": "You are an aggressive negotiator."
        },
        
        "Fair": {
            "prompt_addition": "You are a fair negotiator."
        },
        
        "Liar": {
            "prompt_addition": "You are a deceptive negotiator."
        },
        
        "Logical": {
            "prompt_addition": "You are a logical negotiator."
        },
        
        "Cooperative": {
            "prompt_addition": "You are a cooperative negotiator."
        },
        
        "Stubborn": {
            "prompt_addition": "You are a stubborn negotiator."
        },
        
        "Desperate": {
            "prompt_addition": "You are a desperate negotiator."
        },
        
        "Strategic": {
            "prompt_addition": "You are a strategic negotiator."
        }
    }
    
    @classmethod
    def get_persona(cls, persona_name: str) -> Dict:
        """
        Get a persona configuration by name
        
        Args:
            persona_name: Name of the persona
            
        Returns:
            Persona dictionary or empty dict if not found
        """
        return cls.PERSONAS.get(persona_name, {})
    
    @classmethod
    def list_personas(cls) -> List[str]:
        """
        Get list of all available persona names
        
        Returns:
            List of persona names
        """
        return list(cls.PERSONAS.keys())
    
    @classmethod
    def get_persona_prompt(cls, persona_name: str) -> str:
        """
        Get the prompt addition for a persona
        
        Args:
            persona_name: Name of the persona
            
        Returns:
            Prompt addition string
        """
        persona = cls.get_persona(persona_name)
        return persona.get("prompt_addition", "")
    
    @classmethod
    def persona_exists(cls, persona_name: str) -> bool:
        """
        Check if a persona exists
        
        Args:
            persona_name: Name of the persona
            
        Returns:
            True if persona exists, False otherwise
        """
        return persona_name in cls.PERSONAS
