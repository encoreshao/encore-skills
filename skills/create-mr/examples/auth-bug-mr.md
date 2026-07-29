# Example: MR for the auth bug fix

## Title
```
fix: #42 users with uppercase emails can now log in
```

## Description

```markdown
## What and why

Closes #42

- Problem: users with uppercase characters in their email (e.g., "User@Example.com") couldn't log in — the auth lookup was case-sensitive
- Fix: normalize the input email to lowercase before the database query
- Result: root cause confirmed and resolved

## How

- Added `.downcase` to the email parameter in `AuthService` before the `find_by` call — no stored data changes, only the lookup input is normalized

## Verified

- [x] Original problem reproduced and confirmed fixed
- [x] Tests pass
- [x] Manually tested: logged in with "User@Example.com" against account stored as lowercase
```
