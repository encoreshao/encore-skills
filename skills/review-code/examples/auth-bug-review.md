# Example: Self-review of the auth bug fix

## Input
```bash
git diff origin/main
```

Diff shows: one line changed in `auth_service.rb`, one new test in `auth_service_spec.rb`.

## Output

```
## Self-review: fix/42-uppercase-email-login

### Does it solve the problem?
Yes. Issue #42 reported login failure for uppercase emails. The fix normalizes the input
email to lowercase before the DB lookup. Manually verified: login succeeds with mixed-case email.

### ✅ Looks good
- Fix targets the root cause (case-sensitive lookup), not a symptom
- Change is minimal: one line
- Regression test added that would fail without the fix
- No existing tests broken

### ⚠️ Suggestions (non-blocking)
- Consider adding a database constraint or model callback to normalize email on write too,
  so stored emails are always lowercase. This would prevent the inverse case. Track as a
  separate issue.

### ❌ Must fix
- None

### Verdict: Ready to merge
```
