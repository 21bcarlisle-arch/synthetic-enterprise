# B8: no retention desk holds anyone out in the standing run, and the book now says so per desk and year

**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout`

*Delivery seat (executor worktree), 2026-11-21. Claims `land-the-b8-holdout-publishing-from-the-executor-worktree`
and `b8-the-book-publishes-its-holdout-so-uplift-is-measured`. These are one piece of work: the second
claim is the build, and the first is its landing.*

## What was found

- **The work this item said was waiting uncommitted was gone.** The executor worktree was clean at
  `c88197a91f` (= origin/main). Of the 05:08 build, only the test's `.pyc` survived. It was not on
  origin, in the shared tree or in a stash. The tick's 5400s limit cut the landing off, and the
  worktree was reset before the next draw. So the uncommitted work was destroyed, not parked. **The
  executor's reset discards a tick's unlanded work without saying so.** The test's bytecode gave the
  original shape (its names, its keys and its defect strings), and the work was rebuilt from it in
  this turn.
- **Neither retention desk holds anyone out in any standing policy.** `retention_runs_holdout` (the
  renewal offer's coin) and `retention_save_rate_learned_against_holdout` (the save offer's coin)
  both default to `False` in `company/policy/decision_policy.py`. Both coins are blind: each reads
  the account id and the day only. They simply never run. Before this commit the book was silent on
  this, because `retention_holdout_log` is only emitted when the switch is on.

## What landed

- `run_output["retention_holdout_by_desk_year"]`, emitted on every run, through
  `growth_desk.retention_holdout_by_desk`. For each desk it carries `assigned`. If `assigned` is
  false, it also carries a `reason` naming the switch. If true, it carries `by_year[YYYY]` with
  `treated`, `held_out`, `retained_treated`, `retained_held_out`, `interval` (Newcombe, through the
  same `offer_effect_from_counts` both desks now share; `None` where an arm is empty) and `reason`.
- "Retained" means stayed at the decision on the renewal desk, because there is no outcome window
  (`RETENTION_OUTCOME_WINDOW_DAYS` is None). On the save desk it means not lost at that renewal (the
  ledger's own count).
- The GAP for the next step is on `docs/market_research/retention_slope_per_pound_of_renewal_cut.md`
  §3.5. It is not built here.

## Prediction, filed before any book carries the commit

For the first standing book (the `CURRENT_POLICY` arm) whose commit descends from this landing:

| key | will hold |
|---|---|
| `retention_holdout_by_desk_year["renewal_offer"]["assigned"]` | `False` |
| `retention_holdout_by_desk_year["renewal_offer"]["reason"]` | starts `"retention_runs_holdout is off on this policy"` |
| `retention_holdout_by_desk_year["save_offer"]["assigned"]` | `False` |
| `retention_holdout_by_desk_year["save_offer"]["reason"]` | starts `"retention_save_rate_learned_against_holdout is off on this policy"` |
| `"by_year"` under either desk | absent |

What refutes it: either desk reading `assigned: True` on the standing arm. That would mean a standing
policy turned a coin on that this seat does not know about. A value-test arm with
`retention_save_rate_learned_against_holdout=True` is expected to read `save_offer.assigned: True`.
That is not the standing arm, and it does not refute the prediction.

## Status, 21 Nov ~07:45Z (delivery seat, `b8-grade-the-holdout-prediction-and-source-the-held-out-share`)

- **Not graded yet: no book carries the commit.** The newest book on the shared tree is
  `docs/reports/run_output_6a588a832f_20261120T134224Z.json`, and the sim-runner was last booted on
  `270bf6a178`. Neither descends from `775a3c46c`. The prediction above stands unread. The grading is
  handed on as `b8-grade-the-holdout-prediction-on-the-first-book-after-775a3c46c`.
- **The held-out share is researched** (`docs/market_research/retention_slope_per_pound_of_renewal_cut.md`
  §3.5). Nothing published gives a GB desk's share. The rule is SLC 22B (the ban on
  acquisition-only tariffs) with its Fixed Retention Tariff derogation, not 22C, and no text found
  sets a holdout either way. Ofgem's own trials and Ascarza et al. (2016) use held-out controls,
  but neither gives a share as a rule. The build needs no outside share: the company already
  derives one (`competitive_pressure.save_holdout_share`). Two questions stay open: whether GB
  desks hold renewals out at all, and whether the derogation's ¶7 allows withholding the proactive
  approach. They are raised as `b8-s-retention-holdout-needs-two-practitioner`, recommending a
  default-off build at the derived share.
