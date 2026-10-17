---
name: ingest-meeting
description: Turn a meeting transcript or meeting notes (from vault/Sources/Transcripts/ or pasted by the user) into a structured meeting note; extract decisions, action items and people, and link them to project hubs. Use for "process this meeting", "summarise this call", "new transcript", "here are my meeting notes".
---

# Ingest Meeting

Reply in the user's language (see CLAUDE.md About you).

1. **Find.** With no argument, list transcripts in `vault/Sources/Transcripts/` with `status: new`. If the user pasted text into the chat, first save it as `vault/Sources/Transcripts/YYYY-MM-DD <topic> transcript.md` (`type: source`, `tags: [source]`, `status: new`); the ` transcript` suffix keeps its name distinct from the meeting note. If they gave an audio file, say that transcription isn't included here and suggest the meeting tool's own transcript (Zoom, Meet, Teams) or a local tool such as whisper.
2. **Read.** Use speaker labels if present. If it's unclear which speaker is the user, ask.
3. **No inference.**
   - Never guess an ambiguous speaker. Leave "Speaker 1" and ask.
   - Don't tie the meeting to other vault context (projects, earlier meetings, people) unless the transcript itself gives evidence for it. Ask which project it belongs to if it isn't clear.
   - Extract action items only from explicit statements ("I'll send it by Friday"), not from implications.
4. **Context.** Once the project is known, read its hub and recent meeting notes so you can connect "what we said last time".
5. **Write.** `vault/Meetings/YYYY-MM-DD <Project> <topic>.md`, following `vault/System/Templates/Meeting.md`:
   - `## Summary`: 3–6 bullets.
   - `## Decisions`: decisions that were settled, with who said them.
   - `## Action items`: `- [ ] Who: what (due YYYY-MM-DD)`. The user's own first.
   - `## Open questions`.
   - `## Notes`: important technical details, numbers.
   - Frontmatter: `type: meeting`, `date`, `tags: [meeting, <project tag>]`, `hub`, `participants: ["[[Name]]"]`, `transcript: "[[transcript file]]"`, `recording:` (may stay empty), `description`.
   Don't write anything that isn't in the transcript. Mark unclear parts with `(?)`.
6. **Link.**
   - For participants without a note in `vault/People/`, open a short one from `vault/System/Templates/Person.md` (role, projects).
   - If new information, concepts or decisions came up, update the related notes following `capture` rules.
   - If the hub's `## Now` section is now wrong, update it.
   - Add a link under `## Meetings` in the daily note for the meeting date.
7. **Close.** Set the transcript's frontmatter to `status: processed` and `meeting: "[[...]]"`. Show the user the summary and action items. The user's action items stay as `- [ ]` lines in the note; plan-day picks them up from there.
