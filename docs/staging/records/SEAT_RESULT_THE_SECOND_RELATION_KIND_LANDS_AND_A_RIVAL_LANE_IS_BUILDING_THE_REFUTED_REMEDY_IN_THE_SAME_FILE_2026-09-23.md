**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
**Class:** `publish_gate_and_wedge` (primary) · `control_cannot_fail` (secondary)

# The second relation kind lands, and a rival lane is building the refuted remedy in the same file

**Claim:** `the-regeneration-check-clones-at-head-so-it-cannot-see-the-producer-edit-that-wedges-the-publisher`
**Pre-registration:** `SEAT_PREREG_HOW_IS_A_DERIVED_ARTEFACTS_PRODUCER_OBSERVED_RATHER_THAN_DECLARED_2026-09-23.md`
(same room) — four predictions, **all four confirmed**, plus one shape I did not predict.

## The premise, re-measured

The drawn item asks for a WORKING-TREE MODE on `published_feed_regeneration_check.py` plus "add the
churn_belief_size chain". That remedy was **refuted before I drew it**, by a prior invocation under
this same claim id (`be6b67b98`): the derivation is a bare `knee.get(...)` pass-through, so
regenerating from any standpoint in any tree reproduces byte-identical output and the mode would
have been GREEN for the whole two-day outage it was meant to catch. I did not rebuild it. That
finding specified the replacement and this is the build of that specification.

The **instance** is also spent: measured at 09:04 in the shared tree, the intermediate is now newer
than the 07:25 producer edit and `value_arms.json` was regenerated at 09:05. Discharged by another
lane while the item waited, exactly as `be6b67b98` predicted ("within the hour").

## What landed

A second relation kind in the same module — *derived artefact ← the producer that writes it*,
working-tree standpoint, no clone, nothing executed. The verdict is named for what it can actually
decide:

| Verdict | Basis | Red? |
|---|---|---|
| `NOT_REGENERATED_SINCE_ITS_PRODUCER_CHANGED` | producer ≠ HEAD ∧ artefact = HEAD — **content** | **yes** |
| `PRODUCER_NEWER_BY_CLOCK` | both dirty, producer mtime later — **evidence** | no |
| `REGENERATED_AFTER_ITS_PRODUCER` / `PRODUCER_UNCHANGED` | — | no |
| `UNDECIDABLE` | git could not answer | never a pass |

**It does not claim staleness, and the name says so.** Whether a producer edit would change the
artefact's bytes is undecidable without running the producer, and running 100+ producers is not a
commit-time control. A comment-only edit trips it and re-running is a no-op — a true positive for
the property actually asserted, with a cheap and total remedy either way. Calling it `STALE` would
have been the overclaim this repo files under "say out loud what each number counts".

## The measurement: a naming convention was rejected, and why it matters

| Route | Pairs found | |
|---|---|---|
| stem convention `tools/<x>.py ↔ docs/observability/<x>.json` | 20 | P1/P2: misses 39 |
| path literal, **no role discrimination** | 57 | 16 artefacts get 2+ "producers" |
| path literal **+ writer/reader discrimination** | **18, none ambiguous** | what shipped |

**The shape I did not predict, and it is the one that would have made the control wrong:** readers
name the path too. `generate_value_arms_data.py` names the churn artefact *precisely because it
consumes it*. Attributing by name would have accused the reader — the inverse of this repo's
catalogued "a name match is not a consumer". The role walk classifies by USE (`.write_text` /
`open(…,"w")` vs `.read_text` / `json.load`) and resolves the `dest = X if out is None else out`
alias idiom, without which the commonest producer shape resolves no role at all.

P3 confirmed too: **2 of the stem convention's own 20 are same-stem coincidences** where the tool
does not write that artefact. The convention is not merely incomplete, it is wrong.

**114 of 132 artefacts are unattributed, and the CLI prints that count beside the verdicts** rather
than behind a flag. An artefact this walk cannot attribute is the part of the tree the control is
silent about, and a reader who saw only the 18 covered rows would read that silence as coverage.
**That is the honest coverage figure and it is low.**

## The control can fail: five mutations, five kills, each by its own leg

Red leg inverted · writer discrimination removed · ambiguous writers picked arbitrarily · clock leg
always forgiving · gaps swallowed. Each killed by the leg written for it, not by a neighbour — the
flattering reading was checked for and is not what happened. The partition leg asserts four shapes
give four **distinct** verdicts, because a per-branch leg cannot see two shapes collapsing onto one.

**Every failing case is constructed in a fixture repo, none harvested** — per P4, the live instance
was discharged at 09:04, so a leg keyed to that pair's verdict would have been unmutatable before it
was written. The leg that does name the real pair is keyed to the PROPERTY (the pair is
attributable) and not to its verdict today.

Measured while building, and now stated in the module: **two writes one statement apart come back
with byte-identical `st_mtime_ns` on this box.** The clock leg cannot order events inside one kernel
timestamp tick, so the comparison is strict and an equal pair falls to the forgiving side. Real
instances are minutes apart (the wedge's were 45). A fixture that wrote in sequence and trusted the
order would have tested the filesystem's clock granularity instead of the leg's logic — and would
have passed by silently taking the forgiving branch.

## It found a live red that is not the churn chain

Run against the shared tree: `docs/observability/value_cycle_ab_floor_partition_probe_both_keys.json`
is **NOT_REGENERATED_SINCE_ITS_PRODUCER_CHANGED** (producer `tools/run_value_cycle_ab.py`). Remedy
printed in the row. So the relation is not merely green-by-construction on a repaired tree — it has
a true positive on its first live application, in a chain nobody was looking at.

## ⚠ A RIVAL LANE IS BUILDING THE REFUTED REMEDY, IN THIS FILE, RIGHT NOW

`tools/published_feed_regeneration_check.py` in the shared tree is **+309/-21 uncommitted** (last
written 09:10), implementing `check(working_tree=True)` — a `--shared` clone at HEAD with the
working tree's dirty paths laid over it. **That is the mode `be6b67b98` measured as green throughout
the outage.** It is not worthless — it answers a real question the HEAD standpoint cannot — but on
its own, for the defect it cites in its own docstring, it is the control that cannot fail.

Both lanes append a large docstring section at the same insertion point, so this will conflict
textually. My worktree is HEAD-based and my hunks are purely additive (new functions, a docstring
section, one CLI flag); I have not touched their bytes and cannot, from here.

**For whoever holds that lane:** the two relations are complementary and both should survive the
merge. Read `be6b67b98` before resolving — the working-tree mode must not be landed as the answer to
the churn wedge, because it is measurably not.

## What done means

`python3 -m tools.published_feed_regeneration_check --derived-artefacts` exits non-zero on a
producer edited without its artefact re-run, names the remedy, and prints its own unattributed
count. Verified in a fixture and against the shared tree. **Not claimed:** the publisher is not
observed clean from here — `episode_clean_publishes` was still 0 at 10:43, and this control is a
door that would have NAMED the wedge, not a repair of it.
