import json
import pickle
import time
from pathlib import Path
from typing import cast

from rich.console import Console
from xdg_base_dirs import xdg_cache_home

from .config import load_user_config
from .constants import APP_NAME
from .models import GameStats

CACHE_DIR = xdg_cache_home() / APP_NAME
GAMES_JSON_PATH = CACHE_DIR / "games.json"
GAMES_PICKLE_PATH = CACHE_DIR / "games.pkl"
SESSION_PICKLE_PATH = CACHE_DIR / "session.pkl"

SESSION_PICKLE_ENV = "STEAM_PLATFORM_STATS_GAMES_PICKLE"


def load_games_from_pickle(path: Path) -> list[GameStats]:
    with path.open("rb") as f:
        raw = pickle.load(f)

    if not isinstance(raw, list):
        return []

    games: list[GameStats] = []
    for item in cast(list[object], raw):
        if isinstance(item, GameStats):
            games.append(item)
        elif isinstance(item, dict):
            games.append(GameStats.model_validate(item))
    return games


def save_games_to_pickle(games: list[GameStats], path: Path = GAMES_PICKLE_PATH) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        pickle.dump(games, f)


def load_games_from_session_pickle() -> list[GameStats] | None:
    import os

    path_raw = os.environ.get(SESSION_PICKLE_ENV)
    if not path_raw:
        return None

    path = Path(path_raw)
    if not path.is_file():
        return None

    return load_games_from_pickle(path)


def load_games_from_cache() -> list[GameStats]:
    if not GAMES_JSON_PATH.is_file():
        return []

    cache_ttl_seconds = load_user_config().cache.ttl_minutes * 60
    file_age_seconds = time.time() - GAMES_JSON_PATH.stat().st_mtime
    if file_age_seconds > cache_ttl_seconds:
        return []

    if GAMES_JSON_PATH.stat().st_size == 0:
        return []

    if (
        GAMES_PICKLE_PATH.is_file()
        and GAMES_PICKLE_PATH.stat().st_mtime >= GAMES_JSON_PATH.stat().st_mtime
    ):
        try:
            return load_games_from_pickle(GAMES_PICKLE_PATH)
        except (pickle.PickleError, OSError, ValueError):
            pass

    with GAMES_JSON_PATH.open("r", encoding="utf-8") as f:
        try:
            raw = cast(object, json.load(f))
        except json.JSONDecodeError as e:
            Console(stderr=True).print(
                f"[red]Failed to load games from cache.[/red] {e}"
            )
            return []

    if not isinstance(raw, list):
        return []

    games: list[GameStats] = []
    for item in cast(list[object], raw):
        if isinstance(item, dict):
            games.append(GameStats.model_validate(item))

    save_games_to_pickle(games)
    return games


def save_games_to_cache(games: list[GameStats]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with GAMES_JSON_PATH.open("w", encoding="utf-8") as f:
        json.dump([game.model_dump() for game in games], f, indent=2)
    save_games_to_pickle(games)


def write_session_pickle(games: list[GameStats]) -> Path:
    save_games_to_pickle(games, SESSION_PICKLE_PATH)
    return SESSION_PICKLE_PATH
