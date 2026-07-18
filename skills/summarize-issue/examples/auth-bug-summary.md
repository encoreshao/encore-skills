# Example: Summary comment for the auth bug fix

## Input
Issue #42 fixed, MR !87 merged (see `create-mr`'s example).

## Output — posted as an issue comment

```markdown
## Summary

Users with uppercase characters in their email (e.g. "User@Example.com") couldn't log in
because the auth lookup was case-sensitive. The lookup now normalizes the email to
lowercase before querying, so any case variant matches the stored account.

## Changes

- Normalize the email input to lowercase in `AuthService` before the `find_by` call
- Added a regression test covering mixed-case login

## Verified

- Reproduced the original failure, confirmed it's gone after the fix
- Manually logged in with "User@Example.com" against an account stored as lowercase
- Tests pass

## MR

!87 — merged
```
