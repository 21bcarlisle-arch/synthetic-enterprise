**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The next-step gate now asks the MAP DIFF as well as the prose — and the map has not moved in 245 commits, so the second trigger is built and still dormant

Successor to `SEAT_FINDING_THE_NEXT_STEP_GATE_IS_REACHABLE_ON_ONE_COMMIT_IN_200_AND_NO_ATOM_HAS_
MOVED_IN_241_2026-09-25.md`, which is the measurement this acts on. That finding's claim 2 —
*"nothing else asks"* — is now false for one route and still true for the rest, and the difference
is the whole of what landed here.

## What changed

`tools/next_step_gate.py` had ONE trigger: a commit whose MESSAGE names an open atom owes a `NEXT:`
trailer. It now has two. The second is the record rather than the account: **a commit whose staged
diff moves an atom's `level_current` owes a trailer whatever its prose says.** The message leg is
kept — it is the cheaper half and it catches the commit that advances an atom without touching the
map, which on this trunk is nearly all of them.

The trigger is keyed to the **VALUE**, not to the line. Measured over the last 120 first-parent
commits touching the map: 32 add and remove a line containing `level_current`, and only **31** move
a value. `2cc924ed9` rewrote the trailing comment on a level that stayed at 2 — a bookkeeping edit
a line-keyed trigger would have demanded a successor for. The same census says **89 of those 120
touch the map and move no level at all**, so a trigger keyed merely to *the map being staged* would
ask ~4× as often and be wrong most times it asked.

It is keyed to **changed**, not to increased. `level_promotion_gate.level_increases` returns
increases only, correctly, because its question is whether a promotion was authorised. This
question is different: an atom dropped from 2 to 0 is a claim withdrawn and *what follows* is
exactly what a reader needs. **No commit in the last 120 moves a level down**, so history cannot
exercise that branch and `test_a_level_WITHDRAWN_is_a_move_too` is its only witness.

## What is NOT fixed, and this is the half that matters

**The map's last commit is `86504d951` (2026-09-22) and there are now 245 first-parent commits
since it.** The new trigger therefore fires on **zero** of today's trunk traffic. It is reachable —
proved against the real index, through the real script entry point, in
`test_the_MAP_LEG_FIRES_WHEN_RUN_THE_WAY_THE_HOOK_RUNS_IT` — and it is unasked, for a different
reason than before. The previous reason was that the gate looked in the wrong place. This one is
that **the thing it now looks at has not changed in eight days of commits**, which is a reading
about what the work is being spent on and is not H_harness's to settle.

Stated plainly so it is not mistaken for a repair: *wiring* made the gate able to fire on 78% of
trunk traffic; *this* made it fire on the right evidence; **neither makes an atom move.**

## Evidence

* Re-measured at `d4244a93f`, 2026-09-25: 110 atoms open, 100 distinct number forms, **1** of the
  last 200 first-parent commits names any of them. Unchanged from the predecessor finding.
* Seven mutations run against the new leg; six red on the control written for them, none on a
  different leg. The seventh — replacing `_map_is_staged` with `return True` — came back **GREEN**,
  and it is a missing control rather than an equivalence: the suite's own clock went 1.18s → 2.29s,
  which is the two YAML parses it adds to every commit of every lane. Closed by keying the control
  to the predicate itself. The green result is recorded here because a mutation census that reports
  only its refutations is the flattering reading.
* Prediction and refutation: `docs/staging/records/PREREG_HOW_OFTEN_A_MAP_COMMIT_ACTUALLY_MOVES_A_
  LEVEL_VALUE_2026-09-25.md`. I predicted 20–26 value moves out of the 32 line hits and at least one
  downward move; the answers were 31 and 0. Both wrong, kept beside the prediction.

## Falsifiers

* Stage a `level_current` change and commit without a trailer. If it lands, this leg is not wired —
  `tools/git-hooks/commit-msg` runs the gate and `tools/surgical_land.py` runs that chain since
  `68717e7e1`, so both doors should refuse.
* `git log --first-parent -1 --format=%h -- docs/design/maturity_map.yaml` — if it is no longer
  `86504d951`, the 245 is stale and the dormancy claim above must be re-measured before it is
  repeated.
* Change `old != new` to `new > old` in `atoms_whose_level_moved`. If the suite stays green, the
  withdrawn-level branch is unreachable and the control that claims to witness it does not.
