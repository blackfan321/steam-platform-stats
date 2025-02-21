# PYTHON_ARGCOMPLETE_OK
from rich.console import Console
from rich.table import Table

from .steam_utils import get_owned_games
from .utils import *
from .models import GameStats


def print_platform_stats(games: list[GameStats], platform: str, no_color: bool):
    console = Console(no_color=no_color)
    count, total_minutes = 0, 0

    pretty_platform_names = {
        "windows": "🖥️ Windows",
        "mac": "🍏 MacOS",
        "linux": "🐧 Linux",
        "deck": "🕹️ Steam Deck",
        "all": "🌐 All Platforms"
    }

    platform_pretty_name = pretty_platform_names.get(platform, 'all')

    for game in games:
        playtime = get_playtime_for_platform(game, platform)
        if playtime > 0:
            count += 1
            total_minutes += playtime

    console.print(f"[bold blue]{platform_pretty_name}[/bold blue]  "
                  f"[bold cyan]🎮 {count}[/bold cyan]  "
                  f"[bold yellow]🕒 {format_minutes(total_minutes)}[/bold yellow]")


def print_games_table(games: list[GameStats], platform: str, limit: int, min_playtime: int, no_color: bool):
    console = Console(no_color=no_color)
    table = Table(header_style="bold magenta")
    table.add_column("#", style="dim cyan", justify="right")
    table.add_column("GAME", style="green")
    table.add_column("PLAYTIME", style="yellow", justify="right")

    games_to_display = games[:limit] if limit else games

    for idx, game in enumerate(games_to_display, 1):
        playtime = get_playtime_for_platform(game, platform)
        if playtime > min_playtime:
            table.add_row(str(idx), game.name, format_minutes(playtime, True))

    console.print(table)


def main():
    parser = get_argument_parser()
    args = parser.parse_args()

    steam_api_key, steam_id = get_steam_env_vars()

    games: list[GameStats] = get_owned_games(steam_api_key, steam_id)

    sort_games_by_platform(games, args.platform)

    if not args.no_stats:
        print_platform_stats(games, args.platform, args.no_color)

    if not args.no_table:
        print_games_table(games, args.platform, args.limit, get_min_playtime(args), args.no_color)


if __name__ == "__main__":
    main()
