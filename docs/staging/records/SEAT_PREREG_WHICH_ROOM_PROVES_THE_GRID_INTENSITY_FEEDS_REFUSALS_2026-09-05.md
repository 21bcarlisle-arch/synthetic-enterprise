**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# PRE-REGISTRATION: which room proves `generate_grid_intensity_feed`'s refusals?

**Written 2026-09-05 by the delivery seat BEFORE any mutation ran, in the shared tree at
`37bf9d2d6`. Claim id `register-low-water-evidence-convergence-sweep`. The predictions below are
kept unrevised beside the result whatever they score — a prediction filed after the answer is not a
prediction.**

---

## Why this subject, and what the sweep has learned so far

Subject 5. The four before it:

* `background/register_low_water.py` — four caller suites; one contract proved by **nobody**.
* `background/ops_repo.py` — three callers, **no test importer at all**.
* `simulation/run_phase3b_recalibration.py` — six callers, zero direct importers.
* `simulation/segment_vocabulary.py` — 8 callers, 3 direct, 321 reaching. Behavioural contracts died
  in up to seven rooms; **all four refusals died ONLY in rooms that name the module**, and two of
  the four apparent caller kills were golden-output tripwires that name no segment — *detected*, not
  *proved*.

`tools/generate_grid_intensity_feed.py` was drawn alongside segment_vocabulary and deliberately not
run then. The standing instruction from that turn: **start at the mutation list and attack refusals
first.** This module is unusually refusal-dense — `_percentile` and `build` both raise
`ShapeUnavailable`; `versus_published` has two distinct fail-closed returns; `published_series`
converts every exception into a reported why-not; the records carry `null` rather than a substituted
`1.0`; `dates_with_reads` swallows an unreadable artefact on purpose.

## The screen's `direct` column, re-derived by hand — and the callers collapse before the battery

The screen ranks this subject **8 callers, 2 direct**. `grep -rln generate_grid_intensity_feed tests/`
returns 4 files. Hand-reading all four:

| file | how it touches the subject | in the battery? |
|---|---|---|
| `tests/tools/test_grid_intensity_feed_and_explore_carbon.py` | `from tools import generate_grid_intensity_feed as gif` — real importer, 43 tests | **yes** |
| `tests/background/test_process_run_complete.py` | names `"tools.generate_grid_intensity_feed"` as a **string** in a pipeline-writer registry | **yes** |
| `tests/sim/test_grid_carbon_intensity.py` | prose only, in a docstring explaining the control is *elsewhere* | **yes** |
| `tests/tools/test_ep13_embedded_generation_bound.py` | reads the subject's **source text** to assert it does NOT import ep13 | **yes** |

The eight callers are `tools/ep13_*.py` (7) and `sim/grid_carbon_intensity.py` /
`sim/neso_carbon_intensity.py` (prose mentions only, not callers at all — the grep over-counts here
exactly as its own finding predicts).

**And every one of the seven ep13 callers imports the subject inside `measure()` and nowhere else** —
`from tools.generate_grid_intensity_feed import (...)` at `ep13_input_ceiling.py:545`,
`ep13_peer_bound.py:386`, `ep13_per_fuel_oracle_bound.py:460`, `ep13_biomass_oracle_bound.py:213`,
`ep13_ccgt_level_ceiling.py:668`, `ep13_ccgt_swap_ceiling.py:594`,
`ep13_embedded_generation_bound.py:521`. **`grep -c "measure()"` over each of the seven caller test
suites returns 0.** Not one of them calls the only function that reaches the subject.

## PREDICTION 1 — the impossibility, and how it is proved rather than argued

A suite that never imports a module cannot detect any semantic mutation of it. That is a claim about
*this tree*, not a general truth, so it is measured: a **poison round** replaces the subject's body
with a top-level `raise RuntimeError`, which reds any room that imports it at all, for any reason,
by any route.

> **P1: all seven ep13 caller suites stay GREEN under the poison.** Including
> `test_ep13_embedded_generation_bound.py`, whose one contact is `read_text()` on the source file —
> a reader, not an importer.
>
> **P2: `tests/sim/test_grid_carbon_intensity.py` stays GREEN under the poison** (prose mention).
>
> **P3: `tests/background/test_process_run_complete.py` REDS under the poison** — the registry entry
> `("tools.generate_grid_intensity_feed", "generate", "out_path", "OUT_PATH", ...)` reads like an
> importlib round-trip.

If P1 holds, the seven caller suites are excluded from the semantic battery **because they have been
proved unable to fail for this subject** — the same exclusion `test_segment_case_guard.py` earned
last turn, but here it covers 7 of the 8 callers the screen ranks this subject on.

## PREDICTION 2 — the semantic battery

Nine mutations, applied one at a time, each target asserted present exactly once, `__pycache__`
cleared between runs, every surviving room run separately.

| # | kind | the contract |
|---|---|---|
| M1 | refusal | `_percentile` raises on an empty series |
| M2 | refusal | `build` raises rather than publishing an empty shape |
| M3 | refusal | an unavailable published series is **said** (`available: False`), never omitted |
| M4 | refusal | no year over `MIN_SHARED_HALF_HOURS` ⇒ no headline, said as a why |
| M5 | refusal | an undefined comparison term survives as `null`, never dropped |
| M6 | refusal | `dates_with_reads` accepts only a 10-char dashed ISO date |
| M7 | behavioural | the two renormalisation divisors keep 8 places, not 4 |
| M8 | refusal | an uncovered half hour is `null` and **never a substituted `1.0`** |
| M9 | behavioural | `BIOMASS_DISPATCH_WIRED = False` is a decision, not an inert switch |

> **P4: the dedicated suite kills 7 of the 9, and the two survivors are M6 and M7.** Its 43 tests
> name the refusals explicitly — `..._REFUSES_to_publish_...`, `..._is_REPORTED_not_omitted`,
> `..._is_NULL_and_never_a_substituted_ONE`, `...does_not_count_toward_the_headline`,
> `..._UNWIRED_flag_is_a_DECISION_and_not_an_INERT_switch`. But no test names the divisor
> **precision** (M7), and `test_dates_with_reads_survives_a_missing_or_broken_artefact` is about
> `OSError`/`ValueError`, not about the date **shape** check one line up (M6).
>
> **P5: `test_process_run_complete.py` kills 0 of the 9.** It grades the writer's signature and
> output isolation, not a single one of these contracts.
>
> **P6: the whole battery is killed in at most ONE room.** This is the inverse of subject 4's shape:
> there, a well-named module's refusals were proved only where it was named, and the 321 reaching
> suites were blind by construction. Here the *reaching* count is small and the dedicated suite is
> strong — so the prediction is not "under-proved" but **"proved, and every contract standing on a
> single file"**. If M6 or M7 survives everywhere, that is the low-water rung this subject
> contributes.

## What would refute the sweep's emerging class

Two subjects showed one-suite proof, one showed nothing-proves-it, and subject 4 showed
refusals-proved-only-where-named. **A caller suite killing a refusal here would refute the class
outright** — and P1 says no caller suite can even run the code, which makes this subject the
strongest available test of it: if the callers cannot fail, "the callers do not prove it" is not a
finding about test quality, it is a fact about reachability, and the screen's `callers` column is
measuring something that has no bearing on proof at all.

*Scored against the result in the paired `SEAT_RESULT_*` document. Unrevised.*
