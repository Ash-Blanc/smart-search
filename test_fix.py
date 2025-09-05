#!/usr/bin/env python3

from agents.personalization import PersonalizedSmartSearch

def test_search():
    """Test the search functionality after fixing the RunResponse issue"""
    print("Testing search functionality...")
    
    # Initialize the search system
    search_system = PersonalizedSmartSearch()
    
    # Test a simple query
    try:
        result = search_system.search("What is the capital of France?")
        print("Search completed successfully!")
        print(f"Results: {result['results'][:100]}...")
        print(f"Confidence: {result['confidence']}")
        print(f"Verification: {result['verification'][:100]}...")
        print("Test passed!")
        return True
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False

if __name__ == "__main__":
    test_search()