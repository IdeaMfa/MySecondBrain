#!/usr/bin/env bash
# SessionStart hook: gives Claude a one-glance status of the brain at the start of every session.
# Always exits 0 so it can never block a session.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
V="$ROOT/vault"
today=$(date +%F)
echo "MySecondBrain | today: $today ($(LC_ALL=C date +%A))"
if grep -q '{{NAME}}' "$ROOT/CLAUDE.md" 2>/dev/null; then
  echo 'Setup not finished: the "About you" section in CLAUDE.md is empty. Offer onboarding (onboarding skill).'
fi
if [ -f "$V/Daily/$today.md" ]; then
  open=$(grep -c '^\s*- \[ \]' "$V/Daily/$today.md" 2>/dev/null)
  echo "Daily note exists: Daily/$today.md (${open:-0} open plan items)"
else
  echo "No daily note for today (plan-day can create it)."
fi
inbox=$(find "$V/Inbox" -name '*.md' ! -name 'Inbox.md' 2>/dev/null | wc -l)
[ "$inbox" -gt 0 ] && echo "$inbox unprocessed notes in Inbox."
new=$(grep -l '^status: new' "$V/Sources/Transcripts/"*.md 2>/dev/null | wc -l)
[ "$new" -gt 0 ] && echo "$new unprocessed meeting transcripts (ingest-meeting)."
vids=$(grep -l '^status: new' "$V/Sources/YouTube/"*.md 2>/dev/null | wc -l)
[ "$vids" -gt 0 ] && echo "$vids unprocessed video transcripts (ingest-video)."
python3 "$ROOT/tools/vault_lint.py" --quiet 2>/dev/null | sed 's/^/Vault: /'
exit 0
