#!/usr/bin/env python3

"""
Test script to verify OpenRouter integration with smart-search
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Set environment variables for testing if not already set
os.environ.setdefault('OPENROUTER_API_KEY', 'test-key')
os.environ.setdefault('COHERE_API_KEY', 'test-key')

from agents.search_agent import SmartSearchAgent

def test_search():
    """Test the search functionality with a simple query"""
    print("Initializing SmartSearchAgent...")
    try:
        agent = SmartSearchAgent()
        print("✅ SmartSearchAgent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize SmartSearchAgent: {e}")
        return False

    print("\nPerforming test search...")
    try:
        # Simple search query
        query = "What are the latest developments in AI?"
        result = agent.search(query, use_reasoning=False)
        print("✅ Search completed successfully")
        print(f"\nQuery: {query}")
        print(f"Result type: {type(result)}")
        # Print first 500 characters of result for brevity
        result_str = str(result)
        print(f"Result (first 500 chars): {result_str[:500]}{'...' if len(result_str) > 500 else ''}")
        return True
    except Exception as e:
        print(f"❌ Search failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing OpenRouter integration with smart-search")
    print("=" * 50)
    
    success = test_search()
    
    if success:
        print("\n🎉 All tests passed! OpenRouter integration is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Tests failed! Please check the error messages above.")
        sys.exit(1)