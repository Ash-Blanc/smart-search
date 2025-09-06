#!/usr/bin/env python3
"""
Test script for the enhanced Smart Search agents.
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agents.agent_team import AgentTeam
from agents.api_failover import api_failover
import json

def test_api_failover():
    """Test the API failover mechanism."""
    print("Testing API failover mechanism...")
    
    # Test available APIs
    llm_apis = api_failover.get_available_apis("llm")
    print(f"Available LLM APIs: {[api['name'] for api in llm_apis]}")
    
    search_apis = api_failover.get_available_apis("search")
    print(f"Available Search APIs: {[api['name'] for api in search_apis]}")
    
    reranker_apis = api_failover.get_available_apis("reranker")
    print(f"Available Reranker APIs: {[api['name'] for api in reranker_apis]}")
    
    print("✅ API failover test completed\n")

def test_agent_team():
    """Test the agent team functionality."""
    print("Testing agent team...")
    
    try:
        team = AgentTeam()
        
        # Get team status
        status = team.get_team_status()
        print(f"Team status: {json.dumps(status, indent=2)}")
        
        # Test a simple search
        print("Executing test search...")
        result = team.search("What is the capital of France?", "test_user")
        print(f"Search result: {json.dumps(result, indent=2)}")
        
        print("✅ Agent team test completed\n")
        
    except Exception as e:
        print(f"❌ Agent team test failed: {e}\n")

def test_personalized_search():
    """Test the personalized search functionality."""
    print("Testing personalized search...")
    
    try:
        from agents.personalization import PersonalizedSmartSearch
        
        search_system = PersonalizedSmartSearch()
        
        # Test search without personalization
        print("Executing non-personalized search...")
        result1 = search_system.search("Latest AI developments", "default")
        print(f"Non-personalized result: {json.dumps(result1, indent=2)}")
        
        # Test search with personalization
        print("Executing personalized search...")
        result2 = search_system.search("Latest AI developments", "test_user_123")
        print(f"Personalized result: {json.dumps(result2, indent=2)}")
        
        print("✅ Personalized search test completed\n")
        
    except Exception as e:
        print(f"❌ Personalized search test failed: {e}\n")

if __name__ == "__main__":
    print("Running enhanced agent tests...\n")
    
    test_api_failover()
    test_agent_team()
    test_personalized_search()
    
    print("🎉 All tests completed!")