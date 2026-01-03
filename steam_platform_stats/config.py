from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv
from xdg_base_dirs import xdg_config_home

APP_NAME = "steam-platform-stats"
DEFAULT_ENV_PATH = xdg_config_home() / APP_NAME / ".env"


@dataclass(frozen=True)
class SteamConfig:
    steam_api_key: str
    steam_id: int
    env_file_path: Path

    @staticmethod
    def resolve_env_path(env_file_path: Path | None) -> Path:
        return (env_file_path or DEFAULT_ENV_PATH).expanduser()

    @classmethod
    def load(cls, env_file_path: Path | None = None) -> "SteamConfig":
        path = cls.resolve_env_path(env_file_path)
        if not path.exists():
            raise FileNotFoundError(f".env file not found at {path}")

        load_dotenv(path)

        steam_api_key = os.environ.get("STEAM_API_KEY")
        steam_id_raw = os.environ.get("STEAM_ID")

        if not steam_api_key:
            raise ValueError("STEAM_API_KEY variable is missing")
        if not steam_id_raw:
            raise ValueError("STEAM_ID variable is missing")

        return cls(steam_api_key=steam_api_key, steam_id=int(steam_id_raw), env_file_path=path)
