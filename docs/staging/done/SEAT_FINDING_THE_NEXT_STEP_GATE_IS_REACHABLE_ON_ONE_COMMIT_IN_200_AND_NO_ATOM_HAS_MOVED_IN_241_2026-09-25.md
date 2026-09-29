**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# `next_step_gate` is reachable on 1 commit in 200, and the reason is that the trunk has not advanced an atom in 241 consecutive commits

Found while censusing the blast radius of wiring the `commit-msg` chain into
`tools/surgical_land.py` (`docs/staging/records/
PREREG_HOW_MANY_LIVE_LANDINGS_THE_TWO_COMMIT_MSG_GATES_WOULD_REFUSE_2026-09-25.md`). The wiring
landed; this is the thing the number turned up on the way, and it is not fixed here.

## The measurement

Over the last 200 first-parent commits of `HEAD` (`ba9bc6733`), with the open-atom set read from
the maturity-map blob **at each commit**:

* **110 atoms were open**, 100 of them carrying a distinct number form (`A45`, `W2_34`, …).
* **1 commit in 200 names any of them.** Confirmed twice: once through `next_step_gate.
  atoms_named_in`, and once through an independent grep for the 100 number forms, which is the
  control that matters — a near-zero count out of a matcher is exactly what a broken matcher also
  returns. (Its positive arms pass: the full-id form, the number form and the negative arm all
  answer correctly on a constructed message.)
* **`next_step_gate` therefore refuses 1 of 200**, and `write_time_gate` refuses 1 of 200.
* **0 of the 200 commits stage `docs/design/maturity_map.yaml` at all.** The map's last commit is
  `86504d951` (2026-09-22) and there are **241 first-parent commits since it**.

## Why this is a finding and not just a small number

`next_step_gate` exists because a next step named in prose is one nothing can draw, and its own
docstring records the director's reason: *"the queue offers machinery because machinery is what's in
it."* The gate asks its question only of a commit whose **message names an open atom**. So:

1. **A green `next_step_gate` currently means almost nothing.** It is not wrong — it refuses
   correctly on the one commit that reaches it — it is unasked. Wiring the chain into the landing
   door (today) makes the gate *able* to fire on 78% of trunk traffic that it previously could not
   reach at all; it does not make that traffic trigger it. Those are two different repairs and only
   the first is done.
2. **Nothing else asks.** `level_promotion_gate` records a level move and does not ask for a
   successor; no other module in `tools/` or `background/` reads a `NEXT:` trailer as a
   requirement. So a commit that moves `level_current` while its message says
   *"the housing joint, stage 2"* — naming no id — is asked for nothing by anything.
3. **241 commits without a map change is the shape the gate was built to surface, measured at the
   trunk rather than in the queue.** That is a reading for the director about what the commits are
   being spent on, not a control defect, and it is the half of this finding that is not H_harness's
   to settle.

## Two smaller observations, recorded so they are not re-derived

* `next_step_gate.escape_rate(200)` reports **4 declared, 2 escaped (50%)**, which does not
  reconcile with the 1-in-200 above because it is **not the same 200**: it uses plain `git log -200`
  (which walks every parent, date-ordered) where the census walks `--first-parent`. Both populations
  are defensible; the printed sentence *"over the last 200 commits"* does not say which it means.
* The escape reasons it records are both about landing mechanics, not about work — consistent with
  everything above.

## Falsifiers

* Re-run the census on a window in which the map moves: if a commit advances a level and carries no
  trailer and nothing refuses it, claim 2 holds. If something refuses it, claim 2 is wrong and the
  successor requirement lives somewhere this survey missed.
* `git log --first-parent --format=%h -- docs/design/maturity_map.yaml | head -1` — if it is no
  longer `86504d951`, the 241 is stale and the allocation reading has changed.
