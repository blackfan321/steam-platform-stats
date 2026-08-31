import sys
from datetime import UTC, datetime
from io import StringIO

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .config import UserConfig, load_user_config
from .formatting import format_minutes, format_time_ago
from .games import game_is_filtered, get_playtime_for_platform
from .models import GameStats
from .types import GameTableRow, Platform


def _preview_panel(game: GameStats, *, width: int) -> Panel:
    total_playtime = game.playtime_forever
    platforms = [
        ("💻", "Windows", game.playtime_windows_forever, "blue"),
        ("🍏", "Mac", game.playtime_mac_forever, "green"),
        ("🐧", "Linux", game.playtime_linux_forever, "yellow"),
        ("🎮", "Steam Deck", game.playtime_deck_forever, "magenta"),
    ]

    max_playtime = max((playtime for _, _, playtime, _ in platforms), default=0)
    panel_content: list[str] = []

    for emoji, name, playtime, color in platforms:
        if total_playtime > 0:
            percentage = playtime / total_playtime * 100
            is_leader = playtime == max_playtime and playtime > 0

            if is_leader:
                panel_content.append(
                    f"[bold {color}]{emoji} {name}: {format_minutes(playtime)} ({percentage:.1f}%) 🏆[/]"
                )
            else:
                panel_content.append(
                    f"[{color}]{emoji} {name}: {format_minutes(playtime)} ({percentage:.1f}%)[/]"
                )
        else:
            panel_content.append(
                f"[{color}]{emoji} {name}: {format_minutes(playtime)}[/]"
            )

    panel_content.append(f"\n[bold]🌐 Total: {format_minutes(total_playtime)}[/bold]")

    if game.rtime_last_played:
        last_played = datetime.fromtimestamp(
            game.rtime_last_played, tz=UTC
        ).astimezone()
        time_ago = format_time_ago(game.rtime_last_played)

        panel_content.append(
            f"\n [dim]Last played: {last_played.strftime('%Y-%m-%d %H:%M')}[/dim]"
        )
        panel_content.append(f"[dim]   ({time_ago})[/dim]")

    return Panel(
        "\n".join(panel_content),
        title=f"[bold blue]{game.name}[/bold blue]",
        subtitle=f"[dim]AppID: {game.appid}[/dim]",
        border_style="blue",
        padding=(1, 2),
        width=width,
    )


def print_game_preview(games: list[GameStats], appid: int) -> None:
    console = Console(force_terminal=True)

    game = next((g for g in games if g.appid == appid), None)
    if not game:
        console.print("[red]Game not found[/red]")
        return

    console.print(_preview_panel(game, width=console.width // 2 - 5))


def format_platform_stats(
    games: list[GameStats], platform: str, config: UserConfig | None = None
) -> str:
    config = config or load_user_config()
    count, total_minutes = 0, 0
    platform_pretty_name = config.platform_label(platform)

    for game in games:
        if game_is_filtered(game, platform, config):
            continue

        playtime = get_playtime_for_platform(game, platform)
        count += 1
        total_minutes += playtime

    console = Console(force_terminal=True, file=StringIO(), width=120)
    console.print(
        f"[bold blue]{platform_pretty_name}[/bold blue]  "
        + f"[bold cyan]🎮 {count}[/bold cyan]  "
        + f"[bold yellow]🕒 {format_minutes(total_minutes)}[/bold yellow]"
    )
    return console.file.getvalue().rstrip("\n")  # type: ignore[union-attr]


def format_games_table(rows: list[GameTableRow]) -> str:
    table = Table(header_style="bold magenta", show_header=False)
    table.add_column("#", style="dim cyan", justify="right")
    table.add_column("GAME", style="green")
    table.add_column("PLAYTIME", style="yellow", justify="right")
    table.add_column("APPID", style="dim", justify="right")

    for row in rows:
        table.add_row(
            str(row["index"]), row["name"], row["playtime"], str(row["appid"])
        )

    console = Console(force_terminal=True, file=StringIO(), width=120)
    console.print(table)
    lines = console.file.getvalue().splitlines()  # type: ignore[union-attr]
    return "\n".join(lines[1:-1])


def format_interactive_header(
    games: list[GameStats], platform: Platform, config: UserConfig | None = None
) -> str:
    config = config or load_user_config()
    bold = "\033[1m"
    reset = "\033[0m"
    controls_header = (
        f"{bold}TAB:{reset} Next platform | "
        + f"{bold}CTRL-P:{reset} Platform menu | "
        + f"{bold}ESC:{reset} Exit"
    )
    stats_header = format_platform_stats(games, platform, config)
    return f"{controls_header}\n{stats_header}"


def print_platform_stats(games: list[GameStats], platform: str) -> None:
    sys.stdout.write(format_platform_stats(games, platform))
    sys.stdout.write("\n")


def print_games_table(rows: list[GameTableRow]) -> None:
    if not rows:
        return

    sys.stdout.write(format_games_table(rows))
    sys.stdout.write("\n")
