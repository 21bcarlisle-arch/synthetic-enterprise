# EP14 — the largest line source-checks clean, and its unlisted twin in `company/` does not

**Atom:** `EP14_adapter_published_cost_stack` · lane `W4_the_wall` · epoch 3 · level 0 → 3 · `loop_stage: idle`
**Draw:** 2026-08-19 worker tick, LANE 3 (DISCOVER/FRAME only). **No BUILD code written** — the atom is
epoch-3 BUILD-gated (`block_reason`: director-reserved curriculum sequencing, R13);
`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1 permits DISCOVER/FRAME on a parked atom and forbids BUILD.
**Level:** HELD at 0 — the adapter is the deliverable, not the document (EP10 precedent, as passes 2–4).
**Map and note store deliberately NOT edited** — `tests/design/test_simplifications_store.py` couples
`simplifications_count` to the store's note count, so a note append obliges a same-commit map edit, and
`docs/design/maturity_map.yaml` is carrying another lane's STAGED hunk right now. This document is the
record, as it was for passes 3 and 4.

**This is the FIFTH pass.** Pass 4 (`EP14_PUBLISHED_COST_STACK_SOURCE_CHECK_2026-08-17.md` §6) named its
own largest remaining gap in one sentence, and this pass went straight at it:

> "**The network and RO tables were not source-checked.** … this pass checked 3 of 13 tables … the two
> largest lines by money (electricity network £869k, RO £1.72M) are untouched."

The RO table is now checked, on **both** of its inputs, on **all ten** years. Everything below is
`observed-with-evidence` unless labelled otherwise (R9). **MEASURED AT:** HEAD `a275425f1`, live
`docs/reports/run_output_latest.json`, live committed `docs/reports/ANNUAL_REPORT.md`, with
`simulation/policy_costs.py` and `company/regulatory/roc_ledger.py` constants read from the shipped
modules and nothing monkeypatched. Publications fetched this pass are listed at the foot.

---

## 1. The world's RO table is EXACT — twenty of twenty inputs, ten of ten years

`_RO_COST_BY_OY_START` is the biggest single line in the non-commodity stack (£1.72M, ~35.6%) and the
first entry in `_UNVERIFIED_TABLES`. Its declared reason for being unpinnable was precise, and correct:

> "Ofgem publishes the RO buy-out price and obligation level separately; the tabulated £/MWh is a
> DERIVED product of both, so pinning it needs the two inputs pinned, not one figure."

Both inputs pinned. The table's own per-row comments state the pair it used; each was checked against
the publication that sets it:

| OY | model level | published level | model buy-out | published buy-out | table £/MWh | level × buy-out | Δ |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2016/17 | 0.348 | **0.348** | 44.77 | **44.77** | 15.60 | 15.57996 | +0.13% |
| 2017/18 | 0.409 | **0.409** | 45.58 | **45.58** | 18.60 | 18.64222 | −0.23% |
| 2018/19 | 0.468 | **0.468** ¹ | 47.22 | **47.22** | 22.10 | 22.09896 | +0.005% |
| 2019/20 | 0.484 | **0.484** | 48.78 | **48.78** | 23.60 | 23.60952 | −0.04% |
| 2020/21 | 0.471 | **0.471** | 50.05 | **50.05** | 23.60 | 23.57355 | +0.11% |
| 2021/22 | 0.492 | **0.492** ² | 50.80 | **50.80** | 25.00 | 24.99360 | +0.03% |
| 2022/23 | 0.491 | **0.491** ² | 52.88 | **52.88** | 26.00 | 25.96408 | +0.14% |
| 2023/24 | 0.469 | **0.469** | 59.01 | **59.01** | 27.70 | 27.67569 | +0.09% |
| 2024/25 | 0.491 | **0.491** ³ | 64.73 | **64.73** | 31.80 | 31.78243 | +0.06% |
| 2025/26 | 0.493 | **0.493** | 67.06 | **67.06** | 33.06 | 33.06058 | −0.002% |

Every buy-out price is `primary` (Ofgem's RO suppliers page for 2016/17–2023/24; the 2024-25 and
2026-27 buy-out notices for the last two). Eight of ten obligation levels are `primary` from the DESNZ /
BEIS / DECC level-calculation notice for that year; **2021/22 and 2022/23 are `secondary`** — quoted
verbatim inside the 2023-24 and 2024-25 notices respectively, which I did fetch, but their own notices
were not. Stated rather than smoothed over: two of twenty are one hop from primary.

**The residual is rounding and nothing else.** The tabulated £/MWh is the product rounded to 1dp (2dp for
2025), worst case 0.23% on 2017/18, £0.0422/MWh. On the run's own volumes that is worth **under £120
across ten years** — I did not bother to state it to the penny because it is smaller than the rounding on
the numbers it would be compared with, which is the honest reason.

**This is a GREEN result on the largest line in the stack, and it is the first one this atom has had.**
Passes 3 and 4 each found the table they looked at to be wrong (calendar-vs-Apr-Mar keying; £43k of
mis-transcribed CCL). The RO table is right, and it is right on the hard construction — a derived product
of two separately published series, over a decade in which both moved non-monotonically.

¹ **2018/19 has two published levels and the model uses the second.** The statutory six-months-ahead
notice (29 Sept 2017) sets **0.452** ROCs/MWh for GB; the same notice then computes, under a heading
"How the 2018/19 obligation level for Great Britain would be adjusted to account for the EII exemption",
that the revised methodology "would increase the obligation level … from 0.452 ROCs/MWh to 0.468
ROCs/MWh", and the notice's own later arithmetic uses 0.468 ("126,190,667 ROCs in GB ÷ 0.468 ROCs per
MWh"). 0.468 is the level that applied. See §3 — this is the right number for the world and a
point-in-time question for the pricing path.

² Quoted inside the notices for 2023-24 ("the 2021 to 2022 obligation level of 0.492 ROCs per MWh") and
2024-25 ("0.491 ROCs per MWh" for 2022 to 2023) respectively.

³ Also a revision, and a *better-behaved* one: the 27 Sept 2023 notice published **0.487** and stated in
the same breath that if the 100% EII exemption were legislated before 1 April 2024 the level "would
become 0.491". It was; the 26 March 2024 revision confirms 0.491, and the 2026-27 notice records "The
exemption was increased to up to 100% for the 2024 to 2025 obligation year onwards." The conditional was
published on the statutory date, so unlike 2018/19 there was no six months in which the future level was
unknowable.

## 2. THE FINDING — the Annual Report publishes a SECOND RO rate table, ten years of both columns, matching no publication, and it is 26.5% below the RO cost the company actually pays

Looking for the run's RO volumes surfaced `roc_summary` in `run_output_latest.json`, and its constants
are not the ones above. They come from `company/regulatory/roc_ledger.py`, via
`company/regulatory/statutory_obligations.py::_roc_summary`, and they are rendered as a table by
`saas/reporting/annual_report.py::_section_roc_obligations` under the heading **"Renewable Obligation
(RO) Cost Observatory"** — committed at HEAD in `docs/reports/ANNUAL_REPORT.md` lines 2064–2077.

| OY | report level | published | report buy-out | published | report cost | on published constants |
|---|---:|---:|---:|---:|---:|---:|
| 2016 | 0.317 | 0.348 | £43.30 | £44.77 | £925 | £1,050 |
| 2017 | 0.334 | 0.409 | £44.77 | £45.58 | £30,968 | £38,608 |
| 2018 | 0.342 | 0.468 | £46.43 | £47.22 | £48,828 | £67,954 |
| 2019 | 0.351 | 0.484 | £47.22 | £48.78 | £117,296 | £167,085 |
| 2020 | 0.358 | 0.471 | £48.78 | £50.05 | £176,424 | £238,154 |
| 2021 | 0.364 | 0.492 | £50.80 | £50.80 | £184,468 | £249,336 |
| 2022 | 0.370 | 0.491 | £52.88 | £52.88 | £194,408 | £257,984 |
| 2023 | 0.376 | 0.469 | £54.35 | £59.01 | £203,369 | £275,420 |
| 2024 | 0.382 | 0.491 | £56.19 | £64.73 | £214,249 | £317,236 |
| 2025 | 0.389 | 0.493 | £58.10 | £67.06 | £96,296 | £140,861 |
| **total** | | | | | **£1,267,231** | **£1,753,689** |

**Understatement £486,458.88, 27.74%.** Decomposed by substituting one column at a time on the report's
own volumes: obligation levels carry **£390,791 (80.3%)**, buy-out prices **£74,741 (15.4%)**, the
interaction the rest. *(This is a constants-only counterfactual — it holds the report's volume series and
its year-keying fixed and changes only the two constant tables, so the delta is attributable to the
constants alone and does not double-count the keying question in §3.)*

**The shape is the tell, and it is the same shape pass 4 found in the CCL table.** `_ROC_OBLIGATION_LEVEL`
is a smooth monotonic ramp — 0.317, 0.334, 0.342, 0.351, 0.358, 0.364, 0.370, 0.376, 0.382, 0.389, i.e.
+0.006 to +0.007 every single year after the first. The published series is **not monotonic**: it climbs
to a plateau at 0.484/0.471/0.492/0.491, **falls to 0.469** in 2023/24, and comes back to 0.491. A model
that ramps cannot produce a dip. Likewise `_ROC_BUY_OUT_PRICE_GBP`'s last three years — 54.35, 56.19,
58.10 — are each ~+3.4% on the last, while the actual prices went 52.88 → **59.01** (+11.6%, RPI-linked
into the inflation spike) → **64.73** (+9.7%) → **67.06**. The table applies a quiet average escalator
across exactly the years the escalator was not quiet. **Invented smooth physics where the publication has
a plateau, a dip and a spike** — the third instance of that class on this atom.

**Why this is an error and not a permitted company belief.** The regulation-commons doctrine says the
regulatory TEXT is a shared commons readable by every lane, because law is published in reality; a lane's
*reading* may be wrong, the *text* may not be substituted. `roc_ledger.py`'s own docstring asserts these
are the published figures — "Buy-out prices are published annually. Obligation levels are published",
and, naming one, "Buy-out price: set annually by Ofgem (e.g. £54.35/ROC for 2023-24)". The 2023-24
buy-out price is £59.01. **A citation is not an agreement** — pass 4's sentence, and this is the same
defect one module over.

**The corroboration that makes it an error rather than two defensible readings.** The world's own settled
RO line for this run, `ro_levy_gbp` summed over `years`, is **£1,724,548.80**. Recomputing the report's
observatory on the published constants gives **£1,753,688.88 — 1.7% away**, the residue being
calendar-year vs Apr–Mar bucketing. As shipped it is **£1,267,231, 26.5% BELOW** the world's figure.
Change only the constants and the two organs agree; leave them and they disagree by a quarter. That is
the null control this finding needed and it moves the right thing.

**And the caveat inverts.** The rendered section says *"ROC buy-out cost is the maximum supplier
exposure; ROC market purchases reduce actual cost"* and closes *"Buy-out price is the regulatory
ceiling."* The published number sits **26.5% below** the RO cost the same run actually charges the
company. A figure labelled a ceiling that is nowhere near a ceiling is worse than an unlabelled wrong
number, because the label tells the reader which direction the error cannot be in.

Filed as `docs/staging/WORKER_FINDING_THE_REPORTS_RO_OBSERVATORY_PUBLISHES_TEN_YEARS_OF_RATES_THAT_MATCH_NO_PUBLICATION_2026-08-19.md`
(**BLOCKING** — queued, not fixed, per SELF_INTERRUPT discipline; grading argument in the finding).

## 3. Why neither class control could see it: both are scoped to the module that declares them

This is the part worth keeping. Two R10 class controls exist for exactly this defect family, and both are
census-based, and **both census `simulation/policy_costs.py` and only that**:

* `tests/simulation/test_policy_cost_year_basis.py` discovers tables with `vars(policy_costs)` and
  requires each to declare its year convention in `policy_costs.YEAR_KEY_BASIS`.
* `tests/simulation/test_policy_cost_values_vs_source.py` classifies every table **in `YEAR_KEY_BASIS`**
  as verified-with-a-pin or unverified-with-a-reason, and ratchets the unverified count downward.

`_ROC_OBLIGATION_LEVEL` and `_ROC_BUY_OUT_PRICE_GBP` are year-keyed rate tables of precisely the governed
shape, sitting in `company/regulatory/roc_ledger.py`. Neither control can name them, because the
enumeration is `vars()` of one module. So:

* the values control's `_UNVERIFIED_TABLES` says of `_RO_COST_BY_OY_START` "£1.72M, the largest line" —
  **and that one turns out to be right**;
* the table that is wrong by £486k is not in the register at all, and cannot be added by any mutation of
  either control, because it is out of scope by construction rather than by omission.

**A register of unverified constants inherits the blindness of its own enumerator.** The scope leg of the
values control fires when a new table appears *in `policy_costs`* — mutation 4 in its R15 set proves
exactly that and nothing wider. Its docstring's honest closing line ("11 of the 13 year-keyed tables have
never been source-checked") is true and is also narrower than it reads, because *thirteen* is the count
of tables in one module, not the count of year-keyed rate tables the company ships.

Both are also **read on the wrong year boundary**: `_annual_elec_mwh` buckets by
`settlement_date[:4]`, and `_roc_summary` looks both constants up on that same calendar integer, while
the RO obligation year runs 1 April – 31 March. That is the identical defect repaired in
`policy_costs.get_electricity_network_cost_per_mwh` on 2026-08-13 and made a class by
`YEAR_KEY_BASIS` — **the class fix did not travel to `company/`, because the class was defined as
"tables in this module" rather than "year-keyed rate tables".** Not quantified here and deliberately not
folded into the £486k: the keying error and the value error would have to be measured on one basis to be
added, and this pass measured the values.

**Recommendation, acted on by recording it rather than asking** (NEVER_ASK_WITHOUT_RECOMMENDING): when
EP14 opens, the first thing built is not an adapter but the **repo-wide census** — every year-keyed rate
dict under `simulation/`, `company/` and `saas/`, discovered by AST walk, each classified verified or
unverified-with-reason against the commons. That is the enumerator both existing controls should have
had, it is what makes the adapter's output checkable when it lands, and it is the only version of B5
that can fail on a table nobody remembered to declare.

## 4. A negative result, recorded so a later pass does not "repair" the world's RO table upward

The world table's own comment calls itself an "RO effective cost **floor**", and the report's section
says market purchases "reduce actual cost". Both suggest the true supplier cost is *above* obligation ×
buy-out, and a future pass could reasonably try to add the ROC market premium. **`inferred`, not observed:
that would be double-counting.** Ofgem redistributes the buy-out fund to suppliers *pro rata to ROCs
presented*, so a supplier taking the ROC route pays roughly buy-out + recycle per ROC and receives the
recycle back; a supplier taking the buy-out route pays buy-out and receives nothing. The two routes are
arbitraged to the same net cost per obligation-MWh, which is buy-out × obligation level — what the table
already has. Recycle values fetched this pass for scale (2020-21 ≈ £3.87/ROC, 2021-22 £7.04 + £0.40 late
= £7.44, 2022-23 £6.88, 2023-24 £5.81) are the *gross* redistribution, not an uncovered cost.

The reconciliation that supports the mechanism, from the 2020-21 redistribution notice: obligation
119,090,744 ROCs, presented 105,263,447, so 13,827,297 ROCs short × £50.05 = **£692,056,214**, against a
buy-out fund of £415,555,547 plus a late-payment shortfall of £276,500,668.37 = **£692,056,215**. Exact
to £1. What the buy-out route does *not* cover — the failed suppliers' unpaid £276.5M — is the
mutualisation mechanism, and the model books that on a separate table (£157,256.46, pass 3 B7).

**So the world's "floor" is not a floor, it is the number**, and its comment is more modest than its
arithmetic deserves. Recorded because the obvious next move on this table would have made it worse.

## 5. What this pass did NOT do

* **No adapter, parser, schema-drift or cap-annex work.** Nothing in `file_scope` touched. No BUILD.
* **The `roc_ledger` divergence is NOT repaired** — filed and queued (§2). A LANE 3 draw carries no BUILD,
  and the repair is a class question (which *other* year-keyed rate tables live outside the census?), not
  a twenty-value edit. §3 is the class; fixing the instance without it repeats the 2026-08-13 mistake in
  the other direction.
* **The census of §3 was not run.** I named two tables outside the register by finding them; I did not
  sweep `company/` and `saas/` for the rest, so the population of unregistered year-keyed rate tables is
  **unknown and is at least two**. An instance count is not a population.
* **The keying error in `_roc_summary` was not quantified** (§3), deliberately, to keep the £486k
  attributable to the constants alone.
* **The network tables are still unchecked** — pass 4's other named gap (electricity network £869k) is
  untouched here, and `_UNVERIFIED_TABLES` still carries nine other entries.
* **2021/22 and 2022/23 obligation levels are `secondary`**, quoted inside notices for other years (§1).
* **B1 still not run** (blocked on this atom's own unbuilt half). **B6 still not run** (`D2_three_clocks`).
* No level moved, no map edit, no note-store edit, nothing under `company/`, `saas/`, `sim/`,
  `simulation/` or `site/` changed.

---

## Sources fetched this pass

* [Renewables Obligation (RO) — Suppliers, Ofgem](https://www.ofgem.gov.uk/environmental-and-social-schemes/renewables-obligation-ro/suppliers) — buy-out price table, 2016-17 (£44.77) to 2023-24 (£59.01).
* [RO buy-out price, mutualisation threshold and ceilings 2024 to 2025, Ofgem](https://www.ofgem.gov.uk/publications/renewables-obligation-ro-buy-out-price-mutualisation-threshold-and-mutualisation-ceilings-2024-2025) — "£64.73 per Renewables Obligation Certificate (ROC)".
* [RO buy-out price and mutualisation threshold and ceilings 2026 to 2027, Ofgem](https://www.ofgem.gov.uk/data/renewables-obligation-buy-out-price-and-mutualisation-threshold-and-ceilings-2026-2027) — 2026-27 £69.34, and 2025-26 £67.06.
* [The Renewables Obligation for 2016/17 (DECC)](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/464685/Renewables_Obligation_Level_Calculations_for_2016-17.pdf) — "0.348 ROCs per MWh in England, Scotland and Wales".
* [RO setting 2017-18 explanatory note, 1 October 2016 (BEIS)](https://assets.publishing.service.gov.uk/media/5a80b6cf40f0b62305b8cbc4/RO_setting_2017-18_explanatory_note_-_1_October_2016_-_typos_corrected.pdf) — "0.409 ROCs per MWh in England, Wales and Scotland".
* [The Renewables Obligation for 2018/19 (BEIS, Sept 2017)](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/648424/Renewables_Obligation_2018_19_FINAL.pdf) — "0.452 ROCs per MWh in Great Britain", and the EII adjustment "from 0.452 ROCs/MWh to 0.468 ROCs/MWh".
* [Calculating the level of the RO for 2019 to 2020, GOV.UK](https://www.gov.uk/government/publications/renewables-obligation-level-calculations-2019-to-2020/calculating-the-level-of-the-renewables-obligation-for-2019-to-2020) — "0.484 ROCs per MWh in Great Britain".
* [The Renewables Obligation for 2020-21 (BEIS, Sept 2019)](https://assets.publishing.service.gov.uk/media/5d8b47a140f0b6098d33fee6/renewable-obligation-calculating-level-2020-2021.pdf) — "0.471 ROCs per MWh in Great Britain (England, Wales and Scotland)".
* [Calculating the level of the RO for 2023 to 2024, GOV.UK](https://www.gov.uk/government/publications/renewables-obligation-level-calculations-2023-to-2024/calculating-the-level-of-the-renewables-obligation-for-2023-to-2024) — "0.469 ROCs per MWh in Great Britain"; quotes 2021-22 at 0.492.
* [Calculating the level of the RO for 2024 to 2025, GOV.UK (27 Sept 2023)](https://www.gov.uk/government/publications/renewables-obligation-level-calculations-2024-to-2025/calculating-the-level-of-the-renewables-obligation-for-2024-to-2025) — "0.487 ROCs per MWh", conditional "0.491"; quotes 2022-23 at 0.491.
* [Revising the level of the RO for GB for 2024 to 2025 … EII (26 March 2024), GOV.UK](https://www.gov.uk/government/publications/renewables-obligation-level-calculations-2024-to-2025/revising-the-level-of-the-renewables-obligation-for-great-britain-for-2024-to-2025-to-implement-an-increased-exemption-for-energy-intensive-industries) — revised "0.491 ROCs per MWh in Great Britain (England, Wales and Scotland)".
* [Calculating the level of the RO for 2025 to 2026, GOV.UK](https://www.gov.uk/government/publications/renewables-obligation-level-calculations-2025-to-2026/calculating-the-level-of-the-renewables-obligation-for-2025-to-2026) — "0.493 ROCs per MWh in Great Britain (England, Wales and Scotland)".
* [Calculating the level of the RO for 2026 to 2027, GOV.UK](https://www.gov.uk/government/publications/renewables-obligation-level-calculations-2026-to-2027/calculating-the-level-of-the-renewables-obligation-for-2026-to-2027) — 2026-27 "0.472 ROCs per MWh"; "The exemption was increased to up to 100% for the 2024 to 2025 obligation year onwards."
* [RO: ROCs presented and Redistribution of Buy-Out Fund 2020-21, Ofgem](https://www.ofgem.gov.uk/publications/renewables-obligation-rocs-presented-and-redistribution-buy-out-fund-2020-21) — recycle ≈ £3.87/ROC; fund £415,555,547; presented 105,263,447; late-payment shortfall £276,500,668.37.
