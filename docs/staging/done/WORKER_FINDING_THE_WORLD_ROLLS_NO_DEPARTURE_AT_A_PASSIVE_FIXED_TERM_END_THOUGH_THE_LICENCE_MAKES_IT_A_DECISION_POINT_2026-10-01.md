**Severity:** LATENT · **Lane:** B_commercial (world side: `simulation/`) · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon (upstream world fidelity)
**Evidence:** `docs/market_research/what_a_renewal_decision_is_for_a_gb_domestic_customer.md`; `simulation/renewals.py:211-231`, `simulation/run_phase2b.py:2323-2376` and `:2097`

# The world rolls no departure at a passive fixed-term end, though the licence makes every term end a decision point

**2026-10-01.** Found while defining what a renewal decision is for EP1's tenure horizon.

## What the record says

Every fixed-term end is a decision point. The supplier must serve a Statement of Renewal Terms
(SLC 22C.3 → 31I). The customer gets a Switching Window, which opens 49 days before the term end at
the latest, and can leave in it with no Termination Fee (24.8(b), 24.17). A customer who does
nothing becomes subject to the cheapest evergreen tariff (22C.7). An evergreen customer can leave on
any day (24.7), never pays an exit fee (24.3(a)) and has **no anniversary**. Their prompts come with
each price increase notice and at least once in any 12 months, on a date the supplier chooses
(31F.5(b)(ii), 31F.5(c)).

## What the world does

At a later fixed-term end, `rolls_active_renewal` draws active or passive for a resi household,
with about 35% drawn active.

- **Active:** `roll_lifecycle_event` rolls churn or renew.
- **Passive, about 65%:** an SVT stint begins. No departure is rolled at the term end. The only exit
  route is the C1b inertia hazard per cap segment, which has no spike at the term end.

The household then draws again at its acquisition anniversary while on SVT. The record has no such
date for an evergreen customer.

## Two fidelity questions, for a baseline decision taken blind to company results

1. **The passive term end needs a departure roll of its own.** On the least mobile book published,
   Ofgem's 2019 End of Fixed Term trial measured 6% external switching within six weeks of the term
   end. The world puts no departure there for 65% of term ends. The error runs the company's way:
   fewer exits.
2. **Whether an SVT household's look at the market should follow its anniversary.** The record
   points to the cap-change notices and the annual prompt instead. The C1b segment hazard already
   follows the cap calendar, so this may only mean the anniversary re-draw is redundant.
   **I cannot yet say** which way it errs.

## Not done here

The world is not changed. EP1's H2 does not depend on either question: it values on all-cause exits
over exposure (`BookExitRecord`), and that reading is right whatever the world does at a term end.
The size of the passive term-end spike for a small supplier's switched-in book is still unsourced
(`FIRST_RENEWAL_DEPARTURE_PRIOR = None`), so an honest fix here may have to carry it as a named gap.
