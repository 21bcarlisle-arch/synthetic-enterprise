**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# Explore's slots picked the extreme with no validity check, and five of the seven were errors

This answers the director's steer and question of 26 Oct (`docs/staging/advisor/done/DIRECTOR_STEER_EVERY_EXPLORE_EXAMPLE_MUST_MAKE_SENSE_TO_AN_ENERGY_READER_2026-10-26.md`,
`.../DIRECTOR_QUESTION_WHY_DID_THE_TESTS_NOT_FIND_THE_EXPLORE_ERRORS_2026-10-26.md`). Everything below is
measured on the published 4ae8da9b0f book: 752 households, 52,782 bills.

## What changed tonight

`tools/generate_explore_cast.py` now ranks each slot by its extreme **only among households that pass
its checks**. A slot that has no passing household is shown empty, and the page names how many
households matched the slot's rule and which check each one failed.

The re-built cast fills **5 of 8** slots:

- switch-in: unchanged
- renewal: unchanged
- estimate trap: now PROS-2017-0264
- debt: SYN-2016-356, which passes the six-year check
- 2022 shock: now PROS-2019-0246, on actual reads

Three slots are honestly empty:

- **mover:** as before.
- **EV:** 21 households match the rule and none passes.
- **storage heating:** 96 match and none names a profile class 2 meter.

The six-stage section opened on C1, four bills long. It now opens on the feed's `default_account`,
chosen by a stated rule: a dual-fuel home on supply from 2016 to the end of the run that passes every
check, with electricity use nearest the book's median. On this run that is SYN-2016-434.

## Root cause per defect

| Defect | Module | Class | Why no test caught it | What catches it now |
|---|---|---|---|---|
| 1 EV on gas-only, -65% "effect" | `simulation/life_events.py`, `tools/generate_customer_reaction_chain.py:71` | joins fail; one-sided | nothing asked the effect's sign, size or fuel | EV checks; `SEAT_FINDING_AN_EV_LIFE_EVENT_...` |
| 1 prepayment billed as credit | billing, ledger | joins fail | payment method and billing each passed alone | common check; `SEAT_FINDING_A_PREPAYMENT_...` |
| 1 crisis gas "half the cap" | none: the premise is refuted, below | n/a | n/a | n/a |
| 2 storage heating C1 | generator rule: a second register taken to mean Economy 7 | provenance taken for correctness | the rule's own test passed on any two-register bill | profile class and winter-use checks; `SEAT_FINDING_EXPLORES_CAST_FINDS_..._2026-10-23` |
| 3 shock on two estimates, 37,500 kWh/yr | shock rule; no use band anywhere | aggregates hide tails | means and totals stayed green | actual reads and percentile band; `SEAT_FINDING_THE_2022_SHOCK_...` |
| 4 33 estimates against SLC 21B.4 | read duty / estimator | one-sided (the duty was tested to fire, not to bound the run) | no test read the run length off the bills | read-duty year; `SEAT_FINDING_A_THIRD_OF_HOUSEHOLDS_...` |
| 5 statute-barred clock | `company/billing/collections_journey.py` | one-sided | the write-off was tested to happen, not to wait six years | six-year check; `SEAT_FINDING_A_STATUTE_BARRED_...` |
| 6 mover, and "households move" on the home page | the record carries no move-out | provenance taken for correctness | the copy check reads bytes, not meaning | the slot is empty with its reason; the home-page claim is open below |
| 7 752 vs 750 households | Explore counts `customers.json` groups; the home page counts households served (`tools/generate_dashboard_data.py:3121`) | definition never stated | each count is right for what it counts | open below |

The director's hypothesis 2, same author and same blind spot, sits under every row. It is why the
ruling's invariant suite must be written from the Knowledge pages by an agent that has not read the
code.

## Counts across the whole book (the question's ask)

- **Life events against fuel legs:** 21 EV arrivals.
  - 1 is on a gas-only household.
  - 1 has a negative effect.
  - 5 state an effect outside the 1,750–3,300 kWh a year band.
- **Prepayment against billing:** 100 households pay by prepayment.
  - 88 of them are sent estimated bills.
  - 3 carry an outstanding bill.
- **Estimate runs against the read duty:** 250 of 752 households have a bill more than 365 days after
  that fuel's last actual read.
- **Use against population percentiles:** 27 of 752 households are outside the 1st–99th percentile
  for their fuel and segment.
- **IDs:** 161 of 752 households carry a non-public id, such as C1, the archive cells. They are listed
  in the six-stage picker. Open.
- **SVT price against the cap, every period:** this uses the bills before each fuel's first renewal,
  because the published book has no recorded term. The median all-in unit rate sits **at** the cap in
  every window from Apr 2021 to Mar 2023, for both fuels, at a ratio of 1.00. The 10th percentile is
  0.82 to 1.00. 45 gas bills in Apr–Sep 2022 are under 0.6x the cap. They are not yet read, and may be
  stubs.

## Correction, beside the claim: the crisis gas price

The steer and the ruling, step 2, say SYN-2016-476 paid about 3.9p/kWh for gas in Jan 2022, against
"a cap of about 7.4p". **The cap in force in Jan 2022 was 4.07p/kWh**, including VAT. That is the
Oct 2021–Mar 2022 window: `ofgem_default_tariff_cap_windows.json`, gas 40.7 £/MWh. **7.37p is the
Apr–Sep 2022 cap.**

That household's bill is £74.46 for 1,621.7 kWh, about 4.6p including the standing charge. The
`tariff_max £38.76/MWh` in `annual_pnl` is the commodity rate alone, not the all-in rate. Across the
book the Oct 2021–Mar 2022 SVT median is 4.07p against a cap of 4.07p.

So step 2's measurement is done and refutes the premise. SVTs are not materially under the cap, and
the crisis P&L does not move on this account.

The floor side of the ruling's band, "between wholesale cost and cap", is a **GAP**. The cast
generator has no wholesale cost per period, so only the ceiling is checked.

## Open, owned here

- Take the home page's "households move" off until the record carries a move.
- Define the household count once, and use it on both pages.
- Keep non-public ids out of the picker, or say what they are.
- Layers 1 and 2 of the steer, beyond tonight's per-slot checks: the standing invariant suite and the
  post-publish cold reader. These are the ruling's steps 4 and 6, and they are not built yet.
