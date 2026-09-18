# Example: reformatting a status-update reply into labeled sections

## Before (posted, then flagged as wrong format)

```
@Frank confirmed, backfill:context_investor_portfolios was re-run on production after your deploy note: `Done. copied=93108 skipped_no_source=0 in 190.0s.`. Since it's idempotent on (investor, company), that catches the stray rows from the gap window, so nothing further needed there. Normalization step (!1339) is merged and its import has already run — Ken's frontend swap to read from the new table is the one remaining open item on this issue.
```

This answers @Frank's question plus reports two more facts (the normalization step, the one open item) in the same paragraph — a reader has to untangle "confirmed and done" from "still open" by re-reading it.

## After (edited in place)

~~~markdown
Confirmed with @Frank: `backfill:context_investor_portfolios` was re-run on production after the deploy.

```
Done. copied=93108 skipped_no_source=0 in 190.0s.
```

**What's done:**

- The backfill is idempotent on `(investor, company)`, so this re-run safely catches the stray rows from the gap window — no further backfill action needed.
- The normalization step (!1339) is merged and its import has already run.

**What remains:**

- Ken's frontend swap to read from the new table is the one open item left on this issue.
~~~

## Why this mapping

The command output is pulled into its own fenced code block instead of an inline backtick-quoted sentence — a multi-field status line (`copied=`, `skipped_no_source=`, timing) is easier to scan as a block than parsed out of prose. The two facts that read as "done, no action needed" go under one heading; the one fact that's still open goes under a separate heading, so a reader who only cares about open items can skip straight to the last section.
