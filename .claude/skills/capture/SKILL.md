---
name: capture
description: Save a fact, idea, decision or learning note to the vault as an atomic note; tag it, link it to its hub and related notes. Use for "take a note", "save this", "remember that", "I learned that", or whenever a lasting piece of information comes up in conversation. For "process the inbox", apply the same steps to every file in Inbox.
---

# Capture

Reply in the user's language (see CLAUDE.md About you).

1. **Search.** Before writing, check whether a note on this already exists: `rg -il "<key term>" vault/Notes vault/Meetings vault/Hubs`. If it does, update it instead of opening a new one.
2. **Classify.** Pick the right tag(s) from `vault/System/Tags.md`. If nothing fits, propose a new tag; if the user approves, add it to the dictionary and open a hub if needed (copy `vault/System/Templates/Hub.md`).
3. **Write.** `vault/Notes/<Title>.md` with the frontmatter schema from CLAUDE.md. One note, one idea. Keep the user's own words; don't invent additions. Mark unsure facts with `(?)`. Absolute dates only.
4. **Link.**
   - `hub:` field: the relevant hub(s).
   - In the body, `[[...]]` to the people, projects and concepts mentioned. If a concept without its own note now appears in 2+ notes, open a short `type: concept` note for it.
   - If useful, add a backlink line to related older notes (one line is enough).
5. **Daily log.** If today's `vault/Daily/YYYY-MM-DD.md` exists, add `- HH:mm [[Note]] added` under `## Log`.
6. **Report.** One line: which file, which tags.

Processing the inbox: for each file run steps 2–4, then move it from `Inbox/` to `Notes/` (or `Meetings/`). Collect anything ambiguous into one batch of questions.

Never write secrets (passwords, tokens, API keys) into the vault. For confidential work, keep only method, decisions and task tracking, never the real data.
