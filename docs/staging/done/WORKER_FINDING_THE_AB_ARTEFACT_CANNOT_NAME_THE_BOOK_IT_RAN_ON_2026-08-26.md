**Severity:** LATENT · **Lane:** H_harness · **Rank:** after the current delivery-lane item · **Epoch:** 3 · **Atom:** `D9_worse_than_blind_chip_is_metric_blind`

**Discharged:** `tests/tools/test_run_value_cycle_ab.py::test_an_overridden_book_and_a_curriculum_book_are_DIFFERENT_CLAIMS`, `tests/tools/test_run_value_cycle_ab.py::test_a_book_the_caller_never_recorded_is_UNAVAILABLE_not_todays_curriculum`, `tests/tools/test_run_value_cycle_ab.py::test_the_arm_reports_the_book_IT_ran_on_and_not_the_one_live_at_assembly`, `tests/tools/test_run_value_cycle_ab.py::test_two_arms_on_TWO_books_fail_and_both_books_are_on_the_surface`, `tests/tools/test_run_value_cycle_ab.py::test_ONE_arm_cannot_agree_with_itself_so_the_verdict_is_CANNOT_TELL`, `tests/tools/test_run_value_cycle_ab.py::test_an_arm_that_recorded_NO_book_makes_the_verdict_CANNOT_TELL_not_TRUE`, `tests/tools/test_the_level_arm_in_the_ab_runner.py::test_two_arms_on_two_books_are_REFUSED_rather_than_reported`, `tests/tools/test_the_level_arm_in_the_ab_runner.py::test_the_run_publishes_a_same_book_verdict_a_reader_can_check` — 2026-08-30. Conditions 1–4 all closed; seven source mutations, each killing its own named test.

---

## Closed 2026-08-30 — and condition 1 had landed WRONG, which is why 2–4 could not

Condition 1 landed on 2026-08-27 as `book_identity`'s `served_segments`, read from the resolver
at **artefact-assembly** time. That is not the measurement this finding asked for, and the gap
was not cosmetic:

- `served_segments()` resolves from the curriculum file (or the env override) on **every call**,
  and an arm here is a full phase-4c pass. A curriculum edit or an override change between the
  control arm and the value arm genuinely puts two arms on two books — and an artefact that asks
  the resolver once, afterwards, reports the **second** book for both of them.
- It made condition 4 unbuildable. Comparing two calls to the same function in the same process
  is a tautology whose FAIL branch does not exist; a same-book control written on top of it would
  have been theatre. Snapshotting per arm (`book_at_run`, called beside each `run_phase4c`) is
  what gives the cross-arm control a reachable failure, and
  `test_two_arms_on_two_books_are_REFUSED_rather_than_reported` reaches it by flipping
  `SE_SERVED_SEGMENTS` between the two passes.

What now stands:

1. **Per-arm snapshot.** `book_at_run()` beside every arm that runs, including the optional level
   arm, which now has a `book_identity` block of its own.
2. **The override recorded separately** (`resolved_from`, `override_env`) — an env-overridden run
   and a curriculum run are different claims even when they resolve to the same list, and the
   test deliberately sets the override *equal to* the curriculum so a control that inferred the
   source from the segments could not pass it.
3. **`same_book_across_arms`**, published inside `book_identity` so the verdict cannot be
   deployed apart from the books it grades. Tri-state: `null` is "cannot tell", and it is the
   verdict whenever fewer than two arms recorded a book or any arm recorded none — one arm
   agreeing with itself is a pass branch reached by having nothing to compare.
4. **The run refuses** a delta whose arms served different segments, the same treatment the
   control-arm emptiness check already gets. Compared on the RESOLVED segments and never on
   account counts: different prices cause different churn, so a control keyed to the arms'
   realised books would go red precisely when the experiment worked.
5. **Fail closed on an unrecorded book.** `served_segments: null` plus a stated reason, rather
   than today's curriculum standing in for a book nobody observed.

Not backfilled, deliberately: the three artefacts below cannot have their books established
after the fact. `docs/design/THE_VALUE_CYCLE_REALISED_AB.md` carries the annotation instead, and
now also carries why condition 1's first landing was half a repair.

# The value-cycle A/B artefact cannot name the book it ran on

**Filed by the worker seat, 2026-08-26, while writing the resi+SME reading into
`docs/design/THE_VALUE_CYCLE_REALISED_AB.md`. QUEUED, not fixed on sight (SELF-INTERRUPT
DISCIPLINE): a second concurrent code change plus its gate run would have contended with the
in-flight suspension landing.**

## The defect

`tools/run_value_cycle_ab.py` writes an artefact carrying `arm_identity`, `control_credibility`,
`decision_shape`, `belief_vs_outcome` and the basis string for every margin figure — and
**nowhere records which segments the run served.**

```
$ grep -n "served_segments\|SE_SERVED_SEGMENTS" tools/run_value_cycle_ab.py
$   # (no output)
```

The population is read through `simulation.live_population`, which applies
`docs/design/curriculum/served_segments.json` (and the `SE_SERVED_SEGMENTS` override) at import
time. So the book is a **free variable of the run that the record of the run does not capture.**

## Why this is the finding and not a tidy-up

This is the exact mechanism of the 48-hour confusion the suspension landing closes. Three
readings were produced from this tool on 2026-08-26:

| artefact | control accounts | book | EV delta |
|---|---|---|---|
| `value_cycle_ab.json` | 172 | resi + SME + I&C | +£2,293,743 |
| `value_cycle_ab_resi.json` | 131 | resi + SME | +£10,800 |
| `value_cycle_ab_resi_only.json` | 123 | resi | +£9,759 |

**The book column is inferred from account counts and from the filenames — neither is in the
artefact.** Two of those three readings were quoted as the company's answer to its own founding
question while being about a segment the director had already ordered suspended, and no control
could fire, because the artefact had nothing to check against.

It is the R14 shape one level up: *no financial figure without its clock* — and a realised A/B's
population is as much a part of its basis as its settlement clock is. It is also FAIL-OPEN in
R15's sense: a run on the wrong book produces a clean, complete, entirely plausible artefact.

The filename is not the control. `value_cycle_ab_resi.json` in fact served resi **and SME**, so
the one piece of provenance a reader does have is actively misleading.

## What closes it

1. `run_value_cycle_ab` records `served_segments` — the resolved list, read back from
   `simulation.live_population.served_segments()` after the run rather than from the file, so it
   reports what the run USED and not what the curriculum said (independence: a tautology here
   would re-read the same source the run read).
2. It records the `SE_SERVED_SEGMENTS` override separately when set, since an env-overridden run
   and a curriculum run are different claims.
3. R15 mutation: a run with the override set to `resi` must produce an artefact whose
   `served_segments` differs from one without it — a control that cannot distinguish two books
   is the defect being closed, not a fix for it.
4. Both arms are asserted to have served the SAME book. Two arms on two books is an
   uncontrolled variable of exactly the class `arm_identity` already exists to catch, and it is
   currently unguarded on the population axis.

Existing artefacts cannot be backfilled honestly and should not be — the three above are
annotated in `docs/design/THE_VALUE_CYCLE_REALISED_AB.md` instead, which is where a reader
looks.

Archive to `docs/staging/done/` when the artefact names its own book and the mutation test
proves it can tell two books apart.
