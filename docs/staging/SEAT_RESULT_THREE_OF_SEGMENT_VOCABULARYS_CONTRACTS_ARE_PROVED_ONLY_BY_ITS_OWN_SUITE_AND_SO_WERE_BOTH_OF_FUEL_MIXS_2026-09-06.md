**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# RESULT: three of `segment_vocabulary`'s eight contracts are proved only by its own suite, and so were both of `fuel_mix`'s kills

**Measured 2026-09-06, delivery seat, isolated worktree `/var/tmp/se-seat-executor` at `2722a8401`.
Claim id `converged-battery-audit-mixed-populations`. Grades
`SEAT_PREREG_WHAT_THE_CALLER_ONLY_RE_REDUCTION_OF_THE_TWO_MIXED_SPECS_WILL_SHOW_2026-09-06.md`,
landed in its own commit BEFORE the re-reduction ran. All five predictions hold. The finding is
what the census found on the way past, which no prediction covered.**

**No test was re-executed.** `survived_all` is a pure reduction over `row["per_suite"]`; a cell is
`(mutation, suite)` and what it measures does not depend on which population the reduction later
uses. Both subjects' cells were already on disk, so the corrected verdict cost two file reads.

Sources, as fixed in the pre-registration: `/var/tmp/segvocab_battery.json`,
`/var/tmp/gif_fuel_mix_battery_CACHED.json`,
`/var/tmp/grid_intensity_fuel_mix_battery_95c9da4db380.json`.

---

## The answer

| | published | on the CALLER population |
|---|---|---|
| `segment_vocabulary` contracts unproved | **0 of 8** | **3 of 8** — M3, M4, M8 |
| `segment_vocabulary` distinct killers | 8 suites | **5 caller suites** of 6 |
| `fuel_mix` contracts killed | 2 of 10 | **0 of 10** |
| `fuel_mix` rows carrying a machine verdict | — | **0** — the eighth caller was never graded |

### `segment_vocabulary` — the three that only its own suite proves

| contract | killed by DIRECT | killed by CALLER | caller verdict |
|---|---|---|---|
| M1 alias maps to its own canon | 3 | 5 | dies |
| M2 lookup is case-insensitive | 3 | 4 | dies |
| **M3 a `CompanyBookLabel` is refused** | **1** (`W215`) | **0** | **SURVIVES** |
| **M4 a present-but-unknown segment RAISES** | **3** | **0** | **SURVIVES** |
| M5 `is_business` false for a household | 2 | 2 | dies |
| M6 `BUSINESS_SEGMENTS` contains SME | 2 | 2 | dies |
| M7 `CANONICAL_SEGMENTS` is all three | 1 | 1 | dies |
| **M8 an absent segment defaults to RESIDENTIAL** | **1** (`CASE`) | **0** | **SURVIVES** |

M4 is the sharpest: **three** suites kill it and all three are the subject's own. A reader of
`killed_by` sees a well-covered contract; not one caller of this module can tell whether a
present-but-unknown segment raises or silently defaults — which is one alias-table edit away from
C5 and C6 returning by the route the module exists to close.

### `fuel_mix` — both kills were the subject's own suite, and no row has a verdict

All ten contracts (eleven on the M11 re-run) survive every caller suite. M1, M2 and M11 are killed
by `tests/tools/test_grid_intensity_feed_and_explore_carbon.py` and by nothing else, and that suite
is a DIRECT importer. Separately, `tests/tools/test_ep13_embedded_generation_bound.py` is a member
of `CALLER_SUITES` and was never graded (655.1s a run), so `len(callers) == len(spec.suites)` is
false on every row: **the caller answer is "ten of ten survive the seven graded callers, with the
eighth ungraded" — a bound, not a verdict.**

## The predictions, scored

| # | prediction | outcome |
|---|---|---|
| P1 | the JSON reproduces both published prose tables exactly | **CONFIRMED** — every row, asserted rather than eyeballed: the re-reduction recomputes `killed_by` from `per_suite` and asserts equality with the recorded field on all 29 rows |
| P2 | three of eight survive `segment_vocabulary`'s caller population — M3, M4, M8 | **CONFIRMED**, membership exact |
| P3 | that changes the published headline, not a footnote | **CONFIRMED** |
| P4 | all ten of `fuel_mix`'s survive; no row carries a verdict; the eighth caller ungraded | **CONFIRMED** |
| P5 | five distinct caller killers on `segment_vocabulary`; both subjects move the same way; the sweep's conclusion survives | **CONFIRMED**, and the count was exact |

Five for five is not a comfortable result and it is worth saying why rather than claiming
foresight: P1–P5 were arithmetic over tables already published in prose. The pre-registration's
value here was **fixing which files would be read** before reading them, not guessing an unknown.

## What no prediction covered, and it is the finding

The census run to build the control — every suite in every spec, AST-walked for a direct import of
its subject — turned up two things nobody was looking for.

**1. `segment_vocabulary` has a FOURTH direct importer, and it is the repair for M3.**
`tests/sim/test_segment_debt_obligation.py` imports `normalise_segment` and `UnknownSegmentError`
at line 152 — inside a function body. It sat in `CALLER_SUITES`. The spec's own comment says
`grep -rl segment_vocabulary tests/` returns FOUR files and dismisses the extra as
`test_segment_case_guard.py`; **it returns five**, and this is the one nobody counted.

It matters more than a miscount. That test was written **on 2026-09-06, after the battery ran, as
the repair for M3** — its docstring says *"deleting the isinstance check in `normalise_segment`
killed that one file and nothing else, this suite included."* Left in the caller population it
kills M3 on the next run, and the pre-registered question — *does any CALLER prove this* — becomes
unanswerable the moment the repair lands. That is the exact hazard `repair_suite` was built for,
about to fire in a spec that did not have one. It is now declared as a direct suite. **No published
number moves**: it killed nothing in the recorded run, so the caller population going from seven to
six leaves `{M3, M4, M8}` unchanged. That is luck, not a control, which is why it is written down.

**2. The discriminator everyone assumed does not work, and a gate built on it would have fabricated
a defect in `direction`.** "Imports the subject" is *not* "is the subject's own dedicated suite":
all four of `direction`'s caller suites import `background.direction` directly, and each is
legitimately the dedicated suite of a module that calls it. The obvious control — *no member of
`suites` may import the subject* — is unsatisfiable there and would have condemned a correct spec.
The census was run before the control was written, which is the only reason that was found rather
than shipped.

**3. Six controls on the battery's own reachability floor had been dead since the engine was
extracted.** `tests/tools/test_a_green_mutation_cell_is_not_evidence_until_the_poison_round_ran.py`
reaches for `SUBJECT`, `POISON_OLD`, `_poison` and `_score` on `direction_contract_battery`; the
extraction into `tools/contract_battery.py` took all four with it and left the spec holding only
data. All six had been erroring on `AttributeError: module has no attribute 'SUBJECT'` — proved
pre-existing in a clean `git archive HEAD` extract before anything was changed. **This is the class
that file exists to catch, committed against that file**: a control whose subject moved proves
nothing, and it says so in a colour nobody was reading. Repointed and re-proved here.

## The repair

* `BatterySpec.direct_suites` — the subject's own dedicated test files, scored as their own columns
  and never folded into `survived_all`. Same mechanism as `repair_suite`, named separately because
  the reasons differ; what they share is the only thing the reduction cares about — neither is a
  caller.
* `killed_by_own_suites_only` on each row. `killed_by: []` said *"proved by the subject's own
  tests"* and *"proved by nothing"* in one word, and those are different claims.
* The `partial` fail-open, found while writing the control: it read `len(per_suite) <
  len(spec.suites)`, and `per_suite` also carries the direct and repair columns — so a row missing
  a caller cell can hold MORE cells than there are callers and be reported as fully graded. Live on
  `fuel_mix`: eight callers, one never graded, two direct columns, nine cells. Now
  `rows_without_a_caller_verdict`, counted over caller cells.
* `direct_suites` enters the fingerprint. A resumed row keeps the verdict it was written with —
  `run()` skips a mutation whose cells are all present and never re-reduces it — so a spec that
  re-splits its population must not be able to inherit rows scored under the old split.
* `tests/tools/test_the_caller_verdict_excludes_the_subjects_own_suites.py`, six legs. Poison round
  first (import-time raise: all six red), null round (behaviour-preserving comment: all six green),
  then the battery. **All six mutations fire.** Two survived the first pass: one was my mutation
  being an equivalence (`[] or X` is `X`), the other a real gap — dropping `direct_suites` from the
  fingerprint payload survived, because the only pair being compared also differed in `suites`. The
  leg that closes it compares two specs differing in `direct_suites` alone.

## What this does not settle

**Neither results file was rebuilt.** Both fingerprints moved (`segment_vocabulary`
→ `a8df36398b6a`, `grid_intensity_fuel_mix` → `d7eb36a0b901`), correctly — the split changed, and
the fingerprint is what stops a stale verdict being inherited. The corrected verdicts above come
from cells already scored and are not affected. A re-run writes the machine field to match; it is
named as follow-on, not assumed done, and `fuel_mix`'s is ten suites by eleven mutations.

**The eighth caller is still ungraded.** `test_ep13_embedded_generation_bound.py` at 655.1s is
where `fuel_mix`'s remaining doubt lives, and no row can carry a verdict until it is run.

**Whether `direction`'s four columns are callers or the subject's own is not settled here.** Each
imports the subject directly and each is a caller's dedicated suite. The discriminator is whether
the suite NAMES a contract of the subject, which is not statically decidable, and this turn
deliberately did not guess.

## Where this leaves the sweep

| subject | published shape | on the caller population |
|---|---|---|
| `register_low_water` | proved by one caller | unchanged |
| `run_phase3b_recalibration` | proved by one caller | unchanged |
| `ops_repo` | reaches, patches by name, proves nothing | unchanged |
| `company_data` | ten of ten survive three callers | unchanged (repaired at `2d1dd41d5`) |
| `segment_vocabulary` | **refutes the shape — no unproved contract** | **three unproved; 5 caller killers of 6** |
| `fuel_mix` | one suite, 2 of 10 | **zero callers, 0 of 10, no verdict** |

Both moved the same way — **less caller evidence than published, never more** — which is the
direction a mixed population is guaranteed to bias. The sweep's conclusion survives it and is
sharpened: `segment_vocabulary` no longer refutes the one-caller shape outright, and caller count
still fails to predict evidence across all six. The module with the most callers has three
contracts that only its own suite proves.
