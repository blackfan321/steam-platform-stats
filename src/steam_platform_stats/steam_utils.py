import requests
from requests import RequestException

from .models import GameStats


def get_owned_games(key: str, steamid: int) -> list[GameStats] | None:
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"

    try:
        r = requests.get(url=url, params={'key': key,
                                          'steamid': steamid,
                                          'include_played_free_games': 'true',
                                          'include_appinfo': 'true'})
        r.raise_for_status()
    except RequestException as e:
        print(f"Couldn't get owned games. {e}")
        return None

    response = r.json()['response']

    # game_count = response['game_count']
    games = [GameStats.from_dict(game) for game in response['games']]

    # return game_count, games
    return games
