# FINDING — the SVT floor's filed repair applies a 2024-referenced ratio to a 2019–20 rate

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`
**Filed:** 2026-08-31.
**Pre-registration:** `WORKER_PREREGISTRATION_WHAT_A_BASE_YEAR_MISMATCH_IN_THE_SVT_FLOOR_MUST_SHOW_2026-08-31.md`,
filed before any measurement below was run.
**Opened by:** item 3 of the owed list at
`WORKER_FINDING_THE_BAND_CONTROL_IS_GREEN_ON_A_POPULATION_THE_BAND_IS_NOT_ABOUT_2026-08-31.md`.

---

## Part 1 — item 3 is discharged, and the union does NOT double-count

The open question was whether drift off SVT is an *external change of supplier* at all, or whether
`svt_rates_active_passive_2016_2025.md` §4's bottom row — "all customers ~20–22%" — is the same
quantity as the published band, which would make the SVT rows a COMPONENT of that rate rather than
a route on top of it and the whole-book union a double-count.

**It is a component, and the union is still right.** §4 is a segmentation of one population by
customer type. Its basis column states the bottom row as *"DESNZ: ~6M switches / ~28M accounts
(2019–20)"* — literally the commons artefact's own numerator and denominator
(`gb_domestic_switching_rate.json`: external changes of supplier on a GB domestic electricity MPAN,
over all GB domestic electricity accounts). The rows above it are that same rate resolved by
segment.

Double-counting would require the segments to overlap. They do not, and the reason is structural
rather than measured: an account is on a fixed deal or on SVT at any given moment, so a renewal
decision and an SVT cap segment cannot both describe the same account-year exposure. The commons
states the composition identity directly — *"the account-weighted mean supplier loss rate IS this
rate"* — which is exactly what a union over an account denominator computes. So `b8e6ba32d` stands
and the union is the construction §4's own structure implies.

**What this does change** is that the two routes are not independently free: they are jointly
constrained to average to the published band. `b8e6ba32d` already assumed that when it pinned the
whole-book total, so no code moves on this leg. Item 3 closes.

---

## Part 2 — the part that is a defect, and it is in a repair not yet implemented

Establishing the base year for Part 1 surfaced something nobody had written down.

`SVT_INERTIA_ANNUAL_RECENT = 0.20` and `SVT_INERTIA_ANNUAL_LONG_STAYER = 0.10` are **absolute
annual rates**, and §4 infers them against a **2019–20** market. `market_switching_multiplier` is a
**dimensionless ratio** with `MULTIPLIER_REFERENCE_YEAR = 2024`. `18a09617d` filed the repair for
the SVT route's market-invariance as `floor × market_switching_multiplier(year)`. That composition
is only correct if the constants' base year is 2024. It is not.

The record's own high endpoint is 0.213 at 2019 and 0.230 at 2020 against 0.161 at 2024, so the two
base years differ by a factor of **1.3758**. The filed form levels a 2019–20 rate up into a market
it was already measured in.

### Measured

| year | multiplier | naive `0.20 × m` | base-corrected | naive/corrected |
|---|---|---|---|---|
| 2016 | 1.0932 | 0.2186 | 0.1589 | 1.375776 |
| 2018 | 1.2422 | 0.2484 | 0.1806 | 1.375776 |
| 2020 | 1.4286 | 0.2857 | 0.2077 | 1.375776 |
| 2022 | 0.2671 | 0.0534 | 0.0388 | 1.375776 |
| 2024 | 1.0000 | 0.2000 | 0.1454 | 1.375776 |
| 2025 | 1.1118 | 0.2224 | 0.1616 | 1.375776 |

**P1 CONFIRMED.** The error is a constant 1.375776 in all ten years; spread across years 2.2e-16,
i.e. float noise. The year cancels, which is what makes this invisible to any year-shaped check.

**P2 CONFIRMED.** At 2020 the naive form reads 0.2857 against a source figure of 0.20 — the
constant levelled up into its own inference window.

**P4 CONFIRMED.** 10 of 10 years reduced by the correction. **2024 is the one that matters**: there
the naive form reads 0.2000 and looks like it did nothing at all, because `multiplier(2024) = 1.00`
by definition. A base-year error is exactly invisible at the reference year, and 2024 is the year a
reader would spot-check.

**P5 CONFIRMED.** No production call site composes `svt_inertia` with `market_switching_multiplier`.
`departure_risks.py:291` composes `level_anchor * svt_inertia * action_propensity`, and `18a09617d`
established the world composes it unanchored on all 1,266 rows. **So this is a correction to a
filed plan, not a live mis-levelling.** Severity is LATENT for that reason -- a real defect that
invalidates no published figure and no control's verdict -- and would have been BLOCKING had P5
been refuted, because the mis-levelled floor would already be in a capture.

### P3 was a tautology and could not have refuted anything

I filed P3 — "the corrected form returns the floor to 0.20 inside the inference window" — as the
leg that would refute the finding. **It cannot.** With the base defined as the mean of 2019 and
2020, `corrected(y) = 0.20 × R(y) / base`, so the mean over exactly those two years is
`0.20 × base / base = 0.20` by construction. Verified: the identity holds to 1e-15. It confirms the
algebra and establishes nothing about the base year.

That is a control that cannot fail, filed by me as this finding's own refutation leg, one level
above the controls it was written to check. Recording it rather than quietly dropping it, and the
honest position is: **the evidence that 2019–20 is the base year is documentary alone** — §4's
basis column — and there is no arithmetic in this repo that can test it.

**What can be said instead is robustness.** Taking the base from a different plausible window moves
the corrected floor at 2019–20 by only a few per cent — 0.1926 (2020 only), 0.2080 (2019 only),
0.2145 (2018–19) — against a mismatch of 37.6% being corrected. So the finding does not depend on
resolving the window: every candidate window is far nearer to each other than any of them is to
2024. That is a weaker claim than P3 pretended to make and it is the one the evidence bears.

---

## Consequence, and it is in the flattering direction — which was predicted before measuring

`18a09617d`'s own check on the naive form — "all eight years under their target with headroom" — is
a check on a floor inflated by 1.376x, so it passes a fortiori under the correction.

But the whole-book total is pinned to the record, so the two routes are **zero-sum**: a floor
1.376x too high pushes the renewal anchor the same amount too LOW. `18a09617d` reported exactly
that symptom — 2023's floor consuming 12.43 of 12.50 available and the fit returning **0.03**, near
total extinction of the one route the company can price against. The base-year correction relieves
the pressure it found.

This was written down in the pre-registration before the measurement, because it is the flattering
direction and it should be on the record that it was predicted rather than discovered.

**It does not unblock the anchor.** The blocking cause at `18a09617d` is a mechanism fact —
`svt_inertia_hazard` takes `years_on_svt` and `segment_days` and nothing else, so there is no
parameter the market can arrive through — and correcting the base year of a repair that has not
been implemented does not add one. The refusal there is keyed to that property and stays.

## What is owed

1. **Unchanged and still blocking:** the SVT route needs a parameter the market can arrive
   through. Baseline not curriculum, needs its own capture–fit–capture cycle.
2. **When that lands, the composition must divide by the base-year multiplier**, not just multiply
   by the year's. Recorded on the constant itself (`simulation/departure_risks.py`) rather than
   only here, because the next implementer will read the constant and not this file.
3. **Open, no number attached:** §4's segment rates are M-confidence structural inferences, and
   their base year is stated once in a basis column on a different row. If a per-fuel Ofgem Retail
   Market Indicators series settles the 2019–20 level (the `unreconciled_cross_check` in the
   commons names the same source), the base becomes measurable rather than read off a table.
