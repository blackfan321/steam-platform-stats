from typing import Literal, TypedDict

Platform = Literal["all", "windows", "linux", "mac", "deck"]
GamesSource = Literal["cache", "api"]


class GameTableRow(TypedDict):
    index: int
    name: str
    playtime: str
    appid: int
