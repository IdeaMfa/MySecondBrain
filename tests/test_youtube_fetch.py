import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

FETCH = Path(__file__).resolve().parents[1] / "tools" / "youtube" / "fetch.py"
spec = importlib.util.spec_from_file_location("yt_fetch", FETCH)
fetch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetch)  # yt_dlp is imported only inside main(), so this needs no dependencies


def info(**kw):
    base = {"id": "abc123", "title": "How filters work", "channel": "Demo Channel", "duration": 600,
            "upload_date": "20260301", "language": "en", "subtitles": {}, "automatic_captions": {}}
    base.update(kw)
    return base


class TimestampTest(unittest.TestCase):
    def test_ts_and_link(self):
        self.assertEqual(fetch.ts(75), "1:15")
        self.assertEqual(fetch.ts(3725), "1:02:05")
        self.assertEqual(fetch.link("abc", 75.9), "[1:15](https://youtu.be/abc?t=75)")

    def test_linkify_only_line_start(self):
        out = fetch.linkify_timestamps("[01:05] hello\n[1:00:00] VISUAL: $x$\nsee [02:00]", "v")
        self.assertIn("[1:05](https://youtu.be/v?t=65) hello", out)
        self.assertIn("[1:00:00](https://youtu.be/v?t=3600) VISUAL", out)
        self.assertTrue(out.endswith("see [02:00]"))

    def test_safe_name(self):
        self.assertEqual(fetch.safe_name('A/B: "C" [d] #e?'), "A B C d e")
        self.assertLessEqual(len(fetch.safe_name("x" * 200)), 90)


class TrackTest(unittest.TestCase):
    def test_manual_beats_auto(self):
        i = info(subtitles={"en-US": ["m"]}, automatic_captions={"en-orig": ["a"]})
        self.assertEqual(fetch.pick_track(i, None), ("en-US", "manual", ["m"]))

    def test_auto_orig_in_video_language(self):
        i = info(language="de", automatic_captions={"de-orig": ["o"], "de": ["t"], "en": ["x"]})
        self.assertEqual(fetch.pick_track(i, None)[:2], ("de-orig", "auto"))

    def test_forced_language(self):
        i = info(subtitles={"en": ["e"], "fr": ["f"]})
        self.assertEqual(fetch.pick_track(i, "fr")[0], "fr")

    def test_english_manual_fallback_and_none(self):
        i = info(language=None, subtitles={"en": ["e"], "live_chat": ["c"]})
        self.assertEqual(fetch.pick_track(i, None)[0], "en")
        self.assertIsNone(fetch.pick_track(info(language=None, subtitles={"live_chat": ["c"]}), None))


class ParseTest(unittest.TestCase):
    def test_json3_and_speaker_change(self):
        raw = json.dumps({"events": [
            {"tStartMs": 0, "segs": [{"utf8": ">> Hello"}, {"utf8": "  there"}]},
            {"tStartMs": 1000},
            {"tStartMs": 2000, "segs": [{"utf8": "yes >> no"}]},
        ]})
        self.assertEqual(fetch.parse_json3(raw), [(0, "— Hello there"), (2, "yes — no")])

    def test_paragraphs_and_chapters(self):
        cues = [(0, "One."), (10, "Two."), (50, "Three."), (60, "Four"), (130, "Five.")]
        chapters = [{"start_time": 0, "title": "Intro"}, {"start_time": 120, "title": "Part two"}]
        out = fetch.paragraphs(cues, chapters, "v").splitlines()
        out = [l for l in out if l]
        self.assertEqual(out[0], "### Intro ([0:00](https://youtu.be/v?t=0))")
        self.assertEqual(out[1], "[0:00](https://youtu.be/v?t=0) One. Two.")
        self.assertEqual(out[2], "[0:50](https://youtu.be/v?t=50) Three. Four")
        self.assertEqual(out[3], "### Part two ([2:00](https://youtu.be/v?t=120))")
        self.assertEqual(out[4], "[2:10](https://youtu.be/v?t=130) Five.")


class OutputTest(unittest.TestCase):
    def test_render_frontmatter(self):
        text = fetch.render(info(title='Say "hi"'), "en", "auto", "body", "2026-03-02")
        self.assertTrue(text.startswith("---\ntype: source\nsource_kind: youtube\nstatus: new\n"))
        self.assertIn('title: "Say \\"hi\\""\n', text)
        self.assertIn("video_id: abc123\n", text)
        self.assertIn("upload_date: 2026-03-01\n", text)
        self.assertIn("tags: [source, video]\n", text)
        self.assertIn("> [!warning] External content", text)
        self.assertTrue(text.endswith("body\n"))

    def test_existing_finds_by_video_id(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            self.assertIsNone(fetch.existing("abc123", d))
            (d / "x.md").write_text(fetch.render(info(), "en", "manual", "b", "2026-03-02"))
            self.assertEqual(fetch.existing("abc123", d), d / "x.md")
            self.assertIsNone(fetch.existing("abc12", d))


if __name__ == "__main__":
    unittest.main()
