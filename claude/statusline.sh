#!/bin/bash
# Claude Code statusLine: dir  branch  model  context%
# Single jq call + single git call to keep this cheap on every render.

input=$(cat)

IFS=$'\t' read -r cwd model used_pct <<EOF
$(printf '%s' "$input" | jq -r '[
  (.cwd // .workspace.current_dir // ""),
  (.model.display_name // .model.id // ""),
  (.context_window.used_percentage // "")
] | @tsv')
EOF

segments=()

if [ -n "$cwd" ]; then
  dir_name=$(basename -- "$cwd")
  segments+=("$(printf '\033[2;37m%s\033[0m' "$dir_name")")
fi

if [ -n "$cwd" ]; then
  branch=$(git -C "$cwd" --no-optional-locks branch --show-current 2>/dev/null)
  if [ -n "$branch" ]; then
    segments+=("$(printf '\033[2;36m%s\033[0m' "$branch")")
  fi
fi

if [ -n "$model" ]; then
  segments+=("$(printf '\033[2;35m%s\033[0m' "$model")")
fi

if [ -n "$used_pct" ]; then
  pct=$(printf '%.0f' "$used_pct" 2>/dev/null)
  if [ -n "$pct" ]; then
    segments+=("$(printf '\033[2;33m%s%%\033[0m' "$pct")")
  fi
fi

out=""
for s in "${segments[@]}"; do
  if [ -z "$out" ]; then
    out="$s"
  else
    out="$out  $s"
  fi
done

printf '%s' "$out"
