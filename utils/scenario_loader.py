"""
Scenario Loader
Loads and validates scenario JSON files
"""

import json
import os
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path


class ScenarioLoader:
    """Loads and manages negotiation scenarios"""
    
    def __init__(self, scenarios_dir: str = "scenarios"):
        """
        Initialize the scenario loader
        
        Args:
            scenarios_dir: Directory containing scenario JSON files
        """
        self.scenarios_dir = Path(scenarios_dir)
        self.scenarios = {}
        self._load_all_scenarios()
    
    def _load_all_scenarios(self):
        """Load all scenario files from the scenarios directory"""
        if not self.scenarios_dir.exists():
            raise FileNotFoundError(f"Scenarios directory not found: {self.scenarios_dir}")
        
        for json_file in self.scenarios_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    scenario_data = json.load(f)
                    scenario_name = scenario_data.get('name', json_file.stem)
                    self.scenarios[scenario_name] = scenario_data
            except json.JSONDecodeError as e:
                print(f"Error loading {json_file}: Invalid JSON - {e}")
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
    
    def get_scenario(self, scenario_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a scenario by name
        
        Args:
            scenario_name: Name of the scenario
            
        Returns:
            Scenario dictionary or None if not found
        """
        return self.scenarios.get(scenario_name)
    
    def list_scenarios(self) -> list:
        """
        Get list of all available scenario names
        
        Returns:
            List of scenario names
        """
        return list(self.scenarios.keys())
    
    def get_public_info(self, scenario_name: str) -> Dict[str, Any]:
        """
        Get public information for a scenario (visible to both agents)
        
        Args:
            scenario_name: Name of the scenario
            
        Returns:
            Public information dictionary
        """
        scenario = self.get_scenario(scenario_name)
        if scenario:
            return scenario.get('public_info', {})
        return {}
    
    def get_agent_secrets(self, scenario_name: str, agent: str) -> Dict[str, Any]:
        """
        Get private information for a specific agent
        
        Args:
            scenario_name: Name of the scenario
            agent: 'agent_a' or 'agent_b'
            
        Returns:
            Agent's private information dictionary
        """
        scenario = self.get_scenario(scenario_name)
        if scenario:
            key = f"{agent}_secrets" if not agent.endswith('_secrets') else agent
            return scenario.get(key, {})
        return {}
    
    def get_market_value(self, scenario_name: str) -> Dict[str, Any]:
        """
        Get market value/truth data for a scenario
        
        Args:
            scenario_name: Name of the scenario
            
        Returns:
            Market value dictionary
        """
        scenario = self.get_scenario(scenario_name)
        if scenario:
            return scenario.get('market_value', {})
        return {}
    
    def validate_scenario(self, scenario_name: str) -> Tuple[bool, List[str]]:
        """
        Validate that a scenario has all required fields
        
        Args:
            scenario_name: Name of the scenario
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        scenario = self.get_scenario(scenario_name)
        if not scenario:
            return False, [f"Scenario '{scenario_name}' not found"]
        
        required_fields = [
            'name',
            'description',
            'public_info',
            'agent_a_secrets',
            'agent_b_secrets',
            'market_value',
            'agreement_criteria'
        ]
        
        errors = []
        for field in required_fields:
            if field not in scenario:
                errors.append(f"Missing required field: {field}")
        
        return len(errors) == 0, errors
