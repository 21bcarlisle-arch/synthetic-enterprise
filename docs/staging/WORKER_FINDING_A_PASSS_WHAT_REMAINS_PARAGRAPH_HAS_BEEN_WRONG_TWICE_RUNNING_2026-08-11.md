# WORKER FINDING — a wall pass's "what remains" paragraph has now been wrong two steps running

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-11, during KNIFE3 step 18 (`A_composition_lift`), while working the remainder
enumeration step 17 left behind.
**Disposition:** QUEUED as a candidate atom, NOT fixed on sight (SELF_INTERRUPT_DISCIPLINE — the
machine is not blocked; the supply of harness findings is infinite).
**Class:** one name, two numbers — a hand-maintained count in prose beside a mechanised one.

## Observed, with evidence

`docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md` §3l ("What did NOT fall", step 17, 2026-08-11)
states `run_phase2b` keeps **31 direct + 2 indirect**, then names four groups as the remainder.

Measured on the tree as it stood at `8dd04db1d`, via `tools/epistemic_wall.live_crossings()`:

- 34 direct live in total — **29** on `simulation.run_phase2b`, 4 on `simulation.customer_events`,
  1 on `simulation.run_phase4c_on_phase2b`.
- The four groups §3l names total 6 + 9 + 4 + 8 = **27**.
- The two edges in neither the count nor any group:
  `simulation.run_phase2b -> company.market.flexibility_revenue_book` and
  `simulation.run_phase2b -> company.market.ic_flexibility_revenue`.

So the headline over-counted the module by 2 (it appears to have folded in the other two modules'
edges) while the enumeration under-counted it by 2, and the two errors are unrelated. A reader
planning the rest of this pass off that paragraph — which is exactly what it exists for — would have
found two edges nobody had planned a group for.

Step 17's own `exit_evidence` filed the identical class against step 16 ("its headline reads
'2 EDGES CUT, 41 → 39 LIVE' while its EVIDENCE paragraph reports 45 live"). **That is two
consecutive steps, and step 17 wrote its own instance while filing step 16's.** A defect that
survives being named by the very step that names it is not an attention lapse.

## Why the code was never wrong

`tools/wall_crossing_dispositions.py` prints the live count from the walker on every run, and
`tests/architecture/test_epistemic_wall_ratchet.py` reds on a stale allowlist entry. The mechanised
count has been right throughout; only the prose has drifted. That is the finding: the register
carries two counts of the same tree, one derived and one typed, and nothing compares them.

## What step 18 did about it

Entered a CORRECTION block in §3l rather than editing the original paragraph (the record of what was
believed at the time is worth keeping), and wrote §3m's own remainder as `6 + 9 + 4 + 8 = 27` with
the arithmetic shown, because step 17's was not shown and did not close.

That is an instance fix. **R10 says an absurdity-class defect may not be closed with one** — the
class fails again at step 19 unless the count stops being typed.

## Candidate atom — the shape of a real fix

Make the register's per-module remainder DERIVED, not typed. Options, with the recommendation:

1. **(RECOMMENDED) `tools/wall_crossing_dispositions.py` gains a per-source-module breakdown and a
   check that every live edge on a module appears in exactly one named group** in that module's
   most recent section, failing rc≠0 on an edge in no group. Cheap: the walker already has the
   edges, and the group names are already in the register as prose lists — they would move to
   parseable markers alongside the existing `WALL-CROSSING-DESIGN` ones. Kills the class: an
   unplanned-for edge becomes impossible to leave unnamed, and the count cannot be typed at all.
2. Generate the "what did NOT fall" paragraph entirely and forbid hand-editing it. Stronger, but it
   throws away the prose reasoning about *why* a group is a group, which is the part worth reading.
3. Do nothing and rely on each step re-measuring. This is the status quo, and it has now failed
   twice in a row, so it is listed only to be rejected.

Sizing: S. `file_scope` is `tools/wall_crossing_dispositions.py`,
`docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md`, `tests/tools/test_wall_crossing_dispositions*`
— disjoint from any cut step, so it can run beside step 19 rather than blocking it.

R15 note for whoever builds it: the control must fail on its own named defect — a mutation that
deletes one edge from a group list, and a vacuity guard on the number of modules examined, since a
register with no parseable group markers would make every finding list empty for free.
