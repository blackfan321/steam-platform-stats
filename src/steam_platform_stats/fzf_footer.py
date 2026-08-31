import os
import re
import sys

FZF_COLUMN_DELIMITER = "\u2502"
_PLAYTIME_RE = re.compile(r"[^0-9.]")


def _match_count() -> int:
    raw = os.environ.get("FZF_MATCH_COUNT", "0")
    try:
        return int(raw)
    except ValueError:
        return 0


def _playtime_hours(field: str) -> float:
    cleaned = _PLAYTIME_RE.sub("", field)
    if not cleaned:
        return 0.0
    return float(cleaned)


def run_fzf_footer() -> None:
    if not os.environ.get("FZF_QUERY", "").strip():
        return

    total_hours = 0.0
    for line in sys.stdin:
        parts = line.split(FZF_COLUMN_DELIMITER)
        if len(parts) < 4:
            continue
        total_hours += _playtime_hours(parts[3])

    match_count = _match_count()
    _ = sys.stdout.write(
        f"\033[36m🎮 {match_count}\033[0m  \033[33m🕒 {total_hours:.1f}h\033[0m"
    )
