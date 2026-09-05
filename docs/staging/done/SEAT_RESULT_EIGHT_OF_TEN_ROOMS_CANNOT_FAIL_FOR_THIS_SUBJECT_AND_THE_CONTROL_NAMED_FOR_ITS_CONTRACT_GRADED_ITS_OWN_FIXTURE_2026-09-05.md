**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# RESULT: eight of ten rooms are PROVED unable to fail for this subject, and the one control named for its contract was grading its own fixture

**Result document. The pre-registration is
`docs/staging/records/SEAT_PREREG_WHICH_ROOM_PROVES_THE_GRID_INTENSITY_FEEDS_REFUSALS_2026-09-05.md`,
written before any mutation ran and kept unrevised beside this. It scored **4 of 6** on its named
predictions and its one wrong prediction is the finding. Claim id
`register-low-water-evidence-convergence-sweep`. Convergence-evidence sweep, subject 5:
`tools/generate_grid_intensity_feed.py`, run in the shared tree at `37bf9d2d6` with the subject
byte-identical to `origin/main`.**

---

## The battery

Ten rooms. Nine mutations plus a **poison** round, each applied **alone**, target asserted present
**exactly once** before patching, `__pycache__` cleared between every run, every room run
separately, original bytes restored and verified after each. Baseline **294 passed** across the ten.

## The poison round, and why it replaced two thirds of the work

The seven `ep13_*` callers all import the subject **inside `measure()` and nowhere else**, and
`grep -c "measure()"` over each of their seven test suites returns **0**. That is an argument, not a
measurement, so it was measured: the subject's body was replaced with a top-level
`raise RuntimeError`, which reds any room that imports it at all, by any route, for any reason.

| room | baseline | under the poison |
|---|---|---|
| `tests/tools/test_grid_intensity_feed_and_explore_carbon.py` | 43 passed | **1 error** (collection) |
| `tests/background/test_process_run_complete.py` | 95 passed | **95 errors** |
| `tests/sim/test_grid_carbon_intensity.py` | 40 passed | 40 passed |
| `tests/tools/test_ep13_biomass_oracle_bound.py` | 15 passed | 15 passed |
| `tests/tools/test_ep13_ccgt_level_ceiling.py` | 18 passed | 18 passed |
| `tests/tools/test_ep13_ccgt_swap_ceiling.py` | 13 passed | 13 passed |
| `tests/tools/test_ep13_input_ceiling.py` | 16 passed | 16 passed |
| `tests/tools/test_ep13_peer_bound.py` | 15 passed | 15 passed |
| `tests/tools/test_ep13_per_fuel_oracle_bound.py` | 17 passed | 17 passed |
| `tests/tools/test_ep13_embedded_generation_bound.py` | 22 passed (621s) | 22 passed (640s) |

**Eight of the ten rooms are green with the module raising on import.** They cannot detect any
mutation of it, and that is now proved rather than inferred. `P1`, `P2` and `P3` all held.

**This is what the poison round is for and it should become the sweep's first step.** It cost one
round and excluded eight rooms from nine; running the nine semantic mutations across all ten rooms
would have cost about **2h40m of embedded_generation_bound alone** to learn nothing, because a
suite that never executes a line of the subject returns "survived" for every mutation and
"survived" is exactly what an unproved contract also returns. The two are indistinguishable in the
output and opposite in meaning — a fail-silent shape in the sweep's own instrument. The poison round
separates them.

## The nine mutations, scored in the one room that can see them

`tests/background/test_process_run_complete.py` **killed 0 of 9** — `P5` held — despite the poison
showing it imports the subject in all 95 of its tests. It grades the writer's signature and its
output isolation, and touches none of these contracts. So every column below is one room.

| # | kind | contract | verdict |
|---|---|---|---|
| M1 | refusal | `_percentile` raises on an empty series | **survived — proved by nobody** |
| M2 | refusal | `build` raises rather than publish an empty shape | KILLED · `test_the_feed_refuses_to_publish_an_empty_shape` |
| M3 | refusal | an unavailable published series is *said*, never omitted | KILLED · `test_an_ABSENT_published_series_is_REPORTED_not_omitted` |
| M4 | refusal | no year over `MIN_SHARED_HALF_HOURS` ⇒ no headline | **detected, NOT proved** — see below |
| M5 | refusal | an undefined comparison term survives as `null` | **survived — proved by nobody** |
| M6 | refusal | `dates_with_reads` takes only a 10-char dashed ISO date | **survived — proved by nobody** |
| M7 | behavioural | the two renormalisation divisors keep 8 places | **survived — proved by nobody** |
| M8 | refusal | an uncovered half hour is `null`, **never a substituted `1.0`** | **survived, and a test carries that exact name** |
| M9 | behavioural | `BIOMASS_DISPATCH_WIRED` is a decision, not an inert switch | KILLED · two named tests |

**Three of nine proved. One detected. Five proved by nothing.** In a module whose dedicated suite
has 43 tests and reads, by name, as one of the better-controlled files in the tree.

### M4 is killed by a crash, and the test named for it stays green

M4 removes the refusal that fires when no year shares enough half hours with the published series.
Three tests went red and **all three are `ZeroDivisionError` at `generate_grid_intensity_feed.py:390`**
— `sum(overstatement) / len(overstatement)` over an empty list. None of them mentions the headline
threshold; two are about meter-read days and one about the biomass envelope.

`test_a_year_sharing_ONE_half_hour_does_not_count_toward_the_headline` — the test written for this
defect, whose docstring says *"MUTATION (must fire): drop the `counts_toward_headline` filter from
the average"* — **passed under the mutation.** It is correct about the flag; the mutation is on the
*refusal*, and the refusal is held up by an accidental division by zero. A tidy-up that guarded that
division, which is an obviously good change, would silently leave this contract proved by nothing.

This is subject 4's lesson at the next level down: a kill by a crash in an unrelated test is
**detection**, not **proof**, exactly as a kill by a golden-output tripwire was.

### M8 is the finding: the control named for the contract grades its own fixture

`test_a_half_hour_the_published_series_does_not_cover_is_NULL_and_never_a_substituted_ONE` — an R15
FAIL-OPEN control, with a docstring explaining that a substituted `1.0` "always drags the measured
gap TOWARD ZERO, i.e. toward 'our model is fine'".

Its subject is `_paired_feed()`, and that fixture **builds the records list itself**:

```python
"records": [{"date": d, "period": p, "shape": ours.get((d, p)),
             "published": published.get((d, p))} for d, p in keys if (d, p) in ours],
```

`published.get(...)` returns `None` for a missing key *by definition of `dict.get`*. The assertion
is a property of the test's own dictionary. The line that implements the contract is in
`build` — `None if published is None or (date_str, period) not in published` — and **nothing
executed it**. Proved, not argued: rewriting that `None` to `1.0` left all 43 tests in the file
green, and all 95 in the only other importing suite.

**Repaired this turn, and the repair is mutation-proven both ways.** A second leg drives the real
`build` with `published_series` patched to cover the second of two days:

* M8 (`None` → `1.0`) now **KILLS** it — 1 failed, 42 passed, and the failing test is the one whose
  name carries the contract.
* The inverse mutation (`None if True or ...`, every record null) **also kills it**, on the leg that
  asserts the covered day still carries a value — so the control cannot pass on an all-null feed,
  the partition-level check `CLAUDE.md` asks for.

The fixture legs are kept and the docstring now says what they grade and what they do not.

## Scoring the pre-registration, unrevised

| | prediction | outcome |
|---|---|---|
| P1 | all seven ep13 caller suites green under the poison | **held** |
| P2 | `test_grid_carbon_intensity.py` green under the poison | **held** |
| P3 | `test_process_run_complete.py` reds under the poison | **held** |
| P4 | the dedicated suite kills 7 of 9; survivors M6 and M7 | **WRONG** — it killed 3, and the survivors were M1, M5, M6, M7, M8 |
| P5 | `test_process_run_complete.py` kills 0 of 9 | **held** |
| P6 | the whole battery is killed in at most one room | **held** |

**P4 is the same error as last turn's, mirrored, and that is the thing to carry.** Subject 4's
write-up closed with: *"grading a suite from its subject matter instead of what its assertions
touch."* I then graded this suite from its **test names** instead of what their assertions touch —
`..._is_NULL_and_never_a_substituted_ONE` and `..._does_not_count_toward_the_headline` are both
precisely named, both cited in the prereg as the reason to predict a kill, and **neither proves its
contract**. A test name is a claim about what a test covers, written by someone who believed it. It
is evidence of intent, never of reach. Two turns, two directions, one root: the only reading that
grades a control is the one that follows its assertions to the line of shipped code they touch.

## What this does to the screen

The screen ranks this subject **8 callers, 2 direct**. Measured: **7 of the 8 callers cannot execute
a line of it from their own suites**, and the eighth contact is a `read_text()` asserting an
*absence*. `sim/grid_carbon_intensity.py` and `sim/neso_carbon_intensity.py` are prose mentions and
not callers at all — the grep over-counts here exactly as its own finding predicts, for the second
consecutive subject.

**The `callers` column has no bearing on proof.** Subject 4 showed the `reaching` column blind by
construction to refusals; this subject shows the `callers` column can be entirely unreachable. Both
columns rank; neither grades. That is now three subjects' worth of evidence that **only a battery
per subject answers the question**, and the poison round is the cheap first leg of one.

## Filed, not fixed (SELF_INTERRUPT_DISCIPLINE)

Four contracts survived and are correct in shipped code — LATENT, not blocking:

* **M1** `_percentile`'s empty-series raise. `test_the_two_percentile_implementations_cannot_drift_apart`
  never passes an empty list. Note also that this control compares `gif._percentile` to
  `neso._percentile` — worth a separate look for the same-number-by-opposite-routes tautology.
* **M4** the headline-coverage refusal, standing on a `ZeroDivisionError`.
* **M5** `None` surviving into the feed as `null` rather than being dropped, whose own comment says
  *"an absent key reads to every consumer as a comparison that came out clean"*.
* **M6** the 10-char dashed-ISO date shape in `dates_with_reads`.
* **M7** the 8-place divisor rounding, whose comment explains it is the one value **divided by**.

Also noted, unrelated to the battery: `fuel_mix()` is annotated `-> tuple[dict, dict, dict, dict]`
and returns **seven** elements; the docstring's first line names four. Cosmetic today because every
caller unpacks positionally, and filed rather than fixed on sight.

## The next hand

The screen ranks 12 more rows. **Run the poison round first on each** — it is minutes, it excludes
the unreachable rooms by proof rather than by argument, and on this subject it removed 80% of the
population before a single semantic mutation was written.
