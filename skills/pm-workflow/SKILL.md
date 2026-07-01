---
name: pm-workflow
description: Full PM/designer loop — draft an issue, interact with users and stakeholders to validate it, refine until dev-ready, then finalize
license: MIT
compatibility: GitLab project access required. glab CLI optional. No codebase required.
metadata:
  author: encoreshao
  version: "1.0"
  tags: gitlab pm product designer workflow issue feedback stakeholder no-code
---

# PM Workflow

The PM loop is not about code — it's about getting the problem definition right before anyone writes a line. A vague issue creates vague work. Your job is done when a developer can pick this up and start without asking you a single question.

## The loop

```
write-issue → share → gather-feedback → synthesize → refine → validate → finalize
      ↑                      |
      └───────── iterate ────┘
```

## Entry points

| Where you are | Start here |
|---------------|------------|
| Rough idea, bug report, user complaint | Phase 1: Draft |
| Issue drafted, not yet shared | Phase 2: Share |
| Feedback collected, need to update issue | Phase 4: Synthesize |
| Issue refined, checking if it's ready | Phase 5: Validate |

---

## Phase 1: Draft the issue

Use `write-issue`. Don't try to be complete — a good draft is specific about the problem and honest about what's still unknown.

**Gate:** The issue has a clear problem statement, a best-guess root cause, and at least draft acceptance criteria.

---

## Phase 2: Share with stakeholders

Post the issue link and ask for structured feedback — not just "does this look right?"

```bash
# Post to GitLab and get the URL
GITLAB="$HOME/.claude/skills/gitlab-config/scripts/gitlab_api.py"
python $GITLAB get-issue <project> <issue_iid>   # confirm it's visible

# Or create it first if still a draft
glab issue create --title "TITLE" --description "DESCRIPTION"
```

Who to share with:
- **Users affected** — do they recognize this as their problem?
- **Stakeholders** — is this the right priority? any constraints?
- **Designer** (if applicable) — any UX implications missed?
- **Tech lead** — is the proposed approach feasible? any hidden complexity?

Ask specific questions, not open ones:
- "Does this match what you reported in [original report]?"
- "Is acceptance criterion #2 testable from your side?"
- "What would make this out of scope?"

---

## Phase 3: Gather feedback

Collect responses. Document them directly — don't rely on memory.

Track each piece of feedback as:

```
[Source] [Type: clarifies / contradicts / adds / removes] — <what they said>
```

Examples:
```
[User A] clarifies — the bug only happens on mobile, not desktop
[Tech Lead] adds — this touches the auth service, needs security review
[Stakeholder] contradicts — out of scope for this quarter, defer to Q3
```

Keep collecting until one of these is true:
- You have responses from all critical stakeholders
- New feedback is no longer changing anything (saturation)
- A blocker has emerged that requires a decision before continuing

---

## Phase 4: Synthesize

Before updating the issue, process what you heard:

1. **What changed?** — requirements that need updating
2. **What's consistent?** — confirmed and solid, no action needed
3. **What conflicts?** — two stakeholders said opposite things; you must decide or escalate
4. **What's new scope?** — things that came up that belong in a separate issue

For conflicts: make a call and document the reasoning. Don't leave ambiguity in the issue — that's what a developer will hit at 11pm.

For new scope: open a linked issue. Don't expand this one.

---

## Phase 5: Refine the issue

Update the issue based on synthesis. Edit the original — don't add a comment with the changes.

What to update:
- **Title** — still accurate after feedback?
- **Problem statement** — clearer root cause?
- **Acceptance criteria** — testable, specific, complete?
- **Out of scope** — explicitly list what this does NOT cover
- **Open questions** — remove resolved ones; flag any still unresolved

```bash
# Update via API
GITLAB="$HOME/.claude/skills/gitlab-config/scripts/gitlab_api.py"
# Edit the issue directly in GitLab UI, or use glab:
glab issue update <issue_iid> --description "UPDATED_DESCRIPTION"
```

---

## Phase 6: Validate — is it dev-ready?

Read the issue as if you've never seen it. Ask:

- [ ] Could a developer start on this without asking me a single question?
- [ ] Is every acceptance criterion specific and testable?
- [ ] Is the root cause identified (for bugs) or clearly stated (for features)?
- [ ] Is the scope boundary explicit — what's in and what's out?
- [ ] Are there any open questions still unresolved?

If any answer is "no" — go back to Phase 2 or Phase 5 and close the gap.

If all answers are "yes" — the issue is ready.

---

## Phase 7: Finalize

Mark it ready and hand it off.

```bash
GITLAB="$HOME/.claude/skills/gitlab-config/scripts/gitlab_api.py"

# Add labels to signal dev-ready
glab issue update <issue_iid> --label "ready-for-dev"

# Post a comment summarizing what was validated
python $GITLAB post-issue-comment <project> <issue_iid> \
  "Issue validated with stakeholders. Ready for dev. Key decisions: <summary of any non-obvious calls made>"

# Assign if known
glab issue update <issue_iid> --assignee <developer-handle>
```

Notify the developer or team in whatever channel they use. Don't just change the label and disappear — confirm they've seen it.

---

## Principles

- **The issue is the contract.** Whatever you write in acceptance criteria is what gets built. Be precise.
- **One issue, one problem.** If scope grows, open a new issue. Don't expand this one mid-flight.
- **Conflicts belong in the issue, not in your head.** If you made a call, write it down and why.
- **Iterate fast, then stop.** Two rounds of feedback is usually enough. Three is the max. After that, you're polishing, not improving.
- **Done means a developer can start.** Not "done means everyone agreed." Consensus is nice; clarity is required.
