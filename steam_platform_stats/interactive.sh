#!/usr/bin/env bash

platforms=("all" "windows" "linux" "mac" "deck")
platform_names=("🌐 All Platforms" "💻 Windows" "🐧 Linux" "🍏 MacOS" "🎮 Steam Deck")

current_index=0

# ANSI codes
BOLD=$'\033[1m'
RESET=$'\033[0m'

while true; do
  platform="${platforms[$current_index]}"
  platform_pretty="${platform_names[$current_index]}"

  stats_header=$(steam-platform-stats --platform="$platform" --no-table)
  controls_header="${BOLD}TAB:${RESET} Next platform | ${BOLD}CTRL-P:${RESET} Platform menu | ${BOLD}ESC:${RESET} Exit${RESET}"

  full_header="$controls_header"$'\n'"$stats_header"

  result=$(steam-platform-stats --platform="$platform" --no-stats --fzf-table | \
    tail -n +2 | head -n -1 | \
    fzf --reverse --ansi --delimiter $'\u2502' --with-nth=1,2,3,4 \
        --header="$full_header" \
        --no-info \
        --preview="steam-platform-stats --game-stats {5}" \
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
