# Pre-registration: the per-customer switches on together, against CURRENT and against flat

**Written 2026-10-21 ~04:30Z, before any arm runs.** Claim `the-per-customer-switches-on-together-against-flat`
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
