import dspy
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptOptimizer:
    """Optimize prompts per user using DSPy."""
    
    def __init__(self):
        # Configure DSPy with OpenRouter
        try:
            lm = dspy.OpenAI(
                model=OPENROUTER_MODEL,
                api_key=OPENROUTER_API_KEY,
                api_base=OPENROUTER_BASE_URL,
                max_tokens=2000
            )
            dspy.settings.configure(lm=lm)
            self.dspy_configured = True
        except Exception as e:
            logger.warning(f"Failed to configure DSPy with OpenRouter: {str(e)}")
            self.dspy_configured = False
        
        # Store user-specific prompt optimizations
        self.user_optimizations = {}
    
    def optimize_search_prompt(self, user_id: str, query: str, feedback: dict = None):
        """
        Optimize search prompt for a specific user based on feedback.
        
        Args:
            user_id (str): User identifier
            query (str): Original search query
            feedback (dict): User feedback on previous results
        
        Returns:
            str: Optimized prompt
        """
        if not self.dspy_configured:
            logger.warning("DSPy not configured, returning original query")
            return query
        
        try:
            # Get user's optimization history
            user_history = self.user_optimizations.get(user_id, [])
            
            # Create optimization signature
            class OptimizePrompt(dspy.Signature):
                """Optimize a search prompt based on user feedback and history."""
                
                user_id = dspy.InputField(desc="User identifier")
                query = dspy.InputField(desc="Original search query")
                feedback_history = dspy.InputField(desc="History of user feedback")
                optimized_prompt = dspy.OutputField(desc="Optimized search prompt")
            
            # Create prediction
            optimizer = dspy.Predict(OptimizePrompt)
            prediction = optimizer(
                user_id=user_id,
                query=query,
                feedback_history=json.dumps(user_history[-5:]) if user_history else "No feedback history"
            )
            
            optimized_prompt = prediction.optimized_prompt
            
            # Store optimization
            if user_id not in self.user_optimizations:
                self.user_optimizations[user_id] = []
            
            self.user_optimizations[user_id].append({
                "original_query": query,
                "optimized_prompt": optimized_prompt,
                "feedback": feedback,
                "timestamp": __import__('datetime').datetime.now().isoformat()
            })
            
            logger.info(f"Optimized prompt for user {user_id}")
            return optimized_prompt
            
        except Exception as e:
            logger.error(f"Failed to optimize prompt: {str(e)}")
            return query
    
    def get_user_preferences(self, user_id: str):
        """
        Get user preferences based on optimization history.
        
        Args:
            user_id (str): User identifier
        
        Returns:
            dict: User preferences
        """
        user_history = self.user_optimizations.get(user_id, [])
        
        if not user_history:
            return {
                "preferred_depth": "standard",
                "preferred_tone": "neutral",
                "preferred_sources": ["general"]
            }
        
        try:
            # Use DSPy to analyze user preferences
            class AnalyzePreferences(dspy.Signature):
                """Analyze user preferences from interaction history."""
                
                interaction_history = dspy.InputField(desc="User interaction history")
                preferences = dspy.OutputField(desc="User preferences in JSON format")
            
            analyzer = dspy.Predict(AnalyzePreferences)
            prediction = analyzer(
                interaction_history=json.dumps(user_history[-10:])  # Last 10 interactions
            )
            
            preferences = json.loads(prediction.preferences)
            return preferences
            
        except Exception as e:
            logger.error(f"Failed to analyze user preferences: {str(e)}")
            return {
                "preferred_depth": "standard",
                "preferred_tone": "neutral",
                "preferred_sources": ["general"]
            }

# Enhanced search agent with DSPy optimization
class DSPyOptimizedSearchAgent:
    """Search agent with DSPy-based prompt optimization."""
    
    def __init__(self):
        self.prompt_optimizer = PromptOptimizer()
        
        # Import our enhanced search agent
        from agents.serper_enhanced_search import SerperEnhancedSearchAgent
        self.base_agent = SerperEnhancedSearchAgent()
    
    def search(self, query: str, user_id: str = "default"):
        """
        Execute optimized search with user-specific prompt optimization.
        
        Args:
            query (str): Search query
            user_id (str): User identifier
        
        Returns:
            dict: Search results
        """
        # Optimize prompt based on user history
        if user_id != "default":
            optimized_query = self.prompt_optimizer.optimize_search_prompt(user_id, query)
            logger.info(f"Using optimized query for user {user_id}: {optimized_query}")
        else:
            optimized_query = query
        
        # Execute search with optimized prompt
        results = self.base_agent.search(optimized_query)
        
        # Extract content if needed
        if hasattr(results, 'content'):
            results_content = results.content
            return {
                "results": results_content,
                "verification": "Standard search with DSPy optimization",
                "confidence": 85,
                "optimized": user_id != "default"
            }
        elif isinstance(results, dict):
            results["optimized"] = user_id != "default"
            return results
        else:
            return {
                "results": str(results),
                "verification": "Standard search with DSPy optimization",
                "confidence": 85,
                "optimized": user_id != "default"
            }

# Example usage
if __name__ == "__main__":
    # This would require valid OpenRouter credentials to run
    try:
        optimizer = PromptOptimizer()
        # Example optimization
        # optimized = optimizer.optimize_search_prompt("user123", "Latest AI developments")
        # print(f"Optimized prompt: {optimized}")
    except Exception as e:
        print(f"Error: {e}")