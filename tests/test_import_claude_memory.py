import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

IMPORTER = Path(__file__).resolve().parents[1] / "tools" / "import_claude_memory.py"
FAKE_KEY = "sk-ant-" + "A1b2C3d4E5f6G7h8I9j0"


def memory(name, mtype, body, description="d"):
    return f"---\nname: {name}\ndescription: {description}\ntype: {mtype}\n---\n\n{body}\n"


class ImportTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        self.projects = t / "projects"
        self.vault = t / "vault"
        self.mirror = self.vault / "Sources" / "Claude Memory"
        self.mirror.mkdir(parents=True)
        (self.mirror / ".gitkeep").write_text("")
        self.config = t / "memory_sources.json"
        self.config.write_text(json.dumps({
            "_comment": "test",
            "profile_hub": "Alex Rivera",
            "sources": {
                "-work-site": {"hub": "Website Redesign", "tags": ["project/website-redesign"]},
                "-work-type": {"hub": "Learning", "tags": ["learning/typography"]},
                "-work-skip": {"skip": True},
            },
        }))
        self.mem("-work-site", "MEMORY.md", "- [Setup](setup.md) - how the site builds\n")
        self.mem("-work-site", "setup.md", memory("Site setup", "project",
                 f"Uses a static generator. Token was {FAKE_KEY} once. See [[Shared name]]."))
        self.mem("-work-site", "prefs.md", memory("Alex prefs", "feedback", "Short answers."))
        self.mem("-work-site", "shared.md", memory("Shared name", "project", "site side"))
        self.mem("-work-type", "shared.md", memory("Shared name", "reference", "type side"))
        self.mem("-work-skip", "x.md", memory("Skipped", "project", "never mirrored"))
        self.mem("-work-unlisted", "y.md", memory("Unlisted", "project", "new project"))

    def tearDown(self):
        self.tmp.cleanup()

    def mem(self, key, fname, text):
        d = self.projects / key / "memory"
        d.mkdir(parents=True, exist_ok=True)
        (d / fname).write_text(text, encoding="utf-8")

    def run_importer(self, *args, config=None):
        cmd = [sys.executable, str(IMPORTER), "--config", str(config or self.config),
               "--projects-dir", str(self.projects), "--vault", str(self.vault), *args]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return p.returncode, p.stdout + p.stderr

    def files(self):
        return sorted(str(p.relative_to(self.mirror)) for p in self.mirror.rglob("*") if p.is_file())

    def read(self, rel):
        return (self.mirror / rel).read_text(encoding="utf-8")

    def test_writes_notes_with_frontmatter_and_banner(self):
        code, out = self.run_importer()
        self.assertEqual(code, 0, out)
        text = self.read("Website Redesign/Site setup.md")
        self.assertTrue(text.startswith("---\ntype: claude-memory\nmemory_type: project\n"))
        self.assertIn("tags: [project/website-redesign, claude-memory]", text)
        self.assertIn('hub: ["[[Website Redesign]]"]', text)
        self.assertIn("source: ", text)
        self.assertRegex(text, r"synced: \d{4}-\d{2}-\d{2}")
        self.assertIn("> [!info] Mirrored from Claude Code memory. Do not edit here; "
                      "every sync overwrites this file.", text)
        self.assertIn("1 secret-like strings redacted.", out)
        self.assertIn("5 notes (4 memories + 1 indexes) -> Learning, Website Redesign;", out)

    def test_index_note(self):
        self.run_importer()
        text = self.read("Website Redesign/Memory index - work site.md")
        self.assertIn("type: claude-memory-index", text)
        self.assertIn("[[Site setup|Setup]]", text)  # md link relinked to wikilink

    def test_secret_redacted(self):
        self.run_importer()
        text = self.read("Website Redesign/Site setup.md")
        self.assertNotIn(FAKE_KEY, text)
        self.assertIn("[REDACTED]", text)

    def test_duplicate_names_suffixed_and_relinked(self):
        self.run_importer()
        files = self.files()
        self.assertIn("Website Redesign/Shared name (work site).md", files)
        self.assertIn("Learning/Shared name (work type).md", files)
        self.assertIn("[[Shared name (work site)|Shared name]]", self.read("Website Redesign/Site setup.md"))

    def test_profile_hub_for_feedback_and_user(self):
        self.run_importer()
        self.assertIn('hub: ["[[Website Redesign]]", "[[Alex Rivera]]"]', self.read("Website Redesign/Alex prefs.md"))
        self.assertNotIn("Alex Rivera", self.read("Website Redesign/Site setup.md").split("---")[1])

    def test_skip_and_unlisted_not_mirrored(self):
        self.run_importer()
        joined = " ".join(self.files())
        self.assertNotIn("Skipped", joined)
        self.assertNotIn("Unlisted", joined)

    def test_dry_run_writes_nothing(self):
        code, out = self.run_importer("--dry-run")
        self.assertEqual(code, 0)
        self.assertIn("Site setup.md", out)
        self.assertEqual(self.files(), [".gitkeep"])

    def test_rewrite_removes_stale_but_keeps_gitkeep(self):
        stale = self.mirror / "Old Hub" / "Stale.md"
        stale.parent.mkdir()
        stale.write_text("old")
        (self.mirror / "loose.md").write_text("old")
        self.run_importer()
        self.assertFalse(stale.exists())
        self.assertFalse((self.mirror / "loose.md").exists())
        self.assertTrue((self.mirror / ".gitkeep").exists())
        # A second run is idempotent.
        before = self.files()
        self.run_importer()
        self.assertEqual(self.files(), before)

    def test_list_new(self):
        code, out = self.run_importer("--list-new")
        self.assertEqual(code, 0)
        self.assertIn("-work-unlisted", out)
        self.assertNotIn("-work-site", out)
        self.assertNotIn("-work-skip", out)
        self.assertEqual(self.files(), [".gitkeep"])

    def test_list_new_marks_own_repo(self):
        import re
        own = re.sub(r"[^A-Za-z0-9]", "-", str(IMPORTER.resolve().parents[1]))
        self.mem(own, "status.md", memory("Session state", "project", "wrap-up notes"))
        code, out = self.run_importer("--list-new")
        self.assertEqual(code, 0)
        line = next(l for l in out.splitlines() if own in l)
        self.assertIn("(this second brain; recommend skip)", line)
        other = next(l for l in out.splitlines() if "-work-unlisted" in l)
        self.assertNotIn("recommend skip", other)

    def test_missing_config(self):
        code, out = self.run_importer(config=Path(self.tmp.name) / "nope.json")
        self.assertEqual(code, 1)
        self.assertIn("No tools/memory_sources.json. Copy tools/memory_sources.example.json", out)
        self.assertEqual(self.files(), [".gitkeep"])

    def test_example_config_is_valid(self):
        example = IMPORTER.parent / "memory_sources.example.json"
        data = json.loads(example.read_text())
        self.assertIn("sources", data)
        for cfg in data["sources"].values():
            self.assertTrue(cfg.get("skip") or (cfg.get("hub") and cfg.get("tags")))


if __name__ == "__main__":
    unittest.main()
