# WORKER FINDING (QUEUED) — the sentence Hour #31 corrected is on no published surface, and the control built to keep it honest has no caller and never runs: it also passes on a WIDENED band, which is the one move its own error message names

**Severity:** BLOCKING · **Lane:** H_harness · **Disposition:** QUEUED (not fixed on sight)

**STATUS UPDATE, 2026-08-15 fourth tick — TWO OF THE THREE ARE REPAIRED AND LANDED; THE
FINDING STAYS BLOCKING.** No discharge field is written here, deliberately: a discharge claim
reads this whole document down to RECORDED, and BLOCKING 1 is still true of the live door as
of this tick. What is now false is BLOCKING 2 and BLOCKING 3, both landed at `0a9c969f5`
(pushed to origin, `python3 -m tools.surgical_land --verify 0a9c969f5` → tree `13fae02d6`,
gate rc 0), with `tests/tools/test_couple_w2_11_d5.py` at **489 passed** on the working tree
that produced it.

* **BLOCKING 2 — done.** The interior-band comparison in
  `tools/couple_w2_11_d5.py` is equality, not containment; it names the WIDER direction in its
  own violation string, and an OMITTED declaration is a violation rather than a clean sheet.
  Six new mutation cases, including the widening case this document said no case covered.
* **BLOCKING 3 — done, and as the class fix R10 requires rather than the wiring fix.**
  `measure_check_call_census` reads `main()` off the AST and `check_check_call_census` puts
  every `check_*` this module defines on trial for reachability from the run that publishes.
  This document's own 5-of-15 measurement was the census's first population; all five are now
  dispositioned by name — three wired onto the default path with printed verdicts, two
  declared in `CHECKS_BEHIND_A_FLAG` with the flag that guards them and the reason. The census
  is itself on the default path, because a reachability census with no caller would have been
  instance four. R15 both ways: an empty subject and a missing `main()` each fail closed, and
  a stale or false exemption fires whichever side moved.
* **BLOCKING 1 — NOT discharged, and not attempted this tick, with a reason.** Re-verified
  live rather than assumed: `https://poesys.net/data/proof.json` → HTTP 200, 747,008 bytes,
  `generated_at` **2026-08-14T06:04:08Z**, the uncorrected clause still served
  (`NECESSARY, NOT SUFFICIENT` scores 0). Its supplier is not this lane's to land: at this
  tree `site/data/proof.json` sits inside a **198-file staged index** belonging to
  `background/process_run_complete.py`, which was live and mid-gate during this tick (pid
  801440, full suite running). Committing that one path out of another writer's publish batch
  is the entanglement this repo has now paid for twice; the publish is in flight and owns its
  own discharge. **The finding therefore stays live and correctly drawing at rung 1c**, and
  the next tick should take BLOCKING 1 alone exactly as the closing section says.

**Found by:** the 2026-08-15 worker tick, THIRTY-SECOND HOUR on `H27_payment_belief_gap`
(level 2, `level_target` 3, `loop_stage: harden`, `file_scope` = `tools/couple_w2_11_d5.py` +
`tests/tools/test_couple_w2_11_d5.py`). Run as a fresh read-only instance with no memory of the
build, which is what this atom's own record asked for. Measured at HEAD `f4144b4f0`.
Everything below is `observed-with-evidence` unless labelled `inferred` (R9).

**This Hour is the one the atom itself specified, and it does not move the level.** The 2026-08-14
Hour (#31) found a false CLAIM shipping on every surface the detection figure feeds, corrected it,
and then deliberately refused its own 2→3, reasoning that "an Hour cannot be its own confirmation".
It wrote down the honest promotion condition verbatim: *"an Hour that ends with no BLOCKING finding
against the corrected instrument"*. This Hour ends with three. **`level_current` stays 2.** The two
D28 residuals that record explicitly ruled non-blocking (the `S`-side predictor, unidentified; the
reshape, unbuilt) are NOT among them — every finding below is something else.

## What survived the Hour, so the next one need not re-do it

The instrument's **numbers are sound**. Re-derived independently from `build_scenario` /
`dense_drift_grid` / `score_triad` without calling the measurement under test: interior pairs
86/86/86; counted change points **38/34/32**; excluded **62/63/61**; silent-set moves **34/40/37**;
the move-iff-it-touches-`S ∪ N` predicate **258/258, zero disagreements**; excluded band 212/209/213
of 900. Every headline the 2026-08-14 record asserts reproduces exactly. The correction is in HEAD
(commit `2a9ea1c76`, gate receipt rc 0), the suite is **471 passed**, the caveat's numbers really are
interpolated (forcing the register to `(5,5)` moves the rendered sentence to "steps at 5"), and R12
holds — the diff touches no scorer arithmetic. **R13 premise confirmed:** the truth-side sets are
invariant across the drift on all three seeds.

## BLOCKING 1 — the corrected sentence never reached a reader; the live door still serves the claim this Hour's predecessor corrected

`observed-with-evidence`, by live fetch (R11's actual requirement — the deployed surface, not the
file on origin):

- `https://poesys.net/data/proof.json` → HTTP 200, 747,008 bytes, `generated_at`
  **2026-08-14T06:04:08Z**. At `coupled_gaps.pairs[5].components.drift_resolution_caveat` a reader
  today meets the uncorrected clause verbatim: *"…so a company's terms error moves it only where
  that error carries an invoice across the grace line."* That is the exact sentence #31 corrected.
- On the live payload, the corrected phrases score **zero**: `NECESSARY, NOT SUFFICIENT` = 0,
  `DO NOT RUN THAT BACKWARDS` = 0, `DENOMINATORS, NOT THE BOOK` = 0.
- The corrected string exists **only in the git index and the working tree**:
  `git show :site/data/proof.json | grep -c "RESOLUTION IS WHICH CASES"` = 1;
  `git show HEAD:site/data/proof.json` = 0. Staged, uncommitted, unpublished.
- The test cited as "R11's shape on a sentence" (`tests/tools/test_couple_w2_11_d5.py:4210`) asserts
  against `pair.measure(...)["detection"].components[...]` — an in-process object. That is not a
  published surface, so it cannot fail on this.
- `docs/design/simplifications/H27_payment_belief_gap.yaml` states the residuals are "now published
  in the sentence a reader meets". The fetch refutes it.

This is the project's own staged-half shape — the consumer landed and the supplier did not — and this
atom's record logged that same shape as a defect one day earlier.

**Discharge:** regenerate and COMMIT `site/data/proof.json` and the ledger it derives from, publish,
then re-fetch the live URL and quote the served `drift_resolution_caveat` containing
`NECESSARY, NOT SUFFICIENT`. Code on origin is not the evidence; the fetched value is.

## BLOCKING 2 — R15 FAIL-OPEN: the control passes on a WIDENED declaration, and its own error message names that exact move

`observed-with-evidence`, read off the shipped source and executed:

`tools/couple_w2_11_d5.py:8777` —

```python
if not (tuple(declared)[0] <= got[0] and got[1] <= tuple(declared)[1]):
```

That is **containment**, while the docstring says the control "requires that the DECLARATION match
the BOOK". Declaring all three bands `(0, 86)` returns `[]` — no violation — and the caveat then
publishes the widened band as its own cause: *"the flagged set steps at **0-86** on the EXCLUDED
band … and at **only 0-86** on the two populations this figure counts."* The entire rhetorical
contrast the sentence exists to draw ("61-63 … and at *only* 32-38") is destroyed, and the control
is silent. The violation string it cannot emit ends **"never widen the band to fit"**.

All four band mutation cases narrow or shift (`42`, `(60,70)`, `(1,2)`, `(0,1)`). **None widens.**
"R15 both ways" is proven in one direction only — the direction that cannot hide a defect.

`observed-with-evidence`, a second fail-open on the same loop: `declared = e.get(field)` followed by
`if declared is None: continue`. A register entry that simply omits a band is not a violation. The
missing-value shape is R15 killer pattern 2 verbatim.

**Discharge:** make the band comparison a tightness test (equality, or containment in the other
direction), and add a WIDENING case plus an OMITTED-band case to
`test_a_declared_interior_band_that_stopped_describing_the_book_fires`. Both must be red on today's
code before they count.

## BLOCKING 3 — the control that "puts the declaration on trial every run" has no caller on any run that publishes the sentence

`observed-with-evidence`, re-verified this tick independently of the Hour:

- Repo-wide grep for `check_detection_interior_change_points` / `measure_detection_interior_change_points`
  outside `tests/`: **two hits, both comments** (`tools/couple_w2_11_d5.py:4120` and `:8864`). Zero
  production callers.
- AST census of the module: **15 `check_*` functions defined, 10 called in `main()`.**
  `check_detection_interior_change_points` is among the 5 that are not. Its three resolution
  siblings — `check_dimension_drift_resolution`, `check_own_drift_resolution`,
  `check_ageing_resolution` — are all called, and they print their verdicts *before* the
  `if args.write_ledger:` branch that publishes the caveat. **The run that publishes the sentence
  runs every sibling resolution check and not this one.**
- Two shipped comments assert the opposite. `:4120` says the bands are "re-derived every run by
  `check_detection_interior_change_points`"; `:8864` says the entry is put "on trial every run by"
  it. Both are false as shipped.
- The decay path is concrete, not hypothetical: `tools/pre_commit_test_gate.py` selects tests by
  NAME STEM, so this module's tests run only when `tools/couple_w2_11_d5.py` itself changes. The
  bands are properties of a book built from `simulation/payment_behaviour_source.py` and
  `company/billing/payment_observation_consumer.py` — a change there moves the bands and fires
  nothing at all.

**R10, and this is why it is BLOCKING rather than a third instance.** This atom's own record for
Hour #30 says, in as many words, that a no-caller control on this instrument was already "the
SECOND … a rate, not an incident", and recorded the class closed because "the grader has a caller on
every publish". This is the **third**, shipped one Hour after that closure. R10 forbids closing an
absurdity-class defect with an instance fix: the class was closed at the instance and the next
instance shipped immediately. The discharge below is therefore two-part.

**Discharge:** (a) call both functions in `main()` beside `check_dimension_drift_resolution`, print
the verdict, and add a wiring test; (b) **the class fix R10 actually requires** — an automated census
asserting that every `check_*` in this module is reachable from `main()`, so instance four cannot
ship. The 5-of-15 gap this Hour measured is that census's first population, and the other four
uncalled checks (`check_door_row_surfaces`, `check_published_figure_caveat_coverage`,
`check_published_resolution_floor`, `check_scenario_constant_census`) must be dispositioned by it
rather than left unnamed.

## LATENT 4 — one of the "two corrected sentences" is typed, not interpolated

`observed-with-evidence`: `DIMENSION_DRIFT_RESOLUTION["detection"]["why"]` hard-types `"61-63"`,
`"86"`, `"32-38"`, `"34-40"` as literal prose (lines 4159/4163/4164), sitting directly beside the
band fields it could interpolate from. Nothing compares them; the guard test only asserts a
substring is present. Both the H27 record and D28 note 4 claim "the two sentences corrected and now
interpolated from the register rather than typed" — only the caveat is.

LATENT rather than BLOCKING because `why` reaches no reader: its distinctive phrase scores zero in
the live payload and nowhere under `docs/observability/` or `site/data/`. A stale `why` misleads a
maintainer, not a customer. It is nonetheless the exact decay shape this correction exists to close,
reintroduced in the same commit that closed it.

## LATENT 5 — "258/258" is half an identity, and the code already says so

`inferred` (arithmetic, not measured): where the flagged step lies wholly inside the excluded band,
`D∩S` and `D∩N` are unchanged by construction, so neither rate can move. That half of the predicate
is arithmetic, not evidence; only the cancellation direction is informative. **No action** — the
docstring states this and disclaims independence. Recorded only so a later Hour does not read
258/258 as stronger than it is.

## RECORDED 6 — "63 distinct distances" does not reproduce

`observed-with-evidence`: the H27 record and the test-file header both say "212 of 900 invoices sit
past the grace line at 63 distinct distances". Seed 7, n=300: 900 records, **212 past grace ✓**, but
distinct `days_late` among them = **73**; distinct `days_late − grace` = **73**; restricted to the
readable interior = **70**; to `[-6, 82]` = **71**. None is 63. **63 is the seed-11 excluded
change-point count**, so this reads as two quantities conflated in the prose. Narrative only,
unpublished, no figure moves.

## RECORDED 7 — a bare test run re-publishes into the supplier of a public door

`observed-with-evidence`: `python3 -m pytest tests/tools/test_couple_w2_11_d5.py -q` rewrote
`docs/observability/coupled_gap_ledger.json` (md5 `e50a5bf26…` → `10405d458…`). A test run silently
re-publishes a gap measurement into the supplier of a public door. Hour #30 recorded this as a lead;
it is still open, and it lives in `tests/tools/test_couple_w2_11_d5.py` — this atom's own file_scope.

**Not restored, deliberately, and disclosed rather than quietly left.** By the time the Hour
reported, the file had been rewritten AGAIN by a concurrent lane: it now reads md5 `ac003306d…`,
which matches neither the Hour's pre-run snapshot (`e50a5bf26…`), nor its post-run value
(`10405d458…`), nor HEAD (`29195a5e0…`). Restoring the snapshot would have clobbered another lane's
live write on the shared tree, which is the worse defect. The pre-Hour snapshot is preserved at
`/tmp/ledger_before_expert_hour.json` for whoever owns the isolation fix; the file should not be
swept into a commit as-is by anyone.

## Why BLOCKING, and what it holds

LATENT is "real defect; does not invalidate anything published **or any control's verdict**". Both
exclusion clauses fail here: BLOCKING 1 invalidates something **published** (the live door serves a
claim the repo believes it corrected), and BLOCKINGs 2 and 3 invalidate a **control's verdict** (a
band check that cannot see a widening, and does not run at all on the publishing path). Lane
`H_harness` level-raises are refused until this is discharged — including `H27_payment_belief_gap`'s
own 2→3, which is exactly the move this Hour was run to decide, and exactly the move that would
otherwise certify an instrument whose stated cause never reached a reader.

Down-classifying any of the three to let the promotion through would be the anti-pattern
`background/finding_severity.py` names in its own header. The atom's record wrote the promotion
condition before the Hour ran, precisely so the Hour could not negotiate it afterwards.

## For the tick that takes this

Take BLOCKING 1 first and alone: it is a regenerate-commit-publish-refetch with no design in it, it
is the only one a reader is currently harmed by, and it discharges against a live fetch rather than
a test. BLOCKING 2 is a one-line comparison plus two mutation cases. BLOCKING 3 is the one with real
work in it, because R10 makes it a class fix and not a wiring fix — do not close it by adding the
missing call alone; that is precisely what Hour #30 did, and this Hour is the receipt for why that
does not hold.
