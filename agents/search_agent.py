from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools
from agno.knowledge.url import UrlKnowledge
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.embedder.openai import OpenAIEmbedder
from agno.reranker.cohere import CohereReranker
from agno.memory.agent import AgentMemory
from config import OPENAI_API_KEY, COHERE_API_KEY

class SmartSearchAgent:
    def __init__(self):
        # Initialize knowledge base
        self.knowledge = self._create_knowledge_base()
        
        # Create main search agent
        self.agent = Agent(
            name="Smart Search",
            role="Provide accurate, unbiased search results",
            model=OpenAIChat(
                id="gpt-4o-mini",  # Faster & cheaper for hackathon
                api_key=OPENAI_API_KEY,
                base_url="https://openrouter.ai/api/v1"  # OpenRouter endpoint
            ),
            memory=AgentMemory(),
            knowledge=self.knowledge,
            tools=[
                DuckDuckGoTools(),
                ReasoningTools(add_instructions=True)
            ],
            instructions=[
                "Search comprehensively across sources",
                "Use reasoning to analyze results",
                "Never make up information",
                "Cite sources for all claims"
            ],
            show_tool_calls=True,
            markdown=True
        )
    
    def _create_knowledge_base(self):
        """Create knowledge base with hybrid search"""
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
                    api_key=OPENAI_API_KEY,
                    base_url="https://openrouter.ai/api/v1"  # OpenRouter endpoint
                ),
                reranker=CohereReranker(
                    model="rerank-english-v3.0",
                    api_key=COHERE_API_KEY
                )
            )
        )
    
    def search(self, query: str, use_reasoning: bool = True):
        """Execute search with optional reasoning"""
        if use_reasoning:
            # First, use reasoning to understand query
            reasoning_prompt = f"Analyze this search query and identify key concepts: {query}"
            analysis = self.agent.run(reasoning_prompt)
            
            # Then search with enhanced understanding
            search_prompt = f"""
            Based on this analysis: {analysis}
            
            Now search for: {query}
            
            Provide comprehensive, accurate results.
            """
            return self.agent.run(search_prompt)
        else:
            return self.agent.run(query)

# Quick test
if __name__ == "__main__":
    agent = SmartSearchAgent()
    result = agent.search("latest AI developments in 2024")
    print(result)