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

## Result (2026-10-24, worker, same claim; predictions above unedited)

**Correction before the graded pair ran.** The first full B arm ran on pre-landing code and was not
graded. It showed 6 re-fixes priced above the default the household was paying, 5 of them in 2021.
The re-fix bypassed the world's decline-and-stay rule (`DECLINE_A_FIX_ABOVE_THE_DEFAULT`, ON): the
pop skips a `_WOKEN_REFIX` term, and the splice never asked. Prediction 1 had assumed the rule held
("a woken household leaves or stays on the default"). `_splice_a_refix` now refuses a fix whose
`position_vs_default` is above zero against the default paid on the contact day, and names the gap
on the row. The pair below ran on that code. Two arms killed at session end on 2026-10-23 (22:52,
mid-2018) were never graded.

Full window, re-fix switch on in both, ~51 min each:

| | A (no letter) | B (once per stint) |
|---|---|---|
| letters sent | 0 | 803 |
| re-fixes | 0 | 20 |
| refused as dearer than the default | — | 7 (+1.6% to +82.0%) |
| SVT departures | 257 (all `svt_inertia`) | 257 (248 `svt_inertia`, 9 `price_position`) |
| `total_net` | £556,707.93 | £556,319.35 |

1. **Re-fixes, 10–60: held (20).** By fix year: 2016 4, 2017 7, 2018 1, 2019 2, 2020 4, 2023 2, and
   none in 2021–22. Each re-fix withdrew 4 default segments.
2. **H > 0 at £20–£150 per re-fix: held.** H = £1,749 ex VAT, energy only, which is £87 per re-fix.
   One re-fix is negative (2018): it was below the default on the contact day and above the later
   cap.
3. **ΔC < 0: held.** ΔC = −£389.
4. **H + ΔC < 0: REFUTED on the point estimate.** H + ΔC = +£1,360, and I cannot yet say why. On
   transfer arithmetic alone, ΔC should sit near −H, less the margin lost on the 2 leavers the letter
   added before the first fix. It is £1,360 less negative than that. Total departures are equal
   (257 each), so over the window the letter moved 9 exits from `svt_inertia` to `price_position`
   rather than adding exits. The pair cannot separate what offsets the margin given up. It could be
   knock-ons through hedging and pricing, the re-fixed terms' margin against what the default
   actually earned, or path noise. No perturbation floor has been measured for `total_net` on a book
   of ~£556k. **So this is not evidence that the letter creates value.** F11: read it as "not shown
   to destroy value on what the world records".
5. **A and B identical before the first fix starts: held, in the form that can be checked.** B's
   first letter goes on the first SVT row (2016-01-04), so "before the first send" is empty. Before
   the first fix (2016-07-01), all 88 paired rows have the same roll. Every unsent row matches on
   probability and outcome. Only the 61 letter rows differ, as built, and 2 of those flip from
   stayed to churned.

**Next (one variable):** arm C is B's letter with `A_WOKEN_SVT_STAYER_REFIXES` off. B − C is the
re-fix's own company-side effect with the letter's departures held fixed, and C − A is the
letter's departure cost alone. Handed off as `c30-whose-gain-offsets-the-refix-margin`.
