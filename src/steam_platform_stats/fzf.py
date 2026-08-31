import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

from rich.console import Console

from .cache import SESSION_PICKLE_ENV, write_session_pickle
from .config import load_user_config
from .constants import PLATFORM_ORDER
from .models import GameStats
from .ui_cache import (
    UI_HEADER_PATH,
    UI_TABLE_PATH,
    activate_platform_ui,
    build_ui_cache,
    set_platform_index,
)

FZF_COLUMN_DELIMITER = "\u2502"


def _pwsh_single_quoted(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _file_content_command(path: Path) -> str:
    path_str = str(path.resolve())
    if sys.platform == "win32":
        if shutil.which("pwsh"):
            quoted = _pwsh_single_quoted(path_str)
            return f"pwsh -NoProfile -Command Get-Content -LiteralPath {quoted}"
        escaped = path_str.replace('"', '""')
        return f'type "{escaped}"'
    return f"cat {shlex.quote(path_str)}"


def _system_opener() -> str | None:
    if sys.platform == "win32":
        return 'cmd /c start ""'
    for command in ("xdg-open", "open"):
        if shutil.which(command):
            return command
    return None


def _pick_platform_index(platform_names: list[str]) -> int | None:
    menu = subprocess.run(
        ["fzf", "--reverse", "--height=100%", "--ansi", "--prompt=Platform > "],
        input="\n".join(platform_names),
        text=True,
        capture_output=True,
        check=False,
    )
    choice = menu.stdout.strip()
    if not choice:
        return None

    try:
        return platform_names.index(choice)
    except ValueError:
        return None


def run_platform_pick() -> None:
    config = load_user_config()
    platform_names = [config.platform_label(platform) for platform in PLATFORM_ORDER]
    picked = _pick_platform_index(platform_names)
    if picked is not None:
        set_platform_index(picked)


def launch_interactive_mode(games: list[GameStats]) -> None:
    if not shutil.which("fzf"):
        Console(stderr=True).print("[red]Error:[/red] fzf not found in PATH")
        return

    opener = _system_opener()
    if opener is None:
        Console(stderr=True).print(
            "[red]Error:[/red] No opener found (start/xdg-open/open)"
        )
        return

    config = load_user_config()
    build_ui_cache(games, config)

    current_index = 0
    default_platform = config.fzf.default_platform
    if default_platform in PLATFORM_ORDER:
        current_index = PLATFORM_ORDER.index(default_platform)

    activate_platform_ui(current_index)
    session_pickle = write_session_pickle(games)

    platform_names = [config.platform_label(platform) for platform in PLATFORM_ORDER]

    cli = shlex.quote(str(Path(sys.argv[0]).resolve()))
    reload_table = _file_content_command(UI_TABLE_PATH)
    reload_header = _file_content_command(UI_HEADER_PATH)
    switch_platform = (
        f"execute-silent({cli} platform next)"
        + f"+reload({reload_table})"
        + f"+transform-header:({reload_header})"
    )

    env = os.environ.copy()
    env["PATH"] = f"{Path(sys.argv[0]).resolve().parent}{os.pathsep}{env.get('PATH', '')}"
    env[SESSION_PICKLE_ENV] = str(session_pickle)
    env["_STEAM_OPENER"] = opener

    preview_cmd = f"{cli} preview {{5}}"
    footer_cmd = (
        f"cat {{*f}} | {cli} fzf-footer"
        if sys.platform != "win32"
        else f"{cli} fzf-footer {{*f}}"
    )

    while True:
        initial_table = UI_TABLE_PATH.read_text(encoding="utf-8")
        initial_header = UI_HEADER_PATH.read_text(encoding="utf-8")

        result = subprocess.run(
            [
                "fzf",
                "--reverse",
                "--cycle",
                "--ansi",
                f"--delimiter={FZF_COLUMN_DELIMITER}",
                "--with-nth=1,2,3,4",
                "--nth=3",
                "--no-sort",
                f"--header={initial_header}",
                "--no-info",
                f"--preview={preview_cmd}",
                f"--bind=enter:execute-silent({env['_STEAM_OPENER']} steam://nav/games/details/{{5}})",
                f"--bind=result:bg-transform-footer:({footer_cmd})",
                f"--bind=tab:{switch_platform}",
                "--expect=ctrl-p,esc",
            ],
            input=initial_table,
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )

        output = result.stdout
        if not output:
            break

        lines = output.splitlines()
        if not lines:
            break

        key = lines[0]

        if key == "esc":
            break

        if key == "ctrl-p":
            picked = _pick_platform_index(platform_names)
            if picked is not None:
                set_platform_index(picked)
            continue

        break
