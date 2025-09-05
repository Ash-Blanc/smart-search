from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.memory.agent import AgentMemory
from agno.storage.json import JsonStorage
from config import OPENAI_API_KEY
from agents.verification import AntiHallucinationSearch
import json
from datetime import datetime

class PersonalizationEngine:
    def __init__(self):
        self.agent = Agent(
            name="Personalization Engine",
            role="Learn user preferences and personalize results",
            model=OpenAIChat(
                id="gpt-4o-mini", 
                api_key=OPENAI_API_KEY,
                base_url="https://openrouter.ai/api/v1"  # OpenRouter endpoint
            ),
            memory=AgentMemory(),
            storage=JsonStorage("./data/personalization"),  # Use JSON storage for personalization data
            instructions=[
                "Track user search patterns",
                "Build interest profiles",
                "Personalize result rankings"
            ]
        )
        self.user_profiles = {}
    
    def update_profile(self, user_id: str, interaction: dict):
        """Update user profile based on interaction"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "searches": [],
                "clicks": [],
                "interests": [],
                "created": datetime.now().isoformat()
            }
        
        profile = self.user_profiles[user_id]
        
        # Track search
        if "query" in interaction:
            profile["searches"].append({
                "query": interaction["query"],
                "timestamp": datetime.now().isoformat()
            })
        
        # Track clicks
        if "clicked_result" in interaction:
            profile["clicks"].append(interaction["clicked_result"])
        
        # Update interests using agent
        if len(profile["searches"]) > 5:
            interests_prompt = f"""
            Based on these recent searches: {profile["searches"][-10:]}
            And clicked results: {profile["clicks"][-10:]}
            
            Identify top 5 user interests/topics.
            """
            interests = self.agent.run(interests_prompt)
            profile["interests"] = interests
        
        return profile
    
    def personalize_results(self, user_id: str, search_results: str):
        """Re-rank results based on user profile"""
        profile = self.user_profiles.get(user_id, {})
        
        if not profile.get("interests"):
            return search_results
        
        personalization_prompt = f"""
        User interests: {profile['interests']}
        Recent searches: {profile.get('searches', [])[-5:]}
        
        Re-rank and highlight these search results based on user preferences:
        {search_results}
        
        Make results more relevant to their interests.
        """
        
        return self.agent.run(personalization_prompt)

# Main search with all features
class PersonalizedSmartSearch:
    def __init__(self):
        self.anti_hallucination = AntiHallucinationSearch()
        self.personalization = PersonalizationEngine()
    
    def search(self, query: str, user_id: str = "default"):
        """Complete search pipeline"""
        # Track query
        self.personalization.update_profile(user_id, {"query": query})
        
        # Search with verification
        search_result = self.anti_hallucination.search(query)
        
        # Personalize if we have user data
        if user_id != "default":
            personalized = self.personalization.personalize_results(
                user_id, 
                search_result["results"]
            )
            search_result["results"] = personalized
            search_result["personalized"] = True
        
        return search_result