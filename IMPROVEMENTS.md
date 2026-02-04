# 🔧 Negotiation Logic Improvements

## Problems Identified:
1. ❌ Agents were **inconsistent** (Seller offering $675, then $680, then back to $700)
2. ❌ Agents **repeating positions** without real negotiation
3. ❌ **Weak model** (gpt-4o-mini) couldn't handle complex reasoning
4. ❌ **No memory** of previous offers
5. ❌ Scenario was **too complex** with too much information

## Solutions Implemented:

### 1. ✅ Price Offer Tracking
- **What**: Agent now tracks ALL previous price offers
- **Why**: Prevents inconsistency (can't offer $700 after offering $675)
- **How**: 
  - Extracts prices from messages using regex
  - Stores in `my_price_offers` list
  - Shows agent their previous offers in the prompt

### 2. ✅ Consistency Rules
- **What**: Explicit rules preventing backwards negotiation
- **Why**: Seller can't offer lower after offering higher (and vice versa)
- **Rule for Seller**: 
  - "Your lowest offer so far is $675"
  - "You MUST NOT offer lower than $675"
- **Rule for Buyer**:
  - "Your highest offer so far is $650"
  - "You MUST NOT offer higher than $650"

### 3. ✅ Better Model
- **Changed**: `gpt-4o-mini` → `gpt-4-turbo`
- **Why**: Better reasoning, better instruction following
- **Cost**: More expensive but MUCH better results
- **Alternative**: Can also use `gpt-4` or `claude-3-opus`

### 4. ✅ Simplified Scenario
- **What**: Removed extra info (urgency reasons, bottom lines, etc.)
- **Why**: Too much information confused the agents
- **Now**: Just the essentials:
  - Seller: min $600, ideal $750
  - Buyer: max $800, ideal $650

### 5. ✅ Enhanced Prompts
- **What**: Added explicit sections showing:
  - "YOUR PREVIOUS OFFERS"
  - "CONSISTENCY RULE"
  - Clear reminder of role (Seller vs Buyer)
- **Why**: LLMs need very explicit instructions

## Files Modified:
1. `agents/agent.py`
   - Added `_extract_price_from_message()` method
   - Added `my_price_offers` tracking
   - Passes offers to prompt builder

2. `personas/persona_manager.py`
   - Added `my_previous_offers` parameter
   - Added "YOUR PREVIOUS OFFERS" section
   - Added "CONSISTENCY RULE" with min/max constraints

3. `config/config.py`
   - Changed default model to `gpt-4-turbo`

4. `scenarios/used_car_sale.json`
   - Simplified agent secrets
   - Removed confusing fields

5. `env.template`
   - Updated recommended model

## Expected Results:
✅ Agents will negotiate **consistently**
✅ Seller will start high and come down gradually
✅ Buyer will start low and go up gradually  
✅ No more jumping back and forth between prices
✅ More realistic negotiation patterns

## Testing:
1. Restart the Streamlit app (it's already running)
2. Refresh your browser at http://localhost:8501
3. Run a new negotiation with:
   - Scenario: Used Car Sale
   - Agent A: Any persona
   - Agent B: Any persona
4. Watch for consistent price movements!

## Cost Considerations:
- **gpt-4o-mini**: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- **gpt-4-turbo**: ~$10 per 1M input tokens, ~$30 per 1M output tokens
- **Per negotiation**: ~2000-3000 tokens → ~$0.05-0.10 with gpt-4-turbo

**Recommendation**: Use `gpt-4-turbo` for your project. It's worth the cost for quality results.

## If Results Are Still Bad:
1. Try `claude-3-opus-20240229` (Anthropic - sometimes better at instructions)
2. Increase `temperature` to 0.5 (more focused responses)
3. Add more examples in the prompt
4. Test with "Fair" persona first (easiest to work with)

## Model Comparison for Your Project:

| Model | Quality | Cost | Recommendation |
|-------|---------|------|----------------|
| gpt-4o-mini | ⭐⭐ | 💰 | ❌ Too weak |
| gpt-4-turbo | ⭐⭐⭐⭐ | 💰💰💰 | ✅ Best choice |
| gpt-4 | ⭐⭐⭐⭐ | 💰💰💰 | ✅ Also good |
| claude-3-opus | ⭐⭐⭐⭐⭐ | 💰💰💰💰 | ✅ Best quality |
| claude-3-sonnet | ⭐⭐⭐ | 💰💰 | ⚠️ OK backup |

**For your professor's requirements**: Use `gpt-4-turbo` or `claude-3-opus`
