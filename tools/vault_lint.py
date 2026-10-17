#!/usr/bin/env python3
"""Vault health check: broken wikilinks, notes without tags/hub, unknown tags, orphans.

Usage: python3 tools/vault_lint.py [--quiet] [--strict] [--vault PATH]
  --quiet   print only the summary line
  --strict  exit 1 if any issue is found (default: always exit 0)
  --vault   check another vault folder (default: <repo>/vault)
"""
import argparse
import re
import sys
from pathlib import Path

DEFAULT_VAULT = Path(__file__).resolve().parents[1] / "vault"
NEEDS_META = ("Notes", "Meetings", "People")  # folders whose notes must carry tags + hub
SKIP_DIRS = {".obsidian", ".trash", "Attachments"}
NO_ORPHAN_CHECK = ("System", "Daily")

LINK = re.compile(r"\[\[([^\]|#^]+)(?:[#^][^\]|]*)?(?:\|[^\]]*)?\]\]")
CODE = re.compile(r"```.*?```|`[^`\n]*`", re.S)
COMMENT = re.compile(r"<!--.*?-->", re.S)


def frontmatter(text):
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            return text[4:end]
    return ""


def lint(vault):
    """Return (notes, broken, missing, unknown_tags, orphans) for the vault folder."""
    notes = sorted(p for p in vault.rglob("*.md") if not SKIP_DIRS & set(p.relative_to(vault).parts))
    names = {p.stem.lower(): p for p in notes}
    names.update({str(p.relative_to(vault).with_suffix("")).lower(): p for p in notes})
    # Attachments (images, PDFs, Word files) are linked with their extension, e.g. [[x.pdf]].
    att_dir = vault / "Attachments"
    attachments = {a.name.lower() for a in att_dir.rglob("*") if a.is_file()} if att_dir.is_dir() else set()
    tags_file = vault / "System" / "Tags.md"
    known_tags = None  # None = no dictionary, skip the unknown-tag check
    if tags_file.is_file():
        known_tags = set(re.findall(r"`([a-z0-9/-]+)`", tags_file.read_text(encoding="utf-8")))

    broken, missing, unknown_tags = [], [], []
    inbound = {p: 0 for p in notes}
    outbound = {p: 0 for p in notes}
    for p in notes:
        text = p.read_text(encoding="utf-8", errors="replace")
        fm = frontmatter(text)
        for target in LINK.findall(COMMENT.sub("", CODE.sub("", text))):
            key = target.strip().lower()
            if key in attachments:
                continue
            t = names.get(key)
            if t is None:
                broken.append((p, target))
            elif t != p:
                outbound[p] += 1
                inbound[t] += 1
        if p.relative_to(vault).parts[0] in NEEDS_META:
            if not re.search(r"^tags:\s*\[.+\]", fm, re.M):
                missing.append((p, "tags"))
            if not re.search(r"^hub:\s*\[.+\]", fm, re.M):
                missing.append((p, "hub"))
        m = re.search(r"^tags:\s*\[(.*)\]", fm, re.M)
        if m and known_tags is not None:
            for tag in (t.strip().strip("\"'") for t in m.group(1).split(",")):
                if tag and not any(tag == k or tag.startswith(k + "/") for k in known_tags):
                    unknown_tags.append((p, tag))
    orphans = [p for p in notes if inbound[p] == 0 and outbound[p] == 0
               and p.relative_to(vault).parts[0] not in NO_ORPHAN_CHECK]
    return notes, broken, missing, unknown_tags, orphans


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check the vault for broken links, missing metadata and orphans.")
    ap.add_argument("--quiet", action="store_true", help="print only the summary line")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any issue is found")
    ap.add_argument("--vault", type=Path, default=DEFAULT_VAULT, help="vault folder to check")
    args = ap.parse_args(argv)
    vault = args.vault.resolve()
    if not vault.is_dir():
        print(f"No vault folder at {vault}")
        return 1 if args.strict else 0

    notes, broken, missing, unknown_tags, orphans = lint(vault)

    def show(title, rows, fmt):
        if rows and not args.quiet:
            print(f"\n## {title} ({len(rows)})")
            for r in rows[:50]:
                print("  " + fmt(r))
            if len(rows) > 50:
                print(f"  ... +{len(rows) - 50}")

    rel = lambda p: str(p.relative_to(vault))
    show("Broken links", broken, lambda r: f"{rel(r[0])} -> [[{r[1]}]]")
    show("Missing frontmatter", missing, lambda r: f"{rel(r[0])}: no {r[1]}")
    show("Tags not in dictionary", unknown_tags, lambda r: f"{rel(r[0])}: {r[1]}")
    show("Orphan notes (no links)", orphans, rel)
    print(f"{len(notes)} notes | {len(broken)} broken links | {len(missing)} missing fields | "
          f"{len(unknown_tags)} unknown tags | {len(orphans)} orphans")
    issues = len(broken) + len(missing) + len(unknown_tags) + len(orphans)
    return 1 if args.strict and issues else 0


if __name__ == "__main__":
    sys.exit(main())
