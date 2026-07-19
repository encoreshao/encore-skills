# Changelog

All notable changes to encore-skills are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Fixed
- README: Cursor and Codex install docs now use the same one-line curl install as Claude Code instead of a manual `git clone` step (the setup script already self-clones to `~/.encore-skills` on first run regardless of tool flag).
- README: GitLab manual-setup and uninstall commands now reference `~/.encore-skills/...` instead of `~/.claude/skills/...` or a bare `./scripts/...`, since those paths only exist for Claude-only installs or a local repo checkout.
- `setup-codex.sh`: manual GitLab fallback instructions pointed at `~/.claude/skills/gitlab-config/...`, which doesn't exist for a Codex-only install — now points at `~/.encore-skills/skills/gitlab-config/...`.
- `setup-cursor.sh`: now prints the same "Next: configure GitLab access" guidance as `setup-claude.sh` and `setup-codex.sh` — previously Cursor installs ended silently with no pointer to `gitlab-config`.

### Added
- `summarize-issue` skill — once an issue is fixed and its MR exists, writes a high-level markdown recap (Summary / Root cause / Changes / Verified / MR) grounded in the actual issue, MR, and commits, and posts it as an issue comment. Fuller than `create-mr`'s one-line "Fixed in !123" note.

### Changed
- `triage-issue` description widened to lead with "replying to comments on a GitLab issue" so it triggers on a direct ask to reply, not only when triaging a whole thread.

### Removed
- `project-memory` skill and its `docs/CONTEXT.md` workflow — `analyze-issue`, `fix-issue`, and `eng-workflow` no longer reference it.

### Fixed
- `setup-claude.sh` and `setup-cursor.sh` now prune symlinks/rule files for skills removed from `skills/` instead of leaving dangling references after `--upgrade`.
- `create-mr` pre-flight now checks for uncommitted changes and commits them (per `fix-issue`'s commit convention) before pushing, instead of assuming everything was already committed.

### Added
- `triage-issue` skill — reads an issue's comment thread, decides which comments actually need your reply (tags you, or you're the assignee with an unanswered question), grounds the reply in the current codebase, drafts it in your own voice, and always shows it to you for approval before posting. Replies match the length/format of the comment they answer instead of one fixed template, and non-trivial codebase digs delegate to a subagent.
- `whoami` command to `gitlab_api.py` — fetches the authenticated GitLab user, used by `triage-issue` to detect self-mentions.
- Local instance/group/project/issue cache (`gitlab_cache.py`) under `~/.gitlab/cache/` — `sync-issue`, `sync-project`, and `sync-group` commands merge fresh API data onto whatever's already cached (by note id for issues), so team rosters and issue history persist across runs instead of being refetched and rederived every time. A project's parent group (e.g. `acme/rocket` holding `rocket-web` and `rocket-mobile`) is synced once and shared across its projects instead of duplicated. `analyze-issue` and `triage-issue` now read/write it; `annotate-project` gives projects with no local codebase a `docs/CONTEXT.md`-equivalent memory. See `gitlab-config` skill's "Local memory" section.
- `create-mr` now checks the issue thread for related work already mentioned (prior MRs, commits, decisions) before drafting, and adds a "Related" section to the description when it finds any — so reviewers aren't missing context that was already posted.

### Changed
- Renamed `workflow` skill to `eng-workflow` for clarity now that `pm-workflow` and `triage-issue` exist alongside it.
- `fix-issue` now checks the current branch and cuts a new one off `main`/`master`/`develop`/`staging`, named `<type>/<issue-number>-<func-name>`, recording the originating branch so `create-mr` can target the MR back to it instead of always assuming `main`.
- `create-mr` titles must always include the issue number now: `<feature_type>: #<issue_number> <description>`. A title without one is a blocker, not something to draft around.

## [1.3.0] - 2026-07-01

### Added
- `pm-workflow` skill — full PM/designer loop with no codebase dependency: draft issue → share → gather user feedback → synthesize → refine → validate → finalize. Includes structured feedback tracking, conflict resolution guidance, and dev-ready gate criteria.

## [1.2.0] - 2026-07-01

### Added
- `project-memory` skill — records root cause, fix approach, key files, and gotchas into `CODEBASE.md` after each resolved issue; read mode surfaces accumulated knowledge before analysis to avoid re-scanning

### Changed
- `analyze-issue`: added "Before you start" section — reads `CODEBASE.md` first if present, skipping re-discovery of known patterns
- `fix-issue`: Phase 1 now checks `CODEBASE.md` for past fixes and established patterns before scanning the codebase
- `workflow`: loop diagram updated to show memory cycle; added Phase 6 (update project memory) after post-merge verification

## [1.1.0] - 2026-07-01

### Changed
- `write-issue`: rewritten to lead with root cause identification; acceptance criteria now must be testable
- `analyze-issue`: removed "be literal" guidance; now explicitly requires questioning assumptions and finding root cause
- `fix-issue`: added "read existing code before touching anything" as Phase 1; fixed backwards git stash advice; added root cause vs symptom check
- `review-code`: reordered — problem solved? comes first, before security/correctness
- `create-mr`: complete rewrite of description template; high-level summary only, `Closes #` first, no laundry checklists
- `workflow`: added Phase 5 post-merge verification in real environment

### Added
- `metadata`, `compatibility`, `license` frontmatter fields in all SKILL.md files
- `examples/` directory in each skill with a concrete end-to-end example
- `CHANGELOG.md`, `CONTRIBUTING.md`, `LICENSE`, `CODE_OF_CONDUCT.md`
- `.github/` templates: PR template, issue templates, frontmatter validation workflow
- `scripts/upgrade.sh` and `--upgrade` flag in `setup.sh`

## [1.0.0] - 2026-07-01

### Added
- Initial release with 6 skills: `write-issue`, `analyze-issue`, `fix-issue`, `review-code`, `create-mr`, `workflow`
- Setup scripts for Claude Code, Cursor, and Codex
- Single-command install via `./scripts/setup.sh`

[Unreleased]: https://github.com/encoreshao/encore-skills/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/encoreshao/encore-skills/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/encoreshao/encore-skills/releases/tag/v1.0.0
