**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_29_the_coverage_is_re_measured_against_the_demand_vector`
**Knowledge:** `how-many-synthetic-households` -- the page whose first named limit is that N has not converged

# The demand-vector N against a 480,000 reference is still rising: 15,030 to 25,028, median rung 19,500 (2026-11-27)

*Autonomous worker, drawn on the W2_29 finding
(`SEAT_FINDING_THE_DEMAND_VECTOR_RE_MEASUREMENT_HAS_NO_SHAPE_TO_CONSUME_AND_ITS_INSTRUMENT_IS_UNDER_A_RUNNING_PREREG_2026-10-15`).
This grades `SEAT_PREREG_THE_DEMAND_VECTOR_N_AT_480K_2026-10-14`, which was filed before any 480k seed ran.
The seeds finished between 14 and 15 October. Their grading was the director's named next step
(2026-10-14), and it sat undone for six weeks.*

## Provenance

- The five results are `/var/tmp/dvn480/s{0..4}.json`. `run.py` writes each one atomically (`os.replace`)
  after `smallest_n_chosen` returns, so a file on disk means its seed ran to completion.
- **The `.err` files could not be read.** They are not on disk, and neither is leg A's `DONE_A`
  marker. The longjob logs are empty. So this grade does not claim the stderr was clean. It claims
  only that every seed wrote a complete result.
- The worktree was `/var/tmp/se-dvn480` at `e999ca6f6`. Between `fa7ac5168` (the 240k cell) and
  `e999ca6f6`, `git diff` over `tools/demand_vector_coverage.py`, `tools/reduction_dimension.py`,
  `tools/demand_case_coverage.py`, `sim/` and `simulation/` is empty. The cwd-fallback fix
  (`58e1e89051`) is in both. Only the reference size changed, and with it the generation of the
  population.

## Result

| Seed | First passing size | Rung | Worst KS one rung below | Worst KS on the 6.8k rung | Wall time | Peak RSS |
|---|---|---|---|---|---|---|
| 0 | 19,529 | 19,500 | 0.0573 at 15,030 | 0.0743 | 5.5 h | 1,929 MB |
| 1 | 25,028 | 25,000 | 0.0533 at 19,531 | 0.0834 | 5.5 h | 1,928 MB |
| 2 | 15,030 | 15,000 | 0.0514 at 11,531 | 0.0690 | 2.1 h | 1,929 MB |
| 3 | 19,531 | 19,500 | 0.0541 at 15,032 | 0.0770 | 5.5 h | 1,929 MB |
| 4 | 19,530 | 19,500 | 0.0625 at 15,032 | 0.0572 | 4.8 h | 1,929 MB |

**480k range: 15,030 to 25,028** (rungs 15,000 ×1, 19,500 ×3, 25,000 ×1; median 19,500). That is
3.1% to 5.2% of the reference. Every run reported `peak_window_share_is_constant: false`.

The sequence of medians, all at tolerance 0.05 over five design seeds:

| Reference | Range | Median rung |
|---|---|---|
| 20,000 | 5,215 to 6,815 | 6,800 |
| 120,000 | 8,823 to 11,522 | 11,500 |
| 240,000 | 8,828 to 15,025 | 11,500 |
| 480,000 | 15,030 to 25,028 | 19,500 |

## Against the predictions

1. **Median rung 11,500 (~50%): REFUTED.** The median rung is 19,500. The weaker form, "at or below
   11,500 (~60%)", is also **REFUTED**: no seed sits there. The prereg gave one alternative to
   "converged or noise": the 20k-to-120k trend (exponent 0.29), which "predicts about 17,000 to
   18,000, which is the 19,500 rung". That is where the median landed.
2. **At least one seed at 15,000 or above (~55%): HELD.** All five are there.
3. **No seed runs off the ladder (~95%): HELD, only just.** Seed 1 passed on the ladder's last rung,
   25,028. A sixth draw has a real chance of running past the top.
4. **Diagnostic, the mean worst-KS on the 6.8k rung within ±0.006 of 240k's 0.0639: REFUTED.** It is
   0.0722 (+0.0083). The 120k mean, read here for the first time as the prereg said it would be,
   is 0.0599. That is over four seeds: seeds 1 to 4 are in `/var/tmp/dvn/`, and seed 0's file is
   not on disk. So at a fixed sample size the fit worsens steadily as the reference grows:
   0.0599, then 0.0639, then 0.0722.

I leaned toward convergence, and the 240k grade had leaned the same way. Both were wrong. The 240k
cell's unmoved median, which was read as the rise flattening, now reads as a draw that sat one rung
low.

## How it reads

The reading rule's **still rising** branch fires on both legs. The median rung is 19,500, which is
at least 15,000, and no seed at all sits at or below 11,500. The rule's further clause also fires:
the median reached 19,500, so the page's "slowed" sentence is withdrawn.
`how-many-synthetic-households` now gives the 480k range and says the rise continues past 240k.

**The power law the 240k grade set aside fits the whole run.** Through the medians, from 20k to
480k the exponent is ln(19,500/6,800) / ln 24 ≈ 0.33. From 120k to 480k it is ln(19,500/11,500) /
ln 4 ≈ 0.38. Both are inside one rung of the 0.29 that 20k to 120k gave. The converging account
(in-sample help fading as k/P) predicted that almost all of the rise would be over by 120k. That
account is refuted as the main effect.

**Why the requirement keeps growing, I cannot yet say.** The evidence allows at least three causes,
and this cell cannot separate them:

- **(i)** A larger generated population carries more distinct joint combinations in its tails,
  which a fixed KS bar over 64 random projections must then cover.
- **(ii)** Each size uses a fresh generation, so a population's own draw is confounded with its
  size. This is one population per size.
- **(iii)** Something in how the choosing scales with P.

The one-variable test is a 240k reference SUBSAMPLED from this 480k population, with the five
seeds unchanged. It holds the generation fixed and varies only P. Under (ii) alone, its median
falls back toward 11,500. Under (i) or (iii), it does not. It is not launched here, because the
director's 14 October ruling was "no further rungs". It goes to him as a proposal.

**What this means for the figure.** "How many synthetic households represent Britain" has no
reference-independent answer on this instrument yet. If an exponent near 0.33 held all the way to
28 million homes, the figure would be several times 19,500. Nothing establishes that it holds, so
this is only the scale of the question, not a figure. The page keeps "not shown to have converged"
and now says plainly that the rise continues.

## What this does to W2_29

The instrument is no longer under a running prereg, which was half of the 15 October finding's
block. The other half stands unchanged. `tools/demand_vector_coverage.py` still has no route from
a generated household to a fabric trace (a), and no written definition of a distance along a shape
(b). `REDUCES_OVER.blind_to` still names both shape components. W2_29 stays at level 1, and its
block reason now names (a) and (b).
