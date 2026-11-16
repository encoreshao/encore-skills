# Example: release MR !1331 (camp)

**Input:** release MR whose included MRs are #1322, #1325-#1330 (authors: keira, benedict, axel).

**Output** (opening line G, fits because the release has three clear themes):

```markdown
This release focuses on smoother queues, a tidier dashboard, and better Japan support. The details, by area:

### **1. Queue & Mission Control**

* **Queue Position Display:** Queue status now reads "In line, N of M" and is live in production. The position is paired with the queue total, so it can no longer exceed it. ([#1325](https://gitlab.example.com/group/camp/-/merge_requests/1325), [#1328](https://gitlab.example.com/group/camp/-/merge_requests/1328), [#1330](https://gitlab.example.com/group/camp/-/merge_requests/1330)) · @benedict

### **2. Worth Attention**

* **Worth Attention Dashboard:** The v2 dashboard list is now split into three groups, so it's easier to scan. Investor profile filters are simpler too. ([#1322](https://gitlab.example.com/group/camp/-/merge_requests/1322), [#1329](https://gitlab.example.com/group/camp/-/merge_requests/1329)) · @keira

### **3. Localization**

* **Japan Market Localization:** Japanese market names now display correctly, and firm-type labels in the Sankey chart are localized. ([#1327](https://gitlab.example.com/group/camp/-/merge_requests/1327)) · @axel
```

Compared with the old description: no `ccing` line, numbers are links instead of backticked text, authors are on each feature, and the opening line is varied.
