# Example: Full workflow loop for a bug fix

## Scenario
Report: "Users can't log in with uppercase emails"

## Phase 0: Write Issue (`write-issue`)
Created issue #42: "Users cannot log in when email contains uppercase letters"
- Root cause: case-sensitive DB lookup
- Acceptance criteria: login works for any email case, regression test added

## Phase 1: Analyze Issue (`analyze-issue`)
- Root cause confirmed: `User.find_by(email: params[:email])` — no normalization
- Risk: index on email column — verify LOWER() doesn't cause full scan
- Decision: use `.downcase` on input (not on stored value)
- Ready to code: yes

## Phase 2: Fix Issue (`fix-issue`)
- Read existing code before touching it ✓
- Plan confirmed: one-line fix + one test
- Implemented + test passes + manually verified

## Phase 3: Review Code (`review-code`)
- Problem solved? Yes — confirmed manually
- Simplest solution? Yes — one line
- Security / correctness: clean
- Verdict: Ready to merge

## Phase 4: Create MR (`create-mr`)
MR !87 opened: "fix: users with uppercase emails can now log in"
- Closes #42 in description
- CI passing

## Phase 5: Post-merge verification
Checked staging: logged in with "User@Example.com" — success.
Issue #42 auto-closed by merge. Confirmed resolved.
