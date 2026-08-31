import os
import re
import sys
from pathlib import Path

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
_PLAYTIME_H_RE = re.compile(r"(\d+(?:\.\d+)?)h")


def _lines() -> list[str]:
    text = sys.stdin.read()
    if text.strip():
        return text.splitlines()

    lines: list[str] = []
    for arg in sys.argv[2:]:
        path = Path(arg)
        if path.is_file():
            lines.extend(path.read_text(encoding="utf-8").splitlines())
    return lines


def run_fzf_footer() -> None:
    if not os.environ.get("FZF_QUERY", "").strip():
        return

    total_hours = 0.0
    for line in _lines():
        plain = _ANSI_RE.sub("", line)
        if match := _PLAYTIME_H_RE.search(plain):
            total_hours += float(match.group(1))

    try:
        match_count = int(os.environ.get("FZF_MATCH_COUNT", "0"))
    except ValueError:
        match_count = 0

    _ = sys.stdout.write(
        f"\033[36m🎮 {match_count}\033[0m  \033[33m🕒 {total_hours:.1f}h\033[0m"
    )
