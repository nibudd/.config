#!/usr/bin/env bash
# Usage: preview.sh start|stop <key>
# Opens ~/.claude-work/<key>/orient.md in a headless nvim that renders a live browser preview.
set -euo pipefail

action=${1:?start or stop}
key=${2:?task key}
socket="${TMPDIR:-/tmp/}build-it-${key}.sock"
file="${BI_WORK_ROOT:-$HOME/.claude-work}/${key}/orient.md"
lua="$HOME/.claude/skills/build-it/preview.lua"

case "$action" in
  start)
    if [ -S "$socket" ]; then
      echo "preview already running for $key"
      exit 0
    fi
    nohup nvim --headless --listen "$socket" "$file" -c "luafile $lua" >/dev/null 2>&1 &
    echo "preview started for $file"
    ;;
  stop)
    if [ -S "$socket" ]; then
      nvim --server "$socket" --remote-send '<C-\><C-n>:qa!<CR>' || true
    fi
    rm -f "$socket"
    echo "preview stopped for $key"
    ;;
  *)
    echo "unknown action: $action" >&2
    exit 2
    ;;
esac
