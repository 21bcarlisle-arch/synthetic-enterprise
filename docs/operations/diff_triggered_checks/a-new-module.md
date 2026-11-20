---
paths: ["**/*.py"]
added_only: true
fired_on: '3236963419'
claude_md_rows: [30, 76]
claude_md: ["Finish the file before you commit", "A new module needs a REUSE block"]
---
# The diff adds a module

**Check:**
1. `python3 -m tools.write_time_gate --explain <module>` and a REUSE block in the commit message
   naming what the index returned and why new code anyway;
2. wire it and file its findings before committing: the gates read the whole tree, so an unwired
   module or an unfiled finding blocks every lane's commit, not only yours.

**Lineage:** the REUSE gate's words enter with the rewrite, `3d83edffb6` (28 Aug); the
whole-tree incident is GAP: origin unknown. Fired on `3236963419` (adds `tools/isolate_hunks.py`).
CLAUDE.md lineage rows 30, 76.
