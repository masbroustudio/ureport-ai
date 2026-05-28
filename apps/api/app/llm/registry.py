from app.settings import Settings


def get_available_models(app_settings: Settings) -> list[dict]:
    """Return list of available models based on configured API keys."""
    models = []

    if app_settings.GROQ_API_KEY:
        models.append({
            "provider": "groq",
            "model_id": "groq/llama-3.3-70b-versatile",
            "display_name": "Llama 3.3 70B (Groq)",
        })

    if app_settings.CEREBRAS_API_KEY:
        models.append({
            "provider": "cerebras",
            "model_id": "cerebras/llama-3.3-70b",
            "display_name": "Llama 3.3 70B (Cerebras)",
        })

    if app_settings.GEMINI_API_KEY:
        models.append({
            "provider": "gemini",
            "model_id": "gemini/gemini-2.0-flash",
            "display_name": "Gemini 2.0 Flash",
        })

    if app_settings.SUMOPOD_API_KEY:
        models.append({
            "provider": "sumopod",
            "model_id": "openai/sumopod-default",
            "display_name": "Sumopod Default",
        })

    return models
