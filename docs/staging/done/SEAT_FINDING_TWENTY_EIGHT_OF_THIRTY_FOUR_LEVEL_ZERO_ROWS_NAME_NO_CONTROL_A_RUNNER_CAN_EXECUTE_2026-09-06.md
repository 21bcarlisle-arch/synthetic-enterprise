**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted

# Twenty-eight of thirty-four level-zero rows name no control a runner can execute

**Found:** 2026-09-06, delivery seat, building the lane-0 item
`the-map-cannot-say-zero-about-work-whose-controls-pass`. Measured with
`tools/level_zero_contradicted_by_its_own_controls.py`, written for it.

---

## The drawn work assumed a set that mostly does not exist

The lane-0 instruction was: refuse an atom at `level_current: 0` with `loop_stage: build` **when
the controls named in its own row all pass**, with PB6 and W2_19 named as the two live instances.
The check is built and it fires. But the instruction's own premise — that these rows name controls
— holds for six rows out of thirty-four.

```
  level_current: 0 + loop_stage: build            34 rows
    names no test_*.py file at all                26   ungradable, silent
    names a test_*.py file that is not on disk     2   ungradable, silent  (D9, PB5)
    names control file(s) that exist               6   gradable
```

**Of the six it can grade, four are contradicting themselves** — and only one of the four was
known when this started:

```
  SPINE_1_scenario_world_state          tests/sim/test_scenario_spine.py
  H41_the_map_ratchet_has_no_ongoing_drain   tests/design/test_simplifications_store.py
  SITE4_ia_register_and_nav             site/test_ia_register.py
  PB4_engagement_separated_from_elasticity   (repointed below; OPS11 froze its move)
```

Three rows in three different lanes, each at `level_current: 0` with a named, existing, passing
control. Their moves are not made here — they are now in the seat's orientation brief, which is
where a level move belongs — but they are the answer to whether this check was worth building.

W2_19, the doorbell's second named instance, is in the twenty-six. Its `file_scope` is
`['simulation/household_segments.py', 'simulation/population_draw.py', 'docs/market_research/',
'site/knowledge/']` — four scopes and no control. There is nothing for a check to grade, and
inventing a name to grade it against would be the fabrication this project keeps paying for.

**A directory is not a control, and that exclusion is load-bearing.**
`H40_full_suite_pollution_bisect` names `tests/`. Grading it against the whole suite would make
every lane's green H40's evidence — a verdict about the repository wearing an atom's name. Six
rows name a directory under `tests/` and are counted as naming nothing, deliberately.

## The two instances the check was built for were invisible for the same reason

PB4 and PB6 each landed a module and a dedicated passing test, and each row still read
`level_current: 0`. Neither could be seen by any instrument, and the reason is not that no
instrument existed — it is that **each row named the control file the build meant to write, and
the build wrote a differently-named one.**

```
  PB4  row named  tests/simulation/test_engagement_and_elasticity_are_separate.py
       1fe160dc8 wrote  tests/simulation/test_payment_channel_carries_the_engagement_antecedent.py
  PB6  row named  tests/company/test_the_engagement_observable_crosses.py
       99d2befb4 wrote  tests/company/test_the_engagement_observable_crosses_the_seam.py
```

Nothing catches this. `tools/scope_evidence_ratchet.py` keys on `level_current > 0` by an argued
design decision — a level-0 row naming files it *would* create is exactly the case that module
protects, and it is right to. So a level-0 row's `file_scope` is unchecked by construction, and a
row can name a file that never existed for as long as it stays at zero. Which it will, because the
thing that would move it off zero is the control it cannot name.

Both rows are repointed in this commit. PB6 moved L0→L1 (recorded,
`docs/observability/gate_authorizations.jsonl`). **PB4 did not move and should not have:** OPS11
refused the raise because lane `W2_customer_generator` holds a live BLOCKING finding —
`SEAT_FINDING_THE_ENGAGEMENT_ANTECEDENT_R1_NEEDS_IS_DESTROYED_BY_A_COLLAPSED_PAYMENT_BUCKET_2026-09-05.md`,
which is about the very antecedent PB4 builds. A row that is contradicted by its own controls
**and** correctly frozen by its lane is a real state, not a bug in either mechanism, and the
check's refusal text now says so rather than instructing the reader to do something the machinery
will refuse.

## What this costs, and it is not tidiness

`tools/lane_formation.py::formation` derives `buildable_lanes` from exactly this pair of fields.
A row stuck at zero is a permanently-buildable atom that keeps winning draws it has already been
paid for. That is the mechanism behind
`SEAT_FINDING_THE_PRODUCT_SHARE_IS_ZERO_AND_THE_SELECTOR_NOT_THE_DIAL_IS_WHY_2026-09-05.md`: it
corrupts the input to direction itself.

## The bound nearly made the check useless, and it did so silently

Wired into `background/delivery_seat.py`, the check has to fit inside a three-hourly orientation
whose brief must arrive. A per-atom timeout alone is not a bound on a pass — six gradable rows at
120s each is a twelve-minute worst case — so a whole-pass budget was added. **Set to 120s it
returned zero contradictions with all thirty-four rows ungradable.** Two expensive rows
(`D27`, `KNIFE3`, the latter naming twelve architecture suites) come first in map order and ate
the entire budget between them.

That output is honest and self-describing and still completely useless, because *no
contradictions* is exactly what a healthy map looks like. Measured properly: four of the six
gradable rows resolve in ~19s **between them** and produce every verdict the check exists for;
the other two exceed any cap worth setting and merely consume it. At 60s per atom and a 300s
budget the pass takes 2m19s, reaches every row, and reports the two it gave up on **by name** in
`bounded_out` — because `ungradable_count` cannot distinguish "names no control" from "has a
control I ran out of time to run", and only the second means the seat is being told less than the
check could have told it.

## Why this is LATENT and not BLOCKING

No published figure is wrong and no control is untrustworthy. The check does what it says over the
six rows it can speak about, and it is explicit — on stdout, per row, with the reason — about the
twenty-eight it cannot. What is missing is coverage, not correctness. **A check that grades six of
thirty-four and says so is worth more than one that grades thirty-four by inventing twenty-eight
subjects**, which is the shape this project has shipped before.

## The obvious next move, and the argument against it

The tempting fix is a gate requiring every `loop_stage: build` row to name a control file. It is
wrong for now, on this file's own rule that a mechanism should be the smallest thing that can
fail: twenty-six rows would need a control named at once, most of them genuinely unbuilt, and the
names would be invented to satisfy the gate. That is how `PB4`'s stale path got there in the first
place — a planned name written before the build, never reconciled after it.

The narrower version that would work: **when an atom's level is recorded as moving, require that
its row name a control file that exists.** That fires once, at the moment the evidence genuinely
exists, on one row at a time, and it would have caught both PB4 and PB6 at the commit that landed
them. Not built here; filed as the recommendation.
