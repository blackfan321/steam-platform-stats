import tomllib
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError
from rich.console import Console
from xdg_base_dirs import xdg_config_home

from .constants import APP_NAME, DEFAULT_PLATFORM_LABELS
from .types import Platform

CONFIG_PATH = Path(xdg_config_home()) / APP_NAME / "config.toml"


class SteamApiSettings(BaseModel):
    timeout_seconds: int = Field(default=15, gt=0)
    include_played_free_games: bool = True


class CacheSettings(BaseModel):
    ttl_minutes: int = Field(default=5, ge=0)


class FzfSettings(BaseModel):
    default_platform: Platform = "all"
    min_playtime_minutes: int = Field(default=0, ge=0)


class NotificationsSettings(BaseModel):
    enabled: bool = True


class GameOverride(BaseModel):
    custom_name: str | None = None
    hidden: bool = False


class UserConfig(BaseModel):
    steam_api: SteamApiSettings = Field(default_factory=SteamApiSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    fzf: FzfSettings = Field(default_factory=FzfSettings)
    notifications: NotificationsSettings = Field(default_factory=NotificationsSettings)
    platform_labels: dict[str, str] = Field(default_factory=dict)
    game_override: dict[int, GameOverride] = Field(default_factory=dict)

    def platform_label(self, platform: str) -> str:
        return self.platform_labels.get(
            platform, DEFAULT_PLATFORM_LABELS.get(platform, platform)
        )

    def is_hidden(self, appid: int) -> bool:
        override = self.game_override.get(appid)
        return bool(override and override.hidden)

    def display_name(self, appid: int, default: str) -> str:
        if (override := self.game_override.get(appid)) and override.custom_name:
            return override.custom_name
        return default


@lru_cache
def load_user_config() -> UserConfig:
    if not CONFIG_PATH.is_file():
        return UserConfig()

    try:
        with CONFIG_PATH.open("rb") as f:
            data = tomllib.load(f)
        return UserConfig.model_validate(data)
    except ValidationError as e:
        Console(stderr=True).print(
            f"[yellow]Warning:[/yellow] could not load {CONFIG_PATH}: {e}"
        )
        return UserConfig()
    except tomllib.TOMLDecodeError as e:
        Console(stderr=True).print(
            f"[yellow]Warning:[/yellow] could not parse {CONFIG_PATH}: {e}"
        )
        return UserConfig()
