---
paths: ["**/*.py", "**/*.sh", "**/*.service", "**/*.timer"]
symbols: ['\bpgrep\b', '(until|while)\b.*\bsleep\b', '\btime\.sleep\(\s*\d{2,}']
fired_on: '71cdda78a5'
claude_md_rows: [62]
claude_md: []
---
# A waiter

**Check:** it names its subject and carries a deadline; use `tools/wait_for.py`, never a
hand-rolled `pgrep`.

**Lineage:** R18, director 27 Aug, `docs/design/WAITERS_NAME_THEIR_SUBJECT.md` (`71cdda78a5`):
`until ! pgrep -f` matched its own command line, 12 hours burned. Row 62 is one line of the
enforcement table and stays; this item counts no characters.
