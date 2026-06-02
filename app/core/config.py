from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./enterprise.db"
    chroma_persist_dir: str = "./chroma_db"
    log_level: str = "INFO"
    app_env: str = "development"
    app_name: str = "NLP-SQL Platform"
    app_version: str = "1.0.0"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
