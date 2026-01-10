from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from enum import Enum
from test_agent import config
import dotenv
import os

dotenv.load_dotenv()


class ModelManager:

    _ollama_llm_instances = {}
    _gemini_llm_instances = {}
    _gpt_instances = {}

    class PLATFORMS(Enum):
        OLLAMA = "ollama"
        GEMINI = "gemini"
        GPT = "gpt"

    @classmethod
    def get_instance(
        cls,
        llm_platform: str = config.DEFAULT_LLM_PLATFORM,
        llm_model: str = None,
    ):

        if llm_platform.lower() == cls.PLATFORMS.OLLAMA.value:
            llm_model = llm_model or config.DEFAULT_LLM_MODELS[cls.PLATFORMS.OLLAMA.value]
            if llm_model not in cls._ollama_llm_instances:
                cls._ollama_llm_instances[llm_model] = ChatOllama(
                    base_url=os.getenv("OLLAMA_BASE_URL"), model=llm_model
                )
            return cls._ollama_llm_instances[llm_model]

        if llm_platform.lower() == cls.PLATFORMS.GEMINI.value:
            llm_model = llm_model or config.DEFAULT_LLM_MODELS[cls.PLATFORMS.GEMINI.value]
            if llm_model not in cls._gemini_llm_instances:
                cls._gemini_llm_instances[llm_model] = ChatGoogleGenerativeAI(
                    model=llm_model, google_api_key=os.getenv("GOOGLE_API_KEY")
                )
            return cls._gemini_llm_instances[llm_model]
        
        if llm_platform.lower() == cls.PLATFORMS.GPT.value:
            llm_model = llm_model or config.DEFAULT_LLM_MODELS[cls.PLATFORMS.GPT.value]
            if llm_model not in cls._gpt_instances:
                cls._gpt_instances[llm_model] = ChatOpenAI(
                    model=llm_model, api_key=os.getenv("OPEN_AI_API_KEY")
                )
            return cls._gpt_instances[llm_model]

        raise ValueError(f"Not supported llm_platform passed. Should be one of {[p.value for p in cls.PLATFORMS]}")
