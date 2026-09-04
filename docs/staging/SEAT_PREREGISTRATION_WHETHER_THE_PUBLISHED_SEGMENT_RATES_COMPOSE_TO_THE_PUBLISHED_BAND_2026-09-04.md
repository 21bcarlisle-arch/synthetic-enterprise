**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION — whether the published segment rates compose to the published band

**Filed:** 2026-09-04, delivery seat, Lane 0, claim
`departure-level-emerges-from-the-household-not-the-solver`, BEFORE the composition below was run
as code.

A prediction, filed before its measurement. It becomes evidence only when graded, and it is graded
in `SEAT_FINDING_THE_LEVEL_IS_CLAMPED_AND_THE_MECHANISM_UNDER_IT_IS_COMPRESSED_NOT_MISDIRECTED_2026-09-03.md`
§11 beside the result.

Filed at `6c97430d0`, **before** the identity below was implemented, run, or printed at real inputs
for any year other than the two disclosed in the next section.

---

## What is being predicted, and why it needs pre-registering at all

§9 of the finding above measured the SVT route's shortfall to a single named quantity — the hazard
per SVT-account-year — and put the gap at **1.67× and 1.71×** against the world's own published
source in the two years where the world runs that source to within 4%. §10 removed composition as an
explanation. Both closed with the same open question, in §9's words:

> *"the question is not 'raise the constant' but **whether 0.20 is the right published quantity for
> what this hazard models at all**: the hazard is drift off the SVT product, and the band it is being
> asked to reproduce is external change of supplier. Those are not the same event, and nobody has
> established the relation."*

That question has a form that can be settled from published evidence alone, with **no world in it**,
and it is the form this turn measures. The record publishes three things that must be mutually
consistent:

> `R(y)  =  s(y) · H_svt(y)  +  (1 − s(y)) · H_fixed(y)`

- **`R`** — GB domestic electricity changes of supplier over all GB domestic electricity accounts,
  per year, banded. `simulation/market_switching_propensity.published_departure_band()`, off the
  regulation commons.
- **`s`** — share of GB domestic accounts on a default/SVT tariff, per year, banded, on two declared
  bases and `None` where nothing is established. `tools/published_tariff_mix.DEFAULT_TARIFF_SHARE`,
  landed by §10.
- **`H_svt`, `H_fixed`** — external switching rates *within* each segment.
  `svt_rates_active_passive_2016_2025.md` §4 offers ~15–20% recent / ~5–10% long-stayer for the SVT
  segment, and ~35% *"fixed at expiry → active switch"* for the other. Those are the numbers
  `SVT_INERTIA_ANNUAL_RECENT = 0.20` was taken from.

One equation, two unknowns: per year the record admits a **line**, not a point. The reading owed is
that line — the interval of `H_svt` the record can bear — and where the published 0.20 and the
world's required 0.334 each sit on it.

**The load-bearing asymmetry, and it is the reason this is worth a measurement rather than an
argument.** `H_fixed` is NOT 0.35. 0.35 is the share of expiring fixed-term households who *actively
renew to a new fixed deal*, and a household that picks a new fixed deal **with its existing
supplier** is an internal tariff move, which the published numerator does not count. So
`H_fixed = 0.35 · φ`, where **φ is the external share of active fixed renewals** and is a quantity
this pre-registration does not know the value of.

## The disclosure this pre-registration owes

**I have already done part of this arithmetic by hand, before writing this file, and filing a
prediction while concealing that would make the document worthless.** Specifically, at 2019 I took
`s ≈ 0.53` as-published, `H_svt ≈ 0.17`, `H_fixed = 0.35` at φ = 1 and got a composed rate of about
**0.255** against a band of 0.207–0.213 — an overshoot — and inverted the same year to an admissible
`H_svt` of about **[0.08, 0.39]**. I did the same by hand for 2017, 2018, 2023 and 2024 at one
significant figure and read an overshoot in each. So the *direction* of P1 is not news to me at
filing time and P1 is filed as the weak prediction it is; **P2, P3 and P4 are the ones that carry
this document**, and none of their answers is known to me.

## The predictions

**P1 (weak, direction already hand-derived — filed for the record, not for credit).** The forward
composition at the published pair (`H_svt` from the ~15–20 / ~5–10 bands, `H_fixed` at φ = 1)
**overshoots** the published band — composed above the band's high endpoint — in **every** year that
can be compared, on **both** published-share bases. If any year lands inside, P1 is refuted for that
year and the finding says so.

**P2.** The φ that the record requires in order to admit the world's needed
`H_svt(2019) = 0.334` is **below 0.25** — i.e. fewer than a quarter of active fixed-term renewals
would have to be external changes of supplier. Refuted if it comes out at or above 0.25, and refuted
badly if it comes out above 0.5.

**P3.** The record's LOWER bound on `H_svt` — the value implied when the fixed segment is given the
most it can possibly do, φ = 1 — is **below the published 0.20 in every comparable year**. If that
holds, then the published 0.20 is not a floor the record insists on, and the direction of §9's gap
("the world needs 1.7× its own source") is not by itself evidence that the source is wrong. Refuted
if any comparable year's lower bound sits at or above 0.20.

**P4.** **φ is not established anywhere in this tree.** Neither `docs/market_research/` nor
`docs/domain_artefact_library/` holds a figure for the external share of active fixed-term renewals,
and `simulation/renewal_engagement.py` — which implements the 35/65 active/passive split — does not
distinguish internal from external at all. Predicted: this measurement ends in a **declared gap with
a named published route to closing it** (Ofgem's *Consumer Impacts of Market Conditions* survey
separates "switched supplier" from "switched tariff with the same supplier"), not in a number.
Refuted if a sourced φ is already in the tree, in which case the deliverable is a reconciliation and
not a gap — which is exactly what happened to §10 and is the reason this prediction is filed.

**P5.** This reading **closes no year of rung 1 and moves no constant.** No value in
`simulation/departure_risks.py` is edited, no solver aim point moves, `YEAR_LEVEL_ANCHOR` is
untouched, and `emergent_level_verdict` still reports six years of seven outside their bands after
this lands. §4's constraint 4 is honoured a seventh time. Refuted if any of those move.

## What would make this measurement worthless, stated in advance

- Composing on the **world's** tenure mix rather than a published one would put the world inside the
  published check and make the reading circular. The SVT-segment rate must be composed from the
  published tenure split (Ofgem Consumer Engagement Survey 2018: 29% on SVT 3+ years, 23% under 3
  years) and from nowhere else, and the control must refuse a `simulation/` import.
- Filling 2020 and 2021 by interpolation. They are declared gaps in `DEFAULT_TARIFF_SHARE` for a
  stated reason and they stay refused here; the denominator is reported as what it actually is.
- Quoting one basis as the other. Both `as_published` and `all_domestic` are carried through to the
  verdict and every row names which it used.

— Delivery seat, 2026-09-04.
