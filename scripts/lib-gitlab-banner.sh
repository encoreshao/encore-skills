# Shared "configure GitLab access" banner, sourced by setup-claude.sh,
# setup-cursor.sh, setup-codex.sh, and setup.sh. Kept in one place so the
# three per-tool scripts can't drift out of sync and so setup.sh can print
# it once (not once per tool) when installing multiple tools together.

print_gitlab_banner() {
  local skills_dir="$1"
  shift
  local tools=("$@")
  local gitlab_config="$HOME/.gitlab/config.json"

  mkdir -p "$HOME/.gitlab"

  local hint
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  if [ -s "$gitlab_config" ]; then
    echo "GitLab access: already configured"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "  ✓ Found $gitlab_config — nothing to do."
    echo ""
    echo "  To add or update an instance/token:"
    for tool in "${tools[@]}"; do
      hint="$(_gitlab_banner_hint "$tool")"
      echo "    $hint"
    done
  else
    echo "Next: configure GitLab access"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "  Option 1 — recommended:"
    for tool in "${tools[@]}"; do
      hint="$(_gitlab_banner_hint "$tool")"
      echo "    $hint"
    done
    echo ""
    echo "  Option 2 — manual:"
    echo "    cp $skills_dir/gitlab-config/gitlab_config.json.template ~/.gitlab/config.json"
    echo "    chmod 600 ~/.gitlab/config.json"
    echo "    # Edit ~/.gitlab/config.json with your GitLab URL and token"
    echo "    python $skills_dir/gitlab-config/scripts/gitlab_api.py list-instances"
  fi
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

_gitlab_banner_hint() {
  case "$1" in
    claude) echo "Claude Code: restart, then type /gitlab-config" ;;
    cursor) echo 'Cursor: prompt "run the gitlab-config skill to set up my GitLab access"' ;;
    codex)  echo 'Codex: prompt "run the gitlab-config skill to set up my GitLab access"' ;;
  esac
}
