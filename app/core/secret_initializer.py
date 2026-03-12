# app/core/secret_initializer.py
import os
import secrets
from app.core.config import settings

def ensure_api_secret() -> str:
    # If settings.SECRET_KEY already set, return it
    if getattr(settings, "SECRET_KEY", ""):
        return settings.SECRET_KEY

    # generate a new secret
    new_secret = secrets.token_urlsafe(32)

    env_path = os.path.join(os.getcwd(), ".env")
    # Append SECRET_KEY if file exists, else create
    with open(env_path, "a", encoding="utf-8") as f:
        f.write(f"\nSECRET_KEY={new_secret}\n")

    # Update runtime settings (won't persist across process reloads via pydantic settings object; it's okay)
    settings.SECRET_KEY = new_secret
    return new_secret
