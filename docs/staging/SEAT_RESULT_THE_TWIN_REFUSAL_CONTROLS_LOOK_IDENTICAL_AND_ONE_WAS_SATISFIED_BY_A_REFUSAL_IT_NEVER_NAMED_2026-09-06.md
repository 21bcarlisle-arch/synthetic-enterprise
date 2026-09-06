**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# RESULT: the two refusal controls on `fuel_mix` look identical, and one of them was satisfied by a second refusal it never named

**Measured 2026-09-06, delivery seat, isolated worktree at `eb048fb64`. Claim id
`convergence-sweep-subject-4-grid-intensity-feed`. Spec:
`tools/grid_intensity_feed_contract_battery.py` (fingerprint `2ca33c272697`), over the shared
engine `tools/contract_battery.py`. Pre-registration landed BEFORE the run at `da7336230`:
`docs/staging/SEAT_FINDING_THE_NEXT_SUBJECTS_CONVERGED_SURFACE_IS_MOSTLY_RE_EXPORTS_AND_A_BATTERY_WOULD_HAVE_SCORED_THEM_2026-09-06.md`.**

The fifth graded subject of the convergence-evidence sweep — the pre-registration calls it the
fourth, written before `ops_repo` landed — `tools/generate_grid_intensity_feed.py`, graded on
`fuel_mix` only — the one name of its five-name converged surface that this module
actually defines.

---

## The pre-registered prediction, and both halves of the verdict

> `fuel_mix` is proved by `test_grid_intensity_feed_and_explore_carbon.py` and by nothing else in
> the ten-suite population, and at least one `ep13_*` suite reddens under the NULL round.

**First half: CONFIRMED, and more sharply than predicted.** Exactly one of eight contracts is
proved, by exactly one test, in exactly that suite.

**Second half: REFUTED.** Every suite is behaviour-only under the null round, including all six
textual readers. That refutation is the more useful result and is treated below rather than
buried.

## The table

Ten suites. `tests/tools/test_ep13_embedded_generation_bound.py` is excluded from the mutation
rounds and the exclusion is stated, not silent — see the bound at the end.

| | contract of `fuel_mix` | killed by | missing test or equivalence? |
|---|---|---|---|
| M1 | an absent FUEL cache raises out of `fuel_mix` | **nothing** | missing test — **repaired here** |
| M2 | an absent BIOMASS cache raises too | `test_grid_intensity_feed_and_explore_carbon.py` (1 test) | — proved |
| M3 | the thermal floor is unpacked to per-YEAR here | **nothing** | missing test |
| M4 | the thermal floor comes from the THERMAL cache | **nothing** | missing test |
| M5 | the returned tuple's ORDER | **nothing** | missing test |
| M6 | coal capacity is MEASURED from the outturn series | **nothing** | missing test |
| M7 | the published import coverage is the MEASURED one | **nothing** | missing test |
| M8 | must-run coverage is measured, not asserted complete | **nothing** | missing test |

Every survivor was put to the question rather than assumed: each mutation was applied and
`fuel_mix()` called against the real caches under a pinned hash seed, and each one changes the
result. **Seven of eight are missing tests. None is an equivalence.**

## The headline: two controls that look the same, and only one of them is one

`test_grid_intensity_feed_and_explore_carbon.py` carries a matched pair, four hundred lines
apart, written the same way for the same reason:

* `test_the_feed_REFUSES_to_publish_without_the_fuel_mix_rather_than_reverting_to_the_old_shape`
* `test_the_feed_REFUSES_to_publish_without_the_BIOMASS_envelope_too`

Each points a cache path at nothing and asserts `pytest.raises(fuel.FuelOutturnUnavailable)`.
The biomass one killed M2. **The fuel one passed under M1 entire** — verified directly, not
inferred: `1 passed in 1.55s` with the fallback in place.

One variable at a time, because the first probe moved two and could attribute nothing:

```
--- FUEL cache absent ---
  pristine : RAISED FuelOutturnUnavailable :: /var/tmp/no_such_cache.json does not exist...
  M1       : RAISED FuelOutturnUnavailable :: no coal reading in any year, so no capacity can be measured
--- BIOMASS cache absent ---
  pristine : RAISED FuelOutturnUnavailable :: /var/tmp/no_such_cache.json does not exist...
  M2       : RETURNED -- NO REFUSAL AT ALL
```

Under M1 the refusal still arrives — from `coal_capacity_by_year`, which independently refuses an
empty series. **Same exception class, different site, and `pytest.raises(Class)` cannot tell them
apart.** So the fail-open fallback the test exists to forbid could be written into `fuel_mix`
tomorrow and this control would stay green.

**The asymmetry is an accident of ordering, not of design.** The fuel series feeds three adapters
and one of them re-refuses; biomass is computed last and nothing downstream of it re-refuses.
That is the whole of why one twin is load-bearing and the other was decoration, and nothing in
either test's name, shape or docstring records it.

**Repaired in this commit**, and mutation-proven both ways: the control now asserts the refusal
NAMES the missing cache. Red under M1 (`1 failed`), green at HEAD (`1 passed`). The reason is
written beside the assertion, because the next reader will otherwise see a redundant-looking
string check on an exception message and delete it.

*This is a new member of an old family. The recorded shape is two implementations giving the same
NUMBER for opposite reasons; this is two code paths giving the same EXCEPTION TYPE for different
reasons, and it defeats `pytest.raises` exactly as the other defeats an equality assertion. Any
`pytest.raises(X)` where more than one site in the call tree can raise `X` is a candidate.*

## The poison round: seven of eight "callers" have suites that never execute the calling path

| suite | reaches `fuel_mix`? |
|---|---|
| `tests/sim/test_elexon_fuel_outturn.py` | reaches |
| `tests/tools/test_grid_intensity_feed_and_explore_carbon.py` | reaches |
| `tests/background/test_process_run_complete.py` | reaches |
| all seven `tests/tools/test_ep13_*.py` | **NEVER REACHES** |

Both control suites stayed green, so the floor discriminates and the column is not void.

This is hazard 3 of the pre-registration, confirmed. Every caller imports inside a function body,
so the floor grades *does this suite execute the calling path* rather than *does this suite import
the module* — and on that stricter and more honest question, **63 of the 72 mutation cells in the
table above were never at risk.** The screen's "8 first-party callers" is correct about the tools
and says nothing about the suites.

`tests/background/test_process_run_complete.py` reaches the subject and killed nothing across all
eight contracts. It is a reaching suite that proves no contract of it — the ops_repo shape again,
in a population where two other suites do carry evidence.

## The null round was refuted, and the reason is a limit worth writing down

The prediction was that at least one textual reader would redden. None did.

The six `ep13_*` tools do read the subject with `.read_text()` and AST-walk it — that part of the
pre-registration was right. But what they grade is *nothing in this file imports an ep13 module*,
and a behaviour-preserving marker does not perturb that property. So:

**A green null-round cell means the suite does not grade the bytes THIS EDIT perturbs. It does not
mean the suite runs the code.** The round is a detector for one class of text-grader, not for the
class. Said here because a column of `behaviour only` reads like a clean bill and is not one, and
because the flattering reading was available and was pre-registered against.

The honest instrument was still the right one to reach for: an edit tuned until it tripped those
walks would have had to add an import, which is a behaviour change, and the round would then have
been measuring itself.

## One defect found by inspection, not by the battery, and left for a follow-on

`fuel_mix` is annotated `-> tuple[dict, dict, dict, dict]` and its docstring's first line
describes a four-member tuple. **It returns seven**, and all seven callers unpack seven. The
annotation has been wrong since the thermal floor, must-run and biomass envelope were added.

Not repaired here on purpose: the battery's reachability anchor is that exact `def` line, so
correcting it changes the spec fingerprint and would leave the results above unreproducible
against the spec landing beside them. It is the hand-off.

## The bound on this run, stated rather than left to be noticed

`tests/tools/test_ep13_embedded_generation_bound.py` takes **607 seconds per pass**. It was
graded on baseline, poison and null — the three rounds that decide what its cells could mean —
and the poison round reported `NEVER REACHES`. It was then **excluded from the eight mutation
rounds**, which would have cost 80 minutes to produce eight cells the floor had already
disqualified. The engine prints those rows as `NOT YET GRADED ON EVERY SUITE (no verdict)` and
they carry no verdict on the standing prediction, which is correct and is why `survived_all`
reads `none` above rather than eight.

## What this does NOT establish

Nothing about `AGWS_CACHE`, `DEMAND_CACHE`, `aggregate_demand` or
`aggregate_renewable_generation` — four fifths of the converged surface, and re-exports of
`sim/grid_carbon_intensity.py` and `sim/generation_demand_history.py`. Neither owner has been
screened for convergence in its own right.

Six contracts (M3–M8) remain unproved by every suite that reaches the subject. Only M1 was
repaired, because only M1 had a control already claiming to prove it.

## Where the sweep stands after four subjects

| subject | shape |
|---|---|
| `register_low_water` | proved through one caller |
| `run_phase3b_recalibration` | proved through one caller |
| `ops_repo` | three reaching suites, nothing proving it |
| `segment_vocabulary` | refutes the shape — 8 killer suites, no unproved contract |
| **`generate_grid_intensity_feed.fuel_mix`** | **one killer test in one suite; seven of eight contracts unproved; seven of ten suites never reach it** |

The one-caller shape is not universal — `segment_vocabulary` settled that. What four subjects now
agree on is narrower and sharper: **caller count predicts nothing about evidence, and the poison
round is the only thing that has ever told the two apart.**
