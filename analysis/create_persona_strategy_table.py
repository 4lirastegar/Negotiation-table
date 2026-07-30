"""
Create Per-Persona Strategy Table
Aggregates strategy usage for each individual persona across all negotiations
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
    print("📊 PER-PERSONA STRATEGY TABLE GENERATOR")
    print("=" * 80)
    
    # Connect to MongoDB
    print("\n🔗 Connecting to MongoDB...")
    mongo = get_mongodb_client()
    negotiations = list(mongo.negotiations_collection.find())
    
    print(f"✅ Found {len(negotiations)} negotiations in database")
    
    if len(negotiations) == 0:
        print("❌ No negotiations found! Run batch tests first.")
        return
    
    # Aggregate data by persona
    persona_data = defaultdict(lambda: {
        'persuasion': [],
        'cooperation': [],
        'compromise': [],
        'deception': [],
        'pressure': [],
        'agreements': [],
        'positive_emotion': [],
        'utility': []
    })
    
    print("\n📈 Processing negotiations...")
    
    for neg in negotiations:
        persona_a = neg.get('agent_a_persona', 'Unknown')
        persona_b = neg.get('agent_b_persona', 'Unknown')
        
        # Get tactics
        tactics = neg.get('qualitative_metrics', {}).get('persuasion_tactics', {})
        
        # Agent A tactics
        if tactics and 'agent_a' in tactics:
            a_tactics = tactics['agent_a'].get('tactic_counts', {})
            persona_data[persona_a]['persuasion'].append(a_tactics.get('persuasion', 0))
            persona_data[persona_a]['cooperation'].append(a_tactics.get('cooperation', 0))
            persona_data[persona_a]['compromise'].append(a_tactics.get('compromise', 0))
            persona_data[persona_a]['deception'].append(a_tactics.get('deception', 0))
            persona_data[persona_a]['pressure'].append(a_tactics.get('pressure', 0))
        
        # Agent B tactics
        if tactics and 'agent_b' in tactics:
            b_tactics = tactics['agent_b'].get('tactic_counts', {})
            persona_data[persona_b]['persuasion'].append(b_tactics.get('persuasion', 0))
            persona_data[persona_b]['cooperation'].append(b_tactics.get('cooperation', 0))
            persona_data[persona_b]['compromise'].append(b_tactics.get('compromise', 0))
            persona_data[persona_b]['deception'].append(b_tactics.get('deception', 0))
            persona_data[persona_b]['pressure'].append(b_tactics.get('pressure', 0))
        
        # Agreement data
        agreement = 1 if neg.get('agreement_reached') else 0
        persona_data[persona_a]['agreements'].append(agreement)
        persona_data[persona_b]['agreements'].append(agreement)
        
        # Emotions
        emotions = neg.get('qualitative_metrics', {}).get('emotional_tone', {})
        if emotions and 'agent_a' in emotions:
            a_dist = emotions['agent_a'].get('emotion_distribution', {})
            persona_data[persona_a]['positive_emotion'].append(a_dist.get('positive', 0))
        
        if emotions and 'agent_b' in emotions:
            b_dist = emotions['agent_b'].get('emotion_distribution', {})
            persona_data[persona_b]['positive_emotion'].append(b_dist.get('positive', 0))
        
        # Utility
        utility_a = neg.get('utility_a')
        utility_b = neg.get('utility_b')
        
        if utility_a is not None:
            persona_data[persona_a]['utility'].append(utility_a)
        if utility_b is not None:
            persona_data[persona_b]['utility'].append(utility_b)
    
    # Create table
    print("\n📊 Generating table...")
    
    table_data = []
    for persona in sorted(persona_data.keys()):
        data = persona_data[persona]
        
        if not data['persuasion']:  # Skip if no data
            continue
        
        row = {
            'Persona': persona,
            'Persuasion (Avg)': f"{np.mean(data['persuasion']):.2f}",
            'Cooperation (Avg)': f"{np.mean(data['cooperation']):.2f}",
            'Compromise (Avg)': f"{np.mean(data['compromise']):.2f}",
            'Deception (Avg)': f"{np.mean(data['deception']):.2f}",
            'Pressure (Avg)': f"{np.mean(data['pressure']):.2f}",
            'Agreement Rate': f"{np.mean(data['agreements'])*100:.0f}%",
            'Positive Emotion %': f"{np.mean(data['positive_emotion'])*100:.1f}%" if data['positive_emotion'] else "N/A",
            'Avg Utility': f"{np.mean(data['utility']):.2f}" if data['utility'] else "N/A",
            'N (agent instances)': len(data['persuasion'])
        }
        table_data.append(row)
    
    df = pd.DataFrame(table_data)
    
    # Display
    print("\n" + "=" * 80)
    print("TABLE: NEGOTIATION STRATEGIES PER PERSONA")
    print("=" * 80)
    print("\n" + df.to_string(index=False))
    
    # Save to CSV
    output_file = 'table_strategies_per_persona_accurate.csv'
    df.to_csv(output_file, index=False)
    print(f"\n✅ Saved to {output_file}")
    
    # Summary statistics
    print("\n" + "=" * 80)
    print("📊 SUMMARY STATISTICS")
    print("=" * 80)
    
    print("\n🎯 PERSUASION RANKING (High to Low):")
    persuasion_sorted = sorted(table_data, key=lambda x: float(x['Persuasion (Avg)']), reverse=True)
    for i, row in enumerate(persuasion_sorted, 1):
        print(f"   {i}. {row['Persona']}: {row['Persuasion (Avg)']}")
    
    print("\n💰 UTILITY RANKING (High to Low):")
    utility_sorted = sorted([r for r in table_data if r['Avg Utility'] != 'N/A'], 
                           key=lambda x: float(x['Avg Utility']), reverse=True)
    for i, row in enumerate(utility_sorted, 1):
        print(f"   {i}. {row['Persona']}: {row['Avg Utility']}")
    
    print("\n🤝 AGREEMENT RATE RANKING (High to Low):")
    agreement_sorted = sorted(table_data, key=lambda x: float(x['Agreement Rate'].rstrip('%')), reverse=True)
    for i, row in enumerate(agreement_sorted, 1):
        print(f"   {i}. {row['Persona']}: {row['Agreement Rate']}")
    
    print("\n" + "=" * 80)
    print("✅ Analysis complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
