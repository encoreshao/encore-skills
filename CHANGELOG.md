# Changelog

All notable changes to encore-skills are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

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
