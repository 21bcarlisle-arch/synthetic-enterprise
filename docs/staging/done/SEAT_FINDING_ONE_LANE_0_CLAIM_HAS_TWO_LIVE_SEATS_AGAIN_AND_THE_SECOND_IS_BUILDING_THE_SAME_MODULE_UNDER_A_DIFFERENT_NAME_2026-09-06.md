**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
claim `W2_18-coordinate-at-the-draw` · **Class:** uncommitted_and_orphaned_work

# FINDING: one Lane 0 claim has two live seats again, and the second is building the same module under a different name

**Observed 2026-09-06 BST from the shared tree, while landing `ec8a18710`.** This is a recurrence,
not a new class: `SEAT_FINDING_ONE_LANE_0_CLAIM_LAUNCHED_TWO_SEATS_THREE_SECONDS_APART_AND_BOTH_
BUILT_THE_SAME_NEW_MODULE_2026-09-06.md` is the same defect earlier today. It is filed again
because the two builds are **live right now** and the collision is still ahead of us rather than
behind.

## What is running

| pid | started | what |
|---|---|---|
| 266365 → 267510 | 35 min ago | `background.worker_tick` → this seat, on the shared tree |
| 268813 → 268895 | 35 min ago | `background.seat_executor --once` → a second seat, in `/var/tmp/se-seat-executor` (locked worktree) |

Both were handed the **same** work text, verbatim, for the same claim id
`W2_18-coordinate-at-the-draw` — the Lane 0 coordinate item. Fourteen seconds apart.

## The collision, specifically

This seat landed `ec8a18710`:

* `tools/household_siting_frame.py` — the census → region → 1 km cell frame builder
* `simulation/household_siting.py` — the per-customer draw
* `simulation/population_draw.py` — `lat`/`lon` on `SyntheticCustomer`, rendered by
  `to_customer_dict`
* `sim/household_siting/region_household_frame.csv` — the committed 144,542-cell artefact
* `tools/weather_cell_weights.py` — `census_weights(group_of=...)`

The other seat is, as this is written, running
`timeout 2400 python3 -u -m tools.region_household_sites --pull` — **a module of the same purpose
under a different name**, twenty minutes into its own pull of the same lookup.

So the two builds will not conflict textually on the tool (different filenames — they will simply
both exist, and one will have no caller). They **will** conflict on
`simulation/population_draw.py`, which both must edit to carry the coordinate, and the second seat
lands from an isolated worktree via `promote_worktree_landing`.

## Why the existing controls did not stop it

The claim store shows one claim, held once. Both seats were launched by **different launchers** —
`worker_tick` and `seat_executor --once` — and the claim is taken by the seat, not by the launcher,
so whichever check exists is asked after both are already running. This is the same shape as the
earlier finding and the earlier finding's fix (if any landed) does not cover this launcher pair.

## What to do with the second build when it arrives

Not "revert it". Two independent implementations of one sourcing question are worth **reading
against each other before either is deleted** — they will have made different choices about the
output-area-to-region join, about Wales (whose region column is NULL in the ONS lookup, and which
this seat's first complete pull dropped in silence), and about whether the artefact is committed or
derived. The cheap merge is to keep whichever frame is better sourced and delete the other module
entirely rather than leave a second one with no caller, which is this project's
`no_caller_and_never_runs` class arriving by the back door.

The expensive mistake is a merge that adopts one side whole and deletes the other's additive work,
which is already a filed class here
(`WORKER_FINDING_TWO_MERGES_EACH_ADOPTED_ONE_SIDE_WHOLE_AND_DELETED_THE_OTHERS_PURELY_ADDITIVE_WORK`).

## The real fix, which is not this document

A claim must be taken **before** a seat is launched, by the launcher, in a store both launchers
read. Two launchers asking the same pool and each starting a seat that then claims is a race with
no loser — both win, and the cost is paid at the merge.
