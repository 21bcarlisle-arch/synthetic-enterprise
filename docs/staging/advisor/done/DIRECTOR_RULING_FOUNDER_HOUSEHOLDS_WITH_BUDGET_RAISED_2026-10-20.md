**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] Founders are 400 households, and the settlement budget rises to about 7,800 customer-years (2026-10-20)

**Type:** RULING, through the advisor channel. It answers `for_the_director` row `your-400-household-founder-ruling-fits-in`, which recommended "households with the budget raised" (`019924a7`). The advisor told the director:

> Recommendation: households, budget raised to about 7,800 customer-years; meanwhile it holds 400 meter points. My view: agree, with one caveat — about 0.5 GB of memory headroom is thin, so I'd ask it to watch peak memory on the first few runs. Runs will also take longer, roughly in proportion to the extra customer-years.

The director's words, from chat on Tue 20 Oct:

- 17:40 BST: "Great, agree with all you said."

## What to do

1. **Switch the unit.** Set `founder_unit: households` with `founder_accounts: 400` in `docs/design/FOUNDER_BOOK.yaml`. Raise the settlement budget to the figure your measurement gives for 400 households plus a campaign that can still win, about 7,800 customer-years. Record the derived figure, not a typed guess. Trailer: `Director-doc: his-words -- founders are 400 households, budget raised, director 20 Oct 17:40`.
2. **Close the row** `your-400-household-founder-ruling-fits-in` with this ruling.
3. **His caveat binds.** Watch peak memory on the first production runs at the new shape, at least the first three, against the 6,008 MB allowance. Record each peak in the stretch log. If a run comes within 5% of the allowance, or the reaper fires, go back to 400 supply points for production. Then bring a proposal that closes the gap (streaming per R8, or index-once per R6). Do not trim headroom elsewhere to make room.
4. **Re-run the checks on the change.** Run `tools/world_claims.py` over the new book. Record before and after on the same seed: homes, supply points, dual share, wins per year, run time. Record this as the new held draw (EP17).
5. **Report** in one stretch-log entry: the budget figure and how it was derived, the census before and after, peak memory and wall time for each of the first runs, and the published figures it moves.

— Director ruling, 20 Oct 2026, his words above; the drafting is the advisor's.

## In hand (worker tick, 20 Oct 16:58Z). Do not start it again.

- Step 2 is done. The row is answered (`director_concerns --answer`).
- The budget is derived from the book at seed 20260724: 6,535.7 founder cy (689 records) plus the
  campaign's 1,206.5 cy room gives 7,742.2. It ships at **7,700**.
- **Step 1 waits on a curve.** `test_the_settlement_ceiling_does_not_outrun_the_measured_memory_curve`
  prices the ceiling from the newest slope file. The 9 Oct curve supports about 6,857, so 7,700 cannot
  land on it. The curve is re-taken at the new shape by `longjob-founder-households-ceiling-probe`
  (points 7,000 and 7,700, worktree `/var/tmp/se-hh-probe`, log `/var/tmp/se-hh-probe-probe.log`,
  about 4.7 h). The pre-registration and its decision rule are in
  `docs/staging/records/SEAT_PREREG_THE_SETTLEMENT_CURVE_AT_400_FOUNDER_HOUSEHOLDS_AND_A_BUDGET_OF_7700_2026-10-20.md`.
  When it completes: grade it, land the slope file together with `founder_unit: households` and the
  budget, then do steps 3–5. The continuation `founder-households-switch-after-the-curve` carries this.

## Moved to done/ by the channel's refusal (worker tick, 20 Oct). The ruling stands.

The advisor channel refused this file because "the commit that staged it (e81c55a05) is not signed
by the advisor's pinned key". That is true, but it is not a reason to doubt the ruling. The advisor
staged the ruling in `dbb56caae`. `e81c55a05` is the seat's own commit, which appended the In-hand
section above. The channel checks only the newest commit that touched the path, so any seat append
to an advisor file makes that file refused. In future, record in-hand notes in `docs/staging/records/`
and leave the advisor's file alone.

Steps 1, 3, 4 and 5 are still owed. The continuation `founder-households-switch-after-the-curve`
carries them and now points here. When they are done, add a Done section below.

## Done (delivery seat, 20 Oct 23:10 BST)

- **Step 1.** `founder_unit: households` (400 homes, 689 supply points at seed 20260724).
  `SETTLEMENT_CUSTOMER_YEAR_BUDGET = 7700.0`, derived as 6,535.7 founder cy plus 1,206.5 campaign
  room = 7,742.2, floored to 50. Both land with the curve re-taken at this shape,
  `docs/observability/settlement_ceiling_slope_20261020.json`. At 7,700 the peak is 5,113.2 MB, or
  5,340 MB with the parent. That is 668 MB under 6,008 and outside the 5% stop line. The curve
  supports 8,638.6. The pre-registration is graded in
  `docs/staging/records/SEAT_PREREG_THE_SETTLEMENT_CURVE_AT_400_FOUNDER_HOUSEHOLDS_AND_A_BUDGET_OF_7700_2026-10-20.md` §5.
- **Step 4.** `tools/world_claims.py` was run over both books: every claim holds on every route,
  before and after. Same-seed census, before → after: homes 233 → 400; supply points 400 → 689;
  founder dual share 71.7% → 72.3%; quotes 3,373 → 3,250; settled campaign wins 216 → 205 (of
  619 → 597 funnel); run time 5,481 s → 9,232 s. This is the new held draw.
- **Step 5.** One stretch-log entry, `docs/status/SEAT_STRETCH_LOG.md`, 2026-10-20.
- **Step 3 is still open, by construction.** It needs the first three production runs at the new
  shape. The continuation `founder-households-first-three-peaks` carries it, with the rule: within
  5% of 6,008 MB, or the reaper fires, go back to 400 supply points at 5,000 and bring a proposal.
  The journal leg of the ceiling control
  (`test_the_ceiling_still_fits_the_peak_systemds_own_journal_reports_today`) re-prices on those
  peaks automatically.
