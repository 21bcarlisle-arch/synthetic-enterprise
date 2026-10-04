**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing` — Lane 0 delivery

# The DD opening-arms instrument now reads the openings the run used, and an older substrate refuses

Claim `make-the-dd-opening-arms-instrument-measure-the-live-rule-again`. The draw's duplicate-work
note named this same id as "held". No rival process was running it (checked with `ps`), so the
note was the draw's own write. I did the work rather than releasing the claim.

**Defect.** `tools/dd_opening_arms.estimate_opening_by_customer` called
`_opening_dd_by_customer(customers)` without settlement records. Since `ed41ffa1e` the DD books open
each account at the rate it was sold at, so the instrument has been measuring the cap fallback while
labelling it "the live rule".

**Repair.**
- `simulation/run_phase4c_on_phase2b.py` now returns `opening_dd_by_customer`, the exact mapping
  both DD books were fed.
- `saas/reporting/annual_report.extract_report_data` passes that key through to the persisted run
  output.
- The instrument reads the key. A substrate that lacks it gets a `SystemExit` naming the key. It
  does not re-derive the rate from first bills, because that would be the second implementation its
  docstring forbids.
- The published "refused" statement used to assert that every refusal was caused by the pre-2019 cap
  gap. Under the rate-sold rule that is no longer necessarily true, so the statement is now built
  from the two cause counts.

**What the published page says now.** `site/data/dd_opening_arms.json` was last written on
2026-09-03, from a substrate that predates the rate-sold rule. When that page was produced the cap
rule *was* the live rule, so the page is still honest about its own substrate. It cannot be
refreshed until a run output produced after this landing exists. The current
`docs/reports/run_output_latest.json` (09-09) lacks the key and will refuse, which is intended.

**Controls (both mutation-proven).**
- One test checks that the arm equals the handed-over mapping and that a run output without the key
  refuses.
- One test checks that the key survives `extract_report_data`. Renaming the key in that whitelist
  turns it red.

**Gap left open.** No control covers the simulation side returning the key. The run takes roughly
100 minutes, so no test executes `main()`. If the key is dropped there, the next re-run refuses with
a message naming the key. That is a loud failure, not a silent one.
