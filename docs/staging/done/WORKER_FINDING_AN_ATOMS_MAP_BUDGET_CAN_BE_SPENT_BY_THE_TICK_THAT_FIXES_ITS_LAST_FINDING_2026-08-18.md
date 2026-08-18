# WORKER FINDING — an atom's map budget can be spent by the very tick that answers its last finding

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-18, SITE2_two_sided_wall_exhibit worker tick (commit `fe6dd5aae`).
**Rank:** backlog. Not blocking today; blocks the *next* narrative touch on this atom.
**Class:** harness / map bookkeeping. Queued per SELF-INTERRUPT DISCIPLINE, not fixed on sight.

## What happened, observed-with-evidence

The tick that fixed `coldwalk:site2_c1_pinned_exhibit_reads_as_the_open_households` was
**refused by the pre-commit gate** on `tests/design/test_simplifications_store.py::test_map_within_per_atom_budget`:

```
SITE2_two_sided_wall_exhibit: 13651 B, above the 12288 B per-atom cap
```

Measured, both sides, from one ref:

| tree | SITE2 bytes | headroom |
|---|---|---|
| HEAD before the tick | 12,194 | 94 B |
| first draft (fix reasoning written as map comments) | 13,651 | **−1,363 B** |
| landed | 12,221 | **67 B** |

The repair for the draft was correct and cheap — the reasoning belongs in the ledger row's
`fix_evidence`, which already carried it, and which the map's own `fixed_2026_08_18:` header
already points at ("Full evidence: the ledger row's own fix_evidence"). So nothing was lost.

## The finding, which is not "I wrote too much"

**Closing a finding is itself an append to this atom's map.** Every answered finding moves
from `findings:` to a dated `fixed_<date>:` list — the key stays, it just changes list — and
each new dated list costs its own header line. The atom had 94 B of headroom before this tick
and has 67 B after, having added *two* bare keys and one `file_scope` entry and having spent
its entire comment allowance getting back under.

So the budget is now structurally exhausted in a way that is invisible until a commit is
refused: the next tick that touches SITE2's map narrative *at all* goes red, and it will go
red on a control whose message names accretion, at a moment when the author is thinking about
something else entirely. That is the failure mode worth registering — not the byte count.

## The designed repair already exists and has a consumer waiting for it

`tools/generate_proof_data.py::_expert_hour_findings` was built precisely for this and says so:

> "`expert_hour.findings` is the append-per-Hour narrative list that crossed the per-atom map
> budget and wedged publishing; it now moves to the sibling record store one atom at a time,
> **as the cap names each one**. So the migration is PARTIAL by design and this reader must
> see both shapes."

The cap has now named SITE2. The reader already handles both shapes, inline-wins, and SITE2's
store currently holds `evidence` only (`expert_hour_findings` is `None` — checked, so there is
no stale copy waiting to resurrect). SITE2 already carries `records_rehomed: [evidence]` and
`notes_rehomed: [name]`, so the rehome machinery is live on this atom.

## What to do — recommendation, not a question

Rehome `SITE2_two_sided_wall_exhibit`'s `expert_hour.findings` / `fixed_*` lists into
`docs/design/simplifications/SITE2_two_sided_wall_exhibit.yaml` under `expert_hour_findings`.

Three things a doer must check, each of which has bitten before:

1. **Inline wins.** `_expert_hour_findings` prefers the inline list, so the map keys must be
   *removed*, not duplicated — a store copy under a surviving inline list is dead weight that
   makes the two-sources contract unfalsifiable (the reader's own docstring says this).
2. **`tests/controls/test_map_reconciliation.py` reads the map.** Confirm it follows the
   rehome (read the store, or read both) *before* the keys leave the map, or the ledger-vs-map
   reconciliation silently stops covering this atom — a control that passes because its
   subject vanished is the FAIL-SILENT pattern.
3. **A store append forces a shared-map edit in the same commit** (the `records_rehomed` /
   `notes_rehomed` facet has to name the new tenant), and a store append can ROLL into a
   second file. Both files land together or the atom's evidence points at nothing.

## Null control for whoever builds it

After the rehome, SITE2's map bytes must *drop* and the Proof door's verification stack must
still render the same finding history it renders today. If the door's finding list changes,
the rehome moved the record rather than its home — which is the thing `_expert_hour_findings`
exists to prevent.

## Not claimed

This is a bookkeeping-capacity finding. It says nothing about the atom's eight exit criteria,
its level (still 2), or the 2026-08-17 Expert Hour's verdict (still NO — a verdict is a
property of a walk, not of a to-do list going empty).
