---
name: release-mr
description: Write the description for a GitLab release MR — a casual opening line, changes grouped by feature area, every number linked to its MR, and the author @mentioned on each feature. Use when asked to write, rewrite or post release MR notes or a release summary.
license: MIT
compatibility: glab CLI authenticated to the GitLab instance.
metadata:
  author: encoreshao
  version: "1.3"
  tags: gitlab release mr release-notes changelog summary
---

# Release MR notes

Loop X (`loop-x` repo, `crates/core/src/release_mr/render.rs`) renders its own release MR descriptions in code with the same opening lines and format rules; it does not read this skill. Change both together.

Produce the description of a release MR: a short opening line, then features grouped by area, each with MR links and its author.

## Steps

1. **Collect the included MRs.** Read the release MR (`glab api projects/<path>/merge_requests/<iid>`) and its commits or the MRs it merges. Note each MR's `iid`, `title` and `author.username`.
2. **Use the author, not the assignee.** They can differ; the author is who gets tagged.
3. **Group by feature area** (for example Queue & Mission Control, Worth Attention, Localization). Merge MRs that belong to one feature into one bullet. Skip chore-only MRs unless user-visible.
4. **Write each bullet** as `**Feature name:** one or two plain sentences on what changed and the benefit. (links) · @author`. Vary the sentence shape so bullets don't all read "X is now Y".
5. **Link every number.** Format `[#1325](https://<host>/<project-path>/-/merge_requests/1325)`, never bare or in backticks. The numbers are usually MRs. If an MR title references a real issue (`#1407`), link the MR and mention the issue only if it is in the same project.
6. **Opening line:** pick one of A to H below at random, skipping any that don't fit the content. Use G only when you can name the release's three main themes.
7. **No `ccing` line at the top.** The per-feature `@author` mentions do the notifying. Several authors on one feature: `· @a @b`.
   - A commit in the release with no MR of its own: tag its commit author on the closest feature and say so when reporting back.
   - Keep one author set per bullet. If a catch-all bullet mixes MRs from different authors, give each MR group its own `· @author` instead of one trailing set.
8. **Before posting,** read the current description so nothing real is overwritten. Then update with `glab api -X PUT projects/<path>/merge_requests/<iid> -F "description=@file.md"`. Posting only when asked. No AI attribution lines.

## Opening lines

- A) Here's what's shipping in this release, grouped by feature area:
- B) This release rounds up a handful of improvements, sorted by area:
- C) Quick tour of what's new, by feature area:
- D) A few things got better in this release. Here's the rundown by area:
- E) Fresh from the branch: this release's changes, grouped by feature area.
- F) Short version of what's changed, organized by area so you can jump to what matters to you:
- G) This release focuses on <theme>, <theme>, and <theme>. The details, by area:
- H) What you'll notice in this release, area by area:

## Example

Full version: `examples/loopx-release.md` (project, people and links are made up).

```markdown
This release focuses on Slack control, chat organisation, and project memory. The details, by area:

### **1. Slack & Agents**

* **Slack Agent:** Mention `@LoopX` in a channel, thread or DM and it starts a loop or an ad-hoc task on your Mac, then replies in the thread with progress and the result. Setup lives in Settings, and replies are escaped so they can't ping a channel. ([#412](https://gitlab.example.com/acme/loop-x/-/merge_requests/412), [#418](https://gitlab.example.com/acme/loop-x/-/merge_requests/418)) · @mira @tomas
* **Cursor Agent for Creator:** Generate, Showcase and Retry now run on Cursor Agent when it's your selected AI CLI, and the job log follows its output. ([#421](https://gitlab.example.com/acme/loop-x/-/merge_requests/421)) · @priya

### **2. Chat**

* **Chat History Folders:** File chats into folders by dragging them over or using the folder menu on each chat, and rename or delete a folder without losing its chats. ([#405](https://gitlab.example.com/acme/loop-x/-/merge_requests/405), [#409](https://gitlab.example.com/acme/loop-x/-/merge_requests/409)) · @jonas

### **3. Insights & Memory**

* **Project Memory Graph:** The Memory page now has a graph of projects, linked only where there is evidence, with zoom, filters and a one-page summary for each node. ([#398](https://gitlab.example.com/acme/loop-x/-/merge_requests/398)) · @priya
```
