**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `find-the-ratchets-in-tests-background-that-are-red-at-head-and-select-nothing`) · **Class:** controls_that_cannot_fail

# PREREGISTRATION — why does a nightly census that names a red every night surface nothing?

Written **before** the measurements below were run. Two observations are already in hand and are
stated as observations, not predictions, so they cannot be counted as successful calls:

* **OBSERVED (not predicted).** `head-green-census.timer` is enabled and has completed a run every
  night. `journalctl` for Sep 4 → Sep 10 (the retention window) shows seven completed runs, and
  **every one of them names both**
  `tests/background/test_live_ledger_guard.py::test_the_narrowing_to_measurement_ledgers_is_measured_not_assumed`
  and `tests/background/test_seat_guard_daemons.py::TestStructuralLock::test_every_main_entrypoint_is_guarded`
  as `NEW RED`. Counts: 25, 21, 29, 28, 25, 35, 43.
* **OBSERVED (not predicted).** `docs/observability/head_red_observed.json` **at HEAD** holds exactly
  one run — `2026-09-02T04:30:02+00:00`, head `ec2e0b1a4`, 830 red of which 760 are `OSError`. That
  is the tmpfs/ENOSPC-wrecked run. All 830 rows carry `currently_red: true` and an identical
  `last_seen`.

These two observations already refute the mechanism claim shared by
`SEAT_FINDING_THE_UNGUARDED_LEDGER_WRITER_RATCHET...2026-09-09` and
`SEAT_FINDING_A_SECOND_WHOLE_BACKGROUND_RATCHET...2026-09-10` — *"nothing anywhere can currently
see it"* / *"nothing ever surfaces it to be triaged"*. Something saw it, by name, seven nights
running. **What follows is therefore a question about the route between the observation and the
seat, not about observation.** The predictions below are about that route.

## The questions, and what I predict before looking

**Q1. Why has `head_red_observed.json` not gained a row since 2026-09-02, given seven completed runs?**

*Prediction (confidence: moderate-high).* The file **is** current in the shared working tree at
`/home/rich/synthetic-enterprise` and is stale only **at HEAD** — written every night by
`_record_observation` and never committed, because no lane's pathspec names it and the census does
not commit its own artefact. If so, then every clean-HEAD extract — including the ones both sibling
findings used — reads the 2026-09-02 poisoned run and nothing else.

*The alternative I am predicting against:* `record()` refuses or raises silently each night. I rate
this lower because the same run demonstrably wrote `HEAD_RED_REGISTER.md` successfully.

**Q2. Do the two sibling findings' claim "it is present in `head_red_observed.json`" hold at
test-id granularity?**

*Prediction (confidence: high — this is close to already checked, and is recorded as a prediction
only because I have not yet done the string comparison exhaustively).* **No, for both.** The
register's `live_ledger_guard` row is `test_write_gap_entry_still_writes_when_given_a_scratch_path`,
and its `seat_guard_daemons` rows are four `TestRefuseIfForeign`/`TestResidentDetection...` tests.
Neither ratchet's own test id is in the file. The claim was true at **file** granularity and was
read as true at **test** granularity.

**Q3. Every night reports these as `NEW RED`, never as "red for N nights". Is age computable at all?**

*Prediction (confidence: high).* No. Age is derived from `head_red_observed.json`, and since that
store has been frozen at 2026-09-02 in every extract the census can reach, a red standing for
fourteen days and one that appeared last night are **indistinguishable in the output**. This, and
not the absence of observation, is why 43 named reds read as wallpaper.

**Q4. Is `docs/staging/reference/HEAD_RED_REGISTER.md` — which the census's own message says is
"DRAWN as work while this is non-zero" — actually drawn?**

*Prediction (confidence: low, genuinely open).* I expect the draw route **exists and fires**, and
that the failure is one of rank rather than absence: the register is drawable but never wins
against the ranked staging queue. I hold this weakly and would not be surprised by a hard break.

**Q5. How many ratchet-shaped assertions are there under `tests/background/`, and how many are red
at HEAD right now?**

*Prediction.* Population **6** (band 4–9) — the prior turn's census found 6 with a stated
over-counting predicate, and I am reusing that predicate unchanged rather than re-deriving one
after seeing an answer. Red at HEAD: **2** (band 2–4) — the two already known. I expect the prior
turn's number to hold and expect to find **no third**.

*What would refute me:* a third red in `tests/background/` that neither sibling finding names.

## The threshold, fixed now

If Q4 shows the register is written but has **no live reader**, the answer to "why did nobody
notice" is a broken route and the fix is a route, not a longer `CONTROL_TESTS`. If Q4 shows the
route fires and the register is simply outranked, the fix is ranking and **the recommendation in
`SEAT_RESULT_THE_STEM_SELECTOR_CANNOT_REACH_TWENTY_SEVEN...` — change the selector — is aimed at
the wrong layer**, because selection was never the binding constraint.

I am recording that second branch in advance because it makes my own prior turn's recommendation
falsifiable, and it is the branch I would otherwise be slowest to see.
