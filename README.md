# steam-platform-stats

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-0.1.0-orange)

This little tool lets you check your Steam gaming stats by platform. Pick a platform, and it’ll show you how many games you’ve played, total hours logged, and which games you’ve spent the most time on.

![A screenshot of dog making a DNS request](screenshot.png)

## Features

- Grabs your Steam stats by platform — games run and total hours.
- Displays a clean table with your played games by platform.
- Supports all Steam platforms (Windows, Mac, Linux, and Steam Deck).
- Easy installation via `pipx`.
- Some CLI-arguments you can toy with.

## Installation

1. First, clone the repo:
   ```bash
   git clone https://github.com/blackfan321/steam-platform-stats
   cd steam-platform-stats
   
2. Run pipx to install a package:
    ```bash
    pipx install steam-platform-stats

3. (Optional) Enable autocompletion for zsh/bash:
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

## CLI Arguments
- `-h`, `--help`  
  Show the help page.  

- `-p`, `--platform`  
  Choose the platform: `windows`, `mac`, `linux`, `deck`, or `all`.  
  **Example**: `--platform linux`

- `-l`, `--limit`  
  Limit the number of games shown in the table.  
  **Example**: `--limit 5`

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
