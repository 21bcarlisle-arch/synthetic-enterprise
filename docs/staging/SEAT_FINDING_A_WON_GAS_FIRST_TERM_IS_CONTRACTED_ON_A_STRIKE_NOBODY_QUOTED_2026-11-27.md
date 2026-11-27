**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 2 · **Atom:** `PB3_book_growth_as_earned_outcome`

# A won gas first term is contracted on a strike nobody quoted

Found by the delivery seat while grading S2, 27 Nov 2026
(`docs/staging/records/SEAT_GRADE_S2_THE_CAP_HOLD_DELETION_ARM_ON_S1S_SEEDS_2026-11-27.md`).

**What happens.** S1 strikes a won electricity first term at the quote the campaign gated it on. Gas
gets no quote: `QUOTED_FIRST_TERM_RATE_KEY` is set on the electricity dict only
(`simulation/live_population.py:1553`). So a dual-fuel winner's gas first term is contracted on the
spot-led `quote_renewal` strike at the notice date. That is the same split that
`SEAT_FINDING_A_WON_FIRST_TERM_IS_CONTRACTED_ON_A_STRIKE_IT_WAS_NOT_QUOTED_2026-11-24.md` found
for electricity, and it is still open on gas. It is latent today, because the acquisition cap hold
(`held_at_published_cap`, term 0) clamps those terms to the cap.

**The measurement.** The arm with `FIRST_TERM_CAP_HOLD_DELETED = True`, against S1's 76f894811d book,
one variable:

- **47 gas first terms** move by at least 1p/MWh. 43 of them rise by more than 50p, from exactly the
  cap (SVT − 4.76%) to **up to 2.9× the SVT**. Examples: PROS-2021-0399g goes from 38.76 to
  118.29 £/MWh, and PROS-2022-0327g from 98.29 to 207.66.
- That is **+£39.63 per win** of first-term revenue, against +£0.30 from the electricity legs.
- 13 of the 47 fall in the MSC window.

**Why it matters.** Deleting the hold before gas is struck at a quote bills households above a price
they were never shown. That is transfer, not value (M2). It is the reason #2 is not flipped and is
not given a standing book (grade record, last section). The hold currently does a job the gas quote
should be doing, in the same way it did for electricity before S1.

**What done looks like.** The world-side campaign strikes a won gas first term at a price the
household saw. Either the campaign quotes gas, or the dual-fuel quote carries a gas leg. Then the S2
arm is re-run on that book, and the gas legs are predicted 0 before it runs. K8 applies: the
knowledge page for the dual-fuel quote comes first.

**GAPs.**
- Whether a real supplier's dual-fuel acquisition quote prices gas separately or bundles it is not
  established here. That goes to the knowledge layer before any build.
- The 2 SYN electricity first terms the hold also clamps (SYN-2021-001 and SYN-2016-064_3) are not
  campaign-quoted either. The mechanism that wins them was not read.
