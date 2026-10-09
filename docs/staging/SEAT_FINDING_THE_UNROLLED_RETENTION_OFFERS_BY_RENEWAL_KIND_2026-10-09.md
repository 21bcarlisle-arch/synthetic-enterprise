**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted` · **Filed:** 2026-10-09 08:25, pre-registration before the run

# The 44 retention offers no household answers: what kind of renewal are they?

## Disposition of the draw (`land-the-rate-honest-retention-offer-and-count-the-unrolled-offers`)

The draw said to land `bf52e72e6` (in `/var/tmp/se-retrate`, on no remote ref). **It was not landed,
and that was deliberate.** At draw time (08:17) another seat was already landing the same fix from
`/var/tmp/se-seat-retention-rate` (surgical_land pid 90475, gating since 08:01). That version was
ordered by the director on 2026-10-09 ("hand the world the discounted rate, retire the flat
constant") and does more than `bf52e72e6`: it adds `simulation/retention_offer.py`, retires
`RETENTION_EFFECTIVENESS`, and bills a kept customer at the offered rate. Both versions rewrite the
same block of `simulation/run_phase2b.py`, so landing both would conflict or apply the fix twice.
`bf52e72e6` is superseded. Its pre-registration and refuted predictions (byte-equal arms; 28 of 72
offers rolled; a 3% offer over-credited about 3x) are kept below as evidence, and nothing in them
is needed by the landing.

That leaves the question `bf52e72e6` left open, which this file answers.

## What the code already says

`simulation.customer_events.departure_rolled_at_renewal(previous_tariff_type)` is False **only**
when the previous term was an SVT segment. So an offer that falls on an unrolled renewal is, by
construction, an offer to a household coming off the default tariff. Lines 3416-3433 of
`run_phase2b.py` split those renewals into two kinds:
- `svt_conversion`: the household converted from the SVT onto the fix;
- `declined_fix`: the household turned the fix down and stayed on the SVT.

A rolled fixed-term renewal can never be unrolled, so the count of "rolled term" offers among the 44
is **0 by construction**, not by measurement.

## Instrument

One run of `simulation.run_phase2b.main(report_end="2025-06-07")` at origin `1d09ef0f0`, the
same run shape as `bf52e72e6`'s base arm. Neither fix changes where offers land (the offer is
decided before the roll). Each `retention_log` row is joined on (customer_id, event_date) to the
decision-leg `customer_events` row and classified by its `departure_occasion`.
Script: `/var/tmp/unrolled_kinds.py` (scratch).

## Predictions, written before the run

1. The run reproduces 72 offers, 44 of them unrolled. If either count differs, the world has moved
   since `bf52e72e6`'s base, and I report the new counts.
2. Among the unrolled offers: `rolled term` = 0, and `other` = 0 (an unrolled renewal has only the
   two occasions above).
3. Most unrolled offers are `svt_conversion`, at least 30 of 44. I am less sure of this one: it
   depends on how often the world's household refuses the fix.

## Result, 2026-10-09 08:51 (the predictions above are kept as filed)

One run, origin `1d09ef0f0`, to 2025-06-07. Every one of the 81 offers joined to exactly one
decision-leg event.

| renewal kind | rolled? | offers | 3% / 5% / 8% | booked retention cost | outcome |
|---|---|---|---|---|---|
| SVT-to-fix conversion (`svt_conversion`) | no | **36** | 22 / 6 / 8 | GBP 1,329 | 36 "retained" |
| declined fix, stays on the SVT (`declined_fix`) | no | **21** | 10 / 5 / 6 | GBP 996 | 21 "retained" |
| rolled fixed-term renewal (`renewal`) | yes | 24 | 19 / 5 / 0 | GBP 455 | 18 retained, 6 left despite the offer |
| other | — | 0 | — | — | — |
| **all** | | **81** | | **GBP 2,781** | |

- **Prediction 1 is refuted.** The world has moved since `bf52e72e6`'s base (`9470735ca`): 81 offers,
  57 unrolled, not 72 and 44. The share is about the same or higher: 70% of offers (61% before) and
  **84% of retention cost** go to renewals where no household is asked.
- **Prediction 2 holds.** No unrolled offer is a rolled term, and no unrolled offer is "other".
- **Prediction 3 holds as a count** (36 conversions, against "at least 30"). As a share it is 63%,
  a little under the 68% that "30 of 44" implied.
- Every unrolled offer is logged `retained`. That is not a save. The world gives a household coming
  off the SVT no exit at that point (`svt_conversion_event`: `realized_churn_probability` 0.0), so
  the offer cannot change the outcome. Only the 24 rolled offers can buy anything, and on
  `bf52e72e6`'s and `b922911b7`'s shadow runs those buy a fraction of a household between them.

## Could the company have known the kind before offering?

**Partly, and the known part is enough to decide.**
- **Unrolled versus rolled: yes.** The kind is set by the account's *previous* tariff, and the
  company billed that term. Its own registry holds `tariff_type` (`company/crm/customer_registry.py`).
  The run's account-state row carries it, and the run already refuses an offer on an SVT term itself
  (`_indexed_tariff`). A real supplier knows which of its customers are on its default tariff. This
  needs no estimate. It is simply not passed through the renewal door today (`RenewalObservation`
  has no tariff field).
- **Conversion versus declined fix: no.** That is the household's answer to the fix, given after
  the offer. Neither kind can be saved from *leaving*.
  - *Correction, 09:05, same day: "it does not matter here" was too strong on the landed code.*
    Since `b922911b7`, `_offer_vs_default` is recomputed at the discounted rate *before*
    `renewal_outcome` applies the dominance rule (decline iff the fix is above the default). So in
    today's world a discount can turn a decline into a conversion: any decline within 3-8% of
    parity converts. **On landed code, the offer at an SVT anniversary can win a conversion.** It
    still cannot prevent a departure. That is the very alternative the director's row names ("the
    offer is what wins the conversion"). Which of the 21 declines it flips is not counted here,
    because this run predates `b922911b7`.

That is the evidence for the director's open retention-at-conversion row in
`docs/direction/DIRECTION.yaml`. His proposal there cites an older count, 32 of 60 offers and 59% of
spend. On today's world it is **57 of 81 offers and 84% of spend**. Which way to resolve it is still
his call, and nothing here acts on it.

## Caveats

- This run predates `b922911b7` (which landed while it ran). That commit leaves offer placement
  alone but bills a kept customer at the offered rate. That changes the next term's old rate, and so
  the company's next estimate, so later offers in the landed world may differ by a few. The split
  should be re-read on the landed code before anyone quotes it to the pound.
- *Checked 09:05:* `b922911b7` does **not** bill the discount on a `declined_fix` renewal. The declined
  term's account-state row is withdrawn and the window is spliced back to the SVT
  (`run_phase2b.py`, "THE DECLINED TERM IS REPLACED BY THE DEFAULT TARIFF"). The offer's booked cost
  stays in `retention_log`, which does not reach the P&L.
- `bf52e72e6`'s run-level control (`test_a_retention_offer_is_answered_at_its_discounted_rate`) was
  not carried over. It reads `nudge_physics_log` fields the landed implementation does not write.
  The landed commit's controls are unit-level, plus a census of readers.
