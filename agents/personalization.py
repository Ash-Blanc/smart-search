from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.memory.agent import AgentMemory
from agno.storage.json import JsonStorage
from config import (
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL,
    OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
)
import json
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersonalizationEngine:
    def __init__(self):
        self.agent = Agent(
            name="Personalization Engine",
            role="Learn user preferences and personalize results",
            model=OpenAIChat(
                id=OPENROUTER_MODEL, 
                api_key=OPENROUTER_API_KEY,
                base_url=OPENROUTER_BASE_URL  # OpenRouter endpoint
            ),
            memory=AgentMemory(),
            storage=JsonStorage("./data/personalization"),  # Use JSON storage for personalization data
            instructions=[
                "Track user search patterns",
                "Build interest profiles",
                "Personalize result rankings",
                "Adapt response tone/style to user preferences"
            ]
        )
        self.user_profiles = {}
    
    def _extract_content(self, response):
        """Extract content from RunResponse or return string representation"""
        if hasattr(response, 'content'):
            return response.content
        return str(response)
    
    def update_profile(self, user_id: str, interaction: dict):
        """Update user profile based on interaction"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "searches": [],
                "clicks": [],
                "interests": [],
                "preferred_tone": "neutral",  # default tone
                "preferred_depth": "standard",  # default depth
                "feedback": [],
                "created": datetime.now().isoformat()
            }
        
        profile = self.user_profiles[user_id]
        
        # Track search
        if "query" in interaction:
            search_record = {
                "query": interaction["query"],
                "timestamp": datetime.now().isoformat(),
                "confidence": interaction.get("confidence", 0)
            }
            profile["searches"].append(search_record)
        
        # Track clicks
        if "clicked_result" in interaction:
            profile["clicks"].append(interaction["clicked_result"])
        
        # Track feedback
        if "feedback" in interaction:
            profile["feedback"].append({
                "feedback": interaction["feedback"],
                "timestamp": datetime.now().isoformat()
            })
        
        # Track preferences
        if "preferred_tone" in interaction:
            profile["preferred_tone"] = interaction["preferred_tone"]
        
        if "preferred_depth" in interaction:
            profile["preferred_depth"] = interaction["preferred_depth"]
        
        # Update interests using agent after 3 searches
        if len(profile["searches"]) >= 3:
            try:
                interests_prompt = f"""
                Based on these recent searches: {profile["searches"][-5:]}
                And clicked results: {profile["clicks"][-5:]}
                And user feedback: {profile["feedback"][-3:]}
                
                Identify top 5 user interests/topics.
                Also determine preferred communication style (formal/casual/technical).
                """
                interests = self.agent.run(interests_prompt)
                # Extract content from RunResponse if needed
                interests_content = self._extract_content(interests)
                profile["interests"] = interests_content
            except Exception as e:
                logger.warning(f"Failed to update interests: {str(e)}")
        
        return profile
    
    def personalize_results(self, user_id: str, search_results: str, query: str = ""):
        """Re-rank and adapt results based on user profile"""
        profile = self.user_profiles.get(user_id, {})
        
        if not profile.get("interests") and not profile.get("preferred_tone"):
            return search_results
        
        # Extract content from search_results if it's a RunResponse
        search_results_content = self._extract_content(search_results)
        
        personalization_prompt = f"""
        User interests: {profile.get('interests', 'Not available')}
        Preferred tone: {profile.get('preferred_tone', 'neutral')}
        Preferred depth: {profile.get('preferred_depth', 'standard')}
        Recent searches: {profile.get('searches', [])[-3:]}
        User feedback: {profile.get('feedback', [])[-2:]}
        
        Adapt and re-rank these search results based on user preferences:
        {search_results_content}
        
        Query: {query}
        
        Instructions:
        1. Re-rank results to match user interests
        2. Adjust tone to user preference
        3. Modify detail level based on preferred depth
        4. Highlight results most relevant to user interests
        5. Maintain factual accuracy
        6. Consider user feedback in personalization
        """
        
        try:
            return self.agent.run(personalization_prompt)
        except Exception as e:
            logger.warning(f"Personalization failed: {str(e)}")
            return search_results_content

# Main search with all features
class PersonalizedSmartSearch:
    def __init__(self):
        # Import here to avoid circular import
        from agents.dspy_optimization import DSPyOptimizedSearchAgent
        self.search_agent = DSPyOptimizedSearchAgent()
        self.personalization = PersonalizationEngine()
    
    def search(self, query: str, user_id: str = "default"):
        """Complete search pipeline with personalization"""
        # Track query
        self.personalization.update_profile(user_id, {"query": query})
        
        # Search with verification and optimization
        search_result = self.search_agent.search(query, user_id)
        
        # Extract content from search results
        search_results_content = self.search_agent.base_agent._extract_content(search_result)
        if isinstance(search_result, dict) and "results" in search_result:
            search_results_content = search_result["results"]
        
        # Personalize if we have user data
        if user_id != "default":
            personalized = self.personalization.personalize_results(
                user_id, 
                search_results_content,
                query
            )
            # Extract content from RunResponse if needed
            personalized_content = self.personalization._extract_content(personalized)
            
            # Return personalized results
            if isinstance(search_result, dict):
                search_result["results"] = personalized_content
                search_result["personalized"] = True
                return search_result
            else:
                return {
                    "results": personalized_content,
                    "verification": "Personalized results",
                    "confidence": 85,  # Default confidence for personalized results
                    "personalized": True
                }
        
        # Return non-personalized results
        if isinstance(search_result, dict):
            search_result["personalized"] = False
            return search_result
        else:
            return {
                "results": search_results_content,
                "verification": "Standard search results",
                "confidence": 80,  # Default confidence for standard results
                "personalized": False
            }