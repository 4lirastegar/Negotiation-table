# Prompt Engineering: Transition to Minimal Goal-Oriented Prompts

## 🎯 **What Changed (2026-02-05)**

### **Rationale:**
Based on academic requirements and the Facebook "Deal or No Deal?" paper, we transitioned from **explicit rule-based prompts** to **minimal goal-oriented prompts** to allow for emergent negotiation behavior.

---

## 📋 **Comparison**

### **BEFORE: Explicit Rule-Based Prompt**

```
⚠️ CRITICAL: YOUR ROLE ⚠️
YOU ARE THE SELLER.

IMPORTANT RULES:
- You want to SELL the item for the HIGHEST price possible
- You START with a HIGH asking price (your ideal price)
- You negotiate DOWNWARD only if the buyer won't accept your price
- NEVER offer a price LOWER than what the buyer is offering
- If buyer offers $650, you should counter with $700 or higher, NOT lower

EXAMPLE: If buyer offers $650, you say: 'I can do $700' or 'How about $680'
WRONG: If buyer offers $650, you say: 'I can do $500' (this is backwards!)

🚨 CRITICAL CONSISTENCY RULE 🚨
You are the SELLER. Your lowest offer so far is $750.00
You MUST NOT offer a price LOWER than $750.00
You can only offer $750.00 or HIGHER
```

**Characteristics:**
- ❌ Tells agent exactly what to do
- ❌ Provides explicit examples
- ❌ Uses warnings and emojis
- ❌ Prescriptive rules
- ❌ Limits strategic freedom
- ✅ Prevents illogical behavior

---

### **AFTER: Minimal Goal-Oriented Prompt**

```
============================================================
YOUR ROLE: SELLER
============================================================
You are selling the item described below.
Your goal: Sell for the HIGHEST price possible within your acceptable range.

You are an aggressive negotiator.

============================================================
NEGOTIATION CONTEXT:
============================================================
Item: 2018 Honda Civic
Condition: Good condition, 45,000 miles
Features: Bluetooth, Backup camera, Sunroof
Visible Issues: Minor scratches on rear bumper

============================================================
YOUR CONSTRAINTS:
============================================================
Role: Seller
Minimum Acceptable Price: 600
Ideal Price: 750
Urgency: medium

Note: Use this information strategically. You may choose whether to reveal it.

============================================================
YOUR PREVIOUS OFFERS:
============================================================
  Round 1: $750.00

Note: As the seller, your offers typically decrease as you make concessions.

============================================================
CONVERSATION HISTORY (Round 2):
============================================================
Round 1:
  You said: [message]
  The other party said: [message]

============================================================
YOUR TASK:
============================================================
Read the conversation above and respond to the other party's latest message.
Continue negotiating toward an agreement that maximizes your outcome.

Your response (do not include labels like 'Agent A:' or 'Seller:'):
```

**Characteristics:**
- ✅ Clear goals without prescribing methods
- ✅ Allows strategic freedom
- ✅ Enables emergent behavior
- ✅ Minimal consistency hint (not a rule)
- ✅ Academically defensible
- ⚠️ May allow illogical behavior (to be observed)

---

## 🔬 **Research Implications**

### **What We Can Now Claim:**

1. **Emergent Strategies:**
   > "We observe whether negotiation strategies emerge naturally from goal-oriented prompts without explicit instruction."

2. **Genuine Reasoning:**
   > "Agents must reason about negotiation tactics rather than follow scripted rules."

3. **LLM Capabilities:**
   > "We test whether GPT-4 possesses inherent strategic reasoning for economic negotiations."

### **What We Lost:**

1. **Guaranteed Consistency:**
   - Agents may offer illogical prices (e.g., seller lowering below buyer's offer)
   - Need to observe and document when this happens

2. **Predictable Behavior:**
   - More variability in outcomes
   - Some negotiations may fail unexpectedly

### **What We Gained:**

1. **Academic Validity:**
   - Aligns with professor's "emergent behavior" requirement
   - Comparable to Facebook's approach
   - Publishable findings

2. **Interesting Failures:**
   - If agents fail → interesting finding about LLM limitations
   - If agents succeed → impressive demonstration of reasoning

---

## 📊 **Expected Outcomes**

### **Scenario 1: Agents Negotiate Well**
**Result:** Strong evidence that GPT-4 can reason strategically  
**Paper claim:** "Modern LLMs demonstrate emergent negotiation capabilities with minimal guidance"

### **Scenario 2: Agents Make Some Errors**
**Result:** Mixed findings showing both capabilities and limitations  
**Paper claim:** "While GPT-4 shows strategic reasoning, it occasionally produces illogical offers, suggesting..."

### **Scenario 3: Complete Failure**
**Result:** Evidence that LLMs need explicit guidance  
**Paper claim:** "Despite advanced language capabilities, GPT-4 requires structured prompts for consistent economic reasoning"

**All three outcomes are academically valuable!**

---

## 🧪 **Testing Plan**

### **Phase 1: Observe Behavior**
1. Run 20-30 negotiations with minimal prompts
2. Document:
   - Agreement rate
   - Illogical behaviors (count them!)
   - Emergent strategies
   - Differences by persona

### **Phase 2: Analysis**
- Compare to explicit prompt results (if available)
- Identify common failure patterns
- Look for creative strategies

### **Phase 3: Iterate (if needed)**
- If too many failures, add ONE minimal constraint at a time
- Document what works and what doesn't
- This iterative process itself is research!

---

## 📝 **For Your Report**

### **Methodology Section:**

> "We employed minimal goal-oriented prompts inspired by Lewis et al. (2017), providing agents with clear objectives (maximize/minimize price) and constraints (acceptable ranges) while avoiding explicit negotiation instructions. This approach allows us to evaluate whether strategic negotiation behaviors emerge naturally from the model's reasoning capabilities, or whether LLMs require more structured guidance for coherent economic dialogue."

### **Prompt Design Subsection:**

> "Each agent receives:
> 1. Role identification (Buyer or Seller)
> 2. Goal specification (maximize/minimize price)
> 3. Private constraints (acceptable price range)
> 4. Public scenario information (item details)
> 5. Conversation history
> 6. Persona modification (e.g., 'aggressive negotiator')
> 
> Critically, agents are NOT given explicit rules about offer direction (e.g., 'sellers should decrease prices') or negotiation tactics. Instead, these strategies must emerge from the agent's understanding of economic roles and goals."

---

## 🎓 **Discussion Points for Report**

### **If Agents Succeed:**
- "GPT-4 demonstrates understanding of economic roles"
- "Agents adapted strategies based on persona"
- "Emergent behaviors included: [list specific tactics observed]"

### **If Agents Struggle:**
- "LLMs may lack robust models of economic agency"
- "Occasional illogical offers suggest limitations in multi-step strategic reasoning"
- "Trade-off between flexibility and consistency"

### **Key Insight:**
> "The need for explicit prompting in prior experiments may reflect not a limitation of prompt engineering, but rather a genuine gap in current LLMs' economic reasoning capabilities."

---

## 💡 **Next Steps**

1. ✅ Minimal prompts implemented
2. ⏳ Run test negotiations (observe behavior)
3. ⏳ Document all outcomes (good and bad)
4. ⏳ Decide if iteration needed
5. ⏳ Write up findings honestly

**Remember:** Negative results are still valuable results in research!

---

## 📚 **Academic Justification**

This approach aligns with:

1. **Lewis et al. (2017):** Goal-based agents that learn strategies
2. **Professor's requirements:** "Emergent communicative strategies"
3. **AI research standards:** Testing capabilities, not instruction-following

**Your project now has strong academic grounding!** 🎓
