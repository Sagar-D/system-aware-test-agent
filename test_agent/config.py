import dotenv
import os
from pathlib import Path

dotenv.load_dotenv()
env = str(os.getenv("ENV")).lower()
is_prod = env == "prod"

DATA_DIR = Path(os.getenv("DATA_DIR", ".data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED_LLM_PLATFORMS = ["ollama", "gemini"]
DEFAULT_LLM_PLATFORM = "gemini" if is_prod else "ollama"
DEFAULT_LLM_MODELS = {"ollama": "qwen3:8b", "gemini": "gemini-2.5-flash", "gpt": "gpt-4o-mini"}

## PRD Agent
MAX_REFLECTION_COUNT = 2

## Relational DB
RELATIONAL_DB_NAME= DATA_DIR / "test_agent_db.sqlite3"
USER_ROLES=["Admin", "Product Manager", "Software Developer", "Software Architect", "Software Tester"]
RELEASE_STATUS_LIST=["DRAFT", "APPROVED"]
DOCUMENT_TYPES=["PRD", "ADR", "DB_SCHEMA", "API_SPEC", "OTHER"]
INSIGHT_STATUS=["PROPOSED", "APPROVED", "REJECTED"]
CONCERN_STATUS=["OPEN", "RESOLVED"]