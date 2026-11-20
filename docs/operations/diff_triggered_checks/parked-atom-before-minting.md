---
paths: ["docs/design/maturity_map.yaml"]
symbols: ['^-\s*id:\s*\S']
fired_on: '67a2584214'
claude_md_rows: [29]
claude_md: ["Look for the parked atom"]
---
# A new atom: look for the parked one first

**Check:** the diff mints an atom. Search the map and `maturity_map_closed.yaml` for one that
already holds it, including one parked on a `blocked_on` that has since been abolished
(`tests/tools/test_abolished_block_classes.py`). Revive it instead of minting beside it.

**Lineage:** `67a2584214` (28 Aug): the atom for the director's biggest problem was parked with
nothing blocking it. CLAUDE.md lineage row 29.
