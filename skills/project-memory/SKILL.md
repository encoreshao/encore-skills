---
name: project-memory
description: Record what was learned fixing an issue into CODEBASE.md — so the next analysis starts from knowledge, not a blank scan
license: MIT
compatibility: No tools required. git optional for initial CODEBASE.md commit.
metadata:
  author: encoreshao
  version: "1.0"
  tags: memory knowledge codebase loop-engineering workflow
---

# Project Memory

Every issue fix teaches you something about the codebase. Record it. The next session shouldn't have to rediscover the same root causes, the same patterns, the same traps. This is the knowledge layer that makes the loop smarter with every cycle.

Two modes: **read** before analyzing, **update** after merging.

## Read mode — before analyze-issue or fix-issue

If `CODEBASE.md` exists at the project root, read it before touching the codebase:

```bash
cat CODEBASE.md
```

Scan these sections and apply what's already known:
- **Architecture** — understand the layers before searching
- **Patterns** — what's the established way to do what you're about to do?
- **Solved Issues** — has something similar been fixed before?
- **Gotchas** — what has surprised people here?

If the relevant pattern or root cause is already documented: use it. Don't re-derive it.

## Update mode — after merge

Run this after the MR is merged and post-merge verification passes. Takes 5 minutes. Saves hours next cycle.

### 1. Create CODEBASE.md if it doesn't exist

```bash
cat > CODEBASE.md <<'EOF'
# Project Knowledge Base

## Architecture

## Patterns

## Hotspots

## Solved Issues

| Issue | Root Cause | Fix Approach | Key Files |
|-------|-----------|--------------|-----------|

## Gotchas
EOF

git add CODEBASE.md
```

### 2. Append what you learned from this fix

```markdown
## Architecture
- <Layer / component> — <what it does and where it lives>

## Patterns
- <Pattern name> — <what it is, where to find a canonical example>

## Hotspots
- `path/to/file` — <why it changes frequently, what to watch out for>

## Solved Issues

| Issue | Root Cause | Fix Approach | Key Files |
|-------|-----------|--------------|-----------|
| #<N> <title> | <one line: specific cause> | <one line: what changed> | `file1`, `file2` |

## Gotchas
- <What surprised you at the start> — <why it happens / how to avoid>
```

Write the Solved Issues row precisely:
- **Root cause**: specific. "Email comparison is case-sensitive at the DB query layer" — not "login bug"
- **Fix approach**: what changed. "Normalize email to lowercase before query" — not "edited user.rb"
- **Key files**: 1–3 files that were the actual locus of the change

Only add a Gotcha if it would have surprised you at the start of the investigation. If it was obvious from reading the code, skip it.

### 3. Commit

```bash
git add CODEBASE.md
git commit -m "chore: update project memory after resolving #<N>"
```

## What NOT to record

- Things readable from the code itself (don't duplicate what's already clear from naming or comments)
- Full implementation detail — keep it to one line; the MR has the code
- Anything already covered in the README or official docs
- Temporary state — only durable knowledge that will still be true in 6 months
