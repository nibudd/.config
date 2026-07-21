#!/usr/bin/env bash
# SessionStart nudge: remind (at most once per ~30 days) to run /workflow-review.
# Prints a systemMessage the user sees; does NOT auto-run anything.
set -euo pipefail

stamp="$HOME/.claude/.workflow-review-stamp"
interval=2592000          # 30 days in seconds
now=$(date +%s)

last=0
if [ -f "$stamp" ]; then
  last=$(cat "$stamp" 2>/dev/null || echo 0)
fi
case "$last" in ''|*[!0-9]*) last=0 ;; esac   # treat garbage as "never"

if [ $(( now - last )) -ge "$interval" ]; then
  printf '%s' "$now" > "$stamp"
  echo '{"systemMessage": "⏰ It has been about a month — consider running /workflow-review to refresh your Claude Code setup (it now sweeps the web + CC docs for new ideas)."}'
fi

exit 0
