from typing import AsyncGenerator

import litellm

from app.settings import Settings


def _get_api_key_for_model(model: str, app_settings: Settings) -> str | None:
    """Resolve the API key for a given model string."""
    if model.startswith("groq/"):
        return app_settings.GROQ_API_KEY or None
    elif model.startswith("cerebras/"):
        return app_settings.CEREBRAS_API_KEY or None
    elif model.startswith("gemini/"):
        return app_settings.GEMINI_API_KEY or None
    elif model.startswith("openai/"):
        return app_settings.SUMOPOD_API_KEY or None
    return None


def _get_api_base_for_model(model: str, app_settings: Settings) -> str | None:
    """Resolve the API base URL for models that need it."""
    if model.startswith("openai/") and app_settings.SUMOPOD_BASE_URL:
        return app_settings.SUMOPOD_BASE_URL
    return None


async def stream_chat_completion(
    messages: list[dict],
    model: str,
    app_settings: Settings,
) -> AsyncGenerator[dict, None]:
    """Stream chat completion from litellm."""
    api_key = _get_api_key_for_model(model, app_settings)
    api_base = _get_api_base_for_model(model, app_settings)

    kwargs: dict = {
        "model": model,
        "messages": messages,
        "stream": True,
    }
    if api_key:
        kwargs["api_key"] = api_key
    if api_base:
        kwargs["api_base"] = api_base

    response = await litellm.acompletion(**kwargs)

    chunk = None
    async for chunk in response:
        delta = chunk.choices[0].delta
        if delta.content:
            yield {"type": "token", "text": delta.content}

    usage = None
    if chunk and hasattr(chunk, "usage") and chunk.usage:
        usage = {
            "tokens_in": getattr(chunk.usage, "prompt_tokens", None),
            "tokens_out": getattr(chunk.usage, "completion_tokens", None),
        }
    yield {"type": "done", "usage": usage}
