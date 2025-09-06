from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools
from config import (
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL,
    OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
)
from agents.personalization import PersonalizedSmartSearch
from agents.jira_integration import AgentTaskManager
from agents.serper_client import SerperAPIClient
from agents.api_failover import api_failover
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentTeam:
    """Orchestrate multiple agents for enhanced search capabilities."""
    
    def __init__(self):
        # Initialize team coordinator
        self.coordinator = Agent(
            name="Team Coordinator",
            role="Orchestrate multiple agents for enhanced search",
            model=OpenAIChat(
                id=OPENROUTER_MODEL,
                api_key=OPENROUTER_API_KEY,
                base_url=OPENROUTER_BASE_URL
            ),
            tools=[
                ReasoningTools(add_instructions=True)
            ],
            instructions=[
                "Analyze query intent and select appropriate agents",
                "Coordinate between different specialized agents",
                "Synthesize results from multiple agents",
                "Ensure quality and accuracy of final output",
                "Manage agent workflows and task delegation"
            ]
        )
        
        # Initialize specialized agents
        self.search_agent = PersonalizedSmartSearch()
        self.task_manager = AgentTaskManager()
        self.serper_client = SerperAPIClient() if api_failover.get_available_apis("search") else None
        
        # Track team activities
        self.activities = []
    
    def _extract_content(self, response):
        """Extract content from RunResponse or return string representation."""
        if hasattr(response, 'content'):
            return response.content
        return str(response)
    
    def _analyze_query_intent(self, query: str, user_id: str = "default"):
        """
        Analyze query intent to determine which agents to use.
        
        Args:
            query (str): Search query
            user_id (str): User identifier
            
        Returns:
            dict: Intent analysis results
        """
        intent_prompt = f"""
        Analyze this search query and determine the best approach:
        
        Query: {query}
        User ID: {user_id}
        
        Consider:
        1. Query type (factual, opinion, creative, technical, etc.)
        2. Required search depth
        3. Need for personalization
        4. Specialized tools needed
        5. Confidence requirements
        
        Return a JSON object with:
        - query_type: category of the query
        - complexity: simple/medium/complex
        - required_agents: list of agents needed
        - search_strategy: approach to take
        - confidence_threshold: minimum acceptable confidence
        """
        
        try:
            analysis = self.coordinator.run(intent_prompt)
            return analysis
        except Exception as e:
            logger.warning(f"Intent analysis failed: {str(e)}")
            # Default analysis
            return {
                "query_type": "general",
                "complexity": "medium",
                "required_agents": ["search"],
                "search_strategy": "comprehensive",
                "confidence_threshold": 70
            }
    
    def _coordinate_agents(self, query: str, user_id: str = "default", intent_analysis: dict = None):
        """
        Coordinate multiple agents to handle the query.
        
        Args:
            query (str): Search query
            user_id (str): User identifier
            intent_analysis (dict): Results from intent analysis
            
        Returns:
            dict: Coordinated results
        """
        results = {
            "primary": None,
            "secondary": [],
            "synthesis": None,
            "confidence": 0
        }
        
        try:
            # Execute primary search
            logger.info("Executing primary search")
            primary_result = self.search_agent.search(query, user_id)
            results["primary"] = primary_result
            results["confidence"] = primary_result.get("confidence", 0)
            
            # Get additional context from Serper if available
            if self.serper_client and intent_analysis:
                try:
                    logger.info("Fetching additional context from Serper")
                    serper_results = self.serper_client.get_organic_search_results(
                        query, 
                        num_results=5
                    )
                    
                    # Add Serper context to results
                    results["secondary"].append({
                        "source": "serper",
                        "results": serper_results,
                        "timestamp": __import__('datetime').datetime.now().isoformat()
                    })
                except Exception as e:
                    logger.warning(f"Serper context fetching failed: {str(e)}")
            
            # Synthesize results if needed
            if results["secondary"]:
                synthesis_prompt = f"""
                Synthesize these search results:
                
                Primary Results:
                {self._extract_content(results['primary'])}
                
                Secondary Context:
                {results['secondary']}
                
                Query: {query}
                
                Provide a comprehensive answer that combines all information
                while maintaining accuracy and citing sources.
                """
                
                try:
                    synthesis = self.coordinator.run(synthesis_prompt)
                    results["synthesis"] = self._extract_content(synthesis)
                except Exception as e:
                    logger.warning(f"Result synthesis failed: {str(e)}")
                    results["synthesis"] = self._extract_content(results['primary'])
            
            return results
            
        except Exception as e:
            logger.error(f"Agent coordination failed: {str(e)}")
            raise Exception(f"Agent coordination failed: {str(e)}")
    
    def search(self, query: str, user_id: str = "default"):
        """
        Execute a coordinated search using multiple agents.
        
        Args:
            query (str): Search query
            user_id (str): User identifier
            
        Returns:
            dict: Final search results
        """
        # Log activity
        activity = {
            "type": "search",
            "query": query,
            "user_id": user_id,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        self.activities.append(activity)
        
        # Create Jira task for the search
        jira_task = self.task_manager.create_search_task(query, user_id)
        task_key = jira_task.get("key") if jira_task else None
        
        try:
            # Analyze query intent
            intent_analysis = self._analyze_query_intent(query, user_id)
            logger.info(f"Intent analysis: {intent_analysis}")
            
            # Coordinate agents
            coordinated_results = self._coordinate_agents(query, user_id, intent_analysis)
            
            # Prepare final results
            if coordinated_results["synthesis"]:
                final_results = coordinated_results["synthesis"]
            elif coordinated_results["primary"]:
                final_results = coordinated_results["primary"]
            else:
                final_results = {"results": "No results found", "confidence": 0}
            
            # Ensure consistent result format
            if isinstance(final_results, dict):
                result_dict = final_results.copy()
                if task_key:
                    result_dict["task_key"] = task_key
            else:
                result_dict = {
                    "results": self._extract_content(final_results),
                    "verification": "Coordinated agent search",
                    "confidence": coordinated_results["confidence"],
                    "task_key": task_key
                }
            
            # Update Jira task with results
            if task_key:
                self.task_manager.update_task_with_results(task_key, result_dict)
            
            # Log successful activity
            self.task_manager.log_agent_activity(
                "Successful coordinated search",
                {
                    "query": query,
                    "user_id": user_id,
                    "confidence": result_dict.get("confidence", 0),
                    "task_key": task_key
                }
            )
            
            return result_dict
            
        except Exception as e:
            # Log failed activity
            self.task_manager.log_agent_activity(
                "Failed coordinated search",
                {
                    "query": query,
                    "user_id": user_id,
                    "error": str(e)
                }
            )
            
            # Return fallback result
            return {
                "results": f"Search failed: {str(e)}",
                "verification": "Error occurred during search",
                "confidence": 0,
                "error": True
            }
    
    def get_team_status(self):
        """
        Get the current status of the agent team.
        
        Returns:
            dict: Team status information
        """
        available_apis = {
            "llm": [api["name"] for api in api_failover.get_available_apis("llm")],
            "search": [api["name"] for api in api_failover.get_available_apis("search")],
            "reranker": [api["name"] for api in api_failover.get_available_apis("reranker")]
        }
        
        return {
            "team_members": ["coordinator", "search_agent", "task_manager"],
            "available_apis": available_apis,
            "activities_count": len(self.activities),
            "jira_integration": self.task_manager.jira is not None
        }

# Example usage
if __name__ == "__main__":
    # This would require valid API keys to run
    try:
        team = AgentTeam()
        # status = team.get_team_status()
        # print(json.dumps(status, indent=2))
    except Exception as e:
        print(f"Error: {e}")