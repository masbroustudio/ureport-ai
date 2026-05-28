from app.llm.registry import get_available_models
from app.settings import Settings


def get_default_model(app_settings: Settings) -> str:
    """Return the default model ID, preferring groq > cerebras > gemini > sumopod."""
    models = get_available_models(app_settings)
    if models:
        return models[0]["model_id"]
    return "groq/llama-3.3-70b-versatile"
