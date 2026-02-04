"""
Negotiation Engine
Main loop that runs negotiations between agents
"""

from typing import Dict, List, Optional, Tuple, Any
from agents.agent import Agent
from agents.judge import Judge
from utils.scenario_loader import ScenarioLoader
from utils.mongodb_client import get_mongodb_client
from config.config import MAX_ROUNDS


class NegotiationEngine:
    """Manages negotiation simulations between agents"""
    
    def __init__(self, max_rounds: int = None):
        """
        Initialize the negotiation engine
        
        Args:
            max_rounds: Maximum number of rounds (default from config)
        """
        self.max_rounds = max_rounds or MAX_ROUNDS
        self.scenario_loader = ScenarioLoader()
    
    def create_agents(
        self,
        scenario_name: str,
        agent_a_persona: str,
        agent_b_persona: str,
        llm_provider: str = None,
        llm_model: str = None
    ) -> Tuple[Agent, Agent]:
        """
        Create two agents for negotiation
        
        Args:
            scenario_name: Name of the scenario
            agent_a_persona: Persona for Agent A
            agent_b_persona: Persona for Agent B
            llm_provider: LLM provider override
            llm_model: LLM model override
            
        Returns:
            Tuple of (Agent A, Agent B)
        """
        # Load scenario data
        public_info = self.scenario_loader.get_public_info(scenario_name)
        agent_a_secrets = self.scenario_loader.get_agent_secrets(scenario_name, "agent_a")
        agent_b_secrets = self.scenario_loader.get_agent_secrets(scenario_name, "agent_b")
        
        # Create agents
        agent_a = Agent(
            agent_id="Agent A",
            persona_name=agent_a_persona,
            scenario_public_info=public_info,
            agent_secrets=agent_a_secrets,
            llm_provider=llm_provider,
            llm_model=llm_model
        )
        
        agent_b = Agent(
            agent_id="Agent B",
            persona_name=agent_b_persona,
            scenario_public_info=public_info,
            agent_secrets=agent_b_secrets,
            llm_provider=llm_provider,
            llm_model=llm_model
        )
        
        return agent_a, agent_b
    
    def run_negotiation(
        self,
        agent_a: Agent,
        agent_b: Agent,
        max_rounds: int = None,
        scenario_type: str = "price_negotiation"
    ) -> Dict[str, Any]:
        """
        Run a negotiation between two agents
        
        Args:
            agent_a: First agent
            agent_b: Second agent
            max_rounds: Maximum rounds (overrides default)
            
        Returns:
            Dictionary with negotiation results
        """
        max_rounds = max_rounds or self.max_rounds
        
        # Reset agents
        agent_a.reset()
        agent_b.reset()
        
        # Track negotiation
        messages = []
        round_count = 0
        
        # Negotiation loop - run to completion (let Judge determine outcome)
        for round_num in range(1, max_rounds + 1):
            round_count = round_num
            
            # Agent A's turn
            try:
                message_a = agent_a.generate_message()
                messages.append({
                    "round": round_num,
                    "agent": "Agent A",
                    "persona": agent_a.persona_name,
                    "message": message_a
                })
                
                # Add to Agent B's history
                agent_b.add_message_to_history("Agent A", message_a)
                
            except Exception as e:
                messages.append({
                    "round": round_num,
                    "agent": "Agent A",
                    "persona": agent_a.persona_name,
                    "message": f"[Error: {str(e)}]"
                })
                break
            
            # Agent B's turn
            try:
                message_b = agent_b.generate_message()
                messages.append({
                    "round": round_num,
                    "agent": "Agent B",
                    "persona": agent_b.persona_name,
                    "message": message_b
                })
                
                # Add to Agent A's history
                agent_a.add_message_to_history("Agent B", message_b)
                
            except Exception as e:
                messages.append({
                    "round": round_num,
                    "agent": "Agent B",
                    "persona": agent_b.persona_name,
                    "message": f"[Error: {str(e)}]"
                })
                break
        
        # Now use Judge to analyze the complete negotiation
        judge = Judge()
        judge_analysis = judge.analyze_negotiation(
            messages=messages,
            scenario_info=agent_a.scenario_public_info,
            agent_a_secrets=agent_a.agent_secrets,
            agent_b_secrets=agent_b.agent_secrets,
            scenario_type=scenario_type
        )
        
        # Extract results from Judge analysis
        agreement_reached = judge_analysis.get("agreement_reached", False)
        agreement_terms = judge_analysis.get("agreement_terms")
        
        # Calculate utilities if agreement reached
        utility_a = None
        utility_b = None
        if agreement_reached and agreement_terms:
            utility_a = agent_a.calculate_utility(agreement_terms)
            utility_b = agent_b.calculate_utility(agreement_terms)
        
        # Build results
        results = {
            "agreement_reached": agreement_reached,
            "rounds": round_count,
            "max_rounds": max_rounds,
            "messages": messages,
            "agreement_terms": agreement_terms,
            "utility_a": utility_a,
            "utility_b": utility_b,
            "agent_a_info": agent_a.get_info(),
            "agent_b_info": agent_b.get_info(),
            "scenario": agent_a.scenario_public_info.get("item", "Unknown"),
            "judge_analysis": judge_analysis  # Include full Judge analysis
        }
        
        return results
    
    def simulate(
        self,
        scenario_name: str,
        agent_a_persona: str,
        agent_b_persona: str,
        max_rounds: int = None,
        llm_provider: str = None,
        llm_model: str = None,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Complete simulation: create agents and run negotiation
        
        Args:
            scenario_name: Name of the scenario
            agent_a_persona: Persona for Agent A
            agent_b_persona: Persona for Agent B
            max_rounds: Maximum rounds
            llm_provider: LLM provider override
            llm_model: LLM model override
            save_to_db: Whether to save results to MongoDB
            
        Returns:
            Negotiation results dictionary
        """
        # Create agents
        agent_a, agent_b = self.create_agents(
            scenario_name=scenario_name,
            agent_a_persona=agent_a_persona,
            agent_b_persona=agent_b_persona,
            llm_provider=llm_provider,
            llm_model=llm_model
        )
        
        # Store scenario name for Judge
        scenario = self.scenario_loader.get_scenario(scenario_name)
        scenario_type = scenario.get("type", "price_negotiation") if scenario else "price_negotiation"
        
        # Run negotiation with scenario type
        results = self.run_negotiation(agent_a, agent_b, max_rounds, scenario_type)
        
        # Add scenario info to results
        results["scenario_name"] = scenario_name
        results["scenario_type"] = scenario_type
        results["agent_a_persona"] = agent_a_persona
        results["agent_b_persona"] = agent_b_persona
        
        # Save to MongoDB if requested
        if save_to_db:
            try:
                mongodb = get_mongodb_client()
                doc_id = mongodb.save_negotiation(
                    scenario_name=scenario_name,
                    agent_a_persona=agent_a_persona,
                    agent_b_persona=agent_b_persona,
                    results=results
                )
                results["_id"] = doc_id
            except Exception as e:
                print(f"Warning: Could not save to MongoDB: {e}")
                # Don't fail the simulation if MongoDB save fails
        
        return results
