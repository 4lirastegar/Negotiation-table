"""
Calculate Metrics from MongoDB Data
Academic analysis: agreement rate, rounds to convergence, utility scores, language complexity
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.mongodb_client import get_mongodb_client
from analysis.language_metrics import LanguageMetrics
from typing import Dict, List, Any
import statistics


class MetricsCalculator:
    """Calculate academic metrics from stored negotiations"""
    
    def __init__(self):
        self.mongo_client = get_mongodb_client()
        self.language_analyzer = LanguageMetrics()
    
    def calculate_all_metrics(self, limit: int = None) -> Dict[str, Any]:
        """
        Calculate all academic metrics from MongoDB data
        
        Args:
            limit: Maximum number of negotiations to analyze (None = all)
            
        Returns:
            Dictionary with all calculated metrics
        """
        print("=" * 70)
        print("CALCULATING ACADEMIC METRICS")
        print("=" * 70)
        print()
        
        # Retrieve negotiations from MongoDB
        print("📥 Retrieving negotiations from MongoDB...")
        negotiations = self.mongo_client.get_all_negotiations(limit=limit)
        
        if not negotiations:
            print("❌ No negotiations found in database!")
            return {}
        
        print(f"✅ Found {len(negotiations)} negotiations")
        print()
        
        # Calculate metrics
        metrics = {
            "total_negotiations": len(negotiations),
            "agreement_metrics": self._calculate_agreement_metrics(negotiations),
            "rounds_metrics": self._calculate_rounds_metrics(negotiations),
            "utility_metrics": self._calculate_utility_metrics(negotiations),
            "language_metrics": self._calculate_language_metrics(negotiations),
            "persona_comparison": self._calculate_persona_metrics(negotiations)
        }
        
        # Print results
        self._print_metrics(metrics)
        
        return metrics
    
    def _calculate_agreement_metrics(self, negotiations: List[Dict]) -> Dict[str, Any]:
        """Calculate agreement rate"""
        agreements = [n for n in negotiations if n.get("agreement_reached", False)]
        agreement_rate = (len(agreements) / len(negotiations)) * 100
        
        return {
            "total_agreements": len(agreements),
            "total_disagreements": len(negotiations) - len(agreements),
            "agreement_rate_percent": agreement_rate
        }
    
    def _calculate_rounds_metrics(self, negotiations: List[Dict]) -> Dict[str, Any]:
        """Calculate rounds to convergence"""
        all_rounds = [n.get("rounds", 0) for n in negotiations]
        
        # Rounds for successful agreements only
        agreement_rounds = [n.get("rounds", 0) for n in negotiations 
                           if n.get("agreement_reached", False)]
        
        return {
            "avg_rounds_all": statistics.mean(all_rounds) if all_rounds else 0,
            "median_rounds_all": statistics.median(all_rounds) if all_rounds else 0,
            "min_rounds": min(all_rounds) if all_rounds else 0,
            "max_rounds": max(all_rounds) if all_rounds else 0,
            "avg_rounds_to_agreement": statistics.mean(agreement_rounds) if agreement_rounds else 0,
            "median_rounds_to_agreement": statistics.median(agreement_rounds) if agreement_rounds else 0
        }
    
    def _calculate_utility_metrics(self, negotiations: List[Dict]) -> Dict[str, Any]:
        """Calculate utility score statistics"""
        # Only for successful negotiations
        successful = [n for n in negotiations if n.get("agreement_reached", False)]
        
        utilities_a = [n.get("utility_a") for n in successful if n.get("utility_a") is not None]
        utilities_b = [n.get("utility_b") for n in successful if n.get("utility_b") is not None]
        
        # Combined utilities
        all_utilities = utilities_a + utilities_b
        
        return {
            "agent_a_avg_utility": statistics.mean(utilities_a) if utilities_a else 0,
            "agent_a_median_utility": statistics.median(utilities_a) if utilities_a else 0,
            "agent_b_avg_utility": statistics.mean(utilities_b) if utilities_b else 0,
            "agent_b_median_utility": statistics.median(utilities_b) if utilities_b else 0,
            "combined_avg_utility": statistics.mean(all_utilities) if all_utilities else 0,
            "combined_median_utility": statistics.median(all_utilities) if all_utilities else 0,
            "utility_stdev": statistics.stdev(all_utilities) if len(all_utilities) > 1 else 0
        }
    
    def _calculate_language_metrics(self, negotiations: List[Dict]) -> Dict[str, Any]:
        """Calculate language complexity metrics"""
        all_agent_a_metrics = []
        all_agent_b_metrics = []
        
        for negotiation in negotiations:
            messages = negotiation.get("messages", [])
            if messages:
                transcript_metrics = self.language_analyzer.analyze_negotiation_transcript(messages)
                all_agent_a_metrics.append(transcript_metrics["agent_a"])
                all_agent_b_metrics.append(transcript_metrics["agent_b"])
        
        # Aggregate across all negotiations
        def aggregate_language_metrics(metrics_list):
            if not metrics_list:
                return {}
            
            return {
                "avg_words_per_message": statistics.mean([m["avg_words_per_message"] for m in metrics_list]),
                "avg_word_length": statistics.mean([m["avg_word_length"] for m in metrics_list]),
                "avg_sentence_length": statistics.mean([m["avg_sentence_length"] for m in metrics_list]),
                
                # Vocabulary diversity (using lexicalrichness library)
                "avg_vocabulary_richness": statistics.mean([m["avg_vocabulary_richness"] for m in metrics_list]),
                "avg_root_ttr": statistics.mean([m.get("avg_root_ttr", 0) for m in metrics_list]),
                "avg_corrected_ttr": statistics.mean([m.get("avg_corrected_ttr", 0) for m in metrics_list]),
                
                # Readability (academic standard - Flesch metrics)
                "avg_flesch_reading_ease": statistics.mean([m.get("avg_flesch_reading_ease", 0) for m in metrics_list]),
                "avg_flesch_kincaid_grade": statistics.mean([m.get("avg_flesch_kincaid_grade", 0) for m in metrics_list]),
                
                # Linguistic features
                "total_questions": sum([m["total_questions"] for m in metrics_list]),
                "total_exclamations": sum([m["total_exclamations"] for m in metrics_list]),
                "total_dollar_mentions": sum([m["total_dollar_mentions"] for m in metrics_list])
            }
        
        return {
            "agent_a": aggregate_language_metrics(all_agent_a_metrics),
            "agent_b": aggregate_language_metrics(all_agent_b_metrics)
        }
    
    def _calculate_persona_metrics(self, negotiations: List[Dict]) -> Dict[str, Any]:
        """Calculate metrics by persona pairing"""
        persona_stats = {}
        
        for negotiation in negotiations:
            agent_a_info = negotiation.get("agent_a_info", {})
            agent_b_info = negotiation.get("agent_b_info", {})
            
            persona_a = agent_a_info.get("persona", "Unknown")
            persona_b = agent_b_info.get("persona", "Unknown")
            
            pair_key = f"{persona_a} vs {persona_b}"
            
            if pair_key not in persona_stats:
                persona_stats[pair_key] = {
                    "count": 0,
                    "agreements": 0,
                    "total_rounds": 0,
                    "utilities_a": [],
                    "utilities_b": []
                }
            
            persona_stats[pair_key]["count"] += 1
            
            if negotiation.get("agreement_reached", False):
                persona_stats[pair_key]["agreements"] += 1
            
            persona_stats[pair_key]["total_rounds"] += negotiation.get("rounds", 0)
            
            if negotiation.get("utility_a") is not None:
                persona_stats[pair_key]["utilities_a"].append(negotiation["utility_a"])
            if negotiation.get("utility_b") is not None:
                persona_stats[pair_key]["utilities_b"].append(negotiation["utility_b"])
        
        # Calculate aggregates
        for pair_key, stats in persona_stats.items():
            stats["agreement_rate"] = (stats["agreements"] / stats["count"]) * 100 if stats["count"] > 0 else 0
            stats["avg_rounds"] = stats["total_rounds"] / stats["count"] if stats["count"] > 0 else 0
            stats["avg_utility_a"] = statistics.mean(stats["utilities_a"]) if stats["utilities_a"] else 0
            stats["avg_utility_b"] = statistics.mean(stats["utilities_b"]) if stats["utilities_b"] else 0
        
        return persona_stats
    
    def _print_metrics(self, metrics: Dict[str, Any]):
        """Print formatted metrics"""
        print("=" * 70)
        print("METRICS RESULTS")
        print("=" * 70)
        print()
        
        # Agreement metrics
        print("📊 AGREEMENT RATE")
        print("-" * 50)
        agr = metrics["agreement_metrics"]
        print(f"  Total negotiations: {metrics['total_negotiations']}")
        print(f"  Agreements: {agr['total_agreements']}")
        print(f"  Disagreements: {agr['total_disagreements']}")
        print(f"  Agreement rate: {agr['agreement_rate_percent']:.1f}%")
        print()
        
        # Rounds metrics
        print("📊 ROUNDS TO CONVERGENCE")
        print("-" * 50)
        rounds = metrics["rounds_metrics"]
        print(f"  Average rounds (all): {rounds['avg_rounds_all']:.2f}")
        print(f"  Median rounds (all): {rounds['median_rounds_all']:.1f}")
        print(f"  Range: {rounds['min_rounds']} - {rounds['max_rounds']}")
        print(f"  Average rounds to agreement: {rounds['avg_rounds_to_agreement']:.2f}")
        print(f"  Median rounds to agreement: {rounds['median_rounds_to_agreement']:.1f}")
        print()
        
        # Utility metrics
        print("📊 UTILITY SCORES")
        print("-" * 50)
        util = metrics["utility_metrics"]
        print(f"  Agent A average utility: {util['agent_a_avg_utility']:.3f}")
        print(f"  Agent A median utility: {util['agent_a_median_utility']:.3f}")
        print(f"  Agent B average utility: {util['agent_b_avg_utility']:.3f}")
        print(f"  Agent B median utility: {util['agent_b_median_utility']:.3f}")
        print(f"  Combined average: {util['combined_avg_utility']:.3f}")
        print(f"  Standard deviation: {util['utility_stdev']:.3f}")
        print()
        
        # Language metrics
        print("📊 LANGUAGE COMPLEXITY")
        print("-" * 50)
        lang = metrics["language_metrics"]
        
        print("  Agent A:")
        if lang.get("agent_a"):
            lang_a = lang["agent_a"]
            print(f"    Avg words per message: {lang_a['avg_words_per_message']:.1f}")
            print(f"    Avg word length: {lang_a['avg_word_length']:.2f} characters")
            print(f"    Avg sentence length: {lang_a['avg_sentence_length']:.1f} words")
            print(f"    Vocabulary richness (TTR): {lang_a['avg_vocabulary_richness']:.3f}")
            if lang_a.get('avg_root_ttr', 0) > 0:
                print(f"    Root TTR (length-normalized): {lang_a['avg_root_ttr']:.3f}")
                print(f"    Corrected TTR (length-independent): {lang_a['avg_corrected_ttr']:.3f}")
            print(f"    Flesch Reading Ease: {lang_a.get('avg_flesch_reading_ease', 0):.1f}/100")
            print(f"    Flesch-Kincaid Grade: {lang_a.get('avg_flesch_kincaid_grade', 0):.1f}")
            print(f"    Questions asked: {lang_a['total_questions']}")
            print(f"    Price mentions: {lang_a['total_dollar_mentions']}")
        
        print()
        print("  Agent B:")
        if lang.get("agent_b"):
            lang_b = lang["agent_b"]
            print(f"    Avg words per message: {lang_b['avg_words_per_message']:.1f}")
            print(f"    Avg word length: {lang_b['avg_word_length']:.2f} characters")
            print(f"    Avg sentence length: {lang_b['avg_sentence_length']:.1f} words")
            print(f"    Vocabulary richness (TTR): {lang_b['avg_vocabulary_richness']:.3f}")
            if lang_b.get('avg_root_ttr', 0) > 0:
                print(f"    Root TTR (length-normalized): {lang_b['avg_root_ttr']:.3f}")
                print(f"    Corrected TTR (length-independent): {lang_b['avg_corrected_ttr']:.3f}")
            print(f"    Flesch Reading Ease: {lang_b.get('avg_flesch_reading_ease', 0):.1f}/100")
            print(f"    Flesch-Kincaid Grade: {lang_b.get('avg_flesch_kincaid_grade', 0):.1f}")
            print(f"    Questions asked: {lang_b['total_questions']}")
            print(f"    Price mentions: {lang_b['total_dollar_mentions']}")
        print()
        
        # Persona comparison
        print("📊 PERSONA COMPARISON")
        print("-" * 50)
        persona_stats = metrics["persona_comparison"]
        
        for pair_key, stats in sorted(persona_stats.items()):
            print(f"  {pair_key} (n={stats['count']}):")
            print(f"    Agreement rate: {stats['agreement_rate']:.1f}%")
            print(f"    Avg rounds: {stats['avg_rounds']:.2f}")
            print(f"    Avg utility A: {stats['avg_utility_a']:.3f}")
            print(f"    Avg utility B: {stats['avg_utility_b']:.3f}")
            print()
        
        print("=" * 70)


if __name__ == "__main__":
    calculator = MetricsCalculator()
    
    print("\n🔍 Analyzing all negotiations in database...\n")
    
    metrics = calculator.calculate_all_metrics()
    
    print("\n✅ Analysis complete!")
    print("These metrics are ready for your academic report! 📊")
