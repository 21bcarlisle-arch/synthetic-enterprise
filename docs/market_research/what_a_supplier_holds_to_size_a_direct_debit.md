# What a supplier holds to size a direct debit — and what the published record does not establish

*Knowledge pass, delivery seat, 2026-09-02, atom `D_opening_dd_seasonal_sizing`. Written BEFORE any
estimator was built, on the director's correction of 2026-09-01 that there is no such thing as a
half-month direct debit.*

**Why this page exists.** `docs/institutional/knowledge_map.md` and `docs/domain_artefact_library/`
returned nothing for the direct-debit review duty or for annual consumption estimation. The DD path
in this repository had no estimated annual consumption anywhere in it. Before writing a number, this
is what the published record actually says.

---

## 1. The duty, and the citation this repo had wrong

**The obligation is SLC 27.15**, in both the electricity and gas supply standard licence conditions:

> "Save where a clear and express Principal Term of the relevant Domestic Supply Contract provides
> otherwise, the licensee must take all reasonable steps to ensure that the fixed amount of the
> regular direct debit payment is based on the **best and most current information available (or
> which reasonably ought to be available) to the licensee**."

Ofgem **strengthened** this wording with effect from **21 October 2022**, following the *Credit
Balances — Strengthening existing Direct Debit rules* statutory consultation: the amendment removed
the supplier's ability to derogate via contract terms and tightened "all reasonable steps" toward a
"must ensure" obligation. Ofgem's compliance engagement on direct debits runs against
**SLC 0.3, 4A.1 and 27.13–27.16**.

### The finding: "SLC 27B" does not exist, and the ±5% is not in the licence

This repository cites **"Ofgem SLC 27B"** in two places —
`company/billing/dd_review.py` (`_VARIANCE_THRESHOLD_PCT = 5.0`, "Variance beyond ±5% triggers a DD
adjustment under Ofgem SLC 27B") and `docs/market_research/what_bill_shock_is.md` ("The regulated
trigger for a review is a variance beyond ±5% (SLC 27B)").

Neither half survives the record:

1. **There is no SLC 27B.** The direct-debit provisions are numbered **27.13–27.16** within SLC 27.
   The lettered conditions that do exist alongside SLC 27 are **27A** (prepayment) and **28A/28AD**
   (price cap benchmark consumption).
2. **No ±5% variance threshold appears in the licence.** SLC 27.15 states an information-quality
   duty and names no numeric trigger. The only published numeric cut is Ofgem's **100%** threshold
   from the 2022 Direct Debit Market Compliance Review — the increase level at which suppliers were
   *required to re-review* — which is an enforcement instrument, not a licence threshold.

**Status of the ±5%: an industry convention, not a regulated trigger.** It is not fabricated — it is
a widely used supplier review band — but it is **not sourced to SLC 27.15 and must stop claiming to
be.** Filed as `FINDING_THE_DD_REVIEW_THRESHOLD_CITES_A_LICENCE_CONDITION_THAT_DOES_NOT_EXIST`.

---

## 2. What a real supplier actually holds, in precedence order

This is the "best and most current information" of SLC 27.15, ordered from best to worst:

| rank | source | what it is | when it exists |
|---|---|---|---|
| 1 | **Metered history** | The supplier's own actual meter reads over a completed period | Only after the account has been read; not at registration |
| 2 | **Registry EAC / AQ** | Electricity: **EAC (Estimated Annual Consumption)**, held by the Non-Half-Hourly Data Collector and communicated on the **D0019** data flow, derived from the latest **D0010** meter reading. Gas: **AQ (Annual Quantity)**, calculated annually via Xoserve/UK Link. | **Handed to the gaining supplier on registration.** This is the normal case at day one. |
| 3 | **Customer declaration** | What the customer said at sign-up | When the customer was asked and answered |
| 4 | **Ofgem TDCV** | The published typical value for the commodity and band | Always — the explicit published fallback |

On the EAC specifically: it is *initially provided by the supplier and thereafter forecast by the
Data Collector from actual readings*; each fresh D0010 read triggers a new D0019, so the EAC tracks
consumption changes with a lag. **It is an estimate with error, not the household's true annual
usage** — which is exactly why the epistemic wall permits it and forbids the truth.

### TDCV is the published fallback, in Ofgem's own words

> "The TDCVs are also used by suppliers and price comparison websites **in the absence of individual
> consumers' data**."
> — Ofgem, *Decision on revised Typical Domestic Consumption Values*, 25 May 2023, §1.1

Methodology (§1.2): the low/medium/high values are the **lower quartile, median and upper quartile**
of household consumption over the two most recent years of data, averaged. So "medium" is a
**median**, not a mean — and the low/high are quartiles, meaning **half of all households fall
outside the low–high band**. Any bound built on TDCV inherits that.

---

## 3. The TDCV series in force across the 2016–2025 run window

All figures below are from Ofgem's own decision letters, read directly. **The value in force depends
on the date** — a company running 2016–2025 that uses today's TDCV is using a number that did not
exist yet.

| in force from | Gas L / M / H | Elec PC1 L / M / H | Elec PC2 L / M / H | source |
|---|---|---|---|---|
| (before 1 Oct 2017) | 8,000 / 12,500 / 18,000 | 2,000 / 3,100 / 4,600 | 2,500 / 4,300 / 7,200 | "Current" column of the 2017 decision |
| **1 Oct 2017** | 8,000 / 12,000 / 17,000 | 1,900 / 3,100 / 4,600 | 2,500 / 4,200 / 7,100 | Ofgem TDCV decision letter, 3 Aug 2017 |
| **1 Apr 2020** | 8,000 / 12,000 / 17,000 | 1,800 / 2,900 / 4,300 | 2,400 / 4,200 / 7,100 | Ofgem TDCV decision letter, 6 Jan 2020 |
| **1 Oct 2023** | 7,500 / 11,500 / 17,000 | 1,800 / 2,700 / 4,100 | 2,200 / 3,900 / 6,700 | Ofgem decision, 25 May 2023, §2.4, §2.41 |
| **1 Jul 2026** | 6,000 / 9,500 / 14,000 | 1,600 / 2,500 / 3,800 | *not established* | Ofgem decision, 27 May 2026 |

Notes carried from the primary sources:

* **2021: no change.** Ofgem *postponed* the update to assess the COVID-19 impact on consumption
  (2023 decision §1.3). There is no 2021 or 2022 revision.
* **2023 used 2019+2021 data, deliberately excluding 2020** because of the pandemic (§2.4–2.5).
* **"Material" means ≥100 kWh electricity / ≥500 kWh gas** when rounded; below that Ofgem does not
  update (2020 decision, footnote 2).
* **PC2 values are known to be biased low.** Ofgem's own note: multi-meter properties could not be
  aggregated, so "the estimated Electricity Profile Class 2 TDCVs are bound to be below their actual
  value." A PC2 fallback carries that bias and must say so.

### A note, not a finding: the repo's TDCV constants are the 2026 values

`company/compliance/domain_invariants.py::TDCV_{ELEC,GAS}_{LOW,MEDIUM,HIGH}` and its duplicate in
`simulation/population_draw.py::TDCV_BANDS_KWH` carry the **1 July 2026** bands, sourced correctly to
the 2026 review — I checked, and that citation is sound. They are used to *draw the synthetic
population*, which is a world-building decision inside the baseline/curriculum split and therefore
not mine to change for a company-side reason. It is recorded here only so the next reader knows the
two uses are different: **drawing a population is not estimating a customer's consumption**, and the
estimator below keys TDCV to the date in force rather than reusing the draw's bands.

---

## 4. What the published record does NOT establish

These are gaps, stated rather than filled. Each is a place where the code must carry an honest
`None` or a named modelling choice, never a number that looks established.

1. **The arithmetic converting an annual estimate into a monthly amount is not published.** No SLC,
   decision letter or Ofgem guidance found states a formula. `/12` is the **director's practitioner
   statement** (2026-09-01): *"an annualised plan divides estimated annual cost by twelve whatever
   the start date."* It is cited as that — the third side of knowledge — and not as regulation.
2. **No published smoothing, buffer or seasonal-weighting convention.** Real suppliers commonly add
   a buffer or weight the first winter; nothing in the published record establishes a figure, so
   none is applied. A buffer invented here would be load-bearing within a week.
3. **No ±5% (or any) statutory review variance threshold** — see §1.
4. **The accuracy of the registry EAC at registration is not published.** How far a D0019 EAC
   typically sits from the household's realised annual consumption — the error that *causes* the
   drift the director described — has no published distribution found. This is the single most
   load-bearing gap for measuring whether a better estimate reduces harm.
5. **No published fixed-versus-variable direct-debit split** (carried forward from
   `what_bill_shock_is.md`, still the load-bearing gap there).

---

## Sources

- [Ofgem, *Electricity Supply Standard Consolidated Licence Conditions*](https://www.ofgem.gov.uk/sites/default/files/2025-08/Electricity-Supply-Standard-Consolidated-Licence-Conditions.pdf) — SLC 27.13–27.16
- [Ofgem, *Credit Balances — Strengthening existing Direct Debit rules*, decision letter](https://www.ofgem.gov.uk/sites/default/files/2022-08/Decision%20letter%20DD%20rules.pdf) — SLC 27.15 amendment, in force 21 Oct 2022
- [Ofgem, *Statutory Consultation: Strengthening fixed direct debit rules*](https://www.ofgem.gov.uk/consultation/statutory-consultation-strengthening-fixed-direct-debit-rules)
- [Ofgem, *Direct Debit Market Compliance Review: Progress Update*](https://www.ofgem.gov.uk/decision/direct-debit-market-compliance-review-progress-update) — the 100% re-review threshold
- [Ofgem, *Decision on revised TDCVs and Economy 7 consumption split*, 25 May 2023](https://www.ofgem.gov.uk/sites/default/files/2023-05/TDCV%202023%20Decision%20Letter.pdf)
- [Ofgem, *TDCV decision letter*, 6 Jan 2020](https://www.ofgem.gov.uk/sites/default/files/docs/2020/01/tdcvs_2020_decision_letter_0.pdf)
- [Ofgem, *TDCV decision letter*, 3 Aug 2017](https://www.ofgem.gov.uk/system/files/docs/2017/08/tdcvs_2017_decision.pdf)
- [Ofgem, *Decision on postponing the TDCV update*, 27 May 2021](https://www.ofgem.gov.uk/sites/default/files/docs/2021/05/tdcv_decision_letter_2021_0.pdf)
- [Ofgem, *Review of typical domestic consumption values* (2026 decision)](https://www.ofgem.gov.uk/consultation/review-typical-domestic-consumption-values)
