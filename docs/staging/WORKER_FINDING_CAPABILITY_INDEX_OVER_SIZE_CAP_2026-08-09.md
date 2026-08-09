# WORKER FINDING — `tools/capability_index.py` is 923 lines against a 600 cap, and KNIFE4 grew it

**Found:** 2026-08-09, during `KNIFE4_orphan_disposition` (commits a019ad96d, ae3aebec2)
**Class:** size-ratchet debt, pre-existing and worsened
**Disposition:** QUEUE (SELF_INTERRUPT_DISCIPLINE — the machine is not blocked; the ratchet is at
`rollout_state=warn` and blocked nothing)

## Observed, with evidence

`tools/capability_index.py` was **678 lines at 39142e005**, already over the 600-line new-file cap,
and already logged: `docs/observability/size_ratchet_warnings.jsonl` carries a
`new_file_over_cap` entry for it dated **2026-08-08T19:10:53Z**, before this pass existed. KNIFE4's
disposition machinery took it to **923** (+245).

The function-level warning KNIFE4 itself raised (`disposition_findings: 105 > 60`) was **paid in
the pass**, by splitting the ruling across `disposition_findings` / `_row_findings` /
`_referent_findings` — the H27 shape, rehome rather than trim. The file-level one was not, and
saying so is the point of this note.

## Why it was not fixed on sight

Two reasons, and the second is the real one:

1. It is **pre-existing** — the file was over cap before this pass, so fixing it is not this
   atom's exit condition and would have been a second refactor opened inside a bounded tick.
2. The obvious split is **not obviously right**. The disposition machinery (~250 lines) would move
   cleanly to `tools/orphan_disposition.py`, but the index's own docstring argues at length that
   the index must be the single derived answer to "what is an orphan", and the register check's
   whole integrity rests on reading `status` from the same derivation it guards. A split that puts
   the ruling one import away from the fact it rules on is a candidate for the very
   independence-vs-tautology tradeoff R15 keeps landing on. That needs a design decision, not a
   line-count response — and "split a file to dodge a count" is what the ratchet's own message
   tells you not to do.

## What would close it

Either a designed extraction (the ruling half moves out and the seam between fact and ruling is
stated), or a logged override with a reason
(`python3 tools/size_ratchet_override.py --file tools/capability_index.py ...`). Owed to
`AO6_consolidation_rhythm`, which is the standing duty for exactly this.
