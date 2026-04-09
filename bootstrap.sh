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
link "$CONFIG_DIR/claude/hooks"           "$HOME/.claude/hooks"
