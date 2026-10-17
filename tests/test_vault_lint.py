import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

LINT = Path(__file__).resolve().parents[1] / "tools" / "vault_lint.py"

TAGS = "| Tag | Hub | Meaning |\n|---|---|---|\n| `project` | | Projects |\n| `person` | [[People]] | People |\n| `hub` | | Hubs |\n"


def note(tags="[project/demo]", hub='["[[Demo]]"]', body=""):
    fm = ["---", "type: note"]
    if tags is not None:
        fm.append(f"tags: {tags}")
    if hub is not None:
        fm.append(f"hub: {hub}")
    return "\n".join(fm + ["---", "", body, ""])


class LintTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.vault = Path(self.tmp.name) / "vault"
        for d in ("Notes", "Hubs", "System", "Daily", "Attachments", "People"):
            (self.vault / d).mkdir(parents=True)
        (self.vault / "System" / "Tags.md").write_text(TAGS)
        self.write("Hubs/Demo.md", "---\ntype: hub\ntags: [hub, project/demo]\n---\n# Demo\n")
        self.write("Hubs/People.md", "---\ntype: hub\ntags: [hub, person]\n---\n# People\n")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, text):
        p = self.vault / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def lint(self, *args):
        p = subprocess.run([sys.executable, str(LINT), "--vault", str(self.vault), *args],
                           capture_output=True, text=True, timeout=30)
        return p.returncode, p.stdout

    def summary(self, out):
        return out.strip().splitlines()[-1]

    def test_clean_vault(self):
        self.write("Notes/A.md", note(body="See [[B]] and [[Demo]]."))
        self.write("Notes/B.md", note(body="Back to [[A]]."))
        code, out = self.lint("--strict")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.summary(out),
                         "5 notes | 0 broken links | 0 missing fields | 0 unknown tags | 0 orphans")

    def test_broken_link(self):
        self.write("Notes/A.md", note(body="[[Demo]] [[Nowhere]] [[Nope|alias]] [[Demo#Section]]"))
        _, out = self.lint()
        self.assertIn("## Broken links (2)", out)
        self.assertIn("Notes/A.md -> [[Nowhere]]", out)
        self.assertIn("Notes/A.md -> [[Nope]]", out)
        self.assertIn("| 2 broken links |", out)

    def test_missing_tags_and_hub(self):
        self.write("Notes/A.md", note(tags=None, hub=None, body="[[Demo]]"))
        self.write("People/Sam.md", note(tags="[]", hub=None, body="[[Demo]]"))
        _, out = self.lint()
        self.assertIn("## Missing frontmatter (4)", out)
        self.assertIn("Notes/A.md: no tags", out)
        self.assertIn("Notes/A.md: no hub", out)
        self.assertIn("People/Sam.md: no tags", out)

    def test_meta_not_required_outside_needs_meta(self):
        self.write("Daily/2026-01-05.md", "# Monday\n[[Demo]]\n")
        _, out = self.lint()
        self.assertIn("0 missing fields", out)

    def test_unknown_tag(self):
        self.write("Notes/A.md", note(tags='[project/demo, "secret-stuff", personnn]', body="[[Demo]]"))
        _, out = self.lint()
        self.assertIn("## Tags not in dictionary (2)", out)
        self.assertIn("Notes/A.md: secret-stuff", out)
        self.assertIn("Notes/A.md: personnn", out)

    def test_subtag_of_known_root_is_valid(self):
        self.write("Notes/A.md", note(tags="[project/demo/deep, person]", body="[[Demo]]"))
        _, out = self.lint()
        self.assertIn("0 unknown tags", out)

    def test_orphan(self):
        self.write("Inbox/Lonely.md", "no links here\n")
        self.write("Daily/2026-01-05.md", "no links, but daily notes are never orphans\n")
        _, out = self.lint()
        self.assertIn("## Orphan notes (no links) (2)", out)  # Lonely + Demo hub
        self.assertIn("  Inbox/Lonely.md", out)
        self.assertIn("  Hubs/Demo.md", out)

    def test_hub_field_counts_as_link(self):
        self.write("Notes/A.md", note(body="no body links"))
        _, out = self.lint()
        self.assertIn("0 orphans", out)
        self.assertNotIn("Daily/2026-01-05.md", out)
        self.assertNotIn("System/Tags.md", out)

    def test_attachment_link_not_broken(self):
        (self.vault / "Attachments" / "slides.pdf").write_bytes(b"%PDF")
        self.write("Notes/A.md", note(body="[[Demo]] ![[slides.pdf]] [[Slides.PDF]]"))
        _, out = self.lint()
        self.assertIn("0 broken links", out)

    def test_links_in_code_and_comments_ignored(self):
        body = "[[Demo]]\n```\n[[InFence]]\n```\nInline `[[InCode]]`.\n<!-- [[InComment]] -->\n"
        self.write("Notes/A.md", note(body=body))
        _, out = self.lint()
        self.assertIn("0 broken links", out)

    def test_path_style_link_resolves(self):
        self.write("Notes/A.md", note(body="[[Hubs/Demo]]"))
        _, out = self.lint()
        self.assertIn("0 broken links", out)

    def test_skipped_dirs(self):
        self.write(".obsidian/x.md", "[[Nowhere]]")
        self.write(".trash/y.md", "[[Nowhere]]")
        self.write("Notes/A.md", note(body="[[Demo]]"))
        _, out = self.lint()
        self.assertIn("0 broken links", out)

    def test_missing_tags_file_does_not_crash(self):
        (self.vault / "System" / "Tags.md").unlink()
        self.write("Notes/A.md", note(tags="[anything/goes]", body="[[Demo]]"))
        code, out = self.lint()
        self.assertEqual(code, 0)
        self.assertIn("0 unknown tags", out)

    def test_quiet_prints_summary_only(self):
        self.write("Notes/A.md", note(body="[[Nowhere]]"))
        _, out = self.lint("--quiet")
        self.assertEqual(len(out.strip().splitlines()), 1)
        self.assertTrue(out.startswith("4 notes | 1 broken links"))

    def test_strict_exit_code(self):
        self.write("Notes/A.md", note(body="[[Nowhere]]"))
        self.assertEqual(self.lint()[0], 0)
        self.assertEqual(self.lint("--strict")[0], 1)

    def test_missing_vault_folder(self):
        p = subprocess.run([sys.executable, str(LINT), "--vault", str(Path(self.tmp.name) / "none")],
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(p.returncode, 0)
        self.assertIn("No vault folder", p.stdout)


if __name__ == "__main__":
    unittest.main()
