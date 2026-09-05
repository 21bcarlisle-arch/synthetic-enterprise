**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# RESULT: the collection gap is closed, and the feed that fell through it had no caller either

**Measured 2026-09-05, delivery seat, isolated worktree, base `f4df63cd9`. Claim id
`register-low-water-evidence-convergence-sweep`. Closes
`SEAT_PREREG_CLOSING_THE_COLLECTION_GAP_THE_FORTY_TWO_TESTS_FELL_THROUGH_2026-09-05.md` and
discharges the uncontested half of
`SEAT_FINDING_FORTY_TWO_TESTS_LIVE_WHERE_NO_RUNNER_LOOKS_AND_ONE_OF_THEM_HAS_BEEN_RED_FOR_SEVEN_WEEKS_2026-09-05.md`
(severity BLOCKING), which named the repair and deliberately did not apply it.**

---

## What landed

1. The four real suites moved `tools/` → `tests/tools/`, with the repo-root arithmetic corrected
   from `parent.parent` to `parent.parent.parent` in the three that are location-dependent. **42
   tests are now collected by `pytest tests/` for the first time since they were written.**
2. `tools/generate_regulatory_data.py` wired into `background/process_run_complete.py`'s regen
   cycle, after `gen_company` because it reads `site/data/company.json`.
3. `site/data/regulatory.json` regenerated.
4. `tests/architecture/test_a_test_file_lives_where_a_runner_looks.py` — the control that makes
   this species unable to recur silently.

## The predictions, against the answers

**P1 — CONFIRMED exactly.** From `tests/tools/`, with the path correction and nothing else:
`41 passed, 1 failed`, the failure being `test_live_cache_matches_regeneration` and no other. No
second location dependency existed.

**P3 — CONFIRMED exactly.** The new control, run against a clean `git archive HEAD` extract of the
pre-move tree, examines 8 candidate files and names 4:

    tools/test_generate_company_data.py
    tools/test_generate_decisions_data.py
    tools/test_generate_market_data.py
    tools/test_generate_regulatory_data.py

It does **not** name `tools/test_execution_metric.py`, nor `company/risk/stress_test.py`,
`collateral_death_test.py` or `liquidity_stress_test.py`. All four match pytest's default
filename patterns and none defines a test. A name-keyed control would have called all four
defects and been switched off within the week.

**P4 — CONFIRMED.** No other `site/data/*.json` changed. The publish commit half needed no work:
`process_run_complete` already commits `site/data/*.json` by glob, so only the generator call was
missing.

**P2 — the badge half held; the field list was incomplete, and one field I did not predict is the
most interesting one.** Predicted: `module_count`, the RAG/obligation figures, the stamp, and *no
per-scheme badge flips*. Eight fields moved:

| field | was | now |
|---|---|---|
| `module_count` | 63 | 67 |
| `overall_rag` | AMBER | GREEN |
| `status_counts.GREEN` / `.AMBER` | 19 / 4 | 23 / — |
| **`domestic_customer_count`** | **8** | **162** |
| `generated_at` | 2026-07-18T19:30:45Z | 2026-09-05T17:13:45Z |
| two scheme `basis` strings | "portfolio has 8 domestic customers…" | "…162…" |

`obligation_count` did not move, so `company.json`'s compliance block has not changed shape — the
chain risk the pre-registration flagged as its least-confident point did not materialise. **No
`status` flipped**, as predicted: 162 is still four orders of magnitude below the 150,000
large-supplier threshold, so WHD and ECO remain EXEMPT for the same reason at the new count.

The unpredicted field is worth its own line. **The committed feed said this supplier had 8
domestic customers.** That is not a compliance figure drifting; it is a seven-week-old snapshot of
a book that has since grown twentyfold, sitting in a file whose whole purpose is to stop the
Regulatory tab's claims drifting from the real build state.

## The thing found on the way, which is the same shape one level down

**The generator's own documented invocation does not work.** Its docstring said
`Usage: python3 tools/generate_regulatory_data.py`. Run that way:

    ModuleNotFoundError: No module named 'company'

— because as a script the repo root is not on `sys.path`, and `derive_regulatory()` imports
`company.regulatory.compliance_scorecard`. It only runs as `python3 -m tools.generate_regulatory_data`
from the root, which is how it is now called.

**Every test of this module is blind to that by construction**, because each test inserts the repo
root on `sys.path` itself before importing the generator — which is exactly the reason those tests
had to be written that way (`tools/` has no `__init__.py`). So the single invocation a human would
have copied was the single invocation nobody had. The docstring now says the working form and says
why the old one was wrong, rather than being silently corrected.

This compounds with the missing caller rather than duplicating it: there was no automated caller,
**and** the documented manual fallback raised on its first line.

## What is still open, and belongs to someone else

The finding named three routes for the drifted feed and this took route 2 (give the generator a
caller), on the evidence that it was four lines in a pattern `process_run_complete` already applies
to five sibling generators with the reason written beside each one — not the "larger change" the
finding estimated without opening the call site. That is recorded as a correction to the finding's
own sizing, not to its analysis.

**Route 3 remains live and is not mine.** Nothing under `site/` reads `regulatory.json` — no HTML,
no JavaScript, no runtime fetch. The feed is now fresh, committed, controlled and regenerated every
publish cycle, and **still has no reader.** Wiring the generator fixed a feed that decays; it did
not establish that anything wants it. That is Door 3's call, as the finding said, and closing the
collection gap has made the question sharper rather than answering it: the tab this generator names
in its own docstring either fetches this file or should stop claiming to.

## What this does NOT establish

**Nothing about whether those 42 tests are good controls.** None has been mutation-tested. 41 of
them now have a pass record exactly two runs long. That they are collected means a runner looks at
them, not that any of them can fail.

**Nothing about the drawn sweep question.** `tools/generate_company_data.py`'s shared contracts —
`segment_revenue_mix`, reached from two generators, and `generate`, from the publisher — still
stand on whatever those 16 tests happen to cover, and that has not been examined. The screen's
remaining queue is unchanged apart from this module's row, which will now read 3 callers and 4
direct importers rather than 4 callers and 0.

**The instrument's limit is now closed from the other side.** The finding warned that
`converged_contract_screen.py` cannot tell "a test file misplaced in a production root" from "a
module that never had a suite" — a sixth file under `tools/` tomorrow would look like the latter.
The screen still cannot tell them apart and is not the place to fix it: the new architecture
control catches the misplaced file directly, at commit time, before the screen ever has to
disambiguate it.

## Controls

`tests/architecture/test_a_test_file_lives_where_a_runner_looks.py`, 8 legs. Seven build their own
tree in `tmp_path` and never read this repository, so no lane's landing can make them pass or fail.

* **The partition leg runs first and asserts all four kinds exist at once** — a misplaced suite, a
  production module matching `test_*.py`, a correctly-placed suite, and a production module
  matching `*_test.py` — before any leg asserts what the detector does with one of them. A
  detector that reports nothing passes every negative leg individually.
* Keyed to **location**: the identical bytes moved under a collected root stop being a finding.
* Keyed to **defining a test** (AST, not substring): the pattern-matching production module is
  clean until a `def test_*` is added to it, then it is not.
* `class Test*` counts; a production class merely *containing* `Test` does not.
* **Fail-closed**: no derivable root, or a root that would swallow the tree, **refuses**. An
  unparseable candidate refuses naming the file rather than being skipped.
* The collected roots are **derived from the runners** — `head_green_census.pytest_argv()` and
  `site_lane_gate.SITE_PREFIX` — not typed here, and a leg asserts the derivation still finds both
  lanes, so a moved runner reds instead of silently narrowing the live leg's subject.
* The live leg carries a **population guard**: an empty finding list is only meaningful if the walk
  examined something, and this tree genuinely contains four uncollected pattern-matching production
  modules for it to examine.

No simulation output, gap value or financial figure passes through the new control; it parses
Python and reads directory names. The regenerated feed carries figures, and every one of them is
derived by a generator that was already tested — what changed is that the derivation now runs.
