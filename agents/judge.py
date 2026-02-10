"""
Judge/Adjudicator System
Analyzes negotiation transcripts to determine outcomes, agreements, and winners
Uses OpenAI Structured Outputs for guaranteed valid JSON responses
"""

from typing import Dict, List, Any, Optional
from config.config import OPENAI_API_KEY, ANTHROPIC_API_KEY, LLM_PROVIDER, LLM_MODEL
import json
import re

# Define the JSON schema for structured outputs
# ACADEMIC APPROACH: Judge only determines FACTS, not subjective ratings
JUDGE_ANALYSIS_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "negotiation_analysis",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "agreement_reached": {
                    "type": "boolean",
                    "description": "Whether both agents explicitly agreed to the same terms"
                },
                "agreement_terms": {
                    "anyOf": [
                        {
                            "type": "object",
                            "properties": {
                                "price": {
                                    "type": "number",
                                    "description": "The agreed upon price in dollars"
                                }
                            },
                            "required": ["price"],
                            "additionalProperties": False
                        },
                        {
                            "type": "null"
                        }
                    ],
                    "description": "The agreed upon terms (price), or null if no agreement"
                },
                "explanation": {
                    "type": "string",
                    "description": "Brief factual explanation of whether/how agreement was reached"
                }
            },
            "required": ["agreement_reached", "agreement_terms", "explanation"],
            "additionalProperties": False
        }
    }
}

# Lightweight schema for quick agreement checking during negotiation
QUICK_AGREEMENT_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "quick_agreement_check",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "agreement_reached": {
                    "type": "boolean",
                    "description": "Whether both agents explicitly agreed to the same terms"
                },
                "agreed_price": {
                    "anyOf": [
                        {"type": "number"},
                        {"type": "null"}
                    ],
                    "description": "The agreed price, or null if no agreement"
                },
                "explanation": {
                    "type": "string",
                    "description": "Brief explanation of why agreement was or wasn't reached"
                }
            },
            "required": ["agreement_reached", "agreed_price", "explanation"],
            "additionalProperties": False
        }
    }
}


class Judge:
    """Adjudicator that analyzes negotiation outcomes"""
    
    def __init__(self, llm_provider: str = None, llm_model: str = None):
        """
        Initialize the Judge
        
        Args:
            llm_provider: LLM provider to use (openai or anthropic)
            llm_model: Model name to use
        """
        self.llm_provider = llm_provider or LLM_PROVIDER
        
        # For Judge, we need a model that supports structured outputs
        # Use gpt-4o if available, otherwise use the configured model
        if llm_model:
            self.llm_model = llm_model
        elif LLM_MODEL in ["gpt-4-turbo", "gpt-4"]:
            # These models don't support structured outputs, use gpt-4o instead
            self.llm_model = "gpt-4o"
            print("⚠️ Judge: Using gpt-4o for structured outputs support")
        else:
            self.llm_model = LLM_MODEL
        
        self.llm_client = self._initialize_llm_client()
    
    def _initialize_llm_client(self):
        """Initialize the appropriate LLM client"""
        if self.llm_provider == "openai":
            try:
                from openai import OpenAI
                if not OPENAI_API_KEY:
                    raise ValueError("OPENAI_API_KEY not found in environment")
                return OpenAI(api_key=OPENAI_API_KEY)
            except ImportError:
                raise ImportError("openai package not installed")
        
        elif self.llm_provider == "anthropic":
            try:
                from anthropic import Anthropic
                if not ANTHROPIC_API_KEY:
                    raise ValueError("ANTHROPIC_API_KEY not found in environment")
                return Anthropic(api_key=ANTHROPIC_API_KEY)
            except ImportError:
                raise ImportError("anthropic package not installed")
        
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    def check_agreement_quick(
        self,
        message_a: str,
        message_b: str,
        round_num: int
    ) -> Dict[str, Any]:
        """
        Quick check if agreement was reached in the last round
        Uses lightweight structured output for speed
        
        Args:
            message_a: Agent A's most recent message
            message_b: Agent B's most recent message
            round_num: Current round number
            
        Returns:
            Dictionary with agreement_reached (bool), agreed_price (float or None), explanation (str)
        """
        # Build quick check prompt
        prompt = f"""You are a negotiation referee. Analyze these two messages from a negotiation round and determine if BOTH agents explicitly agreed to the SAME terms.

ROUND {round_num}:

Agent A: "{message_a}"

Agent B: "{message_b}"

RULES:
- Only return TRUE if BOTH agents explicitly agreed to the SAME price
- Look for phrases like "I agree to $X", "I accept $X", "deal at $X", "let's finalize at $X"
- If one agent proposes and the other accepts the SAME price → TRUE
- If agents are still counter-offering different prices → FALSE
- If agents are discussing logistics after agreement → still TRUE

Return your analysis in JSON format."""

        try:
            if self.llm_provider == "openai":
                response = self.llm_client.chat.completions.create(
                    model=self.llm_model,
                    temperature=0.1,
                    messages=[
                        {"role": "system", "content": "You are an expert negotiation referee. Be strict: only confirm agreement when BOTH agents explicitly accept the SAME terms."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format=QUICK_AGREEMENT_SCHEMA,
                    max_tokens=150
                )
                result = json.loads(response.choices[0].message.content.strip())
                return result
            
            elif self.llm_provider == "anthropic":
                # Anthropic doesn't support structured outputs, use basic parsing
                response = self.llm_client.messages.create(
                    model=self.llm_model,
                    max_tokens=150,
                    temperature=0.1,
                    system="You are an expert negotiation referee. Return only valid JSON.",
                    messages=[{"role": "user", "content": prompt}]
                )
                result = json.loads(response.content[0].text.strip())
                return result
                
        except Exception as e:
            print(f"Quick agreement check error: {e}")
            return {
                "agreement_reached": False,
                "agreed_price": None,
                "explanation": f"Error during check: {str(e)}"
            }
    
    def analyze_negotiation(
        self,
        messages: List[Dict],
        scenario_info: Dict,
        agent_a_secrets: Dict,
        agent_b_secrets: Dict,
        scenario_type: str = "price_negotiation"
    ) -> Dict[str, Any]:
        """
        Analyze a complete negotiation transcript and determine the outcome
        
        Args:
            messages: List of all messages in the negotiation
            scenario_info: Public scenario information
            agent_a_secrets: Agent A's private information
            agent_b_secrets: Agent B's private information
            scenario_type: Type of scenario (price_negotiation, resource_allocation, etc.)
            
        Returns:
            Dictionary with analysis results
        """
        # Build the analysis prompt
        prompt = self._build_analysis_prompt(
            messages, scenario_info, agent_a_secrets, agent_b_secrets, scenario_type
        )
        
        # Get LLM analysis
        analysis_text = self._call_llm(prompt)
        
        # Parse the analysis
        analysis = self._parse_analysis(analysis_text, scenario_type)
        
        # Extract agreement terms if agreement reached
        if analysis.get("agreement_reached"):
            analysis["agreement_terms"] = self._extract_agreement_terms(
                messages, scenario_type, agent_a_secrets, agent_b_secrets
            )
        else:
            analysis["agreement_terms"] = None
        
        return analysis
    
    def _build_analysis_prompt(
        self,
        messages: List[Dict],
        scenario_info: Dict,
        agent_a_secrets: Dict,
        agent_b_secrets: Dict,
        scenario_type: str
    ) -> str:
        """Build the prompt for the Judge to analyze the negotiation"""
        
        # Format conversation
        conversation_text = self._format_conversation(messages)
        
        # Build prompt - FACTUAL ANALYSIS ONLY
        prompt_parts = []
        prompt_parts.append("=" * 70)
        prompt_parts.append("YOU ARE A FACTUAL NEGOTIATION ANALYZER")
        prompt_parts.append("=" * 70)
        prompt_parts.append("")
        prompt_parts.append("Your task: Determine if an agreement was reached (FACTUAL ONLY)")
        prompt_parts.append("DO NOT provide subjective opinions, ratings, or judgments.")
        prompt_parts.append("")
        
        prompt_parts.append("=" * 70)
        prompt_parts.append("NEGOTIATION TRANSCRIPT:")
        prompt_parts.append("=" * 70)
        prompt_parts.append(conversation_text)
        prompt_parts.append("")
        
        prompt_parts.append("=" * 70)
        prompt_parts.append("YOUR TASK:")
        prompt_parts.append("=" * 70)
        prompt_parts.append("")
        prompt_parts.append("Analyze the transcript and provide FACTUAL output:")
        prompt_parts.append("{")
        prompt_parts.append('  "agreement_reached": true/false,')
        prompt_parts.append('  "agreement_terms": { "price": 712 } or null,')
        prompt_parts.append('  "explanation": "Brief factual summary"')
        prompt_parts.append("}")
        prompt_parts.append("")
        prompt_parts.append("RULES:")
        prompt_parts.append("- Only mark agreement_reached=true if BOTH agents explicitly agreed to SAME price")
        prompt_parts.append("- Look for explicit acceptance: 'I accept', 'I agree', 'deal', 'sold'")
        prompt_parts.append("- Extract the exact agreed price")
        prompt_parts.append("- Keep explanation factual (e.g., 'Both agents accepted $712 in round 7')")
        prompt_parts.append("- NO subjective opinions about who won or satisfaction levels")
        prompt_parts.append("")
        prompt_parts.append("Your analysis (JSON only):")
        
        return "\n".join(prompt_parts)
    
    def _format_conversation(self, messages: List[Dict]) -> str:
        """Format conversation messages for the prompt"""
        lines = []
        for msg in messages:
            agent = msg.get("agent", "Unknown")
            persona = msg.get("persona", "")
            message = msg.get("message", "")
            round_num = msg.get("round", 0)
            
            lines.append(f"[Round {round_num}] {agent} ({persona}):")
            lines.append(f"  {message}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM API with structured outputs (like FishGPT!)"""
        try:
            if self.llm_provider == "openai":
                # Use structured outputs for guaranteed valid JSON!
                response = self.llm_client.chat.completions.create(
                    model=self.llm_model,
                    temperature=0,  # 0 = deterministic for consistency
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert negotiation adjudicator. Analyze negotiations objectively and provide structured analysis."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    response_format=JUDGE_ANALYSIS_SCHEMA,  # Structured output!
                    max_tokens=1000
                )
                # JSON is guaranteed to be valid!
                return response.choices[0].message.content.strip()
            
            elif self.llm_provider == "anthropic":
                # Anthropic doesn't support structured outputs yet, use regular JSON mode
                response = self.llm_client.messages.create(
                    model=self.llm_model,
                    max_tokens=1000,
                    temperature=0.3,
                    system="You are an expert negotiation adjudicator. Analyze negotiations objectively and provide detailed analysis in JSON format.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text.strip()
        
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def _parse_analysis(self, analysis_text: str, scenario_type: str) -> Dict[str, Any]:
        """Parse the LLM's analysis response - much simpler with structured outputs!"""
        try:
            # With structured outputs, JSON is GUARANTEED to be valid!
            # No need for markdown stripping or fallback parsing
            analysis = json.loads(analysis_text)
            
            # Validate required fields (though schema guarantees them)
            if "agreement_reached" not in analysis:
                analysis["agreement_reached"] = False
            
            return analysis
        
        except json.JSONDecodeError:
            # This should rarely happen with structured outputs
            # But keep fallback just in case
            return self._fallback_parse(analysis_text)
    
    def _fallback_parse(self, text: str) -> Dict[str, Any]:
        """Fallback parsing if JSON parsing fails"""
        text_lower = text.lower()
        
        # Try to detect agreement
        agreement_reached = any(phrase in text_lower for phrase in [
            "agreement reached", "deal was reached", "agreed", "successful negotiation"
        ]) and not any(phrase in text_lower for phrase in [
            "no agreement", "failed", "did not reach"
        ])
        
        # Try to detect winner
        winner = "Neither"
        if "agent a" in text_lower and ("won" in text_lower or "benefited" in text_lower):
            winner = "Agent A"
        elif "agent b" in text_lower and ("won" in text_lower or "benefited" in text_lower):
            winner = "Agent B"
        elif "both" in text_lower and ("won" in text_lower or "benefited" in text_lower):
            winner = "Both"
        
        return {
            "agreement_reached": agreement_reached,
            "winner": winner,
            "reasoning": text[:500] if len(text) > 500 else text,
            "agent_a_satisfaction": "medium",
            "agent_b_satisfaction": "medium"
        }
    
    def _extract_agreement_terms(
        self,
        messages: List[Dict],
        scenario_type: str,
        agent_a_secrets: Dict,
        agent_b_secrets: Dict
    ) -> Dict[str, Any]:
        """Extract agreed-upon terms from the conversation"""
        terms = {}
        
        if scenario_type == "price_negotiation":
            # Look for price mentions in the last few messages
            # Check for explicit agreement with price
            for msg in reversed(messages[-6:]):  # Check last 6 messages
                message = msg.get("message", "")
                
                # Look for dollar amounts
                price_pattern = r'\$(\d+(?:\.\d{2})?)'
                prices = re.findall(price_pattern, message)
                
                if prices:
                    # Check if this message contains agreement language
                    msg_lower = message.lower()
                    if any(agree in msg_lower for agree in [
                        "deal", "accept", "agree", "sold", "take it"
                    ]):
                        try:
                            terms["price"] = float(prices[-1])
                            break
                        except ValueError:
                            continue
            
            # If no explicit price found, look for numbers in context of agreement
            if "price" not in terms:
                for msg in reversed(messages[-4:]):
                    message = msg.get("message", "")
                    msg_lower = message.lower()
                    
                    if any(agree in msg_lower for agree in [
                        "deal", "accept", "agree", "sold", "finalize"
                    ]):
                        # Look for prices in context (with $ or words like "at" or "for")
                        # Avoid matching years or model numbers
                        context_prices = re.findall(r'(?:at|for|of|price|pay|offer)\s+\$?(\d{3,4})\b', message, re.IGNORECASE)
                        
                        if context_prices:
                            try:
                                potential_price = float(context_prices[-1])
                                # Check if it's in reasonable range
                                if 100 <= potential_price <= 10000:
                                    terms["price"] = potential_price
                                    break
                            except ValueError:
                                continue
                        else:
                            # If no context price found, try all numbers but exclude "2018" etc
                            all_numbers = re.findall(r'\b(\d{3,4})\b', message)
                            # Filter out year-like numbers (2000-2030 range)
                            filtered_numbers = [n for n in all_numbers if not (2000 <= int(n) <= 2030)]
                            if filtered_numbers:
                                try:
                                    potential_price = float(filtered_numbers[-1])
                                    if 100 <= potential_price <= 10000:
                                        terms["price"] = potential_price
                                        break
                                except ValueError:
                                    continue
        
        return terms
