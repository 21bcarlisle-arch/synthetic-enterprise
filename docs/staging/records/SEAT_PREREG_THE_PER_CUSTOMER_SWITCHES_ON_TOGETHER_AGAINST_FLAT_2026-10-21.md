# Pre-registration: the per-customer switches on together, against CURRENT and against flat

**Written 2026-10-21 ~04:30Z, before any arm runs.** *(Correction, at grading: "~04:30Z" was BST.
The prereg landed at about 03:15Z, and the arms started after it — arm `current` at 07:22:07Z.)* Claim `the-per-customer-switches-on-together-against-flat`
(Lane 0, seat). DEVELOPMENT: one book, the default seed. A diagnostic, not EP17's blind grade.

**Why a new file and not an extension of the 18 Oct prereg.**
`SEAT_PREREG_B11_C35_C34_ON_THE_FIRST_PUBLISHED_DUAL_FUEL_RUN_2026-10-18.md` grades the B11 and C35
*instruments* on a published run. It holds no arm and no book-level figure. This file is the
three-arm run.

## 0. What runs, and two corrections to the item that asked for it

- **Code and book.** All three arms run from one origin worktree, `/var/tmp/se-pcs-arms` at
  `9ca972774`. That is after `ec7fd9942` (the standing-charge opex credit in the term
  contribution). Each arm is run by `tools/per_customer_switch_arms.py <arm> <out>`, which follows
  `tools/read_instruction_arms.py`. Outputs: `/var/tmp/se-pcs-arms-out/{current,all_on,flat}.json`.
  - `current`: `CURRENT_POLICY`.
  - `all_on`: `CURRENT_POLICY` with `next_best_action_decides_at_renewal`,
    `next_best_action_shares_by_retention_rise` and `save_offer_decides_per_household` all True.
  - `flat`: `FLAT_SUPPLIER_POLICY`.
  - Each arm is also bound to `run_phase2b.CURRENT_POLICY` and entered through `policy_scope`.
    `company/policy/decision_policy.py` is not changed.
- **Correction 1: this is not "the 8b6fea024 book".** `8927e9345` (400 founder households, a
  settlement budget of 7,700) changed the book after the 19 Oct publish. At `9ca972774` the book is
  `8927e9345`'s. Between them, the only `simulation/`, `company/` or `saas/` commits are two D48
  billing changes: `7a266cb76` (a held estimate on a closed account goes out on its final bill) and
  `032b3dec2` (four founder bills held at C8's semi are released). The 8b6fea024 publish is
  therefore not a baseline for any figure here. The baseline is the `current` arm at the same
  commit.
- **Correction 2: two of the three switches cannot move the book.** `next_best_action_decides_at_renewal`
  is "records only: nothing is sent and the world is unmoved" (`decision_policy.py`; the C34
  prereg's O1 confirmed this byte for byte). C35's rise is priced only through that desk, into the
  same log. So `all_on` against `current` tests one book-moving switch, the per-household save.
  The other two add a record of what the company *would* have decided. **This run therefore cannot
  show the per-customer advice creating or transferring value (M2). It can show only what the
  company would decide, and at what claimed value to each side.** Turning that record into an act
  the world answers is the build that would let it. That is named in §5 and not done here.
- **The flat arm is not "flat renewal pricing".** `CURRENT_POLICY` and `FLAT_SUPPLIER_POLICY` both
  hold `renewal_margin_arm="flat_rules"`. The flat arm removes targeted retention (tier share 0, so
  no retention offer goes to anyone), the per-segment framing and the per-segment tone. Hedging,
  the save on a loss notice (`price_match`) and every regulatory duty are the same in both arms
  (`test_the_flat_supplier_policy_differs_from_current_in_exactly_the_per_customer_fields`).

## 1. The anchor I read before writing, and what it is

I read one run before writing: `/var/tmp/se-read-arms-out/off.json`, the read-instruction `off` arm.
It is `CURRENT_POLICY` at `8927e9345`, full window, default seed. It is not one of these arms. It is
the nearest run to `current`, and differs from it only by the two D48 commits above.

| figure | 8927e9345 off arm |
|---|---|
| `provisioned_net_gbp` (the like-for-like clock, `cd1f976c7`) | £600,806.22 |
| `total_net_gbp` (settled-realised; NOT differenced against the line above) | £721,188.51 |
| `provisioned_bad_debt_gbp` | £124,805.98 |
| `churned_billing_accounts` (departures) | 354 |
| `total_acquisition_wins` | 612 |
| `retention_log` offers: retained / churned despite offer | 113: 76 / 37 |
| retention cost (sum of `retention_cost_gbp`) | £2,837.65 |
| household paid us (sum of `bills[].total_amount_gbp`, inc VAT) | £3,133,805.35 over 53,314 bills |

**What each count counts.** "Accounts retained" is read here as departures
(`churned_billing_accounts`, billing accounts whose household left). Fewer departures means more
retained. A retention-log "retained" means only that an offered household did not leave at that
roll. It does not mean the offer caused the stay.

## 2. Predictions: `current` (9ca972774) against the anchor

- **K1.** `retention_log` has 113 offers, 76 retained, as in the anchor. Departures are 354 ± 3.
  Why: the two D48 commits change bills on closed or held accounts, not a renewal roll. A
  departure could move only if a bill change feeds a world roll. I hold this at about 80%.
- **K2.** `provisioned_net_gbp` is within ±£1,500 of £600,806. Household paid is within ±£3,000
  of £3,133,805. Why: the four released founder bills and the final-bill estimates are small, and
  they add revenue rather than remove it.
- **K3.** There is no `next_best_action_renewal_log` key. `save_on_loss_notice_log` is present
  (carried from the raw run): 40–100 rows, at most 15 holding an Invitation, and 0–3 saved. This
  is scaled from the 20 Oct `e4271755f` arms (69 / 10 / 1) to a book whose founders changed.

## 3. Predictions: `all_on` against `current`

**Decisions taken, by kind** (from `next_best_action_renewal_log`, which has 3 rows per household
decision state, one per stated advice effect):

- **A1. Rows 750–1,300.** Why: the C34 arms on the 19 Oct book gave 972–978. The founder book has
  400 founder households and its own campaign, and I do not know which way that moves the count.
- **A2. Advised (`action == tariff_advice`) is at most 3% of rows; point 1%.** Why: with the term
  contribution and no opex credit it was 4 of 972 (0.41%). The credit lifts the median household
  state from about −£3.66 to +£1.00…+£3.50 a month (the opex-credit prereg's P2), against a give-up
  of £2–£3 a month and a hazard cut of 0.1–0.3 pt. That is more advised, but still rare. If advised
  rows are above 10%, the opex-credit result is wrong too, and the two must be read together.
- **A3. The rise is reachable from 2019 and absent before it.** Every pre-2019 row carries
  `retention_rise_gbp_per_month = None` and a refusal naming no published default. Of 2019+ rows
  that C34 refused, at least 50% carry a rise under (£2, 0.3 pt). The 20 Oct C35 window gave 70.8%.
- **A4. Unscored rows: 0.**
- **A5. Retention offers and saves.** `retention_log` is identical to `current`: the same 113 rows
  and outcomes. The save site has the same rows as `current`. The rows that differ carry only the
  household fields, plus at most 3 rows where the household offer price differs from the per-leg
  price match.

**The book:**

- **A6. Byte-identical book, about 70%.** `provisioned_net_gbp`, `churned_billing_accounts`,
  `bills` and household paid are equal to `current` to the penny. The two arms differ only in
  `next_best_action_*`, the save log's household fields, `_per_customer_switch_arm` and the run
  stamps. The other 30% is one dual household's save being decided and taken differently. If that
  happens: departures within ±2, and provisioned net within ±£1,000.
- **A7. Household side.** No decision in the renewal log is sent, so no household pays a rise or
  gets advice. The log's claimed value to each side (`value_change_gbp` for us; the stated give-up
  for the household) is a *claim about a counterfactual*, not money that moved. It must not be
  summed into the book.

## 4. Predictions: `flat` against `current`

- **F1. 0 retention offers** (`retention_log` empty, retention cost £0). Pinned by the policy's
  zero tier share. If any offer appears, the flat arm is not flat, and the run is void for F2–F5.
- **F2. Departures rise by +2 to +25; point +10.** Why: 76 offered households stayed under
  `current`. Most of them would have stayed anyway, since the world's response to a 1–8% cut is
  small. The rest leave. Once one roll differs, the book's later term heap differs. So I give the
  width and do not predict a per-household match.
- **F3. Provisioned net: current − flat is in [−£4,000, +£8,000]; point +£1,000.** Why: flat saves
  the £2.8k of discounts and loses the margin on the extra leavers, at roughly 10 × 1–2 years ×
  £100–£200. The two are the same size, so I give no confident sign. **F11: a per-customer lead
  above +£8,000 would be the flattering surprise.** It is read against the tie rule of the 16 Oct
  varied-draws prereg: a lead bought with retention discounts is "bought with discounts", not
  knowledge. This run has no flat-at-level arm to separate the two.
- **F4. Provisioned bad debt within ±5% of `current`.** The firm tone for everyone moves dunning
  slightly. I do not know the sign.
- **F5. Household side: a GAP.** The run records what *our* households paid us. Under `current`,
  stayers paid £2.8k less because of the discounts: that is a transfer to them, not value created.
  A household that leaves under `flat` stops appearing in `bills`, and what it pays its next
  supplier is not in the run. So "household paid us" falls under `flat` for a reason that is not a
  saving. **The household-side money of retention against flat cannot be read from this run.**
  Household paid is reported per arm, with that caveat beside it, and it is never differenced as
  household value.

## 5. How it will be graded, and what this run cannot answer

The grade is a continuation, taken when all three outputs exist. It reads K1–K3, A1–A7 and F1–F5
from the three files with the definitions in §1, marks each held, refuted or cannot tell, and
keeps the refuted ones beside the result. One seed and one book: F2 and F3 are graded as point
readings with no interval, and they are labelled so. EP17's six fresh seeds are the blind grade.

**What it cannot answer.** C34's advice and C35's rise are records. The world never receives them
(§0, correction 2). So the thesis question, "does the per-customer view create value against flat
rules", is answered here only for retention offers and saves. The next build is the one that sends
the renewal desk's advice to the world as an observable act. It goes knowledge page first (K8). I
have not filed it as an atom in this commit. The grade will say whether the recorded decisions
are frequent enough to be worth sending (A2).

**2026-10-21 ~09:20Z — the arms' worktree is locked.** `git worktree lock` on `/var/tmp/se-pcs-arms`, reason naming this record, because an unlocked worktree is what got the bad-debt arm's worktree pruned last stretch. When locked: the `current` arm had been running since 07:22Z after `run_three_arms.sh` waited 14,145 s for pid 845286. `current.log` was still being written; `all_on` and `flat` follow it in order. The worktree's HEAD is `0f2b04c84`, which descends from `8fbb641d8`, so the arms run the code this record pre-registered plus later commits. Run `git worktree unlock` and remove it once the grade has read all three outputs.

## 6. Grade (2026-10-21 ~15:10Z, all three outputs present)

**What ran.** `run_three_arms.log`: `current` 07:22–09:48Z, `all_on` 09:48–12:21Z, `flat`
12:21–14:51Z, all rc=0. Every output stamps `producing_commit` `d846185c1`, a fork-salvage child of
`8fbb641d8`. The only `simulation/`, `company/`, `saas/` or `sim/` change between `9ca972774` (the
commit §0 names) and the worktree's HEAD `0f2b04c84` is `f8659d6a9`, which adds the arm tool itself.
So the arms ran the code that was pre-registered. One seed, one book: every difference below is a
point reading with no interval.

| figure (§1 definitions) | current | all_on | flat |
|---|---|---|---|
| `provisioned_net_gbp` | £600,806.22 | £600,806.22 | £600,902.77 |
| `provisioned_bad_debt_gbp` | £124,805.98 | £124,805.98 | £125,212.58 |
| departures (`churned_billing_accounts`) | 354 | 354 | 353 |
| retention offers: retained / despite | 113: 76 / 37 | 113: 76 / 37 | 0 |
| retention cost | £2,837.65 | £2,837.65 | £0 |
| household paid us (inc VAT) / bills | £3,133,805.35 / 53,314 | identical | £3,139,341.17 / 53,256 |
| save log: rows / Invitation / saved | 96 / 15 / 1 | 96 / 15 / 1 | 94 / 15 / 1 |
| renewal desk rows: nothing / tariff_advice | absent | 848 / 514 | absent |

**K: `current` against the anchor**
- **K1 HELD, exactly.** 113 offers, 76 retained, 354 departures. These are the anchor's figures, not
  just within ±3.
- **K2 HELD, exactly.** Provisioned net and household paid equal the `8927e9345` off arm to the
  penny. So the two D48 commits (`7a266cb76`, `032b3dec2`) move nothing on this book. That is
  stronger than I predicted: I expected a small upward move.
- **K3 HELD.** There is no renewal-desk key. The save log has 96 rows (inside 40–100), 15 hold an
  Invitation (at the ≤15 bound) and 1 is saved.

**A: `all_on` against `current`**
- **A1 REFUTED, above the range.** 1,362 rows (454 decision states × 3 stated effects), against
  750–1,300.
- **A2 REFUTED, by a factor of about 13 over the bound.** 514 of 1,362 rows advised (37.7%), against
  "at most 3%, point 1%". By decision state, 177 of 454 (39%), and 164 of those 177 are advised under
  all three stated effects. **The cause is C35's rise, not the opex credit.** 508 of the 514 advised
  rows carry a `retention_rise_gbp_per_month` (median £2.09 a month, against a median headroom of
  £14.32 under the default). Advice with no rise is 6 rows (0.44%), which matches the 0.41% that
  C34 alone gave before the credit. So my tripwire ("above 10%, the opex-credit result is wrong too")
  does not fire as written. Above 10% is explained by the second switch I folded into A2's reasoning
  and then left out of its arithmetic. A rise sized to recover the household's stated give-up turns
  "neither side no worse off" into "both sides no worse off" for most 2019+ states. That was the
  rise's purpose, and I under-read it.
  - **The claim is frequent but small.** Averaging the three stated effects per advised state, the
    claimed `value_change_gbp` sums to **£121 over the whole run** (median £0.11 per state, max
    £30.91). It is a counterfactual claim (A7), not money.
- **A3 HELD.** All 546 pre-2019 rows carry no rise, each refusing with "no published default for
  this fuel on the renewal date". From 2019, 508 of 816 rows carry a rise (62%). Of the 2019+ rows
  C34 alone would refuse (all but the 6 no-rise advised rows), 508 of 810 (63%) carry one: ≥50%,
  where the 20 Oct window gave 70.8%. Every remaining 2019+ refusal is "the rise our side needs is
  above the headroom". *Side reading:* no row has a 2022 `term_start`, so the desk decided nothing in
  the crisis year.
- **A4 REFUTED as worded.** 848 rows carry a non-empty `unscored` list: every `nothing` row, 546 of
  them for no published default and 302 for the rise exceeding headroom. Two legs are also in
  `next_best_action_legs_without_contribution`. If A4 meant "a row with no reason", it holds: every
  `unscored` entry names its reason. The wording I filed does not say that, so it stands refuted.
- **A5 HELD.** `retention_log` is byte-identical. The save site has the same 96 keys. Every row
  differs only in the added `household_save_rates` / `household_legs`, and 2 rows (≤3) carry a
  different save price and `p_stay_at_save`: PROS-2022-0237 and SYN-2016-353, both electricity
  terms from 2024. Their save outcome is unchanged.
- **A6 HELD, the 70% branch.** The bills, departures, retention log, provisioned net and bad debt
  are byte-identical. The top-level keys that differ are exactly the renewal-desk logs, the save
  log, the arm tag and the run stamps.
- **A7 HELD by construction, and kept.** Nothing in the desk log was sent. The £121 is not summed
  into any book figure.

**F: `flat` against `current`**
- **F1 HELD.** `retention_log` is empty and the cost is £0. The run is valid for F2–F5.
- **F2 REFUTED, wrong sign.** Departures are **353 under flat, one fewer than `current`**, against
  +2…+25 (point +10). Account by account, 3 left only under `current` (PROS-2016-0098 and
  SYN-2016-387, both "retained" by a 2017/2018 offer and gone later anyway; OCC-d69e9e947a9e, a
  successor occupant) and 2 left only under flat (SYN-2016-399 and SYN-2016-541, both "retained" by
  an offer under `current`). **On this book the 76 "retained" outcomes trace to about 2 households
  whose departure the offer plausibly prevented,** and a divergent book then returned two others.
  §1's warning was the right one: a retention-log "retained" is not a save.
- **F3 HELD, inside the range on the side I did not point at.** current − flat = **−£96.55** (flat
  ahead), inside [−£4,000, +£8,000] but below the +£1,000 point. Flat gives no discounts (£2.84k),
  and the one fewer departure nets out to about zero. Not the flattering surprise (F11). On one seed,
  this is a tie.
- **F4 HELD.** Provisioned bad debt is +£406.59 under flat (+0.33%), inside ±5%.
- **F5 the GAP stands, read with its caveat.** Household paid is £5,535.82 *higher* under flat, on 58
  fewer bills. That fits the discounts not given plus a different book after the rolls diverge. It
  is not differenced as household value: a leaver's next supplier is outside the run, and the
  discounts under `current` are a transfer, not value created (M2).

**What the grade settles (§5's question).** On this book, targeted retention against flat rules is
a tie for us: −£97, −1 departure. It amounts to £2.8k transferred to households for about two kept.
That is evidence the per-customer retention offer creates no value here, and it errs against the
thesis, as F11 asks. The renewal desk's recorded advice, the question A2 was to settle, **is
frequent enough to be worth sending: 39% of decision states from 2019. It is worth sending only
with C35's rise attached, because without the rise it is 0.4%.** The claimed joint value is pennies
a state (£121 over the run). So the build that sends the advice as an act the world answers is
worth building as a *test*: whether the world's response is larger than the stated range. On these
claimed values, it is not worth building as a source of value. Both remain one seed. EP17's six
fresh seeds are the blind grade.

**Housekeeping.** The `/var/tmp/se-pcs-arms` worktree has been read in full by this grade and can be
unlocked and removed. The outputs stay in `/var/tmp/se-pcs-arms-out/` (not evidence held anywhere
else; ~500 MB).

## 7. Splitting the tie: inference or lever (2026-10-21, no run launched)

**Does any output carry the belief per decision state? Yes.** `next_best_action_renewal_log` has one
`monthly_hazard` per (account, `term_start`). `RenewalAdviceDesk.observe_roll` sets it to
`monthly_hazard(company_est_pre)`, which is the company's own renewal churn belief spread over 12
months. So the belief inverts exactly: `p = 1 − (1 − h)^12`. It is the belief the retention gate
reads at the same roll, taken before any offer. The population is the desk's: residential rolls
that carry a term contribution. That is 454 decision states on 263 billing accounts, read from
`all_on`. It is not every renewal in the book.

**Definitions.**
- **Leaver.** A billing account with a `churned` event in `customer_events` or `svt_departures` on
  any of its legs, dated within 365 days on or after the decision state's `term_start`, and with no
  `home_move_outs` row for the account before that departure in the window. Every
  `departure_cause` in the vocabulary is a switching risk (bill_shock, price_position,
  dissatisfaction, svt_inertia). A move-out is a separate journey (`home_move_outs`). Gas leg
  `<id>g` maps to account `<id>`.
- **At risk under flat.** The account is still supplied under `flat` at `term_start`: no `flat`
  departure or move-out dated before it. States whose account had already gone under flat are
  dropped from (a) and counted.
- **Targeted (b).** An account with a `retention_log` row under `all_on`, or a save-log row with
  `saved` true. The outcome is read in the 365 days from the offer's date (`event_date` /
  `term_start`): did it leave under `flat`, and did it leave under `all_on`.

**Predictions, written before any count below was computed (17:37Z).**
- **P7a.** Base rate: 5–15% of at-risk states are leavers under flat, point 9% (~40 leavers).
  AUC 0.55–0.75, point 0.65. The top decile of belief holds 15–35% of leavers, point 22%. With
  ~40 leavers, the AUC's standard error is about ±0.05, so an AUC below ~0.60 cannot be told from
  chance.
- **P7b.** Of the targeted accounts (about 100), 5–20 would have left under flat, point 10. Of
  those, 1–4 stayed under `all_on`, point 2, consistent with §6's account-by-account F2 reading.
- **P7c. Which carries the tie: the lever, about 65%.** The belief ranks leavers better than chance,
  but the offers convert few of the would-be leavers they reach. If the AUC's lower bound is below
  0.6, the inference carries the tie, and the renewal-advice build that §6 recommends would test
  nothing until the belief improves.

**Result (computed 17:40–17:55Z from the three outputs; one seed, one book).**

*(a) Inference: the company's renewal churn belief ranks flat-arm leavers at chance or worse.*

| reading (desk states at risk under flat) | value |
|---|---|
| states / accounts / dropped as already gone under flat | 450 / 263 / 4 |
| leavers (365 days from `term_start`) | 110 (24.4%); 94 of them leave on the roll's own date |
| **AUC of belief for leaving** | **0.461**, 95% [0.400, 0.522] (Hanley–McNeil); account-clustered bootstrap [0.398, 0.524] |
| top belief decile (45 states): share of all leavers | **11 of 110 = 10.0%** (Wilson 5.7–17.0%); its leave rate 24.4%, equal to the base |
| roll-only outcome (leaves on `term_start`) | AUC 0.412 |
| outcome read under `all_on` instead | AUC 0.442 |
| pre-2019 / 2019+ | 0.482 (182 states, 64 leavers) / **0.333** (268, 46) |
| leave rate by belief band [0,.05) [.05,.1) [.1,.2) [.2,.4) [.4,1] | 3/11, 11/34, 20/78, 43/169, 33/158: flat to falling |
| mean belief vs realised | 0.357 vs 0.244 |

The outcome *can* be ranked. On `flat`'s `customer_events` (555 rows, 95 churned), the world's own
`realized_churn_probability` ranks them at AUC 0.898. The company estimate on the same rows ranks
them at 0.531. So the gap is the company's inference, not noise in the world. From 2019 the belief
is inverted: the households it thinks most likely to leave are the least likely.

*(b) Lever: the offers reached leavers, and kept almost none.*
- 113 retention offers on 97 accounts, plus the one save. Every offered roll is a desk state. Within
  365 days of an offer, **44 accounts would have left under flat**. At the offered roll itself, 37
  leave under flat and the same 37 leave under `all_on`. **The offer kept no one at the roll it
  priced.**
- **4 of the 44 stayed under `all_on`** in the window (9%): SYN-2016-115, PROS-2016-0263,
  SYN-2016-399 and SYN-2016-541. All four left under flat months later on `svt_inertia`. That fits
  a household that, without the offer, declined the fix and drifted out of default. Under `all_on`,
  SYN-2016-115 still left about two months after its flat date, and SYN-2016-399 moved out in
  October 2019. That leaves **2 durable: PROS-2016-0263 (to 2023) and SYN-2016-541 (still
  supplied)**. That is §6's "about two", now counted per household.
- **What reached the leavers was not the belief.** Among states with belief ≥ 0.30 (the retention
  threshold), the 112 offered left at 39.3% (44) and the 127 not offered at 6.3% (8). What separates
  them is the offer gate `_cut is not None`: the market beats our fix, which is a price-position
  observable. Offered states are 25% of the desk and hold 40% of its leavers. The selection
  worked through price position. The churn belief contributed nothing to it.
  *[Corrected in §8, 2026-10-21: `all_on` sizes by `risk_tiers`, so the gate is our re-fix's
  headroom over its own cost floor, not the market beating our fix; and 62 of the 110 leavers are
  dual-fuel households whose gas leg never rolled because they left at the electricity roll.]*

**Which carries the tie: both are short, and each is measured on its own population.**
- **The retention tie (§6: −£97, −1 departure) is carried by the LEVER.** On the 44 would-be leavers
  the offers reached (out of 110 leavers in 450 states), conversion was 4, and 0 at the roll. A
  better belief could not have bought more from that offer. The reach was already 1.6× the base
  rate, through the price gate.
- **The next build is blocked by the INFERENCE.** The desk's advice, and C35's rise, are weighed
  through `monthly_hazard`, which is this belief. With AUC 0.46 (upper bound 0.52), advice ranked
  or valued by it is targeted no better than at random. The £121 of claimed `value_change_gbp` is
  priced on a hazard that does not predict leaving. **So sending the advice as an act the world
  answers (§6's recommendation) would test the lever with a random aim.** The belief should rank
  first. The cheapest candidate is the price-position observable that already selects 39% against 6%.

**Grading P7.**
- **P7a REFUTED.** The base rate is 24.4%, not 5–15%. The AUC is 0.46, below the 0.55–0.75 range.
  The top decile holds 10% of leavers, not 15–35%.
- **P7b REFUTED on the first count, HELD on the second.** 44 would-be leavers, not 5–20 (the base
  rate was wrong by the same factor). 4 stayed, inside 1–4; 2 are durable, the point.
- **P7c HELD for the tie, REFUTED in its reason.** The lever carries the retention tie, but not
  because "the belief ranks leavers better than chance". It ranks them no better than chance, so the
  tripwire I wrote (AUC lower bound below 0.6) fires: the renewal-advice build tests nothing until
  the belief improves.

**Not settled here.** One seed. `churn_model_performance` in the same output reports
`prevented_churn_saves: 76`. That is the retention-log "retained" count, which (b) shows saved no
one at the roll. It is a surface claiming saves it cannot see. Whether a belief rebuilt on price
position ranks out of sample is the next question, and it needs no run: refit on pre-2019 states
and grade on 2019+.

**Housekeeping (2026-10-21 ~17:58Z).** Nothing was left to remove. `/var/tmp/se-pcs-arms` was
already absent from disk and from `git worktree list`; another lane removed it after §6. The outputs
stay in `/var/tmp/se-pcs-arms-out/`.

## 8. Does a price-position ranker order leavers out of sample? (2026-10-21, no run launched)

*Read first: `SEAT_RESULT_THE_RENEWAL_BELIEF_DOES_NOT_ORDER_WHO_LEAVES_AND_THE_GRADE_WAS_ALREADY_ON_DISK_2026-09-22.md`.
§7's AUC 0.46 is the second time the belief has failed to rank. The first was 0.4988 on 144
renewals, where the world's ceiling was 0.74 and **bill shock was the only world factor that ordered
departures on its own**. A price-position ranker therefore tests a channel the first reading did not
name as the one carrying the signal.*

**Two corrections to the item, found before any outcome was read.**
- **The fit-on-pre-2019 design cannot carry the market feature.** `published_default_rate_ex_vat`
  is `None` before 2019-01-01, because the default tariff cap began then. So "the market's best
  published deal beats our re-fix" (`default × (1 − gap) < unit_rate`, gap > 0) is False on all 182
  pre-2019 states. A model fitted there gives it no weight. The market feature is graded below as a
  fixed-sign score with nothing fitted.
- **§7's offer gate is not the market's price.** `all_on` sizes cuts by `risk_tiers`
  (`CURRENT_POLICY.retention_cut_sizing`), not by the price match. So `_cut is not None` above the
  0.30 threshold means the tier cut (3–8%) fits above *our own cost floor*. That is our margin
  position. **Correction to §7, beside its claim "the offer gate `_cut is not None`: the market beats
  our fix":** the gate is our re-fix having headroom over its own cost, not the market beating
  it. The rebuilt market test agrees with the actual offers on only 92 of 240 states above the
  threshold. On every state, the desk log's `monthly_margin_gbp` (the term's contribution per month,
  at the roll) is the observable that gate reads.

**Population and outcome.** As §7: the desk states at risk under `flat`, with leavers under `flat`
within 365 days. That is 182 pre-2019 states (64 leavers) to fit on and 268 from 2019 (46 leavers) to
grade on. The belief reads AUC 0.333 on those 268.

**Rankers (every input is company-visible at the roll).**
- **R1, fitted.** Logistic regression on standardised `rate_vs_svt_pct` (the mean over the state's
  legs, from `account_state_log` at `term_start`), tenure in years since the account's first term,
  and `monthly_margin_gbp`. Fitted on pre-2019, graded on 2019+.
- **R2, unfitted.** The market gap `(unit_rate − default_ex_vat × (1 − gap)) / unit_rate`, the
  maximum over legs, where higher means the market undercuts us by more. Graded on 2019+ only. In
  the crisis years the gap is 0, so there it measures our rate against the default alone.
- **R3, unfitted.** `monthly_margin_gbp`, where higher means more likely to leave: §7's gate, as a
  continuous score.

Bounds: an account-clustered bootstrap (1,000 draws, seed 7) on each AUC, and on the paired
difference against the belief over the same states.

**Predictions (filed before any ranker was scored, 19:1xZ).**
- **P8a.** R1 2019+ AUC point 0.60, range 0.50–0.70. Clustered lower bound above 0.5: 45%.
- **P8b.** R2 point 0.62, range 0.50–0.75. Lower bound above 0.5: 50%.
- **P8c.** R3 point 0.58, range 0.48–0.68.
- **P8d.** At least one ranker beats the belief, with the lower bound of the paired difference
  above 0: 80%. The belief is inverted, so this is the easy bar. The bar that decides is above 0.5.
- **Decision rule, fixed now.** If any ranker's clustered lower bound clears 0.5, the advice build
  has an aim, and that ranker is it. If none clears 0.5, the inference is the work ahead of the
  build. It then starts from the 22 Sep reading's bill-shock channel, not from price.

**Result (computed 19:15–19:45Z from `all_on` and `flat`; one seed, one book).**

| ranker, graded on the 268 states from 2019 (46 leavers) | AUC | account-clustered 95% | minus belief, paired |
|---|---|---|---|
| belief (§7) | 0.333 | [0.253, 0.426] | — |
| **R1 as pre-registered** (rate vs SVT, tenure, `monthly_margin_gbp`) | **0.706** | [0.621, 0.788] | [+0.23, +0.49] |
| R2 market gap, unfitted | 0.543 | [0.439, 0.642] | [+0.11, +0.30] |
| R3 `monthly_margin_gbp`, higher = leaves | 0.248 | [0.167, 0.337] | [−0.17, −0.01] |
| *after the leak below is removed:* | | | |
| rate vs SVT of the electricity leg on the book, unfitted | **0.594** | **[0.479, 0.709]** | [+0.15, +0.36] |
| rate vs SVT + tenure, fitted pre-2019 | 0.584 | [0.486, 0.676] | |
| household EAC from the book / household is dual-fuel | 0.473 / 0.486 | | |

**R1 clears the bar, and it clears it on a leak.** The desk log's `fuels` lists the legs that
*rolled*. When a dual-fuel household leaves at its electricity roll, its gas leg never rolls, so
the desk state reads "electricity only" because the household left. There are 69 such states
(dual-fuel household on the book, gas absent from the state), and **62 of them are leavers: 62 of
§7's 110.** Anything summed over the state's legs carries that. Volume is one such feature: the desk
legs' EAC alone ranks at 0.813 out of sample. `monthly_margin_gbp` is another, and it is what R1
weighted most (coefficient −0.85). Read from the company's book at the roll instead, household
volume and fuel count rank at chance (0.47, 0.49). Margin per MWh reads 0.67 over all states, but
it flips to 0.41 on the states the leak cannot reach. So R1's 0.706 is a description of how the log
was written, not an aim. *(The no-leak subset is selected on an outcome-caused shape, so it is a
sensitivity reading only. On it, rate vs SVT + tenure reads 0.666 [0.511, 0.810] with 19 leavers.)*

**What survives is price position, and it is weak.** The electricity leg's rate against SVT ranks
leavers at 0.60 before 2019 and 0.59 from 2019, in the same direction on both sides of the cut.
That stability is the belief's opposite: the belief reads 0.48 before 2019 and 0.33 after. It beats
the belief, with the paired bound above 0. But its own bound reaches 0.479, so on 46 leavers it
cannot be told from chance.

**By the decision rule written above: the inference is the work, ahead of the build.** Read
literally, the rule fires on R1, whose lower bound is 0.621. I am not taking that, and the reason is
stated: R1's weight sits on a feature the outcome writes. With R1 set aside, no leak-free ranker's
bound clears 0.5. So the renewal-advice build still has no aim. Price position is a real, stable,
weak signal (about 0.6) and belongs in the rebuilt belief. The 22 Sep reading points at bill shock
as the channel that carries the world's ordering (0.70 on its own), and the belief reaches bill
shock through a term that is zero on almost every leg. That is the next place to look, not more
price features.

**Two things this changes outside §8.**
- **§7's leaver population is 56% the leak.** The belief is not leaky: it is taken at the roll,
  before the departure. But the leak states carry a low mean belief (0.15, against 0.34 elsewhere)
  and are 90% leavers, and that drags §7's 0.33 below chance. It does not rescue the belief: on the
  states the leak cannot reach, from 2019, it reads 0.452 against rate vs SVT's 0.654.
- **Any grade or fit on `next_best_action_renewal_log` must take a household's fuels and volume
  from the book, not from the state's legs.** The desk also values a household that leaves at its
  electricity roll on electricity alone. Whether that is how a real desk sees the roll (the gas
  notice goes out at the same time) or an artefact of the loop's leg order is not settled here.
  The `flat` output also records no gas `churned` event for these households (PROS-2018-0002: the
  electricity leg leaves on 2019-01-02, and the gas leg's term simply stops). Where the gas leg goes
  is a question for the world's departure record, unasked.

**Grading P8.**
- **P8a, out of range and void as an aim.** 0.706 is above the 0.50–0.70 range, and the bound
  clears 0.5, but on the leak.
- **P8b, inside the range and below the bar.** 0.543 is inside 0.50–0.75. The lower bound, 0.439,
  does not clear 0.5. The market gap adds nothing over our own rate against SVT.
- **P8c, refuted.** Margin runs the other way (0.248), and its sign is the leak's.
- **P8d, held.** Every ranker except R3 beats the belief, with the paired bound above 0. That was
  the easy bar, as written.

Scripts: `/tmp/pcs8_{feat,grade,rob,fuel,leg,clean,strat,last}.py`, scratch only and not landed.
They reuse §7's `/tmp/pcs_split.py` definitions.

## 9. Can the company see the bill shock that orders renewal departures? (2026-10-21, no run launched)

*The question §8 left: the world orders renewal departures by bill shock (22 Sep, 0.70 alone), and
the belief reaches it through a term that is almost always zero. Is the gap modelling or
observability? If a company-visible shock observable ranks §7's leavers out of sample, the belief has
a rebuild path. If the world's own shock ranks them and nothing the company sees does, the gap is
observability.*

**What the world's shock is (`simulation/experienced_bill_shock.py`), read before writing.** It is
one per household per renewal, over the twelve months before the roll. **Direct debit:** the DD
the review sets from this year's spend, against the DD set from last year's (in year one, against
the sign-up amount). **Standard credit:** this year's mean monthly bill against last year's (in year
one, against the quote). The shock is a rise above 15%. Prepayment is out of scope. Every input is
something a supplier holds (its bills, its DD review), but the world reads settlement revenue on
*true* consumption, and the company bills on its reads and estimates.

**Population and outcome:** as §7 and §8. Desk states at risk under `flat`, leavers under `flat`
within 365 days. Fit on 182 pre-2019 states, grade on 268 from 2019 (46 leavers). The household's
fuels and volume come from the book (`account_state_log`, the latest term per fuel on or before
`term_start`), never from the state's legs.

**Observables. Each is household-level (both legs), reads only artefacts dated before `term_start`,
and never reads a `true_*` field.**
- **S1, its own shock count.** The household's bills with `period_end` < `term_start` in the
  previous 365 days that have `bill_shock_yoy_pct` > 0.15 and are not `bill_shock_likely_seasonal`.
- **S2, the DD change.** On the household's latest `annual_dd_review` events (all legs, dated in
  the 365 days before `term_start`): Σ recommended / Σ current − 1. Direct-debit households only.
- **S3, the trailing-year bill rise.** Mean monthly `total_amount_gbp` (summed over legs) for bills
  ending in the 12 months before `term_start`, against the 12 months before that. In year one,
  against `opening_dd_by_customer` summed over legs. This is the company's copy of the world's
  definition, read from its billed amounts.
- **S4, the bill change it is about to send.** Σ over the book's fuels of (the new term's unit rate
  − the previous term's) × `company_eac_kwh`, as a share of S3's trailing-year annual bill.
- **C, composite, fitted pre-2019.** Logistic regression on the electricity leg's rate vs SVT plus
  S2 (0 for non-DD), S3 and S4, standardised. Graded on 2019+.
- **Placebo L.** The number of bills in S3's window. A leaver's billing history should not be
  shorter before the roll. If L ranks, the bill window leaks.
- **Reference W, an instrument, never a ranker.** The world's own `sim_experienced_bill_shock`
  (and `sim_bill_shock_base`) from `flat`'s `customer_events` at the state's roll. This is the
  ceiling a company copy could reach.

Bounds: an account-clustered bootstrap (1,000 draws, seed 7), the paired difference against the
belief, and against rate vs SVT alone (0.594 [0.479, 0.709]).

**Predictions (filed before any observable was computed, 18:14Z).**
- **P9a.** S3, 2019+: AUC point 0.60, range 0.50–0.70. Chance the lower bound clears 0.5: 35%.
- **P9b.** S2 on DD households: point 0.58, range 0.48–0.68.
- **P9c.** S1: point 0.55, range 0.45–0.65. It counts months, the retired quantity, and the
  seasonal flag removes some of what the world counts.
- **P9d.** S4: point 0.52, range 0.40–0.65. Rises are book-wide in the crisis, when departures are
  suppressed.
- **P9e.** C: point 0.63, range 0.52–0.72. Lower bound clears 0.5: 45%. Beats rate vs SVT alone with
  the paired bound above 0: 25%.
- **P9f.** W on these states: point 0.68, range 0.58–0.80. Placebo L inside 0.45–0.55.
- **Decision rule, fixed now.** (i) If S2, S3 or C clears 0.5, that is the belief's rebuild path.
  (ii) If W ranks (lower bound above 0.5) and no company observable clears 0.5, the gap is
  observability: what the company bills is not what the household experienced. Its size is W
  minus S3. (iii) If W does not rank on this population either, then 22 Sep's 0.70 does not carry
  to this book, and bill shock is not the aim here. (iv) If L ranks, every bill-window reading is
  void until the leak is named.

**Result (computed 18:15–18:24Z from `all_on` and `flat`; one seed, one book).**

*Rule (iv) fired first, and the leak is named.* On the window as pre-registered (bills ending in the
365 days before `term_start`), placebo L ranked leavers at **0.933**. 90 of 110 leavers had 13
billed months, against 1 of 340 stayers. **The departure writes a final bill dated before the
roll.** PROS-2018-0002 rolls on 2019-01-02, and its final bills run 2019-01-01 to 2019-01-01:
£1.13 for electricity, and a −£27.22 actual-read credit for gas. The bills are `all_on`'s, and
`all_on`'s departure at the roll is `flat`'s (§7: 37 of 37), so any artefact written by the leaving
can predate `term_start`. That short bill pulls the trailing-year mean down, which is why S3 first
read inverted. **Remedy:** every bill window is now the 12 full calendar months before the roll's
month, by `period_start`. After it, L reads 0.500. Everything below uses the remedied window.

| graded on the 268 states from 2019 (46 leavers), clustered 95% | AUC | minus rate vs SVT, paired |
|---|---|---|
| belief | 0.333 [0.253, 0.426] | [−0.36, −0.15] |
| rate vs SVT, electricity leg (§8) | 0.594 [0.479, 0.709] | — |
| S1 own shock count | 0.412 [0.328, 0.504] | [−0.34, −0.03] |
| S2 DD change (195 DD states with a review, 29 leavers) | 0.435 [0.322, 0.549] | [−0.31, +0.11] |
| S3 trailing-year bill rise | **0.337** [0.258, 0.416] | [−0.39, −0.12] |
| S4 bill change about to be sent | 0.625 [0.534, 0.710] | [−0.06, +0.12] |
| C fitted pre-2019 (rate vs SVT, S2, S3, S4) | 0.608 [0.512, 0.699] | [−0.05, +0.08] |
| W, the world's own shock (instrument; 209 states where it is defined, all years) | 0.495 [0.415, 0.581] | |
| placebo L / placebo DD-review count | 0.500 / 0.427 [0.350, 0.505] | |
| **the roll type: the term now ending was a fix** (company-visible, unfitted) | **0.818 [0.760, 0.868]** | **[+0.09, +0.35]** |
| roll type + rate vs SVT, fitted pre-2019 | 0.742 [0.652, 0.830] | [+0.10, +0.20] |

**Bill shock does not order departures on this book, not even in the world's own record.** The
company's copy of the world's quantity is close: S3 correlates 0.936 with the world's
`rise_fraction` where both exist. So what the company bills is not the gap. The world's shock
itself ranks at chance: 18 of 38 shocked states leave, and 76 of 171 unshocked ones do. Its
factor `sim_bill_shock_base` reads 0.510, while the world's `realized_churn_probability` reads
0.809 on the same 450 states. S3's 2019 inversion is the era: in 2019–21Q3 it reads 0.27; in the
crisis, bills rose 67% and 2 of 34 states left. S4's 0.625 is mostly the roll type (below).

**Why 22 Sep's 0.70 does not carry.** 22 Sep graded the world's old month-count base, before
PB4 (2026-10-01) swapped it for one shock per year. On the end-of-fix rolls here, the month-count
base, which still rides on the event, reads 0.548, and the PB4 base 0.520. The 0.70 was a
different book, on a quantity the world has since retired. §8's pointer to bill shock rested on
that reading and is withdrawn here.

**What does order departures is when the roll happens.** In `flat`, the world rolls departure dice
only at `renewal` occasions, the end of a fix: 181 desk states, 93 of them leavers. At
`svt_conversion` (150) and `declined_fix` (119) it rolls none, and those events carry no factor
fields. Of the 18 leavers whose electricity leg's previous term was not a fix, 11 left on SVT
drift (`svt_inertia`). The other 7 left the same day at a `renewal` roll that the electricity
leg's previous term does not mark as a fix. Which leg's term the world read there is not traced. From 2019,
end-of-fix rolls lose 40 of 92 households, and the other rolls lose 6 of 176. **The belief has it
backwards:** its mean is 0.193 on end-of-fix rolls and 0.378 on the others. That inversion is §7's
0.333. The company knows the previous term's tariff type before the roll, so this is not a leak.
Pre-2019 the roll type reads 0.597, because more of that era's leavers drift from SVT.

**Inside end-of-fix rolls (2019+, 92 states, 40 leavers), almost nothing ranks.** The belief reads
0.504. Rate vs SVT reads 0.621 [0.501, 0.740]. S1, S2, S3 and S4e read 0.44–0.53, and the world's
shock base 0.502. Even the world's own `realized_churn_probability` reads only 0.653 [0.535,
0.762]. That is the ceiling: within the rolls that matter, the world holds little orderable
signal, and price position is the only company observable near it.

**Grading P9.**
- **P9a REFUTED.** S3 reads 0.337, below 0.50–0.70, inverted by the era.
- **P9b REFUTED.** S2 reads 0.435, below the 0.48 floor.
- **P9c REFUTED.** S1 reads 0.412, below the 0.45 floor.
- **P9d HELD in range, void in reason.** S4 reads 0.625, but it is the roll type. On the electricity
  leg inside end-of-fix rolls, it reads 0.524.
- **P9e HELD in range.** C reads 0.608, and its bound (0.512) clears 0.5, but C weighs S4. It does
  not beat rate vs SVT (the 25% leg did not happen).
- **P9f REFUTED.** W reads 0.495, below 0.58–0.80. Placebo L was 0.933 on the pre-registered
  window: the leak, as rule (iv) anticipated.

**By the decision rule.** (iv) fired and was remedied. (i) is satisfied only by C, whose weight
is S4, which is the roll type, so no bill-shock observable is the rebuild path. **(iii) holds:
the world's own shock does not rank on this population, so bill shock is not the aim here.** The
renewal-advice build's aim is the roll type plus price position (0.742, fitted pre-2019, beats
rate vs SVT alone with the paired bound above 0). The first rebuild of the belief is to condition
on the roll type. That is a modelling gap, not an observability gap: the company holds the
tariff type and does not use it. Inside end-of-fix rolls the ceiling is about 0.65, so advice
there is aimed by price position or not at all. **Whether the world is right** to roll no departure
risk at an SVT conversion, and to let SVT drift lose only 6 of 176 a year from 2019, is a world
question decided blind to these results. It is not settled here. A published figure on switching
from default tariffs against at fix end would settle it.

**Named, not fixed: why `flat` records no gas `churned` event for a dual household that leaves at
its electricity roll.** `simulation/run_phase2b.py` rolls one departure per household on the leg
`departure_decision_leg` returns (`simulation/customer_events.py`): electricity for every account
that holds an electricity leg. The household-level skip ("Phase 6b: skip churned accounts", in
the term loop) then drops the gas leg's next term without emitting anything. PROS-2018-0002:
one `churned` row (electricity, 2019-01-02, cause `dissatisfaction`); the gas term ends 2019-01-02
with no successor and no event. So the gas leg's departure exists only by the absence of its next
term. Any reader that counts departures per leg (gas churn rates, `company_gas_churn_log`'s
grading) undercounts gas, and the desk sees the household as electricity-only at the roll (§8).
In `flat`'s book the electricity leg also carries a 2019-01-02 term after the departure. Whether
those readers should be keyed by household or the world should emit the gas leg's event is
unasked.

Scripts: `/tmp/pcs9/{grade,score,diag,s4,s4leak,eof,last}.py`, scratch only and not landed.

## 10. The renewal churn belief, conditioned on the term now ending (2026-10-21, no run launched)

*The rebuild §9 named: the company holds the tariff type of the term that is ending, and its belief
ignores it. This section grades a default-off switch that conditions the belief on it, fitted only
on what the company could see before 2019 and graded on §7's 268 states from 2019.*

**One correction to the item, found before any outcome was read.** The item lists three roll
types (fix, default/SVT conversion, declined fix) and says the company knows each before the roll.
Two of them it does. **A fix declined AT THIS ROLL is not one of them:** `declined_fix_event` is
written only for a household that *stayed* (`event_type` is always `renewed`, and
`customer_events.declined_fix_event` raises on any other), at the roll's own date. Used as a
feature, it would mark non-leavers by construction. What the company does know before the roll is
whether the default stint now ending *began* with a fix the household declined at an earlier roll.
So the three types are, all read off the decision leg's previous term:
- **`fixed`**: the term ending is a fix (the end-of-fix renewal).
- **`default`**: the term ending is a default-tariff stint the household was rolled or placed on.
- **`default_after_declined_fix`**: the term ending is a default-tariff stint spliced in because the
  household refused our fix at an earlier roll (`_DECLINED_FIX_SPLICE`).

**The mechanism (built to the design below before scoring).** Per type, the company keeps the
renewals it priced, the belief it held on each, and how many of those accounts it then lost at a
renewal. These are the same competitive losses `CompetitivePressureLedger` already books, attributed
to the account's roll as B8 attributes its price moves. For a renewal in year Y, it reads only rolls
from years before Y. The multiplier is observed over expected, with the ledger's own Jeffreys
continuity correction: `m = ((losses + 0.5) / (n + 1)) / (Σ belief / n)`. It is applied in survival
space, `p' = 1 − (1 − p)^m`, so the order within a type is the belief's own and `p'` stays in [0, 1].
No prior and no shrinkage are applied. A type with no closed renewals is left unconditioned. The
belief is booked into every existing learner *before* conditioning, so the switch moves no other
learner's evidence.

**Grade.** Population and outcome as §7–§9: desk states at risk under `flat`, leavers under `flat`
within 365 days, fuels from the book. The fit reproduces what the company sees at 2019-01-01: the
182 pre-2019 desk states with their `all_on` beliefs, and `all_on`'s own roll-date departures dated
before 2019-01-01. Only departures at a roll reach the ledger. The SVT-drift departures in
`svt_departures` do not, so the fit does not see them either. The conditioned belief is computed by
the company's own functions on those counters. Bounds as before: account-clustered bootstrap, 1,000
draws, seed 7, and the paired difference over the same states.

**Predictions (filed 2026-10-21 before any count by type or outcome was computed).**
- **P10a.** The conditioned belief, 2019+: AUC point 0.80, range 0.72–0.86. Lower bound above 0.5:
  97%. Reason: §9's unfitted binary roll type reads 0.818 with half-credit ties. A chance-level
  ordering inside each type breaks those ties at the same expected value, so separation near 0.8
  is kept if `m_fixed` lifts every end-of-fix belief above every default one.
- **P10b.** Paired against the current belief (0.333): bound above 0, 99%. Against rate vs SVT
  (0.594): bound above 0, 85%. Against roll type + price (0.742): point +0.05, and the paired bound
  spans 0, 70%.
- **P10c.** No pre-2019 roll-date departure in `all_on` follows a default-tariff term, because the
  world rolls no departure there (`departure_rolled_at_renewal`): 90%. So `m_default` is set by the
  continuity correction alone, and lies below 0.15: 85%.
- **P10d.** From 2019, under `flat`, the `default_after_declined_fix` states leave more often than the
  `default` states within 365 days: 55%. This is near a coin, because a refusal marks engagement and
  a stay at once.
- **P10e.** Calibration: the mean conditioned belief from 2019 is within 0.10 of the realised rate
  (46/268 = 0.172): 60%. The current belief's mean is 0.357 against 0.244 over all states.
- **Decision rule, fixed now.** If P10a's lower bound clears 0.5 and the paired bound against the
  current belief is above 0, the switch is the belief's first rebuild. It is then the arm the next
  per-customer arms run should carry. This section flips nothing. If the conditioned belief reads
  below 0.742 with the paired bound below 0, price position is the next term, ahead of any advice
  build. If the lower bound does not clear 0.5, the mechanism, not the roll type, is wrong. The
  first suspect is then the roll-date-only loss feed.

**Result (computed 20:43–20:55Z, after the predictions above were on origin at 3e281075a; one seed,
one book).** The conditioned belief is computed by `ending_term_multiplier` and
`condition_on_ending_term` themselves, on a ledger fed only the pre-2019 desk states and `all_on`'s
roll-date losses dated before 2019-01-01.

| fit, pre-2019 (what the company sees at 2019-01-01) | renewals | lost at a roll | mean belief | multiplier |
|---|---|---|---|---|
| `fixed` | 132 | 52 | 0.392 | **1.006** |
| `default` | 46 | 0 | 0.491 | **0.022** |
| `default_after_declined_fix` | 4 | 0 | 0.501 | 0.199 |

| graded on the 268 states from 2019 (46 leavers), clustered 95% | AUC | paired differences |
|---|---|---|
| belief (current) | 0.333 [0.253, 0.426] | |
| rate vs SVT | 0.594 [0.479, 0.709] | |
| roll type + price, §9's definition, reproduced | 0.742 [0.652, 0.830] | |
| **conditioned belief, switch on, fit before 2019** | **0.819 [0.757, 0.877]** | − belief [+0.386, +0.579]; − rate vs SVT [+0.105, +0.353]; − §9's roll + price **+0.077 [−0.014, +0.173]** |
| the same, read online (each year from the years before it) | 0.833 [0.773, 0.889] | |
| roll type alone, this section's definition | 0.835 [0.783, 0.881] | |
| roll type + price, this section's definition | 0.799 [0.730, 0.864] | conditioned − this: [−0.049, +0.100] |

By type, from 2019: `fixed` 42 of 96 leave (mean belief 0.189, conditioned 0.190); `default` 3 of
152 (0.388 becomes 0.026); `default_after_declined_fix` 1 of 20 (0.363 becomes 0.103).

**What it says.** The current belief ranks backwards because it puts its highest beliefs on the
default-tariff rolls. Those are 57% of the states and lose 2% a year. The company's own pre-2019
book has already lost 52 at fix-end rolls and none at default rolls. A multiplier read off that
history moves 0.388 to 0.026 on the default rolls and leaves the fix-end level where it was
(m = 1.006). Inside the fix-end rolls the belief still ranks at chance (0.515, against rate vs
SVT's 0.611). That is why the conditioned belief sits just under the roll type alone. The
belief's own ordering inside a type adds nothing. The level it now takes from the type is all
of the gain.

**Two definitions of roll type, and why §9's comparator reads lower.** §9 marked a state "fix" only
where the book holds the electricity leg's new term at `term_start`. A fix declined at that roll
has its book row withdrawn (the splice), so §9 counted it as "not a fix". This section reads the
decision leg's latest term before the roll. The two disagree on only 4 of 268 states from 2019,
but they fit different pre-2019 weights. The item's 0.742 is §9's definition, reproduced exactly
above.

**Grading P10.**
- **P10a HELD.** 0.819, inside 0.72–0.86, point 0.80. The lower bound, 0.757, clears 0.5.
- **P10b HELD on all three legs.** Against the belief and against rate vs SVT the paired bound is
  above 0. Against roll type + price the point is +0.077 on §9's comparator (+0.020 on this
  section's), and the bound spans 0, as filed.
- **P10c HELD.** No pre-2019 roll-date loss follows a default term. `m_default` = 0.022 < 0.15.
- **P10d HELD in direction, void in size.** 1 of 20 against 3 of 152 is one leaver. Nothing can be
  read from it.
- **P10e HELD at the edge.** The mean conditioned belief is 0.090 against 0.172 realised (0.082
  apart, inside 0.10). It under-predicts because only roll-date losses reach the ledger. The 4
  leavers on default rolls all leave after the roll, and SVT-drift departures are never booked. The belief is "P(leave at
  this renewal)", so this is its definition, not a leak. But a 365-day reader of it will read low.

**By the decision rule: the switch is the belief's first rebuild,** and it is the arm the next
per-customer arms run should carry (`renewal_belief_by_ending_term=True` beside `all_on`). This
section flips nothing. Price position is not shown to add to it on 46 leavers. Inside fix-end
rolls it is the only observable near the world's ceiling (§9: 0.62 against about 0.65), so it is
the next term, and it is graded where it matters (fix-end rolls), not over the whole desk.

**What this does not settle.** One seed. The fit population is the desk's (resi rolls with a
contribution). In a run the ledger books every renewal the belief is asked about, so its counts
will be larger. No control holds the run loop's leg: a run that stops handing the type over reads
"off". The controls hold the desk, the ledger and the mapper (two mutants, each red). The
mapper's import into `run_phase2b` is pinned by identity, which is a name, not a consumer. **The
world question §9 named is unchanged.** If the world is wrong to roll no departure at a default
anniversary (EFTC 2019 gives 6% external in the six weeks after a fix lapses: knowledge page §5),
then this multiplier learns the world's rule, not the market's. Under that reading 0.022 is the
number most exposed. Scripts: `/tmp/pcs10/{grade,diff,ref9}.py`, scratch only and not landed.

## 11. The conditioned belief in the run: `all_on_ending_term` against `all_on` and flat (filed 2026-10-21 ~21:35Z, before the arm was launched)

*The arm §10's decision rule names. `tools/per_customer_switch_arms.py all_on_ending_term` is
`all_on` plus `renewal_belief_by_ending_term=True`, nothing else (the arm control pins the
difference to that field and the name). It runs on the code at `7a7ad95dc`, one seed, the same
book as §6. It is graded against `all_on.json` and `flat.json` in `/var/tmp/se-pcs-arms-out/`.*

**Where the switch reaches in the run (read from `simulation/run_phase2b.py` before predicting).**
The conditioned `company_est_pre` feeds four places: the retention gate (`> RETENTION_THRESHOLD`,
0.30), the offer's risk-tier sizing, the holdout's `stay_belief`, and the renewal desk's
`monthly_hazard`. It also reaches the world's roll as `precomputed_company_estimate`, but there it
is only recorded after `resolve_departure` has drawn the outcome, so it cannot move a departure.
The multiplier for year Y reads only closed renewals from years before Y, so 2016 is unconditioned.

**Setup facts read from `all_on` (no outcome of the new arm).** These are typed by §10's `kind_at`.
- Retention offers: 113. 102 follow a `fixed` term and 11 a default-tariff term (9 `default`, 2
  `default_after_declined_fix`). The 11 are dated 2018-12 to 2024-01 at beliefs 0.40 to 0.89, and
  every one reads `retained`. Their cost is about £450 in total.
- Desk states: the desk's 2019+ `default` states have a mean `monthly_hazard` of 0.0609 (p ≈ 0.53).
  Their advised rows are 295 of 456. The `fixed` 2019+ states have 180 of 300 advised.
  STATED_ADVICE_EFFECTS cuts the hazard by 0.001 or 0.003 a month, clamped at the household's own
  hazard.

**Predictions.**
- **P11a, the hand-over (the control the tests cannot hold).** On desk states present in both arms
  with a `default` or `default_after_declined_fix` ending term and `term_start` ≥ 2017-01-01,
  `monthly_hazard` is lower in the new arm than in `all_on` on at least 95% of them: 95%. On
  `term_start` < 2017-01-01 states it is identical on every one: 90%. A run that drops the type
  reads identical everywhere. That is the refutation this exists for.
- **P11b, in-run aim.** The new arm's desk belief, `p = 1 − (1 − h)^12`, is graded on §9/§10's 268
  states from 2019 with `flat` outcomes (states absent from the new arm's desk are dropped and
  counted). AUC point 0.81, range 0.74–0.86. Account-clustered lower bound above 0.5: 95%. The
  in-run ledger books every renewal the belief is asked about, not only desk states, so the
  multipliers differ from §10's. `m_default` stays below 0.15 in every year from 2018: 85%.
- **P11c, retention.** Offers fall from 113 to between 95 and 112, point 103. The default-term
  offers from 2017 on disappear (≤ 1 remains): 85%. The fix-end offers stay within ±8 of 102: 75%.
  This is because `m_fixed` ≈ 1 moves only states near 0.30. Retention cost falls by £200 to £800,
  point £450.
- **P11d, advice.** Advised rows on 2019+ default-term states fall from 295 to below 200, point 100.
  The cut clamps at a hazard near 0.0014, so the advice buys almost no retention and the rise needed
  exceeds headroom more often: 80%. Fix-end advised rows stay within ±25 of 180: 75%. The desk's
  claimed `value_change_gbp` total (§6: £121) falls: 70%.
- **P11e, departures.** The world rolls no departure at a default-tariff renewal
  (`departure_rolled_at_renewal`). So removing offers there removes no save. Departures are 354 ± 3:
  80%. Save log: 1 saved, as in `all_on`: 80%.
- **P11f, the sum against flat.** `all_on` − flat was −£96.55. The new arm − flat in
  `provisioned_net_gbp`: point +£350, range [−£1,500, +£2,000], positive 60%. On one seed, anything
  inside ±£1,000 is a tie and is graded as one. Against `all_on`: point +£450 (the default-term
  discounts not given), positive 70%.

**Decision rule, fixed now.** If P11a fails, the run does not carry the switch. That is a defect in
the run loop, the next item, and nothing else here is graded. If P11a holds and P11b's lower bound
clears 0.5, the switch is shown to carry its aim into the run. It becomes the candidate for
CURRENT_POLICY. That is a policy change (G9-free: no director ruling names this field), but it is
proposed separately, not flipped here. If the money against flat is a tie, as I expect, the
finding is that better aim alone does not create value on this book. The next lever is then the one
§6 named, sending the desk's advice to the world as an act. It does not come from refining the
belief further.

**Launched 2026-10-21 21:39Z.** Unit `longjob-pcs-arm-all-on-ending-term`. It runs from the locked worktree
`/var/tmp/se-pcs-arms4` (HEAD `7a7ad95dc` plus this commit's arm-tool change, no other diff) and
writes `/var/tmp/se-pcs-arms-out/all_on_ending_term.{json,log}`. Expect about 2.5 h, as §6's arms took.

### 11. Grade (2026-10-21 ~22:40Z, `all_on_ending_term.json` present, rc=0)

**What ran.** Unit `longjob-pcs-arm-all-on-ending-term`, 21:39–22:32Z (53 min). The output stamps
`7a7ad95dc` and tags `all_on_ending_term`. Graded by `/tmp/pcs11/grade.py`, which reuses §10's
`kind_at`, §9's 268 rows and the same bootstrap. Run with `all_on.json` in place of the new arm as a
placebo, it reproduces §6 to the penny and reads "hand-over failed": no state lower, AUC 0.333.

| figure | flat | all_on | all_on_ending_term |
|---|---|---|---|
| `provisioned_net_gbp` | £600,902.77 | £600,806.22 | **£602,027.96** |
| `provisioned_bad_debt_gbp` | £125,212.58 | £124,805.98 | £125,318.59 |
| departures | 353 | 354 | 353 |
| retention offers / cost | 0 / £0 | 113 / £2,837.65 | **134 / £3,382.15** |
| desk rows / claimed value | – | 1,362 / £121.0 | 1,368 / £112.5 |
| bills | 53,256 | 53,314 | 53,446 |

- **P11a HELD: the run loop hands the type over.** On default-term desk states from 2017, present in
  both arms, `monthly_hazard` is lower on 216 of 222 (97.3%). That is 194 of 198 `default` and 22
  of 24 `default_after_declined_fix`. The 6 that are not lower include the one 2017 `default` state,
  where the multiplier is unconditioned because 2016 closed no default renewal. The pre-2017 leg
  holds on 2 of 2 states, both identical. That is a small population and is read as such. Fix-end
  states from 2017 read **higher** on 222 of 229. I did not predict that, and the next bullet is why.
- **The in-run multipliers, implied per state as `ln(1−p')/ln(1−p)` (median by type and year).**
  `default` reads 0.42 in 2018 (fit on 2017 alone), then 0.022 in 2019, falling to 0.006 by 2025.
  §10 read 0.022 offline. **`fixed` reads 3.39 in 2017, fit on 2016's closed renewals alone,** then
  1.01 to 1.23 from 2018. §10's design applies "no prior and no shrinkage". So in the run's first
  conditioned year, one year of the company's own history triples the fix-end hazard in survival
  space. Offline §10 fitted at 2019-01-01 only, so it never met this year.
- **P11b HELD.** In-run AUC is 0.819 [0.757, 0.873] on all 268 states. Paired against the `all_on`
  belief it is [+0.383, +0.578]. The mean belief is 0.092 against 0.172 realised, the under-read
  §10's P10e named.
- **P11c REFUTED on count, direction and cost.** Offers rose to 134 (range 95–112). Default-term
  offers fell from 11 to 3, against "≤ 1". The 2 `default_after_declined_fix` offers that remain are
  dated 2018-12 and 2019-03, where that type's multiplier was still 0.90 and 0.35. Fix-end offers
  rose from 102 to 131, against ±8. Cost rose £544, where I predicted a fall of £450. The cause is
  the 2017 fix-end multiplier above. It was in the design §10 published, and I missed it when I
  wrote §11.
- **P11d HELD.** Advised 2019+ default rows fell from 295 to 160 (below 200; my point was 100). Fix-end
  rows went from 180 to 175 (±25). Claimed value went from £121.0 to £112.5.
- **P11e HELD on count; its reasoning is REFUTED.** Departures are 353 and 1 save, both in range.
  But the departure sets differ by five households. Under the new arm SYN-2016-399 and SYN-2016-541
  leave, as they do under flat. Under `all_on` PROS-2016-0098, SYN-2016-369 and OCC-d69e9e947a9e
  leave instead. SYN-2016-541's `all_on` offer was a **default-term** one (2023-11-24, belief
  0.74). Without it the household leaves later. So "the world rolls no departure at a default
  renewal, so a default-term offer buys nothing" is wrong: the offer's rate carries into the
  later SVT-drift hazard. PROS-2016-0098 gets a second offer (2021-03-30) under the new arm and
  stays.
- **P11f: in range, outside the tie band, NOT attributable.** New − flat is **+£1,125.18** (range
  [−£1,500, +£2,000], point +£350). New − `all_on` is +£1,221.73 (point +£450). Revenue is £7.8k
  higher on 132 more bills, and bad debt £513 higher. More than one thing changed: the 2017 fix-end
  offers, the withdrawn default-term offers, and which five households leave. **I cannot yet say**
  whether better aim made the money. Five households trading places on one seed is the same size
  of swap as flat against `current` in §6 (F2). So I grade it as book divergence until seeds
  separate it. Erring against the thesis (F11), the reading is a tie of about £1k on one seed, not
  value created.

**By the decision rule.** P11a holds and P11b's bound clears 0.5. The switch carries its aim into
the run. **It is not yet the candidate for CURRENT_POLICY** that the rule names, because the run
showed a defect the offline grade could not reach. The first conditioned year reads a multiplier of
3.39 off one year of history. That is a number the mechanism picks for itself because a number
was needed, which is the K2 failure, and it is what moved the offers and their cost. The next step
is knowledge first (K8): what published evidence gives as the fix-end and default-tariff switching
rate a supplier could hold as a prior. EFTC 2019 is on the knowledge page §5. The step then decides
between that prior, with the ledger's counts shrinking toward it, and a minimum closed-renewal count
before a type's multiplier applies, the latter refusing with a named reason. After that the arm
reruns. The money question stays open, and seeds are what answer it (EP17).

## 12. The ending-term multiplier shrunk towards the belief: `all_on_ending_term` again (filed 2026-10-21 ~22:55Z, before the arm was launched)

*§11's defect: with no prior, the 2016 closed fix-ends set m = 3.39 for 2017. The desk-state
reconstruction puts that at 2 renewals and 1 loss. The knowledge page now gives the multiplier a width
(`docs/market_research/switching_gradient_by_tariff_and_payment_what_the_record_can_grade.md` §5a).
EFTC's fix-end window against CMOC's default flow is 2.9× at the lower published end, so the prior
variance in log space is (ln 2.9 / 2)² = 0.28. The multiplier is now `ratio^w`, with the ledger's own
`w = V_prior / (V_prior + V_evidence)`, centred on 1. No minimum count is used: that would be a picked
number. The arm, book and seed are §11's. Only `ending_term_multiplier` differs. The output goes to
`/var/tmp/se-pcs-arms-out/all_on_ending_term_prior.json`, so §11's file stays as evidence. It is
graded by `/tmp/pcs11/grade.py` with `ARM=` pointed at it.*

**Predictions (no outcome of this arm read).**
- **P12a, the defect itself.** The implied `fixed` multiplier for 2017 (median, as §11 measured it)
  is between 1.0 and 1.6, point 1.2: 85%. `fixed` from 2018 is within 0.05 of §11's 1.01–1.23 in each
  year: 80%. `default` from 2019 is below 0.10 in every year: 85%. For 2018 it is above §11's 0.42:
  85%.
- **P12b, the hand-over and the aim.** Default-term desk states from 2018 that are present in both
  arms read lower than `all_on` on at least 95% of them: 90%. The in-run AUC on §9's 268 states is
  0.815, range 0.76–0.85. Its clustered lower bound is above 0.5: 97%.
- **P12c, retention (the leg §11 refuted).** Offers number 112, range 100–125 (`all_on` 113, §11 134).
  Fix-end offers are 102–120: 75%. Default-term offers are ≤ 3: 85%. Cost is £2,850, range £2,500–£3,200
  (`all_on` £2,837.65, §11 £3,382.15).
- **P12d, departures.** 353 ± 3: 80%.
- **P12e, money.** On one seed, anything within ±£1,000 of flat is a tie. Point against flat +£300,
  and graded as a tie unless outside the band. This section cannot answer the money question. Seeds
  answer it (EP17).

**Decision rule, fixed now.** If P12a's 2017 leg holds and P12b holds, the switch is the candidate
for CURRENT_POLICY. It is proposed separately, with the seeds the money question needs, and nothing
here flips it. If 2017 still reads above 1.6, the in-run counts for 2016 are larger than the
reconstruction says. Then the next step is to read the ledger directly, not to widen the prior.

**Launched 2026-10-21 22:53Z**, after the predictions above were on origin at `e856ddc69`. Unit
`longjob-pcs-arm-all-on-ending-term-prior`, run from the seat-executor worktree at that commit.

### 12. Grade (2026-10-22 ~00:55 BST, `all_on_ending_term_prior.json` present, stamped `e856ddc693`)

| figure | flat | all_on | §11 (no prior) | §12 (prior) |
|---|---|---|---|---|
| `provisioned_net_gbp` | £600,902.77 | £600,806.22 | £602,027.96 | **£601,014.02** |
| `provisioned_bad_debt_gbp` | £125,212.58 | £124,805.98 | £125,318.59 | £125,074.21 |
| departures / saved | 353 / 1 | 354 / 1 | 353 / 1 | 354 / 1 |
| retention offers / cost | 0 / £0 | 113 / £2,837.65 | 134 / £3,382.15 | **122 / £2,968.23** |
| implied `fixed` m, 2017 (median, 95 states) | – | – | 3.386 | **1.215** |

- **P12a HELD on all four legs.** `fixed` for 2017 is 1.215, inside 1.0–1.6 (point 1.2). From 2018
  every year is within 0.05 of §11: 1.014 / 1.03 / 1.073 / 1.219 / 1.159 / 1.20 / 1.228, against
  1.015 / 1.014 / 1.061 / 1.21 / 1.157 / 1.19 / 1.231. `default` from 2019 is 0.028 at most. For
  2018 it is 0.778, against §11's 0.42. Reading back, the in-run 2016 weight is
  `ln 1.215 / ln 3.386` = 0.16, which is the small-n weight the reconstruction implied.
- **P12b HELD.** Default-term desk states from 2017 that are present in both arms read lower on 215
  of 222 (96.8%). In-run AUC is 0.806 [0.745, 0.860], inside 0.76–0.85. Paired against the `all_on`
  belief it is [+0.373, +0.562]. That is 0.013 below §11's 0.819, and the cause is the shrunk
  2018/2019 default multipliers (0.78 and 0.51 for `default_after_declined_fix` in 2019, where
  §11 read 0.42 and 0.35). The prior costs a little aim in the young years. That is the trade it was
  built to make.
- **P12c HELD on count, fix-end and cost; REFUTED by one on default-term offers.** There were 122
  offers (range 100–125). Fix-end offers were 118 (range 102–120) and default-term offers 4,
  against ≤ 3. Cost was £2,968.23 (range £2,500–£3,200). Fix-end offers are still 16 above
  `all_on`, because `fixed` reads 1.01–1.23 in every year, not 1. That is the company's own
  book, now weighed, not a picked number.
- **P12d HELD.** 354 departures.
- **P12e: a tie.** New − flat is **+£111.25** and new − `all_on` is +£207.80, both inside ±£1,000.
  §11's +£1,125 against flat fell by £1,014 when only the multiplier's first years changed. I cannot
  yet say how much of that was the 2017 offers and how much was the five-household swap §11 named.
  It does show that §11's £1k was not a property of the switch. Erring against the thesis (F11), the
  switch has not been shown to create value on this book.

**By the decision rule: the switch is now the candidate for CURRENT_POLICY**, with the K2 defect
§11 found removed and its aim kept (P12a, P12b). It is proposed separately, with the seeds the
money question needs (EP17). Nothing here flips it. The grade used `/tmp/pcs11/grade.py` unchanged,
with `ARM=` pointed at the new output, and it re-read §11's output to give the comparison column.

## 13. The retention guard weighs its own save odds: `all_on_save_odds` against §12 and flat (filed 2026-10-22, before the arm was launched)

*Drawn as `the-retention-guard-weighs-its-save-odds-by-the-ending-term-belief`. §12 held P12a's 2017 leg
and P12b, so the item proceeds. Knowledge first:
`docs/market_research/a_save_offer_against_the_switching_rules_and_the_seam.md` §9. No published source
gives the save rate of a discounted retention offer at a domestic fix end (GAP). The one randomised
supplier contact, EFTC, moved external loss 6% → 6%.*

**What changed (one field).** `retention_weighs_save_odds`. With it on, the guard's value is
belief at the roll × the company's own save rate × the value it already protects. The save rate is
per ending-term type, over offers in years before the roll: `1 − observed/expected` losses on the
accounts it offered, Jeffreys-corrected, floored at 0. Where a type has no closed offers, the
standing guard decides. The arm is `tools/per_customer_switch_arms.py all_on_save_odds`, which is
§12's `all_on_ending_term` plus this field and nothing else. The book and seed are §12's. Output:
`/var/tmp/se-pcs-arms-out/all_on_save_odds.json`.

**Setup facts read from §12's output (`all_on_ending_term_prior.json`), not from this arm.**
`/tmp/pcs13/setup.py` reconstructs the rate from `retention_log` outcomes by §10's `kind_at`.
- Offers by type and year: fixed 2017 83 (42.1 predicted losses, 34 lost), fixed 2018 20,
  fixed 2019–2025 15, default 2018 3, default_after_declined_fix 2018 1. No offers were made in 2016.
- So 2017 decides on the fall-back. From 2018 the fix-end save rate reads 0.19 (0.18–0.24 by 2025).
  Default-term types first have closed offers in 2019, when no default-term offer was made.
- At s = 0.19, belief × s × value beats cost on 0 or 1 of the 35 fix-end offers from 2018. The median
  belief is 0.46, but value protected is £14–£120 against costs of £0.4–£107.
- **A limit the design carries, named now.** Once the guard stops offering on a type, no new offers
  close, and the rate freezes at what 2017 taught. Only a holdout, or offers made to explore, would
  re-open it. This arm cannot test whether the rate would have risen.

**Predictions (no outcome of this arm read).**
- **P13a, the hand-over.** The 2017 offer set (account, date) is identical to §12's 83: 85%. Every
  offer from 2018 that follows a fix carries a `save_rate` in the log: 95%. A run in which no
  2018+ offer carries one, while 2018+ offers stay near §12's 35, has dropped the field.
- **P13b, retention.** Fix-end offers from 2018 number 0–4 (§12: 35), point 1: 85%. Default-term
  offers in 2018 number 3–5, point 4 (fall-back): 80%. Total offers are 85–92, point 88. Cost is
  £1,450–£1,950, point £1,650 (§12 £2,968.23).
- **P13c, departures.** 354 ± 4: 80%. Per §7, the offers kept no one at the roll they priced, so
  withdrawing them should move only the few that carry into a later SVT-drift hazard. Point 355.
- **P13d, money.** The discount not given is about £1,300. New − §12 is +£800, range
  [−£1,000, +£2,000], positive 70%. New − flat is +£900. On one seed anything within ±£1,000 of flat is
  a tie and is graded as one (EP17). This section cannot answer whether the guard creates value.
- **P13e, the aim is untouched.** The desk's beliefs are the same as §12's on the states present in
  both arms (AUC on §9's 268 states within 0.01 of 0.806): 85%. The field reads the belief and does not
  write it.

**Decision rule, fixed now.** If P13a fails, the run does not carry the field, and that is the next
item. If P13a and P13b hold, the company's own evidence says its fix-end offers save about one in
five of the losses it predicts, and that this pays on almost none of them. The guard is then a
candidate beside the §12 switch, proposed with seeds, and nothing is flipped here. If P13c fails
upward (more than 358 departures), the offers were saving households that the outcome-at-the-roll
reading in §7 missed. In that case the save rate's definition is wrong before its value is, and that
is written up before any seeds are run.

**Launched 2026-10-22 01:29 BST**, after the predictions above were on origin at `7bab213af` (field and
predictions in `0674199b8`). Unit `longjob-pcs-arm-all-on-save-odds`, run from the locked worktree
`/var/tmp/se-pcs-arms13` (detached at `7bab213af`), writing
`/var/tmp/se-pcs-arms-out/all_on_save_odds.{json,log}`. Expect about an hour, as §12 took. The grade
script is `/tmp/pcs13/grade.py`. Its placebo, with §12's output standing in for the new arm, reads §12
back to the penny: the 2017 set identical, 35 fix-end offers from 2018 with no `save_rate`, +£0.00.

### 13. Grade (2026-10-22 ~02:40 BST, `all_on_save_odds.json` present, unit rc=0, stamped `7bab213af7`)

| figure | flat | §12 (`all_on_ending_term_prior`) | §13 (`all_on_save_odds`) |
|---|---|---|---|
| `provisioned_net_gbp` | £600,902.77 | £601,014.02 | **£600,203.83** |
| `provisioned_bad_debt_gbp` | £125,212.58 | £125,074.21 | £124,885.18 |
| departures | 353 | 354 | 354 (same set as §12) |
| retention offers / cost | 0 / £0 | 122 / £2,968.23 | **88 / £1,644.07** |
| fix-end offers from 2018 | – | 35 | **1** (`save_rate` 0.1896, 2018) |

- **P13a HELD on both legs.** The 2017 offer set is identical to §12's 83 (none only in one arm). The
  one fix-end offer from 2018 carries `save_rate` 0.1896.
- **P13b HELD on every leg.** Fix-end offers from 2018: 1 (0–4, point 1). Default-term offers in 2018:
  4, 3 `default` + 1 `default_after_declined_fix` (3–5, point 4). Total: 88 (85–92, point 88). Cost:
  £1,644.07 (£1,450–£1,950, point £1,650).
- **P13c HELD.** 354 departures, and the same set of accounts as §12. The 32 offers from 2018 that
  §12 made and this arm withdrew (paired on account, roll and fuel in `customer_events`) changed no
  household's choice to stay or leave. 11 left in both arms and 21 stayed in both. The company's
  estimate is that about one in five predicted losses is saved. At the roll, the world saved none
  of these 32, which is §7's reading again.
- **P13d: the size of the discount held; the sign was REFUTED.** The discount not given was
  £1,324.16 (predicted about £1,300). But new − §12 is **−£810.19**: inside the range
  [−£1,000, +£2,000], but against the point of +£800 and the 70% I gave to a positive result.
  New − flat is −£698.94, which is a tie under the rule (±£1,000, EP17).
  **Where the money went:** almost all of it moved through a channel I did not predict. A
  withdrawn offer to a household that stays either way can still change its tariff. 5 of the 21
  households that stayed were above the default with §12's discount removed, so the dominance rule
  (`renewal_outcome`: stay but decline a fix priced above the default) put them on the default. In §12 the
  discount had moved them below parity, and they fixed. Example: PROS-2016-0263, at its 2018-09-16
  roll, had the same roll (0.1911) in both arms. With the 3% discount it was −1.28% against the
  default; without it, +1.77%. It sat on the default from then on. Those 5 households move gross by
  about −£2.4k (0263 with its gas leg −£2,313; 0223 −£176; 0092 −£101; 517 +£186; 368 +£18). Every
  other account together moves −£3. Revenue on them falls £3.6k, which those households did not pay
  because they were on the default. **By M2, that is transfer, not creation.** In §12 the offers
  earned their £810 by moving households who were not leaving onto a fix that later cost them more
  than the default. They saved nobody. The guard's value term, belief × save rate × protected
  value, does not price this channel, and the save rate it learns cannot see it.
- **P13e: the AUC leg HELD; the identity leg was REFUTED.** In-run AUC on §9's 268 states is 0.805
  [0.743, 0.859], within 0.01 of 0.806. But the desk's beliefs are identical to §12's on only 306 of
  the 451 states present in both arms. 145 differ (2019–2025, median relative difference 1%, max
  5.4×), and 3 states exist only in §12. The field does not write the belief, but it does change
  the book the belief reads: the 5 households that moved to the default change which ending-term
  type each later state carries. That is the likely cause. I did not isolate it, so I cannot yet say
  it accounts for all 145. My prediction was wrong to equate "does not write the belief" with "the
  belief is unchanged".

**By the decision rule:** P13a and P13b held, so the company's own evidence says its fix-end offers
save about one in five of the losses it predicts, and that this pays on almost none of them. The
guard is a candidate beside the §12 switch, proposed with seeds, and nothing is flipped here. P13c
did not fail upward (354, not more than 358), so §13's rule does not require the save definition to
be rewritten first. There is one addition the rule did not foresee. The one-seed money ran against
the guard, through the parity channel and not through saves, and that money is a transfer from
households who were staying anyway. Erring against the thesis (F11), the seeds must report it
separately: offers that changed a stayer's tariff and offers that changed a departure, each with
the money attached. Otherwise a positive mean for the switch-without-guard arm will read as
retention value. The grade used `/tmp/pcs13/grade.py` unchanged, with P13e's AUC from
`/tmp/pcs11/grade.py` and `ARM=` pointed at the new output, as §12 did.

## 14. The money question across dice seeds, split by channel (filed 2026-10-22, before any seeded arm was launched)

*Drawn as `seeds-for-the-ending-term-switch-and-the-save-odds-guard`. §12 and §13 both left the money
as a one-seed tie, and both decision rules want seeds (EP17) before either switch is proposed for
CURRENT_POLICY. §13 found the −£810 came from stayers moved across the parity edge, not from
departures. So a seeded mean is graded by channel, not as a single number.*

**What is re-drawn.** `tools/per_customer_switch_arms.py ARM OUT --dice-seed N` re-draws every
renewal roll (`churn_roll_for_renewal`, the departure an offer acts on) and every payment draw
(`dice_seeded`, as the held-money seeds do). The roll is imported by name in `run_phase2b` and
`retention_offer` as well as living in `customer_events`. The patch replaces every loaded binding
of the real function, and the run is refused if the renewal or payment dice reached no draw, or if
offers were answered and none read the seeded roll. **Held:** the book, the elasticities, and the
SVT-inertia roll. So the seeds bound the noise in who leaves at a fix end and who pays. They do not
bound the noise in who leaves the default tariff.

**A finding beside this, not fixed here.** `tools/run_value_cycle_ab.noise_floor` with
`redraw_key="churn_roll"` patches only `customer_events.churn_roll_for_renewal`. The same run's
retention answer, save scale and move-with-us answers read the base roll through `run_phase2b`'s
and `retention_offer`'s by-name bindings. Any floor published on that key re-drew the renewal and
not the offer answering it.

**The grade** is `tools/grade_per_customer_switch_seeds.py`. For each arm pair it puts each household
into one channel. The channels are taken in order, on renewal rows paired by household, roll date
and fuel in `customer_events`:
- `departure`: its set of departures differs between the two arms;
- `parity`: it stayed in both, and at some roll one arm fixed where the other declined the fix;
- `other`: any other difference in its rows;
- `same_choice`: identical rows, but gross can still move by a discount the household would have
  taken anyway.

Gross is `per_cid_pnl` summed per household. Net minus gross (offer cost, provision, capital) is
printed as `unattributed`. Both controls were run before this section was filed:
- **Placebo:** each arm against itself reads +£0.00 in every channel.
- **The default-dice outputs reproduce §13:** save_odds − ending_term is −£810.19 net, `departure`
  0 households, and `parity` 5 households at −£2,385.31. That is the five §13 named:
  −2,313 − 176 − 101 + 186 + 18.

**Setup facts this split shows on the default dice. These outputs were already read, so they are
facts, not predictions.**

| pair | net | departure | parity | other | same_choice |
|---|---|---|---|---|---|
| ending_term − flat | +£111.25 | 1h −£2,035 | 7h +£2,308 | 3h −£154 | −£109 |
| save_odds − flat | −£698.94 | 1h −£2,035 | 3h −£60 | 3h −£158 | −£56 |
| save_odds − ending_term | −£810.19 | 0 | 5h −£2,385 | 0 | +£66 |

§12's tie against flat is not "nothing happened". One more household left in the offer arm, and
seven stayers were moved onto fixes priced against them, and these roughly cancel. §13's sentence
"every other account together moves −£3" does not match the +£66 `same_choice` here. I have not
found which basis §13 used, and the 5-household figure agrees, so I leave §13 standing beside this
note.

**The draws.** Dice seeds 1, 2, 3 and 4, with all three arms of each run at ONE commit, the
commit that lands this section. The outputs are
`/var/tmp/se-pcs-arms-out/s{N}/{flat,all_on_ending_term,all_on_save_odds}.json`, from a locked
worktree at that commit. The default-dice outputs are shown beside the seeds and are **not pooled**,
because their three arms ran at three different commits, both before `7939895894` changed the
own-book provision.

**Predictions (no seeded outcome read).**
- **P14a, the dice reach the world.** On each seed, departures in flat differ from the default
  dice's 353 by at least 3, and the departing set differs by at least 20 accounts: 90%. A seed that
  matches the default set has not re-drawn the roll.
- **P14b, the parity channel is the channel the switch's money moves through.** ending_term − flat
  `parity` gross is positive on at least 3 of the 4 seeds: 75%. The mean is +£1,500, with each seed
  in [−£500, +£4,500]. save_odds − ending_term `parity` is negative on at least 3 of 4: 75%, mean
  −£1,500.
- **P14c, offers rarely change a departure.** save_odds − ending_term `departure` holds at most 3
  households on every seed: 80%. Across the 4 seeds, the mean `departure` gross for each arm against
  flat has a 95% interval that contains 0: 70%.
- **P14d, money.** Each pair's mean net across the 4 seeds has a 95% interval that contains 0: 70%
  for ending_term − flat, and 65% for save_odds − flat.

**Decision rule, fixed now.** By M2, only the `departure` channel can show value created. `parity`
moves money from households who were staying. `same_choice` moves the discount to them.
- A switch is proposed for CURRENT_POLICY only if its `departure` gross against flat has a 4-seed
  95% interval above zero AND its mean net against flat is at least 0.
- If its net is positive only through `parity`, it is written up as a transfer and not proposed.
  It also becomes a finding for the dominance rule's knowledge page: an offer that moves a stayer
  onto a fix that later costs more than the default is the shape SLC 0 treatment-of-customers
  reads, not a retention lever.
- If P14a fails on a seed, that seed is void and is re-run after the patch is re-resolved. It is
  not graded.
- With neither switch proposed, the record says that across these draws, on this book, the
  per-customer retention offers create no value that can be detected. That goes in the stretch log,
  and nothing is flipped.

**Launch plan.** The three arms of seed 1 run serially in one unit, about 1h and 7 GB each. Seeds 2
to 4 are handed on as their own launches, so that one seed's 3h never holds a continuation past
its window.

**Seed 1 launched 2026-10-22 03:11Z**, after the predictions above were on origin at `bc1e6ad78`.
Unit `longjob-pcs-arms-s14-seed1`, from the locked worktree `/var/tmp/se-pcs-arms14` (detached at
`bc1e6ad78`). It runs `/var/tmp/se-pcs-arms-out/run_seed.sh 1`: flat, then all_on_ending_term,
then all_on_save_odds, each writing `s1/<arm>.{json,log,rc}`. The unit log is
`/var/tmp/se-pcs-arms-out/s1_unit.log`. Expect about three hours. Seeds 2 to 4 use the same script and
worktree, one unit per seed. Grade a seed with
`python3 -m tools.grade_per_customer_switch_seeds s1:$O/s1/flat.json:$O/s1/all_on_ending_term.json:$O/s1/all_on_save_odds.json`,
and add one `sN:...` triple per seed as each finishes. The 95% interval prints from two seeds.
Each output's `_dice_seed` block records how many renewal-roll and payment draws the seed reached,
per binding.

### 14. Seed 1 (graded 2026-10-22 ~07:45 BST; unit rc=0, all three `s1/*.rc` 0, every arm stamped `bc1e6ad780`)

Graded with `python3 -m tools.grade_per_customer_switch_seeds s1:...` from a worktree at origin/main
`8486305f24`.

**What the dice blocks say.** `customer_events` binding: 236 / 346 / 325 seeded renewal rolls
(flat / ending_term / save_odds). `retention_offer` binding: 0 / 108 / 86, so it is above 0 in both
offer arms. Payment draws: 54,487 / 54,410 / 54,410. The `run_phase2b` binding read **0 in every
arm**. The item asked for "every binding reached", and this one was not. Nothing in these arms
calls the roll through `run_phase2b`'s name. The run's own refusal does not need it, and nothing
here is wrong because of it. But a seed cannot show that this binding is patched.

**P14a, the dice reach the world: FAILED as written.** Flat departed **353** accounts, the same as
the default dice's 353, so the count leg (a difference of at least 3) fails. The set leg passes:
20 accounts left only under the default dice and 20 only under seed 1. At the event level, 62 of
the default's 95 `churned`/`renewal` events and 59 of seed 1's 92 are not in the other run. The
patch did reach the world. The count leg was the wrong instrument, and my prediction was wrong
because only about 95 of the 353 departures are fix-end rolls the seed re-draws. The rest come from
channels §14 holds, so the total barely moves. The set comparison is also confounded. The default
flat ran at `0f2b04c84`, and `5c0eeeb489` (shared shortfall on by default) landed between that
commit and `bc1e6ad78`.

**By the rule fixed before the run, seed 1 is void.** I keep the rule. The rule's remedy, "re-run
after the patch is re-resolved", has nothing to act on, because the patch fired. A re-run of seed 1
at `bc1e6ad78` is deterministic and would reproduce this output. So seed 1 stays out of the pool,
and **seed 5 is added** to keep four graded seeds (2, 3, 4, 5). The P14b and P14c legs below were
read, and are recorded as read. They are **not counted**.

| pair (seed 1, void) | net | gross | unattributed | departure | parity | other | same_choice |
|---|---|---|---|---|---|---|---|
| ending_term − flat | −£1,673 | −£4,433 | +£2,760 | 1h −£4,741 | 4h −£30 | 4h +£441 | 385h −£104 |
| save_odds − flat | −£1,617 | −£4,371 | +£2,754 | 1h −£4,741 | 3h −£56 | 4h +£441 | 386h −£15 |
| save_odds − ending_term | +£56 | +£62 | −£6 | 0 | 1h −£26 | 0 | 111h +£89 |

- P14b per-seed legs (not counted): ending_term − flat `parity` was −£30, the wrong sign but inside
  [−£500, +£4,500]. save_odds − ending_term `parity` was −£26, negative as predicted.
- P14c per-seed leg (not counted): save_odds − ending_term `departure` held 0 households, within the
  bound of 3.
- **One thing this seed shows about the decision rule, whatever its status.** The rule grades
  `departure` by **gross**. Here the one extra departure carries −£4,741 gross, and the pair's
  net-minus-gross is +£2,760. The likeliest source is that household's own provision and cost
  lines, which leave with it. That is **not established per household**: the grader does not split
  `unattributed`. If it is the source, gross overstates what a departure costs by about 2.4 times.
  The rule stands as filed. Splitting net by household for the departure channel is a grader
  change, handed on. It is not a reading of this seed.

**P14a′, filed now, before any seed 2 output exists, and binding seeds 2 to 5.** It replaces the
count leg with a comparison at one commit. The `churned` events (account, date) in seed N's flat
differ from seed 1's flat (the same commit, `bc1e6ad78`, with only the seed changed) by at least
20 events in the symmetric difference: 95%. That property is the one the roll controls. A seed that
fails it is void and is re-run as the original rule says. The original count leg is still reported
on every seed, and nothing rests on it.

**Seed 2 launched 2026-10-22 ~07:40 BST** as `longjob-pcs-arms-s14-seed2` (queued behind a landing
in progress, `longjob-pcs-arms-s14-seed2-queued`). It runs `run_seed.sh 2` from the locked
worktree `/var/tmp/se-pcs-arms14` (`bc1e6ad78`). Its unit log is `/var/tmp/se-pcs-arms-out/s2_unit.log`
and its artefact is `s2/all_on_save_odds.json`. Seeds 3, 4 and 5 are each handed on as their own
launch.

## 15. The save rate learned against a holdout: `all_on_save_odds_holdout` beside `all_on_save_odds` (filed 2026-10-22, before either arm was launched)

*Drawn as `the-save-rate-is-learned-against-a-holdout`. Knowledge first:
`docs/market_research/a_save_offer_against_the_switching_rules_and_the_seam.md` §9e. Published
practice measures a retention offer against a randomised untreated group (Ascarza 2018, JMR 55(1);
Ascarza, Iyengar & Schleicher 2016, JMR 53(1); Ofgem's EFTC and CMOC trials). What share a GB
retention desk holds out is a GAP. §13's save rate read 0.19 while the world kept 0 of 32.*

**What changed (one field).** `retention_save_rate_learned_against_holdout`. Of the renewals the
save-odds guard would offer on, the company's own coin (a hash of account and roll date) holds
`SAVE_HOLDOUT_SHARE` = 0.272 out with no offer. That share is derived in §9e from the 83 offers of
2017, their loss rate 34/83, and the break-even save rate of 0.83. From then on, `retention_save_rate`
reads `(h − o)/h`, the holdout's loss rate h against the offered loss rate o. Both are
Jeffreys-corrected, the rate is never below 0, and the belief does not enter it. It returns `None`
with a reason until both groups have closed renewals of the type. The arm is
`tools/per_customer_switch_arms.py all_on_save_odds_holdout`: `all_on_save_odds` plus this field.

**Two arms at ONE commit, because more than one thing has changed since §13.** §13 ran at
`7bab213af`. HEAD has since made the part payment the default (`6b81d3b25`) and changed the
provision. So the control is `all_on_save_odds` re-run at the commit that lands this section, and
§13's output is not the comparator. Default dice, the book and seed of §12/§13. Outputs:
`/var/tmp/se-pcs-arms-out/s15/{all_on_save_odds,all_on_save_odds_holdout}.json`, serially, from a
locked worktree at that commit.

**Every output now carries `retention_offer_money_by_channel`.** It counts offers, households and
booked offer cost under three channels: `changed_a_departure` (left at the full rate, stays at the
offer), `changed_a_stayers_tariff` (stays either way, and only the discount takes its fix to or
below the default: §13's parity channel), and `changed_neither`. This is read world-side from the
world's own answer at both rates, in the harness only. `retention_save_holdout_log` lists the
held-out renewals.

**Setup facts (already read, not predictions).** On §12's output, 2017 carried 83 offers, 34 lost.
At s = 0.272 the expected holdout in 2017 is about 22.6 of 83 (binomial sd 4.1). The SE of `h − o`
at those sizes is about 0.12. With no true effect, `(h − o)/h` then has an SE of about 0.3 around
0, and it is floored at 0.

**Predictions (no outcome of either arm read).**
- **P15a, the coin reaches the run and the split is exact.** In the holdout arm, 2017's offered set
  plus its held-out set equals the control arm's 2017 offer set on (account, date): 85%. The
  held-out share of that set is in [0.17, 0.38], point 0.27: 90%. No held-out renewal appears in
  `retention_log`: 99%.
- **P15b, what the holdout teaches.** The fix-end save rate first read in 2018 lies in [0, 0.45],
  point 0. It reads exactly 0 (offers lost at least as often as the holdout): 55%. It sits below
  §13's 0.19: 65%. Default-term types read `None` in 2018: 90%.
- **P15c, the guard offers no more from 2018.** Fix-end offers from 2018 number 0–3 in the holdout
  arm, point 0: 85%, against the control's 1 (§13), if the control repeats §13. Total held-out
  renewals are 22–32: 80%.
- **P15d, offers rarely change a departure.** In BOTH arms, `changed_a_departure` holds 0–2
  offers: 85%, point 0 (§7 and §13 found 0 saved at the roll). `changed_a_stayers_tariff` holds
  3–15 offers in the control, point 7: 60%. Most of the offer cost sits in `changed_neither`: 75%.
- **P15e, departures and money.** Departures differ between the two arms by at most 4: 80%.
  Holdout − control net is within ±£1,000, so it is a tie under EP17: 70%, point −£300. Withholding
  an offer moves a would-be fixer onto the default, which §13 priced as about −£470 a household. The
  discount not given is about £420 (27% of the roughly £1,550 the 2017 offers cost in §13).

**Decision rule, fixed now.**
- **If P15a fails, the coin did not reach the run.** That is the next item, and nothing is read
  from P15b–e.
- **If P15a holds and P15d's `changed_a_departure` is 0–2 in both arms,** the company's own
  experiment and the world agree that the offers saved nobody. The record then says per-customer
  retention offers on this book are transfer, not creation. The holdout switch becomes the
  candidate to pair with the §13 guard, because it is the only form in which the company could
  learn this as a real supplier would. Proposing it for CURRENT_POLICY waits on §14's seeds.
- **If the holdout's save rate reads above 0.45 on a year where the world saved nobody,** the
  read is noise at this sample size. That is written up as the holdout being too small for one year
  at this book (§9e already says N ≤ about 65 cannot resolve it), and the share is not tuned to
  rescue it.

### 15g. Grade (2026-10-22 ~09:55 BST, both outputs present)

**What ran (the launch line, not landed before launch).** `/var/tmp/se-pcs-arms-out/run_s15.sh`, unit
`longjob-pcs-arms-s15-holdout`, from the locked worktree `/var/tmp/se-pcs-arms15` detached at
`fdec35bd9`. It ran each arm serially as `python3 -m tools.per_customer_switch_arms <arm>
/var/tmp/se-pcs-arms-out/s15/<arm>.json`. `all_on_save_odds` ran 04:35:54–05:36:31Z and
`all_on_save_odds_holdout` ran 05:36:31–06:36:35Z. Both returned rc 0.

**One commit, in substance.** The control stamps `fdec35bd9`. The holdout arm stamps `714164f49`,
because two `SALVAGE(auto)` commits landed on the worktree between the arms (05:09Z and 05:35Z).
`git diff --stat fdec35bd9 714164f49` touches only `docs/context-handshake-latest.md`, `token-log.md`
and four `docs/observability/*.json` ledgers. Nothing changed in `company/`, `saas/`, `simulation/`,
`sim/` or the arm tool, so the two arms ran the same code. The worktree had been removed by the time
of grading. So `grade_s15.py` ran from the shared tree at `15f3e0e22`, and its only use there is
`kind_at`, which feeds P15c's fix-end count.

**Placebo** (`HOLD=` the control): 0 held out, held share 0.000, every money and departure delta
0.00. The control's 2018 fix-end save rate reads 0.1896, so the control repeats §13's 0.19.

| figure | control `all_on_save_odds` | holdout arm |
|---|---|---|
| 2017 offers / held out | 83 / – | 62 / 21 (all fixed-ending), union = control's 83 exactly |
| 2018 offers (fix-end / default) | 5 (1 / 4) | 4 (0 / 4) |
| held-out renewals, total | – | 22 (21 fixed 2017, 1 default 2018) |
| `changed_a_departure` | 0 offers, £0 | 0 offers, £0 |
| `changed_a_stayers_tariff` | 7 offers, £160.49 | 7 offers, £143.65 |
| `changed_neither` | 81 offers, £1,482.46 | 59 offers, £762.79 |
| offer cost | £1,642.94 | £906.44 |
| departures | 355 | 354 (only control: SYN-2016-387) |
| `provisioned_net_gbp` | £600,135.82 | £600,713.81 (H−C **+£577.98**) |

**What the holdout taught.** The run logs no rate on the holdout side, which is an instrument gap.
On that side the rate reaches only the guard's refusal, and no output row carries it. So I rebuilt it
in the harness from the run's own records. Each 2017 offer and held-out renewal was joined to the
world's `customer_events` at its roll date. For the offers this reproduces the run's own `outcome`
field exactly (36 renewed, 26 churned). The holdout lost 8 of 21 (Jeffreys h = 0.386). The offered
group lost 26 of 62 (o = 0.421). `(h − o)/h` = −0.09, floored to **0.000**. The offered group lost
slightly more often than the group that got nothing.

- **P15a HELD.** Offered ∪ held-out equals the control's 2017 set on (account, date): 0 only-C,
  0 only-H. The held share is 0.253, inside [0.17, 0.38]. No held-out key appears in
  `retention_log`. The coin reached the run.
- **P15b HELD.** The 2018 fix-end rate is 0.000. That is in [0, 0.45], exactly 0, and below §13's
  0.19. Default-term types read `None` in 2018 by the code path: no default-ending renewal was held
  out and closed in 2017 (n_h = 0), so the guard kept its standing behaviour and made 4 default
  offers, as the control did. This leg comes from the rebuild above and not from a logged value.
- **P15c HELD.** There were 0 fix-end offers from 2018 in the holdout arm, against the control's 1.
  Total held-out renewals were 22, at the bottom edge of 22–32.
- **P15d HELD.** `changed_a_departure` is 0 in both arms. `changed_a_stayers_tariff` is 7 in the
  control, on the point. `changed_neither` carries 90% of offer cost in the control and 84% in the
  holdout arm.
- **P15e HELD on its bands, REFUTED on its point.** Departures differ by 1. H−C is +£578, inside
  ±£1,000, so it is a tie under EP17. I predicted −£300, and the sign is wrong. The discount not
  given was £736, not about £420. That covers 22 offers withheld in 2017 and a fix-end offer in 2018,
  and on this one seed it outweighed the fixer-to-default loss §13 priced at about −£470 a
  household. With one seed and one book this is a point reading with no interval. §14's seeds are
  what can size it.

**Decision rule.** P15a holds, and `changed_a_departure` is 0 in both arms. So the company's own
experiment and the world agree that **the offers saved nobody**. The record says per-customer
retention offers on this book are **transfer, not creation (M2)**. Every pound of offer cost lands
on a stayer, and most of it changes nothing at all. The holdout switch
(`retention_save_rate_learned_against_holdout`) is now the candidate to pair with the §13 guard,
because it is the only form in which the company could learn this the way a real supplier would.
Proposing it for CURRENT_POLICY waits on §14's seeds, as fixed. The >0.45 noise branch did not
arise. Still owed: write the holdout-side rate and its reason onto each refusal row
(`no_offer_churn_log` or `retention_save_holdout_log`). That would make P15b a reading rather than
a rebuild.
