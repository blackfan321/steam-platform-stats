from .types import Platform

APP_NAME = "steam-platform-stats"

PLATFORM_ORDER: tuple[Platform, ...] = ("all", "windows", "linux", "mac", "deck")

DEFAULT_PLATFORM_LABELS: dict[str, str] = {
    "all": "🌐 All Platforms",
    "windows": "💻 Windows",
    "linux": "🐧 Linux",
    "mac": "🍏 MacOS",
    "deck": "🎮 Steam Deck",
}
