from dataclasses import dataclass

import requests
from requests import RequestException

from .config import SteamApiSettings, load_user_config
from .models import GameStats

STEAM_API_BASE_URL = "https://api.steampowered.com"


def owned_games_params(
    steam_api: SteamApiSettings, api_key: str, steamid: int
) -> dict[str, str | int]:
    return {
        "key": api_key,
        "steamid": steamid,
        "include_played_free_games": "true" if steam_api.include_played_free_games else "false",
        "include_appinfo": "true",
    }


@dataclass(frozen=True)
class SteamApiResult:
    ok: bool
    message: str
    games: list[GameStats] | None = None


def _request_error(exc: RequestException) -> SteamApiResult:
    if isinstance(exc, requests.HTTPError):
        status = exc.response.status_code if exc.response is not None else None

        if status in {401, 403}:
            return SteamApiResult(
                ok=False,
                message="Invalid Steam API credentials",
            )

        return SteamApiResult(
            ok=False,
            message=f"Unknown Steam API error: {exc}",
        )

    if isinstance(exc, requests.Timeout):
        return SteamApiResult(
            ok=False,
            message=f"Steam API request timed out: {exc}",
        )

    if isinstance(exc, requests.ConnectionError):
        return SteamApiResult(
            ok=False,
            message=f"Could not connect to Steam API: {exc}",
        )

    return SteamApiResult(
        ok=False,
        message=f"Unknown Steam API exception: {exc}",
    )


def validate_credentials(api_key: str, steam_id: int) -> SteamApiResult:
    """Check Steam API credentials."""
    timeout = load_user_config().steam_api.timeout_seconds
    url = f"{STEAM_API_BASE_URL}/ISteamUser/GetPlayerSummaries/v0002/"

    try:
        r = requests.get(
            url,
            params={"key": api_key, "steamids": steam_id},
            timeout=timeout,
        )
        r.raise_for_status()
    except RequestException as e:
        return _request_error(e)

    try:
        response: dict[str, object] = r.json().get("response") or {}  # pyright: ignore[reportAny]
    except ValueError as e:
        return SteamApiResult(
            ok=False,
            message=f"Unexpected Steam API response: {e}",
        )

    if not response.get("players"):
        return SteamApiResult(ok=False, message="Invalid Steam64 ID")

    return SteamApiResult(ok=True, message="Steam API credentials OK")


def get_owned_games(api_key: str, steamid: int) -> SteamApiResult:
    steam_api = load_user_config().steam_api
    url = f"{STEAM_API_BASE_URL}/IPlayerService/GetOwnedGames/v0001/"

    try:
        r = requests.get(
            url=url,
            params=owned_games_params(steam_api, api_key, steamid),
            timeout=steam_api.timeout_seconds,
        )
        r.raise_for_status()
    except RequestException as e:
        return _request_error(e)

    try:
        response: dict[str, object] = r.json().get("response") or {}  # pyright: ignore[reportAny]
    except ValueError as e:
        return SteamApiResult(
            ok=False,
            message=f"Unexpected Steam API response: {e}",
        )

    raw_games = response.get("games")
    games: list[object] = raw_games if isinstance(raw_games, list) else []  # pyright: ignore[reportUnknownVariableType]

    return SteamApiResult(
        ok=True,
        message="Fetching owned games OK",
        games=[GameStats.model_validate(game) for game in games],
    )
