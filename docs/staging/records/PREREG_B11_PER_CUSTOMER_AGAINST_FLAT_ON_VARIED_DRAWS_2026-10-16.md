**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history` · **Subjects:** `EP17_varied_population_draw` · **Claim:** `b11-the-flat-baseline-is-pre-registered-for-the-ep17-switch` (Lane 0 delivery)

# Pre-registration: the per-customer supplier against a flat supplier, on fresh varied draws

Written 2026-10-16, at origin `a1d34f30f`, before any varied-draw run of either arm exists. No
book has been run under the flat arm defined below on any seed. This is the comparison EP17's
switch fires into: its four conditions are closed on origin (B12 `badd57e8e`, the held-estimate
catch-up `650fdcdd7` graded in `bdd6d1657`, the E6 first slice `738b3f0ab`, and the stayers
control).

**Why it is written now.** The thesis needs a baseline to beat. Without one, "it performed well"
has nothing to be measured against. The switch condition was met overnight, so the runs could
start before their predictions are on file. A prediction filed after the answer is not a
prediction.

## The two arms

Both arms run the same book, in the same world, at the same commit, with the same seed. Every
figure is what the world did (realised), never what the company believed. This is
`tools/run_value_cycle_ab.py`'s rule, quoted from `company/pricing/value_based_renewal.py`: an arm
scored on its own expected value wins by construction.

### Per-customer arm: `VALUE_ARM_POLICY` (`company/policy/decision_policy.py`)

`CURRENT_POLICY` with `renewal_margin_arm="value_based"`, and nothing else changed. This is the
standing, recorded arm, and no new combination is invented for this run. Its per-customer views
are:

- Renewal margin chosen per customer from the company's own beliefs
  (`company/pricing/value_based_renewal.py`), with bad debt priced on the `own_book` belief.
- Retention offers sent only where the company's per-customer churn belief exceeds
  `RETENTION_THRESHOLD` = 0.30 (`simulation/run_phase2b.py:3396`). The cut is sized by the
  churn-belief tiers (8/5/3%), held to the cost floor, and passed through the value guard.
- Offer framing and letter tone set by `ab_test`, discovered per segment
  (`company/analytics/nudge_discovery.py`).

### Flat arm: `FLAT_SUPPLIER_POLICY`, which no flag produces today

This is the same company with every per-customer view removed. Everyone gets the same rule:

| field | flat value | why |
|---|---|---|
| `renewal_margin_arm` | `"flat_rules"` (the standing GBP 2.00/MWh) | one renewal rule for every account |
| `retention_discount_mode` / `flat_discount_pct` / `retention_tiers` | `"flat"` / `0.0` / `()` | `retention_cut_share_at_risk_tiers` returns None at a share <= 0 (`company/interfaces/growth_desk.py:452`), so no retention offer is made to anyone |
| `framing_mode` / `tone_mode` | `"gain_framed"` / `"firm_toned"` | one letter for everybody, with no per-segment discovery |
| every other field | as `CURRENT_POLICY` | hedging (book-level), the save on a loss notice (`price_match`, sized from the market rather than from a belief about the customer), and every regulatory obligation stay identical, so they are not variables here |

**Why "no offer" rather than "5% to everybody".** A discount given to every renewer is a price
level, and most of it is a transfer (M2). "No targeted retention" is the plain flat posture. F11
asks whether that makes the flat arm the weaker rival. It might: the flat arm loses the retention
it does not buy. **Pre-registered tie rule:** if the per-customer arm's retention lead over the flat
arm is the only measure that clears its bound, it is reported as "bought with discounts", not as
"knowledge". The flat-at-level arm below is what separates the two.

**Flags alone cannot produce this arm today**, for three reasons. The finding filed alongside this
record (`docs/staging/SEAT_FINDING_B11_THE_FLAT_SUPPLIER_ARM_HAS_NO_DOOR_ON_A_VARIED_BOOK_2026-10-16.md`)
names the smallest change that would.

1. No named policy exists. `NAIVE_POLICY` is not a substitute: it gives a flat 5% to everybody
   above the per-customer churn threshold, and it also drops VaR hedging and the
   anniversary rule. That is three variables, and one of them is still per-customer.
2. `tools/run_value_cycle_ab.py` hard-codes `CURRENT_POLICY` as its control. `tools/seed_family.py`
   takes no policy argument and runs the production policy only.
3. Even `CURRENT_POLICY`, the value runner's "flat" control, keeps the per-customer retention gate
   and `ab_test` framing. The standing value-cycle A/B is "per-customer renewal pricing against
   flat renewal pricing", not "per-customer supplier against flat supplier". Its results must
   not be quoted as the second.

### Third arm, for attribution: flat at level

This arm is `FLAT_SUPPLIER_POLICY`, with `renewal_margin_arm="flat_at_level"` at the per-customer
arm's own realised median uplift, read from the same seed's per-customer member. It separates
"chose well" from "charged more", which is the question `tools/run_value_cycle_ab.py --level-arm`
was built for. If the per-customer arm's margin lead over the flat arm is mostly level, the
thesis's knowledge claim is not supported by this run.

## Population seeds

The seeds are **fresh: 61113, 61114, 61115, 61116, 61117, 61118.** Never 61109 (B12's only seed)
and never 42.

All twelve authorised seeds, 61101 to 61112 (`docs/design/curriculum/varied_population_draw_activation.json`),
have already been read under some arm:

- 61101–61107: founders-only runs (`SEAT_FINDING_A_CREDITED_ACCOUNT_IS_DUNNED_..._61106`).
- 61101–61104: all-wins runs.
- 61110–61112: the save, mover offer and provision findings of 10-12 to 10-14.
- 61109: B12.

61108 may be unread, but one seed is not a family. **The six fresh seeds are not yet listed in
the record, so `tools/book_seed_authorisation.py` will refuse them.** The record is written only on
the director's word. His 2026-10-15 ruling ("a fresh draw per run, as canon F13 says") reads as
authorising fresh draws once the conditions close. Even so, the record's own rule is that a
general "yes" does not authorise every seed later typed. This is raised to `for_the_director`
with a recommendation, and it does not block filing this record.

- **Shape:** `tools/seed_family.py`'s authorised analysis book: 40 founders, `all_wins`. This
  follows the director's 2026-10-10 ruling. The 400-founder book stays the production shape.
  Per the ruling's condition 1, every measure below is reported for founders and campaign wins
  separately.
- **Pairing:** all three arms on each seed, with the renewal dice re-drawn at floor seed = book
  seed (the seed-family preamble). The arms are compared within a seed, and the effect is the
  mean of the six paired differences with a t interval on 5 df.
- **Commit:** one origin commit, pinned for all eighteen members, read from the members' own
  stamps (`run_base_seed`, the world digests). A member whose stamp disagrees is refused, not
  pooled.

## Measures, each reported separately and never netted into one score

All measures are per home (billing account), realised in-window, and read beside `tenure_days`.
Each is reported as per-customer minus flat (P−F) and flat-at-level minus flat (L−F), paired by
seed. Any interval that includes zero is reported as "cannot tell". F11 then applies: **a tie
counts against the thesis.**

| # | measure | instrument | predicted P−F | confidence |
|---|---|---|---|---|
| M1 | Net margin after cost to serve, GBP per home | `net_value_gbp` | **positive**, +0% to +15% of F | 0.60 |
| M1s | Selection share of M1 (P−L) | as M1 | **cannot tell** on six seeds; the point estimate is within ±1 se of 0. The value arm's AUC has never left a coin flip (0.4653, null 0.264–0.736) | 0.70 |
| M2 | Bad debt, GBP per home, plus share of homes ever 91 days behind | `bad_debt_gbp`, `behind_91` | **positive** (more debt under P), 0% to +25% of F, because P bills more | 0.50 |
| M3 | Retention: homes still supplied, and switch departures per home-year with **moves counted apart** | `still_supplied`, departure register | **still supplied: cannot tell**, interval spanning −8 to +8 points (P prices higher but buys retention F does not). **Moves: P−F within ±1 point** (a control; moves are the world's, not ours) | 0.55 / 0.80 |
| M4 | Household saving in GBP against the published default tariff | `company/analytics/household_value_share.build_household_value_share` | **negative**: households save less under P. Its size is at least half of M1's gain, meaning **most of M1 is a transfer, not created value** (M2) | 0.60 |
| M5 | Household time, in minutes | **none exists.** C31 is a GAP: published only as perception, plus the phone queue (`docs/institutional/knowledge_map.md` row C31) | **reported as None, LIMITATION_NO_MINUTES_INSTRUMENT.** Counts of effort events per home (switches, save contacts, retention letters) are given as counts, never converted. P−F effort events: **positive** (P sends retention letters, F sends none) | 0.85 |
| M6 | CO2: household kWh × the DESNZ factor per fuel (`company/regulatory/carbon_emissions`) | settled kWh per home | **P−F ≤ 0 and under 2% of F.** Any fall that comes with a higher unit rate is **classified as rationing, not a saving** (CO1 reports what customers saved, and carbon is never a target, per `tests/company/test_carbon_not_a_target.py`) | 0.60 |
| M7 | B11's own forward-value grade, per book, cut 2020 | `saas/reporting/annual_report.py::_section_held_back_grade` | The per-customer forecast AUC minus the flat forecast AUC is **cannot tell on each book**. Pooled over six, the point estimate is positive and the interval includes 0. The flat level over-predicts departure on **every** book (the switching-collapse regime) | 0.75 / 0.55 / 0.70 |

M1 and M4 are read together, before either is quoted. A margin gain the household side pays for
is a transfer, and the page says so.

## Edge households, reported apart (EP17's four)

Each group is reported with its own n, per arm and per seed. Any group with fewer than 30 homes
per arm, pooled, is reported as "too few to tell", never as a figure.

| group | how it is identified | prediction |
|---|---|---|
| Vulnerable | The company's own flags (`company/crm/vulnerability_register.py`, PSR via `company/regulatory/priority_services_register.py`). **There is no world-side truth** (EP17 pass 1 finding 6: `SyntheticCustomer` has no vulnerability field). This grades who we flagged, not who is vulnerable. | M4 per home under P is more negative than the book's (P prices up the less engaged). 0.55 |
| SME-mislabelled | The world's mislabel class (`simulation/segment_debt_obligation.py`, C6's SME-as-household and the reverse at 2%). This is read in the harness only and never by the company. | Too few to tell on at least four of six seeds. 0.70 |
| Gas-heated | The billing account carries a gas leg (`saas.customer_reaction._billing_account_id` folds legs) | The P−F M2 is larger per home than the book's, because winter pounds carry the 2021–23 step-up. 0.55 |
| Movers | `route == home_move_successor` and move-out departures | P−F on move departures is within ±1 point (the M3 control). P−F margin among successors cannot tell. 0.75 |

## Known biases both arms inherit, so neither can be blamed on an arm

1. **The world's late 2021–23 arrears step-up arrives in winter pounds, not in heads, and clears
   within three quarters.** (`WORKER_FINDING_THE_WORLDS_2021_23_ARREARS_STEP_UP_..._2026-10-15`:
   GBP per account more than 30 days behind went from 62 to 146 to 183 at 2022-12 / 2023-03,
   while the head share fell.) M2 is therefore reported both for the whole window and for the
   window excluding 2022-10 to 2023-06. A P−F that exists only inside that window is reported
   as the world's shape, not the arm's.
2. **B12 is closed on one seed only (61109).** The fixed strike prices its bad debt and levies,
   moving 2016-17 from −4.18 to −1.32 points. The remaining shortfall is the 2018-19 hedge leg,
   not the strike. On fresh seeds, writer one's floor may still sell under true cost. Every
   member reports its renewals below their own cost floor
   (`domain_invariants.DISCRETIONARY_RATE_NOT_BELOW_OWN_COST_FLOOR`). A seed with any such
   renewal is flagged beside M1.
3. **The switching collapse after 2021** (B11 slices 6 and 7). The held-back switch rate is 0.35×
   the fit rate, so retention measures in 2022–23 say little about either arm's skill.
4. **A 40-founder book is mostly selected new shoppers**, not a mature back book (the director,
   2026-10-10). Founders and campaign wins are reported apart, and nothing is extrapolated to
   the 400-founder book.
5. **Acquisition is not an arm here.** Both arms win the same prospects the same way. The
   mission's "finding" half (who we choose to win) is not tested by this comparison, and the
   result must not be quoted as if it were.

## What done means for the runs (not for this record)

- Eighteen members (six seeds × three arms) have been run at one origin commit, each stamped.
- M1–M7 and the four edge groups are graded beside the predictions above, in a result record that
  quotes this file.
- Each prediction is marked held, refuted, or "cannot tell". A refutation is kept next to its
  prediction, never revised.

## What this record does not do

It builds nothing. The flat arm's door, the fresh seeds' listing and the per-home columns that
M4–M6 and the edge groups need are named in the finding above. They come before any run.
