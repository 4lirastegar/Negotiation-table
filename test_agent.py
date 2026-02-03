"""
Quick test script to verify agent system works
Note: This requires API keys to be set in .env file
"""

import os
from agents.agent import Agent
from utils.scenario_loader import ScenarioLoader

def test_agent_creation():
    """Test agent creation and basic functionality"""
    print("Testing Agent System...\n")
    
    # Check if API keys are set
    from config.config import OPENAI_API_KEY, ANTHROPIC_API_KEY, LLM_PROVIDER
    
    if LLM_PROVIDER == "openai" and not OPENAI_API_KEY:
        print("⚠️  Warning: OPENAI_API_KEY not set. Skipping LLM tests.")
        print("   Set your API key in .env file to test full functionality.\n")
        return
    
    if LLM_PROVIDER == "anthropic" and not ANTHROPIC_API_KEY:
        print("⚠️  Warning: ANTHROPIC_API_KEY not set. Skipping LLM tests.")
        print("   Set your API key in .env file to test full functionality.\n")
        return
    
    # Load scenario
    scenario_loader = ScenarioLoader()
    scenario_name = "Used Car Sale"
    
    public_info = scenario_loader.get_public_info(scenario_name)
    agent_a_secrets = scenario_loader.get_agent_secrets(scenario_name, "agent_a")
    agent_b_secrets = scenario_loader.get_agent_secrets(scenario_name, "agent_b")
    
    print(f"Scenario: {scenario_name}\n")
    
    # Create agents
    try:
        print("Creating Agent A (Aggressive Seller)...")
        agent_a = Agent(
            agent_id="Agent A",
            persona_name="Aggressive",
            scenario_public_info=public_info,
            agent_secrets=agent_a_secrets
        )
        print("✅ Agent A created successfully")
        
        print("\nCreating Agent B (Fair Buyer)...")
        agent_b = Agent(
            agent_id="Agent B",
            persona_name="Fair",
            scenario_public_info=public_info,
            agent_secrets=agent_b_secrets
        )
        print("✅ Agent B created successfully\n")
        
        # Test agent info
        print("Agent Information:")
        print(f"  {agent_a.get_info()}")
        print(f"  {agent_b.get_info()}\n")
        
        # Test message generation (if API keys are available)
        print("=" * 70)
        print("Testing Message Generation (Round 1):")
        print("=" * 70)
        
        # Agent A starts
        message_a = agent_a.generate_message()
        print(f"\n{agent_a.agent_id} ({agent_a.persona_name}): {message_a}\n")
        
        # Agent B receives and responds
        agent_b.add_message_to_history(agent_a.agent_id, message_a)
        message_b = agent_b.generate_message()
        print(f"{agent_b.agent_id} ({agent_b.persona_name}): {message_b}\n")
        
        # Agent A receives and responds
        agent_a.add_message_to_history(agent_b.agent_id, message_b)
        message_a2 = agent_a.generate_message()
        print(f"{agent_a.agent_id} ({agent_a.persona_name}): {message_a2}\n")
        
        print("=" * 70)
        print("\n✅ Agent system test complete!")
        print(f"   Total messages in history: {len(agent_a.get_conversation_history())}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("  1. API keys are set in .env file")
        print("  2. Required packages are installed: pip install -r requirements.txt")
        print("  3. You have API credits/quota available")

if __name__ == "__main__":
    test_agent_creation()
