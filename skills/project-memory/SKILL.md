---
name: project-memory
description: Record what was learned fixing an issue into docs/CONTEXT.md — so the next analysis starts from knowledge, not a blank scan
license: MIT
compatibility: No tools required. git optional for initial docs/CONTEXT.md commit.
metadata:
  author: encoreshao
  version: "1.1"
  tags: memory knowledge context loop-engineering workflow
---

# Project Memory

Every issue fix teaches you something about the codebase. Record it. The next session shouldn't have to rediscover the same root causes, the same patterns, the same traps. `docs/CONTEXT.md` (or `docs/context/` for large projects) is the living knowledge layer — it grows smarter with every resolved issue.

Three modes: **discover** what context exists, **load** only what's relevant, **update** after merging.

## Structure

**Small to medium projects** — single file:

```
docs/CONTEXT.md
```

**Large projects** — split by domain into a directory:

```
docs/context/
  index.md        ← overview + quick-reference table across all domains
  auth.md
  payments.md
  api.md
  background-jobs.md
  <domain>.md     ← one file per major area of the codebase
```

Start with the single file. Split into a directory only when `CONTEXT.md` grows past ~150 lines or covers more than 4–5 clearly separate domains.

---

## Discover mode — what context exists?

Before reading anything, check what's available. Don't load it all.

```bash
# Check if single file exists and how large it is
ls docs/CONTEXT.md 2>/dev/null && wc -l docs/CONTEXT.md

# Or list available domain files
ls docs/context/ 2>/dev/null
```

---

## Load mode — read only what's relevant to this issue

Don't load everything into context. Load the minimum needed.

**Single file — under 100 lines:** load the whole file.
```bash
cat docs/CONTEXT.md
```

**Single file — over 100 lines:** scan headers first, then read targeted sections.
```bash
grep "^## " docs/CONTEXT.md          # see what sections exist

# Load only relevant sections
awk '/^## Solved Issues/,/^## /' docs/CONTEXT.md
awk '/^## Patterns/,/^## /' docs/CONTEXT.md
```

**Directory — always lazy-load:**
```bash
# Step 1: read index only — always lightweight
cat docs/context/index.md

# Step 2: from the issue title and description, identify which domains apply
# Step 3: load only those files
cat docs/context/auth.md       # only if the issue touches auth
cat docs/context/payments.md   # only if the issue touches payments
```

Apply what's already known before scanning the codebase:
- **Solved Issues** — has something similar been fixed before?
- **Patterns** — what's the established approach in this area?
- **Gotchas** — what has surprised people here?

If the root cause or pattern is already documented: use it. Don't re-derive it.

---

## Update mode — after merge

Run this after the MR is merged and post-merge verification passes. **Always edit in place — update existing entries, don't just append.** The file must reflect current knowledge, not a changelog.

### Single file setup

```bash
mkdir -p docs
cat > docs/CONTEXT.md <<'EOF'
# Project Context

> Living knowledge base. Updated after every resolved issue.
> Read this before analyzing or fixing anything.

## Architecture

## Patterns

## Hotspots

## Solved Issues

| Issue | Root Cause | Fix Approach | Key Files |
|-------|-----------|--------------|-----------|

## Gotchas
EOF

git add docs/CONTEXT.md
```

### Directory setup (large projects)

```bash
mkdir -p docs/context
cat > docs/context/index.md <<'EOF'
# Project Context Index

> Updated after every resolved issue. Read index.md first, then the relevant domain file.

## Domains

| File | Area |
|------|------|
| [auth.md](auth.md) | Authentication & authorization |
| [api.md](api.md) | API layer, endpoints, serialization |

## Recent fixes (last 10)

| Issue | Domain | Root Cause summary |
|-------|--------|--------------------|
EOF

# Then create per-domain files with the same structure as CONTEXT.md
```

---

### Writing a Solved Issues entry

For any structure, write each row precisely:

| Issue | Root Cause | Fix Approach | Key Files |
|-------|-----------|--------------|-----------|
| #`<N>` `<title>` | `<specific cause, one line>` | `<what changed, one line>` | `file1`, `file2` |

- **Root cause**: specific. "Email comparison is case-sensitive at DB query layer" — not "login bug"
- **Fix approach**: what changed. "Normalize email to lowercase before query" — not "edited user.rb"
- **Key files**: 1–3 files that were the actual locus of the change

### Keeping it current

After adding the new entry, do a quick pass over the full file (or relevant domain file):
- Update any Architecture or Patterns section that this fix revealed as wrong or outdated
- Remove Gotchas that are no longer relevant (root fixed, not just patched)
- Rewrite conflicting pattern entries — don't add a second one alongside a stale one

The file must read as a useful brief for someone starting fresh **today** — not a history log.

### Commit

```bash
git add docs/CONTEXT.md          # or docs/context/*.md
git commit -m "chore: update project context after resolving #<N>"
```

---

## What NOT to record

- Things readable directly from the code (don't duplicate what's clear from naming)
- Full implementation detail — one line; the MR has the code
- Anything already in the README or official docs
- Temporary state — only knowledge still true in 6 months
- Changelog-style history — this is a snapshot of current truth, not a log
