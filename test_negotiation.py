"""
Test script for negotiation engine
"""

from simulation.negotiation_engine import NegotiationEngine
import json

def test_negotiation():
    """Test a complete negotiation"""
    print("=" * 70)
    print("Testing Negotiation Engine")
    print("=" * 70)
    print()
    
    # Initialize engine
    engine = NegotiationEngine(max_rounds=10)
    
    # Run a negotiation
    print("Scenario: Used Car Sale")
    print("Agent A: Aggressive (Seller)")
    print("Agent B: Fair (Buyer)")
    print()
    print("Starting negotiation...\n")
    print("-" * 70)
    
    results = engine.simulate(
        scenario_name="Used Car Sale",
        agent_a_persona="Aggressive",
        agent_b_persona="Fair",
        max_rounds=10
    )
    
    # Display messages
    print("\nNegotiation Dialogue:\n")
    for msg in results["messages"]:
        agent_name = msg["agent"]
        persona = msg["persona"]
        message = msg["message"]
        round_num = msg["round"]
        
        print(f"[Round {round_num}] {agent_name} ({persona}):")
        print(f"  {message}\n")
    
    print("-" * 70)
    print("\nJudge Analysis:")
    print("-" * 70)
    judge_analysis = results.get('judge_analysis', {})
    print(f"  Agreement Reached: {judge_analysis.get('agreement_reached', False)}")
    print(f"  Winner: {judge_analysis.get('winner', 'Unknown')}")
    print(f"  Agent A Satisfaction: {judge_analysis.get('agent_a_satisfaction', 'Unknown')}")
    print(f"  Agent B Satisfaction: {judge_analysis.get('agent_b_satisfaction', 'Unknown')}")
    print(f"\n  Reasoning: {judge_analysis.get('reasoning', 'N/A')[:200]}...")
    
    print("\n" + "-" * 70)
    print("\nResults Summary:")
    print(f"  Agreement Reached: {results['agreement_reached']}")
    print(f"  Rounds: {results['rounds']}/{results['max_rounds']}")
    
    if results['agreement_reached']:
        print(f"  Agreement Terms: {results['agreement_terms']}")
        if results['utility_a'] is not None:
            print(f"  Agent A Utility: {results['utility_a']:.2f}")
        if results['utility_b'] is not None:
            print(f"  Agent B Utility: {results['utility_b']:.2f}")
    
    print()
    print("=" * 70)
    
    return results

if __name__ == "__main__":
    try:
        results = test_negotiation()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("  1. API keys are set in .env file")
        print("  2. You have API credits/quota available")
        print("  3. Required packages are installed")
