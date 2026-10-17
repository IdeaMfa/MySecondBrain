---
type: hub
tags: [hub]
description: "Entry point of the vault; every hub links here"
---
# Home

The entry point of your second brain. In graph view everything connects back here.

## Hubs
<!-- The onboarding skill adds your hubs and profile note here. -->
- [[Learning]]: topics I'm studying
- [[People]]: people I work with

## Flow
- Fixed weekly blocks: [[Weekly schedule]]
- Today: the note for today in `Daily/` (ask Claude "plan my day")
- [[Inbox]]: unprocessed captures
- Meetings: `Meetings/`
- System: [[Tags]], [[Changelog]]

## Recently changed
```base
filters:
  and:
    - '!file.inFolder("Sources")'
    - '!file.inFolder("System")'
views:
  - type: table
    name: Recently changed
    order:
      - file.name
      - type
      - file.mtime
    limit: 20
```
