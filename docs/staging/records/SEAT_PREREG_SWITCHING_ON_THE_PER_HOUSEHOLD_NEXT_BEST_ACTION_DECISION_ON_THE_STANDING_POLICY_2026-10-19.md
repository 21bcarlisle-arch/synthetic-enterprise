# Pre-registration: switching `next_best_action_decides_per_household` on, on the standing policy

**Written 2026-10-19 ~11:40Z, before the `8b6fea024` decision probe finished and before any of its
rows were read.** Claim `switch-on-nba-per-household-after-the-c35-grade` (Lane 0, seat).
Subject: `DecisionPolicy.next_best_action_decides_per_household` (`company/policy/decision_policy.py`),
consumed only by `company.crm.next_best_action.states_for_decision`. Starting points: the C35 finding
(`docs/staging/WORKER_FINDING_THE_COMPANY_DECIDES_A_DUAL_HOUSEHOLD_PER_LEG_AND_C35_CHARGED_IT_TWO_RISES_FOR_ONE_BENEFIT_2026-10-18.md`)
and the C35 prereg §3 (`SEAT_PREREG_B11_C35_C34_ON_THE_FIRST_PUBLISHED_DUAL_FUEL_RUN_2026-10-18.md`).

## 0. What the flip reaches, said before predicting what it moves

The flag is read in one place, `states_for_decision`. Its callers in the tree, read at 11:37Z, are
`tools/retention_rise_count.py` (a harness instrument, which sets the flag itself from
`--per-household` and ignores the standing value) and the tests. No module under `company/`,
`simulation/`, `saas/` or `sim/` imports `decide` or `states_for_decision`. The only import of
`company.crm.next_best_action` from the run's side is `contact_programme`'s `in_contact_holdout`. The
retention rise that the merge exists for (`next_best_action_shares_by_retention_rise`) is off on
every standing policy.

So "this book" has two readings, and I predict each separately:

- **The run.** What a standing-policy run decides.
- **The decision the switch exists to fix.** C35 on the `8b6fea024` probe with the rise on, which
  is the population a future rise switch-on will act on.

## 1. Predictions

- **N1. The run: 0 decisions change, on any household.** A standing-policy run at the flipped
  commit gives the same bills, offers and book as one before it, to the digit, at a fixed seed.
  The flip is a defect fix staged ahead of the rise, not a behaviour change. If any run figure moves,
  N1 is wrong, and it means C34/C35 has a production caller I did not find.
- **N2. The instrument: `retention_rise_count`'s two readings do not move with the flip.** The tool
  sets the flag from `--per-household` in both directions. A copy that read the standing value
  would make the "off" reading silently become "on" after the flip. I predict it does not, and the
  control checks it.
- **N3. The decision the switch fixes: how many dual households change.** On the `8b6fea024`
  probe, every `(billing_account, term_start)` group with two legs changes from two decisions to one.
  The count of households that change is `rows − decisions(on)`. As a share of rows with a forecast,
  I put it at **0.30–0.45** (C35 prereg C2's 0.55–0.60 ratio of decisions to rows, widened up because
  this run's campaign is dual on every gas home, so B11 graded 550 merged accounts, not 447). Groups
  of one (single-fuel homes, and a dual home's legs renewing apart) do not change.
- **N4. Direction, per changed household, with the rise on.**
  - (a) **The household pays one rise in place of two.** Over the groups rescued both ways, the
    household's monthly rise on is **0.45–0.60** of the sum of its two leg rises off (finding's
    real-input table: 2.15 against 2.06 + 2.09 = 0.52).
  - (b) **Rescues move only towards the household, refused → rescued**, because the headroom is the
    two legs' summed headroom while the advice is costed once. Groups that go rescued (at least one
    leg) → refused on: **≤ 2%** of the changed groups.
  - (c) **Our side is unchanged in sign.** Every merged rescue still clears zero at both hazard ends.
    This is what `price_retention_rise` requires, so a breach is a defect, not a finding.

## 2. How it is graded

N1 is graded by the census above, repeated on the flipped commit: no new import of `decide` or
`states_for_decision` from the run's side, and the flip's diff touching no run path. A full
fixed-seed run is not spent on it, because the census answers it. **This is a weaker grade than a
run, and I am saying so.** The next scheduled run after the flip lands is the one-variable reading:
if its figures differ from the previous run at the same world digest, the flip is the first
suspect. N2 is graded by the control landed with the flip. N3 and N4 are graded from the
`8b6fea024` probe by a short script over `count()`'s groups, beside the C35 grade in
`SEAT_PREREG_B11_C35_C34_ON_THE_FIRST_PUBLISHED_DUAL_FUEL_RUN_2026-10-18.md` §7. Wrong predictions
are kept.
