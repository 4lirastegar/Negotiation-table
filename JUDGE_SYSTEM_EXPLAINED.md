# 🕵️ The Judge System Explained

## 🎯 **What is the Judge?**

The **Judge** is an **LLM-based adjudicator** that analyzes completed negotiations to determine outcomes. Think of it as a third-party referee that reads the entire conversation and makes an objective assessment.

---

## 🔍 **How It Works**

### **Step 1: Negotiation Completes**
After all rounds finish (or early agreement detected), the system calls the Judge:

```python
# In realtime_negotiation.py (lines 111-118)
judge = Judge()
judge_analysis = judge.analyze_negotiation(
    messages=messages,                    # All conversation messages
    scenario_info=agent_a.scenario_public_info,
    agent_a_secrets=agent_a.agent_secrets,  # Private constraints
    agent_b_secrets=agent_b.agent_secrets,
    scenario_type="price_negotiation"
)
```

### **Step 2: Judge Prompt**
The Judge receives a special prompt with:

1. **Full Transcript** - All messages from both agents
2. **Agent Secrets** - Their private min/max prices (to evaluate satisfaction)
3. **Task** - Determine if agreement was reached and who won

**Example Judge Prompt:**
```
======================================================================
YOU ARE A NEGOTIATION ADJUDICATOR
======================================================================

Your task is to analyze a negotiation transcript and determine:
1. Was an agreement reached?
2. What were the agreed terms (if any)?
3. Who 'won' or benefited more?
4. Why did the negotiation succeed or fail?

======================================================================
AGENT SECRETS (for reference):
======================================================================
Agent A Secrets:
{
  "role": "Seller",
  "minimum_acceptable_price": 600,
  "ideal_price": 750
}

Agent B Secrets:
{
  "role": "Buyer",
  "maximum_budget": 800,
  "ideal_price": 650
}

======================================================================
NEGOTIATION TRANSCRIPT:
======================================================================
[Round 1] Agent A (Aggressive):
  I'm looking to get $850 for it...

[Round 2] Agent B (Fair):
  Would you feel about $650?

[... all messages ...]

======================================================================
YOUR ANALYSIS:
======================================================================

Provide your analysis in JSON format:
{
  "agreement_reached": true/false,
  "agreement_terms": { "price": 715 },
  "winner": "Agent A" / "Agent B" / "Both" / "Neither",
  "reasoning": "Detailed explanation...",
  "agent_a_satisfaction": "high/medium/low",
  "agent_b_satisfaction": "high/medium/low"
}
```

### **Step 3: LLM Response**
The Judge (GPT-4) reads everything and responds with JSON:

```json
{
  "agreement_reached": true,
  "agreement_terms": { "price": 715 },
  "winner": "Both",
  "reasoning": "Agreement reached at $715. Both agents made concessions...",
  "agent_a_satisfaction": "medium",
  "agent_b_satisfaction": "medium"
}
```

### **Step 4: Term Extraction**
The system also uses regex to extract the agreed price from the messages as a backup:

```python
# In judge.py (_extract_agreement_terms method)
# Looks for price patterns in messages with agreement language
# Example: "I agree to $715" → extracts 715
```

---

## 🐛 **The Bug (FIXED)**

### **Problem:**
The price extraction regex was finding "2018" from "2018 Honda Civic" and treating it as the agreed price!

```python
# OLD CODE (line 304)
numbers = re.findall(r'\b(\d{3,4})\b', message)  # Matches ANY 3-4 digit number
# Oops! Matched "2018" from "2018 Honda Civic"
```

### **Fix:**
Now it:
1. **First tries** to find prices with context words ("at", "for", "price", "offer")
2. **Filters out** year-like numbers (2000-2030)
3. **Only then** looks for standalone numbers

```python
# NEW CODE
context_prices = re.findall(r'(?:at|for|of|price|pay|offer)\s+\$?(\d{3,4})\b', message)
# Or filter out years:
filtered_numbers = [n for n in all_numbers if not (2000 <= int(n) <= 2030)]
```

---

## 🎯 **Why Use a Judge?**

### **Academic Justification:**

1. **Objective Evaluation**
   - Consistent assessment across all negotiations
   - No human bias
   - Can evaluate hundreds of negotiations

2. **Mirrors Research Standards**
   - Facebook paper also had agreement detection
   - Standard practice in multi-agent research
   - Allows for quantitative metrics

3. **Handles Ambiguity**
   - Sometimes agents reach implicit agreement
   - Sometimes they use different words
   - LLM Judge can understand context

### **Alternative Approaches:**

| Approach | Pros | Cons |
|----------|------|------|
| **Rule-based** | Fast, deterministic | Can't handle nuance |
| **Human evaluation** | Most accurate | Expensive, not scalable |
| **LLM Judge** | Scalable, context-aware | Costs API calls, can make mistakes |

---

## 📊 **Judge Output Interpretation**

### **Agreement Reached: True**
- Both agents explicitly agreed
- Same terms mentioned by both
- Clear acceptance language used

**Example:**
```
Agent A: "I can agree to $715"
Agent B: "Thank you for agreeing to $715"
→ Agreement = TRUE, Price = $715
```

### **Winner Determination**

The Judge evaluates who got closer to their ideal:

| Outcome | Agent A Satisfaction | Agent B Satisfaction | Winner |
|---------|---------------------|---------------------|--------|
| $715 | Medium (ideal: $750, got $715) | Medium (ideal: $650, got $715) | **Both** |
| $625 | Low (near minimum $600) | High (below ideal $650) | **Agent B** |
| $780 | High (above ideal $750) | Low (near max $800) | **Agent A** |

### **Satisfaction Calculation**

```
Agent A (Seller): min=$600, ideal=$750, agreed=$715
Satisfaction = "medium" (got 76% of ideal range)

Agent B (Buyer): max=$800, ideal=$650, agreed=$715
Satisfaction = "medium" (paid 43% above ideal, still 56% below max)
```

---

## 🔬 **For Your Report**

### **Methodology Section:**

> "To objectively evaluate negotiation outcomes, we employ an LLM-based adjudication system. After each negotiation completes, a separate GPT-4 instance analyzes the full transcript, agent constraints, and conversation patterns to determine: (1) whether mutual agreement was reached, (2) the agreed-upon terms, and (3) relative satisfaction levels for each agent. This approach enables consistent, scalable evaluation across all experimental conditions while accounting for linguistic nuance that rule-based systems might miss."

### **Reliability Note:**

> "We validate the Judge's assessments through cross-checking with regex-based term extraction and manual inspection of a sample of negotiations. This multi-method validation ensures accurate outcome classification."

---

## 🧪 **Judge Limitations**

### **Known Issues:**

1. **Cost**: Each judgment requires an API call
2. **Latency**: Takes a few seconds to analyze
3. **Consistency**: Small variations in similar cases possible
4. **Context Window**: Very long negotiations might exceed limits

### **Mitigation:**

- Use lower temperature (0.3) for more consistent judgments
- Validate with regex extraction as backup
- Manual review of edge cases

---

## 💡 **Advanced: Improving the Judge**

### **Potential Enhancements:**

1. **Multi-Judge Consensus**
   - Use 3 judges, take majority vote
   - More reliable but 3x cost

2. **Fine-tuned Judge Model**
   - Train on labeled negotiations
   - More accurate for specific domains

3. **Hybrid Approach**
   - Rule-based for clear cases (explicit "$X agreed")
   - LLM Judge only for ambiguous cases
   - Cheaper and faster

4. **Structured Output**
   - Use OpenAI's JSON mode for guaranteed valid JSON
   - More reliable parsing

---

## 📝 **Summary**

**The Judge:**
- ✅ Is an LLM (GPT-4) analyzing completed negotiations
- ✅ Receives full transcript + agent secrets
- ✅ Determines agreement, terms, and satisfaction
- ✅ Provides objective, scalable evaluation
- ✅ Academically justifiable approach
- ✅ Fixed bug that extracted "2018" as price

**Your negotiation now correctly shows $715 as the agreed price!** 🎉
