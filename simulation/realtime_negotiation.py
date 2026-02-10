"""
Real-time Negotiation Runner
Yields messages as they're generated for real-time display

JUDGE AS REAL-TIME REFEREE:
- After each round, Judge checks if agreement was reached
- If Judge confirms agreement → stop negotiation
- If no agreement → continue to next round
- Pure LLM-based detection, no hard-coded rules
"""

import uuid
from typing import Dict, Any, Generator
from agents.agent import Agent
from agents.judge import Judge
from utils.scenario_loader import ScenarioLoader
from utils.mongodb_client import get_mongodb_client
from config.config import MAX_ROUNDS


def run_negotiation_realtime(
    agent_a: Agent,
    agent_b: Agent,
    max_rounds: int = None,
    scenario_type: str = "price_negotiation"
) -> Generator[Dict[str, Any], None, Dict[str, Any]]:
    """
    Run a negotiation and yield messages as they're generated
    
    Args:
        agent_a: First agent
        agent_b: Second agent
        max_rounds: Maximum rounds
        scenario_type: Type of scenario
        
    Yields:
        Dictionary with message data for each new message
    Returns:
        Final results dictionary
    """
    max_rounds = max_rounds or MAX_ROUNDS
    
    # Reset agents
    agent_a.reset()
    agent_b.reset()
    
    # Track negotiation
    messages = []
    round_count = 0
    agreement_detected = False
    agreed_price = None
    
    # Initialize Judge for real-time refereeing
    judge = Judge()
    
    # Negotiation loop
    for round_num in range(1, max_rounds + 1):
        round_count = round_num
        
        # Agent A's turn
        try:
            message_a = agent_a.generate_message()
            msg_data = {
                "id": str(uuid.uuid4()),  # Unique message ID
                "round": round_num,
                "agent": "Agent A",
                "persona": agent_a.persona_name,
                "message": message_a,
                "prompt": agent_a.last_prompt,  # Store prompt for debugging
                "type": "message"
            }
            messages.append(msg_data)
            
            # Yield the message for real-time display
            yield msg_data
            
            # Add to Agent B's history
            agent_b.add_message_to_history("Agent A", message_a)
            
        except Exception as e:
            error_msg = {
                "round": round_num,
                "agent": "Agent A",
                "persona": agent_a.persona_name,
                "message": f"[Error: {str(e)}]",
                "type": "error"
            }
            messages.append(error_msg)
            yield error_msg
            break
        
        # Agent B's turn
        try:
            message_b = agent_b.generate_message()
            msg_data = {
                "id": str(uuid.uuid4()),  # Unique message ID
                "round": round_num,
                "agent": "Agent B",
                "persona": agent_b.persona_name,
                "message": message_b,
                "prompt": agent_b.last_prompt,  # Store prompt for debugging
                "type": "message"
            }
            messages.append(msg_data)
            
            # Yield the message for real-time display
            yield msg_data
            
            # Add to Agent A's history
            agent_a.add_message_to_history("Agent B", message_b)
            
        except Exception as e:
            error_msg = {
                "round": round_num,
                "agent": "Agent B",
                "persona": agent_b.persona_name,
                "message": f"[Error: {str(e)}]",
                "type": "error"
            }
            messages.append(error_msg)
            yield error_msg
            break
        
        # Ask Judge: Did they reach agreement this round?
        yield {"type": "status", "message": "⚖️ Judge checking for agreement..."}
        
        quick_check = judge.check_agreement_quick(
            message_a=message_a,
            message_b=message_b,
            round_num=round_num
        )
        
        if quick_check.get("agreement_reached"):
            agreement_detected = True
            agreed_price = quick_check.get("agreed_price")
            yield {
                "type": "status",
                "message": f"✅ Judge: Agreement reached at ${agreed_price:.2f} in Round {round_num}! {quick_check.get('explanation', '')}"
            }
            break
        else:
            yield {
                "type": "status",
                "message": f"↔️ Judge: No agreement yet. {quick_check.get('explanation', 'Negotiation continues...')}"
            }
    
    # Use Judge to analyze the complete negotiation for winner/satisfaction
    yield {"type": "status", "message": "📊 Judge analyzing full negotiation..."}
    
    judge_analysis = judge.analyze_negotiation(
        messages=messages,
        scenario_info=agent_a.scenario_public_info,
        agent_a_secrets=agent_a.agent_secrets,
        agent_b_secrets=agent_b.agent_secrets,
        scenario_type=scenario_type
    )
    
    # If agreement was detected during rounds, use that info
    if agreement_detected:
        judge_analysis["agreement_reached"] = True
        judge_analysis["agreement_terms"] = {"price": agreed_price}
        judge_analysis["stopped_early"] = True
    
    # Extract results from Judge analysis
    agreement_reached = judge_analysis.get("agreement_reached", False)
    agreement_terms = judge_analysis.get("agreement_terms")
    
    # Calculate utilities if agreement reached
    utility_a = None
    utility_b = None
    if agreement_reached and agreement_terms:
        utility_a = agent_a.calculate_utility(agreement_terms)
        utility_b = agent_b.calculate_utility(agreement_terms)
    
    # Build final results
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
        "scenario_type": scenario_type,
        "judge_analysis": judge_analysis,
        "type": "complete"
    }
    
    # Save to MongoDB
    try:
        yield {"type": "status", "message": "Saving to MongoDB..."}
        mongo_client = get_mongodb_client()
        negotiation_id = mongo_client.save_negotiation(
            scenario_name=agent_a.scenario_public_info.get("name", "Unknown"),
            agent_a_persona=agent_a.persona_name,
            agent_b_persona=agent_b.persona_name,
            results=results
        )
        results["negotiation_id"] = negotiation_id
        yield {"type": "status", "message": f"✅ Saved to MongoDB (ID: {negotiation_id})"}
    except Exception as e:
        yield {"type": "status", "message": f"⚠️ Failed to save to MongoDB: {str(e)}"}
        print(f"Warning: Could not save to MongoDB: {e}")
    
    yield results
    return results


def run_single_negotiation(
    scenario_name: str,
    agent_a_persona: str,
    agent_b_persona: str,
    max_rounds: int = None
) -> Dict[str, Any]:
    """
    Run a single negotiation synchronously (for batch testing)
    
    This is a non-generator version that runs the full negotiation
    and returns the complete results.
    
    Args:
        scenario_name: Name of the scenario to use
        agent_a_persona: Persona for Agent A
        agent_b_persona: Persona for Agent B
        max_rounds: Maximum number of rounds (default from config)
        
    Returns:
        Dictionary with complete negotiation results
    """
    if max_rounds is None:
        max_rounds = MAX_ROUNDS
    
    # Load scenario
    scenario_loader = ScenarioLoader()
    scenario = scenario_loader.get_scenario(scenario_name)
    
    if not scenario:
        raise ValueError(f"Scenario '{scenario_name}' not found")
    
    # Get public info and agent secrets
    public_info = scenario_loader.get_public_info(scenario_name)
    agent_a_secrets = scenario_loader.get_agent_secrets(scenario_name, "agent_a")
    agent_b_secrets = scenario_loader.get_agent_secrets(scenario_name, "agent_b")
    
    # Create agents
    agent_a = Agent(
        agent_id="Agent A",
        persona_name=agent_a_persona,
        scenario_public_info=public_info,
        agent_secrets=agent_a_secrets
    )
    
    agent_b = Agent(
        agent_id="Agent B",
        persona_name=agent_b_persona,
        scenario_public_info=public_info,
        agent_secrets=agent_b_secrets
    )
    
    # Run negotiation using the generator, but consume all messages
    generator = run_negotiation_realtime(
        agent_a=agent_a,
        agent_b=agent_b,
        max_rounds=max_rounds,
        scenario_type=scenario.get("type", "price_negotiation")
    )
    
    # Consume all generator messages and get final result
    results = None
    for message in generator:
        if message.get("type") == "complete":
            results = message
            break
    
    # Add total_rounds to match expected format
    if results:
        results["total_rounds"] = results.get("rounds", 0)
    
    return results
