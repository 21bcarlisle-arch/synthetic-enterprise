# PB4 R6: a woken SVT household now chooses by its own elasticity, and the saving gradient is a named None

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity` · **Claim:** `pb4-r6-the-woken-share-for-svt-stock-between-boundaries` (Lane 0)

R6 from `SEAT_FINDING_PB4_EXPERT_HOUR_RETAKE_FAILS_AND_THE_DISENGAGED_ELASTICITY_IS_ALMOST_NEVER_CONSULTED_2026-10-07.md`.

## Knowledge (read from the PDFs; `how_households_respond_to_supplier_contact.md` §2.7)

- Woken share of default-tariff stock between boundaries, per contact: **0.024** (CMOL
  supplier-branded letter), **0.040** (CMOC), **0.203** (Collective Switch 1). The savings shown
  were £200-£300 in all three, so **the instrument sets the level, not the saving**.
- **Saving gradient: no causal source.** CMOL's annex pools all arms with saving as a main effect
  (+0.52 pp/£100). CMOC's +1.2-1.3 pp/£100 is among contacted customers only, because the control
  group had no saving computed. The Collective Switch publishes no gradient: *"switching at all
  levels of potential saving"*. Carried as `WOKEN_SHARE_SAVING_GRADIENT_ON_SVT_STOCK = None`.

## Build (`simulation/contact_response.py`, level 1, not wired)

`svt_departure_after_contact(instrument, p_drift, churn_if_choosing)` keeps the drift and wakes
the instrument's share of the rest. `churn_if_choosing_off_svt(our_premium_pct, elasticity, bill,
level_anchor)` is the woken household's choice, through the world's own loss curve and its own
elasticity. At +20% and the 2017 anchor it runs **0.19 at elasticity 0.3, 0.29 at 1.0 and 0.64 at
2.5**, so the elasticity now reaches behaviour on SVT. Four controls are added, and their three
claimed mutations each red.

## What it does not do

**It is not wired: nothing in the world sends a contact to SVT stock.** The sender is the company's
contact decision (C34) through the seam. Until it exists, this route is available but not reached,
so R6 is half-closed. The shape is right and the run does not observe it. At CMOC inputs the
contact-caused gradient is 0.09-0.63 pp/£100, below CMOC's 1.2-1.3. Those two quantities differ
(see §5 of the research doc), and the gap points the way a flat woken share predicts.

**Next:** wire a company SVT-stock contact through the seam (C34/W2_39 level 2), then re-run the
capture so the disengaged's elasticity shows in `svt_decisions`. R1+R5 (page denominator and
exposure decomposition) are still open.
