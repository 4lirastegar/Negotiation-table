"""
Show what prompts are actually being sent to the LLM
"""

from agents.agent import Agent
from utils.scenario_loader import ScenarioLoader

def show_prompts():
    """Show the actual prompts being sent"""
    print("=" * 80)
    print("SHOWING ACTUAL PROMPTS SENT TO LLM")
    print("=" * 80)
    print()
    
    # Load scenario
    scenario_loader = ScenarioLoader()
    scenario_name = "Used Car Sale"
    
    public_info = scenario_loader.get_public_info(scenario_name)
    agent_a_secrets = scenario_loader.get_agent_secrets(scenario_name, "agent_a")
    agent_b_secrets = scenario_loader.get_agent_secrets(scenario_name, "agent_b")
    
    # Create Agent A
    agent_a = Agent(
        agent_id="Agent A",
        persona_name="Aggressive",
        scenario_public_info=public_info,
        agent_secrets=agent_a_secrets
    )
    
    print("=" * 80)
    print("AGENT A - ROUND 1 PROMPT:")
    print("=" * 80)
    
    # Build prompt for round 1 (no history yet)
    prompt = agent_a.persona_manager.build_agent_prompt(
        persona_name="Aggressive",
        scenario_public_info=public_info,
        agent_secrets=agent_a_secrets,
        conversation_history=None,
        round_number=1
    )
    
    print(prompt)
    print()
    print("=" * 80)
    print()
    
    # Now show what happens after a few messages
    print("=" * 80)
    print("AGENT A - ROUND 3 PROMPT (with conversation history):")
    print("=" * 80)
    
    # Simulate some conversation
    history = [
        {"agent": "Agent A", "message": "I'm asking $700 for the car."},
        {"agent": "Agent B", "message": "I can offer $650."},
        {"agent": "Agent A", "message": "How about $680?"},
        {"agent": "Agent B", "message": "I can do $660."}
    ]
    
    prompt_with_history = agent_a.persona_manager.build_agent_prompt(
        persona_name="Aggressive",
        scenario_public_info=public_info,
        agent_secrets=agent_a_secrets,
        conversation_history=history,
        round_number=3
    )
    
    print(prompt_with_history)
    print()
    print("=" * 80)
    print()
    
    print("HOW IT WORKS:")
    print("1. Each agent gets a FULL prompt with:")
    print("   - Their role (Seller/Buyer)")
    print("   - Their persona (Aggressive/Fair/etc.)")
    print("   - Scenario info")
    print("   - Their private secrets")
    print("   - Conversation history (all previous messages)")
    print("   - Instructions to generate next message")
    print()
    print("2. The LLM (gpt-4o-mini) receives this prompt and generates ONE message")
    print()
    print("3. That message is added to history, and the OTHER agent gets the same")
    print("   prompt structure but with updated history")
    print()
    print("4. They don't 'see' each other's prompts - they only see the conversation")
    print("   history (the messages that were exchanged)")
    print()
    print("PROBLEM: The agents might be confused because:")
    print("- They see 'Agent A' and 'Agent B' in history but don't know which is them")
    print("- The conversation history format might be unclear")
    print("- They might lose track of who said what")

if __name__ == "__main__":
    show_prompts()
