---
type: hub
tags: [hub]
up: "[[Home]]"
description: "Quick captures waiting to be processed"
---
# Inbox

Quick captures land here (Obsidian puts new files in this folder). When you tell Claude "process the inbox", each one gets tagged and moved to `Notes/` or `Meetings/` and linked to its hub.

```base
filters:
  and:
    - file.inFolder("Inbox")
    - file.name != "Inbox"
views:
  - type: table
    name: To process
    order:
      - file.name
      - file.ctime
```
