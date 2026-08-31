import argparse
from dataclasses import dataclass

from .constants import PLATFORM_ORDER
from .types import Platform

PLATFORMS = PLATFORM_ORDER


@dataclass(frozen=True)
class ParsedArgs:
    command: str | None
    keyring_command: str | None
    platform_command: str | None
    platform: Platform
    appid: int


def _str_or_none(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _parse_platform(value: object) -> Platform:
    if isinstance(value, str) and value in PLATFORMS:
        return value
    return "all"


def get_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Browse your Steam playtime stats in an interactive fzf UI."
    )

    subparsers = parser.add_subparsers(dest="command")

    keyring_parser = subparsers.add_parser(
        "keyring", help="manage Steam API credentials in the system keyring"
    )
    keyring_subparsers = keyring_parser.add_subparsers(
        dest="keyring_command", required=False
    )
    _ = keyring_subparsers.add_parser(
        "store", help="store Steam credentials in the system keyring"
    )
    _ = keyring_subparsers.add_parser(
        "status", help="show whether credentials are stored in the keyring"
    )
    _ = keyring_subparsers.add_parser(
        "clear", help="remove Steam credentials from the system keyring"
    )

    platform_parser = subparsers.add_parser(
        "platform", help="internal: switch platform in interactive session"
    )
    platform_subparsers = platform_parser.add_subparsers(
        dest="platform_command", required=False
    )
    _ = platform_subparsers.add_parser("next", help="cycle to the next platform")
    _ = platform_subparsers.add_parser("pick", help="open platform picker")

    stats_parser = subparsers.add_parser(
        "stats", help="internal: render platform stats line"
    )
    _ = stats_parser.add_argument(
        "-p",
        "--platform",
        default="all",
        choices=PLATFORMS,
    )

    table_parser = subparsers.add_parser(
        "table", help="internal: render fzf games table"
    )
    _ = table_parser.add_argument(
        "-p",
        "--platform",
        default="all",
        choices=PLATFORMS,
    )

    preview_parser = subparsers.add_parser(
        "preview", help="internal: render game preview panel"
    )
    _ = preview_parser.add_argument("appid", type=int)

    _ = subparsers.add_parser(
        "fzf-footer", help="internal: render filtered-results footer for fzf"
    )

    return parser


def parse_args(argv: list[str] | None = None) -> ParsedArgs:
    namespace = get_argument_parser().parse_args(argv)

    appid_raw = getattr(namespace, "appid", 0)
    appid = appid_raw if isinstance(appid_raw, int) else 0

    return ParsedArgs(
        command=_str_or_none(getattr(namespace, "command", None)),
        keyring_command=_str_or_none(getattr(namespace, "keyring_command", None)),
        platform_command=_str_or_none(getattr(namespace, "platform_command", None)),
        platform=_parse_platform(getattr(namespace, "platform", "all")),
        appid=appid,
    )
