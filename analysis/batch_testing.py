"""
Batch Testing Script
Run multiple negotiations automatically for statistical analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation import NegotiationEngine, run_negotiation_realtime
from personas.persona_configs import PersonaConfigs
from utils.scenario_loader import ScenarioLoader
from datetime import datetime
import time


def run_batch_negotiations(
    scenario_name: str,
    persona_pairs: list,
    runs_per_pair: int = 5,
    max_rounds: int = 10
):
    """
    Run multiple negotiations for statistical analysis
    
    Args:
        scenario_name: Name of the scenario to use
        persona_pairs: List of (persona_a, persona_b) tuples
        runs_per_pair: Number of negotiations to run per persona pair
        max_rounds: Maximum rounds per negotiation
    """
    engine = NegotiationEngine(max_rounds=max_rounds)
    scenario_loader = ScenarioLoader()
    scenario = scenario_loader.get_scenario(scenario_name)
    scenario_type = scenario.get("type", "price_negotiation") if scenario else "price_negotiation"
    
    total_runs = len(persona_pairs) * runs_per_pair
    completed = 0
    
    print("=" * 70)
    print("BATCH NEGOTIATION TESTING")
    print("=" * 70)
    print(f"Scenario: {scenario_name}")
    print(f"Persona pairs: {len(persona_pairs)}")
    print(f"Runs per pair: {runs_per_pair}")
    print(f"Total negotiations: {total_runs}")
    print(f"Max rounds: {max_rounds}")
    print("=" * 70)
    print()
    
    results_summary = []
    start_time = time.time()
    
    for persona_a, persona_b in persona_pairs:
        print(f"\n📊 Testing: {persona_a} vs {persona_b}")
        print("-" * 50)
        
        for run in range(1, runs_per_pair + 1):
            completed += 1
            print(f"  Run {run}/{runs_per_pair}... ", end="", flush=True)
            
            try:
                # Create agents
                agent_a, agent_b = engine.create_agents(
                    scenario_name=scenario_name,
                    agent_a_persona=persona_a,
                    agent_b_persona=persona_b
                )
                
                # Run negotiation (consume generator)
                results = None
                for update in run_negotiation_realtime(agent_a, agent_b, max_rounds, scenario_type):
                    if update.get("type") == "complete":
                        results = update
                        break
                
                if results:
                    # Store summary
                    results_summary.append({
                        "persona_a": persona_a,
                        "persona_b": persona_b,
                        "run": run,
                        "agreement_reached": results.get("agreement_reached", False),
                        "rounds": results.get("rounds", 0),
                        "utility_a": results.get("utility_a"),
                        "utility_b": results.get("utility_b"),
                        "final_price": results.get("agreement_terms", {}).get("price") if results.get("agreement_terms") else None
                    })
                    
                    status = "✅ Agreement" if results.get("agreement_reached") else "❌ No deal"
                    rounds = results.get("rounds", 0)
                    print(f"{status} in {rounds} rounds")
                else:
                    print("❌ Error: No results")
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")
            
            # Progress indicator
            progress = (completed / total_runs) * 100
            elapsed = time.time() - start_time
            estimated_total = (elapsed / completed) * total_runs
            remaining = estimated_total - elapsed
            
            print(f"      Progress: {completed}/{total_runs} ({progress:.1f}%) - "
                  f"Elapsed: {elapsed:.1f}s - Remaining: ~{remaining:.1f}s")
    
    # Print summary
    total_time = time.time() - start_time
    print("\n" + "=" * 70)
    print("BATCH TESTING COMPLETE")
    print("=" * 70)
    print(f"Total negotiations: {completed}")
    print(f"Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
    print(f"Avg time per negotiation: {total_time/completed:.1f}s")
    print()
    
    # Calculate statistics
    agreements = sum(1 for r in results_summary if r["agreement_reached"])
    agreement_rate = (agreements / len(results_summary)) * 100 if results_summary else 0
    
    avg_rounds = sum(r["rounds"] for r in results_summary) / len(results_summary) if results_summary else 0
    
    successful_negotiations = [r for r in results_summary if r["agreement_reached"]]
    avg_rounds_to_agreement = sum(r["rounds"] for r in successful_negotiations) / len(successful_negotiations) if successful_negotiations else 0
    
    print(f"✅ Agreement rate: {agreement_rate:.1f}% ({agreements}/{len(results_summary)})")
    print(f"📊 Average rounds: {avg_rounds:.1f}")
    print(f"📊 Average rounds to agreement: {avg_rounds_to_agreement:.1f}")
    print()
    
    # Per-persona statistics
    print("Per-Persona Statistics:")
    print("-" * 50)
    for persona_a, persona_b in persona_pairs:
        pair_results = [r for r in results_summary 
                       if r["persona_a"] == persona_a and r["persona_b"] == persona_b]
        
        if pair_results:
            pair_agreements = sum(1 for r in pair_results if r["agreement_reached"])
            pair_agreement_rate = (pair_agreements / len(pair_results)) * 100
            pair_avg_rounds = sum(r["rounds"] for r in pair_results) / len(pair_results)
            
            print(f"  {persona_a} vs {persona_b}:")
            print(f"    Agreement rate: {pair_agreement_rate:.1f}%")
            print(f"    Avg rounds: {pair_avg_rounds:.1f}")
    
    print("\n" + "=" * 70)
    print(f"💾 All results saved to MongoDB")
    print("=" * 70)
    
    return results_summary


if __name__ == "__main__":
    # Define persona pairs to test
    PERSONA_PAIRS = [
        ("Aggressive", "Fair"),
        ("Aggressive", "Aggressive"),
        ("Fair", "Fair"),
        ("Aggressive", "Cooperative"),
        ("Stubborn", "Fair"),
        ("Desperate", "Aggressive"),
        ("Strategic", "Fair"),
        ("Logical", "Logical")
    ]
    
    # Run batch testing
    print("\n🚀 Starting batch negotiation testing...\n")
    
    results = run_batch_negotiations(
        scenario_name="Used Car Sale",
        persona_pairs=PERSONA_PAIRS,
        runs_per_pair=3,  # 3 runs per pair = 24 total negotiations
        max_rounds=10
    )
    
    print("\n✅ Batch testing complete! Use calculate_metrics.py to analyze results.")
