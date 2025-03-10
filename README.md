# steam-platform-stats

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-0.1.0-orange)

This little tool lets you check your Steam gaming stats by platform. Pick a platform, and it’ll show you how many games you’ve played, total hours logged, and which games you’ve spent the most time on.

<img src="screenshot.png" style="width:462px; height:348px; border-radius:10px;" />

## Features

- Grabs your Steam stats by platform — games run and total hours.
- Displays a clean table with your played games by platform.
- Supports all Steam platforms (Windows, Mac, Linux, and Steam Deck).
- Easy installation via `pipx`.
- Some command-line options you can toy with.

## Installation

1. First, clone the repo:
   ```bash
   git clone https://github.com/blackfan321/steam-platform-stats
   cd steam-platform-stats
   
2. Run pipx to install the package:
    ```bash
    pipx install steam-platform-stats

3. Create the `.env` file:
    - Create the directory if it doesn't exist:
     ```bash
     mkdir -p ~/.steam-platform-stats
     ```

    - Create and edit the .env file:
     ```bash
     vim ~/.steam-platform-stats/.env
     ```
   
    - Add the following lines:
     ```bash
     STEAM_API_KEY='your_api_key_here'
     STEAM_ID=your_steam_id_here
     ```
    
    How to get these credentials:
    - `STEAM_API_KEY`: Register at [Steam Web API](https://steamcommunity.com/dev/apikey) to get your API key.
    - `STEAM_ID`: You can use [this site](https://steamid.xyz/): enter your profile URL, then copy obtained Steam64 ID and paste here.

4. (Optional) Enable autocompletion for zsh/bash:
   - Install `argcomplete` via pip:
     ```bash
     pip install argcomplete
     ```

   - Add the following line to your `.bashrc` or `.zshrc` file to enable autocompletion:
     ```bash
     eval "$(register-python-argcomplete steam-platform-stats)"
     ```

   - Reload your shell configuration:
     ```bash
     source ~/.bashrc
     source ~/.zshrc

## Command-line options
- `-h`, `--help`  
  Show the help page.  

- `-p`, `--platform`  
  Choose the platform: `windows`, `mac`, `linux`, `deck`, or `all`.  
  **Example**: `--platform linux`

- `-l`, `--limit`  
  Limit the number of games shown in the table.  
  **Example**: `--limit 5`

- `--env-file-path`  
  Override the path to the .env file.  
  **Example**: `--env-file-path /some/path/.env`

### Filter games by playtime
- `--min-playtime-minutes`  
  Filter displayed games by minimum playtime in minutes.  
  **Example**: `--min-playtime-minutes 120`

- `--min-playtime-hours`  
  Filter displayed games by minimum playtime in hours.  
  **Example**: `--min-playtime-hours 2.5`

### Customize Output
- `--no-stats`  
  Hide platform stats (only show games table).

- `--no-table`  
  Hide the games table (only show platform stats).

- `--no-color`  
  Disable colored output.
