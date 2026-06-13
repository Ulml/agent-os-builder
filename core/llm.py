from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_xai import ChatXAI
from dotenv import load_dotenv
import os
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH, override=True)

def _available_keys():
    # Reload before each lookup so runtime changes in .env are taken into account.
    load_dotenv(ENV_PATH, override=True)
    return {
        "anthropic": os.getenv("ANTHROPIC_API_KEY", "").strip(),
        "gemini": os.getenv("GEMINI_API_KEY", "").strip(),
        "grok": os.getenv("GROK_API_KEY", "").strip(),
    }


def get_llm(provider="auto", temperature=0.7):
    keys = _available_keys()

    if provider == "auto":
        for candidate in ("anthropic", "gemini", "grok"):
            if keys[candidate]:
                provider = candidate
                break
        else:
            raise ValueError(
                "Aucune clé API configurée. Ajoute au moins une clé dans l'onglet Paramètres."
            )
    elif provider not in keys:
        raise ValueError(f"Provider non supporté: {provider}")

    if not keys[provider]:
        raise ValueError(
            f"Clé API manquante pour '{provider}'. Configure-la dans l'onglet Paramètres."
        )

    if provider == "anthropic":
        return ChatAnthropic(
            model="claude-3-5-sonnet-20240620",
            temperature=temperature,
            anthropic_api_key=keys[provider],
        )
    if provider == "gemini":
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=temperature,
            google_api_key=keys[provider],
        )

    return ChatXAI(
        model=os.getenv("GROK_MODEL", "grok-3"),
        temperature=temperature,
        api_key=keys[provider],
    )