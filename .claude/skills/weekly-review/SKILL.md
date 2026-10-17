---
name: weekly-review
description: Weekly review. Scan the past week's daily and meeting notes, open action items and the state of each hub; write a weekly summary and next week's plan. Use for "review my week", "weekly review", "how did this week go".
---

# Weekly Review

Reply in the user's language (see CLAUDE.md About you).

1. Read the last 7 days of `vault/Daily/` and `vault/Meetings/` notes (use the `librarian` subagent if there are many).
2. For each active hub: what moved forward, what got stuck, open action items (`- [ ]`) and who owns them.
3. Highlight forgotten work: open action items older than 7 days, active hubs untouched for more than 14 days.
4. Write `vault/Daily/YYYY-Www Weekly review.md` (ISO week) with `type: note`, `created`, `tags: [weekly]`, `hub: ["[[Home]]"]`, `description`, and the headings `## Summary`, `## By hub`, `## Stuck`, `## Next week's focus`. Link every hub and note you mention.
5. Update the hubs' `## Now` sections. Agree on next week's 3 focuses with the user.
