#!/usr/bin/env bash
# Commit and push ~/.claude-work so working docs survive a dead machine.
# Fired from the Stop hook, so every path must exit 0 — a sync problem is never
# worth failing a session over. The next turn retries anyway.

work="$HOME/.claude-work"
lock="$work/.sync.lock"

[ -d "$work/.git" ] || exit 0

# mkdir is atomic, which matters because parallel sessions (background jobs) would
# otherwise race on the git index. A lock left behind by a killed session goes
# stale after 5 minutes.
if ! mkdir "$lock" 2>/dev/null; then
  if [ -n "$(find "$lock" -maxdepth 0 -mmin +5 2>/dev/null)" ]; then
    rmdir "$lock" 2>/dev/null && mkdir "$lock" 2>/dev/null || exit 0
  else
    exit 0
  fi
fi
trap 'rmdir "$lock" 2>/dev/null' EXIT

cd "$work" || exit 0

# An interrupted rebase from a previous run would otherwise poison every run after
# it. Nothing here is worth hand-resolving, so drop it and start clean.
if [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ]; then
  git rebase --abort 2>/dev/null || exit 0
fi

git add -A 2>/dev/null || exit 0
if ! git diff --cached --quiet 2>/dev/null; then
  # Task keys rather than full paths — enough to see what moved, short enough to read.
  keys=$(git diff --cached --name-only | sed 's|/.*||' | sort -u | tr '\n' ' ')
  git commit -qm "sync ${keys:-working docs}" 2>/dev/null || exit 0
fi

# Push on being ahead rather than on having just committed, so a commit whose push
# failed on an earlier turn is retried instead of stranded.
[ "$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)" != "0" ] || exit 0

git push -q origin main 2>/dev/null && exit 0
# A concurrent push from another machine is the only expected failure; rebase onto
# it and retry once. Anything else waits for the next turn.
if ! git pull -q --rebase --autostash origin main 2>/dev/null; then
  git rebase --abort 2>/dev/null
  exit 0
fi
git push -q origin main 2>/dev/null || true
exit 0
