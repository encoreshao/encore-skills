# Example: Summary comment for the auth bug fix

## Input
Issue #42 fixed, MR !87 merged (see `create-mr`'s example).

## Output — posted as an issue comment

```markdown
**Merge request:** !87 → `main` — merged

**Goal:** users can log in no matter how they capitalize their email.
- "User@Example.com" now signs in to an account stored as "user@example.com"
- The original failure was reproduced first and is gone after the fix
- Checks: 2/2 passed ✅ (commands in the MR)
```

The `AuthService` change and the regression test are how it was done — they're in the MR description, not here.
