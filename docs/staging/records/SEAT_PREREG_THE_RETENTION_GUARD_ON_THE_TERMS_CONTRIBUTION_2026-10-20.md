# Pre-registration: the retention guard's offers once it weighs the term's contribution

**Written 2026-10-20, before any run carrying the change has been launched.** Claim
`one-contribution-margin-for-every-renewal-decision` (Lane 0, seat direction), which subsumes
`c34-renewal-margin-net-of-pass-through`. The findings are
`SEAT_FINDING_THE_RETENTION_GUARD_WEIGHS_THE_SPREAD_OVER_WHOLESALE_AS_THE_VALUE_IT_PROTECTS_2026-10-20.md`
and the C34 finding it shares a cause with.

## What changes, said first

The retention guard's `expected_margin` and the missed-retention log's `expected_term_margin_gbp`
were `(unit rate − company forward) × company EAC / 1000`. Both become `term_contribution_per_year`
(`company/crm/renewal_advice_desk.py`), the function C34's `term_contribution_per_month` is now
that value over 12:
`(unit rate − pre_margin_unit_rate) × company EAC / 1000 − FIXED_OVERHEAD_GBP_PER_YEAR[segment]`.
The standing charge stays out as the GAP §6.1 states. Where the term records no locked costs the
value is `None`: the guard already makes no offer there (both cut sizings need the same floor), and
the missed log carries `None`, which `counterfactual_retention` counts as unpriced.

This is the default policy. The off book moves.

## What the inputs say before the run

`/var/tmp/se-ret-margin/reconstruct.py` rebuilt each of the published off book's 92 offered rows
(19 Oct 15:02Z book) outside the run: EAC from the logged cost and discount, the forward from the
logged margin, and the locked costs from the published schedules on the term start, with the notice
taken as start − 42 days. It is an approximation used only to predict.
- Old margin, median GBP 290 a year. New contribution, median −GBP 31.
- 11 of the 92 offers still pass `contribution + acq_cost_saved > retention cost`: 11 electricity,
  0 of 2 gas. They are rows whose strike an upstream writer raised above cost, or very large accounts.
- Under the old margin nothing could fail the value test, because the spread always exceeded a cut
  floored at cost. So no row the old guard refused can pass the new one at the same inputs.

## Predictions, on the full window and default seed, with only this change added

- **R1. Retention offers (`retention_log`) fall from 92 to between 3 and 30.**
  Point estimate: 11.
- **R2. Retention spend (sum of `retention_cost_gbp`) falls from GBP 2,559 to below GBP 1,300.**
  The surviving offers include the large accounts, so spend falls by less than the count does.
- **R3. Churned-with-no-offer rows (`no_offer_churn_log`) rise from 36 to between 55 and 140.**
  The 34 who churned despite an offer now churn without one. Some of the 58 who were retained
  also go.
- **R4. The missed log's median `expected_term_margin_gbp` (non-`None`) falls from GBP 222 to
  below GBP 0.**
- **R5. No offered row has a `None` margin.** This is the control that the floor gate and the
  value gate agree.

I cannot yet say which way the book's total net margin moves. Fewer discounts and more churn pull
in opposite directions, and the churn is on legs whose contribution is mostly negative. The run
reports it; it is not predicted.

**C34's P2′ band** (`SEAT_PREREG_C34_P2_ON_THE_TERMS_CONTRIBUTION_2026-10-20.md`, 0–10 advised of
about 978) **is restated unchanged** for the on-arm run on this book. The guard change moves which
households are on the book at each roll, but not the contribution any one of them carries.

## What each refutation would mean

- **R1 above 30.** The upstream writers raise strikes above cost far more often than the 19 Oct
  book showed, or the reconstruction's locked costs are too high. Print `expected_term_margin_gbp`
  on the offered rows before reading anything else.
- **R1 below 3.** Either the floor or the overhead is double-counted somewhere. Check that the guard's
  contribution and `_cut_inputs["cost_floor"]` read the same `pre_margin_unit_rate`.
- **R5 fails.** The guard can offer on a term that has no floor. That is a defect in the cut sizings,
  not in this change.

## Grade, 2026-10-20 13:10 BST — off book at `c61d8b608`, full window, default seed

Run: unit `longjob-retention-guard-contribution-grade-c61d8b608`, worktree at `c61d8b608` (its
salvage commit touches only generated observability files). Output
`/var/tmp/se-ret-margin/off_book.json`, log `/var/tmp/se-ret-margin/run.log`. Baseline: the
published book, `producing_commit ad8afadc5`, 19 Oct 15:02Z.

| | Predicted | Published book | `c61d8b608` | Verdict |
|---|---|---|---|---|
| R1 retention offers | 3–30 (point 11) | 92 | **9** | confirmed |
| R2 retention spend | < GBP 1,300 | GBP 2,559 | **GBP 880** | confirmed |
| R3 churned with no offer | 55–140 | 36 | **66** | confirmed |
| R4 missed-log median margin | < GBP 0 | GBP 222 | **−GBP 42** | confirmed |
| R5 offered rows with a `None` margin | 0 | 0 | **0** | confirmed |

The nine offers: 6 retained, 3 churned despite the offer. The two largest are both PROS-2022-0400,
the very large account the reconstruction named (contribution GBP 2,278 a year in 2023, GBP 193 in
2024). One offered row carries a negative contribution (PROS-2018-0223 2021-07-24, −GBP 10.8 against
a GBP 15.1 cut). The value test passed it because the acquisition cost saved is added before the
comparison. That is the design, and it is noted rather than called a defect.

### The book's net margin moved, and this run cannot say why

Net margin was GBP 547,630 on the published book and is **GBP 446,884** here (log line "Net margin",
final treasury GBP 696,884 less the GBP 250,000 start), a move of **−GBP 100,746**. This was not
predicted. It is also not attributable to the guard change. `ad8afadc5..c61d8b608` is 91 commits,
and several of the commits touching `company/`, `saas/` or `simulation/` are on by default:
- `3d518bdef`: the SLC 27.8D dual-fuel offset;
- `6208ea6dd`: the half-hourly account's own EAC;
- `e0b301545`: sole-occupant death;
- `78a36a84c`: income moves for an under-water household;
- `f8fdb99cc`: the budget book pays in pence.

The guard change's own direct pieces are small:
- 83 fewer discounts save GBP 1,679 of spend.
- The 66 churns with no offer carry −GBP 2,339 a year of contribution between them; 5 of the 66 are
  positive.
- Book net margin leaves cost to serve out per leg, so the 30 extra churners forgo at most about
  GBP 55 a leg-year of book margin.

**Prediction for the one-variable control, filed before it runs.** The off book at `6fe4282c0`
(`c61d8b608`'s parent) on the same command:
- **C1.** Its net margin is within GBP 10,000 of GBP 446,884. Most of the −GBP 100,746 is the other
  90 commits, not the guard. The sign of the guard's own move is not predicted.
- **C2.** It makes 60–120 retention offers. The old spread passes almost every eligible roll, as on
  the published book.

If C1 fails, the guard change moved the book by more than its direct pieces can explain. The first
thing to read is the churn journeys of the 30 extra no-offer churners: whether their exit changed
the collections, bad-debt or hedge positions downstream.

## Grade of the one-variable control, 2026-10-20 17:20 BST — off book at `6fe4282c0`

Run: unit `longjob-retention-guard-parent-control-6fe4282c0`. It started at 14:35 and finished at
16:12 BST (1 h 37 min wall clock, 5.7 GB peak). Artefact `/var/tmp/se-ret-margin/parent_off.json`,
log `/var/tmp/se-ret-margin/parent.log`. The worktree it ran in has since been removed, so the commit
it ran at rests on two things: the script's own docstring, and the retention counts below. Those
counts match the published pre-guard book exactly, and the guard at `c61d8b608` cannot produce them.

| | Predicted | `6fe4282c0` (parent) | `c61d8b608` | Verdict |
|---|---|---|---|---|
| C1 net margin | within GBP 10,000 of GBP 446,884 | **GBP 447,689** | GBP 446,884 | confirmed (+GBP 805) |
| C2 retention offers | 60–120 | **92** (58 retained, 34 churned despite) | 9 | confirmed |

Other figures from the parent run:
- Retention spend was GBP 2,526, against GBP 2,559 on the published book.
- Churns with no offer were 36, the same as the published book.
- Gross margin was GBP 1,352,137 and bad debt GBP 101,898.

**Attribution.** Of the −GBP 100,746 between the published `ad8afadc5` book and `c61d8b608`, the
guard change accounts for **−GBP 805**, about 0.8%. The other **−GBP 99,941** comes from the 90
commits in `ad8afadc5..6fe4282c0`. The guard's direct pieces were bounded beforehand: GBP 1,679 of
spend saved against the contribution of the 30 extra churners. A net −GBP 805 sits inside that
bound, so the guard needs no further explanation and the "if C1 fails" path does not apply.

**What this leaves open.** The −GBP 99,941 is unattributed. It is spread across the five default-on
commits listed above, plus anything else in that range, and this control cannot split it further.
The next step is to bisect the range on net margin, starting with the five named commits. That is
handed on as a separate item.
