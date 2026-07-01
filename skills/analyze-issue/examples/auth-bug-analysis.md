# Example: Analyzing a login bug issue

## Input
GitLab issue #42: "Users cannot log in when email contains uppercase letters"

## Output

```
## Analysis: #42 — Users cannot log in when email contains uppercase letters

### Root cause
The authentication query does a case-sensitive string comparison against the stored email.
Email addresses are case-insensitive (RFC 5321), so "User@Example.com" does not match
"user@example.com" in the DB even if they are the same user.

### Requirements
- [ ] Explicit: Login must work for any case variant of the user's email
- [ ] Explicit: Regression test required per acceptance criteria
- [ ] Implicit: Must not break existing users who have uppercase emails stored
- [ ] Implicit: Performance must not degrade (no full-table scan from lowering at query time)

### Risks
- Changing the lookup to use LOWER() may miss an index → check if email column is indexed
- Users with stored uppercase emails may have a mismatch if we normalize on lookup but not on write
  → Mitigation: normalize on lookup only; do not touch stored values

### Blockers
- [ ] None — root cause is clear, approach is straightforward

### Approach
Add .downcase (or DB-level LOWER()) to the email parameter before the auth query.
Affected file is likely auth_service.rb or sessions_controller.rb.
Add a test that logs in with "User@Example.com" when stored email is "user@example.com".
Complexity: small.

### Files likely affected
- `app/services/auth_service.rb` — where the DB lookup happens
- `spec/services/auth_service_spec.rb` — where the regression test goes

### Ready to code? Yes
```
