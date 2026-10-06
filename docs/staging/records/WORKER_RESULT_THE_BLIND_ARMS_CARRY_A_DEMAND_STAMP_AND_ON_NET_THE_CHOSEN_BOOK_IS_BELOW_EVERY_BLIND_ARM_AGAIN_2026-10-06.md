**Severity:** MATERIAL · **Lane:** delivery (lane 0) · **Direction item:** `blind-envelope-arms-carry-a-demand-stamp` · **Claim:** released on landing

# The blind arms carry a demand stamp, and on net the chosen book is below every blind arm again

The four first-hand arms in `docs/design/blind_envelope_arms_2026-09-11.json` were re-run with the
09-15 harness (`arm_rerun.py`, SIM_FAST_MODE=1) **twice** on 2026-10-06. The first run, from
origin/main `8205e9382`, stamped demand `bd27327df0fd194d` and never landed. `fc47cd363` (each
home's always-on load drawn from EFUS, W1_29) landed at 22:31 and moved the live demand to
`b422b3dd8de98b8c`, so the first filing was stale before it could land. The filed figures are from
the second run, from a clean `git archive` of origin/main `fc47cd363`, run in two parallel lanes.
Each arm carries world, home and demand digests `cdba75ebb9197b33` / `35f8efe8ff02f245` /
`b422b3dd8de98b8c`. `_blind_envelope` computes the block as **available** against the shared
tree's live demand: three blind arms in the span, C' excluded with its reason.

## Two things the re-run surfaced before it could be filed

1. **The departure world had moved as well.** The arms now carry `cdba75ebb9197b33` where all five
   arms shared `39a192ce04c1eda8`. C' cannot be re-run and keeps the old digest. `_blind_envelope`
   checked world agreement over every FILED arm, so C' would have refused the block for good,
   even though it is already excluded from the span. Fixed in the first commit of this claim: the
   check now reads only the arms in the span. An arm in the span that states another world still
   refuses. Both legs are tested and both mutations were run.
2. **`cull83` is infeasible in this world.** B now settles 57 accounts and the plain cull settles
   62. 83 accounts cost more than the headroom, so the truncated chooser returns None and the run
   falls back to the plain cull. The `cull83` output is identical to ARM A on all five lines.
   Filing it would have counted one book as two blind arms, which would have held the span at the
   three-arm floor with only two distinct books. ARM C is defined as *count-matched to B*, so it
   was re-run as `cull57` and filed as `C_cull_count_matched`. The reason is in the arm's
   `count_matched_to_B` field.

## The result (positions only; pounds are fast-mode and not publishable)

Filed run, demand `b422b3dd8de98b8c`:

| line | A cull (62) | C cull57 | D tenure (59) | **B chosen (57)** | B vs blind span |
|---|---|---|---|---|---|
| gross margin | 362,430 | 362,662 | 360,732 | **370,874** | above all |
| revenue | 630,396 | 634,850 | 633,492 | **642,625** | above all |
| bad debt | 8,484 | 6,988 | 10,796 | **14,267** | above all (worse) |
| net margin | 115,900 | 123,249 | 116,053 | **108,100** | **below all** |
| net after cost to serve | 77,346 | 81,308 | 77,251 | **69,023** | **below all** |

Superseded run, demand `bd27327df0fd194d` (kept in the artefact's
`re_run_2026-10-06.figures_on_2026_10_06_at_demand_bd27327df0fd194d`): the same five orderings.
B's net margin was 103,331 against blind 109,786–118,522.

**Predictions.** The first, written at 19:34:02Z while cull57 was still running
(`~/.cache/seat_lane0_20261006/prediction.txt`), said B stays above all on gross and revenue and below all
on both net lines. It held, but it was blind only on the cull57 placement. The second was written at
21:39Z before any arm of the b422 run started (`~/.cache/seat_lane0_20261006b/prediction.txt`) and
said the same five orderings would survive the always-on change. It held on all four arms.
Every figure rose about 11–13% under the new demand, and no ordering moved. B settles 57 in
both worlds, so `cull57` is still the count-matched arm. That count was read from B's run before ARM C was filed.

**What moved since 09-15.** The 09-15 re-run put B ABOVE every blind book on net margin and on
net after cost to serve. This run reverses both, back to the 09-11 direction. The
`_blind_envelope` docstring still describes the 09-15 reading. It is corrected beside the claim
in the second commit.

**I cannot yet say why.** At least three things changed together: the departure world (anchor
refit), the four demand changes, and the code between `331c4958f` and `8205e9382`. The book also
shrank from ~83 accounts to ~57. On the evidence available, the visible mechanism is bad debt:
B's is the highest of the four (13.2k against 6.1k–9.8k), while B wins on gross. One seed, one
world. These are orderings and not intervals.

## Hazards for whoever reads this next

- **The stamp is perishable by design, and it perished once in this claim.** The hazard this
  record first named was W1_29's always-on draw landing. It landed as `fc47cd363`, and the block
  would have withheld itself, correctly. Any future change to what a home meters does the same.
  A re-run takes ~45 minutes in two lanes (peak ~5 GB each). The recipe is
  `~/.cache/seat_lane0_20261006b/run_lane{1,2}.sh` followed by
  `file_arms.py <B's settled_wins>`. Run chosen first and read its count before filing C.
- **The cull's count is now a function of the world.** Any future count-matched arm must read
  B's `settled_wins` first. A hard-coded count degrades silently into a duplicate arm.
