# Issue Summary Format

## Purpose

This format provides executive-level summaries of GitLab issues, focusing on impact and actionability rather than technical minutiae.

## Format Structure

### Header
```
# Issue #{issue_iid}: {title}
Status: {state} | Priority: {labels} | Updated: {relative_time}
```

### Executive Summary (2-3 sentences)
A concise overview answering:
- What is the core problem or request?
- What is the business/user impact?
- What is the current status?

**Guidelines:**
- Avoid technical jargon unless essential
- Focus on "why it matters" not "how it works"
- Use active voice and clear language
- Maximum 3 sentences

**Example:**
```
Users are unable to complete checkout when applying discount codes, resulting in abandoned carts and lost revenue. The issue affects approximately 15% of transactions since the recent payment gateway update. A fix is currently in code review and scheduled for deployment this week.
```

### Key Details

**Problem:**
One-sentence description of the issue from the user/business perspective.

**Impact:**
- Who is affected? (e.g., all users, specific user segment, internal team)
- How severe? (e.g., blocking critical functionality, minor inconvenience)
- Quantifiable impact if available (e.g., error rate, number of users)

**Current Status:**
- What stage is the issue in? (e.g., investigating, fix in progress, blocked)
- Who is assigned?
- Expected timeline or blockers

**Next Steps:**
Clear, actionable items remaining to resolve the issue.

### Context (Optional)

Include only if necessary for understanding:
- Related issues or dependencies
- Recent activity summary (if extensive conversation)
- Links to relevant documentation or discussions

## Formatting Guidelines

1. **Length:** Keep total summary under 200 words
2. **Tone:** Professional, objective, action-oriented
3. **Links:** Include issue link and any critical references
4. **Timestamps:** Use relative time (e.g., "2 days ago") not absolute dates
5. **Labels:** Surface priority/type labels prominently
6. **Comments:** Summarize key points from long comment threads, don't repeat everything

## Example Full Summary

```markdown
# Issue #247: Checkout fails with discount codes

Status: In Progress | Priority: Critical, Bug | Updated: 2 hours ago

## Executive Summary

Users are unable to complete checkout when applying discount codes, resulting in abandoned carts and estimated 12% revenue loss over the past 3 days. The root cause has been identified as a validation error in the payment gateway integration introduced in v2.3.1. A hotfix is currently under code review and targeted for production deployment within 24 hours.

## Key Details

**Problem:**
Discount code validation fails during checkout, preventing order completion.

**Impact:**
- Affects: All users attempting to use discount codes (~15% of checkout attempts)
- Severity: Critical - blocking revenue-generating functionality
- Volume: Approximately 300 failed transactions over 72 hours

**Current Status:**
- Root cause identified in payment gateway validation logic
- Fix implemented and under code review (MR !89)
- Assigned to: @dev-team-payments
- Blocker: Awaiting approval from security team

**Next Steps:**
1. Complete security review of payment gateway changes
2. Deploy hotfix to production
3. Monitor error rates post-deployment
4. Investigate refund process for affected users

## Context

Related to the payment gateway upgrade (Issue #201). Initial investigation revealed the issue was introduced when updating discount code validation to support the new gateway API. The fix reverts to the previous validation approach while maintaining compatibility with the new gateway.
```

## Anti-Patterns to Avoid

❌ **Don't:**
- Include full stack traces or code snippets in executive summary
- List every comment in chronological order
- Use vague language like "might be" or "possibly"
- Include internal technical debates unless critical to understanding
- Bury key information deep in the summary

✅ **Do:**
- Lead with business impact
- Be specific about status and timeline
- Surface actionable next steps clearly
- Use concrete numbers when available
- Make it scannable with clear sections
