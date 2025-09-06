from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools
from agno.knowledge.url import UrlKnowledge
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.embedder.openai import OpenAIEmbedder
from agno.reranker.cohere import CohereReranker
from agno.memory.agent import AgentMemory
from config import (
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL,
    OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL,
    COHERE_API_KEY, SERPER_API_KEY
)
from agents.serper_client import SerperAPIClient
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SerperEnhancedSearchAgent:
    def __init__(self):
        # Initialize Serper client
        self.serper_client = SerperAPIClient() if SERPER_API_KEY else None
        
        # Initialize knowledge base
        self.knowledge = self._create_knowledge_base()
        
        # Create primary agent with OpenRouter
        self.primary_agent = self._create_agent(
            name="Serper Enhanced Search (Primary)",
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            model=OPENROUTER_MODEL
        )
        
        # Create fallback agent with OpenAI
        self.fallback_agent = self._create_agent(
            name="Serper Enhanced Search (Fallback)",
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL,
            model=OPENAI_MODEL
        )
        
        # Track which agent is active
        self.active_agent = self.primary_agent
        self.using_fallback = False
    
    def _create_agent(self, name, api_key, base_url, model):
        """Create an agent with the specified configuration."""
        return Agent(
            name=name,
            role="Provide accurate, unbiased search results with Serper API enhancement",
            model=OpenAIChat(
                id=model,
                api_key=api_key,
                base_url=base_url
            ),
            memory=AgentMemory(),
            knowledge=self.knowledge,
            tools=[
                DuckDuckGoTools(),
                ReasoningTools(add_instructions=True)
            ],
            instructions=[
                "Search comprehensively across sources including Serper API results",
                "Use reasoning to analyze results",
                "Never make up information",
                "Cite sources for all claims",
                "Provide confidence scores for responses",
                "Prioritize verified information from authoritative sources"
            ],
            show_tool_calls=True,
            markdown=True
        )
    
    def _extract_content(self, response):
        """Extract content from RunResponse or return string representation."""
        if hasattr(response, 'content'):
            return response.content
        return str(response)
    
    def _create_knowledge_base(self):
        """Create knowledge base with hybrid search."""
        return UrlKnowledge(
            urls=[
                "https://en.wikipedia.org/wiki/Web_search_engine",
                "https://en.wikipedia.org/wiki/Information_retrieval"
            ],
            vector_db=LanceDb(
                uri="./data/knowledge",
                table_name="search_kb",
                search_type=SearchType.hybrid,
                embedder=OpenAIEmbedder(
                    id="text-embedding-3-small",
                    api_key=OPENROUTER_API_KEY,  # Use OpenRouter for embeddings
                    base_url=OPENROUTER_BASE_URL
                ),
                reranker=CohereReranker(
                    model="rerank-english-v3.0",
                    api_key=COHERE_API_KEY
                )
            )
        )
    
    def _execute_with_fallback(self, prompt):
        """Execute a prompt with fallback to OpenAI if OpenRouter fails."""
        try:
            logger.info("Attempting to use primary LLM (OpenRouter)")
            self.active_agent = self.primary_agent
            self.using_fallback = False
            result = self.primary_agent.run(prompt)
            logger.info("Successfully executed with primary LLM")
            return result
        except Exception as primary_error:
            logger.warning(f"Primary LLM failed: {str(primary_error)}")
            try:
                logger.info("Falling back to secondary LLM (OpenAI)")
                self.active_agent = self.fallback_agent
                self.using_fallback = True
                result = self.fallback_agent.run(prompt)
                logger.info("Successfully executed with fallback LLM")
                return result
            except Exception as fallback_error:
                logger.error(f"Both primary and fallback LLMs failed: {str(fallback_error)}")
                raise Exception(f"Both LLM providers failed. Primary: {str(primary_error)}. Fallback: {str(fallback_error)}")
    
    def _get_serper_results(self, query: str, num_results: int = 10):
        """Get enhanced search results from Serper API."""
        if not self.serper_client:
            logger.warning("Serper API key not configured, skipping Serper search")
            return []
        
        try:
            logger.info(f"Fetching Serper results for query: {query}")
            results = self.serper_client.get_organic_search_results(query, num_results)
            logger.info(f"Retrieved {len(results)} results from Serper")
            return results
        except Exception as e:
            logger.error(f"Failed to fetch Serper results: {str(e)}")
            return []
    
    def _format_serper_results(self, results: list) -> str:
        """Format Serper results for inclusion in prompts."""
        if not results:
            return "No additional search results available."
        
        formatted_results = []
        for i, result in enumerate(results[:5], 1):  # Limit to top 5 results
            title = result.get("title", "No title")
            snippet = result.get("snippet", "No description")
            link = result.get("link", "No link")
            formatted_results.append(f"{i}. {title}\n   {snippet}\n   Source: {link}\n")
        
        return "Enhanced Search Results:\n" + "\n".join(formatted_results)
    
    def search(self, query: str, use_reasoning: bool = True):
        """Execute enhanced search with Serper API integration."""
        # Get Serper results
        serper_results = self._get_serper_results(query)
        formatted_serper_results = self._format_serper_results(serper_results)
        
        if use_reasoning:
            # First, use reasoning to understand query
            reasoning_prompt = f"""
            Analyze this search query and identify key concepts: {query}
            
            Additional context from enhanced search:
            {formatted_serper_results}
            """
            try:
                analysis = self._execute_with_fallback(reasoning_prompt)
            except Exception as e:
                logger.error(f"Reasoning step failed: {str(e)}")
                # If reasoning fails, proceed with direct search
                direct_prompt = f"""
                Search for: {query}
                
                Additional context from enhanced search:
                {formatted_serper_results}
                
                Provide comprehensive, accurate results with confidence scores.
                """
                return self._execute_with_fallback(direct_prompt)
            
            # Then search with enhanced understanding
            search_prompt = f"""
            Based on this analysis: {self._extract_content(analysis)}
            
            Now search for: {query}
            
            Additional context from enhanced search:
            {formatted_serper_results}
            
            Provide comprehensive, accurate results with confidence scores.
            Prioritize information from the enhanced search results when relevant.
            """
            return self._execute_with_fallback(search_prompt)
        else:
            direct_prompt = f"""
            Search for: {query}
            
            Additional context from enhanced search:
            {formatted_serper_results}
            
            Provide comprehensive, accurate results with confidence scores.
            """
            return self._execute_with_fallback(direct_prompt)

# Quick test
if __name__ == "__main__":
    agent = SerperEnhancedSearchAgent()
    result = agent.search("latest AI developments in 2024")
    print(result)