**Severity:** LATENT · **Lane:** H_harness

# A landing step can only be caught by a tree it does not control. Every in-tree control is green while the claim is false.

**Found:** 2026-08-18, KNIFE3 step 41, landing the cut that steps 39 and 40 each wrote and
neither committed (`docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md` §3aj).

**Class:** `uncommitted_and_orphaned_work`.

---

## The observation

Four steps of one atom — 36, 37, 39, 40 — each wrote a complete piece of work and committed
none of it. Three of the four wrote, in their own committed-nowhere text, the rule they were
in the act of breaking. Step 40's section is titled *"The landing of §3ah, performed"* and
closes with *"Verified in the tree the commit would create, never in the working tree: 5 live
crossings … and 194 tests green."* That sentence was in no commit either.

The countermeasure so far has been prose: a STALE-DOORBELL NOTICE in the atom's `name` field,
rewritten every step, instructing the next step to run `python3 -m tools.wall_crossing_dispositions
--at-head`. It works when it is read, and it is written **by the step that is about to fail the
check it describes**, so it cannot catch itself. R3 (two-strike redesign) is four strikes past due.

## Why no test can be the replacement — this is the load-bearing part

The obvious mechanisation is a control in `tests/architecture/` that compares the register's stated
live-crossing count against the walker. **It would have been GREEN at steps 39 and 40.**

At both steps the working tree measured 5 live / 91 ruled / cut 86 / owed 5 and was entirely
self-consistent: the code, the register section, the falsifier and the walker all agreed, because
they were all reading the one tree that contained the unlanded work. HEAD measured 6/85/6. Nothing
inside the commit's own tree can see that gap, because the gap IS the difference between that tree
and the committed one. Every working-tree instrument agrees with the false claim — that is the
sentence the notice already contains, and it rules out the entire class of in-tree controls,
including the gate's would-be tree, which is likewise built from the working copy.

The only instrument that has ever caught this — at steps 38, 40 and 41 — is `--at-head`, precisely
because it reads a tree the failing step does not control.

## The control this needs

A **draw rung**, not a test. `background/supervisor.py` currently contains no reference to
`tools.wall_crossing_dispositions` at all. The rung:

* runs the walker both ways and compares live-crossing counts (and the ruled/cut/owed triple);
* on disagreement, re-surfaces `KNIFE3_wall_crossing_paydown` as drawable work whose stated
  deliverable is **a landing**, so the next tick is forced to land rather than reminded to;
* clears itself when the two agree — the close condition is the committed tree, which is
  independent of the thing being guarded (R15 anti-tautology).

**Generalise before building the instance (R10).** The predicate is not wall-specific: it is
*"an atom's own evidence artefact reports a different value at HEAD than in the working tree."*
The wall register is one carrier of that shape; the maturity map, the ratchet baselines and the
finding-class docs are others. Rule the class before wiring the single case, or this returns
under a different artefact's name.

**Fixture isolation is a precondition, not a detail** — a new rung that reads real git state will
otherwise make every other rung's test depend on the machine's working tree
(`feedback_new_draw_rung_needs_fixture_isolation`). The rung must take an injectable measurement
seam and its tests must never shell out to the live repo.

## What is NOT owed

The cut itself is landed (step 41). This finding is only the mechanism, and it is registered here
rather than built on sight per SELF-INTERRUPT DISCIPLINE: a landing step's deliverable is the
landing, and building the guard inside it would have been the fifth consecutive step to leave its
primary artefact unlanded while writing about the problem.
