# Example: release MR for Loop X

**Input:** release MR whose included MRs are !398, !405, !409, !412, !418, !421 (authors: mira, tomas, priya, jonas; names are made up).

**Output** (opening line G, fits because the release has three clear themes):

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

Compared with an old-style description: no `ccing` line, numbers are links instead of backticked text, authors are on each feature, and the opening line is varied.
