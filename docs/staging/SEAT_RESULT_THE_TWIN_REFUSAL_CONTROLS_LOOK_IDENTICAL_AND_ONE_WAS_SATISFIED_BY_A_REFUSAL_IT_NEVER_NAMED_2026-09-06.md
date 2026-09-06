**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# RESULT: the two refusal controls on `fuel_mix` look identical, and one of them was satisfied by a refusal it never named

**Measured 2026-09-06, delivery seat, isolated worktree, from HEAD `eb048fb64`. Claim id
`convergence-sweep-subject-4-grid-intensity-feed`. Pre-registration landed BEFORE the run at
`da7336230`.**

**Read this beside
`SEAT_RESULT_ONE_SUITE_PROVES_TWO_OF_FUEL_MIXS_TEN_CONTRACTS_AND_NOTHING_PROVES_THE_OTHER_EIGHT_2026-09-06.md`,
not instead of it.** The dispatcher launched two seats on one claim id three seconds apart and
both graded `fuel_mix`. This is the second run, reconciled in afterwards. It **replicates** that
result on every round it shares, and **inverts one of its ten rows**.

---

## The one row that inverts, and it is the headline

`tests/tools/test_grid_intensity_feed_and_explore_carbon.py` carries a matched pair of controls
four hundred lines apart, written the same way for the same reason — point a cache path at
nothing, assert `pytest.raises(fuel.FuelOutturnUnavailable)`:

* `test_the_feed_REFUSES_to_publish_without_the_fuel_mix_rather_than_reverting_to_the_old_shape`
* `test_the_feed_REFUSES_to_publish_without_the_BIOMASS_envelope_too`

The other run scores both as killers. **The fuel one is not.** Its kill came from the mutation's
replacement being the wrong TYPE, and one variable at a time is what shows it:

```
M2  (series = [])  -> AttributeError: 'list' object has no attribute 'items'
M11 (series = {})  -> FuelOutturnUnavailable: no coal reading in any year
```

Under `M2` the control reddens because the wrong exception class arrived — it never saw the
contract at all. Under `M11`, which is the same fallback with the type a real fail-open patch
would actually write, `FuelOutturnUnavailable` still arrives — from `coal_capacity_by_year`
refusing an empty series — the control **passes**, and the fallback ships. Verified directly, not
inferred: `1 passed in 1.55s` with the fail-open path in place.

**So the fuel leg of the pair was decoration, and `M2 proved` is one row too generous.**

The asymmetry is an accident of ordering, not of design. The fuel series feeds three adapters and
one of them re-refuses; biomass is computed last and nothing downstream of it does. Nothing in
either test's name, shape or docstring records that.

**Repaired, and mutation-proven both ways:** the control now asserts the refusal NAMES the missing
cache. Red under M11 (`1 failed`), green at HEAD (`1 passed`). The reason is written beside the
assertion, or the next reader deletes a redundant-looking string check on an exception message.

## The class this earns: a false KILL, and the mirror of the family's recorded false survivors

The battery already knows three ways a cell can lie about a survivor — the patch never applied,
the patch applied to a re-export, the suite never reached the subject — and one way it can lie
about a kill, which the null round covers: the suite graded the subject's text.

This is a fourth, and it is not the null round's:

> **A mutation whose replacement is the wrong TYPE reddens a suite on a `TypeError` /
> `AttributeError` rather than on the property under test, and `died` cannot tell the
> difference.**

It bites hardest on exactly the controls that matter most, because `pytest.raises(SomeError)` is
how a fail-closed control is written, and any mutation that makes the code crash differently
satisfies a reader looking at a red cell. **The rule: substitute a value of the SAME TYPE, or the
kill grades the type system.** More generally — any `pytest.raises(X)` where more than one site in
the call tree can raise `X` cannot, on its own, say which site fired.

*Same family as the recorded shape where two implementations give the same NUMBER for opposite
reasons. Here two code paths give the same EXCEPTION CLASS for different reasons, and it defeats
`pytest.raises` exactly as the other defeats an equality assertion.*

## What this run replicates independently

Run from a worktree **with the real caches present**, against a spec of eight contracts written
without sight of the other seat's:

* **The poison round, identically.** All seven `tests/tools/test_ep13_*.py` suites **NEVER REACH**
  the subject; `test_elexon_fuel_outturn.py`, `test_grid_intensity_feed_and_explore_carbon.py` and
  `test_process_run_complete.py` reach it. Both control suites stayed green, so the column is not
  void. Every caller imports inside a function body, so the floor grades *does this suite execute
  the calling path* — and on that question **63 of my 72 mutation cells were never at risk.**
* **`test_process_run_complete.py` reaches the subject and kills nothing** across all eight
  contracts. A reaching suite that proves no contract of it.
* **The null round's prediction is refuted, twice, independently.** Every suite came back
  behaviour-only. My marker was a bare no-op assignment; theirs additionally carried a comment
  naming two `ep13_*` modules. Neither moved a cell.
* **Seven of my eight survivors are missing tests, not equivalences.** Each was applied and
  `fuel_mix()` called against the real caches under a pinned hash seed; every one changes the
  result. The eighth is the biomass leg, which both runs kill for the same reason — the only cell
  of the two runs that agrees for the same reason.

## What a green null cell actually licenses

The six `ep13_*` tools do `.read_text()` the subject and AST-walk it. But what they grade is
*nothing in this file imports an `ep13` module*, and no behaviour-preserving marker can perturb
that property.

**A green null-round cell means the suite does not grade the bytes THIS EDIT touches. It never
means the suite runs the code.** Worth stating because a column of `behaviour only` reads like a
clean bill. Tuning a marker until it tripped those walks would have had to add an import — a
behaviour change — and the round would then have been measuring itself.

## Found by inspection, deliberately not repaired

`fuel_mix` is annotated `-> tuple[dict, dict, dict, dict]` and its docstring's first line
describes a four-member tuple. **It returns seven**, and every caller unpacks seven. Wrong since
the thermal floor, must-run and biomass envelope were added.

Not fixed here because the battery's reachability anchor is that exact `def` line: correcting it
changes the spec fingerprint and would leave both runs' results unreproducible against the spec
beside them. It is the hand-off, and it wants doing in one commit with the anchor.

## The bound on this run, stated rather than left to be noticed

`tests/tools/test_ep13_embedded_generation_bound.py` costs **607 seconds per pass**. It was graded
on baseline, poison and null — the three rounds that decide what its cells could mean — and the
poison round returned `NEVER REACHES`. It was then **excluded from the eight mutation rounds**,
which would have cost 80 minutes to produce eight cells the floor had already disqualified. The
engine prints those rows as `NOT YET GRADED ON EVERY SUITE (no verdict)`, which is why
`survived_all` reads `none` rather than a number.

## Where the sweep stands

| subject | shape |
|---|---|
| `register_low_water` | proved through one caller |
| `run_phase3b_recalibration` | proved through one caller |
| `ops_repo` | three reaching suites, nothing proving it |
| `segment_vocabulary` | refutes the shape — 8 killer suites, no unproved contract |
| **`generate_grid_intensity_feed.fuel_mix`** | **one killer suite; one contract genuinely proved, not two; 7 of 10 suites never reach it** |

The one-caller shape is not universal — `segment_vocabulary` settled that. What five subjects now
agree on is narrower and sharper: **caller count predicts nothing about evidence, and the poison
round is the only thing that has ever told UNPROVED from UNREACHABLE.** To which this subject adds
the other end: **a kill needs its reason established too, and two runs of one subject disagreed
about a kill on exactly the control that mattered most.**
