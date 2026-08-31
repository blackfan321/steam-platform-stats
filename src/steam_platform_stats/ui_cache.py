from pathlib import Path

from .cache import CACHE_DIR
from .config import UserConfig
from .constants import PLATFORM_ORDER
from .games import get_filtered_games_rows, sort_games_by_platform
from .models import GameStats
from .views import format_games_table, format_interactive_header

UI_CACHE_DIR = CACHE_DIR / "ui"
UI_TABLE_PATH = UI_CACHE_DIR / "table"
UI_HEADER_PATH = UI_CACHE_DIR / "header"
SESSION_PLATFORM_INDEX_PATH = CACHE_DIR / "session_platform_index"


def _platform_table_path(platform: str) -> Path:
    return UI_CACHE_DIR / f"{platform}.table"


def _platform_header_path(platform: str) -> Path:
    return UI_CACHE_DIR / f"{platform}.header"


def build_ui_cache(games: list[GameStats], config: UserConfig) -> None:
    UI_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    for platform in PLATFORM_ORDER:
        sort_games_by_platform(games, platform)
        rows = get_filtered_games_rows(games, platform)
        _ = _platform_table_path(platform).write_text(
            format_games_table(rows),
            encoding="utf-8",
        )
        _ = _platform_header_path(platform).write_text(
            format_interactive_header(games, platform, config),
            encoding="utf-8",
        )


def read_platform_index() -> int:
    if not SESSION_PLATFORM_INDEX_PATH.is_file():
        return 0

    try:
        return int(SESSION_PLATFORM_INDEX_PATH.read_text(encoding="utf-8").strip())
    except ValueError:
        return 0


def write_platform_index(index: int) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _ = SESSION_PLATFORM_INDEX_PATH.write_text(str(index), encoding="utf-8")


def activate_platform_ui(index: int) -> None:
    platform = PLATFORM_ORDER[index]
    _ = UI_TABLE_PATH.write_text(
        _platform_table_path(platform).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    _ = UI_HEADER_PATH.write_text(
        _platform_header_path(platform).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    write_platform_index(index)


def cycle_platform_index() -> int:
    next_index = (read_platform_index() + 1) % len(PLATFORM_ORDER)
    activate_platform_ui(next_index)
    return next_index


def set_platform_index(index: int) -> None:
    activate_platform_ui(index)
