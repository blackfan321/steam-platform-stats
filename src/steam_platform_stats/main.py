from pathlib import Path

from . import utils, views


def main():
    parser = utils.get_argument_parser()
    args = parser.parse_args()
    env_file_path = Path(args.env_file_path) if args.env_file_path else None

    loaded = utils.load_or_fetch_games(env_file_path)
    if loaded is None:
        return

    games, source = loaded

    if args.command is None:
        utils.notify_load_source(source, len(games))
        utils.launch_interactive_mode(args.env_file_path)
        return

    if args.command == "preview":
        views.print_game_preview(games, args.appid)
        return

    utils.sort_games_by_platform(games, args.platform)

    if args.command == "stats":
        views.print_platform_stats(games, args.platform)
        return

    if args.command == "table":
        views.print_games_table(utils.get_filtered_games_rows(games, args.platform))


if __name__ == "__main__":
    main()
