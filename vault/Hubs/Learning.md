---
type: hub
hub_tag: learning
tags: [hub, learning]
status: active
up: "[[Home]]"
description: "Topics I study to get better at things"
---
# Learning

Topics I study to get better at things. Each topic gets a `learning/<topic>` tag; when a topic grows, it gets its own hub.

## Now
<!-- Current focus, next step, upcoming dates. recall and plan-day read this. -->
- 

## All notes in this hub
```base
filters:
  and:
    - file.hasTag("learning")
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
