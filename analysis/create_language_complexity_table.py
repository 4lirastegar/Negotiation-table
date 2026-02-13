"""
Generate Language Complexity Table from MongoDB Data

This script:
1. Loads language complexity metrics from MongoDB
2. Aggregates by persona
3. Generates a table for the report
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
from utils.mongodb_client import get_mongodb_client


def main():
    print("=" * 80)
    print("📊 GENERATING LANGUAGE COMPLEXITY TABLE")
    print("=" * 80)
    
    mongo = get_mongodb_client()
    
    # Get all negotiations with language complexity data
    negotiations = list(mongo.negotiations_collection.find({
        'qualitative_metrics.language_complexity': {'$exists': True}
    }))
    
    print(f"\n✅ Found {len(negotiations)} negotiations with language complexity data")
    
    if not negotiations:
        print("❌ No data found! Run recalculate_language_metrics.py first")
        return
    
    # Organize data by persona combination
    persona_combinations = {}
    
    for neg in negotiations:
        agent_a_persona = neg.get('agent_a_persona', 'Unknown')
        agent_b_persona = neg.get('agent_b_persona', 'Unknown')
        combo = f"{agent_a_persona} vs {agent_b_persona}"
        
        if combo not in persona_combinations:
            persona_combinations[combo] = {
                'a_words_per_msg': [],
                'b_words_per_msg': [],
                'a_vocab_richness': [],
                'b_vocab_richness': [],
                'a_flesch_ease': [],
                'b_flesch_ease': [],
                'a_flesch_grade': [],
                'b_flesch_grade': [],
                'a_avg_sentence_length': [],
                'b_avg_sentence_length': []
            }
        
        # Extract language complexity metrics
        lang_complexity = neg.get('qualitative_metrics', {}).get('language_complexity', {})
        
        agent_a_metrics = lang_complexity.get('agent_a', {})
        agent_b_metrics = lang_complexity.get('agent_b', {})
        
        # Store metrics
        if agent_a_metrics:
            persona_combinations[combo]['a_words_per_msg'].append(agent_a_metrics.get('avg_words_per_message', 0))
            persona_combinations[combo]['a_vocab_richness'].append(agent_a_metrics.get('avg_vocabulary_richness', 0))
            persona_combinations[combo]['a_flesch_ease'].append(agent_a_metrics.get('avg_flesch_reading_ease', 0))
            persona_combinations[combo]['a_flesch_grade'].append(agent_a_metrics.get('avg_flesch_kincaid_grade', 0))
            persona_combinations[combo]['a_avg_sentence_length'].append(agent_a_metrics.get('avg_sentence_length', 0))
        
        if agent_b_metrics:
            persona_combinations[combo]['b_words_per_msg'].append(agent_b_metrics.get('avg_words_per_message', 0))
            persona_combinations[combo]['b_vocab_richness'].append(agent_b_metrics.get('avg_vocabulary_richness', 0))
            persona_combinations[combo]['b_flesch_ease'].append(agent_b_metrics.get('avg_flesch_reading_ease', 0))
            persona_combinations[combo]['b_flesch_grade'].append(agent_b_metrics.get('avg_flesch_kincaid_grade', 0))
            persona_combinations[combo]['b_avg_sentence_length'].append(agent_b_metrics.get('avg_sentence_length', 0))
    
    # Generate table
    print("\n" + "=" * 80)
    print("TABLE 5: LANGUAGE COMPLEXITY BY PERSONA")
    print("=" * 80)
    
    table_data = []
    for combo, data in sorted(persona_combinations.items()):
        # Calculate averages (combining both agents)
        all_words = data['a_words_per_msg'] + data['b_words_per_msg']
        all_vocab = data['a_vocab_richness'] + data['b_vocab_richness']
        all_flesch_ease = data['a_flesch_ease'] + data['b_flesch_ease']
        all_flesch_grade = data['a_flesch_grade'] + data['b_flesch_grade']
        all_sent_length = data['a_avg_sentence_length'] + data['b_avg_sentence_length']
        
        row = {
            'Persona Combination': combo,
            'Avg Words/Msg': f"{np.mean(all_words):.1f}" if all_words else "0.0",
            'Vocab Richness': f"{np.mean(all_vocab):.2f}" if all_vocab else "0.00",
            'Flesch Ease': f"{np.mean(all_flesch_ease):.1f}" if all_flesch_ease else "0.0",
            'Flesch Grade': f"{np.mean(all_flesch_grade):.1f}" if all_flesch_grade else "0.0",
            'Avg Sent Length': f"{np.mean(all_sent_length):.1f}" if all_sent_length else "0.0",
            'N': len(data['a_words_per_msg'])
        }
        table_data.append(row)
    
    df = pd.DataFrame(table_data)
    print(df.to_string(index=False))
    
    # Save to CSV
    csv_filename = "table5_language_complexity.csv"
    df.to_csv(csv_filename, index=False)
    print(f"\n✅ Saved to {csv_filename}")
    
    # Print explanation
    print("\n" + "=" * 80)
    print("📖 METRICS EXPLANATION")
    print("=" * 80)
    print("• Avg Words/Msg: Average number of words per message")
    print("• Vocab Richness: Type-Token Ratio (unique words / total words)")
    print("  → Higher = more diverse vocabulary (max = 1.0)")
    print("• Flesch Ease: Readability score (0-100)")
    print("  → Higher = easier to read (90-100 = very easy, 0-30 = very difficult)")
    print("• Flesch Grade: U.S. grade level required to understand the text")
    print("  → Lower = simpler language")
    print("• Avg Sent Length: Average number of words per sentence")
    print("  → Shorter = simpler, more direct communication")
    print("=" * 80)
    
    mongo.client.close()


if __name__ == "__main__":
    main()
