# C32's tenth Expert Hour, in operation: one routed action of three is exercised, and the world's count missed an offer

**Fate (2026-11-15):** RESULT. **C32 stays at level 2**, so no level move goes through the gate.
The question was whether the gate had ever been tested in operation. On a 2016 run the answer is:
for the Consent offer, yes; for the debt objection and recovery through the meter, no.

## How it was run

- **Precondition.** W2_43 (55faf525c), C36 (a3efd1e1a) and C37 (4f68e139c, 426967f49) are
  ancestors of origin/main. W2_44 (4d2da3fb8) is too, so check (d) has a live Breathing Space
  caller. In a 2016 window, though, the world draws none: the scheme starts 4 May 2021.
- **The run.** `simulation.run_phase2b.main(report_end="2016-12-31")` on HEAD 41734bbe71, the
  window `test_collections_journey.py`'s live fixture uses. Instrumentation wrapped `may_take` at
  both import sites, every `LiveSimInterface` debt door, `request_debt_objection` and
  `raise_objection`. Nothing else changed. Probe script: `/tmp/c32p/probe.py`, not kept.
- **The reader.** A fresh general-purpose agent. Its one tool call was a Read of the packet, and it
  saw nothing else. The packet held the `blind_review --packet` text with `--plain-words`, then
  `winter_moratorium.py` lines 277-612 (the actions, grounds, checks, `ENFORCEMENT_TABLE`,
  `DEBT_STEP_CENSUS` and `may_take`, with pass and item references stripped), then the run's debt
  paths. It never saw the ninth pass's findings or commons §5's narrative.
- **Grades the seat checked.** Every claim below was re-measured against the code or the run
  before it was accepted.
- **The ledger.** The battery is recorded in `sanity_adjudication_ledger.json` with
  `independence: false`. It is in the shared tree and not committed here, because that file carries
  about 2,000 lines of other lanes' uncommitted work.

## What the run shows

- **Scale.** 69 domestic and SME collections journeys. There were 6 `may_take` calls, all on
  CONSENT_PPM_OFFER: 5 permitted, 1 refused. The refusal was ACC-SYN-2016-360, a discloser whose
  answers are all unanswered, refused on 27.6(a)(iii).
- **Debt objection.** One request (SYN-2016-002, 29 Dec) stopped at "no debt outstanding more than
  28 days" before the gate. No objection was raised.
- **Meter recovery.** Never asked. Every Consent move returned "take-up share is off", so no meter
  moved.
- **The world's concealing count.** It was printed with `offers: 4`, but the desk made 5 offers.

## The seat's named checks

| Check | Grade | The record that decides it |
|---|---|---|
| (a) every census action goes through `may_take` or is unrouted with its reason | **Pass, on what was reached** | All 6 Consent decisions asked the gate, and the 5 world move requests each follow a permit. The objection request stopped before the gate on the debt filter and took no action, so that is not a bypass (the reader graded it one; rejected). `statement_of_account` is SME, outside the domestic census (the reader flagged it; rejected for C32). |
| (b) the permit and refuse legs are each taken | **Fail for 2 of 3 routed actions** | Consent: 5 permits and 1 refusal. Debt objection: the gate was never reached. Meter recovery: never asked. |
| (c) the concealed-Consent-offer count is printed | **Was failing: fixed here** | It counted 4 of 5. The cause is below. |
| (d) a moved meter takes no deduction under a hold from the day before the read | **Cannot tell in operation** | No meter moved, and Breathing Space is impossible in 2016. It is proven in unit tests only, and the own-hold leg can never engage live (class 2 below). |
| (e) the cold-read trade checks | **Fail on meter identity; partly on the payment method** | One debt meter per billing account, recovered at the electricity rate (`plan_offer_response.py:238`), so a dual-fuel household has one meter. The payment method is dated on the objection path (`_book_method_of(.., request_day)`), but `EnforcementCase` has none, so a Consent offer cannot be refused because the household is already on prepayment. Read repetition: `rows[read:]` is idempotent on a stable prefix. A same-day second advance that first sees a moratorium shrinks the prefix (seat reading, not exercised). |

**The reader's verdict:** "Would you accept this gate is tested IN OPERATION? No." The seat agrees
for two of the three routed actions.

## Fixed in this tick

**The world's count was taken before the desk's last action.**
- **Cause.** `consent_offers_to_concealing_households` was computed at `_psr_registrations`, before
  `collections_journeys(effective_end)`. That call's end-of-run advance made ACC-SYN-2016-005's
  10-26 offer after the count. `later_settlements` already orders itself after the journeys for
  exactly this reason.
- **Fix.** The key now sits after the journeys.
- **Control.** `test_the_world_counts_every_consent_offer_the_company_made` checks that the world's
  `offers` equals the company's `prepayment_offered` stages, on the existing live fixture.
- **It can fail.** The pre-fix ordering gave 4 against 5 on this same run.

## New classes, each with an owner

These are filed in
`docs/staging/WORKER_FINDING_C32_TENTH_PASS_THE_GATE_IS_UNEXERCISED_ON_TWO_OF_THREE_LIVE_ACTIONS_2026-11-15.md`.

1. **Two routed actions are unexercised in operation.** Owner: C32. Done when a probe with take-up
   on, over a window past 4 May 2021, shows both legs of DEBT_OBJECTION and METER_RECOVERY. The
   toggle is a curriculum value, so the probe sets it in-process and does not change the named world.
2. **The own-hold column is covered on paper and hard-wired off live.** Owner: C32. The desk's
   `own_holds` is None in the run, and `request_debt_objection` never passes `own_hold`. So no live
   path can engage the column, on all three routed rows.
3. **One debt meter per billing account.** Owner: W2 (the meter book) with C32 (e). It is stated
   only in a code comment, not on a knowledge page.
4. **Plan re-offers come every 2-5 days.** Owner: the collections desk (D lane). ACC-SYN-2016-012 was
   offered 12 plans in 2016, with pairs two days apart (07-15/07-17, 09-16/09-18). The cause is
   unestablished; per-fuel bills on one account is the first hypothesis.
5. **An arrangement offered with no amount satisfies the 27.8 ground.** Owner: C32. All 69 offers
   carry `instalment_gbp: null` while the world's take-up is off. The gate reads only that an offer
   was made.
6. **A Consent offer cannot be refused for being already on prepayment.** Owner: C32. See (e).
7. **Unanswered S&RP answers are reported as a "negative" finding.** Owner: C32. The refusal is
   right but its words are not: `_suitability_check` prints NOT_SUITABLE over evidence that reads
   "unanswered".

**Rejected, with the reason:**
- The objection "bypass": the filter precedes the gate, and no action was taken.
- `statement_of_account`: an SME step. Breathing Space for sole-trader debts is a separate,
  unresearched question.
- "Holds are undated": the world draws no Breathing Space before 2021, and the own hold is policy.
- PSR codes not read at the Consent offer: already a GAP cell.
- Unrouted actions never asked: `UNROUTED_ACTIONS` says so.

NEXT: C32_one_obligation_one_vulnerability_scorer
