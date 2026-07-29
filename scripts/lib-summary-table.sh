# Renders the "Tool|Created|Updated|Skipped|Pruned" lines written by
# setup-claude.sh / setup-cursor.sh / setup-codex.sh into one table, so a
# multi-tool run shows a single summary instead of three separate "Done."
# lines. Sourced by setup.sh and upgrade.sh.

print_summary_table() {
  local stats_file="$1"
  [ -s "$stats_file" ] || return 0

  echo ""
  echo "┌──────────┬─────────┬─────────┬─────────┬─────────┐"
  echo "│ Tool     │ Created │ Updated │ Skipped │ Pruned  │"
  echo "├──────────┼─────────┼─────────┼─────────┼─────────┤"
  while IFS='|' read -r tool created updated skipped pruned; do
    printf "│ %-8s │ %7s │ %7s │ %7s │ %7s │\n" "$tool" "$created" "$updated" "$skipped" "$pruned"
  done < "$stats_file"
  echo "└──────────┴─────────┴─────────┴─────────┴─────────┘"
}
