**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the renewal arm prices no gas) · **Class:** no_caller_and_never_runs

# FINDING — writer 3's own log is dropped at the reporting reduction, so its published section cannot ever render

Found while looking for the instrument to measure the writer-3 id fix, not by looking for it.

`simulation/run_phase2b.py:3452` emits `profitability_uplift_log` — writer 3's own record of
every renewal it repriced for unprofitability. `saas/reporting/annual_report.py:3335`
(`_section_profitability_uplift`) reads `data.get("profitability_uplift_log", [])` and returns
`""` when it is empty. Between the two sits `extract_report_data`, which never copies the key:

```
$ python3 -c "import json; d=json.load(open('docs/reports/run_output_latest.json')); \
              print('profitability_uplift_log' in d, 'margin_feedback_log' in d)"
False True
```

WRITER 2'S LOG IS CARRIED AND WRITER 3'S IS NOT. The two writers sit four lines apart in
`company/pricing/renewal_rate_chain.py`, answer a near-identical question, and one of them can
be read on the published report while the other cannot be read anywhere. Every saved payload
this repo has ever produced through `tools/run_annual_report --save-json` has an empty log and
a silently omitted section — the section has never rendered, and its emptiness is
indistinguishable from "the policy did not fire".

## Why it did not show

`_section_profitability_uplift` returns the empty string rather than raising or printing a
"nothing fired" line, so a dropped key and a quiet policy produce byte-identical reports. And
writer 3 has in fact been firing 0 times, so nobody chasing a missing section would have
found a contradiction to pull on.

## What it cost, concretely

The Lane 0 item drawn today defines DONE as "the `profitability_uplift` entry count measured
against the electricity-only level". That count is not in the artefact the run saves. The
measurement was rerouted through `rate_decomposition_log`, which IS carried and holds one
`components` entry per writer that moved the rate (`cause == "profitability_uplift"`). On the
run committed at `docs/reports/run_output_latest.json` (2026-09-07T12:04, pre-fix):

```
decomposed renewals : 1878  {electricity: 1516, gas: 362}
writer 3 firings    : 0     {}
every cause present : {margin_surcharge: 127, portfolio_premium: 1847, price_cap: 106}
```

## What is next, and it is NOT just the one line

Carrying the key through `extract_report_data` is the obvious repair and it is not sufficient
on its own. The section that would then render must say something when the log is empty,
because "writer 3 fired on nothing" and "writer 3 was not asked" are the two facts this whole
class keeps confusing — the same shape as `compute_profitability_uplift` returning `0.0` both
for a profitable account and for a book it cannot see. A control that asserts the key survives
the reduction is worth having; a control keyed to today's zero is not.

Not fixed here: it is a different file and a different lane from the writer-3 id repair landed
in `28ba48dd4`, and widening that landing would have made the id fix unattributable.

---

**Discharged:** 2026-09-07, by
`tests/saas/reporting/test_a_log_the_run_makes_and_a_section_reads_survives_the_reduction.py::test_no_log_the_run_makes_and_a_section_reads_is_dropped_by_extract_report_data`,
`tests/saas/reporting/test_a_log_the_run_makes_and_a_section_reads_survives_the_reduction.py::test_writer_3s_section_tells_a_missing_log_from_a_log_that_is_empty`,
`tests/saas/reporting/test_a_log_the_run_makes_and_a_section_reads_survives_the_reduction.py::test_the_census_selects_enough_logs_to_be_capable_of_finding_one_dropped`.

**And the finding understated itself.** It named one dropped log; the control was written as a
census and named THREE — `profitability_uplift_log`, `triad_log`, `volume_tolerance_log`. Two
whole sections (I&C volume tolerance, Phase 27c; TNUoS Triad exposure, Phase 27d) had never
rendered either, by the same mechanism, with nobody looking for them. Both halves the finding
asked for are in: the key is carried, and the section now distinguishes "fired on nothing" from
"the record was dropped" instead of returning `""` for both. Written up in
`SEAT_RESULT_THE_REDUCTION_DROPPED_THREE_LOGS_NOT_ONE_AND_THE_CENSUS_FOUND_THE_TWO_NOBODY_WAS_CHASING_2026-09-07.md`.
