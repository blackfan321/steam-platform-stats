#!/usr/bin/env bash

platforms=("all" "windows" "linux" "mac" "deck")
platform_names=("🌐 All Platforms" "💻 Windows" "🐧 Linux" "🍏 MacOS" "🎮 Steam Deck")

current_index=0
opener=""

if command -v xdg-open &>/dev/null; then
  opener="xdg-open"
elif command -v open &>/dev/null; then
  opener="open"
else
  echo "No opener found (xdg-open/open)"
fi

# ANSI codes
BOLD=$'\033[1m'
RESET=$'\033[0m'

cli_args=()
preview_cmd="steam-platform-stats preview {5}"
if [[ -n "${STEAM_PLATFORM_STATS_ENV_FILE:-}" ]]; then
  cli_args=(--env-file-path "$STEAM_PLATFORM_STATS_ENV_FILE")
  preview_cmd="steam-platform-stats --env-file-path $(printf %q "$STEAM_PLATFORM_STATS_ENV_FILE") preview {5}"
fi

# Requires fzf >= 0.63
filtered_footer='[[ -z $FZF_QUERY ]] || awk -F"│" '\''{ gsub(/[^0-9.]/, "", $4); s += $4 } END { printf "\033[36m🎮 %d\033[0m  \033[33m🕒 %.1fh\033[0m", ENVIRON["FZF_MATCH_COUNT"] + 0, s }'\'' {*f}'

while true; do
  platform="${platforms[$current_index]}"
  platform_pretty="${platform_names[$current_index]}"

  stats_header=$(steam-platform-stats "${cli_args[@]}" stats -p "$platform")
  controls_header="${BOLD}TAB:${RESET} Next platform | ${BOLD}CTRL-P:${RESET} Platform menu | ${BOLD}ESC:${RESET} Exit${RESET}"

  full_header="$controls_header"$'\n'"$stats_header"

  result=$(steam-platform-stats "${cli_args[@]}" table -p "$platform" | \
    sed '1d;$d' | \
    fzf --reverse \
        --ansi \
        --delimiter=$'\xe2\x94\x82' \
        --with-nth=1,2,3,4 \
        --nth=3 \
        --no-sort \
        --header="$full_header" \
        --no-info \
        --preview="$preview_cmd" \
        --bind "enter:execute-silent($opener steam://nav/games/details/{5})" \
        --bind "result:bg-transform-footer:$filtered_footer" \
        --expect=tab,ctrl-p,esc)

  key=$(echo "$result" | head -1)
  selection=$(echo "$result" | tail -n +2)

  case "$key" in
    tab)
      current_index=$(( (current_index + 1) % ${#platforms[@]} ))
      ;;
    ctrl-p)
      new_pretty=$(printf "%s\n" "${platform_names[@]}" | fzf --reverse --height=100% --ansi --prompt="Platform > ")
      if [[ -n "$new_pretty" ]]; then
        for i in "${!platform_names[@]}"; do
          [[ "${platform_names[$i]}" == "$new_pretty" ]] && current_index=$i && break
        done
      fi
      ;;
    esc)
      break
      ;;
    *)
      [[ -n "$selection" ]] && echo "Selected: $selection"
      break
      ;;
  esac
done
