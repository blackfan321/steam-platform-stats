from rich.console import Console
from rich.table import Table
from rich.text import Text

from steam import get_owned_games
from utils import format_minutes, get_argument_parser, get_steam_env_vars
from models import GameStats


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


def print_platform_stats(games: list[GameStats], platform: str):
    console = Console()
    count = 0
    total_minutes = 0
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


def print_games_table(games: list[GameStats], platform: str, limit: int, min_playtime: int):
    console = Console()
    table = Table(header_style="bold magenta")
    table.add_column("#", style="dim cyan", justify="right")
    table.add_column("GAME", style="green")
    table.add_column("PLAYTIME", style="yellow", justify="right")

    games_to_display = games[:limit] if limit else games

    for idx, game in enumerate(games_to_display, 1):
        playtime = get_playtime_for_platform(game, platform)
        if playtime > min_playtime:
            table.add_row(
                str(idx),
                game.name,
                Text(format_minutes(playtime, True), style="yellow")
            )

    console.print(table)


def main():
    parser = get_argument_parser()
    args = parser.parse_args()

    steam_api_key, steam_id = get_steam_env_vars()

    games: list[GameStats] = get_owned_games(steam_api_key, steam_id)

    sort_games_by_platform(games, args.platform)

    print_platform_stats(games, args.platform)
    print_games_table(games, args.platform, args.limit, args.min_playtime)


if __name__ == "__main__":
    main()