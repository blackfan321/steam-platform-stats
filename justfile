set shell := ["zsh", "-eu", "-o", "pipefail", "-c"]

default:
  @just --list

run-app:
  uv run steam-platform-stats

keyring-store:
  uv run steam-platform-stats keyring store

keyring-status:
  uv run steam-platform-stats keyring status

keyring-clear:
  uv run steam-platform-stats keyring clear

fmt:
  uvx ruff format src

lint:
  uvx ruff check src

typecheck:
  uv run basedpyright src

delete-cache:
  rm -rf ~/.cache/steam-platform-stats
