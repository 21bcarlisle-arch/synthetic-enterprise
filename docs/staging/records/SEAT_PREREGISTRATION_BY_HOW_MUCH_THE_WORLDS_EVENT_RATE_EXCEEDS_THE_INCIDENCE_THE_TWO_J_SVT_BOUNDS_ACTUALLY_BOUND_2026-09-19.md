**Severity:** LATENT · **Lane:** W2_customer_generator · **Atom:** none — Lane 0 delivery,
"the J_svt band compares an event count against two incidence bounds"

# Pre-registration: by how much does the world's event rate exceed the incidence the two `J_svt` bounds actually bound?

*The band's admissibility rests on one sentence — "Same KIND of quantity as the floor and as the
world, which is what makes the band admissible at all" — and that sentence is false as written. It
does not follow that the band is inadmissible. It follows that whether it is admissible is a
MEASUREMENT nobody has taken, and this is filed before taking it.*

**Filed 2026-09-19, delivery seat, Lane 0, BEFORE running anything over the capture.** Claim
`j-svt-band-compares-an-event-count-against-two-incidence-bounds`.

**Subject:** `tools.fit_year_level_anchor._internal_return_vs_the_published_ceiling` (the docstring
sentence above), `_internal_return_vs_the_annualised_band` (whose `what_this_cannot_say` already
names the mismatch and its direction), and the world figure both of them judge —
`svt_internal_return_and_tenure`'s `internal_return_rate.per_svt_account_year`.

---

## 0. The mismatch, stated once

Ofgem CIM question C4's internal row is an **INCIDENCE**: the share of surveyed households
reporting *at least one* internal switch in the past six months. One per household, however many
times they moved. Both bounds are derived from it by arithmetic that preserves that kind:

    floor:    J_svt >= (I - (1-s)*0.35) / s_max
    ceiling:  J_svt <=  I / s_min

so both bound an incidence per SVT household. The world's figure is `returned_to_fixed` stints over
SVT account-years — an **EVENT RATE over exposure**, which can exceed 1 and which an incidence
cannot.

Write `E` for the world's event rate and `J` for the world's incidence on the same population.
`E >= J` always, with equality exactly when no SVT household converts twice in the window. So:

* against the FLOOR, testing `E >= F` when the bound is on `J` **flatters** — a pass establishes
  nothing about `J`, while a fail would still be a genuine refusal;
* against the CEILING, testing `E <= C` **harshens** — a pass is strictly stronger than needed.

This matters now and did not before. The 2026-09-19 annualisation work established that the FLOOR
is the live side (world at 1.11–4.14x it, against 0.35–0.70 of the ceiling). The bound that can
actually refuse is exactly the one the mismatch flatters, and at 1.11x the whole distance between
clearing and refusing is smaller than the gap this conflation could open.

## 1. What is being measured

Two ratios, both from the committed capture, both new:

1. **The numerator ratio** — `returned_to_fixed` stints in a year ÷ distinct accounts with at least
   one such stint ending in that year. This is the world's own repeat factor. It is `1.0` exactly
   when no account converts twice in one year.
2. **The denominator ratio** — SVT account-years of exposure ÷ distinct accounts with any SVT
   exposure in that year. Below 1 whenever accounts are on SVT for part of a year.

The kind-matched world incidence is
`distinct converting accounts / distinct SVT-exposed accounts`, and it relates to the published
figure by `E = J * (numerator ratio) / (denominator ratio)`.

## 2. Predictions, before the run

**P1 — the numerator ratio is 1.0, or within rounding of it, in every year.**
`simulation/renewals.py` bounds a passive SVT stint at the household's next anniversary and re-rolls
there. A second conversion inside the same calendar year needs the household to leave SVT, complete
a fixed term, return to SVT and convert again — and fixed terms here are of order twelve months. I
expect no account to do that, so the world's repeat factor should be exactly 1.

**P2 — the denominator ratio is BELOW 1, and materially so.** Accounts enter and leave SVT
mid-year, so account-years of exposure must be less than a headcount of accounts touched. I predict
it lands somewhere in 0.4–0.8 and that it is the larger of the two distortions by a wide margin.

**P3 — therefore `E > J`, driven by the denominator rather than the numerator, and the world's
kind-matched incidence clears the tightest annual floor (0.1676) by LESS than 1.11x — possibly not
at all.** This is the prediction I most expect to be wrong in magnitude and least expect to be wrong
in sign.

**P4 — the direction stated in `_internal_return_vs_the_annualised_band.what_this_cannot_say`
survives:** floor flattered, ceiling harshened. Nothing measured here can invert that, because
`E >= J` is structural.

## 3. What each outcome means, decided now

* **P1 holds and P2 is near 1** — the conflation is an EQUIVALENCE on this capture. That is a
  finding, not a clearance: an unguarded equivalence is one world-change away from being a defect,
  so it must be measured, published and keyed to a control that reds when it stops holding. The
  docstring sentence is still wrong and is corrected beside itself.
* **P1 holds and P2 is well below 1** — the conflation is LIVE through the denominator alone, and
  the correct reading is the kind-matched incidence. The published comparison must carry both, with
  the incidence as the admissible one.
* **P1 fails** — the world converts repeatedly and both halves are live. Same remedy, larger
  number.
* **The world's incidence fails the tightest annual floor while the event rate clears it** — then
  the band has been reporting a pass it never established, and that is a REAL finding of its own,
  filed as such. It would NOT mean the world is wrong; the tightest floor is the `r = 0` corner and
  `r` is a declared `None`. It would mean the margin is not there.

## 4. What this cannot say, whatever it returns

Nothing about whether the world's rate is RIGHT. `SVT_INTERNAL_CONVERSION_RATE` is `None` and two
bounds are not a point estimate. It also cannot repair the denominator mismatch between the world's
account base and a survey's respondent base — it can only measure it and say which way it runs.

## 5. Falsifier

If the numerator ratio is not 1.0 in at least one year, P1 is refuted and this file keeps the
refutation beside the prediction. If the denominator ratio comes back at or above 1.0, P2 is
refuted and the arithmetic in §1 is wrong somewhere.

---

# RESULT, appended 2026-09-19, beside the predictions and not over them

Measured on `c6_second_pass_departure_factors.json`, the committed capture, 1,313 SVT rows.

| year | conversions | distinct converters | repeat factor | acct-years | accounts touched | exposure/account | `E` | `J` |
|---|---|---|---|---|---|---|---|---|
| 2016 | 0 | 0 | — | 0.006 | 2 | 0.003 | 0.0000 | 0.0000 |
| 2017 | 1 | 1 | 1.000 | 25.09 | 39 | 0.643 | 0.0399 | 0.0256 |
| 2018 | 9 | 9 | 1.000 | 29.27 | 42 | 0.697 | 0.3075 | 0.2143 |
| 2019 | 2 | 2 | 1.000 | 23.39 | 29 | 0.806 | 0.0855 | 0.0690 |
| 2020 | 2 | 2 | 1.000 | 27.43 | 36 | 0.762 | 0.0729 | 0.0556 |
| 2021 | 9 | 9 | 1.000 | 29.98 | 40 | 0.749 | 0.3002 | 0.2250 |
| 2022 | 0 | 0 | — | 40.11 | 51 | 0.787 | 0.0000 | 0.0000 |
| 2023 | 18 | 18 | 1.000 | 38.25 | 52 | 0.736 | 0.4705 | 0.3462 |
| 2024 | 3 | 3 | 1.000 | 34.55 | 44 | 0.785 | 0.0868 | 0.0682 |
| 2025 | 5 | 5 | 1.000 | 15.53 | 43 | 0.361 | 0.3219 | 0.1163 |
| **level** | **49** | **49** | **1.000** | **263.60** | **378** | **0.697** | **0.1859** | **0.1296** |

## P1 — CONFIRMED, and exactly

The repeat factor is **1.000 in every year that has any conversion at all**: 49 conversions by 49
distinct accounts. No account converts twice in a calendar year, for the reason predicted. **The
numerator half of the conflation is an EQUIVALENCE on this capture** — which §3 said in advance is a
finding and not a clearance, because it is a property of the world's term lengths and not of the
comparison. It is now derived in `as_an_incidence_which_is_what_the_record_bounds.repeat_factor` and
a control both asserts it and proves the machinery would report otherwise.

## P2 — CONFIRMED, and inside the predicted range

Exposure per account touched is **0.697** pooled, per-year 0.36–0.81. Predicted 0.4–0.8; the pooled
figure and eight of nine scored years land inside it, 2025 falling below at 0.361 because the
capture's window ends mid-year. Predicted as "the larger of the two distortions by a wide margin" —
it is the ONLY one.

## P3 — CONFIRMED in sign, and the strong form of it

`E = 0.1859`, `J = 0.1296`, ratio **1.434**. The world's kind-matched lower endpoint clears the
tightest annual floor (0.1676) at **0.77x** — it does not clear it. The published figure clears it
at 1.11x. **The band straddles that bar**, so the fourth bullet of §3 is the outcome: the reading
has been publishing a pass it never established.

## P4 — CONFIRMED, and one half of its stated CAUSE is refuted

Floor flattered, ceiling harshened, as predicted and as `_internal_return_vs_the_annualised_band`
already said. But that sentence attributes the gap to REPETITION, and repetition contributes
nothing — the world sits at the `r = 0` corner on the numerator. **A true statement with the wrong
cause under it**, corrected beside itself rather than over it, in
`the_gap_is_real_but_not_for_the_reason_above`.

## What this does NOT establish, restated because the result invites the error

It does not refute the world. The tightest annual floor is the `r = 0` corner of a family whose `r`
is a declared `None` — the tightest bar the record *could* support, not one it makes. The bound
actually in force is the `r = 1` corner at 0.0449, and **both** endpoints clear it (2.89x and
4.14x). What changes is that the 1.11x margin which made the floor "the live side" was the top of a
band, and the conclusion that the floor is the live side is thereby **sharpened**: it is the side
carrying a bar the world cannot be shown to clear.

The remaining mismatch is not repaired and cannot be here: `accounts_touched` is not a survey's
point-in-time base either. That is why the answer is a band with one named assumption — that
conversion probability does not decrease with exposure — and not a corrected number.

## Landed

`tools/fit_year_level_anchor.py` (`_verdict_over_a_band`, `_internal_return_as_an_incidence`, both
corrections beside their claims, and the printed surface),
`tests/tools/test_the_worlds_internal_return_is_stated_in_the_kind_the_record_bounds.py` (10 legs),
`docs/reports/svt_internal_return_and_tenure.json` regenerated.
