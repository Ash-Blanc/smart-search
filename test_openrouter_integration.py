#!/usr/bin/env python3

"""
Comprehensive test script to verify OpenRouter integration with smart-search
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from config import OPENAI_API_KEY, OPENROUTER_API_KEY
from agents.search_agent import SmartSearchAgent

def test_configuration():
    """Test that the configuration is properly set up for OpenRouter"""
    print("Testing configuration...")
    
    # Check that both keys are set and identical
    if not OPENROUTER_API_KEY:
        print("❌ OPENROUTER_API_KEY is not set")
        return False
        
    if OPENAI_API_KEY != OPENROUTER_API_KEY:
        print("❌ OPENAI_API_KEY does not match OPENROUTER_API_KEY")
        return False
        
    print("✅ Configuration is correct")
    print(f"   OPENROUTER_API_KEY: {OPENAI_API_KEY[:10]}...")
    return True

def test_search():
    """Test the search functionality with a simple query"""
    print("\nTesting search functionality...")
    try:
        agent = SmartSearchAgent()
        print("✅ SmartSearchAgent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize SmartSearchAgent: {e}")
        return False

    try:
        # Simple search query
        query = "Explain quantum computing in simple terms"
        result = agent.search(query, use_reasoning=False)
        print("✅ Search completed successfully")
        
        # Analyze the result
        result_content = str(result.content) if hasattr(result, 'content') else str(result)
        print(f"\nQuery: {query}")
        print(f"Result length: {len(result_content)} characters")
        
        # Check if result contains expected content
        if len(result_content) > 50 and "quantum" in result_content.lower():
            print("✅ Search result appears to be relevant")
            # Print first 300 characters for review
            print(f"Result preview: {result_content[:300]}...")
            return True
        else:
            print("❌ Search result doesn't appear to be relevant")
            print(f"Result: {result_content}")
            return False
            
    except Exception as e:
        print(f"❌ Search failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Comprehensive OpenRouter integration test")
    print("=" * 50)
    
    config_ok = test_configuration()
    search_ok = test_search() if config_ok else False
    
    print("\n" + "=" * 50)
    if config_ok and search_ok:
        print("🎉 All tests passed! OpenRouter integration is working correctly.")
        return True
    else:
        print("💥 Some tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)