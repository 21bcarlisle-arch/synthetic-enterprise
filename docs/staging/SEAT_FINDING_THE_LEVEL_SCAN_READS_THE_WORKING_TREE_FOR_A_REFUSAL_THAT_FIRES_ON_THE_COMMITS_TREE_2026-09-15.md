# The level scan reads the WORKING TREE to predict a refusal that fires on the COMMIT'S tree, so it prints MOVABLE NOW for a row the gate will refuse

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** SITE4_ia_register_and_nav (the live instance); the defect is in `tools/level_zero_contradicted_by_its_own_controls.py`

**Found:** 2026-09-15, working the delivery-seat item "the two map rows their own controls
contradict". Cost one full land-attempt cycle to discover, which is precisely the cost the
defective field exists to prevent.

**Discharged:** 2026-09-15, landed 5bb74abfd — the probe reads BOTH trees and returns their union, so trees that disagree read FROZEN. Falsifiers: `tests/tools/test_level_zero_contradicted_by_its_own_controls.py::test_a_blocker_archived_only_in_the_WORKING_tree_still_FREEZES_the_row`,
`tests/tools/test_level_zero_contradicted_by_its_own_controls.py::test_the_probe_asks_the_SAME_mechanism_OPS11_refuses_with`,
`tests/tools/test_level_zero_contradicted_by_its_own_controls.py::test_a_tree_git_cannot_read_is_FROZEN_and_never_a_clear_lane`

(The sha is deliberately not in backticks: every backticked string in this claim is read as an
artefact path and checked against the landed set, so a commit id inside one refuses the discharge.)

## What is wrong

`tools/level_zero_contradicted_by_its_own_controls.py` carries a `frozen_by` field, and its own
docstring says why:

> So the verdict carries `frozen_by` — the live blockers on the row's own lane, empty when there
> are none — and the two groups print different instructions, because they ARE different work: a
> movable row is one recording away, a frozen one is a lane to discharge first. […] a reader
> following the printed instruction spends a turn discovering it.

The field is computed from `background.gate_authorization.lane_blockers(lane)` with the DEFAULT
staging root — i.e. `docs/staging/` **in the working tree**. The refusal it exists to predict,
OPS11, fires inside `tools/level_promotion_gate.py` at commit time, and `tools/surgical_land.py`
runs that gate against **the tree the commit would create**. Those are two different trees, and in
a shared worktree with concurrent lanes they routinely disagree.

## The measurement

At `e5b7a438c`, for `SITE4_ia_register_and_nav` (lane `H_harness`):

```
python3 -c "import background.gate_authorization as g; print(g.lane_blockers('H_harness'))"
  -> []
```

and the scan therefore printed:

```
  MOVABLE NOW -- the lane holds no live BLOCKING finding:
  SITE4_ia_register_and_nav (lane H_harness, target L2)
```

The commit gate, on the tree the commit would create, found **nine** live BLOCKING findings in
`H_harness` and refused the level move.

Both readings are correct about the tree each looked at. Another lane has moved those nine
findings from `docs/staging/` into `docs/staging/done/` **in the working tree** and has not
committed the move, so `HEAD` still holds them live. Verified per file rather than inferred — and
`find` alone is not enough here, which is the same trap as
`feedback_a_surviving_copy_verified_with_find_can_be_untracked`:

```
git cat-file -e HEAD:docs/staging/SEAT_FINDING_THE_PAIR_MOVE_PARTNER_WAS_HAND_LAUNCHED_INTO_THE_TICKS_OWN_CGROUP_AND_DIED_WITH_IT_LEAVING_NOTHING_2026-09-08.md   # exit 0 — still live at HEAD
find docs/staging -name '...same name...'
  -> docs/staging/done/...                                                                        # already archived in the working tree
```

## Why it matters, and why it is LATENT rather than BLOCKING

It does not publish a wrong figure and it does not let an unearned level through — OPS11 still
refuses correctly, which is the fail-closed direction. What it does is invert the scan's most
useful output. `frozen_by` was built so a reader could tell "one recording away" from "a lane to
discharge first" WITHOUT attempting the land. On this instance it said the first and the truth was
the second, so the reader pays exactly the turn the field exists to save. The error direction is
the unsafe one for a reader's time: a false MOVABLE sends someone to do work that will be refused,
while a false FROZEN would merely send someone to look at a lane that turns out to be clear.

It is also self-concealing in the shared tree specifically. A daemon or sibling session archiving
staging mid-turn is ordinary here, so the disagreement appears and disappears without anything
changing in either the map or the scan.

## The repair

Compute `frozen_by` against the tree the refusal will actually be evaluated on, not the working
tree. `lane_blockers` already takes `staging_root=` and `repo_root=`, so the shape exists; what is
missing is that the scan passes neither. The honest reading for a level move is `HEAD`'s staging,
because that is what `level_promotion_gate` will see.

Fail-closed direction to keep, and it is the opposite of the current one: if the two trees
DISAGREE, the row is frozen, not movable. An uncommitted archival is a discharge that has not
happened yet.

Do **not** repair this by widening OPS11 or by reaching for `record_limitation_accepted` on the
nine. That route was already refused for this same row at a count of seventeen, in its own
`level_hold_note` on 2026-09-06: *"accepting 17 limitations to push one row through is marking
your own homework at scale."* The count changed; the argument did not.

## What is next

`SITE4_ia_register_and_nav` is left at `level_current: 0` with the real reason written into its
`level_hold_note` (landed `0e13c14a5`), including a one-command test a later reader can run to see
whether the hold has lifted. Its L2 evidence is in hand and re-run — 104 passed across
`site/test_ia_register.py`, `site/test_every_served_page_takes_the_canonical_nav.py` and
`site/test_live_pixel_verify.py` — and a `LEVEL_UP_SELF_CERTIFIED` at 2 carrying that evidence is
already in `docs/observability/gate_authorizations.jsonl`. The row needs no further work on SITE4
itself: it moves when that staging archival reaches `HEAD`.
