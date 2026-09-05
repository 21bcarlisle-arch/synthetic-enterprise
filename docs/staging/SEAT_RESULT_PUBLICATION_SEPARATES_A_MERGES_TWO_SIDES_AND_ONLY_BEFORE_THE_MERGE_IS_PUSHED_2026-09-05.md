**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Which parent of a merge is the base: measured, and neither filed option survived whole

**Subject:** the standalone `python3 -m background.delivery_lane --landed <id>` on a merge HEAD.
**Repairs:** `SEAT_FINDING_LANDED_ON_A_MERGE_BINDS_THE_OTHER_LANES_PATHS_AND_REPORTS_SUCCESS_2026-09-04.md`.

---

## The prior, and where it was registered

The 2026-09-04 finding filed two candidate designs and recommended one, before any of this was
measured. That document is the pre-registration and it is on the record:

1. **Refuse** when HEAD is a merge and no `--commit` was given, naming both parents. *"Option 1 is
   smaller and is the recommendation."*
2. **Default `since` to `origin/main`**, making the standalone ask the same question
   `tools/promote_worktree_landing` asks with the pre-push origin.

The draw that produced this turn added the tiebreaker to test: *"origin/main is readable from any
tree and would make the two routes agree, which is worth something — but measure before choosing."*

**I did not file a second pre-registration of my own before running the measurement below.** The
finding's two options are the registered prior; what follows either confirms or refutes them, and
the refutation is recorded beside the claim rather than folded into the design.

## What was measured

Real merges in this repository's own history, both of the sanctioned
`surgical_land --merge origin/main` shape. No fixtures.

| | `42d253da5` *"merge origin/main: re-gate the shared low-water reader contracts"* | `179a6e042` *"merge origin/main: settle the advisor doc's add/add"* |
|---|---|---|
| first-parent diff (the code's answer) | `DIRECTOR_RULING_AMENDMENT_MERIT_ORDER…` — **1 file, the merged-IN lane's** | `DIRECTOR_RULING…` + the low-water docs — **the merged-IN lane's** |
| second-parent diff | the 3 low-water reader paths — **the landing's own** | `deadmans_switch.py`, `DIRECTION.yaml`, … — **the landing's own** |
| both parents ancestors of *today's* `origin/main`? | **yes, both** | **yes, both** |
| today's `origin/main...<merge>` | **empty** | **empty** |

## What it refutes

**Option 2, as stated, is wrong** — and it fails silently in the direction that matters. A blanket
`since = origin/main` is correct only while the merge is unpushed. Once it is pushed,
`origin/main...HEAD` is empty and `--landed` refuses; the post-promote re-run that the turn
instructions describe as *"harmless: it adds the same paths git already gave"* would become a
refusal with a plausible-sounding cause. A default that is right for a few minutes and wrong
afterwards is the shape of the defect it was replacing.

**Option 1 is right about the hard case and unnecessarily pessimistic about the common one.** The
sides are separable without asking the caller, because *the base a landing was merged onto is
already published and the landing is not — or it would not have needed merging.* That is git's own
answer, not the caller's, so the 2026-08-21 shared-tree hole stays shut. It comes from the merge's
**own parents**, not from a remote-tracking ref that keeps moving, and it lands on precisely the
subject `promote_worktree_landing` passes as `since`. **The two routes now agree.**

**The discriminator has a reachable dead zone, and it is not hypothetical** — the table's third row
is it. Once the merge itself is pushed, both parents are published and publication separates
nothing; with no readable `origin/main`, neither is. There option 1 is exactly right: refuse, name
both sides by sha and subject, and name both ways out.

## What was built

`background/delivery_lane.py`

* `_merge_base_side(parents)` — the published parent is the base, or `None` plus the reason it
  cannot be told. `_commit_facts` uses it wherever it used to take `parents[0]` on faith.
* `refusal_reason` grew the third cause. A merge that plainly touched files used to be reported as
  `UNREADABLE or touched no files`, which is the cause-naming failure that function exists to end.
* `--landed` grew `--since REF`. The refusal names it as a remedy, and argparse did not have it —
  a refusal that names a flag the CLI lacks cannot be acted on.

`tests/background/test_the_standalone_landed_binds_this_lanes_paths_not_the_other_sides.py` — six
controls, each named for its own defect. **Mutation-proven, all three edits run and reverted:**
restore the first-parent read → 4 red; make `_merge_base_side` fall back to `parents[0]` when it
cannot separate → 2 red (the two refusal legs, which is the point of them); drop `since=args.since`
from `main` → the two CLI legs red. The single-parent regression leg stays GREEN under the first
mutation and says so in its own docstring: it is a guard on the untouched majority, not a witness.

`tests/background/test_a_merge_is_a_landing_the_delivery_lane_can_see.py` — its fixture had no
`origin/main`, so under the new rule nothing separated its two sides. The fixture now publishes the
base it merges onto, which is what makes it the `merge side INTO main` case its assertions always
described. Its expectations are unchanged.

## What is NOT claimed

That no past turn was mis-graded. The finding left that open and this does not close it — the cheap
version is still *"look for claims whose bound paths lie outside the lane that holds them"*, and
nothing here ran it.

That the dead zone is now unreachable. It is reachable by construction, both controls hold it open
deliberately, and a tick that meets it pays one re-run with `--commit` or `--since`.

— Delivery seat, 2026-09-05.
