"""
Real-time Negotiation Runner
Yields messages as they're generated for real-time display
"""

import re
import uuid
from typing import Dict, Any, Generator, Optional, Tuple
from agents.agent import Agent
from agents.judge import Judge
from utils.scenario_loader import ScenarioLoader
from utils.mongodb_client import get_mongodb_client
from config.config import MAX_ROUNDS


def detect_mutual_agreement(message_a: str, message_b: str) -> Tuple[bool, Optional[float]]:
    """
    Check if both agents are agreeing to the same price
    
    Args:
        message_a: Agent A's message
        message_b: Agent B's message
        
    Returns:
        Tuple of (agreement_reached, agreed_price)
    """
    # Keywords indicating agreement
    agreement_keywords = [
        r"(let'?s|i'?m ready to|i'?m prepared to|willing to|agree to|accept|finalize|seal|close|deal)",
        r"(finalize.*deal|close.*deal|move forward|ready to proceed)"
    ]
    
    # Check if both messages contain agreement language
    has_agreement_a = any(re.search(pattern, message_a.lower()) for pattern in agreement_keywords)
    has_agreement_b = any(re.search(pattern, message_b.lower()) for pattern in agreement_keywords)
    
    if not (has_agreement_a and has_agreement_b):
        return False, None
    
    # Extract prices from both messages
    price_pattern = r'\$?\s*(\d+(?:\.\d{2})?)'
    prices_a = re.findall(price_pattern, message_a)
    prices_b = re.findall(price_pattern, message_b)
    
    if not prices_a or not prices_b:
        return False, None
    
    # Get the last mentioned price from each message
    try:
        price_a = float(prices_a[-1])
        price_b = float(prices_b[-1])
        
        # Check if they agree on the same price (within $1 tolerance)
        if abs(price_a - price_b) <= 1.0:
            agreed_price = (price_a + price_b) / 2
            return True, agreed_price
    except (ValueError, IndexError):
        pass
    
    return False, None


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
    early_agreement = False
    early_agreement_price = None
    
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
        
        # Check for mutual agreement after both agents have spoken
        agreement_detected, agreed_price = detect_mutual_agreement(message_a, message_b)
        if agreement_detected:
            early_agreement = True
            early_agreement_price = agreed_price
            yield {
                "type": "status", 
                "message": f"🎉 Agreement detected! Both agents agreed on ${agreed_price:.2f} in Round {round_num}"
            }
            break
    
    # Always use Judge to analyze the complete negotiation (even if early agreement detected)
    yield {"type": "status", "message": "Analyzing negotiation with Judge..."}
    
    judge = Judge()
    judge_analysis = judge.analyze_negotiation(
        messages=messages,
        scenario_info=agent_a.scenario_public_info,
        agent_a_secrets=agent_a.agent_secrets,
        agent_b_secrets=agent_b.agent_secrets,
        scenario_type=scenario_type
    )
    
    # If early agreement was detected, override the Judge's terms with detected price
    if early_agreement:
        judge_analysis["agreement_reached"] = True
        judge_analysis["agreement_terms"] = {"price": early_agreement_price}
        judge_analysis["early_stop"] = True
        # Keep Judge's winner and satisfaction analysis
    
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
