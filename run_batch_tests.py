"""
Batch Testing Script for Negotiation Analysis

Runs multiple negotiations with different persona combinations to collect data
for academic analysis.

Persona Combinations:
- None vs None
- Aggressive vs Aggressive
- Aggressive vs Fair
- Fair vs Fair

Each combination runs 5 negotiations for statistical significance.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.agent import Agent
from utils.scenario_loader import ScenarioLoader
from simulation.realtime_negotiation import run_single_negotiation
from utils.mongodb_client import get_mongodb_client
import time


# Test configuration
PERSONA_COMBINATIONS = [
    ("None", "None"),
    ("Aggressive", "Aggressive"),
    ("Aggressive", "Fair"),
    ("Fair", "Fair"),
    ("Liar","Fair"),
    ("Strategic","Aggressive")
]

NEGOTIATIONS_PER_COMBINATION = 10
MAX_ROUNDS = 10


def run_batch_tests():
    """
    Run batch tests for all persona combinations.
    """
    print("=" * 80)
    print("🚀 BATCH TESTING - Qualitative Metrics Analysis")
    print("=" * 80)
    print(f"Persona Combinations: {len(PERSONA_COMBINATIONS)}")
    print(f"Negotiations per combination: {NEGOTIATIONS_PER_COMBINATION}")
    print(f"Total negotiations: {len(PERSONA_COMBINATIONS) * NEGOTIATIONS_PER_COMBINATION}")
    print(f"Max rounds per negotiation: {MAX_ROUNDS}")
    print("=" * 80)
    
    # Load scenario
    print("\n📂 Loading scenario...")
    loader = ScenarioLoader()
    scenario_names = loader.list_scenarios()
    
    if not scenario_names:
        print("❌ No scenarios found!")
        return
    
    # Use the first scenario (Used Car Sale)
    scenario = loader.get_scenario(scenario_names[0])
    print(f"✅ Loaded scenario: {scenario['name']}")
    
    # Initialize MongoDB client
    print("\n📊 Connecting to MongoDB...")
    mongo_client = get_mongodb_client()
    print("✅ Connected to MongoDB")
    
    # Track all results
    test_start_time = datetime.now()
    all_negotiation_ids = []
    total_negotiations = 0
    successful_negotiations = 0
    
    # Run tests for each combination
    for combo_idx, (persona_a, persona_b) in enumerate(PERSONA_COMBINATIONS, 1):
        print("\n" + "=" * 80)
        print(f"📋 Combination {combo_idx}/{len(PERSONA_COMBINATIONS)}: {persona_a} vs {persona_b}")
        print("=" * 80)
        
        combo_negotiation_ids = []
        
        for neg_idx in range(1, NEGOTIATIONS_PER_COMBINATION + 1):
            total_negotiations += 1
            print(f"\n  🎮 Negotiation {neg_idx}/{NEGOTIATIONS_PER_COMBINATION}")
            print(f"     Agent A: {persona_a} (Seller)")
            print(f"     Agent B: {persona_b} (Buyer)")
            
            try:
                # Run negotiation (function creates agents internally)
                print(f"     ⏳ Running negotiation...")
                start_time = time.time()
                
                results = run_single_negotiation(
                    scenario_name=scenario["name"],
                    agent_a_persona=persona_a,
                    agent_b_persona=persona_b,
                    max_rounds=MAX_ROUNDS
                )
                
                elapsed = time.time() - start_time
                
                # Extract key info
                agreement = results.get("agreement_reached", False)
                rounds = results.get("rounds", 0)
                negotiation_id = results.get("negotiation_id")
                
                print(f"     ✅ Completed in {elapsed:.1f}s")
                print(f"        Agreement: {'✓' if agreement else '✗'}")
                print(f"        Rounds: {rounds}")
                print(f"        MongoDB ID: {negotiation_id}")
                
                if negotiation_id:
                    combo_negotiation_ids.append(negotiation_id)
                    all_negotiation_ids.append(negotiation_id)
                    successful_negotiations += 1
                
            except Exception as e:
                print(f"     ❌ Error: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n  📊 Combination Summary:")
        print(f"     Total negotiations: {NEGOTIATIONS_PER_COMBINATION}")
        print(f"     Successful: {len(combo_negotiation_ids)}")
        print(f"     Saved IDs: {combo_negotiation_ids}")
    
    # Final summary
    test_duration = (datetime.now() - test_start_time).total_seconds()
    
    print("\n" + "=" * 80)
    print("🎉 BATCH TESTING COMPLETE!")
    print("=" * 80)
    print(f"Total negotiations attempted: {total_negotiations}")
    print(f"Successfully completed: {successful_negotiations}")
    print(f"Success rate: {successful_negotiations/total_negotiations*100:.1f}%")
    print(f"Total duration: {test_duration/60:.1f} minutes")
    print(f"Average time per negotiation: {test_duration/total_negotiations:.1f}s")
    print(f"\n📁 All negotiation IDs saved to MongoDB:")
    for idx, neg_id in enumerate(all_negotiation_ids, 1):
        print(f"   {idx}. {neg_id}")
    
    # Individual negotiations are already saved to MongoDB!
    # No need to save test metadata separately - you can query by persona combinations
    
    print("\n" + "=" * 80)
    print("🔍 Next Steps:")
    print("1. Use MongoDB Compass to view all negotiations")
    print("2. Run analysis/calculate_metrics.py to compute aggregate statistics")
    print("3. Create comparison tables for your report")
    print("=" * 80)


if __name__ == "__main__":
    run_batch_tests()
