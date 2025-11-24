#!/bin/bash

platforms=("all" "windows" "linux" "mac" "deck")
current_index=0

# ANSI коды для жирного текста
BOLD=$'\033[1m'
RESET=$'\033[0m'

while true; do
  platform="${platforms[$current_index]}"

  # Получаем статистику платформы (без таблицы)
  stats_header=$(time uv run -m steam_platform_stats.main --platform="$platform" --no-table)

  # Верхняя строка с управлением
  controls_header="${BOLD}TAB:${RESET} Next platform | ${BOLD}CTRL-P:${RESET} Platform menu | ${BOLD}ESC:${RESET} Exit${RESET}"

  # Составляем полный header: управление + статистика
  full_header="$controls_header"$'\n'"$stats_header"

  # Запускаем fzf с динамическим header
  result=$(time uv run -m steam_platform_stats.main --platform="$platform" --no-stats | \
    tail -n +2 | head -n -1 | \
    fzf --reverse --ansi --delimiter $'\u2502' --with-nth=1,2,3,4 \
        --header="$full_header" \
        --no-info \
        --preview="uv run -m steam_platform_stats.main --preview {5}" \
        --expect=tab,ctrl-p,esc)

  key=$(echo "$result" | head -1)
  selection=$(echo "$result" | tail -n +2)

  case "$key" in
    tab)
      # Следующая платформа по кругу
      current_index=$(( (current_index + 1) % ${#platforms[@]} ))
      ;;
    ctrl-p)
      # Выбор платформы из меню на весь экран
      new_platform=$(printf "%s\n" "${platforms[@]}" | fzf --reverse --height=100% --ansi --prompt="Platform > ")
      [[ -n "$new_platform" ]] &&
        for i in "${!platforms[@]}"; do
          [[ "${platforms[$i]}" == "$new_platform" ]] && current_index=$i && break
        done
      ;;
    esc)
      break
      ;;
    *)
      # Выбрана игра или обычный выход
      [[ -n "$selection" ]] && echo "Selected: $selection"
      break
      ;;
  esac
done

