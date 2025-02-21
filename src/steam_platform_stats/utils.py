import argparse
import os

import argcomplete
from dotenv import load_dotenv

from .models import GameStats


def get_steam_env_vars(env_file_path: str) -> (str, int):
    load_dotenv(env_file_path)

    steam_api_key = os.environ["STEAM_API_KEY"]
    steam_id = int(os.environ["STEAM_ID"])

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
        '--env-file-path',
        type=str,
        help="override the path to the .env file"
    )
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
        "--no-color",
        action='store_true',
        help="disable colored output"
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


def sort_games_by_platform(games: list[GameStats], platform: str):
    games.sort(
        key=lambda x: get_playtime_for_platform(x, platform),
        reverse=True
    )
