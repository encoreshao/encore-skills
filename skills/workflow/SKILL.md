---
name: workflow
description: Full GitLab development loop — from issue to confirmed-resolved. Covers write-issue, analyze-issue, fix-issue, review-code, create-mr, and post-merge verification.
license: MIT
compatibility: git required. glab CLI optional. GitLab project access required.
metadata:
  author: encore
  version: "1.1"
  tags: gitlab workflow dev pm orchestrator full-loop
---

# Workflow

Full development loop. The goal is not to merge an MR — it's to confirm the problem is actually gone.

## The loop

```
write-issue → analyze-issue → fix-issue → review-code → create-mr → verify
      ↑                                                                  |
      └──────────── new issue from feedback ────────────────────────────┘
```

## Entry points

| Where you are | Start here |
|---------------|------------|
| Have a rough idea or bug report | `write-issue` |
| Have a GitLab issue | `analyze-issue` |
| Have an analysis, ready to code | `fix-issue` |
| Code done, ready to ship | `review-code` |

## Phase guide

### Phase 0: Write Issue
*Skip if issue already exists in GitLab.*

Use `write-issue`. Focus on the root cause, not just the symptom. Define what "fixed" looks like before any code is written.

**Gate:** Issue has a clear problem statement and testable acceptance criteria.

---

### Phase 1: Analyze Issue

Use `analyze-issue`. The goal is to understand the **root cause** — not just read the ticket and start coding.

**Gate:** Root cause identified. No open blockers. Approach defined.

---

### Phase 2: Fix Issue

Use `fix-issue`. Read the existing code before touching it. Fix the root cause, not the symptom. Verify the problem is gone before moving on.

**Gate:** All acceptance criteria met. Problem confirmed gone — not just tests green.

---

### Phase 3: Review Code

Use `review-code`. Start by asking: does this actually solve the problem from the issue? Then check security, correctness, simplicity.

**Gate:** Verdict is "Ready to merge". No open ❌ items.

---

### Phase 4: Create MR

Use `create-mr`. Write a description that tells reviewers what problem was solved and whether it's fixed — in plain language, not a file list.

**Gate:** MR is open, CI is passing, description links to the issue.

---

### Phase 5: After merge — verify in the real environment

This step is skipped too often. Don't skip it.

- Check the target environment (staging or production): does the original problem still occur?
- If you can reproduce the original issue — do it now and confirm it no longer happens
- If the issue isn't auto-closed, close it manually with a comment confirming resolution

```bash
glab issue close <number>
glab issue note <number> --message "Confirmed resolved in <env> after merge."
```

If post-merge verification reveals the fix didn't work: reopen the issue, note what was tried and why it didn't work, and start the loop again from Phase 1 with better information.

## Principles

- **Fix the root cause, not the symptom.** A patch that hides the problem is not a fix.
- **The issue defines done.** When in doubt about whether something is complete, re-read the issue.
- **Small issues, small MRs.** If scope grows, open a new issue. Don't expand the MR.
- **Looping is normal.** Finding a problem in Phase 3 or 4 is better than finding it in production.
