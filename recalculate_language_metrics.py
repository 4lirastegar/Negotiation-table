"""
Recalculate Language Complexity Metrics for Existing Negotiations in MongoDB

This script:
1. Loads all existing negotiations from MongoDB
2. Re-runs LanguageMetrics.analyze_negotiation_transcript() on each one
3. Updates ONLY the `qualitative_metrics.language_complexity` field in MongoDB
"""

from utils.mongodb_client import get_mongodb_client
from analysis.language_metrics import LanguageMetrics


def recalculate_language_metrics(limit=None):
    """
    Recalculate language complexity metrics for existing negotiations
    
    Args:
        limit: Number of negotiations to process (None = all)
    """
    print("=" * 80)
    print("🔄 RE-CALCULATING LANGUAGE COMPLEXITY FOR EXISTING NEGOTIATIONS")
    print("=" * 80)
    
    mongo = get_mongodb_client()
    analyzer = LanguageMetrics()
    
    # Get negotiations from MongoDB
    negotiations_cursor = mongo.negotiations_collection.find({})
    if limit is not None:
        negotiations_cursor = negotiations_cursor.limit(limit)
    
    negotiations_to_process = list(negotiations_cursor)
    print(f"🚀 {'FULL MODE: Processing ALL' if limit is None else f'TEST MODE: Processing first {limit}'} {len(negotiations_to_process)} negotiations")
    
    for i, neg in enumerate(negotiations_to_process):
        print(f"\n{'='*80}")
        print(f"Processing negotiation {i+1}/{len(negotiations_to_process)}")
        print(f"ID: {neg['_id']}")
        print(f"Personas: {neg.get('agent_a_persona', 'Unknown')} vs {neg.get('agent_b_persona', 'Unknown')}")
        print(f"Rounds: {neg.get('rounds', 'Unknown')}")
        
        messages = neg.get('messages', [])
        if not messages:
            print("   ⚠️ No messages found, skipping")
            continue
        
        print(f"   📝 Analyzing {len(messages)} messages...")
        
        # Re-run the language complexity analysis
        try:
            language_results = analyzer.analyze_negotiation_transcript(messages)
            
            # Update only the language_complexity field in the existing qualitative_metrics
            mongo.negotiations_collection.update_one(
                {'_id': neg['_id']},
                {'$set': {
                    'qualitative_metrics.language_complexity': language_results
                }}
            )
            
            # Print summary
            if language_results:
                a_words = language_results['agent_a']['avg_words_per_message']
                b_words = language_results['agent_b']['avg_words_per_message']
                a_vocab = language_results['agent_a']['avg_vocabulary_richness']
                b_vocab = language_results['agent_b']['avg_vocabulary_richness']
                a_flesch = language_results['agent_a']['avg_flesch_reading_ease']
                b_flesch = language_results['agent_b']['avg_flesch_reading_ease']
                
                print(f"   Agent A: {a_words:.1f} words/msg, {a_vocab:.2f} vocab richness, {a_flesch:.1f} Flesch")
                print(f"   Agent B: {b_words:.1f} words/msg, {b_vocab:.2f} vocab richness, {b_flesch:.1f} Flesch")
                print("   ✅ Updated in MongoDB")
            else:
                print("   ⚠️ Analysis returned None")
        
        except Exception as e:
            print(f"   ❌ Error analyzing negotiation: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("✅ RE-CALCULATION COMPLETE!")
    print("=" * 80)
    print("📊 Next steps:")
    print("   1. Run `python3 analysis/create_language_complexity_table.py` to generate CSVs")
    print("   2. Update your LaTeX report with the new table")
    mongo.client.close()


if __name__ == "__main__":
    import sys
    
    # Check if user wants to test with limited negotiations
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("\n🧪 TEST MODE: Processing first 2 negotiations only\n")
        recalculate_language_metrics(limit=2)
    else:
        print("\n🚀 FULL MODE: Processing ALL negotiations\n")
        # Auto-proceed in non-interactive mode
        recalculate_language_metrics(limit=None)
