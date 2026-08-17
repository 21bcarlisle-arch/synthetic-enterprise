# REPORT — the electricity CCL table now equals the statute, and a citation is no longer accepted as agreement

**Severity:** BLOCKING (discharged) · **Lane:** W4_the_wall · **Atom:** `EP14_adapter_published_cost_stack`
**Draw:** 2026-08-17 worker tick, RUNG 1c (OPS12 clause 3) — the BLOCKING finding held the lane.
**Discharges:** `docs/staging/done/WORKER_FINDING_THE_ELECTRICITY_LEVY_TABLE_DIVERGES_FROM_THE_STATUTE_ITS_GAS_TWIN_MATCHES_2026-08-17.md`
**Level:** NOT moved. EP14 stays at 0 — the adapter is the deliverable, not this repair.

Everything below is `observed-with-evidence` unless labelled `inferred` (R9). **MEASURED AT:** working
tree on HEAD `07fcdee3c`, `docs/reports/run_output_latest.json` (the same artefact the finding measured),
`simulation/policy_costs.py` functions called directly, nothing monkeypatched.

---

## 1. What was wrong, and what it is now

`_CCL_ELECTRICITY_RATE_BY_YEAR` cited "HMRC Climate Change Levy rates tables" and diverged from them on
9 of 11 years, always understating. Its gas twin — the same statutory rows, the same Acts, the same
sections — was exact on 10 of 10. The table also had the wrong SHAPE: a gentle monotonic climb
(5.44 → 7.35) where the statute has a spike and a taper, with the module's own comment naming the
step-change in the wrong year **and with the wrong sign**.

| OY | was | now | £/kWh in the statute | source (fetched this tick) |
|---|---:|---:|---:|---|
| 2016 | 5.44 | 5.59 | 0.00559 | **recalled — still not fetched** |
| 2017 | 5.54 | 5.68 | 0.00568 | FA2016 s.145 |
| 2018 | 5.83 | 5.83 | 0.00583 | FA2016 s.146 *(already correct)* |
| 2019 | 6.11 | **8.47** | 0.00847 | FA2016 s.147 — the step UP |
| 2020 | 7.17 | **8.11** | 0.00811 | FA2020 s.92 — a **cut**, not a rise |
| 2021 | 7.17 | 7.75 | 0.00775 | FA2020 s.93 |
| 2022 | 7.17 | 7.75 | 0.00775 | bracketed by two primary 0.00775 years |
| 2023 | 7.26 | 7.75 | 0.00775 | gov.uk CCL rates |
| 2024 | 7.35 | 7.75 | 0.00775 | gov.uk CCL rates |

**Eight of the eleven years are now pinned to a URL I fetched myself this tick**, against six in the
finding: FA2016 s.145 and FA2020 s.93 were located during this pass, which promotes 2017 and 2021 from
recalled to primary. The gas table was re-verified against the same fetches and needed **no change** —
7 of its 9 years are now primary-confirmed rather than asserted.

**Also fixed: two more Acts were checked and are NOT CCL rate sections** — FA2014 s.94 (aggregates levy)
and FA2016 s.144 (abolition of the renewables exemption). Recorded so the next pass does not re-fetch
them looking for the 1 April 2016 rates.

## 2. Exposure — measured, not carried over

Replicating the finding's own method exactly (business electricity only, resi excluded as CCL-exempt,
each bill's kWh apportioned evenly across its period days, bucketed Apr–Mar), **the old table reproduces
the finding's £459,799.16 to the penny**, which is what licenses the comparison:

| | |
|---|---:|
| model electricity CCL line, old table | £459,799.16 |
| model electricity CCL line, repaired | **£509,007.63** |
| correction | **£49,208.47 (10.7%)** |
| of which on primary/bracketed years only | **£49,128.46** |

The finding's defensible floor was £43,074.89, because 2017 and 2021 were unfetched then. Having fetched
both, **the sourced correction is now £49,128.46** — only £80.00 of the total rests on recall (OY 2015
and 2016). OY 2019 alone is £18,274.68, 37% of it, exactly as the finding predicted.

**THE PUBLISHED FIGURE HAS NOT MOVED YET, and this report does not claim it has (R11).** The repair is to
the GENERATOR. `docs/reports/run_output_latest.json` and the front-door Reconciliation Bridge still carry
the £459,799.16 line and the £4.84M stack built on it; they will move at the next full run, which is the
auto-process lane's, not this tick's. Anyone quoting the stack before then is quoting the old table.
*(inferred:* the net margin effect is smaller than £49k and partly self-cancelling, because the stack is
passed through in the tariff at pricing time and deducted at settlement — the finding said the same, and
neither of us has measured it.*)*

## 3. The class closure (R10) — and why a citation census could never have caught this

The class is **"a constant cites a publication and does not EQUAL it"**. A nine-value edit does not close
it, so:

**New: the regulation commons carries the published rates.**
`docs/domain_artefact_library/regulatory/ccl_main_rates.json`, in the shape the Ofgem cap-windows
artefact established — 22 pinned rates, in **the statute's own £/kWh**, one legislation URL per row, and a
per-row `provenance` of `primary` / `bracketed` / `recalled`.

**New: the values-vs-source control.** `tests/simulation/test_policy_cost_values_vs_source.py`, five legs
plus six mutation tests, 13 tests, all green.

**Why the unit redundancy is deliberate and must not be tidied.** The commons never carries the model's
£/MWh figure; the control performs the ×1000 conversion. Had the commons held £/MWh, the checked value
would have been derived from the source it checks — **the R15 tautology shape, which is exactly how this
defect survived**. The prior documentary control (scope brief B5, *"every constant traces to a published
artefact"*) scored 12/13 and **passed this table**, because B5 as run asked *does a comment NAME a
publication* while B5 as meant asks *is the constant the published number*. A census of citations is
fail-open on a mis-transcription by construction: it reads the same comment the author wrote, so the only
defect available to it is a MISSING citation, never a FALSE one.

**R15, proven both ways** — six mutation tests, each red on its own named defect:
restore 2019 = 6.11 → equality leg fires · move a *commons* pin off the statute → same leg fires, so
neither side is privileged · add an unpinned table year → coverage leg fires · add an unclassified table
to `YEAR_KEY_BASIS` → scope leg fires · empty the register → loader raises (the fail-silent guard, since
an empty register would make the equality leg vacuously green) · delete the register → raises.

**The control caught two of my own defects while I wrote it**: two `_UNVERIFIED_TABLES` reasons were too
thin to audit ("as above, gas."). I lengthened the reasons rather than lowering the threshold.

## 4. Five value tests were pinning the defect

`tests/simulation/test_phase27b_ccl.py` asserted the wrong numbers, and one test —
`test_ccl_april_2020_step_change` — **asserted a RISE in April 2020 that the statute records as a cut**.
This is worth naming: a value test that pins whatever the table happens to say converts a transcription
error into specified behaviour and then defends it. Re-pinned to the commons, and the two direction tests
were kept as direction tests (`oy_2019 > oy_2018`, `oy_2020 < oy_2019`, plus 2019 as the series peak)
because **the defect was directional and only a direction assertion can fail on a wrong shape**. The
behavioural assertions there — resi exemption, SME == I&C, obligation-year basis, settlement plumbing —
were correct and are unchanged.

The obligation-year probe got sharper as a side effect: OY 2019 (8.47) and OY 2020 (8.11) now differ *in
the opposite direction* to the old monotonic climb, so mis-keying that date fails loudly rather than by
1.06 in the direction a reader would expect.

## 5. What is NOT closed — stated so the green is not read as wider than it is

* **11 of 13 year-keyed tables have no values-vs-source pin at all**, including the two largest lines by
  money: electricity network (£869k) and RO (£1.72M). They are declared in `_UNVERIFIED_TABLES` with a
  reason each and held by a ratchet at 11 that may only fall. Visible and shrinking ≠ closed.
* **Three pins are `recalled`** (elec 2016, gas 2016, gas 2022), excluded from every equality assertion
  and ratcheted at 3. Gas 2022 cannot be bracketed — its neighbours differ (0.00465 → 0.00672).
* **The stronger closure was not built.** Having the model LOAD these rates from the commons would make
  drift *impossible* rather than merely *detected*. That is EP14's own adapter work, where an ingest
  adapter makes it nearly free, and it is the right home for it — the finding said so and I agree.
* 2025 and 2026 rates are pinned `primary` in the commons but sit past the tables' last key (2024), so
  the control does not require them. They are a sourced input already waiting for whoever draws
  `WORKER_FINDING_THE_COST_STACK_CLAMPS_SILENTLY_INSIDE_ITS_OWN_RUN_WINDOW_2026-08-14`. The clamp
  currently returns 7.75 for 2025, which happens to be the correct published rate.
* **No level was moved**, no map or note-store edit was made, and the two `run_*.py` files dirty in the
  shared tree are another lane's and were not touched.

## 6. The pattern worth keeping

The finding observed that this item had been deferred three passes running for a *stated environmental
reason* — no network — and that "an item deferred three times for an unavailable input is not the same as
an item deferred three times on merit." This tick is the second half of that observation: **the register
still does not distinguish them, and the repair took one tick once the input existed.** Two of the four
Acts I needed were found by guessing section numbers around a known one. If the deferral register carried
"blocked on: network" as a field, a tick with network could draw those items first.
