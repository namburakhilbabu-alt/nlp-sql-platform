from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./enterprise.db"
    chroma_persist_dir: str = "./chroma_db"
    log_level: str = "INFO"
    app_env: str = "development"
    app_name: str = "NLP-SQL Platform"
    app_version: str = "1.0.0"

    # Local Ollama (used when GROQ_API_KEY is not set)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"

    # Groq cloud API (set this for production / HF Spaces deployment)
    groq_api_key: str = ""
    groq_model: str = "mixtral-8x7b-32768"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
