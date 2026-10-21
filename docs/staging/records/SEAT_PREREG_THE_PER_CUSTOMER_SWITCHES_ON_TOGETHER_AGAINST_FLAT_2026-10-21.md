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
