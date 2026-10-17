---
name: garden
description: Vault maintenance. Find and fix broken links, notes without tags or hub, orphan notes; link recurring concepts; propose merging similar notes. Use for "tidy the vault", "fix the links", "do maintenance", "garden".
---

# Garden

Reply in the user's language (see CLAUDE.md About you).

1. Run `python3 tools/vault_lint.py` and read the report.
2. Make the easy fixes directly: missing `hub`/`tags`, broken links with an obvious spelling difference, tags missing from `vault/System/Tags.md` (add them, or correct the note).
3. **Auto-linking:** if another note's title appears as plain text in `Notes/` or `Meetings/` without a link, turn its first occurrence into `[[...]]`. For concepts that appear in 2+ notes but have no note of their own, open a `type: concept` note.
4. Propose risky changes (merging, renaming, archiving) as a list and get approval. Archive = add `status: archived` to the frontmatter; never delete a note.
5. Never edit `vault/Sources/Claude Memory/`; it is a read-only mirror. If something there is wrong, re-run `sync-memory` or write a correction note in `Notes/`.
6. At the end, run the lint again and report the before/after counts.
