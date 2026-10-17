---
type: hub
hub_tag: person
tags: [hub, person]
status: active
up: "[[Home]]"
description: "Everyone with a person note: colleagues, classmates, clients, friends"
---
# People

Everyone who has a note in `People/`. Person notes link here through `hub: ["[[People]]"]`, and meeting notes link to people through `participants:`.

## All people
```base
filters:
  and:
    - file.hasTag("person")
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
