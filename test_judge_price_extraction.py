"""
Test the updated Judge with price extraction
This verifies that check_agreement_quick() now returns price offers
"""

from agents.judge import Judge

# Initialize Judge
print("Initializing Judge...")
judge = Judge()
print(f"✅ Judge initialized with model: {judge.llm_model}\n")

# Test Case 1: Simple negotiation round
print("=" * 70)
print("TEST CASE 1: Simple negotiation round")
print("=" * 70)

message_a = "I'm selling this car for $900."
message_b = "I can offer $650."

print(f"\nAgent A: {message_a}")
print(f"Agent B: {message_b}\n")

result = judge.check_agreement_quick(message_a, message_b, round_num=1)

print("Judge Analysis:")
print(f"  Agreement Reached: {result['agreement_reached']}")
print(f"  Agreed Price: {result['agreed_price']}")
print(f"  Agent A Offer: ${result['agent_a_offer']}")  # ← NEW FIELD!
print(f"  Agent B Offer: ${result['agent_b_offer']}")  # ← NEW FIELD!
print(f"  Explanation: {result['explanation']}")

# Test Case 2: Multiple prices in message
print("\n" + "=" * 70)
print("TEST CASE 2: Multiple prices (context-awareness test)")
print("=" * 70)

message_a = "I can do $850, or if you prefer, maybe $880, but my real offer is $820."
message_b = "How about $700?"

print(f"\nAgent A: {message_a}")
print(f"Agent B: {message_b}\n")

result = judge.check_agreement_quick(message_a, message_b, round_num=2)

print("Judge Analysis:")
print(f"  Agreement Reached: {result['agreement_reached']}")
print(f"  Agent A Offer: ${result['agent_a_offer']}")  # Should be 820!
print(f"  Agent B Offer: ${result['agent_b_offer']}")  # Should be 700
print(f"  Explanation: {result['explanation']}")

# Test Case 3: Agreement reached
print("\n" + "=" * 70)
print("TEST CASE 3: Agreement reached")
print("=" * 70)

message_a = "Okay, I accept your offer of $775."
message_b = "Great! Deal at $775."

print(f"\nAgent A: {message_a}")
print(f"Agent B: {message_b}\n")

result = judge.check_agreement_quick(message_a, message_b, round_num=5)

print("Judge Analysis:")
print(f"  Agreement Reached: {result['agreement_reached']}")  # Should be TRUE!
print(f"  Agreed Price: ${result['agreed_price']}")  # Should be 775
print(f"  Agent A Offer: {result['agent_a_offer']}")  # Should be None (acceptance, not new offer)
print(f"  Agent B Offer: {result['agent_b_offer']}")  # Should be None
print(f"  Explanation: {result['explanation']}")

# Test Case 4: Year filter (2018 Honda Civic)
print("\n" + "=" * 70)
print("TEST CASE 4: Year filtering (should ignore '2018')")
print("=" * 70)

message_a = "This 2018 Honda Civic is available for $850."
message_b = "I'm interested in the 2018 model. Would you take $750?"

print(f"\nAgent A: {message_a}")
print(f"Agent B: {message_b}\n")

result = judge.check_agreement_quick(message_a, message_b, round_num=1)

print("Judge Analysis:")
print(f"  Agent A Offer: ${result['agent_a_offer']}")  # Should be 850 (not 2018!)
print(f"  Agent B Offer: ${result['agent_b_offer']}")  # Should be 750 (not 2018!)
print(f"  Explanation: {result['explanation']}")

print("\n" + "=" * 70)
print("✅ ALL TESTS COMPLETE!")
print("=" * 70)
print("\n💡 Key Improvements:")
print("  1. ONE API call per round (not two!)")
print("  2. Agreement check + price extraction together")
print("  3. Context-aware (extracts the real offer)")
print("  4. Filters out years and non-offers")
print("  5. No extra cost or latency")
