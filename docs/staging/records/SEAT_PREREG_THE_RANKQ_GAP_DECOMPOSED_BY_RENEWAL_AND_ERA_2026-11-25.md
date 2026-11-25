**Severity:** RECORDED · **Lane:** 0 delivery · **Direction item:** `the-retention-result-decomposed-and-checked-against-reality` · **Ruling:** 25 Nov 12:31, s.3

# Pre-registration: where rankq's −£2.45 sits, renewal by renewal and era by era, from the s.12g records

Written 25 Nov before any per-renewal or per-era figure below was computed. It launches no run.

**Records.** `/var/tmp/vtn-out/{rankq,twin}/{member,control}_13131_14141.json` (s.12g, grade `5cf54da43`).
Per renewal they hold the world's `p_stay_without_offer`, `p_stay_at_offered_rate`, the outcome, and the
desk's ask. Per offer they hold `retention_cost_gbp` and `expected_term_margin_gbp`. Realised money exists
only per household over the whole window, not per renewal.

**What is measured, and what each word means.**
- *Offer uplift*: `p_stay_at_offered_rate − p_stay_without_offer`, the world's own answer at the cheaper price.
- *Discount to stayers*: `p_stay_without_offer × retention_cost_gbp`, the expected discount paid to a
  household that would have stayed anyway. This is a transfer to the household.
- *Margin kept by the offer*: `uplift × (expected_term_margin_gbp − retention_cost_gbp)`. It uses the desk's
  term-margin estimate, because no realised per-renewal margin exists. That is a weakness and is stated.
- *Un-offered leave rate*: the share of renewals not offered that ended `churned`, and the world's mean
  `1 − p_stay_without_offer` where it is logged.
- Eras by term start: pre-cap (to 2018-12-31), cap era before 2021, 2021–23, 2024–25.

**Predictions (filed before reading).**
- **P1.** The world's mean offer uplift is small, about +0.03 (0.015 to 0.05), and the mean probability of
  staying anyway is large, about 0.75 (0.6 to 0.9).
- **P2.** So the offer's direct expected economics are NEGATIVE in every era: discount to stayers exceeds
  margin kept, by a factor of about 5 (2 to 15). If so, "each extra offer paid for itself" is false at the
  offer itself, and the −£2.45 must come from somewhere else.
- **P3.** That somewhere else is the household's later path, not the offer's term: the TWIN_ONLY
  households' gap (−£2.66/hh-yr, `read_rankq_split.out`) is held by a few large households, with the top
  10 hh-seeds carrying over half of it.
- **P4.** The un-offered realised leave rate in the world is about 0.3 to 0.5 per renewal, against a real
  end-of-fix external switch rate of roughly 0.06 to 0.2 within the period (2019 trial; Ofgem). If so,
  the world makes un-offered customers leave several times too fast, and every offer's value is inflated.

**Reading rules.** P2 true and P4 true: the money result is the world's error compounded by the
desk's, not evidence about ranking, and no run in this world can test the thesis until the end-of-fix
leave rate is anchored. P2 false (offers pay for themselves directly): name the era and the line that pays.

## Results (25 Nov, read after the predictions above were filed)

- **P1 HELD.** Mean world uplift +0.019 pre-cap, +0.018 cap era, +0.012 in 2021–23. P(stay anyway) 0.60, 0.35, 0.58.
- **P2 HELD, at a larger factor than predicted.** In every era the discount to stayers exceeds the margin kept: overall
  £2,649 against £308 in the twin, a factor of 8.6 (predicted 5, range 2–15).
- **P3 HELD.** The worst 10 TWIN_ONLY hh-seeds carry 82% of the gap. But the "later path" is not a mechanism of the
  world. It is a defect: the offer is answered on a roll the floor did not re-draw. See
  `docs/staging/SEAT_FINDING_AN_OFFERED_LEAVER_IS_ANSWERED_ON_A_DIE_THE_FLOOR_DID_NOT_REDRAW_2026-11-25.md`.
  Nobody predicted it, and it is recorded as found, not as predicted.
- **P4 PARTLY HELD.** The un-offered leave rate is 0.37 to 0.52 by era, inside the predicted 0.3–0.5 except
  2024–25. It is five to seven times the 6% floor of an inert book, but a small switcher-built book's real rate is
  unpublished, so "too fast" is not established. The 2021–23 direction (a rise when real switching collapsed) is
  the clearer disagreement.
- **Reading rule.** P2 true and P4 not established: the money result is void through the defect. The thesis cannot
  be read from it, and a re-grade on the fixed code is the smallest run that answers the money question.
