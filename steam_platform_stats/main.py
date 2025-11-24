# PYTHON_ARGCOMPLETE_OK
from steam_platform_stats.views import print_game_preview, print_platform_stats, print_games_table
from .steam_utils import get_owned_games
from .utils import *
from .models import GameStats

DEFAULT_ENV_PATH = os.path.expanduser('~/.steam-platform-stats/.env')


def main():
    parser = get_argument_parser()
    args = parser.parse_args()

    if args.interactive:
        launch_interactive_mode()
        return

    games: list[GameStats] = load_games_from_cache()

    if not games:
        env_file_path = args.env_file_path or DEFAULT_ENV_PATH
        steam_api_key, steam_id = get_steam_env_vars(os.path.expanduser(env_file_path))

        games = get_owned_games(steam_api_key, steam_id)
        save_games_to_cache(games)

    if args.preview:
        print_game_preview(games, args.preview, args.no_color)
        return

    sort_games_by_platform(games, args.platform)

    if not args.no_stats:
        print_platform_stats(games, args.platform, args.no_color)

    if not args.no_table:
        print_games_table(games, args.platform, args.limit, get_min_playtime(args), args.no_color)


if __name__ == "__main__":
    main()
