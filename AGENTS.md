# Available Skills

This project uses the [encore-skills](https://github.com/encoreshao/encore-skills) workflow library.
AGENTS.md has no file-import syntax, so skill instructions are NOT duplicated
here — `skills/` stays the single source of truth. When a task matches a
skill's description below, open its SKILL.md at the given path and follow it
before proceeding.

## Skills

| Skill | Path | When to use |
|-------|------|-------------|
| `analyze-issue` | `skills/analyze-issue/SKILL.md` | Read a GitLab issue, identify the root cause (not just symptoms), surface real risks, and produce an implementation approach before writing any code |
| `create-mr` | `skills/create-mr/SKILL.md` | Create a GitLab Merge Request — clear title, high-level summary of what was changed and why, explicit confirmation the issue is resolved |
| `eng-workflow` | `skills/eng-workflow/SKILL.md` | Full GitLab development loop — from issue to confirmed-resolved. Covers write-issue, analyze-issue, fix-issue, review-code, create-mr, summarize-issue, triage-issue, and post-merge verification. |
| `fix-issue` | `skills/fix-issue/SKILL.md` | Implement a fix following the human-thinking loop — understand the root cause, plan the minimal change, implement, verify the problem is actually gone |
| `gitlab-config` | `skills/gitlab-config/SKILL.md` | Wire up GitLab API access — multiple instances, project aliases, tokens. Run this once before any other GitLab skill. |
| `pm-workflow` | `skills/pm-workflow/SKILL.md` | Full PM/designer loop — draft an issue, interact with users and stakeholders to validate it, refine until dev-ready, then finalize |
| `review-code` | `skills/review-code/SKILL.md` | Pre-MR self-review — first confirm the problem is actually solved, then check for security, correctness, and simplicity |
| `summarize-issue` | `skills/summarize-issue/SKILL.md` | After an issue is fixed and its MR is created, summarize the work in high-level markdown and post it as a comment on the GitLab issue |
| `triage-issue` | `skills/triage-issue/SKILL.md` | Use when replying to comments on a GitLab issue, or when an issue has comments that might tag you or be waiting on your reply as assignee — figures out which comments genuinely need a response, drafts each reply grounded in the codebase, and posts after you confirm |
| `write-issue` | `skills/write-issue/SKILL.md` | Turn a rough idea into a well-structured GitLab issue with clear problem statement, root cause, and testable acceptance criteria |

