# Is there a bill level at which GB households start switching? — the record says no, and it says the level runs the other way

**Knowledge:** how-households-choose

*That page is where this lands because the question is a CHOOSING question and the answer is about
what a household's decision does NOT depend on: its own bill's size. The finding's negative half —
Ofgem/BMG's −0.07 to +0.05 spend-to-switching correlation — belongs beside that page's account of
why most households don't switch, and its positive half (the same survey's "pounds, not percent")
is already the evidence behind the world's own `churn_position_multiplier`. It is deliberately not
filed under the price-cap or bill-shock pages: the subject is propensity, not price.*

**Research completed 2026-09-22, delivery seat.** Subject:
`company/crm/churn_model.BILL_STRESS_THRESHOLD_GBP = 3000.0`, whose module docstring justifies it
as *"the threshold where empirically customers start actively switching"* and cites nothing, and
which sits on this repository's own no-origin debt list (`python3 -m tools.domain_constant_origins
--list`).

*Both halves of that sentence describe what this pass FOUND on 2026-09-22 and neither is true any
more, which is the point: the constant now carries a named gap citing this document, and it left
the no-origin list on 2026-09-23 as a result. Read the paragraph above as the finding's subject,
not as current state.*

**Opened by:** Lane 0 delivery, `the-three-thousand-pound-knee-under-the-whole-finding-has-no-origin`,
itself opened by
`docs/staging/records/SEAT_RESULT_THE_COMPANYS_CHURN_BELIEF_IS_FLAT_IN_THE_DIMENSION_THE_WORLD_RESPONDS_TO_2026-09-22.md`,
which measured that 235 of 244 supply legs sit below this knee and therefore carry a churn belief
with no size term at all. That measurement reported the knee's position as unsourced and
deliberately did not re-pick it. This is the pass that went looking.

**The brief named three acceptable outcomes and one forbidden one.** Forbidden: choosing any value
because of what it does to a reading on a page. No value is chosen here. The outcome is the second
one, and it arrives stronger than the brief anticipated: **the published record does not establish
a bill-level threshold, it establishes that bill level is close to orthogonal to switching
propensity, and the one population-wide natural experiment in the record moves the opposite way.**

---

## 0. The quantity, stated before any source is read

The constant is a knee in **the previous year's annual bill in pounds**, on one fuel leg, above
which the company's churn belief starts rising with consumption and below which it is *identically
absent* — not small, absent, because of the `max(0.0, ...)`. So the question a source has to answer
is:

> **Does a GB domestic household's probability of leaving its supplier rise with the ABSOLUTE LEVEL
> of its own bill, and is there a level at which that rise begins?**

Three quantities are easy to mistake for it and none of them is it:

| quantity | what it is | is it this? |
|---|---|---|
| **savings available** | the difference between what a household pays and the best offer it could take, in pounds | **no** — a differential, not a level |
| **affordability difficulty / arrears** | whether a household is struggling to pay, self-reported or on the supplier's ledger | **no** — a state, and see §4: it is weakly associated and it is not measured by bill size |
| **market-wide price level, by year** | the cap, the EPG, the average bill | **no** — a time series with one value per year for everybody |

The term's own justification in the module is *financial distress* — *"a customer who spent
£11,000/year last year at crisis prices is under more financial stress than rate % alone shows."*
That is a claim about the third column using the first, and §3 and §4 are why it does not survive.

---

## 1. Searched first, because the answer here is usually already on disk

| where | what it holds on this question |
|---|---|
| `docs/institutional/knowledge_map.md` | *Switching rates*, *Customer lifetime / churn*, *Active vs passive renewal* rows. All are **market-level or per-tariff-type**. None carries a bill level, and none carries switching as a function of a household's own spend. |
| `docs/domain_artefact_library/regulatory/` | `gb_domestic_switching_rate.json` (the record, per year, whole-population); `ofgem_default_tariff_cap_windows.json` (the law — cap and EPG levels). Neither is keyed to a household. |
| `docs/market_research/churn_price_elasticity.md` | §2, and it is the single most on-point paragraph in the repo. Quoted in §3. |
| `docs/market_research/what_a_supplier_can_observe_about_switching_propensity_cim_w6.md` | Ofgem CIM wave 6 Table 56 — switching by every banner a supplier holds. Quoted in §4. |
| `docs/market_research/household_switching_response_amplitude.md` | Establishes that **no published source gives a within-household response at all**, on two named sources fetched live. |
| `docs/staging/done/WORKER_FINDING_THE_WORLD_PRICED_IN_PERCENT_WHEN_HOUSEHOLDS_DECIDE_IN_POUNDS_2026-08-27.md` | Ofgem/BMG *Understanding Consumers' Energy Tariff Choices*, n=3,235. Quoted in §2. This is the source that settles it, and it has been in the tree since August. |

**Nothing in any of them states a bill level at which switching activity rises.** That absence is
not for want of looking: Ofgem publishes switching cut by tariff type, payment method, supplier
size, debt level, bill difficulty, satisfaction and prior switching, and **does not publish it cut
by bill size** — which is itself informative, and §2 says why.

---

## 2. What the record DOES establish about spend, and it is close to zero

**Ofgem / BMG Research, *Understanding Consumers' Energy Tariff Choices*** — conjoint choice
experiment, n = 3,235 GB energy bill payers, representative on 2021 census targets, fieldwork
29 Mar – 9 Apr 2024, published July 2025. Already the calibration source for the world's own
`simulation/market_switching_propensity.churn_position_multiplier`.

Two statements, both the publisher's own words:

> *"We found that consumers value savings in absolute terms rather than in proportion to their
> bill… i.e. £150 and not a 3% saving — particularly for customers with higher energy outgoings."*

> *"Reported household spending on energy has a very limited impact on how consumers evaluate
> prospective deals."*

And its **Table 3**: the Spearman correlation between **energy spend** and **switching propensity**
runs **−0.07 to +0.05** — it does not reliably clear zero in either direction, and its sign is not
determined.

**Read against the constant, this is decisive in shape before it is decisive in level.** A
correlation bounded inside ±0.07 is not a relationship with a knee in it somewhere that this study
failed to find; it is the statement that the variable barely moves the outcome across the range the
study observed. A threshold model asserts the strongest possible form of dependence on that
variable — zero below, linear above — and the source closest to the question puts the dependence at
approximately none.

**What the same source DOES support is the world's construction, not the company's.** Spend does not
change how eagerly a household chases a given number of pounds; it changes **how many pounds a given
percentage is worth**. That is a scale on a differential, which is exactly what
`churn_position_multiplier(price_differential_pct, annual_bill_gbp)` does — and it is not a level
term, and it has no knee.

---

## 3. The one population-wide natural experiment runs the other way, and this module already knows

`docs/market_research/churn_price_elasticity.md` §2, on 2022:

> **CRITICAL FINDING: Rising absolute prices did NOT increase switching propensity. 2022 empirically
> disconfirms the price-momentum-drives-switching hypothesis. PRIMARY driver is SAVINGS AVAILABLE.**

The published series (DESNZ *Quarterly domestic energy switching statistics*, QEP table 2.7.1,
released 2026-06-30, read from `knowledge_map.md`'s *Switching rates* row, which is the corrected
one): GB domestic electricity switching **15.57% in 2021 → 3.06% in 2022**. Every household's bill
rose; the cap reached **£674.7/MWh electricity for Jan–Mar 2023** and a typical dual-fuel bill would
have been **£4,279** had the Energy Price Guarantee not held it at **£2,500**
(`docs/domain_artefact_library/regulatory/ofgem_default_tariff_cap_windows.json`, `epg_note`). The
whole population moved up the axis the term is keyed to, and switching fell to the trough of the
ten-year record.

**`company/crm/churn_model.py` ALREADY CARRIES THIS FINDING, SIXTEEN LINES ABOVE THE TERM.** The
2026-08-25 repair to the *rate* term states it in the file's own words:

> *"That second case is not a hypothesis; it is 2022, when domestic bills reached £3,549/yr and
> switching COLLAPSED to 3-4%… the market-wide component carries NO independent rate response."*

That repair exists precisely to stop a market-wide price rise from raising the company's churn
belief. **`bill_stress` reintroduces it through the back door**: `prev_annual_bill_gbp =
old_rate_gbp_per_mwh × annual_consumption_kwh / 1000`, and `old_rate_gbp_per_mwh` is the
customer's own rate, which rises when the market rises. So the same market-wide move that the rate
term was corrected to ignore still pushes the bill term up for every customer at once.

This is not a new source. **It is the same source, applied to one term of the model and not to the
other, in one file, for thirteen months.** The rate term was fixed on 2026-08-25; this term was
not touched.

---

## 4. What IS positively associated with switching — and it is a ratio, on a different variable

Ofgem *Consumer Impacts of Market Conditions* survey **wave 6**, Table 56 (question C4, base
n=3,458, reported behaviour over the past six months, population base rate 5.3%), read in
`what_a_supplier_can_observe_about_switching_propensity_cim_w6.md` §3:

```
                                       switched in past 6 months     vs base (5.3%)
ARREARS / DEBT   "getting harder"                 6.8%                   1.28x
                 no debt                          4.2%                   0.79x        ratio 1.6x
BILL DIFFICULTY  sometimes struggling             6.7%                   1.26x
                 no difficulties                  3.9%                   0.74x        ratio 1.7x
PAYMENT METHOD   standard credit                  5.7%                   1.08x
                 traditional prepayment           1.7%                   0.32x        ratio 3.4x
TARIFF TYPE      fixed                            7.0%                   1.32x
                 variable                         2.5%                   0.47x        ratio 2.8x
```

Three things follow, and all three are against the term as written:

1. **Financial distress IS positively associated with switching — at 1.6×–1.7×, and it is the
   weakest association in the table.** Payment method (3.4×) and tariff type (2.8×) are both larger,
   and neither is a bill level.
2. **It is a ratio across a binary state, not a knee in a continuous level.** Nothing in the banner
   supports a point of discontinuity, and a banner cannot produce one.
3. **It is not measured by bill size, and cannot be.** Arrears and "keeping up with bills" are what
   a supplier reads off its own ledger. Bill size is what it reads off the meter. Within the
   domestic population those point in **opposite** directions — see §5.

The same table's satisfaction rows are the standing warning against substituting an intuitive
proxy: dissatisfied households switch at **3.0%** against satisfied households' **5.4%**. The naive
relationship is not weak there; it is inverted.

---

## 5. Measured: at benchmark domestic consumption the term never fires, in any window of the record

Printed from the estimator and the cap commons rather than reasoned about
(`BILL_STRESS_THRESHOLD_GBP = 3000.0`, electricity benchmark consumption 3,100 kWh —
Ofgem's own divisor, stated on the face of its cap tables and recorded in
`ofgem_default_tariff_cap_windows.json`'s `basis.benchmark_consumption`):

| cap window | elec £/MWh | benchmark-household elec bill | kWh needed to clear the knee | × benchmark |
|---|---:|---:|---:|---:|
| 2019-01-01 → 2019-03-31 | 165.2 | £512 | 18,160 | 5.86 |
| 2021-10-01 → 2022-03-31 | 208.0 | £645 | 14,423 | 4.65 |
| 2022-10-01 → 2022-12-31 (EPG) | 340.0 | £1,054 | 8,824 | 2.85 |
| **2023-01-01 → 2023-03-31 (cap, the peak)** | **674.7** | **£2,092** | **4,446** | **1.43** |
| 2025-10-01 → 2025-12-31 | 263.5 | £817 | 11,385 | 3.67 |

**In every window of the published record, including the uncapped crisis peak nobody actually paid,
a benchmark-consumption domestic electricity household is below the knee.** The term is identically
zero for the typical household in all of 2016–2025. It has never expressed crisis distress, because
the crisis never reached it.

**What it does express is consumption, and where it starts depends on the price deck, not on the
household.** The knee's location moves from 18,160 kWh to 4,446 kWh — **4.1×** — across the record,
with nothing about any household changing. A control keyed to its kWh position would go red every
time the cap moved and stay green while the mechanism rotted; the finding that opened this pass
already recorded that hazard.

**And within the GB domestic population, a large electricity bill is a large house.** The term is
named for financial distress and selects on a variable whose domestic correlate is floor area,
occupancy and electric heating — i.e. it selects, if anything, **against** the households §4 shows
are actually more likely to switch. That is the definitional failure CLAUDE.md names: the concept
was not stated before it was measured, and the split was inferred from the code rather than the
definition producing the split.

---

## 6. Verdict

**A knee in bill level is the wrong SHAPE, and bill level is the wrong VARIABLE.** This is a finding
about the company's model, not a calibration, and the number is deliberately not re-picked.

- **NOT ESTABLISHED, and now searched:** any published bill level at which GB domestic switching
  activity rises. Ofgem publishes switching by seven household banners and bill size is not one of
  them.
- **ESTABLISHED, and it is a refutation:** household energy **spend** is approximately orthogonal to
  switching propensity (Ofgem/BMG, Spearman −0.07 to +0.05, n=3,235), and the publisher says so in
  words.
- **ESTABLISHED, and it is a relationship without a threshold:** affordability difficulty and
  arrears carry ~1.6–1.7× on switching (Ofgem CIM w6 Table 56) — a ratio over a state a supplier
  observes on its own ledger, not a discontinuity in a level.
- **MEASURED:** the term is identically zero for a benchmark-consumption domestic household in every
  published cap window 2019–2025, and its kWh location moves 4.1× with the price deck.

**What it would take to do this properly, named so the gap is discharged by evidence and not by a
re-pick:** a per-household hazard against the supplier's **own arrears and payment-difficulty
ledger** — which is a company observable, inside the epistemic wall, and is the variable §4 shows
carries the association. That is a different term from this one, keyed to a different quantity, and
building it is not in this pass's scope. The residual question the CIM banner cannot answer —
how much of the 1.6× is the same variation as the 3.4× payment-method effect counted twice — needs
the microdata and is filed with it.

**Not recommended, and said plainly because it is the tempting move:** moving `3000.0` to some other
number. Every candidate would be chosen for its effect on how many legs clear it, which is the
forbidden operation, and none would be more sourced than the one it replaced.

## 7. Sources

- Ofgem / BMG Research, *Understanding Consumers' Energy Tariff Choices*, n=3,235, fieldwork
  29 Mar – 9 Apr 2024, published Jul 2025 — feature importance, the absolute-savings finding, and
  Table 3's spend↔propensity Spearman. In-repo reading:
  `docs/staging/done/WORKER_FINDING_THE_WORLD_PRICED_IN_PERCENT_WHEN_HOUSEHOLDS_DECIDE_IN_POUNDS_2026-08-27.md` §1–2.
- Ofgem, *Consumer impacts of market conditions survey wave 6 data tables* (XLSX), sheet `Tables`,
  Table 56. In-repo reading, with the tautology traps named:
  `docs/market_research/what_a_supplier_can_observe_about_switching_propensity_cim_w6.md`.
- DESNZ, *Quarterly domestic energy switching statistics*, QEP table 2.7.1, released 2026-06-30 —
  the corrected per-year series. Read from `docs/institutional/knowledge_map.md` *Switching rates*,
  which carries the refutation of the earlier series rather than a silent correction.
- Ofgem *Default Tariff Cap* levels and the *Energy Price Guarantee* overlay:
  `docs/domain_artefact_library/regulatory/ofgem_default_tariff_cap_windows.json` (the law, with the
  benchmark-consumption divisor on its face).
- `docs/market_research/churn_price_elasticity.md` §2 — the 2022 disconfirmation. **Its §1 table is
  refuted for the SWITCHES and RATE columns and that refutation does not touch §2**, which is about
  mechanism and savings, not counts.
- `docs/market_research/household_switching_response_amplitude.md` — establishes that no published
  source carries a within-household response amplitude at all, which is why nothing here claims one.
