---
name: plan-day
description: Plan the user's day hour by hour and write it to vault/Daily/YYYY-MM-DD.md. Use for "plan my day", "what should I do today", "plan tomorrow", "my schedule". Also use for the end-of-day close ("close the day", "end of day").
---

# Plan Day

Reply in the user's language (see CLAUDE.md About you).

## Planning
1. **Gather** (as much as you can find; if a source is missing, skip it and say so):
   - `vault/System/Weekly schedule.md`: the fixed blocks for that weekday (classes, recurring meetings, workouts...). Always read this first; remind the user of any `⚠️` conflicts or open questions in it.
   - Any schedule the user gave in this conversation.
   - Google Calendar events, only if the claude.ai Google Calendar connector is connected. If it isn't, skip it and say so.
   - Open tasks in the vault: `rg -n "^\s*- \[ \]" vault/Meetings vault/Notes vault/Daily`. Yesterday's `## End of day` → `- Carried over:` items.
   - The `## Now` sections of active hubs and upcoming deadlines.
2. **Prioritise.** Fixed events first, then whatever has the nearest deadline. Deep-work blocks of 90 min with 15 min breaks. Be realistic: at most 3 big focuses per day. Carried-over items go to the top.
3. **Propose.** Show the plan as a table and get approval.
4. **Write.** After approval, if the daily note doesn't exist, create it from `vault/System/Templates/Daily.md` (fill in the template variables). Write `## Plan` in Day Planner format:
   ```
   - [ ] 09:00 - 10:30 Homepage wireframes [[Website Redesign]]
   - [ ] 11:00 - 11:30 Weekly team sync [[Website Redesign]]
   ```
   Write the day's 1–3 goals under `## Focus`.
5. **Optional.** If the user asks, put the blocks on their calendar. Show exactly what will be written first and get explicit approval.

## End of day ("close the day")
- Go through checked and unchecked plan items with the user and fill `## End of day`: `- Done:` and `- Carried over:`.
- Carried-over items go first in the next planning.
- Absolute dates only; never write "tomorrow".
