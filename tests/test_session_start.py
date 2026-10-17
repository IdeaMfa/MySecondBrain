import shutil
import subprocess
import tempfile
import unittest
from datetime import date
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"


class SessionStartTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        shutil.copytree(TOOLS, self.root / "tools", ignore=shutil.ignore_patterns("__pycache__"))
        v = self.root / "vault"
        for d in ("Inbox", "Daily", "Notes", "System", "Sources/Transcripts", "Sources/YouTube"):
            (v / d).mkdir(parents=True)
        (v / "Inbox" / "Inbox.md").write_text("# Inbox\n")
        (self.root / "CLAUDE.md").write_text("## About you\n- Name: {{NAME}}\n")
        self.vault = v

    def tearDown(self):
        self.tmp.cleanup()

    def run_hook(self):
        p = subprocess.run(["bash", str(self.root / "tools" / "session_start.sh")],
                           capture_output=True, text=True, timeout=30)
        return p.returncode, p.stdout

    def test_fresh_install(self):
        code, out = self.run_hook()
        self.assertEqual(code, 0)
        today = date.today().isoformat()
        self.assertIn(f"MySecondBrain | today: {today} (", out)
        self.assertIn('Setup not finished: the "About you" section in CLAUDE.md is empty.', out)
        self.assertIn("No daily note for today (plan-day can create it).", out)
        self.assertNotIn("Inbox.", out)
        self.assertIn("Vault: ", out)
        self.assertIn(" notes | ", out)

    def test_filled_vault(self):
        (self.root / "CLAUDE.md").write_text("## About you\n- Name: Alex Rivera\n")
        today = date.today().isoformat()
        (self.vault / "Daily" / f"{today}.md").write_text("## Plan\n- [ ] 09:00 - 10:30 A\n- [x] B\n  - [ ] C\n")
        (self.vault / "Inbox" / "idea.md").write_text("x")
        (self.vault / "Sources" / "Transcripts" / "t.md").write_text("---\nstatus: new\n---\n")
        (self.vault / "Sources" / "Transcripts" / "u.md").write_text("---\nstatus: processed\n---\n")
        (self.vault / "Sources" / "YouTube" / "v.md").write_text("---\nstatus: new\n---\n")
        code, out = self.run_hook()
        self.assertEqual(code, 0)
        self.assertNotIn("Setup not finished", out)
        self.assertIn(f"Daily note exists: Daily/{today}.md (2 open plan items)", out)
        self.assertIn("1 unprocessed notes in Inbox.", out)
        self.assertIn("1 unprocessed meeting transcripts (ingest-meeting).", out)
        self.assertIn("1 unprocessed video transcripts (ingest-video).", out)

    def test_never_fails_without_vault(self):
        shutil.rmtree(self.vault)
        (self.root / "CLAUDE.md").unlink()
        code, out = self.run_hook()
        self.assertEqual(code, 0)
        self.assertIn("MySecondBrain | today:", out)


if __name__ == "__main__":
    unittest.main()
