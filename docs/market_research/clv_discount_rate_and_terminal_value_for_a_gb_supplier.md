**Knowledge:** none -- a design reference for company/analytics/clv_three_horizon.py, pending the director's ruling

# CLV discount rate and terminal-value method for a GB domestic energy supplier, 2016-2025

Research question (director's owed item 9): what discount rate, and what terminal-value method,
should a GB domestic energy supplier's customer lifetime value use over 2016-2025, on published
evidence. Written by the discovery agent, read-only against external sources; no simulation code
was read or edited.

Context read first: `company/analytics/clv_three_horizon.py` lines 111-136 (`DISCOUNT_RATE = 0.10`,
already flagged by its own comment as a named simplification, citing Ofgem's 12.3% cost-of-capital
figure as a 2023+, regulatory-allowance figure that does not straightforwardly transfer);
`docs/market_research/CSS_BENCHMARKS.md`; `docs/market_research/company_commercial_strategy.md`;
`docs/market_research/supplier_financial_reporting.md`; `docs/market_research/ASSUMPTIONS.md`.

## 1. Discount-rate / cost-of-capital table

| Source | Figure | Year | What it is a rate OF | URL |
|---|---|---|---|---|
| CMA Energy Market Investigation, Appendix 10.4 "The cost of capital" | Pre-tax nominal WACC for a stand-alone GB retail supply business (assumed fully equity-funded): **9.3%-11.5%**. Components: real RFR 1.0%, nominal RFR 4.0%, equity risk premium 4.0-5.5%, asset/equity beta 0.7-0.8, tax 27%. Estimated from Jan 2007-Mar 2014 firm data (backward-looking, averaged over the period, not a point-in-time estimate) | 2016 (data period 2007-2014) | Cost of capital (market-investigation benchmark for "normal" profit) | https://assets.publishing.service.gov.uk/media/559fb6ce40f0b61567000049/Appendix_10.4_The_cost_of_capital.pdf |
| Ofgem, Default Tariff Cap design decision (Nov 2018) | Adopted the CMA's cost-of-capital analysis and translated it into an **EBIT allowance of 1.9% of revenue** for the notional efficient supplier, applied from cap launch (1 Jan 2019) | 2018 decision, effective 2019 | Regulatory EBIT allowance (% of bill), *derived from* the CMA's ~10% cost-of-capital finding, not itself a cost-of-capital figure | Referenced in Ofgem's Aug 2023 EBIT decision, para 1.1-1.2 (see row below); cross-checked in `supplier_financial_reporting.md` and `CSS_BENCHMARKS.md`, both already in-tree |
| CEPA, "Default Tariff Cap cost of capital", final report for Ofgem | Long-term/"normal market conditions" pre-tax nominal cost of equity: **9.28%-10.88%** (supports continuing the CMA's ~10%). Short-term/stressed-market estimate: **12.23%-14.94%**; headline conclusion "a cost of capital in the range of 12-15% could be appropriate while market conditions remain stressed" | 25 Aug 2022 | Cost of capital (cost of equity, notional fully-equity-financed retailer, CAPM-TMR) | https://www.ofgem.gov.uk/sites/default/files/2022-08/CEPAReport_DTCCostofCapital_2022.08.24.pdf |
| Ofgem, "Price Cap - Decision on amending the methodology for setting the EBIT allowance" | Set cost of capital at **12.3%**, applied to capital employed of £358/customer, effective from cap period 11a (1 Oct 2023). Raise justified by "an increase to the asset beta... in recognition that systematic risks faced by energy suppliers are higher than those estimated in 2018." Produces an EBIT allowance of ~£44/customer (vs £34 under the prior 1.9%-of-revenue approach for the same period) | 25 Aug 2023, effective Oct 2023 | Regulatory cost-of-capital, applied directly to capital employed (£/customer), not to revenue | https://www.ofgem.gov.uk/sites/default/files/2023-08/Price%20Cap%20-%20Decision%20on%20amending%20the%20methodology%20for%20setting%20the%20Earnings%20Before%20Interest%20and%20Tax%20%28EBIT%29%20allowance.pdf |
| Gupta & Lehmann (2003), "Customers as Assets," *Journal of Interactive Marketing* 17(1) | Worked numerical example uses an **illustrative 12% discount rate** (not a GB-market estimate) to demonstrate the margin-multiple formula | 2003 | Illustrative example rate in a methodology paper, not a market benchmark | https://business.columbia.edu/sites/default/files-efs/pubfiles/721/gupta_customers.pdf |

No source in this table is energy-sector-specific equity/debt-market evidence from Octopus or Ovo
(both privately held; no published cost-of-capital or CLV discount rate found for either). Centrica
(British Gas parent) was one of CEPA's three beta comparators (alongside SSE and EDF SA) but CEPA
reports only the blended sector range above, not a standalone Centrica WACC figure.

## 2. Terminal-value method — published treatments

**Finite horizon with retention decay** (Berger & Nasr 1998; Blattberg et al. 2001; Jain & Singh
2002, all cited in Gupta & Lehmann 2003): `CLV = sum_{t=1}^{n} m_t * prod(r_j) / (1+i)^t`, summed
to an assumed or estimated tenure `n`. This requires choosing `n` — "arbitrarily," in Gupta &
Lehmann's own words — and their worked example shows a naive 5-year finite cutoff **overestimates**
true lifetime value by about 44% relative to their infinite-horizon alternative, because a hard
cutoff ignores the compounding retention-probability decay that would otherwise push most of the
tail value toward zero gradually rather than all at once at `n`.

**Perpetuity with constant retention decay** (Gupta & Lehmann 2003, eq. 3): assuming constant
margin `m` and constant retention rate `r`, the infinite geometric series collapses to a closed
form, `CLV = m * r / (1 + i - r)` — the "margin multiple." This needs no arbitrary horizon choice:
the retention rate itself encodes ever-smaller survival probability at every future period, out to
infinity, so it is a decaying-tail terminal value by construction rather than a flat Gordon-growth
perpetuity. Gupta & Lehmann present this as the theoretically preferable simplification *given*
constant margin and constant retention.

**The refinement that matters for a real book (Fader & Hardie 2010, *Marketing Science* 29(1),
"Customer-Base Valuation in a Contractual Setting: The Perils of Ignoring Heterogeneity")**: applying
a single pooled/aggregate retention rate to the Gupta-Lehmann perpetuity **underestimates** the true
residual value of a customer base — by 38% in their worked numerical example — because real
cohort-level retention rates rise with tenure. This is not because any individual customer's risk
falls over time; it is a sorting effect: low-retention customers churn out first, so the survivors
remaining at later tenure are disproportionately the high-retention segment, and a single flat rate
applied to the whole mixed cohort misrepresents both the near-term and long-term tail. Their
prescription is a tenure-varying (cohort-level) hazard/retention curve, not a single constant rate,
whether estimated directly from cohort data or via a mixture model such as the shifted-beta-geometric
(Fader & Hardie 2007a).

**Net published guidance**: neither a hard finite-horizon cutoff (overestimates, Gupta & Lehmann's
own finding) nor a single flat retention rate projected to infinity (underestimates, Fader & Hardie's
finding) is correct in isolation. The published literature supports a tenure-varying survival/hazard
curve carried out to a long or infinite horizon as the terminal-value treatment, not a single n or a
single flat rate.

## 3. GAP — what no source read here establishes

- **No GB retail-energy cost-of-capital estimate for 2016-2018** distinct from the CMA's own
  backward-looking 2007-2014 estimate. The CMA's 9.3-11.5% figure is the only pre-2019 anchor found,
  and it is itself an average over an *earlier* seven-year window, not a 2016-2018-specific estimate.
- **No GB retail-energy cost-of-capital estimate for 2019-2022** (the loss-making cap-crisis era)
  was found as a distinct published figure; CEPA's Aug 2022 report is the first update after the
  2018 CMA-derived figure, and it describes both a "normal" and a "stressed" estimate without dating
  either specifically to 2019-2022.
- **No evidence found that Ofgem's 12.3% cost-of-capital figure (set Oct 2023) has been revisited
  since.** `docs/market_research/ASSUMPTIONS.md` (already in-tree, row dated 2026-07-10) records that
  the EBIT *allowance* (the £/bill outcome, not the 12.3% cost-of-capital input) has drifted from
  1.9% to 2.6% of the relevant cap components by Jul-Sep 2026 — but that drift is consistent with
  capital employed or the indexed-allowance mechanism changing, not necessarily with the 12.3% rate
  itself being re-estimated. Whether 12.3% is still Ofgem's current cost-of-capital assumption for
  2024-2025 is unresolved here.
- **No published cost-of-capital or CLV discount rate specific to a challenger/digital supplier**
  (Octopus, Ovo) was found; the only GB-specific figures are regulatory (CMA, Ofgem, CEPA) and are
  all built on a *notional, fully-equity-financed efficient supplier*, not any single real company's
  actual capital structure.
- **Whether a regulatory cost-of-capital allowance is the theoretically correct discount rate for a
  commercial CLV model at all** is not settled by any source read here — it is a policy benchmark for
  "normal profit" under price-cap regulation, not a company's actual opportunity cost of capital or
  shareholder required return. This is the same gap the existing code comment in
  `clv_three_horizon.py` already names.
- **No GB-energy-specific, heterogeneity-aware (Fader-Hardie-style) retention curve estimate** was
  found; their 38%-underestimate finding is from a general contractual-subscription numerical example,
  not fitted to UK energy-supply churn data.

## 4. What this means for the parameter

Not a single number — a labelled range, because the published sources disagree by era and by
market-stress regime:

- **Low end, ~9.3%** (CMA 2016, pre-tax WACC floor) — supported only as a "normal market conditions"
  floor for a stand-alone, fully-equity-financed GB retail supplier, backward-looking over 2007-2014.
- **Mid, ~10%-10.9%** (CMA central estimate within its own 9.3-11.5% range; CEPA's Aug 2022
  "long-term/normal" sub-range of 9.28-10.88%, which CEPA itself concludes gives "some justification"
  for continuing to use ~10%) — this is the range the current `DISCOUNT_RATE = 0.10` sits inside, and
  it is the best-supported anchor for a "normal conditions" read of the whole 2016-2025 record.
- **High end, ~12.3%-15%** (Ofgem's own adopted 12.3% cost-of-capital from Oct 2023 onward; CEPA's
  stressed-market 12.23-14.94% sub-range) — supported specifically for the crisis-and-recovery tail
  of the period (roughly 2022 onward), not for 2016-2021.

A single flat rate across 2016-2025 cannot be fully correct on this evidence: it was built from
regulatory snapshots that themselves changed by more than 2 percentage points between 2018 and 2023,
with the stated reason being a genuine rise in GB energy-retail systematic risk, not noise. 0.10 is a
defensible "normal-conditions" anchor and sits inside the mid-range above, but understates the
published cost of capital for the 2023-2025 tail of the record, where Ofgem's own adopted figure is
12.3%. The sourced refinement available (not built here, since this file is research only) would be
a time-varying rate: something close to 0.10 pre-2023 and something close to 0.123 from Oct 2023, or
an explicit range sensitivity rather than either single value, until a source narrower than a
regulatory snapshot is found.

On terminal value, the published record supports a tenure-varying survival/hazard terminal
treatment (decaying to a long or infinite horizon) over either an arbitrary finite-horizon cutoff
(Gupta & Lehmann's own finding: overestimates) or a single flat/pooled retention rate run to infinity
(Fader & Hardie's finding: underestimates, if the book is heterogeneous — which a mixed-tenure
domestic energy book plausibly is).
