**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# A declared payment lifecycle would have exposed 10 of 34 past DD defects, so it is dropped (2026-11-16)

*Answers part 2 of `docs/staging/advisor/done/DIRECTOR_RULING_EP11_REFRAME_APPROVED_AND_TEST_A_DECLARED_PAYMENT_LIFECYCLE_AGAINST_PAST_DD_DEFECTS_2026-11-16.md`.
The prediction was filed first, in the commit that also carries the lifecycle:
`SEAT_PREREG_WOULD_A_DECLARED_PAYMENT_LIFECYCLE_HAVE_EXPOSED_THE_PAST_DD_DEFECTS_2026-11-16.md`
(same folder). The replay began while that commit was being gated, so its bytes were already fixed.*

## Answer

**Reading 2, which decides: 10 of 34 defects exposed (29%). That is under half, so by the rule the
lifecycle is dropped.** There is no declared home, no check and no framework. The lifecycle file
leaves `company/` in this commit; it stays in git history at 5bf7e7c87, the commit that filed the prereg.

| Reading | Exposed | Of defects | Share |
|---|---|---|---|
| 1: whole diagram | 14 | 34 | 41% |
| **2: without the two contaminated invariants** | **10** | **34** | **29%** |
| 2, also without #21 and #22 (contaminated by origin, below) | 8 | 34 | 24% |

- Sample: 36 files by the name rule. Two are X, not DD defects: the shared-tree hygiene finding, and
  W1's process measure.
- Grades: I = 10, I* (exposed only by a contaminated invariant) = 4, U = 0, N = 20.

## Prediction against result

| | Predicted | Result |
|---|---|---|
| Reading 2 | about 12 of about 33 (36%), range 25 to 50%, so **drop** | 10 of 34 (29%), so **drop** |
| Reading 1 | reading 2 plus 2 to 4 | plus 4 |
| Half-month first DD | exposed in reading 1 only | I*, reading 1 only |
| Bill shock | N | N (a definition failure) |
| The journey's end with two homes | N | N (two legal exits read from two lists) |

The call held. The point estimate was 7 points high.

## What the ten are

They are not ten independent catches. They collapse into about five classes:

- **DD activity after the mandate ended (4):** #8, #14, #31, #32. Collections and reviews run from
  `off_dd`, which has no such move. This is the one class where the diagram is clearly the right tool,
  and four repeats show it recurred.
- **A DD neither collected nor returned on its date (2):** #4, #5, under `collection_has_two_outcomes`.
- **Arrears that disagree with the one balance (2):** #2 (dunned per bill while in credit) and #6 (the
  journey cured while the missed instalment was never made good).
- **Collection before supply (1):** #22.
- **The review sized from true consumption (1):** #21.

## Contamination, beyond what the prereg named

- **#22, collection before supply.** The rule is a GAP carried as practice. The drafter had seen this
  finding's file name before "not before supply start" was written.
- **#21, review basis.** The practice note the move cites
  (`a_suppliers_annual_dd_review_is_sized_from_its_own_issued_bills_not_true_consumption_2026-10-13.md`)
  was written from this very finding.

Without both, the count is 8 of 34.

## Where the diagram was wrong, not just silent

**#9 (D48) is graded N, and it exposes a drafting gap.** Ofgem's 2 Feb 2023 update says suppliers
commonly add a debit balance to the DD amount at review. The diagram's `review_set` names only the credit
side. With that sentence added in hindsight, #9 would be I and reading 2 would be 11 of 34 (32%). The
verdict does not move. The gap is recorded here and not patched, because the file is dropped.

## Why so few

Twenty of 34 DD defects are not lifecycle-shaped:

- instruments and harnesses (#3, #7, #11, #17, #18, #25);
- pages and published arithmetic (#1, #10, #24);
- prices, VAT and caps (#13, #15, #16, #26);
- citations and constants (#19);
- provisioning (#30);
- the back-billing basis (#12, #28);
- method results (#34);
- seam plumbing (#27);
- a review that never sought the balance (#9).

None of the 34 sat in a state the diagram does not name, so the "undefined state" leg exposed
nothing. **The repeat DD defects are mostly defects of quantity and reading, not of illegal moves.**
That is the same lesson as the concept-link test (0 of 3): what was missing was one definition with
its homes declared, not a structure.

## What survives, as a lead, not a proposal

The four post-mandate repeats (#8, #14, #31, #32) are one class. An existing domain invariant, "no DD
collection or review on an account after its mandate ended", is the one-leg check that class asks
for. It goes in `company/compliance/domain_invariants.py` beside its siblings if a fifth repeat
appears. It is not filed as work now: the latest of the four (#14, 3 Nov) was fixed, and a control
keyed to a fixed defect guards nothing live.

## Grading

The 36 files were read and graded by a forked reader against the frozen prereg and yaml. Its
instruction was to be adversarial against the lifecycle: grade I or U only when a check of each
account's record would genuinely have fired. The seat spot-checked #2 (I: dunned while in credit
under the level schedule, confirmed from the finding's own text) and #9 (N, above).

| # | Short name | Grade | Move or invariant |
|---|---|---|---|
| 1 | cold read: "absolute" DD rule | N | page wording |
| 2 | level DD dunned per bill while in credit | I | on_supply_dd → in_arrears not listed; `one_balance` |
| 3 | payment-belief harness detects late DDs | N | harness |
| 4 | a late DD (181 accounts) | I | `collection_has_two_outcomes` |
| 5 | movers' DDs collected late | I | `collection_has_two_outcomes` |
| 6 | the journey cures, the missed instalment is never made good | I | `arrears_cleared` without its trigger; `one_balance` |
| 7 | the opening cohort split drops sixty | N | instrument |
| 8 | a stopped DD reaches the money side | I | collect from off_dd |
| 9 | D48: the review never asks for the balance | N | the diagram is silent (gap above) |
| 10 | D48: mean barred | N | arithmetic |
| 11 | six level-collection controls red | N | test |
| 12 | the back-billing comparator for DD | N | basis not modelled |
| 13 | blind invariant suite, 67a893e749 | N | price and meter |
| 14 | a level DD kept after the mandate ended | I | collect and review from off_dd |
| 15 | sold above the cap | N | price |
| 16 | the standing charge and VAT twice | N | price and VAT |
| 17 | the DD failure correction | N | calibration |
| 18 | the opening-arms instrument | N | instrument |
| 19 | the review band cites a non-existent SLC | N | citation |
| 20 | 97% of DDs at exactly the bill | I* | `one_regular_amount` |
| 21 | the review told true consumption | I | `review_set` basis (contaminated by origin) |
| 22 | collected before supply (336) | I | `no_collection_without_supply_or_balance` (contaminated) |
| 23 | DDs on weekends and Christmas Day | I* | `collections_on_processing_days` |
| 24 | the opening estimate is unpublished | N | publishing |
| 25 | the publisher's gate cannot grade the row | N | gate |
| 26 | renewal price, prepayment against DD | N | price |
| 27 | the seam follows a stopped DD | N | plumbing |
| 28 | pay-on-receipt back-billed beyond 12 months | N | basis not modelled |
| 29 | shared tree held by records | X | not a DD defect |
| 30 | the stayer provision bucket | N | provisioning |
| 31 | the supplier stops, the money side does not follow | I | collect from off_dd |
| 32 | the triads' DD outcomes after the stop | I | collect and returned from off_dd |
| 33 | a nil DD; settles cleared bills | I* | `one_regular_amount` |
| 34 | the estimated opening no longer beats the first bill | N | method result |
| 35 | W1's level-DD measure | X | process measure |
| 36 | the first DD from half a month | I* | `one_regular_amount` |
