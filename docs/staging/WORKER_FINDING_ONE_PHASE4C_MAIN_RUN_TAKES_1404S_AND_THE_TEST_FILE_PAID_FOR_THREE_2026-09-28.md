**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

# FINDING — one `run_phase4c_on_phase2b.main()` takes 1404 s, and the test file paid for three

Found by Lane 0 `run-phase2b-runtime-regression-unblocks-the-council-tax-listing-feed`, 2026-09-28.

**Measured (shared tree, 16 cores, two other CPU-bound jobs running, unprofiled):** `pytest
tests/simulation/test_run_phase4c_on_phase2b.py` with a module-scoped `main_result` fixture
reports 48 passed in **1412 s**, and **1404 s** of that is the fixture's single `main()`. Before
this change, three tests each called `main()` themselves. That is about **4200 s** for one file,
which is past `surgical_land.GATE_TIMEOUT_SECONDS = 3600` on its own, before the other 46 files the
gate selects for `simulation/run_phase4c_on_phase2b.py`. **That explains why no change to that
module could land. The fixture removes it (3 runs → 1).**

**What is NOT explained: the per-run cost.** `PUBLISH_GATE_HEAVY_IGNORES` catalogues these files at
150–480 s each. One `main()` now takes 1404 s, about 3–9× that. No earlier timing of `main()` is on
record, so there is no known-good commit to bisect from yet. Two `cProfile`d runs (origin/main and
the shared tree) did not finish inside 3000 s, so profiler overhead is well over 2× here and a
profile is not the right instrument. The next step is a sampling profiler, or a timed
`run_phase2b.main()` alone against `run_phase4c_on_phase2b.main()`, to split the 1404 s between
the world run and the company's billing pass. Bisect after that.

**Correction to the item's WHY.** It said this regression was "the likeliest cause of the nightly
census's four timeouts". That is refuted by construction: `tools/head_green_census.HEAVY_IGNORES`
`--ignore`s this file, so the census never runs it. The census timeout needs its own measurement
(`SEAT_FINDING_THE_NIGHTLY_HEAD_GREEN_CENSUS_HAS_TIMED_OUT_FOUR_NIGHTS_RUNNING_AND_SYSTEMD_RECORDS_SUCCESS_2026-09-27.md`).
