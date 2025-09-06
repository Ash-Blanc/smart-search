from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools
from agno.tools.duckduckgo import DuckDuckGoTools
from config import (
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL,
    OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
)
from agents.enhanced_search_agent import EnhancedSmartSearchAgent
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedVerificationAgent:
    def __init__(self):
        # Create verification agent with primary/fallback LLM support
        self.primary_agent = self._create_verification_agent(
            name="Fact Checker (Primary)",
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            model=OPENROUTER_MODEL
        )
        
        self.fallback_agent = self._create_verification_agent(
            name="Fact Checker (Fallback)",
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL,
            model=OPENAI_MODEL
        )
        
        self.active_agent = self.primary_agent
        self.using_fallback = False
    
    def _create_verification_agent(self, name, api_key, base_url, model):
        """Create a verification agent with the specified configuration."""
        return Agent(
            name=name,
            role="Verify information accuracy with primary/fallback LLM support",
            model=OpenAIChat(
                id=model,
                api_key=api_key,
                base_url=base_url
            ),
            tools=[
                ReasoningTools(add_instructions=True),
                DuckDuckGoTools()
            ],
            instructions=[
                "Cross-check facts from multiple sources",
                "Flag any inconsistencies",
                "Return confidence scores",
                "Be skeptical of unsupported claims",
                "Provide detailed verification reports"
            ]
        )
    
    def _extract_content(self, response):
        """Extract content from RunResponse or return string representation."""
        if hasattr(response, 'content'):
            return response.content
        return str(response)
    
    def _execute_with_fallback(self, prompt):
        """Execute a prompt with fallback to OpenAI if OpenRouter fails."""
        try:
            logger.info("Attempting to use primary LLM (OpenRouter) for verification")
            self.active_agent = self.primary_agent
            self.using_fallback = False
            result = self.primary_agent.run(prompt)
            logger.info("Successfully executed verification with primary LLM")
            return result
        except Exception as primary_error:
            logger.warning(f"Primary LLM failed for verification: {str(primary_error)}")
            try:
                logger.info("Falling back to secondary LLM (OpenAI) for verification")
                self.active_agent = self.fallback_agent
                self.using_fallback = True
                result = self.fallback_agent.run(prompt)
                logger.info("Successfully executed verification with fallback LLM")
                return result
            except Exception as fallback_error:
                logger.error(f"Both primary and fallback LLMs failed for verification: {str(fallback_error)}")
                raise Exception(f"Both LLM providers failed for verification. Primary: {str(primary_error)}. Fallback: {str(fallback_error)}")
    
    def verify(self, content: str, sources: list = None):
        """Verify content accuracy with primary/fallback LLM support."""
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
        - Detailed explanation
        """
        
        return self._execute_with_fallback(prompt)
    
    def check_hallucination(self, response: str, original_query: str):
        """Check if response contains hallucinations with primary/fallback LLM support."""
        # Extract content from RunResponse if needed
        response_content = self._extract_content(response)
        
        prompt = f"""
        Original query: {original_query}
        Response: {response_content}
        
        Analyze if the response:
        1. Answers the actual question asked
        2. Makes unsupported claims
        3. Invents facts or sources
        4. Stays within scope of query
        
        Return: 
        - Is this hallucination-free? (Yes/No)
        - Confidence score (0-100)
        - Detailed explanation
        - Specific issues found (if any)
        """
        
        return self._execute_with_fallback(prompt)

# Enhanced anti-hallucination wrapper
class EnhancedAntiHallucinationSearch:
    def __init__(self):
        self.search_agent = EnhancedSmartSearchAgent()
        self.verifier = EnhancedVerificationAgent()
    
    def search(self, query: str):
        """Search with enhanced verification and primary/fallback LLM support."""
        # Get initial results
        results = self.search_agent.search(query)
        
        # Extract content from RunResponse if needed
        results_content = self.verifier._extract_content(results)
        
        # Verify results
        verification = self.verifier.check_hallucination(results_content, query)
        
        # Extract content from verification RunResponse if needed
        verification_content = self.verifier._extract_content(verification)
        
        # If issues found, retry with stricter prompt
        if "No" in verification_content or "no" in verification_content:
            logger.info("Hallucination detected, retrying with stricter prompt")
            strict_prompt = f"""
            Previous search had accuracy issues: {verification_content}
            
            Search again for: {query}
            
            This time:
            - Only include verified information
            - Explicitly cite every source
            - Say "Information not found" if uncertain
            - Provide confidence scores for all claims
            """
            results = self.search_agent._execute_with_fallback(strict_prompt)
            results_content = self.verifier._extract_content(results)
        
        return {
            "results": results_content,
            "verification": verification_content,
            "confidence": self._extract_confidence(verification_content),
            "using_fallback": self.search_agent.using_fallback or self.verifier.using_fallback
        }
    
    def _extract_confidence(self, verification):
        """Extract confidence score from verification response."""
        # Extract content from RunResponse if needed
        verification_content = self.verifier._extract_content(verification)
        
        # Try to extract confidence score from the response
        import re
        confidence_match = re.search(r'[Cc]onfidence.*?(\d+)', verification_content)
        if confidence_match:
            return int(confidence_match.group(1))
        
        # Simple confidence extraction based on verification status
        if "Yes" in verification_content or "yes" in verification_content:
            return 95
        elif "Partial" in verification_content or "partial" in verification_content:
            return 70
        else:
            return 50