program_name := "steam-platform-stats"

set shell := ["zsh", "-eu", "-o", "pipefail", "-c"]

default:
  @just --choose

[group('uv')]
run-app:
  uv run {{program_name}}

[group('uv')]
sync-deps:
  uv sync

[group('uv')]
upgrade-deps:
  uvx uv-upsync

[group('keyring')]
keyring-store:
  uv run {{program_name}} keyring store

[group('keyring')]
keyring-status:
  uv run {{program_name}} keyring status

[group('keyring')]
keyring-clear:
  uv run {{program_name}} keyring clear

[group('lint')]
fmt:
  uvx ruff format src

[group('lint')]
lint:
  uvx ruff check src

[group('lint')]
typecheck:
  uv run basedpyright src

[group('prek')]
prek-install:
  nix develop -c prek install

[group('prek')]
prek-uninstall:
  nix develop -c prek uninstall

[group('prek')]
prek-run:
  nix develop -c prek run --all-files

delete-cache:
  rm -rf ~/.cache/{{program_name}}
