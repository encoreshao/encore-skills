#!/usr/bin/env bash
set -euo pipefail

ENCORE_SKILLS_REPO="https://github.com/encoreshao/encore-skills.git"
ENCORE_SKILLS_HOME="${ENCORE_SKILLS_HOME:-${HOME}/.encore-skills}"

# Detect if we're running from a real local checkout.
# BASH_SOURCE[0] is empty when piped via curl, or a /dev/fd path when
# run via bash <(...) — neither has setup-claude.sh next to it.
_src="${BASH_SOURCE[0]:-}"
_scripts_dir=""
if [ -n "$_src" ] && [ -f "$_src" ]; then
  _scripts_dir="$(cd "$(dirname "$_src")" && pwd)"
fi

if [ -z "$_scripts_dir" ] || [ ! -f "$_scripts_dir/setup-claude.sh" ]; then
  # Not running from a local checkout — clone/update then re-exec
  if [ -d "$ENCORE_SKILLS_HOME/.git" ]; then
    echo "Updating encore-skills at $ENCORE_SKILLS_HOME..."
    git -C "$ENCORE_SKILLS_HOME" pull --ff-only origin main
  else
    echo "Cloning encore-skills to $ENCORE_SKILLS_HOME..."
    git clone "$ENCORE_SKILLS_REPO" "$ENCORE_SKILLS_HOME"
  fi
  echo ""
  exec bash "$ENCORE_SKILLS_HOME/scripts/setup.sh" "$@"
fi

SCRIPTS_DIR="$_scripts_dir"

usage() {
  cat <<EOF
Usage: setup.sh [OPTIONS]

Install encore-skills into AI coding tools.

Options:
  --claude    Install globally into Claude Code (~/.claude/skills/)
  --cursor    Install into current project (.cursor/rules/)
  --codex     Install into current project (AGENTS.md)
  --all       Install for all tools
  --upgrade   Pull latest + re-install Claude, remind about Cursor/Codex
  --help      Show this help

Examples:
  ./scripts/setup.sh --claude
  ./scripts/setup.sh --cursor --codex
  ./scripts/setup.sh --all
  ./scripts/setup.sh --upgrade

One-liner (Claude Code):
  curl -fsSL https://raw.githubusercontent.com/encoreshao/encore-skills/main/scripts/setup.sh | bash -s -- --claude
EOF
}

if [ $# -eq 0 ]; then
  usage
  exit 1
fi

do_claude=false
do_cursor=false
do_codex=false

for arg in "$@"; do
  case "$arg" in
    --claude)  do_claude=true ;;
    --cursor)  do_cursor=true ;;
    --codex)   do_codex=true ;;
    --all)     do_claude=true; do_cursor=true; do_codex=true ;;
    --upgrade) bash "$SCRIPTS_DIR/upgrade.sh"; exit 0 ;;
    --help)    usage; exit 0 ;;
    *)
      echo "Unknown option: $arg"
      usage
      exit 1
      ;;
  esac
done

if $do_claude; then
  echo "=== Claude Code ==="
  bash "$SCRIPTS_DIR/setup-claude.sh"
  echo ""
fi

if $do_cursor; then
  echo "=== Cursor ==="
  bash "$SCRIPTS_DIR/setup-cursor.sh"
  echo ""
fi

if $do_codex; then
  echo "=== Codex ==="
  bash "$SCRIPTS_DIR/setup-codex.sh"
  echo ""
fi

echo "✓ Setup complete."
