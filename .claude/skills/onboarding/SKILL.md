---
name: onboarding
description: First-run setup. Get to know the user, fill the "About you" section of CLAUDE.md, and create their profile note, first tags, hubs and weekly schedule; optionally set up Claude memory import. Use when CLAUDE.md still contains placeholders like {{NAME}}, or when the user says "let's get started", "set me up", "onboarding" or "start over".
---

# Onboarding

Goal: turn the empty skeleton into a working second brain that fits the user's life. Keep it a conversation, not a form: ask 2–3 questions at a time. Reply in the user's language; if you don't know it yet, mirror the language of their first message.

1. **Greet and explain** (3–4 sentences): "I'll ask a few questions, then set up your notes, projects and weekly schedule based on your answers. You can change anything later."
2. **Ask** (in small batches):
   - What's your name? Do you want to give me a name to call me by? (Optional; if not, I'm just "your second brain".)
   - Which language should we use?
   - What do you do? Student, employee, freelancer... What are your active projects, courses and interests right now?
   - Anything fixed that repeats every week? (classes, standing meetings, workouts...)
   - Do you already use Claude Code in other project folders? (If yes, their memories can be mirrored here: step 6.)
   - Don't ask about connectors. Check yourself whether any `mcp__claude_ai_*` tools (Calendar, Gmail, Drive, GitHub) are available, and in the final summary say which are connected and that everything works without them.
3. **Propose, get approval.** Turn the answers into a tag and hub table and show it, e.g.:

   | Tag | Hub | Meaning |
   |---|---|---|
   | `project/thesis` | [[Thesis]] | Master's thesis |
   | `course/stat101` | [[STAT101]] | Intro statistics course |
   | `learning/<topic>` | [[Learning]] | Learning topics (existing hub) |

   Use lowercase, hyphenated tag names (`project/website-redesign`). Adjust until the user approves.
4. **Write** (only after approval):
   - `CLAUDE.md` → in `## About you`, replace `{{NAME}}`, `{{ASSISTANT_NAME}}` (use "your second brain" if none), `{{LANGUAGE}}`, `{{ROLES}}` everywhere they appear, and delete the `<!-- SETUP: ... -->` comment. If the user gave the assistant a name, add a line under the intro: "The user calls you <name>; answer to it."
   - `vault/People/<Name>.md` from `System/Templates/Person.md`, with `hub: ["[[People]]", "[[Home]]"]`: who they are, what they do, preferences, working style. Link their hubs under `## Projects`.
   - One hub per project/course in `vault/Hubs/<Hub name>.md`, from `System/Templates/Hub.md`: set `hub_tag`, `tags`, `description`, the tag inside the `base` block, a short description and a first `## Now` line. Remove the `## Places` section if there's nothing for it.
   - New rows in the `vault/System/Tags.md` table (`| Tag | Hub | Meaning |`).
   - `vault/Home.md` → add each hub and the profile note under `## Hubs`.
   - Fixed blocks into `vault/System/Weekly schedule.md` (format `- HH:mm - HH:mm Name [[Hub]] | place | note`), set `created:` and `valid_from:` to today.
   - `vault/System/Changelog.md`: `- YYYY-MM-DD: Initial setup (onboarding).`
5. **Check.** Run `python3 tools/vault_lint.py` and fix any broken links or missing fields you caused.
6. **Claude memory import (optional, only if they said yes in step 2).**
   - Copy `tools/memory_sources.example.json` to `tools/memory_sources.json` (never overwrite an existing one). Set `profile_hub` to the profile note name and empty the example `sources`.
   - Run `python3 tools/import_claude_memory.py --list-new`. For each folder listed, ask: which hub and tags, or `skip`? The folder marked `(this second brain; recommend skip)` is this repo's own session memory from wrap-up: recommend `{"skip": true}` for it instead of asking for a hub. Write the answers into `sources`.
   - Run `python3 tools/import_claude_memory.py`, then lint again. Tell them memories land in `vault/Sources/Claude Memory/` and are read-only (re-sync with "sync memories").
7. **Version it.** Run `git remote -v`. If `origin` points to a public GitHub repo (this project's upstream or a public fork), explain that the vault is personal and offer `git remote rename origin upstream` (keeps updates possible) and, if they have one, `git remote add origin <their-private-repo>`. If there's no `.git`, suggest `git init`. Then suggest `git add -A && git commit -m "Initial setup"`. Run each command only if they say yes.
8. **Show and finish.** List what you created in a few lines. Say which claude.ai connectors are connected (or that none are, and everything works without them). Suggest opening `vault/` in Obsidian and looking at graph view. Then give 3 example requests: "Note: ...", "Plan my day", "What do I know about <project>?".

Rules:
- Write only what the user told you. No guessing in the profile; mark unsure facts `(?)`.
- Never ask for secrets (passwords, ID numbers, API keys); if given, don't write them.
- "start over" on a set-up vault: don't delete anything. Ask what to change, update CLAUDE.md, hubs and tags, and archive obsolete hubs with `status: archived`.
- Use absolute dates (YYYY-MM-DD) everywhere.
