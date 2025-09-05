from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools
from agno.tools.duckduckgo import DuckDuckGoTools
from config import OPENAI_API_KEY

class VerificationAgent:
    def __init__(self):
        self.agent = Agent(
            name="Fact Checker",
            role="Verify information accuracy",
            model=OpenAIChat(
                id="gpt-4o-mini",
                api_key=OPENAI_API_KEY,
                base_url="https://openrouter.ai/api/v1"  # OpenRouter endpoint
            ),
            tools=[
                ReasoningTools(add_instructions=True),
                DuckDuckGoTools()
            ],
            instructions=[
                "Cross-check facts from multiple sources",
                "Flag any inconsistencies",
                "Return confidence scores",
                "Be skeptical of unsupported claims"
            ]
        )
    
    def verify(self, content: str, sources: list = None):
        """Verify content accuracy"""
        prompt = f"""
        Verify the accuracy of this content:
        {content}
        
        Sources: {sources if sources else 'Not provided'}
        
        Check for:
        1. Factual accuracy
        2. Logical consistency
        3. Source reliability
        4. Potential hallucinations
        
        Return:
        - Verification status (Verified/Unverified/Partial)
        - Confidence score (0-100)
        - Any issues found
        """
        
        return self.agent.run(prompt)
    
    def check_hallucination(self, response: str, original_query: str):
        """Check if response contains hallucinations"""
        prompt = f"""
        Original query: {original_query}
        Response: {response}
        
        Analyze if the response:
        1. Answers the actual question asked
        2. Makes unsupported claims
        3. Invents facts or sources
        4. Stays within scope of query
        
        Return: Is this hallucination-free? (Yes/No) and explain why.
        """
        
        return self.agent.run(prompt)

# Anti-hallucination wrapper
class AntiHallucinationSearch:
    def __init__(self):
        self.search_agent = SmartSearchAgent()
        self.verifier = VerificationAgent()
    
    def search(self, query: str):
        """Search with verification"""
        # Get initial results
        results = self.search_agent.search(query)
        
        # Verify results
        verification = self.verifier.check_hallucination(results, query)
        
        # If issues found, retry with stricter prompt
        if "No" in verification:
            strict_prompt = f"""
            Previous search had accuracy issues: {verification}
            
            Search again for: {query}
            
            This time:
            - Only include verified information
            - Explicitly cite every source
            - Say "Information not found" if uncertain
            """
            results = self.search_agent.agent.run(strict_prompt)
        
        return {
            "results": results,
            "verification": verification,
            "confidence": self._extract_confidence(verification)
        }
    
    def _extract_confidence(self, verification):
        # Simple confidence extraction
        if "Yes" in verification:
            return 95
        elif "Partial" in verification:
            return 70
        else:
            return 50