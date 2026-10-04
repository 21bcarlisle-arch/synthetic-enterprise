# The shared tree's catch-up parked two unlanded lane edits in a preserved ref

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `land-the-lane-edits-parked-by-the-shared-tree-catch-up` (Lane 0 delivery)

**2026-10-04 07:20.** The shared working tree had sat 0 ahead and 171 behind origin since the fork
closed. A fast-forward was refused because 45 dirty or untracked paths collided with incoming
commits. The seat brought it level with origin (`ba50ef5e6`) and destroyed nothing. Every colliding
working copy was first committed to
**`refs/preserved/shared-tree-catchup/2026-10-04-0719`** (`f2fd36d34`, parent `7234966b2`, the
stale HEAD).

What happened to each kind of path:

- **Twins of origin (7) and earlier origin revisions (8):** cleared. Origin already holds them.
- **`background/delivery_lane.py`:** three-wayed onto origin cleanly and left in the working copy,
  so it is still unlanded there.
- **Copies that conflict with origin:** these exist only in the ref. Each of their lines was
  checked against origin:
  - `knowledge_map.md`, `run_phase2b.py`, and the ledger finding in staging: nothing missing.
  - `test_static_quality_ratchet.py` and the `gate_authorizations.jsonl` duplicate PB8 L1 row:
    superseded on origin.
  - `DIRECTION.yaml`, `decisions.jsonl`, `SEAT_STRETCH_LOG.md`: the stale seat's 02:22 and 05:20
    orientations. They are being landed on origin separately ("The delivery seat's two unlanded
    orientations reach origin").

## Owed — two pieces of real work that exist nowhere else

1. **`background/delivery_seat.py` and `tests/background/test_the_direction_record_lands_on_origin.py`**
   (mtime 03:37). This is a follow-up to `3911189ac` and was never landed. It does three things:
   - adds a **grow-only guard**: `GROW_ONLY`, `_keeps_every_line`, `_refuse_a_grow_only_rewrite`,
     an in-order line walk that replaces the "origin is a prefix" check;
   - factors out `_land_in`;
   - **merges origin in and retries only when origin moved under the gate**.
   
   It conflicts with `4aadc11bc` (the startup-anchor page regenerated in the same landing). A hand
   merge must keep both: regenerate the page inside each attempt. It was not merged in a hurry,
   because the 09:20 seat run lands its record through this function and origin's version works.
   Recover it with `git show refs/preserved/shared-tree-catchup/2026-10-04-0719:<path>`, using
   `3911189ac` as the merge base.
2. **`docs/market_research/ASSUMPTIONS.md`.** The *founding-account start-month distribution* row
   is not on origin: "20 of 80 founding accounts start 1 Jan; none start Sep/Nov/Dec", against real
   GB switching being lowest in January. Land the row with its date line. Origin's
   `knowledge_map.md` already carries the matching entry.

The untracked copies that differ from origin are in the same ref. All of them are staging notes or
research docs whose newer versions are already on origin.
