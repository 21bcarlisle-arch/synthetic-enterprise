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
   *Partly answered 2026-10-01:* `how_far_a_settled_eac_sits_from_next_years_use.md` publishes
   the spread of consecutive industry annual figures (AA/EAC) per dwelling from NEED. The
   by-meter-type split is still a gap, and the practitioner question is put there.
5. **No published fixed-versus-variable direct-debit split** (carried forward from
   `what_bill_shock_is.md`, still the load-bearing gap there).
6. **No published per-account credit balance before 2022, by fuel or payment method.** The only
   published figure found is Ofgem's all-household average (£244 falling to £200, year to June
   2025). It is a 2025 dual-fuel figure. It gives the order of magnitude, but a single-fuel
   2016-2018 level-DD book cannot be graded against it. (Found 2026-10-10 while splitting the
   single-levy run's DD book, `tools/dd_book_legs.py`.)
7. **No published rule on what an annual review sizes from.** Nothing found says whether a GB
   supplier's review resets to last year's spend, to last year's consumption at current rates, or
   adds recovery of the balance. SLC 27.15's "best and most current information" points to current
   rates; the practice is unpublished. Practitioner question for the director.
   *ANSWERED 2026-10-11T04:20Z (console): "Your DD review question was answerable. Ofgem's August
   2022 decision strengthened SLC 27.15: a fixed DD must be set on the best and most current
   information in all cases, taking account of reads and of customer and third-party information,
   and reassessed when new information would change it materially. Close the practitioner question
   with this." He also set the shape: the DD amount comes from the company's own twelve-month
   forecast for the property, priced at known rates where fixed and forecast rates beyond, plus
   the balance to be cleared. Built as `own_forecast_plus_balance` in
   `company/billing/dd_review.py` -- see §6.

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

---

## 5. 2026-10-11 pass — the 2022 decision's actual reassessment test, SLC 27.16's refund trigger, and what a risk-based PPP may lawfully use SLC 27.15 for

*Knowledge pass for the director's personal-payment-plan design. Read at source: Ofgem's 26 August
2022 decision letter (the same instrument §1 already cites), and the Nov 2025 edition of the
Operational Capability and Financial Responsibility Principles guidance (which quotes SLC 27.15 and
27.16 by title while explaining SLC 4B). Capital/ringfencing material from the same guidance is filed
in `bad_debt_provisioning.md` §10, not repeated here.*

### Rules (ESTABLISHED, cited)

1. **The reassessment test is "material impact on the DD amount", not any numeric variance.**
   Ofgem's own decision letter, para 1.12: *"suppliers should reassess a customer's fixed DD when
   they receive information that is likely to have a material impact on the DD amount. Where any
   reassessment determines that a change to a DD would be immaterial, suppliers should use their
   discretion when deciding whether a change is necessary."* This is the exact test the director
   described from memory, confirmed verbatim at source. [H]
2. **The strengthened duty does NOT require an automatic reset on every new data point.** Para 1.11:
   *"we do not anticipate a supplier needing to reset a DD where a new meter reading reports a
   minimal change in consumption... and the modification we are making will not change this."* The
   duty is to *reassess* against new information, not to re-run the DD formula on every event. [H]
3. **What counts as "best and most current information" is explicitly wider than consumption.**
   Para 1.13: suppliers must "account for a range of relevant data... includ[ing] for example
   accounting for data such as meter readings, and information provided by consumers and third
   parties about their circumstances and preferences." Preferences and circumstances are named
   alongside meter data — the duty is not consumption-only. [H]
4. **SLC 27.16's duty is reactive, not proactive.** The OCFR guidance (footnote 6, §3.34) titles it
   *"Refunding customer credit balances on request."* The licence obligation is triggered by the
   customer asking; nothing in the material read says a supplier must sweep and refund surplus
   credit unprompted. A supplier that refunds proactively is doing MORE than SLC 27.16 requires, not
   something the licence assumes. [H, on the title and framing; the full operative text of 27.16
   itself was not reached this pass — see GAP 1]
5. **The 2022 Market Compliance Review's initial findings, cited by the same decision letter (para
   1.10):** the majority of reviewed suppliers had "no or minor procedural weaknesses," five had
   "moderate or severe weaknesses" and were required to submit remedial action plans. No later
   (2023-2025) compliance review or open letter specifically on DD-setting practice was found this
   pass — see GAP 2. [H for the 2022 finding; GAP for anything after]

### GAPs

1. **The operative text of SLC 27.16 itself was not retrieved this pass** (the consolidated licence
   conditions PDF cited in §Sources of the base file has moved; the replacement URL was not found
   within this pass's budget). Everything here about SLC 27.16 rests on the OCFR guidance's
   paraphrase and footnote title, which is a secondary restatement of the licence text, not the
   text. Re-fetch before this is treated as settled.
2. **No DD-setting compliance review or open letter after August 2022 was found.** If Ofgem has
   revisited DD practice 2023–2025 (the director's brief anticipates this), it was not located this
   pass.
3. **No published rule distinguishes a "catch-up" component of a fixed DD (recovering an existing
   arrears balance) from the consumption-cost component SLC 27.15 is written about.** The decision
   letter's "best and most current information" is framed throughout around *consumption* ("the
   quantity of electricity/gas... supplied") — arrears recovery through an inflated DD is common
   industry practice but was not found stated as something SLC 27.15 itself licenses or limits.
   SLC 27.8 (repayment-plan ability-to-pay; see `company_debt_management.md` §8) is the clause that
   governs arrears recovery terms. Practitioner question: is a credit-risk-driven DD uplift,
   presented to the customer as part of their regular fixed DD rather than as a separate repayment
   plan, something a real supplier does, and under which clause does it sit?

### What this means for a risk-based personal payment plan

- **ALLOWED, on the published text:** reassessing a DD whenever new information — a meter read, a
  change the customer or a third party discloses, or a material shift in the household's
  circumstances or stated preferences — would materially change the right amount, and NOT
  reassessing (or declining to act on an immaterial one) is an explicit discretion, not a breach.
  A personalised plan that re-sizes a DD on new consumption or payment-behaviour evidence sits
  squarely inside this.
- **UNCLEAR, flagged rather than assumed either way:** using a customer's *credit-risk tier itself*
  (as opposed to evidence about their consumption or circumstances) as the stated basis for a higher
  fixed DD. SLC 27.15's own wording is anchored to consumption information; nothing read this pass
  says risk tier is excluded, but nothing read says it is a basis either. A plan that varies the DD
  by risk tier should be able to point to the *consumption or circumstance evidence* behind the
  number, not just the risk score, if it is to be defended as an SLC 27.15 "best and most current
  information" decision.
- **ALLOWED, and distinct:** a prompt, proactive refund of surplus credit for low-risk customers is
  a service choice *above* SLC 27.16's on-request minimum, not a workaround of it. Nothing read
  forbids being more generous than the licence floor.
- **NOT established either way, flagged for the Capitalisation side:** whether running a deliberately
  wider band around zero for low-risk customers (more credit held, by design) interacts with the
  Cash Coverage Trigger and CCB ringfencing regime — this is addressed in `bad_debt_provisioning.md`
  §10, which is the load-bearing finding for "credits and debits net out across the portfolio."

---

## 6. 2026-10-13 pass — building the third review rule, and what is still owed

*Knowledge pass before build (K8), delivery seat. The director's ruling above (§4.7, 2026-10-11)
closed the practitioner question with the published SLC 27.15 duty and set the shape of the third
`REVIEW_RULES` entry. This records what was built, what the published record still does not
establish, and what the build itself approximates rather than wires end to end.*

**ESTABLISHED, cited (repeats §4.7 and §5 for the reader landing here):** the August 2022
strengthening of SLC 27.15 (reassess on best and most current information, material-impact test,
not a numeric trigger) is the whole of the published duty this rule rests on. Nothing published
describes the arithmetic below; it is the director's practitioner statement, cited as that.

**What `own_forecast_plus_balance` does.** The same trailing-12-month billed kWh and days
`consumption_at_rates_in_force` already reads (`company/billing/dd_review.py`), priced at the
account's known rate for the days its current term still covers and the company's own forward
estimate for the days beyond, grossed for VAT, plus the balance the account carries into the
review, recovered over the same twelve months. All three rules agree when prices are flat and the
account carries no balance.

**GAPs, stated rather than filled:**

1. **WIRED 2026-10-13 -- see §7.** *As first written:* **The known/forward rate split is built
   and unit-tested, but not wired to live term data.**
   `reviewed_standing` takes `term_end_iso` and `forward_rate_per_mwh_ex_vat` as optional
   parameters; `simulation/dd_balance_book.py::build_dd_balance_book` and
   `tools/dd_book_legs.py::account_legs` both call it from bills alone and never supply either, so
   in every run today the whole forecast year prices at the known rate -- the same figure
   `consumption_at_rates_in_force` returns. The data to supply them exists (`account_state_log`'s
   `term_end`/`tariff_type`/`unit_rate_gbp_per_mwh`, and the company's own forward engine,
   `company.pricing.tariff_engine.CompanyTariffEngine.get_forward_price`, against the published
   electricity SSP series `sim/cache/elexon_ssp_full.json` any market participant can read), but
   threading it through either composition root is a separate, larger build: `build_dd_balance_book`
   is a bills-only composition root and would need its caller to pass term records alongside bills,
   and a genuine `company_fwd` is a wholesale figure (`renewal_desk.py:187`,
   `cost_floor = company_fwd + locked_policy + locked_network`) -- converting it to a retail rate
   needs the published policy/network schedule in force, not yet threaded here either. Owed to
   whoever draws that wiring; the mechanism itself is real and reachable today only by calling
   `reviewed_standing` directly (`tests/company/billing/
   test_dd_review_own_forecast_plus_balance.py::test_the_known_forward_split_is_reachable_and_moves_the_price`).
2. **The balance leg's sign symmetry is a modelling choice, not a published rule.** A credit
   balance lowers the debit by the same arithmetic a debit balance raises it
   (`_recommended_monthly_forecast_plus_balance` adds `balance_to_clear_gbp` straight through, post-
   VAT). Nothing published says a supplier treats the two cases alike, and §5's GAP 3 (whether a
   credit-risk-driven uplift is SLC 27.15 or SLC 27.8 territory) does not reach this either -- this
   rule is consumption/balance-based throughout, not risk-tier-based, so it sits inside §5's
   ALLOWED category.
3. **The twelve-month clearing period is the same director's practitioner convention already filed
   in §4.1** ("an annualised plan divides estimated annual cost by twelve whatever the start date"),
   extended to the balance rather than a fresh assumption.
4. **The balance recovered is the simple running figure on the bills** (`simple_balance_after_window`:
   what came in at the standing amount, less what was billed, carried forward), not the book's
   charge-recovery-barred figure (`barred_at_charge_recovery`, the existing `seek_balance_at_review`
   toggle). The two are deliberately different questions -- what a review clerk reads off the bills
   to size next year's debit, versus what SLC 21BA lets the supplier actually demand at a recovery
   action -- and nothing published says a review is supposed to net the two.

---

## 7. 2026-10-13 pass — the term end and the forward rate the review can see

*Knowledge before build (K8), delivery seat, for claim
`dd-own-forecast-forward-split-wired-after-the-pile-lands`. Closes §6 GAP 1's wiring; the
conversion it named stays a stated belief, below.*

**What the company holds at a review, and what is now read.** Both are the company's own records,
already in every run's output:

* **The term in force and its end** -- `account_state_log`, one row per term the supplier sold
  (`term_start`, `term_end`; default-tariff terms run one cap period, fixes their length). The
  review reads the term in force on the review date; it splits the forecast year only when that
  term ends inside it.
* **Its own 12-month forward** -- `basis_risk_terms.company_fwd_gbp_per_mwh`, the forward the
  company priced each term from, dated by the term's start (the world's forward on the same row,
  `sim_fwd_gbp_per_mwh`, is never read). Per the forward-axis page
  (`the_published_forward_has_an_as_of_axis_and_no_delivery_axis_2026-10-07.md`) this is a
  12-month strip from its as-of date, an EWMA of spot with a seasonal shape, so its level swings
  with the season it is read in.

**The forward rate, and the belief in it (not a published figure).** The days after the term end
price at the known unit rate moved by the change in the company's forward between the term's start
(when the known rate was set) and the review date. That is a **1:1 pass-through of wholesale into
the retail unit rate, with no losses uplift**. The direction is near-certain: the cap's wholesale
allowance is indexed to forward prices, so a retail rate set from them moves with them. The
coefficient is not established here: the cap applies a losses factor to the wholesale allowance,
and this pass does not transcribe it, so the 1:1 understates the move by that factor -- erring
toward the rule mattering less (F11). **GAP:** the losses factor in force by year from the cap
methodology, and whether a supplier's own default rate passes wholesale through at the cap's
coefficient.

**Measured (single-levy run, 2018-06, one process).** Review lag: `last_year_spend` -£17.8k,
`consumption_at_rates_in_force` -£14.4k, `own_forecast_plus_balance` with the term records withheld
-£14.4k (identical, as built), wired -£9.6k. Book: -£20.6k, -£17.4k, -£12.6k, -£8.4k. The
pre-registered prediction (forward split moves the lag by under £1.5k) **missed** by a factor of
three: `docs/staging/records/SEAT_PREREGISTRATION_THE_DD_REVIEW_PRICED_AT_THE_TERM_END_AND_THE_COMPANYS_FORWARD_2026-10-13.md`.

**What the forward knows, graded per review.** Against the consumption-weighted rate actually billed
over the days beyond the term end, the forward beats the known rate in rising years and loses in
falling ones (mean absolute % error, known vs forward): electricity 2017 0.109/0.098, 2018
0.098/0.082, 2019 0.072/0.090, 2020 0.077/0.101, 2021 0.209/0.129, 2022 0.377/0.301; gas 2018
0.055/0.092, 2019 0.093/0.154. So the lag it closes at 2018-06 is partly a rising market, and a
book read in 2019-2020 would be priced worse than the known rate. Whether a better-shaped forward
(the cap's own reference quarters) keeps the rising-year gain without the falling-year loss is the
next question; it waits on the basket the forward-axis page names.


---

## 8. 2026-10-16 pass — does the annual review recover a debit balance, and over what period?

*Knowledge before build (K8), for claim `the-dd-review-asks-for-the-balance-it-is-owed` and
`docs/staging/SEAT_FINDING_D48_A_THIRD_OF_DD_ACCOUNTS_ASKED_FOR_THEIR_BALANCE_LOSE_PART_OF_IT_BECAUSE_THE_REVIEW_NEVER_ASKS_2026-10-14.md`.*

**Answer: yes, commonly, over the next twelve months.** Ofgem, *Direct Debit Market Compliance
Review: Progress Update* (2 February 2023), explaining why direct debits rose in 2022:

> "where a consumer account is in a debit position, suppliers commonly add this amount on to the
> Direct Debit amount and smooth the cost over the next 12 months."

The same update records the other side: Ofgem secured commitments that "surplus customer credit
balances are either returned to consumers or factored into a lower Direct Debit amount". [H]

**Why it matters for the bar.** Energy UK, *Energy UK explains — back billing* (February 2025),
lists among the cases where a supplier may not bill energy more than 12 months old: "The customer's
Direct Debit amount was previously set too low to cover any charges due." So a shortfall the review
never asks for ages into the bar, and one the review recovers within the year does not. [H]

**What this is and is not.** It is Ofgem describing common practice, not a licence obligation.
SLC 27.15 requires the debit to rest on the best and most current information (§5). It does not
require the balance to be recovered, and it sets no period. "Commonly" means some suppliers do not.

**GAPs:**

1. **Practice before 2022.** The sentence describes what Ofgem found in its 2022 review. Nothing
   found says whether 2016-2021 practice was the same. The run applies it to the whole window.
2. **The period for large balances.** "The next 12 months" is the common case. Nothing published
   says whether a supplier lengthens it when the step-up is large (2023's median in the run is £55
   a month), or moves the balance to a separate SLC 27.8 repayment plan instead.
3. **A credit balance.** Ofgem names two treatments, refund or a lower debit. This build recovers
   only debits; a credit is handled as before. Where the other fuel of the same household is in
   debit, SLC 27.8D (from 22 Jan 2021) gives the customer a right to offset the two. Whether the
   review itself nets them is not published: see
   `how_a_gb_domestic_book_splits_by_fuel_and_how_a_two_fuel_home_switches.md` §8b.

**Built.** `company/billing/dd_review.py::REVIEW_SEEKS_BALANCE` (True from 2026-10-20. On the
19 Oct published book, seeking cut barred-plus-open-exposure from £82.6k to £29.2k. The barred
share rose from 34.7% to 39.2% because 204 more accounts are asked. Under
`own_forecast_plus_balance`, which already adds the balance, the review does not also seek it.), `BALANCE_RECOVERY_MONTHS = 12` from the sentence above, and
`review_balance_step_up`, reached by `simulation/dd_balance_book.py` through
`company/interfaces/dd_review_outcome.py`. The book's `seek_balance_at_review` now defaults to the
company's switch.

**Sources:** [Ofgem, Direct Debit Market Compliance Review: Progress Update, 2 Feb 2023](https://www.ofgem.gov.uk/decision/direct-debit-market-compliance-review-progress-update) ·
[Energy UK explains back billing, Feb 2025](https://www.energy-uk.org.uk/wp-content/uploads/2025/02/Energy-UK-explains-back-billing-February-2025.pdf)
