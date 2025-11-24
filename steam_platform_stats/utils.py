import argparse
import json
import os
import time
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import argcomplete
from dotenv import load_dotenv

from .models import GameStats


APP_DIR = Path("~/.steam-platform-stats").expanduser()
GAMES_JSON_PATH = APP_DIR / "games.json"


def launch_interactive_mode() -> None:
    script_dir = Path(__file__).resolve().parent
    bash_script_path = script_dir / "interactive.sh"

    if not bash_script_path.exists():
        print("Error: interactive script not found")
        return

    try:
        subprocess.run(["bash", bash_script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running interactive mode: {e}")


def get_steam_env_vars(env_file_path: Path) -> tuple[str, int]:
    env_file_path = env_file_path.expanduser()
    if not env_file_path.exists():
        raise FileNotFoundError(f".env file not found at {env_file_path}")

    load_dotenv(env_file_path)

    steam_api_key = os.environ.get("STEAM_API_KEY")
    steam_id = int(os.environ.get("STEAM_ID"))

    if not steam_api_key:
        raise ValueError("STEAM_API_KEY variable is missing")
    if not steam_id:
        raise ValueError("STEAM_ID variable is missing")

    return steam_api_key, steam_id


def format_minutes(minutes: int, for_table=False) -> str:
    if for_table:
        return f"{minutes / 60:7.1f}h"
    return f"{minutes / 60:.1f}h"


def get_min_playtime(args) -> int:
    if args.min_playtime_hours is not None:
        min_playtime_minutes = int(args.min_playtime_hours * 60)
    else:
        min_playtime_minutes = args.min_playtime_minutes

    return min_playtime_minutes


def get_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', "--platform",
        default="all",
        choices=["windows", "mac", "linux", "deck", "all"],
        help="choose the platform: windows, mac, linux, deck, all"
    )
    parser.add_argument(
        '-l', "--limit",
        type=int,
        default=None,
        help="limit the number of games shown in the table"
    )
    parser.add_argument(
        '--env-file-path',
        type=str,
        help="override the path to the .env file"
    )
    parser.add_argument(
        "--no-color",
        action='store_true',
        help="disable colored output"
    )
    parser.add_argument(
        '--game-stats',
        type=int,
        metavar="APPID",
        help="show detailed stats for specific game by APPID"
    )
    parser.add_argument(
        "--fzf-table",
        action="store_true",
        help="render table in fzf-friendly format (no header, force ANSI, include APPID column)"
    )
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help="launch interactive fzf mode"
    )

    time_group = parser.add_mutually_exclusive_group()
    time_group.add_argument(
        "--min-playtime-minutes",
        type=int,
        default=0,
        help="filter displayed games by minimum playtime in minutes"
    )
    time_group.add_argument(
        "--min-playtime-hours",
        type=float,
        default=None,
        help="filter displayed games by minimum playtime in hours"
    )

    show_group = parser.add_mutually_exclusive_group()
    show_group.add_argument("--no-stats",
                            action="store_true",
                            help="hide platform stats (only show games)")
    show_group.add_argument("--no-table",
                            action="store_true",
                            help="hide the games table (only show platform stats)")

    argcomplete.autocomplete(parser)

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
    games.sort(
        key=lambda x: get_playtime_for_platform(x, platform),
        reverse=True
    )


def load_games_from_cache() -> list[GameStats]:
    if not GAMES_JSON_PATH.exists():
        return []

    file_age_seconds = time.time() - GAMES_JSON_PATH.stat().st_mtime
    if file_age_seconds > 5 * 60:  # check if cache is older than 5 minutes
        return []

    if GAMES_JSON_PATH.stat().st_size == 0:  # check if JSON-file is empty
        return []

    with GAMES_JSON_PATH.open('r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f'Failed to load games from cache. {e}')
            return []
    return [GameStats.from_dict(game) for game in data]


def save_games_to_cache(games: list[GameStats]) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    with GAMES_JSON_PATH.open('w', encoding='utf-8') as f:
        json.dump([game.to_dict() for game in games], f, indent=2)


def format_time_ago(timestamp: int):
    now = datetime.now(timezone.utc)
    last_played = datetime.fromtimestamp(timestamp, tz=timezone.utc)
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


def get_filtered_games_rows(games: list[GameStats], platform: str, min_playtime: int, limit: int) -> list[dict]:
    rows = []
    games_to_display = games[:limit] if limit else games

    for idx, game in enumerate(games_to_display, 1):
        playtime = get_playtime_for_platform(game, platform)
        if playtime > min_playtime:
            rows.append({
                "index": idx,
                "name": game.name,
                "playtime": format_minutes(playtime, True),
                "appid": game.appid,
            })

    return rows
