**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3

# FINDING — 21 gated commits never reached `origin`, `origin` moved 25 past them, and a drawn item's stated premise is invisible to every worktree that can be promoted

**Filed 2026-09-11 by the delivery seat, from the isolated executor worktree, on finding that the
commit a drawn item names as its precondition does not exist on the base the turn can land on.**

---

## The measurement

In `/var/tmp/se-seat-executor` (cut from `origin/main`), 2026-09-11:

```
git rev-parse HEAD origin/main main
  HEAD        cf16f724e6d79f02707008c0af143d2e00c1c90b
  origin/main cf16f724e6d79f02707008c0af143d2e00c1c90b     ← identical
  main        6f5f1d3f48c73bf8009e47c5bb12c3c68f156291     ← the shared tree

git rev-list --count main..HEAD   →  25
git rev-list --count HEAD..main   →  21
git merge --ff-only main          →  fatal: Not possible to fast-forward, aborting.
```

`git worktree list` puts `main` in `/home/rich/synthetic-enterprise` at `6f5f1d3f4`.

**The two histories have diverged.** The shared tree's `main` holds 21 commits that were never
pushed; `origin/main` holds 25 commits that `main` has never fast-forwarded onto. The oldest of the
21 is `dcdfd5ebd`; the newest is `6f5f1d3f4`.

## Why this is BLOCKING rather than housekeeping

**It is not the "tree is behind origin" shape and it is not the "origin moved" shape. It is both at
once, and only one side has a route.** `tools/promote_worktree_landing` pushes to `origin/main` and
refuses anything that is not a fast-forward — which is correct and is the property that makes it
safe to run unattended. It has no failure mode here: an executor worktree cut from `origin/main`
lands, promotes, and `origin` advances, which is exactly what the 25 are. **Nothing in the
architecture pushes the shared tree's `main`.** So the 21 accumulate, and every one of them is
invisible to every worktree the sanctioned route can serve.

**And the invisibility is already costing work.** The delivery lane drew
*"the settlement sample is a count-based cull and the chooser earns 1.64x at its size"* with a WHY
that rests on `0d86d6dfe` — *"`SyntheticCustomer.premise` now carries a Household with
`floor_area_band`, loft, cavity and PV, so `choose_for_difference` has something real to choose over
— it did not before `0d86d6dfe`"*. `0d86d6dfe` is one of the 21.
`git grep floor_area_band origin/main -- simulation/` returns nothing. A seat that took that
sentence at its word would have built against four fields that do not exist on its base, and a seat
that took the tree at *its* word would have concluded the premise was retracted and dropped a live
item. Both readings are wrong and the tree supports both.

**It also means a landed, gated, measured piece of work — a fidelity repair that moved the mean
remaining insulation ceiling from 41.5 to 61.4 W/K, the mission's own quantity, understated by a
third — has been on one machine's disk since 2026-09-10 and in no published artefact.**

## What it is NOT

It is not `--no-verify` and it is not an ungated commit. All 21 carry `surgical_land` receipts; the
gate ran on every one. Nothing here was bypassed. The defect is that **landing and promoting are
two steps, the second is only ever run by the isolated-worktree route, and work landed directly on
the shared tree therefore has no route to `origin` at all.** The one-step-of-two shape, not a wall
crossing.

## The repair, and it is not one this turn should take

The merge is 21 × 25 across `simulation/`, `docs/` and `background/`, and my memory of this
project's own record names the exact hazard: *a merge that adopts one side's rewrite silently
deletes the other side's purely additive work.* This is the shape that produces that. It needs a
gated reconciliation, not a `git merge` from an executor turn that was drawn for something else,
and doing it here would be the largest possible instance of the careless-pathspec class.

**Recommended, and what I am doing about it in this turn:** file this, build the drawn item so that
it is **correct on both bases** — keyed to what a `Household` actually carries rather than to
whether `0d86d6dfe` landed — and hand the reconciliation on as its own item. The alternative,
building against fields that exist on one machine, would produce a landing that cannot be promoted
and a turn that lands nothing.

**The mechanism worth having afterwards**, and it is one leg, not a register: a control that fails
when `main` and `origin/main` have diverged by more than a fast-forward in either direction. Today
nothing anywhere can notice — the promotion route sees only its own base, the shared tree sees only
its own branch, and the divergence is visible from exactly one place, which is a worktree that
happens to resolve both refs and happens to look.

## Related

* `docs/staging/records/SEAT_PREREGISTRATION_WHAT_CHOOSING_THE_SETTLED_SAMPLE_FOR_DIFFERENCE_MOVES_2026-09-11.md`
  §0 — the same measurement, recorded there because it changes what that build can claim.
* `tools/promote_worktree_landing.py` — the route that works, and the reason only one direction has
  one.
