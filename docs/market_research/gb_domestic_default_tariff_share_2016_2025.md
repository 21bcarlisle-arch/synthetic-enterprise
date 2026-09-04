# What share of the GB domestic book sat on a default / standard-variable tariff, 2016–2025

Sourced 2026-09-04 by the delivery seat, for the composition half of
`departure-level-emerges-from-the-household-not-the-solver` and for the focus item
`the-arms-reach-is-a-missing-world-product-not-a-company-choice`. **Those two items converged on
2026-09-04 and this is the single sourcing both were told to share.** Whichever is worked next reads
this rather than sourcing it again.

**The numbers live in `tools/published_tariff_mix.py`, not in this file.** That is deliberate and it
is the point of the exercise — see §1. This document is the write-up: where each figure came from,
what it counts, and what it does and does not settle.

---

## 1. The first result is that this was already in the tree, three times, and nothing pointed at it

The item said *"establish from the published record"*, which reads as a research task. It was mostly
a reconciliation task. Before this turn the same Ofgem series existed as:

| copy | form | what it was missing |
|---|---|---|
| `docs/market_research/svt_rates_active_passive_2016_2025.md` §2–3 | prose | no per-year table; the churn inference beside it is confidence M |
| `docs/design/DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` §(b) | markdown table | windows, not years; the population qualifier dropped |
| `tools/svt_generated_share_check.PUBLISHED_DOMESTIC_FIXED_SHARE` | Python dict | 2020 copied from 2019 with no source; the population qualifier dropped |

None of the three cited the others. The finding that needed this series
(`SEAT_FINDING_THE_LEVEL_IS_CLAMPED_...`) cited none of them, and two focus items were each about to
source it independently. **This is the VAT shape** — one published quantity, N implementations, a
correction applied to one of them — and the note on the focus item exists precisely to stop it, which
means it had already happened before the note was written.

So the deliverable is not a fourth restatement. `tools/published_tariff_mix.py` is now the one home,
`svt_generated_share_check` imports from it, and
`test_the_published_check_band_cannot_be_read_by_the_world_it_judges` holds the wall that keeps it a
check rather than an input.

## 2. The correction that made consolidating it worth doing

**Ofgem's headline default-tariff share excludes prepayment customers. All three copies dropped that
qualifier. More than 90% of prepayment customers are on a default tariff.**

State of the Market 2019 says both halves, two pages apart:

> §3.24 — *"The proportion of customer accounts on these tariffs has declined over time. It was
> around 69% in 2015 and gradually fell to 53% by April 2018. As of April 2019, 53% of electricity
> customer accounts and 51% of gas accounts, **excluding customers on prepayment**, were still on
> default tariffs."*

> §3.56 — *"As of March 2019 there were 4.3 million customers on prepayment meters (PPM),
> representing around **15% of all customers in GB**."*   §3.60 — *"**More than 90%** of prepayment
> customers continue to be on SVTs."*

Restoring prepayment at those published rates — `0.85 × 0.53 + 0.15 × 0.90` — puts the all-domestic
2019 share at about **59%**, not 53%. The same correction moves 2018 from 53% to ~59% and 2017 from
57% to ~62%.

**This is not a rounding argument; it reverses a verdict.** Measured against the world (§4), this
book's 2018 and 2019 SVT share reads *above* the record on the as-published basis and *below* it on
the restored one. Which basis is right is **not settled here and is deliberately not settled**:
`simulation/population_draw.py` gives a household `payment_method: "direct_debit" | "other"` and
models no prepayment meter at all, so this world's book matches neither published population. Both
bases are carried per year and every caller names which it used.

## 3. The series, and the two years that are a declared gap

Per-year bands with sources are in `tools/published_tariff_mix.DEFAULT_TARIFF_SHARE`; each row
carries its own `population`, `source`, `confidence` and `excludes_prepayment` fields. Summary of
the default/SVT share on the **all-domestic** basis:

| year | share | basis of the underlying figure | confidence |
|---|---|---|---|
| 2016 | 66–74% | CMA 2016, Big Six domestic ("70%+"); Ofgem's ~69% for 2015 | M |
| 2017 | ~62–63% | Ofgem Sep 2017 (57%) / Apr 2017 (59%), non-PPM, 10 largest, PPM restored | H |
| 2018 | ~59% | Ofgem SotM 2019 §3.24, April 2018 (53%), non-PPM, PPM restored | H |
| 2019 | ~58–59% | Ofgem SotM 2019 §3.24, April 2019 (53% elec / 51% gas), PPM restored | H |
| **2020** | **no established figure** | — | — |
| **2021** | **no established figure** | — | — |
| 2022 | 80–90% | fixed deals withdrawn market-wide; ~29m of ~32m on SVT by Apr 2023 | M |
| 2023 | 80–90% | ~90% at Apr 2023, FTCs re-emerging in H2 | M |
| 2024 | 80–86% | **derived** — see below | M |
| 2025 | 64–70% | Ofgem SotM Jan 2026: ~one-third on FTCs at July 2025 | H |

**2024 is the one genuinely new figure and it is derived, not read.** Ofgem's January 2026 State of
the Market says: *"By July 2025, around one-third of customers were on FTCs, **twice the proportion
recorded in July of the previous year**."* One-third halved is ~16–17% on FTCs at July 2024, so
~83–84% on default. It is banded 80–86% to carry the rounding in "around one-third" and because
Ofgem's own chart note folds *"non-standard variable/other"* into SVT for reporting, so FTC and
default do not exhaust the market in their series either.

**2020 and 2021 are `None` and are not interpolated.** The obvious move is to interpolate 2019→2022
and it is refused: that interval contains the crisis, the one stretch of this record known to have
moved fast and non-monotonically, so an interpolated value would be a manufactured reading in exactly
the years the world is hardest to check — and indistinguishable from a sourced one downstream.
`test_a_year_with_no_published_share_is_refused_and_never_interpolated` holds that.

**The named route to closing the gap.** Ofgem's SotM chart *"Electricity share of customers on each
tariff type"* starts at April 2021 and would settle 2021 outright. Its values are in an image and are
not in the PDF's text layer, so they were not read off by eye. The per-supplier data-portal series
(*"number of domestic electricity customer accounts by supplier … standard variable, fixed and other
tariffs"*) is the other route and would settle 2020 as well. Neither has been fetched.

## 4. What the world actually does, measured against it

`python3 -m tools.svt_generated_share_check --basis {all_domestic,as_published}`, on the built
schedules, account-days:

| year | world on SVT | published (all-domestic) | world vs published |
|---|---|---|---|
| 2016 | 0.0% | 66–74% | −66pp |
| 2017 | 42.6% | ~62% | −19pp |
| 2018 | 54.7% | ~59% | −4pp (but **+1.7pp** on the as-published basis) |
| 2019 | 55.3% | ~59% | −4pp (but **+2.3pp** on the as-published basis) |
| 2020 | 58.2% | — | cannot tell |
| 2021 | 58.0% | — | cannot tell |
| 2022 | 78.5% | 80–90% | −2 to −12pp |
| 2023 | 73.1% | 80–90% | −7 to −17pp |
| 2024 | 55.0% | 80–86% | **−25 to −31pp** |
| 2025 | 49.5% | 64–70% | −15 to −21pp |

**The world's SVT share is below the published one in every year it can be compared, on the
all-domestic basis, and 2016 and 2024 are the worst two.** 2016 is 0% because the product is not
reached that early at all. The direction agrees with what `simulation/svt_product.py` predicted in
prose before any of this was measured — *"the generated SVT share will come out LOW against the
published one"* — and with the cause it named: home-move-onto-incumbent does not exist in this world
(`CHOICE_AND_CHANNEL_ROADMAP.md`, C6).

## 5. What this settles for rung 1, and it is not what the focus item assumed

`docs/reports/svt_composition_vs_published.json` moves the world's SVT account-day share to the
published one, hazards untouched, and re-measures the rung-1 band.
**It closes nothing.** Five of the seven fitted years are measurable (2020 and 2021 are refused for
the gap above); one of the five reaches the band's low endpoint, and that year — 2023 — was already
reaching it before the counterfactual ran. `years_newly_closed_by_composition` is empty on both
accountings and on both published bases.

That **confirms** §9 of the finding, which had it as a ceiling argument, and strengthens it: the
ceiling bound showed composition fails at values nobody claims are real, and this shows it fails at
the value the record published. **The hazard per SVT-account-year remains the leg.**

It also **refutes** §9's parenthetical about direction. §9 said this world's reach was *"already at
or above any published default-tariff share"* and that a lower published share would widen the hazard
gap. The published share is *higher*, not lower, and the world's share is *below* it — the opposite
sign. §9 compared `reach` (0.67–0.98, a decision count over accounts) against a **stock** statistic;
the comparable quantity is `reach × exposure` (0.43–0.72), which is account-days over account-days.
Two correct figures whose ratio was not the quantity being claimed.

## 6. What is still owed

- **2020 and 2021**, by the two named routes in §3. Until then any whole-window statement about
  composition covers 5 of 7 fitted years and must say so.
- **Whether this world's book is the PPM population or the non-PPM one.** It is currently neither.
  That is a modelling question, not a sourcing one, and it decides the 2018 and 2019 verdicts.
- **The question §9 left with the source, unchanged and still the critical path**: whether
  `SVT_INERTIA_ANNUAL_RECENT = 0.20` is the right published quantity at all. It models drift off the
  SVT *product*; the band it must reproduce is external change of *supplier*. Nobody has established
  the relation, and no share of the book fixes that.

**No constant was picked, no solver aim point moved, and `YEAR_LEVEL_ANCHOR` was not edited.** The
published share is a check on output and never an input, which is `svt_product.py`'s own standing
rule and is now held by a control rather than by a docstring.

## Sources

- [Ofgem, State of the Market 2019](https://www.ofgem.gov.uk/sites/default/files/docs/2019/11/20191030_state_of_energy_market_revised.pdf) — §3.24 (default-tariff share 2015/2018/2019, and the prepayment exclusion), §3.56 (PPM ~15% of GB customers), §3.60 (>90% of PPM on SVT)
- [Ofgem, State of the Market: energy retail highlights, January 2026](https://www.ofgem.gov.uk/sites/default/files/2026-01/State-of-the-Market-Energy-Retail-Highlights-January-2026.pdf) — one-third on FTCs at July 2025, "twice the proportion recorded in July of the previous year", and the chart note folding non-standard-variable into SVT
- [Ofgem, State of the Market Report, April 2025](https://www.ofgem.gov.uk/sites/default/files/2025-04/OFG2296_State%20of%20the%20Market%20Report.pdf) — re-emergence of FTCs in H2 2023
- [Ofgem, Standard variable tariffs: latest trends at September 2017](https://www.ofgem.gov.uk/publications-and-updates/standard-variable-tariffs-latest-trends-september-2017) — 57% at September 2017, 59% at April 2017, non-PPM, 10 largest suppliers
- In-tree, already held: `docs/market_research/svt_rates_active_passive_2016_2025.md`,
  `docs/design/DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` §(b)
