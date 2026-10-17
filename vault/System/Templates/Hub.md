---
type: hub
hub_tag: project/example
tags: [hub, project/example]
status: active
up: "[[Home]]"
description: "one sentence: what this hub collects"
---
# {{title}}

Short description: what it is, who is involved, what the goal is.

## Now
<!-- Current state, next step, upcoming dates. recall and plan-day read this. -->
- 

## Places
<!-- Optional: where related code, docs or files live outside the vault (read-only for Claude). -->

## All notes in this hub
```base
filters:
  and:
    - file.hasTag("project/example")
    - '!file.inFolder("System")'
views:
  - type: table
    name: Notes
    order:
      - file.name
      - type
      - description
      - file.mtime
```
