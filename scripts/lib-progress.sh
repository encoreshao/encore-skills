# Lightweight, dependency-free progress bar. Only renders on a real
# terminal ([ -t 1 ]) — this covers the `curl | bash` one-liner (stdin is
# piped, stdout is still the user's terminal). In CI, logs, or when output
# is captured/redirected, it's a no-op and callers fall back to printing
# each item on its own line instead, which is more useful there.

progress_bar() {
  local current="$1" total="$2" label="${3:-}"
  [ -t 1 ] || return 0
  [ "$total" -gt 0 ] || return 0

  local width=28
  local filled=$(( current * width / total ))
  local empty=$(( width - filled ))
  local filled_bar empty_bar

  filled_bar="$(printf '%*s' "$filled" '')"
  filled_bar="${filled_bar// /#}"
  empty_bar="$(printf '%*s' "$empty" '')"
  empty_bar="${empty_bar// /-}"

  printf "\r  [%s%s] %2d/%2d  %-30s" "$filled_bar" "$empty_bar" "$current" "$total" "$label"
  if [ "$current" -eq "$total" ]; then
    printf "\n"
  fi
  return 0
}

# Call before printing a message (a warning, a prune notice) that must not
# collide with an in-progress bar on the same line.
progress_break() {
  if [ -t 1 ]; then
    printf "\n"
  fi
  return 0
}
