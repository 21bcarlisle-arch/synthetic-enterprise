# REPORT — a group ruling whose stated evidence held for only one of its three members

**Severity:** LATENT · **Lane:** H_harness

**KNIFE3 step 10, 2026-08-10.** Commits `fc450fde3`, `d7ca5a13d`, `bb5e4e002`. Pushed.

## What happened

`A_composition_lift` part 1 (step 9) lifted seven scenario harnesses out of `simulation/` and left
three, describing the three it left with one sentence in both the register and the atom record:
**"all three with walled in-edges."**

An AST census over `company/`, `saas/`, `sim/` and `simulation/` — the same instrument step 9 used,
pointed at the files it did *not* move — shows that sentence is **true for one of the three**.
`run_phase2b` has a walled importer (`simulation/run_scenario.py`). `run_phase4c_on_phase2b` and
`run_segments` have **zero**.

The ban was still right for all three. It rests on a **different condition in each**:

| File | The condition that actually blocks it |
|---|---|
| `run_phase2b` | 1 **and** 2 — a walled importer, plus 18 module-level symbols imported elsewhere |
| `run_phase4c_on_phase2b` | 3, **by its own docstring** (*"a pure LIBRARY — no CLI and no `__main__`"*), and 2 on `build_monthly_bills` |
| `run_segments` | 4 only — and it was repairable |

## The generalisable defect

**A group ruling states one reason; the group's members can each fail for a different reason. Stating
the reason that fits the loudest member makes the ruling uncheckable.** Anyone re-deriving
"all three with walled in-edges" finds it false for two, and is entitled to conclude the ban was
wrong — when the ban was right the whole time and its real support was never written down.

This is not the same as being wrong. Nothing was mis-ruled and nothing was mis-cut. What was missing
is that the evidence was never taken **per member**, so the record could not survive being checked.
The four conditions are now stated in the register as **per-file, not per-group**, and §3d carries
the census as a table with a verdict in every cell.

The tell to watch for: a ruling that names N items and gives one reason. If the reason was measured
on one of them and asserted for the rest, that is this class.

## What it unblocked

Naming `run_phase4c_on_phase2b`'s real blocker makes step 9's own sentence — *"their blocker is part
2"* — mean something specific: B5's residual and B4's remainder wait on a **library holding a
225-line bill-assembly routine**, not on a walled importer. That is a different piece of work from
the one "walled in-edges" implied.

And it turned up the one file whose only failing condition was repairable: `run_segments` was handing
`sim.hedging_strategy.MIN_HEDGE_FLOOR` into the company's `price_fixed_tariff` — **a second live
instance of the leak B7 cut five steps earlier**, which is what makes that a class rather than an
anecdote (R10). Repaired by the B7 template in the same commit as the lift, repair first, because
lifting first would have moved the leak somewhere nothing counts it.

## Related

* `docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md` §3d (the census), §3e (the cut)
* `docs/staging/WORKER_FINDING_RULE_3_HAS_THE_SAME_RENAME_BLINDNESS_2026-08-10.md` — queued
* `docs/staging/done/WORKER_FINDING_A_PURE_RENAME_READS_AS_A_NEW_OVERSIZED_FUNCTION_2026-08-10.md` — built at step 10a
