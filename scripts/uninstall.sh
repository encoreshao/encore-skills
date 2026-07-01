#!/usr/bin/env bash
set -eo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$(cd "$SCRIPTS_DIR/../skills" && pwd)"

usage() {
  cat <<EOF
Usage: uninstall.sh [OPTIONS]

Remove encore-skills from AI coding tools.

Options:
  --claude    Remove from Claude Code / Claude Desktop (~/.claude/skills/)
  --cursor    Remove from Cursor in current project (.cursor/rules/)
  --codex     Remove from Codex in current project (AGENTS.md)
  --all       Remove from all tools
  --help      Show this help

Examples:
  ./scripts/uninstall.sh --claude
  ./scripts/uninstall.sh --all
EOF
}

uninstall_claude() {
  CLAUDE_SKILLS_DIR="${HOME}/.claude/skills"
  echo "Uninstalling from Claude Code / Claude Desktop (~/.claude/skills/)..."
  echo ""

  if [ ! -d "$CLAUDE_SKILLS_DIR" ]; then
    echo "  ~/.claude/skills/ not found — nothing to remove."
    return
  fi

  removed=0
  skipped=0

  for skill_dir in "$SKILLS_DIR"/*/; do
    skill_name="$(basename "$skill_dir")"
    target="$CLAUDE_SKILLS_DIR/$skill_name"

    if [ -L "$target" ]; then
      rm "$target"
      echo "  ✓ $skill_name"
      ((removed++)) || true
    else
      ((skipped++)) || true
    fi
  done

  echo ""
  echo "Done. $removed removed, $skipped not installed."
}

uninstall_cursor() {
  TARGET_DIR="${PWD}/.cursor/rules"
  echo "Uninstalling from Cursor (${TARGET_DIR})..."
  echo ""

  if [ ! -d "$TARGET_DIR" ]; then
    echo "  .cursor/rules/ not found — nothing to remove."
    return
  fi

  removed=0
  skipped=0

  for skill_dir in "$SKILLS_DIR"/*/; do
    skill_name="$(basename "$skill_dir")"
    target="$TARGET_DIR/${skill_name}.mdc"

    if [ -f "$target" ]; then
      rm "$target"
      echo "  ✓ ${skill_name}.mdc"
      ((removed++)) || true
    else
      ((skipped++)) || true
    fi
  done

  echo ""
  echo "Done. $removed removed, $skipped not installed."
}

uninstall_codex() {
  TARGET="${PWD}/AGENTS.md"
  echo "Uninstalling from Codex (${TARGET})..."
  echo ""

  if [ ! -f "$TARGET" ]; then
    echo "  AGENTS.md not found — nothing to remove."
    return
  fi

  echo "  ⚠ AGENTS.md found. This file may have been customized for this project."
  printf "  Delete AGENTS.md? [y/N] "
  read -r reply
  if [[ "$reply" =~ ^[Yy]$ ]]; then
    rm "$TARGET"
    echo "  ✓ AGENTS.md removed."
  else
    echo "  Skipped."
  fi
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
    --claude) do_claude=true ;;
    --cursor) do_cursor=true ;;
    --codex)  do_codex=true ;;
    --all)    do_claude=true; do_cursor=true; do_codex=true ;;
    --help)   usage; exit 0 ;;
    *)
      echo "Unknown option: $arg"
      usage
      exit 1
      ;;
  esac
done

if $do_claude; then
  echo "=== Claude Code / Claude Desktop ==="
  uninstall_claude
  echo ""
fi

if $do_cursor; then
  echo "=== Cursor ==="
  uninstall_cursor
  echo ""
fi

if $do_codex; then
  echo "=== Codex ==="
  uninstall_codex
  echo ""
fi

echo "✓ Uninstall complete."
