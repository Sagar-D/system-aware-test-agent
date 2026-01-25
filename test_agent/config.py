import dotenv
import os

dotenv.load_dotenv()
env = str(os.getenv("ENV")).lower()
is_prod = env == "prod"

SUPPORTED_LLM_PLATFORMS = ["ollama", "gemini"]
DEFAULT_LLM_PLATFORM = "gemini" if is_prod else "ollama"
DEFAULT_LLM_MODELS = {"ollama": "qwen3:8b", "gemini": "gemini-2.5-flash", "gpt": "gpt-4o-mini"}

## PRD Agent
MAX_REFLECTION_COUNT = 2