"""
Language Complexity Metrics
Academic approach using standard NLP measures (not LLM-based)

Uses professional NLP libraries:
- lexicalrichness: For Type-Token Ratio (TTR) and vocabulary diversity
- nltk: For tokenization and linguistic analysis
"""

import re
from typing import Dict, List, Any

# Professional NLP libraries (REQUIRED - no fallbacks!)
from lexicalrichness import LexicalRichness
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
import textstat


class LanguageMetrics:
    """Calculate objective language complexity metrics"""
    
    @staticmethod
    def calculate_metrics(message: str) -> Dict[str, Any]:
        """
        Calculate all language metrics for a message using professional NLP libraries
        
        Args:
            message: Text message to analyze
            
        Returns:
            Dictionary with language metrics
        
        Metrics Explained:
        ------------------
        1. word_count: Total number of words (using NLTK tokenizer if available)
        2. sentence_count: Total number of sentences (using NLTK if available)
        3. avg_word_length: Average number of characters per word
        4. avg_sentence_length: Average number of words per sentence
        5. vocabulary_richness (TTR): Ratio of unique words to total words
           - 1.0 = every word is unique (very diverse)
           - 0.0 = same word repeated (not diverse)
        6. root_ttr: Length-normalized TTR (better for comparing texts of different lengths)
        7. corrected_ttr: Another length-independent TTR measure
        8. question_count: Number of '?' in the message
        9. exclamation_count: Number of '!' in the message
        10. dollar_mentions: Number of dollar amounts mentioned (e.g., $500)
        """
        
        # STEP 1: Tokenize using NLTK (REQUIRED)
        words = word_tokenize(message)  # NLTK's smart tokenizer
        sentences = sent_tokenize(message)  # NLTK's sentence splitter
        
        # STEP 2: Calculate lexical diversity using lexicalrichness library (REQUIRED)
        lex = LexicalRichness(message)
        # TTR = Type-Token Ratio (unique words / total words)
        basic_ttr = lex.ttr
        # Root TTR = TTR / sqrt(total words) - better for long texts
        root_ttr = lex.rttr
        # Corrected TTR = unique words / sqrt(2 * total words) - length-independent
        corrected_ttr = lex.cttr
        
        # STEP 3: Calculate Flesch readability metrics
        flesch_metrics = LanguageMetrics.calculate_flesch_metrics(message)
        
        # STEP 4: Return all metrics
        return {
            # Basic counts
            "word_count": len(words),
            "sentence_count": len(sentences),
            "character_count": len(message),
            
            # Complexity measures
            "avg_word_length": LanguageMetrics._avg_word_length(words),
            "avg_sentence_length": len(words) / len(sentences) if sentences else 0,
            
            # Vocabulary diversity (using lexicalrichness library)
            "vocabulary_richness": basic_ttr,  # Basic TTR
            "root_ttr": root_ttr,  # Length-normalized TTR
            "corrected_ttr": corrected_ttr,  # Another length-independent measure
            
            # Readability (using textstat library - Academic Standard!)
            "flesch_reading_ease": flesch_metrics["flesch_reading_ease"],
            "flesch_kincaid_grade": flesch_metrics["flesch_kincaid_grade"],
            
            # Linguistic features
            "question_count": message.count('?'),
            "exclamation_count": message.count('!'),
            "number_mentions": len(re.findall(r'\d+', message)),
            "dollar_mentions": len(re.findall(r'\$\s*\d+', message)),
        }
    
    @staticmethod
    def _avg_word_length(words: List[str]) -> float:
        """Average word length in characters"""
        if not words:
            return 0.0
        return sum(len(word) for word in words) / len(words)
    
    @staticmethod
    def calculate_flesch_metrics(message: str) -> Dict[str, float]:
        """
        Calculate Flesch readability metrics using textstat library (REQUIRED)
        
        These are well-established academic metrics for text readability:
        
        1. Flesch Reading Ease (0-100):
           - 90-100: Very Easy (5th grade)
           - 80-89: Easy (6th grade)
           - 70-79: Fairly Easy (7th grade)
           - 60-69: Standard (8th-9th grade)
           - 50-59: Fairly Difficult (10th-12th grade)
           - 30-49: Difficult (College)
           - 0-29: Very Difficult (College graduate)
           
           Higher score = Easier to read
        
        2. Flesch-Kincaid Grade Level:
           - Returns U.S. school grade level (e.g., 8.2 = 8th grade)
           - More intuitive interpretation
        
        Academic Citations:
        - Flesch, R. (1948). A new readability yardstick. Journal of Applied Psychology.
        - Kincaid et al. (1975). Derivation of new readability formulas.
        
        Returns:
            Dictionary with both Flesch metrics
        """
        return {
            "flesch_reading_ease": textstat.flesch_reading_ease(message),
            "flesch_kincaid_grade": textstat.flesch_kincaid_grade(message)
        }
    
    @staticmethod
    def analyze_negotiation_transcript(messages: List[Dict]) -> Dict[str, Any]:
        """
        Analyze entire negotiation transcript
        
        Args:
            messages: List of message dictionaries with 'message', 'agent', 'round'
            
        Returns:
            Dictionary with aggregated metrics per agent
        """
        agent_a_messages = []
        agent_b_messages = []
        
        for msg in messages:
            if msg.get('type') != 'message':
                continue
            
            text = msg.get('message', '')
            if msg.get('agent') == 'Agent A':
                agent_a_messages.append(text)
            elif msg.get('agent') == 'Agent B':
                agent_b_messages.append(text)
        
        # Calculate metrics for each agent
        agent_a_metrics = LanguageMetrics._aggregate_metrics(agent_a_messages)
        agent_b_metrics = LanguageMetrics._aggregate_metrics(agent_b_messages)
        
        return {
            "agent_a": agent_a_metrics,
            "agent_b": agent_b_metrics,
            "total_messages": len(messages),
            "agent_a_message_count": len(agent_a_messages),
            "agent_b_message_count": len(agent_b_messages)
        }
    
    @staticmethod
    def _aggregate_metrics(messages: List[str]) -> Dict[str, Any]:
        """
        Calculate aggregated metrics for a list of messages
        
        This takes all messages from one agent and calculates:
        - Average metrics across all their messages
        - Total counts of linguistic features
        """
        if not messages:
            return {
                "message_count": 0,
                "total_words": 0,
                "avg_words_per_message": 0.0,
                "avg_word_length": 0.0,
                "avg_sentence_length": 0.0,
                "avg_vocabulary_richness": 0.0,
                "avg_root_ttr": 0.0,
                "avg_corrected_ttr": 0.0,
                "avg_flesch_reading_ease": 0.0,
                "avg_flesch_kincaid_grade": 0.0,
                "total_questions": 0,
                "total_exclamations": 0,
                "total_number_mentions": 0,
                "total_dollar_mentions": 0
            }
        
        # Calculate metrics for each individual message
        all_metrics = [LanguageMetrics.calculate_metrics(msg) for msg in messages]
        
        # Aggregate the results
        return {
            "message_count": len(messages),
            "total_words": sum(m["word_count"] for m in all_metrics),
            "avg_words_per_message": sum(m["word_count"] for m in all_metrics) / len(messages),
            "avg_word_length": sum(m["avg_word_length"] for m in all_metrics) / len(messages),
            "avg_sentence_length": sum(m["avg_sentence_length"] for m in all_metrics) / len(messages),
            
            # Vocabulary diversity metrics (from lexicalrichness)
            "avg_vocabulary_richness": sum(m["vocabulary_richness"] for m in all_metrics) / len(messages),
            "avg_root_ttr": sum(m.get("root_ttr", 0) for m in all_metrics) / len(messages),
            "avg_corrected_ttr": sum(m.get("corrected_ttr", 0) for m in all_metrics) / len(messages),
            
            # Readability metrics (academic standard - Flesch)
            "avg_flesch_reading_ease": sum(m.get("flesch_reading_ease", 0) for m in all_metrics) / len(messages),
            "avg_flesch_kincaid_grade": sum(m.get("flesch_kincaid_grade", 0) for m in all_metrics) / len(messages),
            
            # Linguistic features (totals)
            "total_questions": sum(m["question_count"] for m in all_metrics),
            "total_exclamations": sum(m["exclamation_count"] for m in all_metrics),
            "total_number_mentions": sum(m["number_mentions"] for m in all_metrics),
            "total_dollar_mentions": sum(m["dollar_mentions"] for m in all_metrics)
        }


if __name__ == "__main__":
    # Test the metrics with a sample negotiation message
    test_message = "Hello! Thanks for your interest in the 2018 Honda Civic. I'm asking for $850. What do you think?"
    
    print("=" * 60)
    print("LANGUAGE METRICS TEST")
    print("=" * 60)
    print(f"\nTest message: \"{test_message}\"\n")
    
    metrics = LanguageMetrics.calculate_metrics(test_message)
    
    print("📊 BASIC COUNTS:")
    print(f"  Word count: {metrics['word_count']}")
    print(f"  Sentence count: {metrics['sentence_count']}")
    print(f"  Character count: {metrics['character_count']}")
    
    print("\n📝 COMPLEXITY MEASURES:")
    print(f"  Avg word length: {metrics['avg_word_length']:.2f} characters")
    print(f"  Avg sentence length: {metrics['avg_sentence_length']:.1f} words")
    
    print("\n🎯 VOCABULARY DIVERSITY (TTR):")
    print(f"  Basic TTR: {metrics['vocabulary_richness']:.3f}")
    print(f"    → Interpretation: {metrics['vocabulary_richness']*100:.1f}% of words are unique")
    if metrics.get('root_ttr', 0) > 0:
        print(f"  Root TTR: {metrics['root_ttr']:.3f} (length-normalized)")
        print(f"  Corrected TTR: {metrics['corrected_ttr']:.3f} (length-independent)")
    
    print("\n💡 LINGUISTIC FEATURES:")
    print(f"  Questions: {metrics['question_count']}")
    print(f"  Exclamations: {metrics['exclamation_count']}")
    print(f"  Dollar mentions: {metrics['dollar_mentions']}")
    print(f"  Number mentions: {metrics['number_mentions']}")
    
    print("\n📖 READABILITY (FLESCH METRICS - ACADEMIC STANDARD):")
    flesch_ease = metrics['flesch_reading_ease']
    flesch_grade = metrics['flesch_kincaid_grade']
    
    print(f"  Flesch Reading Ease: {flesch_ease:.1f}/100")
    if flesch_ease >= 90:
        print(f"    → Very Easy (5th grade level)")
    elif flesch_ease >= 80:
        print(f"    → Easy (6th grade level)")
    elif flesch_ease >= 70:
        print(f"    → Fairly Easy (7th grade level)")
    elif flesch_ease >= 60:
        print(f"    → Standard (8th-9th grade level)")
    elif flesch_ease >= 50:
        print(f"    → Fairly Difficult (10th-12th grade level)")
    elif flesch_ease >= 30:
        print(f"    → Difficult (College level)")
    else:
        print(f"    → Very Difficult (College graduate level)")
    
    print(f"\n  Flesch-Kincaid Grade: {flesch_grade:.1f}")
    print(f"    → U.S. Grade Level: {int(flesch_grade)}th grade")
    
    print("\n📚 CITATIONS:")
    print("  Flesch, R. (1948). A new readability yardstick.")
    print("  Kincaid et al. (1975). Derivation of new readability formulas.")
    
    print("\n" + "=" * 60)
