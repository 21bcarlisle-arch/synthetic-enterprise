**Severity:** LATENT · **Lane:** W4_the_wall · **Epoch:** unassigned · **Atom:** `unminted`
**What:** the in-loop annual DD review is fed settled revenue at TRUE kWh, where the supplier holds only its estimated bills · claim `dd4b-in-loop-bill-basis-tail-and-probe-placebo`
**Status:** measured 2026-10-13 on `f200-low` (200 founders, budget 0); remedy built 2026-10-13, claim `dd4b-in-loop-review-reads-the-suppliers-own-bill` (`simulation/dd_review_in_loop.py`). Evidence in `records/SEAT_PREREG_DD4B_AT_THE_IN_LOOP_REVIEW_LOW_AND_HIGH_2026-10-12.md`, "The content tail, explained". Re-graded at both range ends 2026-10-13 (`f200-low-ownbills`, `f200-high-ownbills`): the volume and move-in tails are gone; a 45-review residue at partial final bills remains, see "Result" at the end.

# The in-loop DD review is told true consumption, not the supplier's estimated bills

**Fate (2026-10-13, clear-the-decks):** DONE -- 5cdaca020 The in-loop DD review now reads the supplier's own bills, not true consumption -- confirmed on origin.

`simulation/dd_review_in_loop.py` builds the review's bills from the loop's monthly settled revenue,
grossed up at VAT. In this world that revenue is priced at the meter's TRUE consumption. The company's
review door (`annual_dd_review_view`) then sizes the household's DD from it. A real supplier reviewing
a household with estimated reads holds its own issued bills, estimates included, not the true volume.

**Size, on `f200-low`.** 135 of 847 reviews differ from the post-loop chain (the supplier's own bills)
by more than 5% on volume alone. In 111 of them the true-up lands in a later window. In 24 (8
households) it never lands. `C7`'s estimates run at a fifth of true use for 42 months, so the in-loop
review is told 3.8 times what the supplier ever billed. Through the chain, 365 of 847 reviews end up
with a different current DD.

**Why it is LATENT, not BLOCKING.** No figure published as the supplier's own knowledge reads the
in-loop chain: the published census is the post-loop one. What the in-loop chain drives is the WORLD's
DD4b response, which is correctly the world's. The defect is in what the household is said to have been
TOLD: a supplier could not have told it that amount.

**A second, separate defect the census exposed.** `C7` has a smart meter and 42 consecutive estimated
bills with no forced catch-up: `simulate_read` (`simulation/meter_reads.py`) treats a smart meter not in
smart mode as traditional, and nothing in the world forces a read across 42 months. This belongs to the
existing atom `W2_36_unbilled_energy_arises_the_way_it_does_in_reality` (estimated reads and their
true-up), not a new one.

**Remedy, built 2026-10-13.** `InLoopDDReview` now keeps each leg's own settled rows (`observe`) and,
at each window close, calls `simulation.run_phase4c_on_phase2b.build_monthly_bills` -- the same
`SimulatedReadFeed`-backed assembly door the post-loop chain calls -- restricted to that leg's rows
observed so far, rather than grossing up the loop's own settled revenue at true kWh. Because
`SimulatedReadFeed.read_for` seeds its RNG on `(customer_id, period_end)` alone, a bill assembled from
a prefix of a leg's rows is byte-identical to the one the post-loop chain assembles later from the
complete history. The move-in attribution is resolved the same way, by construction: both chains now
read one assembly's decision, not two. Knowledge pass:
`docs/market_research/a_suppliers_annual_dd_review_is_sized_from_its_own_issued_bills_not_true_
consumption_2026-10-13.md`. New control:
`tests/simulation/test_dd_review_in_loop.py::test_the_review_told_in_the_loop_is_the_post_loop_chains_
bills_to_the_penny` asserts the in-loop chain's told events equal the post-loop chain's events exactly
(spend to the penny, not just keys). NOT yet re-run at `f200-low`/`f200-high` range ends -- the 135/44
tail counts above are pre-remedy and are owed a re-grade.

**Landed 2026-10-13 by the executor seat** (claim `dd4b-in-loop-review-reads-the-suppliers-own-bill`),
from the prior invocation's unlanded shared-tree copy, with the one caller hunk in
`simulation/run_phase2b.py` (`post(cid, month)`). Mutation: rebuilding the bills as settled revenue x 1.05
inside the new structure reds the to-the-penny control. Still owed from K8: the knowledge note declares
`none` because no site topic covers the DD review, so it is not yet published on the site.

**Pre-registered 2026-10-13, before the re-grade runs** (claim
`dd4b-regrade-the-in-loop-bill-tail-after-own-bills`). Runs `f200-low-ownbills` and
`f200-high-ownbills` under `/var/tmp/dd4b_runs/il/`, from a worktree at `d73cc0d8f` (remedy
`5cdaca020` included); the pre-remedy `f200-low/` and `f200-high/` are kept. Graded with
`tail200.py` and `reconcile()`. Predicted, at both range ends:
- `only_in_loop` = `only_post_loop` = 0, `max_abs_rise_gap_on_matched` = 0.0.
- 0 of N matched reviews differ from the post-loop chain by more than 5% on spend (was 135/847 at low).
- 0 move-in window-0 rows (was 44), and 0 reviews with a different current DD (was 365).
The rival: the loop calls `observe()` per term and `post()` per month, so a term boundary falling
inside a review window could leave rows unobserved when the review posts. That would show as a
non-zero residue concentrated at term boundaries, with the in-loop spend BELOW the post-loop spend.

**Result, 2026-10-13** (runs `f200-low-ownbills`/`f200-high-ownbills`, from `d73cc0d8f`). Graded with
`/var/tmp/dd4b_runs/il/tail200_arg.py <run dir>` (`tail200.py` with the run dir as an argument; on the
old `f200-low/` it reproduces 179 = 135 volume + 44 move-in) and `reconcile()`. Low and high give the
same told stream byte for byte. They did before the remedy too: the setting moves only the world's
answer, not the bills.
- Matched reviews: 801. More than 5% apart on spend: **0** (was 135 + 44). Move-in window-0 rows:
  **0** (was 44). Current DD different: **0** (was 365). `max_abs_rise_gap_on_matched` = **0.0**.
  These three legs held.
- `only_post_loop` = **45**, predicted 0. **That leg is refuted.** The rival I named, a term
  boundary leaving rows unobserved, is not the cause. `observe()` runs before `post()` in
  `run_phase2b.py`, and the residue does not have the shape that rival predicted. The cause, which
  splits the residue exactly: all 45 post-only reviews are dated on a day that is not a month-end, and
  all 801 matched reviews are. A leg's partial last month is billed to its last settled day (a leaver's
  final bill; `2025-06-07` at run end). `post()` looks for its event at `_month_end(month)`, so it
  never finds one there. 37 are leavers and 8 are the run-end month. 8 of the 45 are material rises
  (301 vs 293).
- Before the remedy, the in-loop chain DID tell these 45, because its home-made bills were all dated
  at month-end. So the remedy changed one thing in the world: a household is no longer told a review
  at its own final bill.

**Which side is wrong is not settled, and I did not fix either one.** Making `post()` match on month
would make the two chains equal. But it would also teach the world to tell a leaving household a new
DD on its final bill. As practice I believe that is wrong: the account closes and the mandate ends.
That belief has no source behind it yet. If it holds, the defect is in the published post-loop census
(`annual_dd_review_view` reviews at a final bill and at the run-end stub), not in the loop: 45 of its
846 events, 8 of its 301 material rises. Handed on as
`dd4b-does-a-supplier-review-the-dd-at-a-final-bill`: knowledge pass first (K8), then decide the
side. The two live claims flagged as possible duplicates (`dd4b-grade-the-in-loop-probe-placebo`,
`the-dd-amount-is-set-from-the-companys-own-twelve-month-forecast-plus-the-balance`) are different
work on the same file. Neither was touched.
