# Example: Bug report → structured issue

## Input (rough idea from user)
> "users are complaining they can't log in, something about email"

## Output (structured GitLab issue)

**Title:** `Users cannot log in when email address contains uppercase letters`

**Description:**
```
## Problem
Login fails silently when a user's email has uppercase characters (e.g., "User@Example.com").
The auth query does a case-sensitive match against the database, but email addresses are
case-insensitive by RFC 5321. Root cause: missing `.downcase` normalization before DB lookup.

## Expected behavior
Login succeeds regardless of email case. "user@example.com" and "User@Example.com" are the same user.

## Acceptance Criteria
- [ ] Users can log in with any case variation of their registered email
- [ ] A regression test covers mixed-case login attempts
- [ ] Existing users with stored uppercase emails are not affected

## Out of scope
Email normalization on signup (separate issue if needed).
```

**Labels:** `bug`, `backend`, `auth`
