**Severity:** RECORDED · **Lane:** C_customer_ops · **Epoch:** 3 · **Atom:** `unminted` — direction item `a-dual-household-is-one-decision-to-the-company`

# The company decides a dual household per leg on every customer route but one, and C35 charged it two rises for one benefit

Since `c136809f5` (landed and promoted 18 Oct), three founders in four are dual fuel. The live book
`live_population()` draws at origin holds **788 supply points in 447 households, and 341 of those
(76%) are dual.** Every one of the 341 has both legs acquired on the same date, so both legs reach
each renewal together.

## 1. Knowledge (K8)

`docs/market_research/how_a_gb_domestic_book_splits_by_fuel_and_how_a_two_fuel_home_switches.md`
§8 is new in this commit. Licence text was read this session (electricity SLCs, consolidated to
1 Aug 2025):
- SLC 1's **Same Domestic Customer** and **Dual Fuel Discount**: the regulator treats the pair as one
  person.
- 31H: one optical label on a Dual Fuel Account.
- 31I.5(b): a **Combined** notice at a price change or the end of a fixed term, allowed but not
  required.
- 14.4(a) with SLC 1's "Charges": objections are per fuel.
- 27.8: ability to pay is per customer.
- 27.17: a final bill per fuel's contract.

The page's reading: rates, objections and final bills are per fuel. **The decision to stay or leave,
and the value at stake in it, is the household's.** Labelled GAP: the share of dual accounts on one
DD, one bill or one end date; netting one fuel's credit against the other's debt; and saves that
keep both legs.

## 2. Census: each route, read in company code at `c136809f5`

"Per household" means the decision reads both legs (margin, volume or balance summed under
`billing_account`). "Per leg" means it reads one supply point's.

| Route | Where | Decides | Does splitting the household change the decision? |
|---|---|---|---|
| **C34 SVT contact** (the flat rule's letter, and its holdout coin) | `simulation/run_phase2b.py:3001-3010` → `company/interfaces/contact_programme.contact_arm(billing_account, …)` | **Per household.** The coin and the send are keyed on `billing_account`. | No. One coin per household. (The send is called once per leg's default-tariff segment. The world's `instrument_reaching` is keyed on the account, so a dual household is reached once.) |
| **C34/C35 `decide`** (advice, share, retention rise) | `company/crm/next_best_action.py`. **No caller in the run.** Its one consumer is `tools/retention_rise_count.py`, the instrument behind C35's published 211/780. | **Per leg.** One `AccountState` per renewal row: that leg's margin, the household's B11 hazard (`hazards[…][billing_account]`) and the household's advice benefit. | **Yes, and this is the first such route. Fixed below (§3).** |
| **Save on the loss notice** | `run_phase2b.py:3765-3796`; `company/interfaces/save_offer.py:42-67`; `company/crm/save_offer.py:128-188` | **Per leg.** The world sends a loss notice for every point of the household (`supply_points_on_supply(billing_account, …)`). The company answers only `cid`'s, priced on that fuel's renewal rate against its own default and cost floor. | Not the company's own choice: the save is a rate match with no value comparison, so each leg's offer is the same either way. **But the household is asked to stay on one fuel's cut while both legs leave.** This is the next candidate. It needs world knowledge of how a household weighs a one-fuel save (§8 GAP). |
| **Renewal pricing** (value arm) | `company/pricing/value_based_renewal.py:1712-1738` (records filtered back to one `commodity`); `decide_margin`, 837ff; note at 646-648 | **Per leg**, deliberately: `decide_margin` "prices ONE fuel: a dual-fuel household reaches it twice". Each leg's churn estimate is that leg's own `enriched_churn_estimate` on its own rate. | **Yes, in principle**: P(leave) is drawn per leg, and the value at stake is one leg's. This is the second candidate. It is bigger than one turn because it touches the value arm's controls (~25 value-arms controls, per memory `project_a_level_anchor_refit…`). |
| **DD review** | `company/billing/dd_review_runner.py:121-168` (`by_cust[b["customer_id"]]`); `company/billing/dd_review.py:104-131` | **Per leg.** Each leg has its own DD, review and balance to clear. | Yes, for a household in credit on one fuel and debit on the other. The rules allow either (§8: no condition requires one DD). Practice is one DD (GAP for a share). Third candidate. |
| **Move-out final bill / move-with-us** | `run_phase2b.py:2690-2704` (the move is drawn once per household); 4213-4237 (the offer on `_decision_leg` only) | **The date is the household's. The move-with-us offer is priced on the decision leg alone** (`unit_rate`, `company_fwd` of that leg). | The move-with-us value is understated by the other leg's margin. Off on every standing policy (`move_with_us_offers`). |
| **Collections / arrears** | `background/live_payment_triad.py:830-848` (`ACC-{customer_id}` per leg); `run_phase2b.py:2781-2804` | **Per leg.** One ledger per supply point, never netted. | Yes, where one leg is in credit. SLC 27.8 makes ability to pay the customer's. Netting practice is GAP. |
| `forward_clv` (B11, the input above) | `company/analytics/forward_clv.py:230-259` | **Per household.** Fuels are merged into `_billing_account_id`. | No. It is already the household. |

**Method.** One read-only census agent read the routes. I spot-checked the save, renewal, DD,
move-with-us and ledger lines myself at the cited file:line, and they match. The "no caller in the
run" claim for `decide` is a grep of `company/`, `simulation/`, `tools/` and `background/` for
`next_best_action` imports: only `contact_programme` (for `in_contact_holdout`) and the tool.

## 3. The fix: C35 decides a dual household once

**The defect, printed at real inputs** (the published probe's median legs: electricity GBP 1.17 a
month on 3.03 MWh, gas GBP 1.85 on 11.5 MWh, hazard 0.01, the C35 page's GBP 2 / 0.1 pt advice
effect, horizon 48):

| Decided | Rises charged | Each decision says the household keeps | What the household actually keeps |
|---|---|---|---|
| per leg (today) | 2.06 + 2.09 GBP/month | 20.6 and 19.6 GBP | **one benefit of GBP 96, GBP 151.8 paid (96 − 20.6 + 96 − 19.6): worse off by GBP 55.8** |
| per household | 2.15 GBP/month | 17.6 GBP | 17.6 GBP |

Across the 9 cells of hazard (0.005 / 0.01 / 0.02) by the 3 advice effects, the per-leg pair always
pays about two rises against one benefit. The household floor C35 states ("the household must keep
at least nothing") fails across the pair every time, while each leg reports it held.

**Built** (`company/crm/next_best_action.py`):
- `household_state` merges the legs of one billing account: margin summed, one hazard, the
  household's estimates, and missed payments as the maximum across legs.
- `HouseholdRenewalTerms` carries the headroom of both legs, each under its own fuel's default. It is
  unknown if either leg's is.
- Legs that are not one decision are refused, with the reason: two hazards, two sets of estimates,
  or one leg renewing alone.
- `states_for_decision` sits behind **`DecisionPolicy.next_best_action_decides_per_household`,
  default False**, declared `run_argument` in `FIELD_CONSUMPTION`.
- `tools/retention_rise_count.py` groups rows by `(billing_account, term_start)` and takes
  `--per-household`.

**Controls**: `tests/company/crm/test_a_dual_household_is_one_next_best_action_decision.py`.
- The partition comes first: off gives 3 decisions on {dual, single}, on gives 2, and both
  branches are reachable.
- The defect is kept visible with the switch off.
- With the switch on: one affordable rise, and the summed headroom.
- The unknown-headroom refusal, and the three refusals with their reasons.

**Named mutation:** `sum(leg.monthly_margin_gbp …)` → `first.monthly_margin_gbp`. This turned
`test_on_the_household_is_charged_one_rise_it_can_afford` **red** (1 failed, 7 passed), and was
restored.

**Byte-identical, measured.** On the published probe (`/var/tmp/retention_rise/probe_default.json`
with `docs/reports/run_output_latest.json`), origin's tool and this tool with the switch off give
**`cmp`-identical output (211/780 at both hazard ends)**. With `--per-household` the same probe
also reads 211/780, with 260 decisions. That is a placebo: the probe was drawn on the 1%-dual book,
where no two legs of one account renew on one date.

**What it moves on the corrected book.** Measured with `live_population()` at `c136809f5` (6.6 s):
one renewal round goes from **788 leg decisions to 447 household decisions**, and 341 households
stop being charged twice. The rescue count itself on that book needs a probe on a run drawn from it,
and this item makes no full run. **I cannot yet say** what C35's count becomes. My prediction,
filed before it exists: rescued *decisions* fall by about the dual share of rescued rows (fewer, one
per household), and the household's median kept share rises from 0.40, because one rise replaces
two.

## 4. What is next, in order

1. **The save on the loss notice** answers one leg of a household that is leaving with both. This
   needs knowledge first (§8 GAP: how a household weighs a one-fuel save) before any build.
2. **Renewal pricing**: one P(leave) per household across both legs' offers. This is bigger than a
   turn because it re-takes the value-arms controls.
3. **DD review and collections**: netting across legs. Practitioner question first (K4): do GB
   suppliers net one fuel's credit against the other's debt on one account?

Switching `next_best_action_decides_per_household` on is its own one-variable item after the 19 Oct
publish, together with C35's own switch.

## 5. Item 1, the save on the loss notice: knowledge and company side landed (2026-10-18)

**Knowledge (K8).** Fuel page §8a. One save may cover both fuels: nothing read forbids it, and SLC 1's
Dual Fuel Discount allows pricing the pair. The decisive published fact is that the gap the save
matches is Ofgem's **dual-fuel** bill gap. A household's reason to leave is measured on both fuels,
and a one-fuel match answers it on one fuel's share of the bill. How a household weighs a one-fuel
save is still **GAP**.

**The split does change the decision, so this is not the "already decides correctly" case.** The
run rolls a dual household's departure once, on electricity, and sends both points' loss notices.
The company answers electricity's alone, on electricity's floor. The gas Invitation is filed and
never read. Pair count on the live book at `27b6798ec` (`live_population()`, 6.3 s): **341 of 447
households (76%) are dual, all 341 on one acquisition date**. So every dual departure is a pair of
notices on one date.

**Built** (`company/crm/save_offer.py`):
- `SaveLeg` and `household_save_rates` match every leg to its fuel's default × (1 − gap), never above
  its renewal. The match stands while the household's summed margin over cost is ≥ 0. Otherwise
  each leg is floored on its own.
- `save_rates_for_decision` sits behind **`DecisionPolicy.save_offer_decides_per_household`, default
  False**, declared `run_argument`.

**Controls:** `tests/company/crm/test_a_dual_household_is_one_save_decision.py`.
- One partition control: off answers {X}, on answers {X, Xg}, and on reaches the matched, floored and
  none branches.
- Off equals `price_match_save_rate` across floors either side of the match.
- Named mutation: household headroom → per-leg floor. It turned 2 tests red and was restored.

**Off path.** No run code changed in this commit, so the run's off path is byte-identical by
construction. The switch has **no run consumer yet**, the same shape C35's switch had at its first
landing.

**Next, in order** (item 1's remainder):
- **1b. The run** reads the switch. At the save site it builds a `SaveLeg` per point from
  `supply_points_on_supply`, answers every held notice, and carries the gas leg's save rate to that
  leg's term.
- **1c. The world weighs the pair.** This is a world fidelity choice under the §8a GAP. The stated
  belief proposed: the household weighs a save by its effect on its **combined bill**, because the
  deal it is leaving for is quoted on the combined bill (§8a, §4). The re-asked roll would see the
  decision leg's rate scaled by Σ v·save / Σ v·renewal. That is a sim change, decided blind to company
  results. It needs its own prediction filed before the run.

## 6. Item 3, netting across legs: knowledge landed (2026-10-18)

The fuel page's new §8b answers the K4 question from the published record. **Since 22 Jan 2021, SLC
27.8D requires every domestic contract to give the customer a right to offset its credit against
debt on any other supply contract, gas included.** It came from Ofgem's Supplier Licensing Review,
17 Nov 2020, §5.7. The licence gives the supplier no such right and does not forbid one. EDF's
terms (cl. 17.e) let either side net. SLC 27.16's Credit is defined per contract. Two points are
**GAP**: whether a DD review nets the legs, and whether the other fuel's debt is a "fair and
reasonable" ground to withhold a refund. The exact practitioner question for the advisor channel
is in §8b. §8's Collections row is corrected beside the claim.

So today's per-leg collections chase debt that a dual household may, from 2021, lawfully set
against its credit. Nothing is built yet. The prediction of how many households this touches on the
publish run was filed before that run was read:
`docs/staging/records/SEAT_PREREG_HOW_MANY_DUAL_HOUSEHOLDS_HOLD_A_CREDIT_ON_ONE_FUEL_AND_A_DEBT_ON_THE_OTHER_ON_THE_PUBLISH_RUN_2026-10-18.md`.
The netting build is a later item: §8b's choices (a) to (c). It is sized by that reading.
