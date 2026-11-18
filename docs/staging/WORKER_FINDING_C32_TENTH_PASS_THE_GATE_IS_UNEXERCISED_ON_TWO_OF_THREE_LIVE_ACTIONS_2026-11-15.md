**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 3 · **Atom:** `C32_one_obligation_one_vulnerability_scorer`

# The enforcement gate is unexercised on two of its three live actions, and its own-hold column is wired off (2026-11-15)

Found by C32's tenth blind pass, on a 2016 live run. The full record is
`docs/staging/records/WORKER_RESULT_C32_TENTH_EXPERT_HOUR_THE_GATE_IS_TESTED_IN_OPERATION_ON_ONE_ACTION_OF_THREE_2026-11-15.md`.

## What was measured

On `main(report_end="2016-12-31")`, `may_take` was asked 6 times, all on the Consent offer
(5 permitted, 1 refused). The debt objection never reached the gate: its one request stopped on
the 28-day filter. Meter recovery was never asked, because no meter moves while
`method_prepayment_offer_take_up_share` is 0.

## The classes, in order of what they block

1. **Unexercised in operation** (owner C32). The DEBT_OBJECTION and METER_RECOVERY legs have only
   unit evidence.
   - *Done means:* a probe that sets take-up on in-process, over a window that includes 2021-05-04
     onwards, logs both legs of both actions.
   - *Constraint:* the curriculum value is not changed.
2. **The own-hold column is wired off** (owner C32).
   - The live desk's `own_holds` is None, so `collections_journey.py:864` and `:946` always pass
     False.
   - `company/interfaces/transfer_objection.request_debt_objection` never passes `own_hold` to
     `decide_debt_objection`, which defaults it to False.
   - So a COVERED cell on all three routed rows can never refuse live.
   - *Either:* wire the register.
   - *Or:* mark the column unrouted, with the reason, as `UNROUTED_ACTIONS` does for actions.
3. **One debt meter per billing account** (owner W2 meter book, with C32's check (e)).
   - `simulation/plan_offer_response.py:238` recovers a dual-fuel account's debt at the electricity
     rate on one meter.
   - The knowledge page does not state this.
   - Owed: name it in commons §5 as a simplification, or key the meter book by supply point.
4. **Plan re-offers 2-5 days apart** (owner: the collections desk, D lane).
   - ACC-SYN-2016-012 had 12 plan offers in 2016, including 07-15/07-17 and 09-16/09-18.
   - The trigger reads "a further bill missed".
   - Hypothesis, not yet tested: per-fuel bills on one account each count as a miss.
   - Contact frequency is a conduct question (SLC 0, the treating-customers-fairly standard).
5. **An offer of nothing satisfies 27.8** (owner C32).
   - The CONSENT_PPM_OFFER check reads `arrangement_offered` as a boolean.
   - All 69 live offers carry `instalment_gbp: null` while the world's take-up is off.
   - *Fixed 2026-11-15 (worker tick):* the column now needs an offer the household answered
     (agreed or declined). An unanswered offer, or a desk with no seam, withholds the Consent offer
     on `NO_ARRANGEMENT_OFFERED`, which now names the reason (27.6(a)(ii), 27.8). Live on the
     shipped world, every Consent offer is withheld on this ground. The both-ways live control runs
     a second 2016 run with plan answers on in-process (`high` row; curriculum unchanged). This
     partly meets item 1 for the Consent action only. Commons s.5, "The 27.8 column reads an
     ANSWERED offer". GAP: how many unanswered attempts make an offer "made" is not read.
6. **No payment method on `EnforcementCase`** (owner C32). A Consent PPM offer cannot be refused
   because the account is already on prepayment.
7. **"Negative" printed over unanswered evidence** (owner C32). In `_suitability_check`, the refusal
   is correct but the reason misdescribes it.

Fixed in the same tick: the world's concealing count was taken before the journeys' end-of-run
advance (4 counted, 5 made). It now comes after the journeys, under a control.

NEXT: C32_one_obligation_one_vulnerability_scorer

## Class 2, pre-registered before the probe ran (delivery seat, 2026-11-16)

The probe is `main(report_end="2016-12-31")` on the shipped world, with `may_take` counted per
action, per verdict and per refusing ground. Nothing else is changed. The class-2 change does not
alter any live input, so the prediction holds both before and after it.

- **CONSENT_PPM_OFFER:** asked once or more. Every ask is refused. Each refusal names
  `slc_27_5_to_27_8_ability_to_pay`, because the item 5 fix means an unanswered offer is no 27.8
  offer and plan answers are off on the shipped world. 0 permitted.
- **DEBT_OBJECTION:** asked 0 times. Its one request stops on the 28-day filter before the gate.
- **METER_RECOVERY:** asked 0 times, because no meter moves while take-up is 0.
- **`own_hold_winter_moratorium`:** named in 0 refusals on every action.

**Result, beside the prediction** (`main(report_end="2016-12-31")`, origin `d28822a71e` plus this
change, which adds only a dict that no live path reads):

| action | predicted | printed |
|---|---|---|
| `consent_ppm_offer` | asked at least once, all refused on 27.8, 0 permitted | asked 6, refused 6, all naming `slc_27_5_to_27_8_ability_to_pay`; 1 also names `slc_27_6_a_iii_safe_and_practicable`; 0 permitted |
| `debt_objection_on_switching` | asked 0 | asked 0 |
| `recovery_through_the_meter` | asked 0 | asked 0 |
| the four unrouted actions and support | asked 0 (not stated before the run) | asked 0 |
| `own_hold_winter_moratorium` | named in 0 refusals | named in 0 |

The prediction held. The second ground on one Consent refusal is the S&RP finding, which the
prediction did not rule out. Live, the gate is now one-sided: no Consent offer is permitted on the
shipped world, so the permit leg in operation rests on item 5's second run (plan answers on,
in-process). The probe script is at `/tmp/c32p2/probe.py`; it is not kept.

## Class 2, closed as unrouted with its reason (delivery seat, 2026-11-16)

- **Does a real supplier keep a register of its own holds? Yes.** A dated or open-ended lock,
  with a reason, sits on the contract account, and the dunning run skips the account (SAP IS-U
  dunning lock).
- **What is missing here is the policy that places a hold.** No company decision writes a
  `MoratoriumRecord`. Wiring an empty register would read as live and refuse nothing. So
  `UNROUTED_GROUNDS` in `company/billing/winter_moratorium.py` lists `own_hold_winter_moratorium`
  with that reason, as `UNROUTED_ACTIONS` lists actions.
- **Knowledge first.** The commons page has a new s.5 note, "The own-hold column is unrouted".
  **GAP:** when a real supplier places a discretionary hold is not published.
- **Controls** (`tests/company/billing/test_an_unrouted_ground_has_no_writer.py`):
  1. A ground is listed unrouted exactly when no company code writes it. Mutation-proven both
     ways: the row deleted with no writer reds; a planted writer while still listed reds.
  2. The desk's meter-recovery route and `decide_debt_objection` each permit with no hold and
     refuse with a real register holding one. Mutation-proven: the desk passing `own_hold=False`
     reds.
- **No live input changed,** so no book moves. That keeps faith with "land after the D5-fixed
  book publishes": that book still changes one thing.
- `method_prepayment_offer_take_up_share` is not touched.

## Classes still open, with owners (2026-11-16)

| class | what | owner |
|---|---|---|
| 1 | DEBT_OBJECTION and METER_RECOVERY unexercised in operation (Consent half-met by item 5) | C32 |
| 3 | one debt meter per billing account, not on a knowledge page | W2 meter book, with C32 check (e) |
| 4 | plan re-offers 2-5 days apart | collections desk, D lane |
| 6 | no payment method on `EnforcementCase` | C32 |
| 7 | "negative" printed over unanswered evidence in `_suitability_check` | C32: **closed 2026-11-18**, below |

Closed: 2 (unrouted, above) and 5 (2026-11-15).

## Class 1, pre-registered before the probe ran (delivery seat, 2026-11-16)

The probe counts `may_take` per action, verdict and refusing ground on `main(report_end=E)`, with
two world settings switched to the register's `high` row in-process: `plan_offer_response.BASIS`
(plan take-up 0.53) and `payment_method_dynamics.STRENGTHS` (prepayment take-up 0.4). The
curriculum value is not touched. Two windows: E = 2016-12-31, and E = 2021-12-31, the first year
end after Breathing Space comes into force on 2021-05-04.

| action | 2016-12-31, predicted | 2021-12-31, predicted |
|---|---|---|
| `consent_ppm_offer` | asked; both permitted and refused (as item 5's control) | both |
| `recovery_through_the_meter` | asked at least once; all permitted (no Breathing Space before 2021, and I expect no 27A report this early) | asked; permitted at least once; refused at least once, on 27A or Breathing Space |
| `debt_objection_on_switching` | asked 0 (on the shipped world its one request stops on the 28-day filter) | asked at least once; permitted at least once; refused 0 (Breathing Space × a switch × debt over the de-minimis is rare) |
| `own_hold_winter_moratorium` | named in 0 refusals | named in 0 refusals |

If a leg is still not taken at 2021-12-31, it is a finding about how far the world reaches. I do not
lengthen the window until I find a leg.

**Result for 2016-12-31, beside the prediction** (origin `57158c97c5`; wall clock 42 min, CPU 4.7 min):

| action | predicted | printed |
|---|---|---|
| `consent_ppm_offer` | permitted and refused | asked 2: 1 permitted, 1 refused on `slc_27_5_to_27_8_ability_to_pay` |
| `recovery_through_the_meter` | asked at least once, all permitted | asked 1 (ACC-SYN-2016-005, on 2016-12-31): permitted |
| `debt_objection_on_switching` | asked 0 | asked 0 |
| `own_hold_winter_moratorium` | named in 0 refusals | named in 0 |

The prediction held. Meter recovery's PERMIT leg is now exercised in operation, on one account.
Its refuse leg and both debt-objection legs wait for the 2021-12-31 window, which is running. The
Consent rung is asked 2 times here, against 6 on the shipped world: once plans are answered, some
accounts cure before day 90. The probe script is at `/tmp/c32c1/probe.py`. It wraps
`winter_moratorium.may_take` and the name `transfer_objection_register` imported, and it is not
kept.

## Back on the queue, 2026-11-18 (worker tick)

This file was moved to `done/` in the working tree on 16 Nov 15:39 and never committed. Classes 1,
3, 4 and 6 were still open, so it is back at the staging root.

**The 2021-12-31 window did not finish.** `/tmp/c32c1/r2021.log` stops at simulated 2018-08-13,
last written 16 Nov 16:05. It wrote no `r2021.json`, and no process is running it. The 2016
window took 42 min wall clock for one year, so the 2021 window needs about four hours. It ran
while the memory governor reports its budget exhausted, so the likeliest cause is the run being
killed. That is not established: no record says what killed it. Class 1's refuse leg for meter
recovery and both debt-objection legs are still unexercised in operation. The probe
(`/tmp/c32c1/probe.py`) is intact. Relaunch it as a declared, waited-on run (`tools/wait_for.py`),
not as an untracked background job.

**Class 7, closed.** `_suitability_check` printed `NOT_SUITABLE` ("finding is negative") whenever
the in-effect S&RP record found the bar, including where every bar item was an unanswered
question. It now prints `SUITABILITY_UNANSWERED` in that case. It prints "negative" only where
something held or answered found the bar. The refusal and its ground are unchanged, so the live
gate refuses exactly what it refused before. Only the words differ. The evidence prefix
`UNANSWERED_EVIDENCE` now lives in `winter_moratorium` and the S&RP builder writes it, so the
gate and the builder cannot drift apart. The control is
`test_an_unanswered_conversation_is_refused_as_unanswered_not_as_negative`, mutation-proven both
ways: the gate always printing "negative" reds it, and the gate calling a real bar "unanswered"
reds it. The commons §5 S&RP paragraph is amended (K8).

| class | state |
|---|---|
| 1 | open: the 2021 window must be rerun |
| 3 | open (W2 meter book, with C32's check (e)) |
| 4 | open (D lane) |
| 6 | open (C32) |
| 7 | closed, 2026-11-18 |
