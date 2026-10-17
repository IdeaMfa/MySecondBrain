---
name: sync-memory
description: Mirror Claude Code project memories (~/.claude/projects/*/memory) into vault/Sources/Claude Memory/ and update the hubs. Use for "sync memories", "update from my projects", "add a new project's memory", or when hub information looks stale.
---

# Sync Memory

Reply in the user's language (see CLAUDE.md About you).

1. **Config.** If `tools/memory_sources.json` doesn't exist, offer to create it by copying `tools/memory_sources.example.json`; ask for `profile_hub` (usually the user's person note name) and clear out the example sources.
2. **New folders.** Run `python3 tools/import_claude_memory.py --list-new`. For each listed project folder, ask the user: which hub and tags, or `skip`. The folder marked `(this second brain; recommend skip)` is this repo's own session memory from wrap-up: recommend `{"skip": true}` for it instead of asking for a hub. Write the answers into `sources` in `tools/memory_sources.json`. If a hub doesn't exist yet, offer to create it from `vault/System/Templates/Hub.md` and add the tag to `vault/System/Tags.md`.
3. **Import.** Run `python3 tools/import_claude_memory.py` (use `--dry-run` first if the user wants a preview). The script rewrites `vault/Sources/Claude Memory/` from scratch and redacts secret-like strings.
4. **What changed.** The mirror is gitignored, so `git diff` shows nothing. Run `python3 tools/import_claude_memory.py --dry-run` before importing and compare its file list and summary line with the real run. If an important memory changed, update the affected hub's `## Now` section.
5. **Check.** Run `python3 tools/vault_lint.py` for broken links.
6. **Report.** Short summary: how many notes, which hubs changed and how, how many strings were redacted.

Never hand-edit files in `vault/Sources/Claude Memory/`; the next sync overwrites them. Corrections go into your own note in `Notes/`.
