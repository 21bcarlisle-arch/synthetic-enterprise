# Pre-registration: C30, the once-per-stint SVT letter graded on both sides

*Delivery seat (executor), 2026-10-23. Claim `c30-the-per-account-svt-sender-grades-both-sides`.
Written before either graded arm was launched. The only run before it was a 2016-01..2017-02 timing
arm (146 s; 186 first-segment sends; 4 re-fixes). It sized the window and was not graded.*

## Question

With `contact_response.A_WOKEN_SVT_STAYER_REFIXES` on, does a `cmoc_letter` sent once per
default-tariff stint, at its first segment (`svt_contact_once_per_stint`), create value against
sending nothing? Which side carries that value, and does one side's gain come out of the other's?

## Arms (one variable)

Full window (`report_end=None`, 2016-01..2025-06-07), seeds as standing, and the re-fix switch on
in both.
- **A:** `CURRENT_POLICY`, no contact.
- **B:** `CURRENT_POLICY` with `svt_contact_instrument="cmoc_letter"` and
  `svt_contact_once_per_stint=True`.

`cmoc_letter` is the instrument §7.5 names for this route: CMOC's between-boundary letter, woken
share 0.040.

## What is measured, and what each one counts

- **H, the household side of the re-fixes, £ ex VAT, energy only.** Summed over B's re-fix rows:
  Σ over withdrawn default segments of (default household-charged rate − fix rate) × EAC/1000 ×
  days/365. It counts money the re-fixed households did not pay. GAP: the standing charge is left
  out, and so is the saving of a household that left for a rival (the world does not record it).
- **ΔC, the company side, £.** `total_net` B − A. It counts the whole book, so it includes the
  margin given up on re-fixes, the margin lost on added leavers, and every knock-on through
  hedging and pricing. Those parts cannot be separated in this pair.
- **Counts:** B's sends, re-fixes, re-fix refusals by reason, and SVT departures with cause
  `price_position`, all against A.

## Predictions

1. **Re-fixes:** 10–60 over the window. The timing arm gave 4 in 14 months. Most re-fixes come
   from 2016–2019 and 2023–2025, where fixes priced below the default. 2021–22 adds few: fixes
   then sat above the cap, so a woken household leaves or stays on the default.
2. **H > 0**, at £20–£150 per re-fix. The timing arm's first three were £27–£36/MWh below the
   default, on 2–8 months.
3. **ΔC < 0.** A re-fix gives up margin at the same cost, and the letter adds `price_position`
   departures.
4. **H + ΔC < 0.** On what the world records, the letter as built moves value from the company to
   re-fixed households and loses leavers besides. It does not create value. That errs against the
   thesis (F11). A refutation is H + ΔC ≥ 0. That would need a re-fix to keep a household that
   would otherwise have drifted away later, which this world can do through the anniversary roll.
   I cannot size that from the timing arm.
5. **Before B's first send, A and B are identical**, decision for decision.
