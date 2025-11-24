from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .models import GameStats
from .utils import format_minutes, format_time_ago, get_playtime_for_platform


def print_game_preview(games: list[GameStats], appid: int, no_color: bool) -> None:
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

    panel_content = []

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
        last_played = datetime.fromtimestamp(game.rtime_last_played)
        time_ago = format_time_ago(game.rtime_last_played)

        panel_content.append(f"\n [dim]Last played: {last_played.strftime('%Y-%m-%d %H:%M')}[/dim]")
        panel_content.append(f"[dim]   ({time_ago})[/dim]")

    panel = Panel(
        "\n".join(panel_content),
        title=f"[bold blue]{game.name}[/bold blue]",
        subtitle=f"[dim]AppID: {game.appid}[/dim]",
        border_style="blue",
        padding=(1, 2),
        width=console.width // 2 - 3
    )

    console.print(panel)


def print_platform_stats(games: list[GameStats], platform: str, no_color: bool) -> None:
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


def print_games_table_fzf(rows: list[dict], no_color: bool) -> None:
    console = Console(no_color=no_color, force_terminal=True)  # keep fzf colors
    table = Table(header_style="bold magenta", show_header=False)  # header is not needed for fzf

    table.add_column("#", style="dim cyan", justify="right")
    table.add_column("GAME", style="green")
    table.add_column("PLAYTIME", style="yellow", justify="right")
    table.add_column("APPID", style="dim", justify="right")  # APPID is needed for fzf preview

    for row in rows:
        table.add_row(str(row["index"]), row["name"], row["playtime"], str(row["appid"]))

    console.print(table)


def print_games_table_console(rows: list[dict], no_color: bool) -> None:
    console = Console(no_color=no_color)
    table = Table(header_style="bold magenta")

    table.add_column("#", style="dim cyan", justify="right")
    table.add_column("GAME", style="green")
    table.add_column("PLAYTIME", style="yellow", justify="right")

    for row in rows:
        table.add_row(str(row["index"]), row["name"], row["playtime"])

    console.print(table)
