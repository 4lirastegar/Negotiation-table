"""
Re-calculate Persuasion Tactics with New Model & Threshold

This script:
1. Reads existing negotiations from MongoDB
2. Re-analyzes messages with DeBERTa + threshold 0.5
3. Updates ONLY the persuasion_tactics field in qualitative_metrics

No need to re-run entire negotiations! 🚀
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.mongodb_client import get_mongodb_client
from analysis.persuasion_tactics import PersuasionTacticsAnalyzer

def recalculate_persuasion_tactics(limit=None):
    """
    Re-calculate persuasion tactics for existing negotiations.
    
    Args:
        limit: Number of negotiations to process (None = all)
    """
    print("=" * 80)
    print("🔄 RE-CALCULATING PERSUASION TACTICS")
    print("=" * 80)
    print(f"Model: DeBERTa-v3-large-zeroshot")
    print(f"Threshold: 0.5 (was 0.3)")
    print(f"Labels: Descriptive (e.g., 'Persuasion: gives reasons...')")
    print("=" * 80)
    
    # Connect to MongoDB
    print("\n🔗 Connecting to MongoDB...")
    mongo = get_mongodb_client()
    
    # Get negotiations
    if limit:
        negotiations = list(mongo.negotiations_collection.find().limit(limit))
        print(f"✅ Found {len(negotiations)} negotiations (limit={limit})")
    else:
        negotiations = list(mongo.negotiations_collection.find())
        print(f"✅ Found {len(negotiations)} negotiations (ALL)")
    
    if not negotiations:
        print("❌ No negotiations found!")
        return
    
    # Initialize analyzer (will load DeBERTa model)
    print("\n📥 Loading DeBERTa-v3-large model...")
    analyzer = PersuasionTacticsAnalyzer()
    
    print("\n" + "=" * 80)
    print("🔄 PROCESSING NEGOTIATIONS")
    print("=" * 80)
    
    for i, neg in enumerate(negotiations, 1):
        neg_id = neg['_id']
        persona_a = neg.get('agent_a_persona', 'Unknown')
        persona_b = neg.get('agent_b_persona', 'Unknown')
        
        print(f"\n{i}/{len(negotiations)}: {persona_a} vs {persona_b}")
        print(f"   ID: {neg_id}")
        
        # Get messages
        messages = neg.get('messages', [])
        print(f"   Messages: {len(messages)}")
        
        if not messages:
            print(f"   ⚠️  No messages, skipping...")
            continue
        
        # Re-analyze with new model + threshold
        try:
            results = analyzer.analyze_negotiation(messages, threshold=0.5)
            
            # Show results
            a_tactics = results['agent_a']['tactic_counts']
            b_tactics = results['agent_b']['tactic_counts']
            
            print(f"   Agent A: Pers={a_tactics.get('persuasion', 0)}, Coop={a_tactics.get('cooperation', 0)}, Decep={a_tactics.get('deception', 0)}, Press={a_tactics.get('pressure', 0)}, Comp={a_tactics.get('compromise', 0)}")
            print(f"   Agent B: Pers={b_tactics.get('persuasion', 0)}, Coop={b_tactics.get('cooperation', 0)}, Decep={b_tactics.get('deception', 0)}, Press={b_tactics.get('pressure', 0)}, Comp={b_tactics.get('compromise', 0)}")
            
            # Update MongoDB - only persuasion_tactics field
            mongo.negotiations_collection.update_one(
                {'_id': neg_id},
                {'$set': {'qualitative_metrics.persuasion_tactics': results}}
            )
            print(f"   ✅ Updated in MongoDB")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    print("\n" + "=" * 80)
    print("✅ RE-CALCULATION COMPLETE!")
    print("=" * 80)
    print("\n📊 Next steps:")
    print("   1. Run: python3 analysis/create_report_tables.py")
    print("   2. Check table1_strategies.csv for new results")
    print("   3. See differentiation between personas!")
    print("=" * 80)


if __name__ == "__main__":
    # Process ALL negotiations
    print("\n🚀 FULL MODE: Processing ALL 60 negotiations")
    print("   This will take ~15-20 minutes...")
    print()
    
    recalculate_persuasion_tactics(limit=None)
