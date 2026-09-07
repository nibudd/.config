#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="$HOME/.config"
ZSH_CUSTOM="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"

link() {
  local src="$1" dst="$2"
  if [ -L "$dst" ]; then
    echo "  skip (already linked): $dst"
  elif [ -e "$dst" ]; then
    echo "  WARN: $dst exists and is not a symlink — skipping"
  else
    mkdir -p "$(dirname "$dst")"
    ln -s "$src" "$dst"
    echo "  linked: $dst -> $src"
  fi
}

echo "Creating symlinks..."
link "$CONFIG_DIR/.tmux.conf"       "$HOME/.tmux.conf"
link "$CONFIG_DIR/omz/aliases.zsh"  "$ZSH_CUSTOM/aliases.zsh"
mkdir -p "$HOME/.claude"
link "$CONFIG_DIR/claude/settings.json"   "$HOME/.claude/settings.json"
link "$CONFIG_DIR/claude/CLAUDE.md"       "$HOME/.claude/CLAUDE.md"
link "$CONFIG_DIR/claude/keybindings.json" "$HOME/.claude/keybindings.json"
link "$CONFIG_DIR/claude/skills"          "$HOME/.claude/skills"
link "$CONFIG_DIR/claude/agents"          "$HOME/.claude/agents"
link "$CONFIG_DIR/claude/output-styles"   "$HOME/.claude/output-styles"
link "$CONFIG_DIR/claude/hooks"           "$HOME/.claude/hooks"
link "$CONFIG_DIR/claude/statusline.sh"   "$HOME/.claude/statusline.sh"

echo "Setting up Claude working docs..."
if [ -d "$HOME/.claude-work/.git" ]; then
  echo "  skip (already cloned): $HOME/.claude-work"
elif git clone -q git@github.com:nibudd/.claude-work.git "$HOME/.claude-work" 2>/dev/null; then
  echo "  cloned: $HOME/.claude-work"
else
  mkdir -p "$HOME/.claude-work"
  echo "  WARN: clone failed (ssh auth not set up yet?) — created empty $HOME/.claude-work"
  echo "        re-run once 'gh auth login' succeeds to recover previous worklogs"
fi
