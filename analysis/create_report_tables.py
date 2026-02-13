"""
Report Table Generator

Extracts data from MongoDB and creates comparison tables for academic analysis.
Just describes what the data shows - no manual thresholds or classifications!
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.mongodb_client import get_mongodb_client
import pandas as pd
from collections import defaultdict
import numpy as np


def main():
    print("=" * 80)
    print("📊 REPORT TABLE GENERATOR")
    print("=" * 80)
    
    # Connect to MongoDB
    print("\n🔗 Connecting to MongoDB...")
    mongo = get_mongodb_client()
    negotiations = list(mongo.negotiations_collection.find())
    
    print(f"✅ Found {len(negotiations)} negotiations in database")
    
    if len(negotiations) == 0:
        print("❌ No negotiations found! Run batch tests first.")
        return
    
    # ============================================================================
    # TABLE 1: EMERGENT STRATEGIES (Persuasion Tactics)
    # ============================================================================
    
    print("\n" + "=" * 80)
    print("TABLE 1: EMERGENT COMMUNICATIVE STRATEGIES")
    print("=" * 80)
    
    strategies_by_combo = defaultdict(lambda: defaultdict(list))
    
    for neg in negotiations:
        persona_a = neg.get('agent_a_persona', 'Unknown')
        persona_b = neg.get('agent_b_persona', 'Unknown')
        combo = f"{persona_a} vs {persona_b}"
        
        # Extract tactics
        tactics = neg.get('qualitative_metrics', {}).get('persuasion_tactics', {})
        
        if tactics:
            # Agent A tactics
            a_tactics = tactics.get('agent_a', {}).get('tactic_counts', {})
            for tactic in ['persuasion', 'cooperation', 'deception', 'pressure', 'compromise']:
                strategies_by_combo[combo][f'a_{tactic}'].append(a_tactics.get(tactic, 0))
            
            # Agent B tactics
            b_tactics = tactics.get('agent_b', {}).get('tactic_counts', {})
            for tactic in ['persuasion', 'cooperation', 'deception', 'pressure', 'compromise']:
                strategies_by_combo[combo][f'b_{tactic}'].append(b_tactics.get(tactic, 0))
        
        # Agreement rate
        strategies_by_combo[combo]['agreement'].append(
            1 if neg.get('agreement_reached') else 0
        )
        
        # Rounds
        strategies_by_combo[combo]['rounds'].append(neg.get('rounds', 0))
    
    # Create table
    table1_data = []
    for combo in sorted(strategies_by_combo.keys()):
        data = strategies_by_combo[combo]
        
        # Calculate averages (combining both agents)
        all_persuasion = data.get('a_persuasion', []) + data.get('b_persuasion', [])
        all_cooperation = data.get('a_cooperation', []) + data.get('b_cooperation', [])
        all_deception = data.get('a_deception', []) + data.get('b_deception', [])
        all_pressure = data.get('a_pressure', []) + data.get('b_pressure', [])
        all_compromise = data.get('a_compromise', []) + data.get('b_compromise', [])
        
        row = {
            'Persona Combination': combo,
            'Persuasion (Avg)': f"{np.mean(all_persuasion):.1f}" if all_persuasion else "0.0",
            'Cooperation (Avg)': f"{np.mean(all_cooperation):.1f}" if all_cooperation else "0.0",
            'Deception (Avg)': f"{np.mean(all_deception):.1f}" if all_deception else "0.0",
            'Pressure (Avg)': f"{np.mean(all_pressure):.1f}" if all_pressure else "0.0",
            'Compromise (Avg)': f"{np.mean(all_compromise):.1f}" if all_compromise else "0.0",
            'Agreement Rate': f"{np.mean(data['agreement'])*100:.0f}%",
            'Avg Rounds': f"{np.mean(data['rounds']):.1f}",
            'N': len(data['agreement'])
        }
        table1_data.append(row)
    
    df1 = pd.DataFrame(table1_data)
    print("\n" + df1.to_string(index=False))
    
    # Save to CSV
    df1.to_csv('table1_strategies.csv', index=False)
    print("\n✅ Saved to table1_strategies.csv")
    
    # ============================================================================
    # TABLE 2: EMOTIONAL TONE
    # ============================================================================
    
    print("\n" + "=" * 80)
    print("TABLE 2: EMOTIONAL TONE PATTERNS")
    print("=" * 80)
    
    emotion_by_persona = defaultdict(lambda: defaultdict(list))
    
    for neg in negotiations:
        persona_a = neg.get('agent_a_persona', 'Unknown')
        persona_b = neg.get('agent_b_persona', 'Unknown')
        
        emotions = neg.get('qualitative_metrics', {}).get('emotional_tone', {})
        
        if emotions:
            # Agent A
            a_dist = emotions.get('agent_a', {}).get('emotion_distribution', {})
            if a_dist:
                emotion_by_persona[persona_a]['positive'].append(a_dist.get('positive', 0))
                emotion_by_persona[persona_a]['neutral'].append(a_dist.get('neutral', 0))
                emotion_by_persona[persona_a]['negative'].append(a_dist.get('negative', 0))
            
            # Agent B
            b_dist = emotions.get('agent_b', {}).get('emotion_distribution', {})
            if b_dist:
                emotion_by_persona[persona_b]['positive'].append(b_dist.get('positive', 0))
                emotion_by_persona[persona_b]['neutral'].append(b_dist.get('neutral', 0))
                emotion_by_persona[persona_b]['negative'].append(b_dist.get('negative', 0))
    
    # Create table
    table2_data = []
    for persona in sorted(emotion_by_persona.keys()):
        data = emotion_by_persona[persona]
        
        if data['positive']:  # Only if we have data
            row = {
                'Persona': persona,
                'Positive %': f"{np.mean(data['positive'])*100:.1f}%",
                'Neutral %': f"{np.mean(data['neutral'])*100:.1f}%",
                'Negative %': f"{np.mean(data['negative'])*100:.1f}%",
                'N': len(data['positive'])
            }
            table2_data.append(row)
    
    df2 = pd.DataFrame(table2_data)
    print("\n" + df2.to_string(index=False))
    
    df2.to_csv('table2_emotions.csv', index=False)
    print("\n✅ Saved to table2_emotions.csv")
    
    # ============================================================================
    # TABLE 3: LOGICAL COHERENCE
    # ============================================================================
    
    print("\n" + "=" * 80)
    print("TABLE 3: LOGICAL COHERENCE (GENUINE VS SCRIPTED)")
    print("=" * 80)
    
    coherence_by_persona = defaultdict(lambda: defaultdict(list))
    
    for neg in negotiations:
        persona_a = neg.get('agent_a_persona', 'Unknown')
        persona_b = neg.get('agent_b_persona', 'Unknown')
        
        coherence = neg.get('qualitative_metrics', {}).get('logical_coherence', {})
        
        if coherence:
            # Agent A
            a_coh = coherence.get('agent_a', {})
            if a_coh:
                coherence_by_persona[persona_a]['context'].append(a_coh.get('context_coherence', 0))
                coherence_by_persona[persona_a]['self'].append(a_coh.get('self_coherence', 0))
                coherence_by_persona[persona_a]['goal'].append(a_coh.get('goal_coherence', 0))
            
            # Agent B
            b_coh = coherence.get('agent_b', {})
            if b_coh:
                coherence_by_persona[persona_b]['context'].append(b_coh.get('context_coherence', 0))
                coherence_by_persona[persona_b]['self'].append(b_coh.get('self_coherence', 0))
                coherence_by_persona[persona_b]['goal'].append(b_coh.get('goal_coherence', 0))
    
    # Create table
    table3_data = []
    for persona in sorted(coherence_by_persona.keys()):
        data = coherence_by_persona[persona]
        
        if data['context']:  # Only if we have data
            row = {
                'Persona': persona,
                'Context Coherence': f"{np.mean(data['context']):.2f}",
                'Self Coherence': f"{np.mean(data['self']):.2f}",
                'Goal Coherence': f"{np.mean(data['goal']):.2f}",
                'N': len(data['context'])
            }
            table3_data.append(row)
    
    df3 = pd.DataFrame(table3_data)
    print("\n" + df3.to_string(index=False))
    
    df3.to_csv('table3_coherence.csv', index=False)
    print("\n✅ Saved to table3_coherence.csv")
    
    # ============================================================================
    # TABLE 4: UTILITY & LANGUAGE (Quantitative Metrics)
    # ============================================================================
    
    print("\n" + "=" * 80)
    print("TABLE 4: UTILITY SCORES & LANGUAGE COMPLEXITY")
    print("=" * 80)
    
    utility_by_persona = defaultdict(lambda: defaultdict(list))
    
    for neg in negotiations:
        persona_a = neg.get('agent_a_persona', 'Unknown')
        persona_b = neg.get('agent_b_persona', 'Unknown')
        
        # Utility scores
        utility_a = neg.get('utility_a')
        utility_b = neg.get('utility_b')
        
        if utility_a is not None:
            utility_by_persona[persona_a]['utility'].append(utility_a)
        if utility_b is not None:
            utility_by_persona[persona_b]['utility'].append(utility_b)
    
    # Create table
    table4_data = []
    for persona in sorted(utility_by_persona.keys()):
        data = utility_by_persona[persona]
        
        if data['utility']:
            row = {
                'Persona': persona,
                'Avg Utility': f"{np.mean(data['utility']):.2f}",
                'Utility SD': f"{np.std(data['utility']):.2f}",
                'N': len(data['utility'])
            }
            table4_data.append(row)
    
    df4 = pd.DataFrame(table4_data)
    print("\n" + df4.to_string(index=False))
    
    df4.to_csv('table4_utility.csv', index=False)
    print("\n✅ Saved to table4_utility.csv")
    
    # ============================================================================
    # SUMMARY & INTERPRETATION GUIDE
    # ============================================================================
    
    print("\n" + "=" * 80)
    print("📊 ANALYSIS COMPLETE!")
    print("=" * 80)
    print("\n✅ Created 4 CSV files:")
    print("   1. table1_strategies.csv - Emergent strategies by persona combination")
    print("   2. table2_emotions.csv - Emotional tone by persona")
    print("   3. table3_coherence.csv - Logical coherence by persona")
    print("   4. table4_utility.csv - Utility scores by persona")
    
    print("\n" + "=" * 80)
    print("💡 HOW TO USE IN YOUR REPORT")
    print("=" * 80)
    print("""
1. Open the CSV files in Excel/Google Sheets
2. Copy tables into your report
3. DESCRIBE what you see in the numbers (no manual thresholds!)

Example interpretation:

"Fair agents exhibited significantly higher cooperation counts (M=9.7) 
compared to Aggressive agents (M=2.1), accompanied by higher agreement 
rates (85% vs 45%). This demonstrates emergent cooperative vs competitive 
strategies."

"Emotional tone analysis showed persona-dependent patterns. Fair agents 
displayed predominantly positive tone (58%) vs Aggressive (32%), providing 
evidence for pragmatic adaptation rather than scripted responses."

"High goal coherence across all agents (M=0.77) indicates strategic, 
goal-directed behavior consistent with genuine reasoning. Context coherence 
(M=0.68) suggests pragmatic adaptation to opponent messages."

Just report the numbers and describe patterns! ✨
    """)
    
    print("=" * 80)
    print("🎓 Ready for your report!")
    print("=" * 80)


if __name__ == "__main__":
    main()
