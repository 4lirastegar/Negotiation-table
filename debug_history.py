"""
Debug script to check conversation history
"""

from agents.agent import Agent
from utils.scenario_loader import ScenarioLoader

def debug_history():
    """Check how history is being stored and passed"""
    scenario_loader = ScenarioLoader()
    scenario_name = "Used Car Sale"
    
    public_info = scenario_loader.get_public_info(scenario_name)
    agent_a_secrets = scenario_loader.get_agent_secrets(scenario_name, "agent_a")
    agent_b_secrets = scenario_loader.get_agent_secrets(scenario_name, "agent_b")
    
    # Create agents
    agent_a = Agent(
        agent_id="Agent A",
        persona_name="Aggressive",
        scenario_public_info=public_info,
        agent_secrets=agent_a_secrets
    )
    
    agent_b = Agent(
        agent_id="Agent B",
        persona_name="Fair",
        scenario_public_info=public_info,
        agent_secrets=agent_b_secrets
    )
    
    print("=" * 70)
    print("DEBUGGING CONVERSATION HISTORY")
    print("=" * 70)
    print()
    
    # Round 1: Agent A
    print("Round 1 - Agent A generating...")
    print(f"Agent A history BEFORE: {len(agent_a.conversation_history)} messages")
    message_a = agent_a.generate_message()
    print(f"Agent A said: {message_a}")
    print(f"Agent A history AFTER: {len(agent_a.conversation_history)} messages")
    print(f"Agent A history content: {agent_a.conversation_history}")
    print()
    
    # Add to Agent B
    print("Adding Agent A's message to Agent B's history...")
    agent_b.add_message_to_history("Agent A", message_a)
    print(f"Agent B history: {len(agent_b.conversation_history)} messages")
    print(f"Agent B history content: {agent_b.conversation_history}")
    print()
    
    # Round 1: Agent B
    print("Round 1 - Agent B generating...")
    print(f"Agent B history BEFORE: {len(agent_b.conversation_history)} messages")
    message_b = agent_b.generate_message()
    print(f"Agent B said: {message_b}")
    print(f"Agent B history AFTER: {len(agent_b.conversation_history)} messages")
    print(f"Agent B history content: {agent_b.conversation_history}")
    print()
    
    # Add to Agent A
    print("Adding Agent B's message to Agent A's history...")
    agent_a.add_message_to_history("Agent B", message_b)
    print(f"Agent A history: {len(agent_a.conversation_history)} messages")
    print(f"Agent A history content: {agent_a.conversation_history}")
    print()
    
    # Round 2: Agent A (should see Agent B's message)
    print("Round 2 - Agent A generating (should see Agent B's message)...")
    print(f"Agent A history BEFORE: {len(agent_a.conversation_history)} messages")
    print("What Agent A sees in history:")
    for msg in agent_a.conversation_history:
        print(f"  - {msg['agent']}: {msg['message'][:50]}...")
    print()
    
    message_a2 = agent_a.generate_message()
    print(f"Agent A said: {message_a2}")
    print()

if __name__ == "__main__":
    debug_history()
