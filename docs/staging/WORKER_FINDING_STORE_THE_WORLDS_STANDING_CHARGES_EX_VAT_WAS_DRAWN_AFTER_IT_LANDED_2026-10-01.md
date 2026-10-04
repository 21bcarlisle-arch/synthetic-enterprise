**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` — Lane 0 delivery

# `store-the-worlds-standing-charges-ex-vat` was drawn after its work had landed

Disposition: **released, not rebuilt.** Every DONE condition is already met on origin, under the
claim `close-the-vat-basis-class-in-the-world`:

- The basis is sourced and declared. `0407ce0e3` re-reads both standing-charge tables ex-VAT from
  Ofgem's cap level model v1.31. Inc-VAT is established: 27.13p × 1.05 = 28.49p, Ofgem's published
  figure. The pre-2022 "typical market averages" are gone. 2016–2018 are marked notional (the
  model's back-cast to before the cap).
- The run is filed in `SEAT_FINDING_THE_WORLDS_STANDING_CHARGE_IS_NOW_EX_VAT_AND_THE_VAT_CLASS_HAS_A_CONTROL_2026-10-01.md`.
  Its P4 is the DD opening move this item asked for: the 8 accounts from 2023 that opened above the
  53p fallback now all open lower, and the 20 from 2024–25 shift a median −£1.24/month.
- The class control `tests/architecture/test_a_price_crosses_vat_only_through_a_named_rate.py` is
  on origin at `78f1cc756`.

`--landed-under` refused, correctly: that landing predates this draw, so `--release` is the right
door.

The live claim `attribute-the-renewal-feedback-on-the-ex-vat-standing-charge` is a different piece
of work. It is the un-attributed 12% left in P3 of that finding.

**Gaps still open (not part of this item):**
- 2025 is not tabled and clamps to 2024.
