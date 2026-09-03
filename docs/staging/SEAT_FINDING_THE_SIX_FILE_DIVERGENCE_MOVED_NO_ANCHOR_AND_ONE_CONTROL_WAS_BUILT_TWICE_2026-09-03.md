**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The six-file divergence moved no anchor, and one control was built twice under two names

**Class:** `uncommitted_and_orphaned_work` (primary), `controls_that_cannot_fail` (secondary)
**Filed:** 2026-09-03, delivery seat, Lane 0, claim
`the-baseline-was-beaten-in-a-world-that-no-longer-exists`
**Subject:** the shared tree at `/home/rich/synthetic-enterprise`, 8 behind `origin/main`
(`5d804d671` vs `c2e7921c3`), with six large uncommitted drafts blocking the fast-forward.

---

## The alarm, and why it is the wrong reading

The shared tree is 8 commits behind origin and holds uncommitted drafts on six files that origin
moved in `416e829c7`/`2af612b46`/`dda5a27b2`. Neither side is a subset of the other:

| path | tree-vs-HEAD | origin-vs-HEAD | tree-vs-origin |
|---|---|---|---|
| `simulation/departure_level_anchor.py` | +21/−2 | +85/−6 | +25/−85 |
| `site/data/value_arms.json` | +103/−31 | +39/−27 | +81/−21 |
| `site/test_the_baseline_comparison_reaches_the_reader.py` | +300/−1 | +52/−0 | +292/−45 |
| `tests/architecture/test_switching_rate_commons.py` | +91/−0 | +98/−1 | +80/−86 |
| `tests/tools/test_generate_value_arms_data.py` | +161/−7 | +161/−4 | +165/−168 |
| `tools/generate_value_arms_data.py` | +372/−21 | +174/−2 | +374/−195 |

One of those files is the departure level anchor, which is the exact quantity this claim exists
about. **The obvious reading is that the shared tree is in a third world — neither HEAD's nor
origin's — and that every daemon running from it is producing figures in a world that exists
nowhere in git.** That reading is wrong, and it is wrong on a measurement rather than on an
argument.

## MEASURED: all three trees and the artefact are in ONE world

`world_level_identity()` (landed on origin in `dda5a27b2`) digests `year_level_anchor` for every
year in the published switching record. Recomputed here by the same arithmetic against three
sources of the anchor block — `HEAD:simulation/departure_level_anchor.py`,
`origin/main:simulation/departure_level_anchor.py`, and the uncommitted working-tree copy:

| year | HEAD | origin/main | WORKING TREE |
|---|---|---|---|
| 2016 | 4.259915 | 4.259915 | 4.259915 |
| 2017 | 7.372584 | 7.372584 | 7.372584 |
| 2018 | 2.945347 | 2.945347 | 2.945347 |
| 2019 | 6.637286 | 6.637286 | 6.637286 |
| 2020 | 6.359296 | 6.359296 | 6.359296 |
| 2021 | 5.641346 | 5.641346 | 5.641346 |
| 2022 | 1.000000 | 1.000000 | 1.000000 |
| 2023 | 2.033232 | 2.033232 | 2.033232 |
| 2024 | 4.259915 | 4.259915 | 4.259915 |
| 2025 | 4.259915 | 4.259915 | 4.259915 |

**digest `39a192ce04c1eda8` for all three — equal to `world_identity.digest` in
`value_cycle_ab_s1_three_arm_20260903.json`, the world the live re-run ran in.**

So the six-file divergence is prose and functions, and **it moves not one anchor value**. The
three floor legs now running in `/var/tmp/se-seat-executor` (pids 2964127 / 2969556 / 2969617, at
`c2e7921c3`) are in the same world as the three-arm leg they will bound. On world grounds the
same-world requirement — *"same world on both sides or the comparison is not a comparison"* — is
intact, and the divergence is not a reason to re-run anything.

**This is the check the item says nothing performs.** Every control here asks whether a figure is
arithmetically right; the digest asks whether its world still exists, and it is the first time it
has been asked of the *shared tree* rather than of two artefacts. It answered NO-CHANGE, which is
the unflattering-to-my-own-hypothesis answer and is why it is worth recording: an 8-commit,
six-file, anchor-touching divergence that moves no anchor would otherwise be re-derived as an
alarm by the next seat, exactly as it was by this one.

## The real defect: one control, two lineages, neither aware of the other

The six drafts are not a stale copy of origin's work. They are a **parallel implementation of the
same capability**, and the two do not share a single symbol:

* **Origin, landed and gated:** `world_level_identity()` → `_world_provenance()` → feed key
  `world_provenance` → asserted at `site/test_the_baseline_comparison_reaches_the_reader.py:1988`.
* **Shared tree, uncommitted:** `_world_moved_since()`, `_staleness_caveat()` and the door tests
  `test_the_vintage_of_the_comparison_reaches_the_reader`,
  `test_the_stale_world_statement_names_the_anchor_that_sets_the_surface`, plus three
  `test_MUTATION_*` legs.

`grep -c` for `world_level_identity`, `_world_provenance` and `world_provenance` in all three
shared-tree drafts returns **0, 0, 0**. `git log --all -S_world_moved_since` finds the symbol in no
commit on any branch — only in the two preservation refs.

This is the VAT shape the seat is the only place that can see: one requirement, two
implementations, landed by two seats within hours, and no control anywhere able to notice that the
second exists.

## Not all of it is duplicate, and that is the part at risk

The shared-tree draft also carries `_svt_drift_belief()` in `tools/generate_value_arms_data.py`
with six door tests around it — the *publishing* half of the SVT drift belief. The belief itself is
on origin (`simulation/run_phase2b.py`, `tests/company/crm/`), but this publishing function is in
no commit on any branch. **Adopting origin's lineage wholesale destroys it**, and it is not a
duplicate of anything.

## Preserved, twice, and addressable

* `refs/preserved/shared_tree_divergent_2026-09-03` → `134d3d591` — a prior seat, 7 paths, 11:34.
* `refs/preserved/shared_tree_20260903T1104Z` → `e8f3a2618` — this seat, **whole worktree**, 12:04
  local, so it is the superset and includes `site/data/value_arms.json` as rewritten at 11:45.

Neither is on `main` and neither is a landing. Nothing is lost whatever the disposition.

## Recommended disposition — NOT executed here, and why

Adopt origin's `world_provenance` lineage (landed, gated, on the deployed page); salvage
`_svt_drift_belief` and the `test_MUTATION_*` legs from the preserved ref onto it; discard the rest
of the tree's world-currency draft as the duplicate it is. That is a three-way merge of six large
files followed by a full re-gate.

**It was not done in this bounded tick, on two grounds, both checked rather than assumed.** A full
suite (`pytest tests/ -q`, pid 3035242) has been running from the shared tree throughout this turn;
rewriting six files under it corrupts its result and it would be stamped at the pre-merge commit.
And the three floor legs are mid-run — the reconciliation should land after they do, so the promote
and the merge are graded together rather than two moving parts at once.

## What is NOT claimed

That the fast-forward is safe in general — only that it is safe **on world grounds**, which is the
one question this claim owns. The six files' behavioural divergence is untested here and is the
merge's problem, not the digest's.

That `2,335.87` is distinguishable from zero. The floor legs answer that and had not returned when
this was filed.

## Class registration

`uncommitted_and_orphaned_work`. The novel leg is that the orphaned work is a
*second implementation of a control that landed hours earlier*, so the usual remedy (land it) is
wrong and the usual alarm (it will be swept) understates it: the drafts are armed to revert a
landed control the moment anyone commits those paths by pathspec.
