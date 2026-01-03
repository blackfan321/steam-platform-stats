# PYTHON_ARGCOMPLETE_OK

from pathlib import Path

from .config import SteamConfig
from .models import GameStats
from .steam_utils import get_owned_games
from . import utils
from . import views


def main():
    parser = utils.get_argument_parser()
    args = parser.parse_args()

    if args.interactive:
        utils.launch_interactive_mode()
        return

    games: list[GameStats] = utils.load_games_from_cache()

    if not games:
        env_file_path = Path(args.env_file_path) if args.env_file_path else None

        try:
            steam_config = SteamConfig.load(env_file_path)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            return
        except ValueError as e:
            print(f"Error: {e}")
            return

        if not (games := get_owned_games(steam_config.steam_api_key, steam_config.steam_id)):  # pyright: ignore
            return

        utils.save_games_to_cache(games)

    if args.game_stats:
        game_app_id = args.game_stats
        views.print_game_preview(games, game_app_id, args.no_color)
        return

    utils.sort_games_by_platform(games, args.platform)

    if not args.no_stats:
        views.print_platform_stats(games, args.platform, args.no_color)

    games_rows = utils.get_filtered_games_rows(games, args.platform, utils.get_min_playtime(args), args.limit)
    if not args.no_table:
        if args.fzf_table:
            views.print_games_table_fzf(games_rows, args.no_color)
            return
        else:
            views.print_games_table_console(games_rows, args.no_color)


if __name__ == "__main__":
    main()
