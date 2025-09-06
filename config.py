from dotenv import load_dotenv
import os

load_dotenv()

# Primary LLM provider - OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "gpt-4o-mini")

# Fallback LLM provider - OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Real OpenAI key for fallback
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Search Enhancement APIs
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
RESPONSE_API_KEY = os.getenv("RESPONSE_API_KEY")

# Workflow Integration
JIRA_API_KEY = os.getenv("JIRA_API_KEY")
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")

# Cohere for reranking (kept for backward compatibility)
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")