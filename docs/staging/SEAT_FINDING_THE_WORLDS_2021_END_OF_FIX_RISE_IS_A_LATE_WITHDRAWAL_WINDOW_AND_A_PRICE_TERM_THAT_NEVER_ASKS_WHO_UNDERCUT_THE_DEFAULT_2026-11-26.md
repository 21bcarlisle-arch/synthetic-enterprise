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
