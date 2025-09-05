#!/usr/bin/env python3

"""
Simple test to verify OpenRouter integration is working
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Import our modules
from agents.search_agent import SmartSearchAgent

def test_with_query(query):
    """Test search with a specific query"""
    print(f"Testing search with query: '{query}'")
    try:
        agent = SmartSearchAgent()
        result = agent.search(query, use_reasoning=False)
        result_content = str(result.content) if hasattr(result, 'content') else str(result)
        print(f"✅ Success! Got response with {len(result_content)} characters")
        # Show first 200 characters
        print(f"Preview: {result_content[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

if __name__ == "__main__":
    # Test with a few different queries
    queries = [
        "What is the capital of France?",
        "Who invented the telephone?",
        "What are the latest advancements in renewable energy?"
    ]
    
    success_count = 0
    for query in queries:
        if test_with_query(query):
            success_count += 1
        print()
    
    print(f"Completed {success_count}/{len(queries)} tests successfully")
    if success_count == len(queries):
        print("🎉 All tests passed! OpenRouter integration is working correctly.")
    else:
        print("💥 Some tests failed.")