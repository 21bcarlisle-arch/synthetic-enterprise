**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION — whether a published switcher split can close φ at all, and what it does to the hazard if it can

A pre-registration, not a finding. The finding it serves is
`SEAT_FINDING_THE_LEVEL_IS_CLAMPED_AND_THE_MECHANISM_UNDER_IT_IS_COMPRESSED_NOT_MISDIRECTED_2026-09-03.md`,
which stays **BLOCKING**.

Filed 2026-09-04, **before any external source has been fetched this pass** and before any number
separating "switched supplier" from "switched tariff with the same supplier" has been read.

---

## Why this question

§14 closed the chain owing exactly one thing, and it is the only thing it owes:

> *"the φ cross-tabulation from Ofgem's Consumer Impacts of Market Conditions survey — one
> cross-tabulation of one survey, separating 'switched supplier' from 'switched tariff with the same
> supplier' on one base. Unchanged since §11 … Before sourcing it externally, **look in this tree
> first**: that instruction has now been right four times in this chain."*

**The tree was searched first and it is dry, and that is recorded here before the external pass so
it cannot be reconstructed favourably afterwards.** What the tree holds, and why none of it is φ:

| in-tree candidate | what it is | why it is not φ |
|---|---|---|
| `gb_switching_rate_denominators.md` §7 | Ofgem CIM wave 5 (Jan–Feb 2024, base 174 switchers) and wave 6 (Jan–Feb 2025, base **754 who switched tariff or supplier**), by *stated reason* | Two different waves with two different bases. The file states in terms that *"the domestic instrument does not split it"* and that wave 6 *"is further from the split, because its population includes internal tariff switches"* |
| `household_switching_response_amplitude.md` §2.1 | Ofgem/Ipsos Consumer Survey 2021, 27% switched **supplier** P12M, n = 4,037 | An external rate with no internal companion on the same base. Its engagement segmentation is defined on the outcome (§2.3), so nothing can be differenced out of it |
| `gb_domestic_switching_rate.json` | The published external-switching series | External only, by construction and by its own `basis.numerator`: *"NOT tariff switches within the same supplier"* |
| `svt_rates_active_passive_2016_2025.md` §4 | `FIXED_ACTIVE_RENEWAL_SHARE = 0.35`, *"Fixed at expiry → active switch"* | The **denominator** of φ. It says nothing about where the active renewer goes |
| `simulation/renewals.py`, `renewal_engagement.py` | The world's renewal route | **The world has no internal-switch concept at all** — grep for `internal`, `same_supplier`, `retention`, `recontract` returns nothing. There is no world φ to read off, so no in-tree value can be mistaken for evidence |

So this pass goes external, and it goes with its answer written down first.

---

## The prediction, in full, before the fetch

The record's admissible φ is already published and is what makes this falsifiable.
§13/§14: the mix-free envelope admits φ ∈ **[0.618, 0.850]** on `all_domestic` and **[0.612, 0.770]**
on `as_published`; every *observed* tenure mix REFUSES a constant φ; §12's per-year joint intervals
sit far lower at 2017 **[0.061, 0.100]**, 2018 **[0.217, 0.251]** and 2019 **[0.110, 0.151]**.

**P1 — the instrument exists but does not publish the cross-tabulation at a usable base.** I predict
Ofgem's CIM publishes a *combined* "switched tariff or supplier" figure in its report and that a
clean external/internal split on one base is **NOT** reachable from the published tables this pass.
Confidence deliberately stated: I put this at about 60/40 and I expect to be arguing with myself
about whether a near-miss counts. **Graded FOUND / NOT FOUND, and a near-miss is graded NOT FOUND
with the near-miss described.**

**P2 — if a split is found, φ_survey lands in [0.45, 0.70].** Point prediction **0.58**. Reasoning:
external switching collapsed after 2021 while supplier retention offers did not, so a post-2022
domestic instrument should show internal switching as a large minority of all switching, but not the
majority — comparison-site-led external switching recovered from 2023.

**P3 — φ_survey lands BELOW the record's mix-free interval, i.e. below 0.618, on at least one wave.**
This is the discriminating prediction and it runs **against my own convenience**, which is why it is
worth filing: a lower φ means the fixed route supplies less of the record's external switching, so
the identity `R = s·H_svt + (1−s)·0.35·φ` must give the SVT segment **more**. That widens §9's
1.6×–1.7× hazard gap rather than closing it. **If φ_survey comes back above 0.618 I am wrong, and
the repair gets easier than I expect.**

**P4 — the implied `H_svt` at φ_survey exceeds the tenure-composed band's high end (0.1442) in at
least 3 of the 5 fitted years.** Corollary of P3 and separately gradable.

**P5 — the waves will not cover the fitted years.** I predict every CIM wave located is **2023 or
later**, so no wave falls in 2017–2021, the 2022 structural break sits between the instrument and
the years that need it, and **nothing published will establish that φ can be carried backwards
across it.** The reading must therefore state the carry-back as an assumption it does not adopt.

**P6 — the base will not be φ's base, so even a FOUND split does not close the constant.** This is
the prediction I hold most strongly and it is the definitional half. φ's denominator is *active
renewals at a fixed-term end*. A CIM-style survey's denominator is *everyone who switched anything
in the last 12 months*, which includes SVT households leaving — and those are in the SVT route, not
the renewal route. **Two different populations.** So I predict the honest outcome is a **bound with
a named direction**, not a value: survey-φ mixes the routes, and because the SVT route is
overwhelmingly external (an SVT household has no fixed deal to internally renew onto), survey-φ is
an **UPPER** bound on renewal-route φ. **`EXTERNAL_SHARE_OF_ACTIVE_RENEWALS` therefore stays `None`
whatever this pass finds**, and if I end the pass having written a number into it, P6 is refuted and
the refutation is the finding.

**P7 — nothing is picked.** No constant edited, no solver aim point moved, `YEAR_LEVEL_ANCHOR`
untouched, `emergent_level_verdict` still six of seven outside their bands. §4's constraint 4, an
eleventh time. Graded by reading the artefact's parsed values — **not** by a line diff, which §14's
P8 established is the wrong instrument for a no-value-changed claim.

---

## What I will do in each branch, decided now

- **FOUND and usable** → a register with one home in `tools/published_route_split.py` (the shape
  `SVT_TENURE_OBSERVATIONS` and `published_tariff_mix` already use), a `docs/market_research/` file
  for the source, the reading committed to `docs/reports/published_route_split.json`, φ still `None`
  with the bound published beside it.
- **NOT FOUND** → the negative is the deliverable and it is written up with the same care: what was
  fetched, what it published, and precisely which cross-tabulation is missing, so the next pass does
  not re-run this search. A dry search that is recorded is worth more than one that is repeated.

— Delivery seat, 2026-09-04, before the fetch.
