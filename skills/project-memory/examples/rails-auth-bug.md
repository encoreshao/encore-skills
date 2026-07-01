# Example: Recording a fix for a Rails auth bug

## Issue

**#42** — Users with uppercase emails cannot log in

## What was discovered during the fix

**Root cause**: `User.find_by(email: params[:email])` was an exact case-sensitive match. PostgreSQL `text` columns default to case-sensitive comparison — no `citext` type or `LOWER()` applied.

**Fix**: Normalize `params[:email]` to `.downcase.strip` before the DB lookup in `SessionsController#create`.

**Key files**: `app/controllers/sessions_controller.rb`, `spec/requests/sessions_spec.rb`

**Gotcha**: Test fixtures used lowercase emails throughout. The bug never failed CI — only appeared with real user accounts. Added a mixed-case fixture to the regression test.

## docs/CONTEXT.md entry (single file project)

```markdown
## Patterns
- Email normalization — always `.downcase.strip` before any DB lookup (see `SessionsController#create`)

## Solved Issues

| Issue | Root Cause | Fix Approach | Key Files |
|-------|-----------|--------------|-----------|
| #42 Users with uppercase emails cannot log in | Case-sensitive email match in PostgreSQL | `.downcase.strip` before `find_by` | `sessions_controller.rb`, `sessions_spec.rb` |

## Gotchas
- Test fixtures all use lowercase emails — case-sensitivity bugs won't fail CI without mixed-case fixture data
```

## docs/context/auth.md entry (large project with directory structure)

```markdown
## Patterns
- Email normalization — always `.downcase.strip` before any DB lookup (see `SessionsController#create`)

## Solved Issues

| Issue | Root Cause | Fix Approach | Key Files |
|-------|-----------|--------------|-----------|
| #42 Users with uppercase emails cannot log in | Case-sensitive email match in PostgreSQL | `.downcase.strip` before `find_by` | `sessions_controller.rb`, `sessions_spec.rb` |

## Gotchas
- Test fixtures all use lowercase emails — case-sensitivity bugs won't fail CI without mixed-case fixture data
```

Also add a row to `docs/context/index.md`:

```markdown
## Recent fixes (last 10)

| Issue | Domain | Root Cause summary |
|-------|--------|--------------------|
| #42 Uppercase email login failure | auth | Case-sensitive PostgreSQL text comparison |
```

## What the next session gains

When issue #67 ("Users imported from CSV can't log in") arrives, `analyze-issue` reads `docs/CONTEXT.md` (or `docs/context/auth.md`) first. It immediately flags: "similar to #42 — check whether CSV import normalizes email case before insert." Root cause confirmed in one grep instead of a full auth flow trace.
