"""
Local LLM client using Ollama.
Calls the Ollama HTTP API at localhost:11434.
Same interface as before — generate_with_retry(prompt) returns a string.
"""
import httpx
import time
from app.core.config import settings
from app.core.logging_config import logger

OLLAMA_GENERATE_URL = f"{settings.ollama_base_url}/api/generate"


def generate_with_retry(prompt: str, max_retries: int = 3, temperature: float = 0.1) -> str:
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = httpx.post(
                OLLAMA_GENERATE_URL,
                json={
                    "model": settings.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": 1024,
                        "top_p": 0.9,
                        "stop": ["\n\n\n", "Question:", "User:"],
                    },
                },
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()
            text = data.get("response", "").strip()
            if not text:
                raise ValueError("Empty response from Ollama")
            logger.debug(f"Ollama response (attempt {attempt}): {text[:100]}")
            return text
        except Exception as e:
            last_error = e
            logger.warning(f"Ollama attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Ollama API failed after {max_retries} retries: {last_error}")
