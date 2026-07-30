"""
Check Concession & Convergence Data in MongoDB
Explores what data is available and creates summary tables
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
    print("📊 CONCESSION & CONVERGENCE DATA CHECKER")
    print("=" * 80)
    
    # Connect to MongoDB
    print("\n🔗 Connecting to MongoDB...")
    mongo = get_mongodb_client()
    negotiations = list(mongo.negotiations_collection.find())
    
    print(f"✅ Found {len(negotiations)} negotiations in database")
    
    if len(negotiations) == 0:
        print("❌ No negotiations found!")
        return
    
    # Check what data exists
    print("\n" + "=" * 80)
    print("🔍 CHECKING DATA AVAILABILITY")
    print("=" * 80)
    
    # Sample one negotiation to see structure
    sample = negotiations[0]
    qualitative = sample.get('qualitative_metrics', {})
    
    print("\n📋 Available qualitative metrics:")
    for key in qualitative.keys():
        print(f"   ✓ {key}")
    
    # Check for concession data
    has_concessions = 'concessions' in qualitative
    print(f"\n🔍 Concessions data: {'✓ FOUND' if has_concessions else '✗ NOT FOUND'}")
    
    if has_concessions:
        print("   Sample concession data structure:")
        concessions = qualitative['concessions']
        if isinstance(concessions, dict):
            for agent_key in concessions.keys():
                print(f"      {agent_key}: {list(concessions[agent_key].keys())[:5]}")
    
    # Check messages for price data
    messages = sample.get('messages', [])
    has_price_offers = any('price_offer' in msg for msg in messages)
    print(f"\n🔍 Price offers in messages: {'✓ FOUND' if has_price_offers else '✗ NOT FOUND'}")
    
    # Aggregate concession data
    if has_concessions:
        print("\n" + "=" * 80)
        print("📊 ANALYZING CONCESSION INTENSITY DATA")
        print("=" * 80)
        
        persona_concessions = defaultdict(lambda: {
            'avg_intensity': [],
            'max_intensity': [],
            'concession_count': [],
            'total_concession': []
        })
        
        for neg in negotiations:
            persona_a = neg.get('agent_a_persona', 'Unknown')
            persona_b = neg.get('agent_b_persona', 'Unknown')
            
            concessions = neg.get('qualitative_metrics', {}).get('concessions', {})
            
            # Agent A
            if 'agent_a' in concessions:
                a_data = concessions['agent_a']
                if 'avg_intensity' in a_data and a_data['avg_intensity'] is not None:
                    persona_concessions[persona_a]['avg_intensity'].append(a_data['avg_intensity'])
                if 'max_intensity' in a_data and a_data['max_intensity'] is not None:
                    persona_concessions[persona_a]['max_intensity'].append(a_data['max_intensity'])
                if 'concession_count' in a_data:
                    persona_concessions[persona_a]['concession_count'].append(a_data['concession_count'])
                if 'total_concession_amount' in a_data:
                    persona_concessions[persona_a]['total_concession'].append(a_data['total_concession_amount'])
            
            # Agent B
            if 'agent_b' in concessions:
                b_data = concessions['agent_b']
                if 'avg_intensity' in b_data and b_data['avg_intensity'] is not None:
                    persona_concessions[persona_b]['avg_intensity'].append(b_data['avg_intensity'])
                if 'max_intensity' in b_data and b_data['max_intensity'] is not None:
                    persona_concessions[persona_b]['max_intensity'].append(b_data['max_intensity'])
                if 'concession_count' in b_data:
                    persona_concessions[persona_b]['concession_count'].append(b_data['concession_count'])
                if 'total_concession_amount' in b_data:
                    persona_concessions[persona_b]['total_concession'].append(b_data['total_concession_amount'])
        
        # Create table
        concession_table = []
        for persona in sorted(persona_concessions.keys()):
            data = persona_concessions[persona]
            
            if data['avg_intensity']:
                row = {
                    'Persona': persona,
                    'Avg Intensity': f"{np.mean(data['avg_intensity']):.3f}",
                    'Max Intensity': f"{np.mean(data['max_intensity']):.3f}",
                    'Concession Count': f"{np.mean(data['concession_count']):.1f}",
                    'Total Concession ($)': f"${np.mean(data['total_concession']):.2f}",
                    'N': len(data['avg_intensity'])
                }
                concession_table.append(row)
        
        if concession_table:
            df_concessions = pd.DataFrame(concession_table)
            print("\n" + df_concessions.to_string(index=False))
            df_concessions.to_csv('table_concessions_per_persona.csv', index=False)
            print("\n✅ Saved to table_concessions_per_persona.csv")
        else:
            print("\n⚠️ No intensity data found")
    
    # Analyze price convergence
    print("\n" + "=" * 80)
    print("📊 ANALYZING PRICE CONVERGENCE DATA")
    print("=" * 80)
    
    convergence_data = []
    
    for neg in negotiations:
        messages = neg.get('messages', [])
        
        # Extract price offers
        prices = []
        for msg in messages:
            price = msg.get('price_offer')
            if price is not None:
                prices.append(float(price))
        
        if len(prices) >= 2:
            # Get first offers from each agent
            agent_a_offers = []
            agent_b_offers = []
            
            for i, msg in enumerate(messages):
                agent = msg.get('agent')
                price = msg.get('price_offer')
                if price is not None:
                    if agent == 'Agent A':
                        agent_a_offers.append(float(price))
                    elif agent == 'Agent B':
                        agent_b_offers.append(float(price))
            
            if agent_a_offers and agent_b_offers:
                initial_gap = abs(agent_a_offers[0] - agent_b_offers[0])
                final_gap = abs(agent_a_offers[-1] - agent_b_offers[-1])
                
                if initial_gap > 0:
                    convergence_pct = ((initial_gap - final_gap) / initial_gap) * 100
                else:
                    convergence_pct = 100.0
                
                convergence_data.append({
                    'initial_gap': initial_gap,
                    'final_gap': final_gap,
                    'convergence_pct': convergence_pct,
                    'rounds': len(messages)
                })
    
    if convergence_data:
        print(f"\n✅ Found convergence data for {len(convergence_data)} negotiations")
        
        avg_initial = np.mean([d['initial_gap'] for d in convergence_data])
        avg_final = np.mean([d['final_gap'] for d in convergence_data])
        avg_convergence = np.mean([d['convergence_pct'] for d in convergence_data])
        avg_rounds = np.mean([d['rounds'] for d in convergence_data])
        
        print(f"\n📊 OVERALL STATISTICS:")
        print(f"   Initial Gap: ${avg_initial:.2f}")
        print(f"   Final Gap: ${avg_final:.2f}")
        print(f"   Convergence: {avg_convergence:.2f}%")
        print(f"   Avg Rounds: {avg_rounds:.1f}")
        
        # Save detailed data
        df_convergence = pd.DataFrame(convergence_data)
        df_convergence.to_csv('price_convergence_data.csv', index=False)
        print(f"\n✅ Saved to price_convergence_data.csv")
    else:
        print("\n⚠️ No convergence data found")
    
    print("\n" + "=" * 80)
    print("✅ Analysis complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
