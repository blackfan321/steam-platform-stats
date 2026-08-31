from . import views
from .args import parse_args
from .cache import load_games_from_session_pickle
from .fzf import launch_interactive_mode, run_platform_pick
from .fzf_footer import run_fzf_footer
from .games import (
    get_filtered_games_rows,
    load_or_fetch_games,
    sort_games_by_platform,
)
from .keyring_cli import (
    run_keyring_clear,
    run_keyring_help,
    run_keyring_status,
    run_keyring_store,
)
from .notifications import notify_load_source
from .ui_cache import cycle_platform_index


def main() -> None:
    args = parse_args()

    if args.command == "keyring":
        if args.keyring_command == "store":
            run_keyring_store()
        elif args.keyring_command == "status":
            run_keyring_status()
        elif args.keyring_command == "clear":
            run_keyring_clear()
        else:
            run_keyring_help()
        return

    if args.command == "platform":
        if args.platform_command == "next":
            _ = cycle_platform_index()
        elif args.platform_command == "pick":
            run_platform_pick()
        return

    if args.command == "fzf-footer":
        run_fzf_footer()
        return

    if args.command == "preview":
        games = load_games_from_session_pickle()
        if games is None:
            loaded = load_or_fetch_games()
            if loaded is None:
                return
            games, _ = loaded
        views.print_game_preview(games, args.appid)
        return

    loaded = load_or_fetch_games()
    if loaded is None:
        return

    games, source = loaded

    if args.command is None:
        notify_load_source(source, len(games))
        launch_interactive_mode(games)
        return

    sort_games_by_platform(games, args.platform)

    if args.command == "stats":
        views.print_platform_stats(games, args.platform)
        return

    if args.command == "table":
        views.print_games_table(get_filtered_games_rows(games, args.platform))


if __name__ == "__main__":
    main()
