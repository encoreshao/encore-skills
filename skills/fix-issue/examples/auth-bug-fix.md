# Example: Fixing the login uppercase email bug

## Input
Analysis from #42 — root cause: case-sensitive email lookup in auth_service.rb

## Phase 1: Understand before touching anything

Read `app/services/auth_service.rb`. Found:
```ruby
user = User.find_by(email: params[:email])
```
Confirmed: no normalization. Root cause matches analysis.

## Phase 2: Plan

- Add `.downcase` to the email parameter before the lookup
- Do NOT normalize the stored email (out of scope, separate issue)
- Tricky part: ensure the fix doesn't break users who have uppercase stored — it won't,
  because we're normalizing the input, not the stored value

Plan confirmed.

## Phase 3: Implement

```ruby
# app/services/auth_service.rb
user = User.find_by(email: params[:email].downcase)
```

Test first:
```ruby
# spec/services/auth_service_spec.rb
it "authenticates user regardless of email case" do
  user = create(:user, email: "user@example.com")
  result = AuthService.authenticate("User@Example.com", "password")
  expect(result).to eq(user)
end
```

## Phase 4: Check own work

- Root cause fixed: yes, the lookup now normalizes input
- Security: no issues — downcase is safe
- Existing tests: pass (ran full suite)
- API contract: unchanged

## Phase 5: Verify problem is gone

Manually tested: logged in with "User@Example.com" against account stored as "user@example.com" → success.

## Commit
```bash
git commit -m "fix(auth): normalize email to lowercase before lookup

Closes #42"
```
