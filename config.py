from dotenv import load_dotenv
import os

load_dotenv()

# OpenRouter configuration as primary LLM provider
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

# Use OpenRouter API key for OpenAI-compatible calls
OPENAI_API_KEY = OPENROUTER_API_KEY
COHERE_API_KEY = os.getenv("COHERE_API_KEY")  # Kept for backward compatibility but not required