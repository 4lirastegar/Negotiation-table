# Analysis Tools for Academic Metrics

**Objective, calculable metrics for your scientific report**

---

## 📊 **What We Calculate:**

1. **Agreement Rate**: % of negotiations that reached agreement
2. **Rounds to Convergence**: Average number of rounds until agreement
3. **Utility Scores**: How well each agent achieved their goals (0-1 scale)
4. **Language Complexity**: Word count, readability, vocabulary richness

**All metrics are calculated using standard academic methods, NOT LLM opinions!**

---

## 🚀 **Quick Start:**

### **Step 1: Run Batch Testing**

Run multiple negotiations automatically to collect data:

```bash
cd /Users/ali/Desktop/thesis/nlp
source venv/bin/activate
python analysis/batch_testing.py
```

**What it does:**
- Runs 24 negotiations (8 persona pairs × 3 runs each)
- Tests different persona combinations
- Saves all results to MongoDB
- Shows real-time progress

**Output example:**
```
📊 Testing: Aggressive vs Fair
--------------------------------------------------
  Run 1/3... ✅ Agreement in 7 rounds
  Run 2/3... ✅ Agreement in 6 rounds
  Run 3/3... ❌ No deal in 10 rounds

✅ Agreement rate: 75.0% (18/24)
📊 Average rounds: 7.3
📊 Average rounds to agreement: 6.8
```

---

### **Step 2: Calculate Metrics**

Analyze all negotiation data from MongoDB:

```bash
python analysis/calculate_metrics.py
```

**What it does:**
- Retrieves all negotiations from MongoDB
- Calculates all academic metrics
- Prints formatted results

**Output example:**
```
📊 AGREEMENT RATE
--------------------------------------------------
  Total negotiations: 24
  Agreements: 18
  Disagreements: 6
  Agreement rate: 75.0%

📊 ROUNDS TO CONVERGENCE
--------------------------------------------------
  Average rounds (all): 7.3
  Median rounds (all): 7.0
  Range: 4 - 10
  Average rounds to agreement: 6.8

📊 UTILITY SCORES
--------------------------------------------------
  Agent A average utility: 0.687
  Agent B average utility: 0.543
  Combined average: 0.615

📊 LANGUAGE COMPLEXITY
--------------------------------------------------
  Agent A:
    Avg words per message: 67.3
    Avg word length: 4.52 characters
    Vocabulary richness: 0.756
    Readability score: 62.4/100

  Agent B:
    Avg words per message: 71.2
    Avg word length: 4.48 characters
    Vocabulary richness: 0.762
    Readability score: 64.1/100

📊 PERSONA COMPARISON
--------------------------------------------------
  Aggressive vs Fair (n=3):
    Agreement rate: 100.0%
    Avg rounds: 6.7
    Avg utility A: 0.723
    Avg utility B: 0.501
```

---

## 📁 **File Structure:**

```
analysis/
├── __init__.py              # Package initialization
├── language_metrics.py      # Language complexity calculator
├── batch_testing.py         # Run multiple negotiations
├── calculate_metrics.py     # Analyze MongoDB data
└── README.md               # This file
```

---

## 🔬 **Academic Methods:**

### **1. Agreement Rate**
```python
agreement_rate = (agreements / total_negotiations) * 100
```
Simple percentage calculation.

### **2. Rounds to Convergence**
```python
avg_rounds = sum(rounds_list) / len(rounds_list)
median_rounds = statistics.median(rounds_list)
```
Statistical measures of central tendency.

### **3. Utility Scores**
```python
# Seller utility
utility = (agreed_price - min_price) / (ideal_price - min_price)

# Buyer utility
utility = (max_budget - agreed_price) / (max_budget - ideal_price)
```
Mathematical calculation from value functions.

### **4. Language Complexity**

**Word Count:**
```python
word_count = len(message.split())
```

**Vocabulary Richness (Type-Token Ratio):**
```python
richness = unique_words / total_words
```

**Readability (Flesch Reading Ease):**
```python
score = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
```

**Average Word Length:**
```python
avg_word_length = sum(len(word) for word in words) / len(words)
```

---

## 📚 **For Your Report:**

### **Quantitative Section:**

```markdown
## 4. Results

### 4.1 Agreement Rates

A total of 24 negotiations were conducted across 8 persona pairings.
The overall agreement rate was 75.0% (18/24 negotiations), with a
mean of 7.3 rounds per negotiation (σ=1.8).

Table 1: Agreement Rates by Persona Pairing

| Pairing | n | Agreement Rate | Avg Rounds |
|---------|---|----------------|------------|
| Aggressive vs Fair | 3 | 100% | 6.7 |
| Aggressive vs Aggressive | 3 | 66.7% | 8.3 |
| Fair vs Fair | 3 | 100% | 5.3 |
...

### 4.2 Utility Analysis

Successful negotiations yielded a mean utility of 0.687 (σ=0.143) for
Agent A (seller) and 0.543 (σ=0.156) for Agent B (buyer), suggesting
sellers achieved outcomes closer to their ideal prices on average.

### 4.3 Language Complexity

Agent A used an average of 67.3 words per message with a vocabulary
richness of 0.756, while Agent B averaged 71.2 words per message with
a vocabulary richness of 0.762, indicating slightly more diverse
language use by buyers.
```

---

## 🎯 **Next Steps:**

1. ✅ Run `batch_testing.py` to collect data
2. ✅ Run `calculate_metrics.py` to analyze
3. ⏳ Manually read interesting transcripts
4. ⏳ Create visualizations (charts/graphs)
5. ⏳ Write qualitative analysis
6. ⏳ Statistical significance tests (t-tests, ANOVA)

---

## 💡 **Tips:**

- **Batch Size**: For preliminary testing, 3-5 runs per pair is enough
- **For Report**: Run 10-20 per pair for statistical significance
- **MongoDB**: All data is saved automatically
- **Reproducibility**: Same personas + scenario = comparable results

---

## 📖 **References for Your Report:**

**Language Metrics:**
- Flesch, R. (1948). "A new readability yardstick"
- Type-Token Ratio (TTR): Standard lexical diversity measure

**Negotiation Analysis:**
- Nash, J. (1950). "The Bargaining Problem"
- Lewis et al. (2017). "Deal or No Deal? End-to-End Learning for Negotiation Dialogues"

---

**Questions?** These are all standard academic metrics! ✅
