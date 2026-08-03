import argparse
import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from xdg_base_dirs import xdg_cache_home

from .config import SteamConfig
from .models import GameStats
from .steam_utils import get_owned_games

APP_NAME = "steam-platform-stats"
CACHE_DIR = xdg_cache_home() / APP_NAME
GAMES_JSON_PATH = CACHE_DIR / "games.json"
ENV_FILE_ENV_VAR = "STEAM_PLATFORM_STATS_ENV_FILE"

PLATFORMS = ("windows", "mac", "linux", "deck", "all")
GamesSource = Literal["cache", "api"]


def launch_interactive_mode(env_file_path: str | None = None) -> None:
    script_dir = Path(__file__).resolve().parent
    bash_script_path = script_dir / "interactive.sh"

    if not bash_script_path.exists():
        print("Error: interactive script not found")
        return

    env = os.environ.copy()
    # Prefer this install's CLI when interactive.sh shells out.
    cli_dir = str(Path(sys.argv[0]).resolve().parent)
    env["PATH"] = f"{cli_dir}{os.pathsep}{env.get('PATH', '')}"
    if env_file_path:
        env[ENV_FILE_ENV_VAR] = env_file_path

    try:
        subprocess.run(["bash", bash_script_path], check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"Error running interactive mode: {e}")


def notify_load_source(source: GamesSource, count: int) -> None:
    if source == "cache":
        body = f"Loaded {count} games from cache"
    else:
        body = f"Fetched {count} games from Steam API"

    try:
        subprocess.run(
            [
                "notify-send",
                "--app-name=steam-platform-stats",
                "--urgency=low",
                "--expire-time=3000",
                "steam-platform-stats",
                body,
            ],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        pass


def format_minutes(minutes: int, for_table=False) -> str:
    if for_table:
        return f"{minutes / 60:7.1f}h"
    return f"{minutes / 60:.1f}h"


def get_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Browse your Steam playtime stats in an interactive fzf UI."
    )
    parser.add_argument(
        "--env-file-path", type=str, help="override the path to the .env file"
    )

    subparsers = parser.add_subparsers(dest="command")

    stats_parser = subparsers.add_parser(
        "stats", help="internal: render platform stats line"
    )
    stats_parser.add_argument(
        "-p",
        "--platform",
        default="all",
        choices=PLATFORMS,
    )

    table_parser = subparsers.add_parser(
        "table", help="internal: render fzf games table"
    )
    table_parser.add_argument(
        "-p",
        "--platform",
        default="all",
        choices=PLATFORMS,
    )

    preview_parser = subparsers.add_parser(
        "preview", help="internal: render game preview panel"
    )
    preview_parser.add_argument("appid", type=int)

    return parser


def get_playtime_for_platform(game: GameStats, platform: str) -> int:
    platform_playtime_map = {
        "windows": game.playtime_windows_forever,
        "mac": game.playtime_mac_forever,
        "linux": game.playtime_linux_forever,
        "deck": game.playtime_deck_forever,
        "all": game.playtime_forever,
    }
    return platform_playtime_map.get(platform, 0)


def sort_games_by_platform(games: list[GameStats], platform: str) -> None:
    games.sort(key=lambda x: get_playtime_for_platform(x, platform), reverse=True)


def load_games_from_cache() -> list[GameStats]:
    if not GAMES_JSON_PATH.exists():
        return []

    file_age_seconds = time.time() - GAMES_JSON_PATH.stat().st_mtime
    if file_age_seconds > 5 * 60:  # check if cache is older than 5 minutes
        return []

    if GAMES_JSON_PATH.stat().st_size == 0:  # check if JSON-file is empty
        return []

    with GAMES_JSON_PATH.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Failed to load games from cache. {e}")
            return []
    return [GameStats.from_dict(game) for game in data]


def save_games_to_cache(games: list[GameStats]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with GAMES_JSON_PATH.open("w", encoding="utf-8") as f:
        json.dump([game.to_dict() for game in games], f, indent=2)


def load_or_fetch_games(
    env_file_path: Path | None = None,
) -> tuple[list[GameStats], GamesSource] | None:
    games = load_games_from_cache()
    if games:
        return games, "cache"

    try:
        steam_config = SteamConfig.load(env_file_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None
    except ValueError as e:
        print(f"Error: {e}")
        return None

    if not (
        games := get_owned_games(steam_config.steam_api_key, steam_config.steam_id)
    ):  # pyright: ignore
        return None

    save_games_to_cache(games)
    return games, "api"


def format_time_ago(timestamp: int):
    now = datetime.now(UTC)
    last_played = datetime.fromtimestamp(timestamp, tz=UTC)
    diff = now - last_played

    if diff.days == 0:
        if diff.seconds < 3600:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.days == 1:
        return "yesterday"
    elif diff.days < 7:
        return f"{diff.days} days ago"
    elif diff.days < 30:
        weeks = diff.days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif diff.days < 365:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    else:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"


def get_filtered_games_rows(games: list[GameStats], platform: str) -> list[dict]:
    rows = []

    for idx, game in enumerate(games, 1):
        playtime = get_playtime_for_platform(game, platform)
        if playtime > 0:
            rows.append(
                {
                    "index": idx,
                    "name": game.name,
                    "playtime": format_minutes(playtime, True),
                    "appid": game.appid,
                }
            )

    return rows
