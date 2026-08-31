from typing import ClassVar

from pydantic import BaseModel, ConfigDict


class GameStats(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(extra="ignore")

    appid: int = 0
    name: str = "Game Name"
    playtime_forever: int = 0
    playtime_deck_forever: int = 0
    playtime_linux_forever: int = 0
    playtime_mac_forever: int = 0
    playtime_windows_forever: int = 0
    rtime_last_played: int | None = None
