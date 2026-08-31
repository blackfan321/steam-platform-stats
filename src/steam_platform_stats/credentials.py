from typing import ClassVar

import keyring
from keyring.errors import PasswordDeleteError
from pydantic import BaseModel, ConfigDict

from .constants import APP_NAME

KEYRING_API_KEY = "steam_api_key"
KEYRING_STEAM_ID = "steam_id"


class SteamCredentials(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    steam_api_key: str
    steam_id: int

    @classmethod
    def load_from_keyring(cls) -> "SteamCredentials | None":
        steam_api_key = keyring.get_password(APP_NAME, KEYRING_API_KEY)
        steam_id_raw = keyring.get_password(APP_NAME, KEYRING_STEAM_ID)

        has_key = bool(steam_api_key)
        has_id = bool(steam_id_raw)

        if has_key ^ has_id:
            raise ValueError(
                "Incomplete credentials in the system keyring"
                + "(only one of API key / Steam ID is stored); "
                + "run `steam-platform-stats keyring clear`, then store again"
            )

        if not has_key:
            return None

        assert steam_api_key is not None and steam_id_raw is not None
        try:
            steam_id = int(steam_id_raw)
        except ValueError as e:
            raise ValueError("invalid Steam ID stored in keyring") from e

        return cls(steam_api_key=steam_api_key, steam_id=steam_id)

    @classmethod
    def save_to_keyring(cls, steam_api_key: str, steam_id: int) -> None:
        keyring.set_password(APP_NAME, KEYRING_API_KEY, steam_api_key)
        try:
            keyring.set_password(APP_NAME, KEYRING_STEAM_ID, str(steam_id))
        except Exception:
            cls.clear_keyring()
            raise

    @classmethod
    def clear_keyring(cls) -> None:
        for username in (KEYRING_API_KEY, KEYRING_STEAM_ID):
            try:
                keyring.delete_password(APP_NAME, username)
            except PasswordDeleteError:
                pass
