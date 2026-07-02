# Example: MR for the auth bug fix

## Title
```
fix: #42 users with uppercase emails can now log in
```

## Description

```markdown
Closes #42

Users with uppercase characters in their email address (e.g., "User@Example.com") were
unable to log in because the auth lookup was case-sensitive. Fixed by normalizing the input
email to lowercase before the database query. Root cause confirmed and resolved.

## How

Added `.downcase` to the email parameter in `AuthService` before the `find_by` call.
No stored data is changed — only the lookup input is normalized.

## Verified

- [x] Original problem reproduced and confirmed fixed
- [x] Tests pass
- [x] Manually tested: logged in with "User@Example.com" against account stored as lowercase
```
