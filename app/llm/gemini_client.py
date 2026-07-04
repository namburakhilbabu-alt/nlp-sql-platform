"""
LLM client — auto-selects backend based on environment:
  - GROQ_API_KEY is set  → Groq cloud API (for production / HF Spaces)
  - GROQ_API_KEY not set → Ollama local (for local development)

Same interface either way: generate_with_retry(prompt) returns a string.
"""
import httpx
import time
from app.core.config import settings
from app.core.logging_config import logger

OLLAMA_GENERATE_URL = f"{settings.ollama_base_url}/api/generate"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def _generate_via_groq(prompt: str, temperature: float) -> str:
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.groq_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 1024,
    }
    response = httpx.post(GROQ_API_URL, json=payload, headers=headers, timeout=60.0)
    response.raise_for_status()
    text = response.json()["choices"][0]["message"]["content"].strip()
    if not text:
        raise ValueError("Empty response from Groq")
    return text


def _generate_via_ollama(prompt: str, temperature: float) -> str:
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
    text = response.json().get("response", "").strip()
    if not text:
        raise ValueError("Empty response from Ollama")
    return text


def generate_with_retry(prompt: str, max_retries: int = 3, temperature: float = 0.1) -> str:
    use_groq = bool(settings.groq_api_key)
    backend = "Groq" if use_groq else "Ollama"
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            if use_groq:
                text = _generate_via_groq(prompt, temperature)
            else:
                text = _generate_via_ollama(prompt, temperature)
            logger.debug(f"{backend} response (attempt {attempt}): {text[:100]}")
            return text
        except Exception as e:
            last_error = e
            logger.warning(f"{backend} attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                time.sleep(2 ** attempt)

    raise RuntimeError(f"{backend} API failed after {max_retries} retries: {last_error}")
