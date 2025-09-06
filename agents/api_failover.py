import time
import logging
from typing import Callable, Any, List
from config import (
    OPENROUTER_API_KEY, OPENAI_API_KEY,
    SERPER_API_KEY, COHERE_API_KEY
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIFailover:
    """Handle API failover and key rotation for robust API infrastructure."""
    
    def __init__(self):
        # API configurations with failover order
        self.api_configs = {
            "llm": [
                {
                    "name": "openrouter",
                    "key": OPENROUTER_API_KEY,
                    "available": bool(OPENROUTER_API_KEY),
                    "priority": 1
                },
                {
                    "name": "openai",
                    "key": OPENAI_API_KEY,
                    "available": bool(OPENAI_API_KEY),
                    "priority": 2
                }
            ],
            "search": [
                {
                    "name": "serper",
                    "key": SERPER_API_KEY,
                    "available": bool(SERPER_API_KEY),
                    "priority": 1
                }
            ],
            "reranker": [
                {
                    "name": "cohere",
                    "key": COHERE_API_KEY,
                    "available": bool(COHERE_API_KEY),
                    "priority": 1
                }
            ]
        }
        
        # Track API failures
        self.failure_counts = {}
        self.cooldown_periods = {}
        self.max_failures = 3
        self.cooldown_duration = 300  # 5 minutes
    
    def get_available_apis(self, api_type: str) -> List[dict]:
        """
        Get available APIs of a specific type, sorted by priority.
        
        Args:
            api_type (str): Type of API (llm, search, reranker)
        
        Returns:
            List[dict]: Available APIs sorted by priority
        """
        if api_type not in self.api_configs:
            return []
        
        available_apis = [
            api for api in self.api_configs[api_type] 
            if api["available"] and self._is_api_available(api["name"])
        ]
        
        return sorted(available_apis, key=lambda x: x["priority"])
    
    def _is_api_available(self, api_name: str) -> bool:
        """
        Check if an API is available (not in cooldown).
        
        Args:
            api_name (str): Name of the API
            
        Returns:
            bool: True if API is available
        """
        if api_name not in self.cooldown_periods:
            return True
        
        # Check if cooldown has expired
        if time.time() > self.cooldown_periods[api_name]:
            # Remove from cooldown
            del self.cooldown_periods[api_name]
            if api_name in self.failure_counts:
                del self.failure_counts[api_name]
            return True
        
        return False
    
    def report_failure(self, api_name: str):
        """
        Report an API failure and update failure tracking.
        
        Args:
            api_name (str): Name of the failed API
        """
        if api_name not in self.failure_counts:
            self.failure_counts[api_name] = 0
        
        self.failure_counts[api_name] += 1
        logger.warning(f"API failure reported for {api_name}. Count: {self.failure_counts[api_name]}")
        
        # Put API in cooldown if too many failures
        if self.failure_counts[api_name] >= self.max_failures:
            self.cooldown_periods[api_name] = time.time() + self.cooldown_duration
            logger.warning(f"API {api_name} put in cooldown for {self.cooldown_duration} seconds")
    
    def report_success(self, api_name: str):
        """
        Report an API success and reset failure count.
        
        Args:
            api_name (str): Name of the successful API
        """
        if api_name in self.failure_counts:
            del self.failure_counts[api_name]
        
        if api_name in self.cooldown_periods:
            del self.cooldown_periods[api_name]
        
        logger.info(f"API success reported for {api_name}")
    
    def execute_with_failover(self, api_type: str, operation: Callable, *args, **kwargs) -> Any:
        """
        Execute an operation with failover to backup APIs.
        
        Args:
            api_type (str): Type of API to use (llm, search, reranker)
            operation (Callable): Function to execute
            *args: Arguments for the operation
            **kwargs: Keyword arguments for the operation
            
        Returns:
            Any: Result of the operation
            
        Raises:
            Exception: If all APIs fail
        """
        available_apis = self.get_available_apis(api_type)
        
        if not available_apis:
            raise Exception(f"No available APIs of type {api_type}")
        
        last_exception = None
        
        for api in available_apis:
            try:
                logger.info(f"Attempting operation with {api['name']} API")
                result = operation(api["key"], *args, **kwargs)
                self.report_success(api["name"])
                return result
            except Exception as e:
                logger.warning(f"Operation failed with {api['name']} API: {str(e)}")
                self.report_failure(api["name"])
                last_exception = e
        
        # All APIs failed
        raise Exception(f"All {api_type} APIs failed. Last error: {str(last_exception)}")

# Global failover instance
api_failover = APIFailover()

# Example usage
if __name__ == "__main__":
    # Example of how to use the failover mechanism
    def example_operation(api_key, query):
        # This is a placeholder for an actual API operation
        if "invalid" in api_key:
            raise Exception("Invalid API key")
        return f"Results for: {query}"
    
    try:
        result = api_failover.execute_with_failover(
            "llm", 
            example_operation, 
            "test query"
        )
        print(result)
    except Exception as e:
        print(f"Error: {e}")