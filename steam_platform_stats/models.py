from dataclasses import dataclass
from typing import Optional


@dataclass
class GameStats:
    appid: int
    name: str
    img_icon_url: str
    playtime_deck_forever: int
    playtime_disconnected: int
    playtime_forever: int
    playtime_linux_forever: int
    playtime_mac_forever: int
    playtime_windows_forever: int
    rtime_last_played: Optional[int]

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            appid=data.get("appid", 0),
            name=data.get("name", "some game"),
            img_icon_url=data.get('img_icon_url', 'some icon'),
            playtime_deck_forever=data.get("playtime_deck_forever", 0),
            playtime_disconnected=data.get("playtime_disconnected", 0),
            playtime_forever=data.get("playtime_forever", 0),
            playtime_linux_forever=data.get("playtime_linux_forever", 0),
            playtime_mac_forever=data.get("playtime_mac_forever", 0),
            playtime_windows_forever=data.get("playtime_windows_forever", 0),
            rtime_last_played=data.get("rtime_last_played", 0)
        )

    def to_dict(self) -> dict:
        return {
            "appid": self.appid,
            "name": self.name,
            "img_icon_url": self.img_icon_url,
            "playtime_deck_forever": self.playtime_deck_forever,
            "playtime_disconnected": self.playtime_disconnected,
            "playtime_forever": self.playtime_forever,
            "playtime_linux_forever": self.playtime_linux_forever,
            "playtime_mac_forever": self.playtime_mac_forever,
            "playtime_windows_forever": self.playtime_windows_forever,
            "rtime_last_played": self.rtime_last_played
        }
