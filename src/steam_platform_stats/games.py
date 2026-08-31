from keyring.errors import KeyringError
from rich.console import Console

from .cache import load_games_from_cache, save_games_to_cache
from .config import UserConfig, load_user_config
from .credentials import SteamCredentials
from .formatting import format_minutes
from .models import GameStats
from .steam_api import get_owned_games
from .types import GamesSource, GameTableRow


def apply_user_config_to_games(games: list[GameStats]) -> None:
    config = load_user_config()
    for game in games:
        game.name = config.display_name(game.appid, game.name)


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


def game_is_filtered(game: GameStats, platform: str, config: UserConfig) -> bool:
    if config.is_hidden(game.appid):
        return True

    playtime = get_playtime_for_platform(game, platform)
    if playtime <= 0:
        return True

    return playtime < max(config.fzf.min_playtime_minutes, 0)


def get_filtered_games_rows(games: list[GameStats], platform: str) -> list[GameTableRow]:
    config = load_user_config()
    rows: list[GameTableRow] = []
    index = 0

    for game in games:
        if game_is_filtered(game, platform, config):
            continue

        playtime = get_playtime_for_platform(game, platform)
        index += 1
        row: GameTableRow = {
            "index": index,
            "name": game.name,
            "playtime": format_minutes(playtime, for_table=True),
            "appid": game.appid,
        }
        rows.append(row)

    return rows


def load_or_fetch_games() -> tuple[list[GameStats], GamesSource] | None:
    games = load_games_from_cache()
    if games:
        apply_user_config_to_games(games)
        return games, "cache"

    try:
        credentials = SteamCredentials.load_from_keyring()
    except KeyringError as e:
        Console(stderr=True).print(
            f"[red]Error:[/red] Could not read Steam API credentials from the system keyring: {e}"
        )
        return None
    except ValueError as e:
        Console(stderr=True).print(f"[red]Error:[/red] {e}")
        return None

    if credentials is None:
        Console(stderr=True).print(
            "[red]Error:[/red] No credentials found in the system keyring.\n\n"
            + "Run [bold]`steam-platform-stats keyring store`[/bold]"
        )
        return None

    result = get_owned_games(credentials.steam_api_key, credentials.steam_id)
    if not result.ok:
        Console(stderr=True).print(
            f"[red]Could not fetch your Steam games:[/red] {result.message}"
        )
        return None

    games = result.games or []
    if not games:
        Console(stderr=True).print(
            "[red]Error:[/red] Steam returned no games.\n\n"
            + "Set [bold]Game details[/bold] to Public in Steam privacy settings, "
            + "or confirm this account owns games."
        )
        return None

    save_games_to_cache(games)
    apply_user_config_to_games(games)
    return games, "api"
