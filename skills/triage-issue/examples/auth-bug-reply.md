# Example: Replying to a comment on the auth bug issue

## Input
Issue #42 (see `analyze-issue`'s example), assigned to you. `sync-issue` returns this note, newest-first:

```
@you does this fix change how emails are stored, or just how they're looked up?
  — @reviewer, 2 hours ago
```

No later comment from you addresses it.

## Step 2: Verdict
Directly `@mentions` you with a clear, single question, nothing from you after it → **Clearly needs reply, ready to send.**

## Step 3: Ground it in the codebase
Checked `AuthService` — `.downcase` is only applied to the incoming lookup parameter; no write path touches the stored `email` column.

## Step 4: Draft shown for approval

```
Just the lookup — stored emails are untouched. We downcase the input before the
`find_by` call, so "User@Example.com" now matches whatever case is already in the DB.
```

One-line question, one-line answer — no padding, no unrelated context.

## After approval

```bash
python $GITLAB post-issue-comment auth-service 42 "Just the lookup — stored emails are untouched..."
python $CACHE annotate-issue work 123 42 replied_note_ids '[987654]'
```
