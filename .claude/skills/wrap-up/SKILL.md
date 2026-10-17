---
name: wrap-up
description: Close the session. Record what happened in this session to memory and the daily note, show open ends, and get ready for /clear. Use for "wrap up", "close the session", "I'm done", "switching to a new session", or when a task is finished and the topic changes.
---

# Wrap-up

Goal: a fresh session can pick up exactly where this one left off without ever seeing this conversation.

Reply in the user's language (see CLAUDE.md About you).

1. **Distill.** Scan the session and collect four things: *decision* (what we chose and why), *state* (what's done, last commit), *next step*, *gotcha* (an error that cost time, or something learned). Leave out intermediate steps, abandoned attempts and command output.
2. **Write to memory.** Update the relevant file in Claude Code's auto memory for this project (create it if missing). If auto memory is off, skip this step and put the state in the daily note instead. If there is a "where we left off" status file, overwrite it rather than appending: the old state goes, the new one replaces it. Keep its line in `MEMORY.md` to a single line. Fix or delete old memories that turned out wrong.
3. **Daily log.** If `vault/Daily/YYYY-MM-DD.md` exists, add one line under `## Log`: `- HH:mm <Project>: <what happened>; next: <step>`. If the note doesn't exist, don't create it; just say so.
4. **Open ends.** Show them; don't act on them:
   - `git status --short`: any uncommitted changes?
   - `- [ ]` items written this session that are still unchecked.
   - Background jobs left running.
5. **Report.** At most 5 lines: what went to memory, what went to the daily note, open ends. Last line: "Ready, you can `/clear` now."

Rules: no commit or push (only remind). Don't write to memory what is already in CLAUDE.md or the git history. No relative dates.

Tip, one task, one session: when a task is done and the topic changes, or the context is getting long, suggest running wrap-up and then `/clear`. Long sessions cost more tokens and lose focus.
