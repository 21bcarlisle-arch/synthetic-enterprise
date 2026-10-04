# The world now knows an agreed plan, so the arrears it covers are not paid twice

**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey` · **Claim:** `world-knows-plan-cash` (Lane 0 delivery)

## Premise, re-measured at draw

The draw flagged a live claim under this item's own id. The only seat process in `ps` was this
invocation's executor, and no rival `surgical_land` was running, so the claim is this draw's own
write. The cited commit `2b5c8bf7e` is the company-side half (plan cash posts to the ledger); open
item 1 of `SEAT_FINDING_PLAN_INSTALMENTS_NOW_POST_TO_THE_LEDGER_AND_A_REPAID_PLAN_FREES_THE_ACCOUNT_2026-10-04.md`
was still open at HEAD: nothing world-side read an agreement.

## The double payment, made concrete

The item said the household's "ordinary payments may pay the same arrears again". Following the
thread, the route is specific: `payment_behaviour_source.later_settlement_date` gives an unpaid
domestic bill a lump repayment at due + 28 days + 3 months (35% of failed bills) or + 22 months
(15%), and `background/live_payment_triad.py` queues that cash to cross on its day. The
residential ladder offers a plan at 28 days overdue -- the same day the lump's clock starts. So a
household that agreed a plan at day 28 would pay the bill through the instalments AND as a lump
three months later. Ordinary payments of later bills are not the problem: they pay later bills.

## What was built

- `simulation/plan_offer_response.HouseholdPlanBook`: the world's own record of agreed plans
  (account, date). `answer_plan_offer(..., agreements=)` records a yes on it.
- `LiveSimInterface(household_plans=)` passes the book to the world's answer. Nothing company-side
  reads it.
- `LivePaymentTriad` owns one book. Before a queued lump crosses, it walks that account's journey
  to the day before the lump (inside the two bounds `record_period` already keeps: the account's
  latest posted due date and the date the run has lived through), so an offer due by then has been
  answered. A lump for a bill due before an agreement dated before the lump is withdrawn from both
  companies (`settlements_withdrawn`). Every lump that does cross is kept, and
  `settlements_crossed_despite_a_plan` counts any that a plan agreed earlier covers -- the residue
  the walk exists to keep at zero, counted rather than assumed.
- Named in the module: a broken plan does not hand the debt back to the lump route (conservative),
  and the world does not end a plan -- only the company's plan book stops reading instalments.

Inert live: every answer is still None, so the book stays empty and nothing is withdrawn.

## Pre-registration (written before the run)

Population: residential, high stress, sourced basis injected in the test (take-up 1.0, keep 1.0,
instalment GBP 25), lumps on as live.

1. With the change, MONTHLY bills: `settlements_withdrawn > 0`, `settlements_crossed_despite_a_plan == 0`.
2. Mutation, withdrawal removed: `crossed_despite_a_plan > 0` (the double payment is real in this
   population, not hypothetical).
3. Mutation, pre-walk removed, MONTHLY bills: I predict it does NOT fire -- the ordinary walk lags
   delivery by at most one bill cycle, shorter than the three-month lump window, so the agreement is
   already decided. If so it is an equivalence ON MONTHLY BILLS, not a missing test.
4. Mutation, pre-walk removed, QUARTERLY bills (Jan/Apr/Jul/Oct 28): I predict it fires -- the lump
   for the January bill (~May 25) crosses at the July record before the walk to April decides the
   March offer, so `crossed_despite_a_plan > 0`.

## Result

First build (a pre-walk to the day before each lump, crossing the lump straight after), 40
households, 2020, run to 2021-12-31:

| | agreed | lumps crossed | withdrawn | crossed despite a plan |
|---|---|---|---|---|
| no withdrawal, monthly | 58 | 62 | 0 | **17** |
| no withdrawal, quarterly | 62 | 22 | 0 | **16** |
| pre-walk, monthly | 59 | 52 | 10 | **7** |
| pre-walk, quarterly | 68 | 11 | 11 | **5** |
| pre-walk removed, monthly | 59 | 52 | 10 | 7 |
| pre-walk removed, quarterly | 62 | 19 | 3 | 13 |

- Prediction 2 held: the double payment is real, 17 of 62 lumps on monthly bills.
- Prediction 3 held: on monthly bills the pre-walk changed nothing (same row with and without).
- Prediction 4 held: on quarterly bills it fired (13 → 5).
- **Prediction 1 was WRONG.** I predicted 0 crossed despite a plan; it was 7 on monthly and 5 on
  quarterly. The cause: the walk may go no further than the account's latest posted due date, and a
  lump falls in the month after it, so an offer in that gap was still undecided when the cash
  crossed. Walking further would read a ledger whose next bill is not yet posted.

The fix that landed holds the lump instead. A lump whose day has come waits on its account's hold,
valued on its own day, until a later bill extends how far that account can be walked. Then it is
settled oldest-first, each one after a walk to the day before it. A reader that needs the ledger
now (`arrears_state`, `receivable` for their account; `default_belief_rate`, `detection_cells`,
`measure` for all accounts) forces the held lumps up to its date across unwalked. Any of those
that a later agreement covers is counted, not hidden. With the hold:

| | agreed | lumps crossed | withdrawn | crossed despite a plan |
|---|---|---|---|---|
| monthly | 59 | 45 | 17 | **0** |
| quarterly | 68 | 6 | 16 | **0** |

Crossed plus withdrawn adds up to the no-withdrawal count on both cadences (62 and 22), so the hold
loses no lump. It only routes some through the plan.

Control: `tests/background/test_the_triad_does_not_pay_a_planned_debt_twice.py`. All seven
mutations went red: no withdrawal, no walk before a lump, no hold (cross unwalked), a yes not
recorded, the window open at either end, and the seam dropping the book.

## What it leaves open, named

1. **A forced crossing is unwalked.** A reader at a renewal forces lumps dated after the account's
   latest due date across before an offer in that window is decided. It is small, because an offer
   comes 28 days after its bill and the lump 3 or 22 months after that. It is counted live on
   `settlements_crossed_despite_a_plan`. **Published 2026-10-04:** the run summary carries
   `later_settlements` (`delivered`, `withdrawn`, `crossed_despite_a_plan`), read after the
   end-of-run forced crossing; `test_a_live_run_publishes_what_became_of_the_later_lump_settlements`
   holds it. Under the published basis (no plan agreed) the last two are 0 by construction, so the
   residue is only live once a sourced take-up rate lands. Printed at a run to 2017-06-30: `{delivered: 13, withdrawn: 0,
   crossed_despite_a_plan: 0}`. Unguarded: reading the counters BEFORE `collections_journeys` in
   the summary would drop the end-of-run forced crossings; on the published basis that is an
   equivalence for the two plan counters (both 0), and the live control does not pin `delivered`.
2. **The world does not end a plan, and a broken plan does not return the debt to the lump route**
   (module simplifications 2 and 3). Both are conservative. Neither moves cash twice.
3. The company-side open items 2 and 3 of the predecessor finding still stand: a plan's debt is
   fixed at the offer, and instalments are read only at evaluation dates.

Still inert live: `PUBLISHED_BASIS` answers None, so the book stays empty
(`test_the_published_basis_withdraws_nothing`).
