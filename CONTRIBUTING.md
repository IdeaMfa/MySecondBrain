# Contributing

Issues and pull requests are welcome: bug reports, clearer skills, new workflows, better tools.

- **Keep it in English.** Code, comments, skills and docs. (Skills still tell Claude to reply in the user's language.)
- **Keep it generic.** No personal names, projects, paths or notes. Examples use a fictional person (Alex Rivera, a product designer).
- **Never commit vault content.** The repo ships an empty vault skeleton. Don't add notes from your own vault, and check `git diff` before you push.
- **Python 3 standard library only.** No dependencies. Derive paths from the repo location; never hard-code home paths.
- **Keep skills short.** Numbered steps, bold verbs, practical tone. If a skill changes a format (frontmatter, daily headings, tags), update `CLAUDE.md`, the templates and the lint to match.
- **Don't loosen the safety model.** Changes to `tools/external_guard.py` or `.claude/settings.json` must keep the fail-closed behaviour and come with tests.

Before opening a PR:

```bash
python3 -m unittest discover tests
python3 tools/vault_lint.py
```

Both should pass on the skeleton vault (the lint should report 0 issues).

By contributing you agree that your contribution is licensed under the [MIT License](LICENSE).
