# HARDEN DRAW — KNIFE2 seam DESIGN review, before any KNIFE3 draw

**Status:** FILED as a HARDEN draw. Director-endorsed 2026-08-09 ("Endorsed: your HARDEN
draw on the seam DESIGN before any KNIFE3 draw — file it as such").
**Atom:** `KNIFE2_customer_straddle` — already `loop_stage: harden`, `level_current: 2`.
**No mint required.** This is a HARDEN draw on an existing atom, not a new atom. The
maturity map is deliberately NOT edited by this filing.

## THE DRAW

Review the **design** of `company/interfaces/supply_book.py`. Explicitly **not** its edge
counts — those have been measured three times by three parties and are not in doubt.

## WHY THIS EXISTS

`KNIFE2` was built by a lane that exited without committing or self-recording. Its residue
was adopted twice:

| when | by | what was verified |
|---|---|---|
| ~15:0x | PW2 worker tick | edge counts re-measured; level recorded |
| 16:06:53 | (same) | L0→L2 written to `gate_authorizations.jsonl` |
| 19:xx | worker seat (this landing) | edge counts re-measured; code committed |

All three verified **arithmetic**. None reviewed the seam's shape. The sentence

> "the owning lane should confirm the seam DESIGN; the MEASUREMENT is verified"

appears verbatim in **both** the `supply_book.py` module docstring and the ledger
provenance — written twice by two adopters, answered by neither. There is no lane left to
answer it, which is why it needs an explicit draw.

## WHY IT GATES KNIFE3

`KNIFE3_wall_crossing_paydown` carries `depends_on: [AO5, KNIFE1, KNIFE2]`, and AO5's ledger
entry states the mechanism: *"KNIFE3 stays blocked until both KNIFE1 and KNIFE2 are L2."*
KNIFE2 is now L2, so KNIFE3 is drawable — on a foundation whose only verification is that
sixteen edges became zero. KNIFE3 is the pass that cuts the *remaining* crossings through
this same seam; if the seam's shape is wrong, KNIFE3 propagates it at scale rather than
exposing it.

## SCOPE — the questions to answer

1. **Is `registered_supply_points()` the right shape?** It returns the LIVE list object,
   never a copy, and the docstring argues that identity is part of the contract (a runtime
   accumulator is appended to by `simulation.run_phase2b`; test teardown clears it in
   place). That reasoning is coherent — but it was never reviewed by anyone other than its
   author. A seam that hands out mutable internal state is worth one deliberate look.
2. **Does the seam face the right direction?** The docstring's own defence is that MPAN
   registration is a company act *published to the industry*, so the world reading the
   registered book mirrors reality. Confirm that argument holds, or amend it.
3. **Formally hand over the narrowing debt.** The seam returns full customer dicts —
   contract type and internal segment label included — where a real MPAN registration
   publishes identity, supply start, address, profile class, metering arrangement and EAC.
   Its builder deferred this to KNIFE3 / the Epoch-3 adapter programme and then vanished.
   The handover has never been made to a live owner.
4. **The dwelling-truth inversion** (`home_type`, `bedrooms`, `epc_rating` are world facts
   stored company-side) is recorded as owed-forward, not fixed. Confirm it stays owed, or
   raise it.

## EXIT

Each of the four questions carries a written verdict — confirmed-as-built, or amended with
the reason. Item 3 names a live owner. No edge is re-measured as evidence for this draw;
if the review changes the seam, the measurement is redone as a consequence, not as proof.

## EXPLICIT NON-GOALS

Do not re-derive the crossing counts. Do not reopen KNIFE1. Do not take KNIFE3's cuts
opportunistically — one hotspot per pass is a director wall.
