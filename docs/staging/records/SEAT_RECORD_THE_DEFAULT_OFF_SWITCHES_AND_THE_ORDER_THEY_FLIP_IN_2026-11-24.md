**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `unminted` · **Claim:** `the-default-off-supplier-switches-flip-in-a-chosen-order`

# The default-off switches, what grades each, and the order they flip in

*Autonomous worker, 24 Nov 2026, read against `origin/main` at `bfad11e9fa`. Nothing is flipped here.
This record sets the order. The continuation queue is re-handed to match it (§5).*

## 1. The census

Every switch that is built, defaults to off, and has a pre-registration or a named switch-on rule on
origin. "Acts on" comes from the code at origin, not from the record.

| # | switch (where) | pre-registration | its one-change clause, quoted | what it grades, on which book | acts on |
|---|---|---|---|---|---|
| 1 | `CONTRACT_THE_FIRST_TERM_AT_THE_QUOTED_STRIKE` (`simulation/live_population.py:1205`) | `SEAT_PREREG_THE_FIRST_TERM_CONTRACTED_AT_ITS_QUOTE_2026-11-24` | "B8's five grades read that book, and two changes in one book cannot be told apart." | R1–R5 (campaign exact, legs the hold touches, first-year margin per win), on "the first book whose producing commit has the switch taken" | **The world's contract.** A won first term is struck at a price the household was never shown, up to ×1.54 the cap in 2021 and 18–31% under the cheapest fix in 2023–24. SLC 23. Both arms. |
| 2 | `FIRST_TERM_CAP_HOLD_DELETED` (`company/pricing/renewal_rate_chain.py:261`) | `SEAT_PREREG_THE_FIRST_TERM_CAP_HOLD_DELETED_2026-11-24` | Off-rule: "not flipped while a won first term is contracted on a strike other than the one quoted." | P1–P4, on the first book carrying it. #1's record voids P2–P3 and predicts **0 legs move** once #1 is taken (R3; range 0–6) | Company acquisition rule. Both arms. |
| 3 | `SETTLEMENT_LOSSES_APPLIED` (`simulation/hedged_settlement.py:74`) | `SEAT_PREREG_THE_WORLD_SETTLES_ELECTRICITY_LOSSES_2026-11-24` | "If both landed on one book, neither change could be attributed. So … a one-variable run against a book already read." Waits on #2's one-variable book. | Its own predictions, on the book after #2's | **The world's cost line** (9–13% loss uplift). Both arms. |
| 4 | `B8_BLIND_HOLDOUT_ON_IN_THE_STANDING_POLICY` (`company/policy/decision_policy.py:431`) | `SEAT_PREREG_B8_THE_HOLDOUT_SWITCHED_ON_IN_THE_STANDING_POLICY_2026-11-23` | P4: "the flag flips only after all five have been graded on a book that does not carry it … a book carrying two changes cannot attribute either one." | P1–P5 on the first standing book carrying it; resolving the effect takes about 70 standing books | An **instrument**, randomised inside the book. CURRENT and every arm built from it. The flat twin has no tiers, so it makes no offers to hold. |
| 5 | `EP1_DATED_DISCOUNT_RATE_IN_THE_STANDING_POLICY` (`decision_policy.py:439`, built `63f7faeba`) | Commit body and the switch's comment. No separate record. | "off because the rankq, B8 and first-term pre-registrations each refuse a second decision change in the book they grade" | Nothing is pre-registered yet | **Only the value arm.** `renewal_margin_uplift` returns at `if arm == FLAT_RULES` before it reads `discount_rate` (`value_based_renewal.py`), so CURRENT's own flat-rules renewals do not move. Terms starting from 1 Oct 2023 only. |
| 6 | `renewal_belief_by_ending_term` (policy field) | `SEAT_PREREG_THE_ENDING_TERM_BELIEF_ON_THE_COMING_BOOK_2026-11-22` | §0(a): "A standing book cannot give a departure interval … One book holds one arm. The switch-on rule … needs arms." | On the standing book: only the precondition (Q1/Q3: does the conditioned belief still rank leavers). The switch-on is §14's paired arms re-taken, 6 seeds | Value test (A's belief) |
| 7 | `retention_cut_at_the_flips` (policy field) and its rank-at-q successor | `SEAT_PREREG_WHAT_THE_SUPPLIER_DOES_ON_EACH_S12G_OUTCOME_2026-11-23` | "A next lever chosen after P1 is read cannot be told apart from a lever fitted to P1." | s.12g arms, book 61118, churn pair 13131/14141. rankq is **running now** (`s12g-rankq-is-graded-when-it-ends`) | Value test |
| 8 | Expected-tenure value of a kept household | Named in s.12g's BELOW step 2. **Not built.** No switch on origin. | "only on 'volume'" | One arm against A on 61118 | Value test |
| 9 | `SMART_METER_EXCHANGE` (`simulation/meter_reads.py:441`) | `SEAT_PREREG_THE_SMART_METER_EXCHANGE_SWITCH_FOR_D48_2026-11-15` | "Any result whose two arms, or whose result and baseline, straddle the flip cannot be attributed." Off until the per-customer, opex-credit, bad-debt and retention-netting arms are graded. | D48 and the value arms, re-taken | **The world.** It moves the digest. |
| 10 | `A_WOKEN_SVT_STAYER_REFIXES` (`simulation/contact_response.py:220`) | C30 arms (`SEAT_PREREG_C30_*_2026-10-2{3,4}`) only | None found for the standing book | C30's arm C | World response. Out of this queue: no switch-on rule exists to order. |

The other `False` fields in `DecisionPolicy` (`retention_weighs_save_odds` and its dependants,
`renewal_rate_bills_the_shared_rise`, `next_best_action_*`, `save_offer_decides_per_household`,
`theft_screen_in_billing_run` and the rest) are each graded by their own arms record. None of them
claims "the next book", so none is in this queue.

## 2. The question the queue turns on: attribution, or a standing book?

**It is about attribution.** Every clause above gives the same reason: two changes in one book cannot
be told apart. None of them says the standing policy has to carry the switch for the grade to count.
Separate arms on the same seeds, each with one switch against the same standing baseline, satisfy the
clause for **that switch's own effect**. Four limits decide where that is enough.

1. **World switches (#1, #3, #9) are not arms.** An "arm" with the world changed is a different world,
   and everything compared across it straddles the flip (#9's clause). The baseline/curriculum split
   also means they flip for fidelity reasons, blind to company results. So they are **not ordered by
   the arm-versus-twin gap at all**. They go on the standing book one at a time, world first (W7), and
   each one re-bases every arm that follows it.
2. **An instrument belongs on the standing book.** B8 (#4) is randomised inside the book, so its own
   grade does not depend on what else the book carries. What it needs is books: about 70 of them. An
   arm gives one book of evidence and nothing after it. B8 takes a standing book, and its P4 rule
   (the five grades read first) stands.
3. **A grade pre-registered on "the first book whose producing commit …"** is re-pointed to an arm
   only by an amendment filed before that arm runs. #2 is the case that pays for one (§3, step S2).
4. **Arms measure each switch against the baseline, not the switches together.** Where two switches
   interact, a separate arm does not establish their combination. Two cases are known. #1 makes #2
   near-null (R3). #6's rule depends on #7's outcome (s.12g BELOW: "the money is not in the ranking").

## 3. The order

**Standing books (the world first, one change each).** Each step waits for the book before it to be
read.

- **S0.** The post-s.12g book with no change. B8's five grades (D48, KNIFE3 I1–I5, the dual household's
  answers, won-switch P2–P5, the ending-term precondition) are read on it. *No standing book has been
  built since 20 Nov 15:39. S0 is what the whole queue waits on, not the order.*
- **S1. #1, the first term contracted at its quote.** This is a world defect that transfers value
  (M2), so it comes first. R1–R5 are graded on S1.
- **S2. #2, graded as an arm on S1's seeds, not as a standing book.** R3 predicts 0 legs move, so a
  standing book of its own would buy almost nothing. This one-variable book against S1 meets #3's
  "a one-variable run against a book already read". The amendment that re-points P1–P4 to that arm is
  filed before the arm launches. If the arm moves more than R3's 0–6 legs, #2 gets a standing book
  of its own before S3.
- **S3. #3, settlement losses.** The world's cost line, one variable against S1 plus #2.
- **S4. #4, B8's blind holdout on CURRENT.** It comes after the world switches because every standing
  book with the holdout on adds evidence, and starting two books later costs about 2 of the roughly 70
  books it needs. B8's P5 step 1 still applies: Directions ¶7 is read before the flip.
- **S5. #9, the smart-meter exchange.** It is last because it moves the digest and so re-bases the
  value arms. Its own rule makes it wait on those arms being graded.

**Arms (supplier levers, ordered by the gap; they can run in the box between standing books).** No arm
touches the standing book, so none of them waits on S0–S5. They do compete with S0–S5 for one box.

- **A1. rankq (#7), running.** On the gap, s.12g gives the only interval that excludes zero for any
  switch here: the cut's value-arm gain, cut − A = **+£0.916 (+£0.222 to +£1.790)**. The corrected
  belief alone, A − twin, is **−£0.861 (−£2.095 to +£0.320)**. So the evidence ranks the gate (who is
  offered, and how many) above the belief. rankq tests the gate with no fitted level left. Its reader
  takes the branch s.12g pre-registered and this record does not pick again.
- **A2. Expected-tenure value (#8), only if A1's reader finds "volume".** It is not built yet: a K8 page
  comes first, then a default-off switch, then measure-first (at least 10 value-refused renewals). It is
  ranked second on the gap because §12f put £1.041 of £0.996 on retention beyond one term, which is the
  largest mass the value test does not price. If A1 finds "belief", A2 is not run, as s.12g says.
- **A3. The ending-term belief arms (#6).** §14 is re-taken at 6 seeds, but only if S0's precondition
  holds (Q1 lower bound > 0.5 and Q3 > 0) and A1 has not found that the money is not in the ranking.
- **A4. EP1's dated rate (#5), as an arm.** This means value arm with the switch against value arm
  without, on 61118 at 13131/14141, or as an extra configuration on whichever arm run launches next.
  It acts only in the value arm and only from Oct 2023, so it needs no standing book. Its "next book"
  claim was scoped wrongly: flipping it on CURRENT changes no flat-rules decision. **I cannot yet say**
  which way it moves the gap. A 12.3% rate lowers the annuity on a kept household by about 10%, which
  should lower the value arm's retention cuts from late 2023. The sign of that on the gap is not
  predicted here. It is predicted in A4's own pre-registration, before the arm runs.

## 4. What would show this order wrong

- **S0 never comes, or comes late.** Then every standing step is set by the box, not by this order,
  and the arms (A1–A4) are the only progress. The S0 book is the item that matters most this week.
- **A1 reads ABOVE on origin.** Then the gate carries the advantage, and A3 and A4 move ahead of A2.
- **S2's arm moves legs outside R3's 0–6.** Then #2 gets its own standing book, and S3 moves one step
  later.

## 5. The continuation queue, re-handed to match

The queue offers its oldest entry first. Its embargo grammar takes only a time or a path, and "a
condition on another item's landing has no grammar: hand this off FROM that landing instead". So
three entries are live, handed off in this order on 24 Nov:

1. `s1-contract-the-first-term-at-its-quote-on-the-book-after-s0` (from 09:00 on 25 Nov; it re-hands
   itself daily until the five grades are written). Its landing hands off S1's grade and `s2`, and S2's
   graded arm hands off `s3`.
2. `b8-flip-the-blind-holdout-on-after-the-five-grades`, re-handed under its own id (from 09:00 on 26 Nov)
   so that it sorts after S1. A new STEP 0 holds it until #1 and #3 are on origin and S3's book is read.
   Its grade hands off S5.
3. `a4-ep1-dated-rate-graded-as-a-value-arm` (embargoed on `/var/tmp/vtn-driver/grade_rankq.out`).

A1 was already live (`s12g-rankq-is-graded-when-it-ends`). Its reader hands off A2 or A3, per s.12g.

**Reverse:** drop those ids with `python3 -m background.seat_continuation --drop <id>`, and revert this
file.
