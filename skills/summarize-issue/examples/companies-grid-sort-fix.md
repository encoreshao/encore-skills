# Example: reformatting a dense fix summary into the template shape

## Before (posted, then flagged as wrong format)

```
Implemented the fix: the companies grid's default sort (no explicit sort column chosen) only used the AI rating when a user had no investment profile, otherwise it fell back to an arbitrary id order. Changed `order_from_params` in `app/models/concerns/ag_grid_module.rb` so the default now sorts by `ml_ratings.rating` (love/like/later/pass) as primary and `ml_ratings.score` as secondary for users with a profile too, matching the AI rating fallback already used for profile-less users. I could not verify this locally: `bundle check` fails with 'Your Ruby version is 3.4.1, but your Gemfile specified 3.4.7' before rubocop/rspec can even run, which looks like an environment issue on the runner rather than anything in this change. Flagging for a human to verify Ruby 3.4.7 is available and re-run the suite before merging.
```

One run-on paragraph mixes the fix, the code change, and a blocking caveat for a human — a reader has to parse the whole thing to find the one part that needs their action.

## After (edited in place)

```markdown
### What's done

Implemented the fix: the companies grid's default sort (when no explicit sort column is chosen) previously only used the AI rating when a user had no investment profile — otherwise it fell back to an arbitrary id order.

Changed `order_from_params` in `app/models/concerns/ag_grid_module.rb` so the default sort now uses `ml_ratings.rating` (love/like/later/pass) as primary and `ml_ratings.score` as secondary for users with a profile too, matching the AI rating fallback already used for profile-less users.

### What remains / needs discussion

Could not verify this locally: `bundle check` fails with `Your Ruby version is 3.4.1, but your Gemfile specified 3.4.7` before rubocop/rspec can even run. This looks like an environment issue on the runner, not something caused by this change.

Flagging for a human to:

- Confirm Ruby 3.4.7 is available in the environment
- Re-run rubocop/rspec before merging
```

## Why this mapping

No separate MR was linked and the root cause was already stated plainly in one sentence, so this skips the template's `## Root cause` and `## MR` sections rather than padding them out — see "omit any section that has nothing to say." The blocking caveat (can't verify locally) gets its own heading instead of trailing off the end of the fix description, because it's the one thing that actually needs a human's action before merge.
