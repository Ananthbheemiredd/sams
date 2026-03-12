# app/core/config.py

import os
import secrets
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_SYNC_URL: str
    SECRET_KEY: str | None = None
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    MFA_TEMP_EXPIRE_MINUTES: int = 5
    SUPER_ADMIN_SECRET: str
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

# =====================================================
#  AUTO-GENERATE SECRET_KEY IF BLANK OR NULL
# =====================================================
if settings.SECRET_KEY is None or settings.SECRET_KEY.strip() == "":
    new_key = secrets.token_hex(32)

    # Update settings object
    settings.SECRET_KEY = new_key

    # Update the .env file permanently
    env_path = ".env"
    lines = []

    # Read .env
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()

        with open(env_path, "w") as f:
            wrote_key = False
            for line in lines:
                if line.startswith("SECRET_KEY"):
                    f.write(f"SECRET_KEY={new_key}\n")
                    wrote_key = True
                else:
                    f.write(line)

            # If SECRET_KEY was not found, append it
            if not wrote_key:
                f.write(f"\nSECRET_KEY={new_key}\n")

    else:
        # Create .env if missing
        with open(env_path, "w") as f:
            f.write(f"SECRET_KEY={new_key}\n")

    print(" Generated new SECRET_KEY:", new_key)
else:
    print(" Loaded SECRET_KEY from .env")
