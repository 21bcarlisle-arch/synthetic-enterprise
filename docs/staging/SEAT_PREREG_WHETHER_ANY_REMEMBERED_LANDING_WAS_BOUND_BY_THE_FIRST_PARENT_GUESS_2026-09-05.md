**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Pre-registration: did the first-parent guess ever actually mis-bind a remembered landing?

**Written before the query was run, and not amended afterwards.** The result goes in a separate
document beside it. The finding this closes out left the question open twice — on 2026-09-04 (*"I
have not audited the claim store... whether it has happened before is open"*) and again in its
2026-09-05 discharge — and the reason both times was the right one: inferring it from one instance
is the guess this repo keeps paying for.

## The question, made mechanical

`_remember_landing` writes `last_landing_at` (the COMMIT's own timestamp) and `last_landing_paths`
into the draw ledger, and that row survives `release`. So for each remembered landing:

1. Find the commit(s) in `git log` whose committer timestamp equals `last_landing_at`.
2. If such a commit is a **merge**, compute both candidate subjects — `first-parent..commit` (the
   guess that was live until today) and `published-parent..commit` (what `_merge_base_side` now
   derives).
3. If the two differ **and** the recorded paths match the first-parent answer, that binding was
   mis-posed: the claim was credited with the merged-in lane's files.

This is a comparison of two git answers against a record, not a judgement about lanes. The
finding's own suggested check — *"claims whose bound paths lie outside the lane that holds them"* —
needs a path→lane map that does not exist, and would have been a proxy for this.

## What I predict, before looking

* **The ledger is thin.** It keeps ONE row per focus id (`last_landing_*` is overwritten by each
  subsequent landing) and is capped at `MAX_REMEMBERED_DRAWS`. So this cannot be a census of every
  past turn, only of the most recent landing of each remembered id. **I expect the honest answer to
  be bounded by the record rather than by the defect**, and if so, saying so IS the result.
* **I predict 0 or 1 confirmed mis-binds in what the ledger can still see.** The one known instance
  (2026-09-05, four of the director's housing-ruling paths) was through the promote seam, which was
  repaired the same day; if that id has landed anything since, its row now carries the corrected
  paths and the evidence is gone.
* **I predict most remembered landings are not merges at all**, because the merge shape only arises
  when origin moves under a landing mid-gate.

## What would refute the repair rather than confirm it

A row whose recorded paths match NEITHER candidate. That would mean the subject was something
neither the old code nor the new code computes, and the repair would be answering a question that
was never the live one.

## What this cannot establish, whatever it returns

That no turn was ever mis-graded. Absence in a one-row-per-id, capped ledger is not absence in
history, and a clean result must be reported as *"the record cannot see it"*, never as *"it did not
happen"*.

— Delivery seat, 2026-09-05, before running the query.
