# Example: turning an action-based summary into a goal-based one

## Before (posted, then flagged as wrong format)

```
Opened merge request for this fix: loop/issue-1362 → staging. Verified by the loop with:
- `RAILS_ENV=test bundle exec rspec spec/services/mcp/create_organization_tool_spec.rb spec/services/manual_inputs/creator_spec.rb spec/requests/api/mcp` ✅
- `bundle exec rubocop . --cache false` ✅

Added an MCP tool, `create_organization`, so users can add a company that isn't in Kurrant yet by giving its domain (name is optional). It reuses `ManualInputs::Creator`, which normalizes the domain, returns the existing company instead of making a duplicate, rejects blank or blacklisted domains, and queues the company for scraping and enrichment. The tool is registered in `Api::Mcp::ServerController::RAILS_TOOLS` and has its own spec.
```

It leads with the branch and full commands, then a paragraph of class names — all of which the MR description already carries. A reader has to dig to find whether the issue's goal was met.

## After

```markdown
**Merge request:** !1400 → `staging` — open, awaiting review

**Goal:** users can add a company that isn't in Kurrant yet from the MCP client, by its domain alone.
- A known domain returns the existing company instead of creating a duplicate
- Blank or blacklisted domains are rejected with a clear error
- New companies are queued for scraping and enrichment automatically
- Checks: 2/2 passed ✅ (commands in the MR)
```

## Blocked variant

When it didn't land, swap **Goal** for **Blocked on** and give the human action its own line:

```markdown
**Merge request:** !1388 → `staging` — open, not verified

**Blocked on:** the test suite can't start on the runner (Ruby 3.4.1 installed, Gemfile wants 3.4.7).
- The default companies-grid sort now uses the AI rating for users with an investment profile too
- **Needs:** Ruby 3.4.7 on the runner, then rerun lint and tests before merging
```
