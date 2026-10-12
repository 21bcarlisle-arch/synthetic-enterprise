**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# World freeze: household payment behaviour (2026-10-12)

The director's principles of 2026-10-11 ("1. World first ... 2. Freeze, then solve") and his ruling
of 2026-10-12 (the world's response to a bill shock, mandate cancellation as its own act and the
debt-to-prepayment route, before grading the engine). This records what the world's households do
about paying, every toggle and range, the commit that froze each, and predictions of the world's
own behaviour filed before the low and high runs. No supplier arm has been run against it; the
company in these runs is the shipped one, whose only payment lever that reaches these mechanisms is
the SLC 27.8 repayment-plan offer. Calibrate only against published evidence, never a supplier
result.

## The mechanisms, frozen

Every one is a household answering a stimulus it experiences. None names a supplier policy. Every
toggle defaults to off, so the shipped book is byte-identical (40 founders, budget 0, origin
`25e92033b` vs the tree carrying all four at default: `book_diff` IDENTICAL BOOK).

| # | Stimulus | Response | Toggles (low-high), default off | Frozen at | Knowledge |
|---|---|---|---|---|---|
| 1 | an arrangement offer: repayment plan (instalment named by the household, or by the supplier), lower payment for a period, pause | agree or decline (flat); a plan then kept to completion (cure) or broken in its first six instalments with share x affordability ratio, or at an income shock into HIGH stress; a lower payment cuts failures by elasticity x cut (no effect under MMI's 5.9% token cut); a pause ends in a failed first collection for a still-stretched household | `plan_take_up_share` 0.32-0.53; `plan_break_share` 0.45-0.65; `plan_weeks_to_recover` 46-96; `plan_lower_payment_failure_elasticity` 0.25-1.0; `plan_pause_resume_failure_share` 0.09-0.40 | `f853cd2ff` | `domestic_repayment_plan_take_up_and_keep_rates.md`, "The world's answer to an offer" |
| 2 | a contact about a missed payment (`arrears_contact`) within 30 days of the miss | woken with share x delay weight (1 to day 5, 2/12 to day 10, 0.8/12 to day 30); woken and able: pays the bill by day 30 (its later lump withdrawn); woken and HIGH stress: gets in touch, cannot pay | `early_contact_woken_payer_share` 0.04-0.29 | `9ca9624fc` | same page, "Early contact: the world's answer" |
| 3 | its own reasons (distrust, control, account closure); an offer of a prepayment meter for debt; a meter changed for debt | cancels its DD (monthly hazard from the annual share x stress relativity), pays by hand after; agrees a PPM offer or not; on a debt PPM, repays GBP 6.01/4.40 a week | `method_own_reasons_cancel_share` 0.005-0.02; `method_prepayment_offer_take_up_share` 0.30-0.40 | `1cadad9b5` | `gb_payment_method_migration_rates.md`, "The household's own payment-method acts" |
| 4 | told a new DD amount; offered a collection date nearer payday | a rise over 15% answered as a DD4b shock (cancel / fail more / complain, DD4b's toggles); a stretched household whose date precedes its income (53%) takes the date and fails less from then on | `dd_date_alignment_failure_reduction` 0.10-0.36 (plus DD4b's three, frozen at `d2dddf804`) | `3a35fbc8f` | `what_bill_shock_is.md`, "A changed amount or date (DD4c)" |

**What the world still does not do (GAPs, carried):** payment channel is drawn once and not coupled
to income, tenure or vulnerability (no crosstab reached); no household re-mandates; no
self-disconnection is drawn on a debt PPM; the pay-or-heat state is not in the run; take-up does not
vary with means or offer shape; a fall in a DD draws no response; a pause's own months, an inbound
contact and an offered date have no seam yet. Every GB flow that would calibrate these (Ofgem SOR
Q3.1/3.3/3.6-3.27, ADDACS 1 by sector, Pay.UK returns by date alignment) is collected and unpublished.

**What the book can and cannot exercise today.** The shipped company makes only the SLC 27.8
repayment-plan offer. So on this book mechanism 1's repayment-plan leg and mechanism 3's own-reasons
cancellation can fire; the lower payment, pause, early contact, prepayment and date-change responses
are reachable only through a supplier that sends those stimuli, and their controls prove they can
fire at unit level (`tests/simulation/test_plan_offer_response.py`, `test_early_contact_response.py`,
`test_payment_method_dynamics.py`, `test_dd_change_response.py`).

**Why a world lane touched two files outside `simulation/`, and what it did not add.**
`company/interfaces/sim_interface.py` is the seam, and the only change there is what crosses it: the
offer the household is told (an optional `offer` shape on `answer_plan_offer`), passed to the world,
and the world's own book passed back into `get_plan_instalments`. The answer that returns is the
same three observables as before. `background/live_payment_triad.py` is the harness that draws each
household's payment; it now notes the household's stress tier on the world's plan book, applies a
household's own lower-payment or pause agreement to its own collection, and queues the early-contact
check. No supplier policy was added anywhere: no rule for when to offer, contact, stop a DD, move a
date or fit a meter.

## Predictions, filed before any low or high run of mechanisms 2-4 (2026-10-12 04:49Z)

Book: 40 founders, settlement budget 0, `/var/tmp/m_scale.py` through `wp_run.py` (each mechanism's
module attribute set to the register's `low` or `high` row; `default` touches nothing). Exposure,
from the step-1 runs of the same book: 55 billed accounts (fuel legs), 190.7 account-years, 15 failed
collections over the run, the supplier's SLC 27.8 step reached 94 times with every offer
unanswered and 42-44 times once offers are answered (an agreement ends a journey).

**Not blind, said first.** The plan-offer figures below were SEEN at step 1's low and high runs
before this was written (low: 12 of 42 agreed, 7 completed, 4 broken own, 1 broken by an income
shock; high: 23 of 44 agreed, 6 completed, 15 broken own, 1 shock, 1 running). They are repeated as
the prediction the freeze must reproduce: the plan module is unchanged since, so the same seed must
give the same counts. Everything else is predicted blind.

| Quantity | Low | High | Reasoning |
|---|---|---|---|
| Offers answered / agreed | 42 / 12 | 44 / 23 | reproduced from step 1 (not blind) |
| Agreed plans completed / broken own / broken by income shock / running | 7 / 4 / 1 / 0 | 6 / 15 / 1 / 1 | reproduced from step 1 (not blind) |
| Later lumps withdrawn for planned debt; paid twice | 2; 0 | 4; 0 | reproduced (not blind) |
| Own-reasons mandate cancellations (whole run) | 1 (range 0-3) | 3 (range 1-7) | ~110 DD household-years (72% of 190.7 leg-years, dual-fuel legs sharing a household) x share x a mean stress relativity of about 1.5 on a book with only 15 failed collections in ten years (mostly LOW stress): 0.8 at low, 3.3 at high |
| ... per 1,000 DD household-years | ~9 (0-27) | ~27 (9-64) | the same counts over ~110 |
| Switches to paying by hand | = cancellations | = cancellations | every cancellation pays on receipt thereafter; no re-mandating |
| Extra failed collections ("instruction cancelled") | = cancellations | = cancellations | one return in the cancelling month each |
| Early-contact responses (contacted / woken / paid) | 0 / 0 / 0 | 0 / 0 / 0 | no supplier in the run sends an `arrears_contact` |
| Date-change responses | 0 | 0 | no supplier offers a date change |
| Prepayment offers answered / meters changed for debt | 0 / 0 | 0 / 0 | no supplier makes the offer or pursues a warrant |
| Lower-payment and pause agreements | 0 | 0 | the company's desk sends only the SLC 27.8 repayment-plan offer |
| P&L bad debt vs default (440.85) | within +/- GBP 50 | within +/- GBP 150 | plans do not reach the arrears engine (seen at step 1: unchanged); a cancellation adds one returned month, most of which re-present or settle later |
| Total net vs default (31,124.47) | within +/- GBP 100 | within +/- GBP 300 | the same |

**What would refute the design rather than the numbers:** any non-zero count in a row predicted 0
(a stimulus reaching the world that no supplier sends); a plan count that differs from step 1 (the
plan module moved under steps 2-4); more than 7 cancellations at high (the stress relativity is
acting on far more stretched DD households than this book shows).

### One-variable follow-up, prediction filed before the run (2026-10-12, after the high result was seen)

At high the plan counts moved from step 1 (44 offers / 23 agreed -> 55 / 29) although
`plan_offer_response.py` and the seam are byte-identical between `f853cd2ff` and `3a35fbc8f`. Two
things changed at once (the four own-reasons cancellations, and origin's other commits between the
two runs), so I cannot yet say which. Prediction: the frozen tree at high with ONLY the plan basis
switched (`high-plansonly`) gives step 1's 44 / 23 / 6 / 15 / 1 / 1 exactly, so the extra offers
are journeys opened by the cancellations' returned and pay-on-receipt bills.

## Result

*Runs at the frozen head `3a35fbc8f`, 40 founders, budget 0, through `wp_run.py` (2026-10-12). The
predictions above are unedited; `sha256` of the first block as filed:
`b9985b061629671d2d26b98ef3b9ce43f76befa17afc0c3f30bf4d1206f58455`.*

**Default:** `book_diff` against origin `25e92033b`: IDENTICAL BOOK. Every new count zero; 94 offers
answered None.

| Quantity | Predicted low | Result low | Predicted high | Result high |
|---|---|---|---|---|
| Offers answered / agreed | 42 / 12 | **42 / 12** (29%) | 44 / 23 | **55 / 29** (53%) -- REFUTED in the counts, not the share; see the one-variable run |
| Completed / broken own / income shock / running | 7 / 4 / 1 / 0 | **7 / 4 / 1 / 0** | 6 / 15 / 1 / 1 | **7 / 19 / 1 / 2** |
| Later lumps withdrawn; paid twice | 2; 0 | **2; 0** | 4; 0 | **5; 0** |
| Own-reasons cancellations | 1 (0-3) | **1** (MODERATE stress) | 3 (1-7) | **4** (all LOW stress) |
| ... per 1,000 DD household-years | ~9 | **~9** | ~27 | **~36** |
| Switches to paying by hand | = cancellations | 1 household; 2 bills on standard credit | = cancellations | 4 households; 89 bills on standard credit |
| Extra "instruction cancelled" returns | = cancellations | **+1** (4 -> 5) | = cancellations | **+4** (4 -> 8) |
| Early contact contacted / woken / paid | 0 / 0 / 0 | **0 / 0 / 0** (9 checks queued, no contact sent) | 0 / 0 / 0 | **0 / 0 / 0** (12 queued) |
| Date-change, prepayment, lower-payment, pause | 0 | **0** | 0 | **0** |
| Bad debt vs 440.85 | +/- 50 | **473.41** (+32.56) | +/- 150 | **562.23** (+121.38) |
| Total net vs 31,124.47 | +/- 100 | **31,091.91** (-32.56) | +/- 300 | **31,003.09** (-121.38) |

**The one refutation, attributed by the one-variable run.** At high, with ONLY the plan basis
switched, the frozen tree gives **44 offers / 23 agreed / 6 completed / 15 broken own / 1 shock / 1
running, 4 lumps withdrawn, bad debt and net unchanged** -- step 1 exactly, as the follow-up
predicted. So the 11 extra offers at high come from the four own-reasons cancellations: their
returned and pay-on-receipt bills open collections journeys that reach the SLC 27.8 step. That is
the mechanisms coupling as built (a household that stops its DD falls behind and is offered a plan),
not the plan module moving. The whole movement in bad debt and net is the cancellations: plans do
not reach the arrears engine's P&L (a named limit from step 1).

**What this book says about the world, and what it cannot.** Take-up lands at the toggle (29% at
0.32, 53% at 0.53); break shares among agreed plans are 42% at low and 69% at high against
0.45/0.65 set, within what 12 and 29 plans can resolve. The cure share is 58% (low) and 24% (high)
of agreed plans. 40 founders give about a dozen to thirty plans and one to four cancellations: every
figure here is a count, not a rate, and none should be read as calibrated. Nothing was tuned to
these results, and no supplier arm has yet been run against this world.

## Re-freeze, 2026-10-12: one payment truth -- predictions filed before the low/high runs

Filed at 2026-10-12T10:15Z, before any low or high run with `world_payment_truth.UNIFIED` on. Seen before
filing: the frozen runs above (plans and cancellations at low/high, engine-drawn bad debt) and ONE
unified run at default (bad debt 440.85 -> 161.08, net 31,124.47 -> 31,404.24; 1,497 bills taken
from the triad, none drawn by the engine, 6 repayment rows). Nothing at low or high with the switch
on has been run. Book: 40 founders, budget 0, the frozen head `62596685a` (unified truth landed at `62596685a`), each setting plus `UNIFIED`.

| Quantity | Low | High | Reasoning |
|---|---|---|---|
| Offers / agreed / completed / broken own / shock / running | 42 / 12 / 7 / 4 / 1 / 0 | 55 / 29 / 7 / 19 / 1 / 2 | unchanged from the first freeze: the switch acts only after the run, in the P&L, so no household's behaviour moves (not blind, predicted to reproduce exactly) |
| Own-reasons cancellations | 1 | 4 | the same reason |
| Bills drawn by the engine (fallback) | 0 | 0 | every bill matched at default |
| Repayment rows | ~80 (40-150) | ~70 (30-150) | ~6 settlements plus instalments of the plans that cover a still-unpaid bill: about 7 completed plans x ~10 instalments at low; at high fewer completed and many partial |
| Bad debt (unified default 161.08) | ~150 (90-220) | ~300 (180-450) | low: completed plans repay a few leavers' bills, but two lumps they replace would have repaid anyway, so near-neutral; high: four cancellations add returned months (about +120 under the engine at high, of which some re-present or settle later), and broken plans withdraw lumps that would have repaid (5 withdrawn) while repaying only part, so bad debt RISES |
| Total net (unified default 31,404.24) | ~31,415 (31,345-31,475) | ~31,265 (31,115-31,385) | revenue unchanged; net moves against bad debt one for one |

**What would refute the design rather than the numbers:** any change in the plan or cancellation
counts (the switch reached the run); a fallback count above zero; bad debt at high BELOW low's (a
broken plan repaying as if kept, or a withdrawn lump still counted as repaid).

*Filing note: the block above was hashed at filing (`7397075c...`) before the frozen commit
existed; its only edit since is the head named in its "Book:" line, after `62596685a` landed and
before either run (`e5325669...`).*

## Result (re-freeze)

*Runs at `62596685a`, 40 founders, budget 0, `UNIFIED` on, 2026-10-12. Predictions above unedited.*

| Quantity | Predicted low | Result low | Predicted high | Result high |
|---|---|---|---|---|
| Offers / agreed / completed / broken own / shock / running | 42 / 12 / 7 / 4 / 1 / 0 | **42 / 12 / 7 / 4 / 1 / 0** | 55 / 29 / 7 / 19 / 1 / 2 | **55 / 29 / 7 / 19 / 1 / 2** |
| Own-reasons cancellations | 1 | **1** | 4 | **4** |
| Bills drawn by the engine | 0 | **0** (1,497 from the triad) | 0 | **0** (1,497) |
| Repayment rows | ~80 (40-150) | **40** (at the floor) | ~70 (30-150) | **85** |
| Bad debt (unified default 161.08) | ~150 (90-220) | **131.28** | ~300 (180-450) | **229.46** |
| Total net (unified default 31,404.24) | ~31,415 (31,345-31,475) | **31,434.04** | ~31,265 (31,115-31,385) | **31,335.86** |

Every figure inside its range; no design refutation (counts unchanged, no fallback, high above
low). Two directions I had wrong in size: at low the kept plans repay MORE than the lumps they
replace (bad debt falls 30, where I predicted near-neutral), and at high the rise is smaller than
predicted (+68, not +140), so the broken plans' partial repayments offset more of the withdrawn
lumps than I expected. Repayment rows ran above my high guess's centre and at low's floor: plan
counts are a dozen to thirty, and instalments per plan vary more than "about ten".

**What this makes true.** With the switch on, a kept plan lowers realised bad debt and a broken
one, or a cancellation, raises it, through the same record the supplier's days-behind come from.
Compared like for like (each against unified default 161.08): low -29.80, high +68.38. Under the
engine's own draw the same settings moved bad debt +32.56 and +121.38, with plans contributing
nothing. **The freeze now stands on `62596685a` with `UNIFIED` on as part of the frozen world for
any debt-engine grading; the shipped default stays off until the seat flips it** (it moves the
shipped book: 440.85 -> 161.08 bad debt at default on this book).
