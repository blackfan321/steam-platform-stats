import subprocess

from .config import load_user_config
from .constants import APP_NAME
from .types import GamesSource


def notify_load_source(source: GamesSource, count: int) -> None:
    if not load_user_config().notifications.enabled:
        return

    if source == "cache":
        body = f"Loaded {count} games from cache"
    else:
        body = f"Fetched {count} games from Steam API"

    try:
        _ = subprocess.run(
            [
                "notify-send",
                f"--app-name={APP_NAME}",
                "--urgency=low",
                "--expire-time=3000",
                APP_NAME,
                body,
            ],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        pass
