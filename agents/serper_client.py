import requests
import json
from config import SERPER_API_KEY
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SerperAPIClient:
    """Client for interacting with the Serper API for enhanced search capabilities."""
    
    def __init__(self):
        self.api_key = SERPER_API_KEY
        self.base_url = "https://google.serper.dev"
        
        if not self.api_key:
            raise ValueError("SERPER_API_KEY is required for Serper API client")
    
    def search(self, query: str, search_type: str = "search", **kwargs):
        """
        Perform a search using the Serper API.
        
        Args:
            query (str): The search query
            search_type (str): Type of search - "search", "images", "videos", "news", "shopping"
            **kwargs: Additional parameters for the search
        
        Returns:
            dict: Search results from Serper API
        """
        url = f"{self.base_url}/{search_type}"
        
        payload = {
            "q": query,
            **kwargs
        }
        
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Serper API request failed: {str(e)}")
            raise Exception(f"Serper API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode Serper API response: {str(e)}")
            raise Exception(f"Failed to decode Serper API response: {str(e)}")
    
    def get_organic_search_results(self, query: str, num_results: int = 10):
        """
        Get organic search results for a query.
        
        Args:
            query (str): The search query
            num_results (int): Number of results to return (max 100)
        
        Returns:
            list: List of organic search results
        """
        try:
            response = self.search(query, num=num_results)
            return response.get("organic", [])
        except Exception as e:
            logger.error(f"Failed to get organic search results: {str(e)}")
            return []
    
    def get_knowledge_graph(self, query: str):
        """
        Get knowledge graph information for a query.
        
        Args:
            query (str): The search query
        
        Returns:
            dict: Knowledge graph information
        """
        try:
            response = self.search(query)
            return response.get("knowledgeGraph", {})
        except Exception as e:
            logger.error(f"Failed to get knowledge graph: {str(e)}")
            return {}
    
    def get_related_searches(self, query: str):
        """
        Get related searches for a query.
        
        Args:
            query (str): The search query
        
        Returns:
            list: List of related searches
        """
        try:
            response = self.search(query)
            return response.get("relatedSearches", [])
        except Exception as e:
            logger.error(f"Failed to get related searches: {str(e)}")
            return []

# Example usage
if __name__ == "__main__":
    # This would require a valid SERPER_API_KEY to run
    try:
        client = SerperAPIClient()
        results = client.get_organic_search_results("latest AI developments 2024", 5)
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(f"Error: {e}")