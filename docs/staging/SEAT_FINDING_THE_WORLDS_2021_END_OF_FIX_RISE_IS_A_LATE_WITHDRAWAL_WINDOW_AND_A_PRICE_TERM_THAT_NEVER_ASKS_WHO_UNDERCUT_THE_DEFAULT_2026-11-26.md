**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The world's 2021 end-of-fix rise is a withdrawal window that starts a quarter late, plus a price term that never asks who undercut the default

*Lane 0 item `the-worlds-2021-23-end-of-fix-leave-rate-checked-against-the-switching-collapse`. The knowledge page (K8)
is `docs/market_research/what_happens_at_the_end_of_a_fix_and_whether_the_world_does_it_2026-11-25.md` §6, which
carries the tables. No run was launched. Inputs: the s.12g control records in `/var/tmp/vtn-out/{twin,rankq}/`, the
capture `docs/reports/qep_g_second_qep_pass_anchor_departure_factors.json`, the DESNZ QEP 2.7.1 quarterly sheet, and
`docs/domain_artefact_library/regulatory/gb_best_deal_gap_to_default.json`. Decided blind to company results: the
question is the world against the switching record.*

## For the director, in plain English

The world made households leave fastest just as the real market froze. That was not a mis-set era rate. Two smaller
things caused it. First, the world already switches off fixed deals while none were on sale, but it switches them off
from January 2022. Ofgem's own figures show nothing cheaper than the default from October 2021. Second, in those
autumn months our renewal price was above the capped default, and the world read that as a reason to leave us. In
reality the household just rolls onto our default, because no rival offered anything cheaper. Fixing the first
(one date, from the same evidence as the window's end date) takes those households off the leave-or-stay roll
entirely, which is what the record says happened.

## What was found

1. **The item's premise, corrected.** The "2021–23" bucket on the K8 page holds no 2022 or 2023 fix end. Every
   un-offered fix end in it is a 2021 renewal. The rise is 2021 H2: P(leave) 0.54, and 0.58 for Oct–Dec, against
   0.40 in H1 and 0.42–0.45 across 2019–20.
2. **Which input carries it.** Not the level anchor (×0.92, the right way). Market opportunity moves the right way
   (×0.77, which is the record's annual ratio), but it is annual, while the record's collapse is quarterly: Q4 2021
   transfers were 579k, 0.40× the 2020 quarterly mean. **Price position carries the rise.** Its response goes ×2.5
   because our renewal moved from below the default to 7–21% above it, and the reference is our own capped default.
3. **The window starts a quarter late.** `FTC_WITHDRAWAL_WINDOW` = 2022-01-01 to 2023-06-30. The published best-deal
   gap is 0.0 from 2021-Q4 through 2023-Q2. The window's end agrees with the record and its start does not.
4. **2024–25 (not asked).** The rise there is carried by the level anchor (20.8, fitted on 4 decisions, borrowed by
   2025). This is already recorded as rung-1 debt. It should be refit on the capture that follows fix 0.

## Predicted, filed before any build or run

- **Fix 0** (window start 2021-10-01): the s.12g control arms' 29 un-offered 2021-Q4 fix-end rolls → 0. Those
  households take the SVT route at about 3% a quarter, against 0.58 today. 2021's account-year departure rate moves
  down, so the 2021 anchor needs capture → refit → capture. The test
  `test_the_worlds_realised_departure_rate_is_inside_the_published_band` will say whether it does.
- **Fallback, if fix 0 is refused.** A quarterly market opportunity alone gives 0.58 → 0.44. With the price
  differential capped at 0 in zero-gap quarters, about 0.39. The record implies about 0.2. The residual is
  dissatisfaction, which is not opportunity-scaled, and suppliers being closed to new customers is a GAP.

## What it means for the queue

The rankq re-grade waits on fix 0's capture → refit, not on this page. §5 of the K8 page holds either way: a lower
leave rate in 2021 Q4 makes an offer worth less there, so the conclusion that offering less makes more money gets
stronger.

## The fix-0 capture: launched, first attempt died at import (2026-11-27)

Lane 0 item `launch-the-fix-0-capture-so-the-refit-continuation-releases`. Worktree
`/var/tmp/se-fix0-capture-wt`, detached at `f0012484a2` (origin/main, which descends from the window
landing `daf6029e9c` in `/var/tmp/se-fix0-window-landed.sha`).

- **r1 died before the world started.** Unit `longjob-fix0-departure-capture`, log
  `/var/tmp/se-fix0-capture/capture-r1-import-failure.log`: `ModuleNotFoundError: No module named 'tools'`
  at `tools/capture_departure_factors.py:124`. Running the script by path puts `tools/` on `sys.path`, not
  the repo root. The code was fine. The handed-on command line had no import root, and the queued refit row
  still carries that command.
- **r2 is running.** Unit `longjob-fix0-departure-capture-r2`, with `--setenv PYTHONPATH=/var/tmp/se-fix0-capture-wt`,
  declared at 4,000 MB peak and 45 min. Earlier runs of this tool took about 25 min. It got past the imports
  into market loading. Log: `/var/tmp/se-fix0-capture/capture.log`. Artefact:
  `/var/tmp/se-fix0-capture/departure_factors_fix0.json`.
- **The refit row was drawable too early.** Its hold was on the window sha file, which already existed, so it
  could have launched a second capture beside r2. It has been replaced by a row held on the capture artefact.

## Fix 0 graded on its capture; the 2021 refit is REFUSED by the fitter (2026-11-27)

Lane 0 item `fix-0-2021-anchor-refit-on-the-moved-window-capture`. Capture r2 completed ("SURVIVED — full window"):
`/var/tmp/se-fix0-capture/departure_factors_fix0.json` (282 renewal rows) plus its SVT table (9,131 segment
decisions, 251 departed), world at `f0012484a2`. The only world commit since then is `66911e6380`, which changes
demand, not departures. Fitter output: `/var/tmp/se-fix0-refit-out.txt`.

**The prediction, graded on the capture.** The "29" counts the s.12g control arms, which are a different run.
This capture can only show the direction, and the direction holds.
- 2021-Q4 renewal-route (leave-or-stay) rows: **0**. Q1 8, Q2 3, Q3 8. The committed capture had 1 in Q4.
  Q3 2021 still rolls at P(leave) 0.29–0.53, as designed, because the window now opens on 1 Oct. **HELD.**
- Households that joined the SVT route in 2021-Q4 (`sim_years_on_svt` < 0.3): 34, mean hazard **3.7% per
  segment** (segments average 74 days), 0 departed. The whole SVT route ran 2.8%/segment that quarter against
  3.9–4.2% in 2020, and 0.5% from 2022-Q1. "About 3% a quarter against 0.58": **HELD.**

**The refit: not done, and the fitter is right to refuse.** `python3 -m tools.fit_year_level_anchor` on this
capture gives no whole-book fit: "22 account(s) depart more than once". Only 1 or 2 of these are re-acquisitions.
The rest come from 35 (account, date) pairs in the renewal table, against 0 in the committed capture. These
pairs are **one dual-fuel home's two supply legs, each captured as its own renewal under one `customer_id`**.
Both legs use the same `random_roll` (35 of 35) but carry different `realized_churn_probability` values, because
each leg has its own rate and so its own price response. The outcomes: 19 both left, 14 both stayed, **1 split**
(one leg left, the other stayed), and 1 triple. So a household-level departure is counted twice, and one home
sometimes half-leaves. That is the same class as `66911e6380` (one home, two lives), on the departure side.
The per-year renewal-only diagnostic still prints (2021: 19 rows, anchor 2.64 against the committed capture's
2.42). The tool says it is not the world's level, and it is NOT pasted into `departure_level_anchor.py`.
`YEAR_LEVEL_ANCHOR[2021]` stays at 7.733780.

**The committed capture cannot fit either.** On `qep_g_second_qep_pass_anchor_…` the fitter refuses because
30 SVT rows reproduce under a market-blind hazard. 7.733780 is therefore anchored to a capture the current
fitter calls stale, and that was already true before fix 0.

**The signal file is not written.** `/var/tmp/se-fix0-anchor-refit-landed.sha` releases the rankq re-grade, and
that re-grade must not run on an un-refitted anchor. It stays held until a refit lands.

**Next:** a dual-fuel home makes ONE departure decision. Either the world rolls once per home and the gas leg
follows its primary (the `66911e6380` pattern), or the capture keys a leg. Re-capture, then refit.
Which side is a fidelity question: the 1 split pair is a world behaviour, not just a counting problem.
