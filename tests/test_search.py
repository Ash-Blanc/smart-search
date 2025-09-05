import pytest
from agents.personalization import PersonalizedSmartSearch

def test_basic_search():
    search = PersonalizedSmartSearch()
    result = search.search("What is Python programming?")
    
    assert result["results"] is not None
    assert result["confidence"] > 50
    assert "Python" in result["results"]

def test_hallucination_check():
    search = PersonalizedSmartSearch()
    result = search.search("Tell me about the programming language Zyx123")
    
    # Should catch that this is likely not real
    assert result["confidence"] < 80

def test_personalization():
    search = PersonalizedSmartSearch()
    user_id = "test_user"
    
    # First search
    search.search("Python web frameworks", user_id)
    
    # Second search
    search.search("JavaScript frameworks", user_id)
    
    # Third search should be personalized
    result = search.search("best frameworks for development", user_id)
    assert result.get("personalized") == True

# Run basic tests
if __name__ == "__main__":
    test_basic_search()
    test_hallucination_check()
    test_personalization()
    print("All tests passed!")