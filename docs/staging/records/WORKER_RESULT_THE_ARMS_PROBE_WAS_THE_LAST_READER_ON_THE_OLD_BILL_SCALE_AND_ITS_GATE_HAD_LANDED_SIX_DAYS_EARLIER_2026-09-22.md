# The arms probe was the last reader on the old bill scale, and the gate that fixes it landed six days before its only caller

**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

**Lane 0 item:** `resolve-the-live-couple-value-based-pricing-revert-now-the-publisher-refuses-it`
**Landed:** `7e749735c` (verified against its own receipt: tree `900f6b49a`, gate-rc 0)
**Date:** 2026-09-22

---

## What the item asked, and what was actually there

The item named two paths. One was spent and one was mis-described by its own headline.

- `tools/isolate_hunks.py` — **already landed**, byte-identical to HEAD. Nothing was owed.
- `tools/couple_value_based_pricing.py` — the draw's classifier graded it `holder work` because it
  supplies two names HEAD lacks. **The clock says otherwise and the clock was the load-bearing
  fact**: working-copy mtime `2026-09-09 16:43`, last commit to that path `2026-09-16 14:02`
  (`c4809c5fc`). The copy predated the landing by a week, so landing it whole would have reverted
  the run-output resolver — 104 insertions against 478 deletions, almost all of it revert.

Both readings were true at once, which is why neither door on its own applied: `refresh_to_head`
would have discarded a correction that has never been in any commit of this file, and
`surgical_land` on the working copy would have reverted `c4809c5fc`.

## What the correction actually was

`belief_versus_truth` never passed `annual_bill_gbp`, so `churn_position_multiplier` fell back to
its `CALIBRATION_ANNUAL_BILL_GBP` default and **every row scored the world's response for a
GBP 1,700 household wearing this household's price differential.** `simulation/` stopped working
that way on 2026-08-27; `edded3973` then moved the segment gate `bill_scale_for` into the curve's
own module on **2026-09-16 09:58** — and this, its only caller in `tools/`, never landed. The probe
has been the last reader on the superseded scale for two weeks.

## Numbers at real inputs, printed before the formula shipped

Offered 280, current 250, 3 years, 3,100 kWh:

```
 bill    seg   believes    world  world@mkt  scale_used  own?   err_pp  err_pp@mkt
  600   resi     0.1660   0.0912     0.1622         600  True      7.5         0.4
 1200   resi     0.1660   0.1269     0.1622        1200  True      3.9         0.4
 1700   resi     0.1660   0.1622     0.1622        1700  True      0.4         0.4
 2600   resi     0.1660   0.2186     0.1622        2600  True     -5.3         0.4
 4000   resi     0.1660   0.3964     0.1622        4000  True    -23.0         0.4
 4000    SME     0.1660   0.1622     0.1622        1700 False      0.4         0.4
```

**The belief error inverts across the book** — the company over-estimates churn for small
households and under-estimates it by 23pp for a GBP 4,000 one. That is not noise with respect to
what this probe is read for: the arm selects on household size, so the bias pointed straight at the
population under study. At GBP 1,700 both paths agree exactly, which is the control that they are
the same curve. SME keeps the market average, which is `bill_scale_for` refusing to run a domestic
curve past its evidence.

**The first draft of this table was inert** — every row read `own? False`. The probe had used
segment `"domestic"`; `_DOMESTIC_SEGMENTS` is `{"resi"}` and the book holds 242 `resi` legs and 2
`SME`. The probe was wrong, not the code, and printing the table at real inputs is the only thing
that would have caught it. Had it shipped unprinted, the correction would have been dead code
wearing a repair's commit message.

The pre-repair figure is **published beside** the repaired one rather than replacing it
(`world_would_p_leave_market_average_scale`, `belief_error_pp_market_average_scale`), because
`docs/observability/value_based_pricing_arms.json` has already been quoted on the old scale and a
reader otherwise cannot tell how much of a move is the repair. `bill_scale_used_gbp` and
`bill_scale_is_this_household` say on every row which of the two measurements it is.

## How it was landed

Grafted the correction onto HEAD's bytes in an out-of-tree scratch copy (nine exact-match
assertions, no fuzzy patching), then `surgical_land --content`. `resolve_run_output`,
`PRODUCING_COMMIT`, `--run-output` and `--adopt-latest` are all present and untouched. The landing
lost one race to a concurrent provenance commit and re-gated on the new base by itself.

`--content` lands bytes **without touching the shared worktree**, so the on-disk revert survived its
own fix and was then stale against a newer HEAD. Second door: once the unique content was at HEAD
the copy supplied no name HEAD lacked, so `refresh_to_head --write` was then legitimate and cleared
it (preserved at `refs/preserved/refresh-to-head/cvbp-bill-scale`). **The path is now out of the
stale-copy census.** `tests/background/test_the_publish_path_refuses_a_stale_producer.py` is green,
so the publisher will regenerate from this producer again.

## Two things established that were not asked for

**The four reds on this module are genuine HEAD reds, not stale-copy artefacts.** Measured rather
than assumed: the module was injected from out-of-tree copies so HEAD's bytes and the grafted bytes
could each be run against the same suite. Both give 44 passed / identical failures — the change is
test-equivalent to HEAD. The four failing tests are byte-identical between the working copy and
HEAD, so they belong to the 41 owed and were never this item's to fix.

**The first injection silently did nothing** and I nearly read its output as a baseline:
`sitecustomize` ran before the repo root was importable, `import tools` raised, and the whole swap
was skipped — printing a plausible "HEAD baseline" that was really the shared tree's revert read
twice. A fail-open that wears a measurement's colour. It was caught only by asserting the injected
module's `__file__` and the presence of a marker symbol. **An injection harness must prove it
swapped before its numbers are read.**

## Finding, not fixed here

`tests/tools/test_couple_value_based_pricing.py` is `predates_landing` on the shared tree — a
2026-09-03 snapshot. It is a **genuine two-lane file**, not a clean revert: it carries 6 tests HEAD
lacks (co-calibration/posterior subject — `test_the_company_leg_reads_the_POSTERIOR_and_the_prior_
cannot_stand_in_for_it` and siblings) while reverting the 16 resolver tests `c4809c5fc` landed.
Neither `refresh_to_head` nor a whole-file landing is correct for it; it needs
`isolate_hunks --survey` + `--keep`. Not this item's path, so not taken here.

## Correction in the record

While reaping what I took to be my own killed gate child, I killed PID 132156 — whose parent was
`background/process_run_complete.py` (PID 42494), a **daemon running its own gate**, not my
landing. My own child had already died with its parent. The daemon survived (it has explicit
killed-runner handling) and its staging file is intact, so the cost is one spurious gate result on
that cycle, which it retries. The lesson is narrower than "check the PID": *a PID I obtained by
grepping for my own subject was not mine* — the gate run that lints a module matches a search for
that module, and the only safe test is the parent chain, which I read one command too late.
