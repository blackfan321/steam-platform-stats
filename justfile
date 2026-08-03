set shell := ["zsh", "-eu", "-o", "pipefail", "-c"]

default:
  @just --list

run-app:
  uv run steam-platform-stats

fmt:
  uvx ruff format src

lint:
  uvx ruff check src

delete-cache:
  rm -f ~/.cache/steam-platform-stats/games.json
