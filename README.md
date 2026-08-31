# steam-platform-stats

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-0.3.0-orange)

Browse your Steam library by platform: search games, flip between platforms, peek at where you actually played them.

## Features

- `fzf`-powered browser for your Steam library
- Browse your library by a platform (Windows/Mac/Linux/Steam Deck/all at once)
- Search by game name, switch platforms on the fly
- Preview pane: pick a game to see its hours on each platform
- Hide games or rename them (in a config)
- API creds are stored in the system keyring
- Cached API responses so you're not hitting Steam every time
- Easy installation using `pipx` or `uv tool`

## Requirements

- Python 3.12+
- `fzf` ≥ 0.63
- `notify-send` (libnotify) — optional, for cache/API games load notifications
- A Secret Service provider (GNOME Keyring, KWallet, KeePassXC, etc.)

## Demo

[![asciicast](https://asciinema.org/a/vcxiDYysgwasKltTFJFIbPLM5.svg)](https://asciinema.org/a/765579)

## What you can do

- Scroll your library, type to filter games by name
- Hit `TAB` to cycle platforms — Windows, Linux, Deck, whatever
- Hover a game to see where the hours actually went
- Check total games + playtime for whatever platform you're on
- Filter something? Footer shows how many matches and their combined hours
- `#` column = your rank by playtime on that platform
- `Enter` opens the game in Steam Library

## Navigation and controls

| Key / Action | Description                                                                    |
|--------------|--------------------------------------------------------------------------------|
| `TAB`        | Cycle platforms |
| `CTRL-P`     | Choose the platform you want                                               |
| `ESC`        | Exit                                                                           |
| `Enter`      | Open the game in Steam Library                                            |

## Installation

1. Clone the repo:
```bash
   git clone git@github.com:blackfan321/steam-platform-stats.git
   cd steam-platform-stats
```

2. Install the package:
   - Using `pipx`:

    ```bash
    pipx install .
    ```
    - Using `uv`:

   ```bash
   uv tool install .
   ```

3. Save your Steam API credentials to the system keyring:

    ```bash
    steam-platform-stats keyring store
    ```

    You will be prompted for:
    - Steam64 ID — e.g. via [steamid.xyz](https://steamid.xyz/)
    - API key — register at [Steam Web API](https://steamcommunity.com/dev/apikey)

    Useful commands:

    ```bash
    steam-platform-stats keyring status
    steam-platform-stats keyring clear
    ```

4. [Optional] Create a config-file: `~/.config/steam-platform-stats/config.toml`:

    ```toml
    [steam_api]
    timeout_seconds = 30
    include_played_free_games = true

    [cache]
    ttl_minutes = 30

    [fzf]
    default_platform = "linux"
    min_playtime_minutes = 60

    [notifications]
    enabled = false

    [platform_labels]
    linux = "🐧 Linux"

    [game_override.730]
    custom_name = "CS2"

    [game_override.570]
    custom_name = "Dota 2 (garbage game btw)"
    hidden = true
    ```

    See [`config.example.toml`](config.example.toml).

## Usage

```bash
steam-platform-stats
```

## Acknowledgments

A lot of the code was written with AI help.
Codebase is kinda garbage atm. Gonna fix it some day.
