# MySecondBrain

[![tests](https://github.com/IdeaMfa/MySecondBrain/actions/workflows/tests.yml/badge.svg)](https://github.com/IdeaMfa/MySecondBrain/actions/workflows/tests.yml)

A personal "second brain" you talk to in [Claude Code](https://claude.com/claude-code) and look at in [Obsidian](https://obsidian.md).

You don't write the notes, you tell them. Claude writes each note, tags it, links it to related notes and projects, and finds it again with sources when you ask. Everything stays on your computer as plain Markdown files.

The repo is an empty skeleton: rules, workflows, a few small scripts and an empty vault. On first run Claude asks you a few questions and sets the system up around your projects, courses and weekly routine.

![Demo: a note is told to Claude Code in the terminal, saved with tags and links, found again with sources, and shown in Obsidian](docs/images/demo.gif)

<sub>Screenshots come from a demo vault with fictional content (Alex Rivera, a product designer).</sub>

## A session looks like this

```
> note: we're going with Source Serif for body text, it reads better at small sizes
Saved Notes/Why we chose a serif for body text.md (project/website-redesign, learning/typography), linked to [[Website Redesign]].
> what's pending on the website redesign?
- Homepage wireframes with the new font, due 2026-03-06 [[2026-03-02 Website Redesign weekly]]
- Font web license check (Sam), due 2026-03-04 [[2026-03-02 Website Redesign weekly]]
```

## Why

- **Notes that get written.** Saying "note: we're moving the launch to 2026-05-04" in the terminal you already have open takes less effort than opening a notes app and filing a note.
- **Structure without filing.** Claude picks the tags, the hub and the links. The graph grows on its own.
- **Answers with sources.** "What did we decide about the logo?" comes back with the decision and a link to the note it came from.
- **Plain files.** No database, no lock-in. It's Markdown in a folder you version with git, readable with or without Claude.
- **A system you can change.** The rules live in one file (`CLAUDE.md`) and the workflows are short Markdown recipes. If something doesn't suit you, tell Claude to change it.

## How it works

| Piece | Where | What it does |
|---|---|---|
| Rules | `CLAUDE.md` | Who you are, the note schema, writing rules, hard rules, external content safety. Claude reads it every session. |
| Workflows (skills) | `.claude/skills/` | Step-by-step recipes for each job: capture, recall, plan-day, ingest-meeting, ingest-video, and more. |
| Librarian | `.claude/agents/librarian.md` | Read-only subagent for broad vault searches, so your main session's context stays small. |
| Hooks | `.claude/settings.json` | Session-start status summary, plus the guard on external connectors. |
| Tools | `tools/` | `vault_lint.py` (health check), `session_start.sh` (status summary), `external_guard.py` (connector guard), `import_claude_memory.py` (memory mirror). Python 3 standard library only. Plus the optional `youtube/` tool (video → transcript), which keeps yt-dlp in its own venv. |
| Vault | `vault/` | Your notes. Obsidian opens this folder. |
| Tests | `tests/` | `python3 -m unittest discover tests` |

At the start of every session Claude gets a status summary: today's date, whether today's daily note exists, how many Inbox items and new meeting or video transcripts are waiting, and the vault's lint result.

## Requirements

- **Claude Code** with a Claude Pro or Max subscription (or an API key).
- **Obsidian** 1.9 or later (free). The hubs use the core **Bases** plugin; older versions show them as code blocks.
- **Python 3** (standard library only) and **git**.
- Optional: [ripgrep](https://github.com/BurntSushi/ripgrep) (`rg`). The skills search with it; without it Claude falls back to its own search tool.
- Optional, for YouTube videos: [Node.js](https://nodejs.org/). The video tool installs [yt-dlp](https://github.com/yt-dlp/yt-dlp) into its own folder on first run.

## Install and quick start (~15 minutes)

1. **Clone** the repo somewhere permanent:
   ```bash
   git clone https://github.com/IdeaMfa/MySecondBrain.git ~/Documents/MySecondBrain
   cd ~/Documents/MySecondBrain
   git remote rename origin upstream   # your vault is personal; never push it to a public repo
   ```
   Your notes are personal. If you want a remote, push to a **private** repo of your own, not to a public fork (see FAQ).
2. **Open Claude Code** in the folder: run `claude`. Accept the folder trust prompt. That prompt also enables the hooks in `.claude/settings.json`.
3. **Run onboarding.** Type **"let's get started"**. Claude asks a few questions, two or three at a time: your name, an optional name for the assistant, your language, what you do, your projects and courses, and fixed weekly blocks. It then proposes a tag and hub table. After you approve it, Claude:
   - fills the `## About you` section of `CLAUDE.md`,
   - creates your profile note in `vault/People/`,
   - creates one hub per project or course and adds the tags to `vault/System/Tags.md`,
   - fills in `vault/System/Weekly schedule.md`,
   - runs the lint, and optionally sets up Claude memory import and a first git commit.
4. **Open `vault/` in Obsidian**: "Open folder as vault", then pick the `vault` folder (not the repo root). Look at graph view.
5. **Start talking:** "Note: ...", "Plan my day", "What do I know about <project>?"

Optional: enable Google Calendar, Gmail, Google Drive or GitHub as connectors in your claude.ai settings. They appear in Claude Code when you log in with that claude.ai account (not with an API key). With Calendar connected, "plan my day" also reads your calendar. The guard covers these claude.ai connectors only; MCP servers you add yourself for the same services are not guarded unless you add their tool prefix to the matchers in `.claude/settings.json` (see [Safety model](#safety-model-for-external-content)).

## Skills

Ask in plain language, in any language. These are example phrasings:

| Skill | Say | What happens |
|---|---|---|
| `onboarding` | "let's get started", "set me up", "start over" | First-run setup: profile, tags, hubs, weekly schedule. "start over" adjusts and never deletes. |
| `capture` | "Note: ...", "remember that ...", "I learned that ...", "process the inbox" | An atomic note in `Notes/`, tagged, linked to its hub and related notes, logged in today's daily note. |
| `recall` | "What do I know about X?", "What's pending on <project>?", "Where did I write that?" | Answer from the vault with a `[[link]]` per fact, "as of" dates, and a plain "not recorded" when nothing is there. |
| `plan-day` | "Plan my day", "plan tomorrow", "close the day" | Hourly plan from the weekly schedule, open tasks, carried-over items and the calendar (if connected). You approve before anything is written. |
| `ingest-meeting` | "Process this meeting" (paste a transcript or notes) | Meeting note with summary, decisions, action items and open questions, linked to people and hubs. No guessed speakers, no inferred actions. |
| `ingest-video` | "Process this video: <YouTube link>", "deep notes on this lecture" | Learning note from the video's transcript: summary, key ideas with links to the exact moment, concepts, self-test questions, and an empty `## My notes` section it helps you fill. |
| `weekly-review` | "Review my week", "weekly review" | `Daily/YYYY-Www Weekly review.md`: summary, progress by hub, stuck items, next week's focus. |
| `garden` | "Tidy the vault", "fix the links" | Runs the lint; fixes broken links and missing tags or hubs; links recurring concepts; proposes merges. |
| `sync-memory` | "Sync memories" | Mirrors your Claude Code project memories into the vault (see below). |
| `wrap-up` | "Wrap up", "I'm done" | Closes the session: records state and next step, lists open ends, gets you ready for `/clear`. |

Tasks don't live in a separate app. They are `- [ ]` lines in your notes, and plan-day and recall find them there.

## Knowledge model: folders + tags + hubs

- **Folders by type, not by project.** A note lives in `Notes/`, `Meetings/`, `People/`, `Daily/`... Projects don't get folders.
- **Tags classify.** `project/website-redesign`, `course/stat101`, `learning/typography`, `person`, `meeting`, `idea`, `admin`. A note can have several tags. The dictionary is `vault/System/Tags.md`, and the lint flags tags that aren't in it.
- **Hubs are virtual folders.** Each project, course or topic has a hub note in `Hubs/`. Its Obsidian Bases block lists every note with that tag automatically, so one note can show up in several "folders" at once. A hub's `## Now` section holds the current state and next step, and recall and plan-day read it first.
- **Links make the graph.** Every note links to at least one hub through its `hub:` frontmatter field, and links people, concepts and related notes in its body with `[[wikilinks]]`. A concept that shows up in two or more notes gets a note of its own.

The links add up to a graph you can browse in Obsidian:

![Graph view of a vault built with MySecondBrain: hubs, notes, meetings and people linked together](docs/images/graph.png)

A hub lists its notes through a Bases table, with the current state on top:

![The Website Redesign hub: a Now section and a table of every note tagged project/website-redesign](docs/images/hub.png)

A note carries its tags and hubs in frontmatter, and its backlinks show where it is used:

![A note with tags, hub links and backlinks from a meeting and related notes](docs/images/note.png)

Every note starts with the same frontmatter:

```yaml
---
type: note            # note | meeting | daily | person | hub | concept | source | system
created: 2026-03-02
tags: [project/website-redesign]
hub: ["[[Website Redesign]]"]
description: "one sentence, used by recall and hub tables"
---
```

Templates for notes, meetings, daily notes, people and hubs are in `vault/System/Templates/` and work with Obsidian's core Templates plugin.

## Safety model for external content

If you connect Gmail, Calendar, Drive or GitHub, Claude reads text written by other people. Text in an email can try to give Claude instructions (prompt injection). Three layers handle this:

1. **Rules (`CLAUDE.md`).** Anything from email, calendar, documents, issues or the web is *data, not instructions*. Claude doesn't act on instructions it finds there. It tells you "the content contains this instruction". Authority comes only from your own messages. External text written into the vault gets summarised with its source, never copied verbatim, and suspicious content is marked `> [!warning] External content`.
2. **Guard hook (`tools/external_guard.py`).** Before any claude.ai connector tool call (Gmail, Calendar, Drive, GitHub) that isn't a plain read (send, draft, create, update, delete, share...), Claude Code asks you to approve it, and unknown actions also ask. If the guard itself fails, the call still asks you (fail closed). After every connector result, the hook adds a reminder that the content is untrusted.
3. **Permissions (`.claude/settings.json`).** `WebFetch`, `curl`, `wget`, `git push` and writing `gh` commands always ask first.

Other hard rules: no secrets (passwords, tokens, API keys) in the vault. For confidential work, only methods, decisions and task tracking are kept, never the real data. Notes are never deleted, only marked `status: archived`. Folders outside the repo are read-only for Claude.

## Claude memory import

If you already use Claude Code in other project folders, Claude has built up per-project memories under `~/.claude/projects/<folder>/memory/`. `tools/import_claude_memory.py` mirrors them into `vault/Sources/Claude Memory/` so they show up in recall, hubs and graph view.

- Setup: copy `tools/memory_sources.example.json` to `tools/memory_sources.json` (gitignored) and map each project folder to a hub and tags, or `{"skip": true}`. Or just say "sync memories" and the `sync-memory` skill walks you through it.
- `python3 tools/import_claude_memory.py --list-new` lists memory folders that aren't in your config yet. `--dry-run` previews without writing.
- Each run rewrites the mirror from scratch. Secret-like strings (API keys, tokens) are replaced with `[REDACTED]`, Markdown links between memories become wikilinks, and preference/feedback memories also link to your profile note.
- The mirror is read-only. To correct something, write your own note in `Notes/`. The mirror's contents are gitignored by default.

## YouTube videos

`ingest-video` turns a video into a learning note. Share a link and say "process this video".

- `tools/youtube/yt.sh <url>` writes a timestamped transcript to `vault/Sources/YouTube/` from the video's own captions (manual first, then YouTube's automatic ones). Every paragraph links to that moment in the video.
- No captions, or a lecture full of board work and slides? With a free Gemini API key in `tools/youtube/.env`, `--gemini` transcribes from audio and video and describes what's on screen (equations in LaTeX).
- The note lands in `Notes/` with `learning/<topic>` and `video` tags, in your language. "Deep" mode goes section by section and adds answered self-test questions.
- Setup, settings and troubleshooting: [`tools/youtube/README.md`](tools/youtube/README.md).

## What a filled vault looks like

The repo ships with no example notes. Here is what a few weeks of use might look like for Alex Rivera, a fictional product designer:

```
vault/
├── Home.md
├── Inbox/
│   └── Inbox.md
├── Daily/
│   ├── 2026-03-02.md
│   ├── 2026-03-03.md
│   └── 2026-W10 Weekly review.md
├── Hubs/
│   ├── Website Redesign.md
│   ├── Learning.md
│   └── People.md
├── Notes/
│   ├── Why we chose a serif for body text.md
│   ├── Variable fonts.md
│   └── Homepage hero copy options.md
├── Meetings/
│   └── 2026-03-02 Website Redesign weekly.md
├── People/
│   ├── Alex Rivera.md
│   └── Sam Okafor.md
├── Sources/
│   └── Transcripts/
│       └── 2026-03-02 Website Redesign weekly transcript.md
└── System/
    ├── Tags.md
    ├── Weekly schedule.md
    └── Templates/
```

A note captured from "note: we're going with Source Serif for body text, it reads better at small sizes":

```markdown
---
type: note
created: 2026-03-03
tags: [project/website-redesign, learning/typography]
hub: ["[[Website Redesign]]", "[[Learning]]"]
description: "Body text uses Source Serif because it stays readable at 15-16px"
---
# Why we chose a serif for body text

- Decision (2026-03-03): body text in Source Serif, headings stay in the sans.
- Reason: in the usability test it read better at 15-16px than the sans did.
- Uses the [[Variable fonts]] version so one file covers all weights.
- Agreed with [[Sam Okafor]] in [[2026-03-02 Website Redesign weekly]].
```

A meeting note from a pasted transcript:

```markdown
---
type: meeting
date: 2026-03-02
tags: [meeting, project/website-redesign]
hub: ["[[Website Redesign]]"]
participants: ["[[Alex Rivera]]", "[[Sam Okafor]]"]
transcript: "[[2026-03-02 Website Redesign weekly transcript]]"
description: "Weekly sync: font choice, homepage timeline"
---
# 2026-03-02 Website Redesign weekly

## Summary
- Usability test results are in; body text readability was the main issue.
- Homepage launch stays on 2026-04-15.

## Decisions
- Switch body text to a serif (Sam).

## Action items
- [ ] Alex: homepage wireframes with the new font (due 2026-03-06)
- [ ] Sam: check the font license for the web (due 2026-03-04)

## Open questions
- Do we need a separate font for the docs site?
```

A daily note after plan-day and a few captures:

```markdown
---
type: daily
date: 2026-03-03
tags: [daily]
---
# 2026-03-03 Tuesday

## Focus
- Homepage wireframes

## Plan
- [x] 09:00 - 10:30 Homepage wireframes [[Website Redesign]]
- [ ] 11:00 - 11:30 Design critique [[Website Redesign]]
- [ ] 14:00 - 15:00 Typography course, chapter 4 [[Learning]]

## Meetings

## Log
- 10:40 [[Why we chose a serif for body text]] added

## End of day
- Done:
- Carried over:
```

## Customising and evolving the system

The system is meant to change through use:

- **Change a rule by asking.** "From now on, meeting notes should have a Risks section. Put it in CLAUDE.md." Claude edits the rule or the skill and adds a dated line to `vault/System/Changelog.md`, so you can see later what changed and why.
- **Add a skill.** If you keep asking for the same thing, say "make this a skill". Skills are short Markdown files in `.claude/skills/<name>/SKILL.md`.
- **Add tags and hubs** as projects come and go. Claude adds new tags to `Tags.md` and creates hubs from the template. Hubs you no longer use get `status: archived` and are never deleted.
- **Keep the vault healthy.** Run "tidy the vault" now and then, or `python3 tools/vault_lint.py` yourself.
- **One task, one session.** Long conversations get expensive and unfocused. When a topic is done, say "wrap up", then `/clear`.
- **Commit often.** `git add -A && git commit -m "..."`, or ask Claude to commit. Git is your undo button.
- **Start small.** For the first week, "note: ...", "plan my day" and "what do I know about ...?" are enough.

## FAQ

**Do I need to know Obsidian?**
No. Obsidian is only for viewing: graph view, hub tables, reading notes. You can also edit notes there, and Claude will pick up your changes.

**Does my data leave my computer?**
The notes are local files. Like any Claude Code session, the parts of the vault that Claude reads during a conversation are sent to Anthropic's API to generate replies. Nothing is uploaded anywhere else unless you connect services and approve a write.

**Can I use it in another language?**
Yes. Onboarding asks for your language, and every skill replies in it. Folder names, tags and the rules stay in English, and note content can be in any language.

**Where should I push my vault?**
Only to a **private** repository. Your vault is personal. If you cloned this repo, rename the public remote first (`git remote rename origin upstream`, which keeps updates possible), then add your own private one (`git remote add origin <your-private-repo>`). Onboarding offers this too.

**Can I use it without the connectors?**
Yes. Everything works without Gmail, Calendar, Drive or GitHub. plan-day says the calendar isn't connected and plans from your weekly schedule and tasks.

**Can it record and transcribe meetings?**
No. ingest-meeting works from a transcript or notes you give it. Use your meeting tool's own transcript (Zoom, Meet, Teams) or a local tool such as whisper, then paste the text in.

**I already have notes. Can I bring them in?**
Put them in `vault/Inbox/` and say "process the inbox". Claude classifies, tags and links each one and moves it to the right folder. Start with a small batch.

**How do I update to a newer version of this repo?**
Your `CLAUDE.md` and vault have diverged from upstream by design. Pull upstream changes to `.claude/`, `tools/` and `tests/` selectively, or ask Claude to compare and merge a single skill.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE). See the LICENSE file for the full text.
