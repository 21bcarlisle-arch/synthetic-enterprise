**Severity:** LATENT · **Lane:** W4_the_wall · **Epoch:** unassigned · **Atom:** `unminted`
**What:** the in-loop annual DD review is fed settled revenue at TRUE kWh, where the supplier holds only its estimated bills · claim `dd4b-in-loop-bill-basis-tail-and-probe-placebo`
**Status:** measured 2026-10-13 on `f200-low` (200 founders, budget 0); remedy built 2026-10-13, claim `dd4b-in-loop-review-reads-the-suppliers-own-bill` (`simulation/dd_review_in_loop.py`). Evidence in `records/SEAT_PREREG_DD4B_AT_THE_IN_LOOP_REVIEW_LOW_AND_HIGH_2026-10-12.md`, "The content tail, explained". Not yet re-graded at range ends -- that re-grade is owed to whoever next runs `f200-low`/`f200-high` after this landing.

# The in-loop DD review is told true consumption, not the supplier's estimated bills

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
