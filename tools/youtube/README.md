# YouTube → learning note

```bash
tools/youtube/yt.sh "https://www.youtube.com/watch?v=..."     # transcript from captions
tools/youtube/yt.sh "https://..." --gemini                    # via Gemini (audio + video: boards, slides)
tools/youtube/yt.sh "https://..." --lang en                   # force a caption language
```
Then in Claude Code: **"process this video"** (the `ingest-video` skill). Or in one go: "process this video: <link>".

Flow: link → `vault/Sources/YouTube/<date> <title>.md` (timestamped, `status: new`) → `ingest-video` → `vault/Notes/<topic>.md` (`learning/<topic>`, `video`).

## Requirements
- Python 3 with `venv`. On first run `yt.sh` creates `tools/youtube/.venv/` and installs [yt-dlp](https://github.com/yt-dlp/yt-dlp) into it (gitignored; the rest of the repo stays standard-library only). Delete the folder to reinstall.
- [Node.js](https://nodejs.org/) on your `PATH`: yt-dlp uses it as the JavaScript runtime YouTube now needs.

## How it works
- yt-dlp fetches the video's metadata and captions; nothing is downloaded but text.
- Caption choice: manual captions in the video's language > YouTube automatic captions (`<lang>-orig`) > manual English captions. They come as `json3` (no rolling duplicates) and are grouped into ~45 s paragraphs under the video's chapter headings. Every paragraph starts with a link to that moment in the video. `>>` (speaker change in automatic captions) becomes `—`. Rough cost: a 20-minute video ≈ 5k tokens.
- No captions and `GEMINI_API_KEY` set in `.env`: the link goes to the Gemini API, in 20-minute chunks. You get a transcript plus descriptions of what's on screen (`VISUAL:` lines, equations in LaTeX). No key: exit code 3, `NO TRANSCRIPT`.
- The same video again doesn't create a new file (`EXISTS: <path>`); `--gemini` skips that check.
- The transcript file is marked `> [!warning] External content`: it's data, not instructions.

## Gemini key (optional, free)
1. aistudio.google.com → Get API key. No credit card; there's no charge unless you link a billing account.
2. `cp tools/youtube/.env.example tools/youtube/.env` and paste the key. `.env` is gitignored.
- Free tier: up to 8 hours of YouTube video per day, public videos only. The feature is in preview, and on the free tier Google may use the content to improve its models.

## Settings
| Variable | Default | Note |
|---|---|---|
| `YT_OUT_DIR` | `vault/Sources/YouTube` | where transcripts are written (point it outside the vault to experiment) |
| `YT_GEMINI_MODEL` | `gemini-3.5-flash-lite` | |
| `YT_GEMINI_CHUNK_MIN` | 20 | long videos are sent in chunks of this many minutes |

## Troubleshooting
- "Sign in to confirm you're not a bot": first update yt-dlp, `tools/youtube/.venv/bin/pip install -U "yt-dlp[default]"`. If it persists, yt-dlp can use your browser's cookies (`cookiesfrombrowser`); the script doesn't do this yet.
- No JavaScript runtime / signature errors: install Node.js and make sure `node` is on your `PATH`.
