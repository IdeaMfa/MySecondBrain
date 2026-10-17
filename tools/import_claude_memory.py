#!/usr/bin/env python3
"""Mirror Claude Code project memories into the vault.

Source of truth stays in ~/.claude/projects/<key>/memory/. Each run rewrites
vault/Sources/Claude Memory/ from scratch, so notes there are read-only
mirrors: never hand-edit them, write your own notes in vault/Notes instead.

Which projects go to which hub is set in tools/memory_sources.json
(copy tools/memory_sources.example.json to start).

Usage: python3 tools/import_claude_memory.py [--dry-run] [--list-new]
           [--config PATH] [--projects-dir PATH] [--vault PATH]
"""
import argparse
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "tools" / "memory_sources.json"
DEFAULT_PROJECTS = Path.home() / ".claude" / "projects"
DEFAULT_VAULT = ROOT / "vault"
MIRROR = ("Sources", "Claude Memory")
BANNER = "> [!info] Mirrored from Claude Code memory. Do not edit here; every sync overwrites this file.\n\n"
MISSING_CONFIG = ("No tools/memory_sources.json. Copy tools/memory_sources.example.json and edit it "
                  '(or ask Claude: "sync memories").')
# Claude Code names project folders after their path with every non-alphanumeric char replaced by "-".
HOME_PREFIX = re.sub(r"[^A-Za-z0-9]", "-", str(Path.home())) + "-"

# Never mirror anything that looks like a credential.
SECRET_PATTERNS = [
    re.compile(p) for p in (
        r"sk-ant-[A-Za-z0-9_-]{10,}", r"sk-[A-Za-z0-9]{20,}", r"hf_[A-Za-z0-9]{20,}",
        r"gh[pousr]_[A-Za-z0-9]{20,}", r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",
        r"AIza[0-9A-Za-z_-]{30,}", r"xox[baprs]-[A-Za-z0-9-]{10,}",
    )
]


def parse_frontmatter(text):
    """Tiny parser for the flat/one-level frontmatter Claude memories use."""
    meta, body = {}, text
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            for line in text[4:end].splitlines():
                m = re.match(r"\s*([A-Za-z_]+):\s*(.*)$", line)
                if m and m.group(2):
                    meta.setdefault(m.group(1), m.group(2).strip().strip('"'))
            body = text[end + 4:].lstrip("\n")
    return meta, body


def yaml_str(s):
    return json.dumps(s, ensure_ascii=False)


def label(key):
    """Readable source label: project key without the home-dir prefix, dashes as spaces."""
    if key.startswith(HOME_PREFIX):
        key = key[len(HOME_PREFIX):]
    return key.strip("-").replace("-", " ")


def home_tilde(path):
    return str(path).replace(str(Path.home()), "~", 1)


def own_key():
    """Claude Code's project folder name for this repo (its own session memory from wrap-up)."""
    return re.sub(r"[^A-Za-z0-9]", "-", str(ROOT))


def list_new(config, projects_dir):
    known = set(config.get("sources", {}))
    if not projects_dir.is_dir():
        print(f"No Claude projects folder at {home_tilde(projects_dir)}.")
        return
    new = sorted(d.name for d in projects_dir.iterdir()
                 if d.is_dir() and d.name not in known and any((d / "memory").glob("*.md")))
    if not new:
        print("No new project memories; every project with memory is in the config.")
        return
    own = own_key()
    print(f"{len(new)} project(s) with memory not in the config:")
    for key in new:
        n = len(list((projects_dir / key / "memory").glob("*.md")))
        mark = "  (this second brain; recommend skip)" if key == own else ""
        print(f"  {key}  ({label(key)}, {n} files){mark}")


def build(config, projects_dir, dest):
    """Return ({path: content}, n_memories, n_indexes, n_redacted)."""
    today = date.today().isoformat()
    notes, indexes = [], []  # (key, cfg, file, meta, body) / (key, cfg, file, body)
    for key, cfg in config.get("sources", {}).items():
        mem = projects_dir / key / "memory"
        if cfg.get("skip") or not mem.is_dir():
            continue
        if not cfg.get("hub"):
            print(f"Skipping {key}: no hub set in the config.", file=sys.stderr)
            continue
        for f in sorted(mem.glob("*.md")):
            meta, body = parse_frontmatter(f.read_text(encoding="utf-8", errors="replace"))
            if f.name == "MEMORY.md":
                indexes.append((key, cfg, f, body))
            else:
                notes.append((key, cfg, f, meta, body))

    # Note title = memory `name` so existing [[name]] links keep resolving.
    # Same name in two sources -> suffix with the source label.
    count = {}
    for key, cfg, f, meta, _ in notes:
        n = meta.get("name") or f.stem
        count[n] = count.get(n, 0) + 1
    titles, file_to_title = {}, {}
    for key, cfg, f, meta, _ in notes:
        n = meta.get("name") or f.stem
        t = n if count[n] == 1 else f"{n} ({label(key)})"
        titles[(key, n)] = t
        file_to_title[(key, f.name)] = t

    def relink(key, text):
        # [text](file.md) -> [[title|text]]
        def md_link(m):
            t = file_to_title.get((key, m.group(2)))
            return f"[[{t}|{m.group(1)}]]" if t else m.group(0)
        text = re.sub(r"\[([^\]]+)\]\(([^)\s]+\.md)\)", md_link, text)

        # [[name]] -> [[title|name]] when renamed
        def wiki(m):
            t = titles.get((key, m.group(1)))
            return f"[[{t}|{m.group(1)}]]" if t and t != m.group(1) else m.group(0)
        return re.sub(r"\[\[([^\]|#]+)\]\]", wiki, text)

    redactions = 0

    def redact(text):
        nonlocal redactions
        for p in SECRET_PATTERNS:
            text, n = p.subn("[REDACTED]", text)
            redactions += n
        return text

    def tag_list(cfg):
        return "tags: [" + ", ".join(list(cfg.get("tags", [])) + ["claude-memory"]) + "]"

    out = {}
    profile_hub = config.get("profile_hub")
    for key, cfg, f, meta, body in notes:
        n = meta.get("name") or f.stem
        mtype = meta.get("type", "")
        hubs = [cfg["hub"]] + ([profile_hub] if mtype in ("user", "feedback") and profile_hub else [])
        fm = [
            "---",
            "type: claude-memory",
            f"memory_type: {mtype}",
            f"description: {yaml_str(redact(meta.get('description', '')))}",
            tag_list(cfg),
            "hub: [" + ", ".join(yaml_str(f"[[{h}]]") for h in hubs) + "]",
            f"source: {yaml_str(home_tilde(f))}",
        ]
        if meta.get("modified"):
            fm.append(f"source_modified: {meta['modified'][:10]}")
        fm += [f"synced: {today}", "---", ""]
        out[dest / cfg["hub"] / f"{titles[(key, n)]}.md"] = "\n".join(fm) + BANNER + redact(relink(key, body))

    for key, cfg, f, body in indexes:
        title = f"Memory index - {label(key)}"
        fm = ["---", "type: claude-memory-index", tag_list(cfg),
              f"hub: [{yaml_str('[[' + cfg['hub'] + ']]')}]", f"source: {yaml_str(home_tilde(f))}",
              f"synced: {today}", "---", ""]
        out[dest / cfg["hub"] / f"{title}.md"] = "\n".join(fm) + BANNER + redact(relink(key, body))
    return out, len(notes), len(indexes), redactions


def clear_mirror(dest):
    """Delete everything inside the mirror folder except .gitkeep (the folder itself stays)."""
    if not dest.is_dir():
        return
    for child in dest.iterdir():
        if child.name == ".gitkeep":
            continue
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Mirror Claude Code project memories into the vault.")
    ap.add_argument("--dry-run", action="store_true", help="print what would be written, write nothing")
    ap.add_argument("--list-new", action="store_true", help="list project folders with memory not in the config")
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    ap.add_argument("--projects-dir", type=Path, default=DEFAULT_PROJECTS)
    ap.add_argument("--vault", type=Path, default=DEFAULT_VAULT)
    args = ap.parse_args(argv)

    if not args.config.is_file():
        print(MISSING_CONFIG)
        return 1
    try:
        config = json.loads(args.config.read_text(encoding="utf-8"))
    except ValueError as e:
        print(f"Cannot read {args.config.name}: {e}")
        return 1

    if args.list_new:
        list_new(config, args.projects_dir)
        return 0

    dest = args.vault.joinpath(*MIRROR)
    out, n_mem, n_idx, redactions = build(config, args.projects_dir, dest)
    if args.dry_run:
        for p in sorted(out):
            print(p.relative_to(args.vault))
    else:
        clear_mirror(dest)
        for p, content in out.items():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
    hubs = sorted({p.parent.name for p in out})
    print(f"{len(out)} notes ({n_mem} memories + {n_idx} indexes) -> {', '.join(hubs) or 'none'}; "
          f"{redactions} secret-like strings redacted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
