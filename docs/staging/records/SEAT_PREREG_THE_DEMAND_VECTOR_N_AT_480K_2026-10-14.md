**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** `how-many-synthetic-households` -- the page whose first named limit is that N has not converged

# Pre-registration: is the demand-vector N still rising at 480,000, or is the 240k spread draw noise? (2026-10-14)

*Delivery seat, LANE 0 draw `demand-vector-n-convergence-after-240k`. Filed BEFORE any 480k seed
runs, at base `e999ca6f6`. `tools/demand_vector_coverage.py` there is byte-identical to `b585d3733`,
which produced the 20k, 120k and 240k cells. Already seen before filing: the five 240k curves
(`SEAT_RESULT_THE_DEMAND_VECTOR_N_PAST_120K_2026-10-14`) and the one 120k value that result quotes
(seed 4 at 0.0500 on the 6.8k rung). The other 120k and 20k curves were not opened.*

## The question, and why it is a 480k cell and not five more 240k seeds

After 240k the page cannot tell a slow residual rise from draw noise. The 240k median rung equals
the 120k one (11,500), but its spread is one rung wider (8,800 to 15,000 against 8,800 to 11,500).

**The rung is the binding resolution, not the seed count.** The ladder steps by about ×1.3, so a
cell only shows a rise once the crossing point moves by about one rung. Over one doubling that
needs an exponent of ln 1.3 / ln 2 ≈ 0.38. The 240k cell rules out only that much. Five more 240k
seeds would narrow the 240k distribution and leave the lever arm at ×2. A rise with exponent 0.1
moves the crossing by 7% over that doubling, which no plausible number of 240k seeds can resolve on
this ladder. A 480k cell gives a ×4 lever against 120k. A one-rung move then needs an exponent of
only ln 1.3 / ln 4 ≈ 0.19. For about the same compute, that halves the smallest detectable rise.

**What it can and cannot settle.** A rise with an exponent of about 0.2 or more should show at
480k. A slower one can still hide inside one rung. A null result therefore bounds the rise and does
not show convergence. The page will say that, with the bound.

**No mechanism forces a rise.** The probe for the 120k prereg counted strata: there are always four
(fuel × payment) at every size. The tolerance is fixed at 0.05. So "more strata as P grows" is
ruled out. A converging effect is expected: at small P the chosen-and-weighted sample is fitted
in-sample to a population only 3 to 5 times its size. That makes it easier to pass, and the help
fades as roughly k/P. On its own, that effect predicts N rising toward a ceiling, with almost all
of the rise over by 120k (k/P is already 7% to 10% there).

## What is measured

`PYTHONPATH=. python3 /var/tmp/dvn480/run.py 480000 s` for design seeds s = 0..4. This is the
same script as `/var/tmp/dvn240/run.py`, so it calls `smallest_n_chosen(generated_population(points=480000, seed=0), AXES, seed=s,
ns=CHOSEN_NS + (19500, 25000))` at tolerance 0.05. Only the choosing varies. The population is seed
0, the directions are seed 12345 and the weight fit is seed 999, all as before. The 480,000
population is a fresh generation, not a superset of the 240k one.

## Predictions

The reference distribution is the 10 draws at 120k and 240k pooled: rungs 8,800 ×4, 11,500 ×5,
15,000 ×1.

1. **Median rung at 480k: 11,500.** (~50%) At or below 11,500 (~60%). Converged-or-noise predicts
   11,500. A rise with exponent 0.1 puts the crossing at about ×1.15 of 120k's, which mostly still
   lands on 11,500 and sometimes on 15,000. The 20k→120k trend (exponent 0.29) predicts about
   17,000 to 18,000, which is the 19,500 rung.
2. **At least one seed at 15,000 or above.** (~55%) Under pure noise on the pooled distribution,
   P = 1 − 0.9⁵ ≈ 0.41. A slow rise pushes it up.
3. **No seed runs off the ladder** (none still failing at 25,000). (~95%)
4. *Diagnostic, not a branch:* the mean worst-KS on the 6.8k rung (k ≈ 6,830) over the five
   seeds. At 240k it is 0.0639 (0.0614, 0.0600, 0.0729, 0.0616, 0.0636), with seed SD about 0.005.
   Converged-or-noise predicts the 480k mean lands within ±0.006 of it. That diagnostic is reported
   together with the 120k mean, which will be read for the first time at grading.

## How it is read

- **No rise detected over ×4:** the median rung is ≤ 11,500. The page says that the middle draw did
  not move between 120k and 480k, and that any rise left is slower than about exponent 0.2. It
  keeps "not shown to have converged".
- **Still rising:** the median rung is ≥ 15,000 AND at most one seed sits at ≤ 11,500. The page
  says the rise continues past 240k, gives the 480k range, and withdraws the "slowed" sentence if
  the median reaches 19,500.
- **Between:** the median is ≥ 15,000 but exactly two seeds sit at ≤ 11,500. That is the only
  split the two branches above leave open. It is reported as undecided, and nothing more is
  launched without a new prereg.
- **Off the ladder:** a seed still failing at 25,000 is reported as "> 25,000" and is never read as
  a figure. It counts as above 15,000 for the median.

**Second leg's trigger, written now.** Unit A runs seeds 0, 1 and 2. Unit B runs seeds 3 and 4. If
A's three seeds all land at ≤ 11,500, or all at ≥ 15,000, the median of five is fixed before B
finishes. B still runs and is reported, but it cannot flip the branch. If A splits, the branch
waits for B.

## Cost, priced before launch

`resource_headroom.sample()` at 15:19: 12,365 MB available out of 24,032 MB. Six other long jobs
are active, including the stayers control. At 240k each seed peaked at 1,163 to 1,238 MB and took
32 to 53 minutes alone. Between 120k and 240k peak RSS grew by only about 6%, and time roughly
doubled (20 minutes alone at 120k). The price at 480k is 65 to 110 minutes per seed, longer for
any seed that climbs to the 19,500 rung, with a declared peak of 2,000 MB. Two units run side by
side at about 4 GB, within the 70%-of-available rule. Unit A finishes in roughly 3.5 to 5.5 hours.
The admission check in `launch_long_job` is what decides whether B waits.

## Where it runs

Units `longjob-dvn480-seeds-a` and `-b`, in a locked worktree `/var/tmp/se-dvn480` at
`e999ca6f6`. Results go to `/var/tmp/dvn480/s{0..4}.json` and are written atomically. Each `.err` is
read before its seed is graded.

## Falsifiers

- `PYTHONPATH=. python3 /var/tmp/dvn480/run.py 480000 <s>` from a tree whose
  `tools/demand_vector_coverage.py` equals `b585d3733`'s reproduces each seed's `n` exactly. The
  choosing is deterministic given its seeds.

## Launch log (added after filing; nothing above it changed)

- **16:2x, both legs launched** as `longjob-dvn480-seeds-a` (seeds 0, 1, 2) and `-b` (seeds 3, 4)
  in `/var/tmp/se-dvn480` at `e999ca6f6`. The module there is byte-identical to `b585d3733`, and
  both cgroups are VERIFIED. The two launches were admitted against one snapshot, and neither
  counted the other (`SEAT_FINDING_TWO_LONG_JOBS_LAUNCHED_TOGETHER_ARE_BOTH_ADMITTED_AGAINST_ONE_SNAPSHOT_2026-10-14`).
  Both were kept on a measurement, not the door's sum. After they started,
  `available_mb` was 11,823 with PSI at 0.13, and each seed held about 1.04 GB at 2.5 minutes in.
  That is inside this prereg's 70% rule. The 480k population build fitted in the same memory as at
  240k.
