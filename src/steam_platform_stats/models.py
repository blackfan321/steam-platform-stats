from dataclasses import asdict, dataclass, fields


@dataclass
class GameStats:
    appid: int = 0
    name: str = "some game"
    img_icon_url: str = "some icon"
    playtime_deck_forever: int = 0
    playtime_disconnected: int = 0
    playtime_forever: int = 0
    playtime_linux_forever: int = 0
    playtime_mac_forever: int = 0
    playtime_windows_forever: int = 0
    rtime_last_played: int | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "GameStats":
        return cls(
            **{f.name: data.get(f.name, f.default) for f in fields(cls)}
        )

    def to_dict(self) -> dict:
        return asdict(self)
