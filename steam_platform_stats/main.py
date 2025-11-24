# PYTHON_ARGCOMPLETE_OK
from .views import *
from .steam_utils import get_owned_games
from .utils import *
from .models import GameStats

DEFAULT_ENV_PATH = Path.home() / ".steam-platform-stats" / ".env"


def main():
    parser = get_argument_parser()
    args = parser.parse_args()

    if args.interactive:
        launch_interactive_mode()
        return

    games: list[GameStats] = load_games_from_cache()

    if not games:
        env_file_path = Path(args.env_file_path) if args.env_file_path else DEFAULT_ENV_PATH

        try:
            steam_api_key, steam_id = get_steam_env_vars(env_file_path)
        except FileNotFoundError:
            print(f"Error: .env file not found at {env_file_path}")
            return
        except ValueError as e:
            print(f"Error: {e}")
            return

        if not (games := get_owned_games(steam_api_key, steam_id)):
            return

        save_games_to_cache(games)

    if args.game_stats:
        game_app_id = args.game_stats
        print_game_preview(games, game_app_id, args.no_color)
        return

    sort_games_by_platform(games, args.platform)

    if not args.no_stats:
        print_platform_stats(games, args.platform, args.no_color)

    games_rows = get_filtered_games_rows(games, args.platform, get_min_playtime(args), args.limit)
    if not args.no_table:
        if args.fzf_table:
            print_games_table_fzf(games_rows, args.no_color)
            return
        else:
            print_games_table_console(games_rows, args.no_color)


if __name__ == "__main__":
    main()
