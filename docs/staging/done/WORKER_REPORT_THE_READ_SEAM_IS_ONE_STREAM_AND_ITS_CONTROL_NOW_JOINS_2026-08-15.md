# REPORT — the meter seam is one stream again, and the control named for its agreement now measures it

**Severity:** RECORDED · **Lane:** D_billing_metering · **Disposition:** BUILT and landed

**CORRECTION HISTORY — this header has been wrong TWICE, and the second time was the same
defect as the first.**

*First tick.* The header said "BUILT and landed" while the code was in the working tree and
NOT in HEAD. The landing had been REFUSED (correctly) because
`simulation/run_phase4c_on_phase2b.py` also carried another lane's uncommitted consumer call,
and the record — D3 note 8 — had already landed in `fdcbd91f7`, so HEAD described code HEAD
did not have.

*Second tick.* The correction written to fix that said "The repair is landed now, with the
foreign lane's supplier adopted alongside it". **That was also false, and false in exactly the
same way** — it too was written into a working tree whose contents were not in HEAD. Checked
this tick: `git show HEAD:simulation/meter_reads.py | grep -c meter_read_log_from_events`
returned **0**, as did the same check for `check_read_log_matches_billing_basis` and
`read_events_out`. A "committed" claim written in a working tree is self-refuting, and writing
the correction *for* that class in the same self-refuting shape is why this note now states the
command it ran rather than the conclusion it reached.

*Third tick — the state now, verified.* The repair is in HEAD at **`60fc315da`**, gate receipt
consistent against tree `0fdaa45ba`, rc 0, 7 paths. The four symbol checks above now return
non-zero and `generate_meter_read_log` is gone from `run_phase4c_on_phase2b.py` (0 hits). The
landing shape is NOT what the second correction claimed: the foreign lane's supplier was landed
**first and alone**, in its own commit `3b4b5d71b`, because supplier-before-consumer is the only
coherent half of that adoption — `simulation/policy_costs.py` enters the tree as a pure addition
with zero callers, which cannot move a published number. Its `annual_report.py` consumer, its
test and its record remain UNLANDED and its finding stays live in `docs/staging/`.

The rest of this report was accurate about the WORK throughout and wrong only about where the
work was.

**Drawn:** the BLOCKING finding at rung 1c (OPS12 clause 3),
`WORKER_FINDING_THE_MATCHING_BILLS_CONTROL_MEASURES_CARDINALITY_AND_THREE_PUBLISHED_ROWS_DISAGREE_2026-08-15.md`,
which held lane `D_billing_metering` ahead of its disposition queue.
**Atom:** `D3_catchup_rebilling` (level 3 → 3, no level move). Repair record and every
number: `docs/design/simplifications/D3_catchup_rebilling.yaml` entry 8.

## What was wrong

One meter-read decision was computed twice from the same seed — once by
`company/billing/monthly_bill_assembly.py` for the bills customers are charged on, once
by `simulation/meter_reads.py::generate_meter_read_log` for the published read log. The
billing call site alone applies the Ofgem SLC 21B final-read override (D3's own
2026-07-12 Expert-Hour fix), so the premise stated in that file's comment — *"the
identical seed means the two always agree"* — was false from the moment the override
landed. Three rows of the live 1,600-row published log said `estimated` for a
customer-period whose own published bill said `actual`: **3 of the 3 overrides that
fired**, not 3 of 1,600. The one control over the pair asserted `len(log) == len(bills)`
under the name `test_main_produces_meter_read_log_matching_bills`, so every
equal-length disagreement passed it.

## What changed

- **One stream, two readers.** `build_monthly_bills` takes an optional `read_events_out`
  sink and hands back the `MeterReadEvent` each bill was actually assembled from, in
  bills order, appended in the same step that appends the bill.
  `simulation.meter_reads.meter_read_log_from_events` projects those events through a
  single `read_event_to_log_entry` serialiser, and `run_phase4c_on_phase2b.main` no
  longer calls `generate_meter_read_log` at all.
- **`generate_meter_read_log` survives, demoted.** Kept for callers holding bills without
  their events (tests, standalone analysis); its docstring now states that it cannot see
  a billing-side read decision and must not become the publishing path again.
- **Class control (R10).** `company/compliance/population_sanity.py::check_read_log_matches_billing_basis`
  joins the two PUBLISHED streams on `(customer_id, period_end)` and flags every row
  where `billing_basis != status`, whatever the cause. It is wired into
  `run_all_population_checks`, which `background/sanity_daemon.py` already runs each
  cycle against `run_output_latest.json` — a live automated caller, not just a test.
  Both sides keyed with zero shared keys is flagged as *unmeasurable*, never clean.
- **R15, both ways.** `test_read_log_cannot_be_re_derived_without_losing_the_final_read_override`
  pins reads all-estimated so the override is guaranteed to fire, asserts the projected
  log agrees on every row with the control clean, then re-derives the log the old way and
  asserts the control FIRES naming the customer. Two further mutation tests cover the
  equal-length single-row flip and the fail-open guard.

## Downstream — the question the finding left NOT measured

Measured (`observed`, arithmetic on those 3 rows against the same artefact; not a re-run):
the estimated-read rate every consumer derives from `status` moves 469/1600 = **29.31% →
29.12%** (`saas/reporting/css_statement.py`, `tools/generate_world_data.py`'s site
crossing); mean `delay_days` 3.9931 → 3.9762; `tools/generate_billing_ledger.py`'s per-bill
A/E flag and cumulative meter-register advance for those 3 customer-periods now follow the
bill instead of contradicting it. Nothing crosses a sanity band.

## Not claimed

No customer was mis-billed and **no bill amount changes** — the bills were the SLC
21B-correct artefact throughout; it was the published read log that was stale about them.
The published artefacts still carry the old 3 rows until the next real run regenerates
them, which this draw does not do. `EP8_adapter_dcc_duis` is **not** advanced: no adapter,
no DUIS schema, level stays 0 — what this repair gives it is the precondition its own
"transport-only swap" promise needs (a real transport answers a request once and has no
seed to replay for a second call site).

— Worker tick, 2026-08-15.
