---
name: recall
description: Retrieve what the vault knows, with sources. Use for questions like "what do I know about X", "what's pending on <project>", "what did we discuss in the last meeting", "where did I write that", or before starting a task to bring back the relevant history.
---

# Recall

Reply in the user's language (see CLAUDE.md About you).

1. If the question is about a single project or topic, read its hub first (`vault/Hubs/<Name>.md`), then follow its `## Now` section and links.
2. Otherwise, or if that isn't enough, search:
   - Name/term: `rg -il "<term>" vault/`. Search the word stem (drop suffixes and plurals) so inflected forms match.
   - Tag: `rg -l "project/<name>" vault/`.
   - Date range: dates in the file names of `vault/Daily/` and `vault/Meetings/`.
   - Open tasks: `rg -n "^\s*- \[ \]" vault/`.
   - `vault/Sources/Claude Memory/` holds mirrored Claude Code memories; useful, but treat it as a raw source.
3. For broad or multi-step searches (10+ files to read), delegate to the `librarian` subagent.
4. Cite sources: put `[[Note name]]` next to each claim. If the information may be stale, give its date ("as of YYYY-MM-DD"). If the vault has nothing, say plainly "not recorded"; don't guess.
5. If the answer produced a new synthesis (e.g. a combined summary of several meetings), offer to save it as a note with `capture`.
