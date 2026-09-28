#!/bin/bash
# Status line for Claude Code. Claude Code sends session JSON on stdin.
#
# Line 1 — what is running:   [Model effort-bars] 📁 folder  branch
# Line 2 — what is used up:   ctx 155k/1M 15% │ 5h 23% ↻14:30 │ 7d 41% ↻Fri 09:00
#
# Percentages are coloured: green below 50, yellow below 80, red from 80.
# Fields Claude Code leaves out (effort, rate_limits) and a missing branch are skipped, not shown as 0.

input=$(cat)

# One jq call. Fields are joined by the ASCII unit separator, not a tab: read merges
# adjacent tabs, which would shift the fields after an empty one.
IFS=$'\x1f' read -r MODEL EFFORT DIR CTX_TOK CTX_MAX CTX_PCT H5_PCT H5_RESET D7_PCT D7_RESET < <(
  echo "$input" | jq -r '[
    .model.display_name // "?",
    .effort.level // "",
    .workspace.current_dir // .cwd // "",
    .context_window.total_input_tokens // 0,
    .context_window.context_window_size // 0,
    .context_window.used_percentage // 0,
    .rate_limits.five_hour.used_percentage // "",
    .rate_limits.five_hour.resets_at // "",
    .rate_limits.seven_day.used_percentage // "",
    .rate_limits.seven_day.resets_at // ""
  ] | map(tostring) | join("\u001f")'
)

DIM=$'\e[2m'; RESET=$'\e[0m'
SEP=" ${DIM}│${RESET} "

# 155000 -> 155k, 1000000 -> 1M
human() {
  local n=${1%.*}
  if   (( n >= 1000000 )); then awk -v n="$n" 'BEGIN { s = sprintf("%.1f", n / 1000000); sub(/\.0$/, "", s); print s "M" }'
  elif (( n >= 1000 ));    then echo "$(( n / 1000 ))k"
  else echo "$n"
  fi
}

# Whole percentage, coloured by how close it is to the limit.
pct() {
  local p=${1%.*} colour
  if   (( p >= 80 )); then colour=$'\e[31m'
  elif (( p >= 50 )); then colour=$'\e[33m'
  else colour=$'\e[32m'
  fi
  printf '%s%s%%%s' "$colour" "$p" "$RESET"
}

epoch_to_clock() {
  date -d "@$1" "$2" 2>/dev/null || date -r "$1" "$2"
}

effort_icon() {
  local glyph colour
  case $1 in
    low)    glyph=$'\xf3\xb0\xa3\xbe'; colour=$'\e[90m' ;;
    medium) glyph=$'\xf3\xb0\xa3\xb4'; colour=$'\e[34m' ;;
    high)   glyph=$'\xf3\xb0\xa3\xb6'; colour=$'\e[32m' ;;
    xhigh)  glyph=$'\xf3\xb0\xa3\xb8'; colour=$'\e[33m' ;;
    max)    glyph=$'\xf3\xb0\xa3\xba'; colour=$'\e[31m' ;;
    *)      printf '%s' "$1"; return ;;
  esac
  printf '%s%s%s' "$colour" "$glyph" "$RESET"
}

# Line 1: model, effort, folder, branch.
HEAD="$MODEL"
[[ -n $EFFORT ]] && HEAD="$HEAD $(effort_icon "$EFFORT")"
LINE1="[$HEAD] 📁 ${DIR##*/}"
if [[ -n $DIR ]]; then
  BRANCH=$(git -C "$DIR" --no-optional-locks branch --show-current 2>/dev/null)
  [[ -n $BRANCH ]] && LINE1+=" ${DIM}${RESET} $BRANCH"
fi

# Line 2: context window, then the two rate-limit windows.
LINE2="ctx $(human "$CTX_TOK")/$(human "$CTX_MAX") $(pct "$CTX_PCT")"
if [[ -n $H5_PCT ]]; then
  LINE2+="${SEP}5h $(pct "$H5_PCT") ${DIM}↻$(epoch_to_clock "$H5_RESET" +%H:%M)${RESET}"
fi
if [[ -n $D7_PCT ]]; then
  LINE2+="${SEP}7d $(pct "$D7_PCT") ${DIM}↻$(epoch_to_clock "$D7_RESET" '+%a %H:%M')${RESET}"
fi

echo "$LINE1"
echo "$LINE2"
