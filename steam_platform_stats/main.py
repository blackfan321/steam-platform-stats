# PYTHON_ARGCOMPLETE_OK
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .steam_utils import get_owned_games
from .utils import *
from .models import GameStats

DEFAULT_ENV_PATH = os.path.expanduser('~/.steam-platform-stats/.env')


def get_time_ago(timestamp):
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    last_played = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    diff = now - last_played

    if diff.days == 0:
        if diff.seconds < 3600:  # Меньше часа
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:  # Меньше дня но больше часа
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


def print_game_preview(games: list[GameStats], appid: int, no_color: bool):
    console = Console(no_color=no_color, force_terminal=True)

    game = next((g for g in games if g.appid == appid), None)
    if not game:
        console.print("[red]Game not found[/red]")
        return

    total_playtime = game.playtime_forever
    platforms = [
        ("💻", "Windows", game.playtime_windows_forever, "blue"),
        ("🍏", "Mac", game.playtime_mac_forever, "green"),
        ("🐧", "Linux", game.playtime_linux_forever, "yellow"),
        ("🎮", "Steam Deck", game.playtime_deck_forever, "magenta"),
    ]

    if total_playtime > 0:
        max_playtime = max(playtime for _, _, playtime, _ in platforms)

    # Собираем контент для панели
    panel_content = []

    # Добавляем статистику по платформам
    for emoji, name, playtime, color in platforms:
        if total_playtime > 0:
            percentage = (playtime / total_playtime * 100)
            is_leader = playtime == max_playtime and playtime > 0

            if is_leader:
                panel_content.append(f"[bold {color}]{emoji} {name}: {format_minutes(playtime)} ({percentage:.1f}%) 🏆[/]")
            else:
                panel_content.append(f"[{color}]{emoji} {name}: {format_minutes(playtime)} ({percentage:.1f}%)[/]")
        else:
            panel_content.append(f"[{color}]{emoji} {name}: {format_minutes(playtime)}[/]")

    panel_content.append(f"\n[bold]🌐 Total: {format_minutes(total_playtime)}[/bold]")

    if game.rtime_last_played:
        from datetime import datetime
        last_played = datetime.fromtimestamp(game.rtime_last_played)
        time_ago = get_time_ago(game.rtime_last_played)

        panel_content.append(f"\n [dim]Last played: {last_played.strftime('%Y-%m-%d %H:%M')}[/dim]")
        panel_content.append(f"[dim]   ({time_ago})[/dim]")

    panel = Panel(
        "\n".join(panel_content),
        title=f"[bold blue]{game.name}[/bold blue]",
        subtitle=f"[dim]AppID: {game.appid}[/dim]",
        border_style="blue",
        padding=(1, 2)
    )

    console.print(panel)


def print_platform_stats(games: list[GameStats], platform: str, no_color: bool):
    console = Console(no_color=no_color, force_terminal=True)
    count, total_minutes = 0, 0

    pretty_platform_names = {
        "windows": "️💻 Windows",
        "mac": "🍏 MacOS",
        "linux": "🐧 Linux",
        "deck": "🎮 Steam Deck",
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
    console = Console(no_color=no_color, force_terminal=True)
    table = Table(header_style="bold magenta", show_header=False)
    table.add_column("#", style="dim cyan", justify="right")
    table.add_column("GAME", style="green")
    table.add_column("PLAYTIME", style="yellow", justify="right")
    table.add_column("APPID", style="dim", justify="right")

    games_to_display = games[:limit] if limit else games

    for idx, game in enumerate(games_to_display, 1):
        playtime = get_playtime_for_platform(game, platform)
        if playtime > min_playtime:
            table.add_row(str(idx), game.name, format_minutes(playtime, True), str(game.appid))

    console.print(table)


def launch_interactive_mode():
    """Запускает интерактивный bash-скрипт"""
    import subprocess
    import os
    import sys

    # Находим путь к bash-скрипту (он лежит рядом с main.py)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bash_script = os.path.join(script_dir, "interactive.sh")

    if not os.path.exists(bash_script):
        print("Error: interactive script not found")
        return

    try:
        # Запускаем bash-скрипт
        subprocess.run(["bash", bash_script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running interactive mode: {e}")
    except FileNotFoundError:
        print("Error: bash not found. Please install bash.")


def main():
    parser = get_argument_parser()
    args = parser.parse_args()

    if args.interactive:
        launch_interactive_mode()
        return

    games: list[GameStats] = load_games_from_cache()

    if not games:
        env_file_path = args.env_file_path or DEFAULT_ENV_PATH
        steam_api_key, steam_id = get_steam_env_vars(os.path.expanduser(env_file_path))

        games = get_owned_games(steam_api_key, steam_id)
        save_games_to_cache(games)

    if args.preview:
        print_game_preview(games, args.preview, args.no_color)
        return

    sort_games_by_platform(games, args.platform)

    if not args.no_stats:
        print_platform_stats(games, args.platform, args.no_color)

    if not args.no_table:
        print_games_table(games, args.platform, args.limit, get_min_playtime(args), args.no_color)


if __name__ == "__main__":
    main()
