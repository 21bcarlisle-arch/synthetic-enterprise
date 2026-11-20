---
paths: ["docs/design/maturity_map.yaml"]
fired_on: '8ab0ce8be9'
claude_md_rows: [73]
claude_md: ["Writing a map row"]
---
# A map row costs bytes against a ratchet

**Check:** before writing a level, a park or a `blocked_on`, run `python3 -m tools.maturity_map_store`
and read the headroom. Over the line, `tests/design/` reds every lane. The remedy is always downward:
drain a comment, or rehome a growing field to `docs/design/simplifications/<atom_id>.yaml`. Never
raise the ceiling.

**Lineage:** `8ab0ce8be9` (17 Sept): 693 bytes of headroom, below a median commit, because six
paragraphs had been pasted thirty times. CLAUDE.md lineage row 73.
