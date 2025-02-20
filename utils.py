import argparse
import os

from dotenv import load_dotenv


def get_steam_env_vars() -> (str, int):
    load_dotenv()

    steam_api_key = os.getenv("STEAM_API_KEY")
    steam_id = int(os.getenv("STEAM_ID"))

    if not steam_api_key:
        raise ValueError("STEAM_API_KEY variable is missing")
    if not steam_id:
        raise ValueError("STEAM_ID variable is missing")

    return steam_api_key, steam_id


def format_minutes(minutes: int, for_table=False) -> str:
    if for_table:
        return f"{minutes / 60:7.1f}h"
    return f"{minutes / 60:.1f}h"


def get_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--platform",
        default="all",
        choices=["windows", "mac", "linux", "deck", "all"],
        help="Specify the platform: windows, mac, linux, deck, all"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of games displayed"
    )
    parser.add_argument(
        "--min-playtime",
        type=int,
        default=0,
        help="Filter displayed games by minimum playtime in minutes"
    )

    return parser
