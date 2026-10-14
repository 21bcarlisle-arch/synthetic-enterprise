**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** `how-many-synthetic-households` -- the page whose first named limit is that N has not converged

# Pre-registration: does the demand-vector N converge past a 120,000 reference? (2026-10-14)

*Delivery seat, LANE 0 draw `demand-vector-n-convergence-past-120k`. Written BEFORE any 240k seed
ran, at base `b585d3733`, with `tools/demand_vector_coverage.py` identical to origin. The only
thing run beforehand was a probe that times the population build and counts strata at 20k, 120k
and 240k. It computes no N.*

## The question

The page says N "grows with the reference". Against 20,000 the five-draw range is 5,215 to 6,815.
Against 120,000 it is 8,823 to 11,522 (`b585d3733`). Is that growth still going on past 120,000,
or does it flatten?

**What N is here.** N is the first rung of the ladder at which a sample that has been chosen and
then weighted passes. To pass it must reproduce the generated population within a fixed KS
tolerance of 0.05. That holds on every axis, on 64 joint directions, and inside every stratum on
its own. The tolerance does NOT shrink as the reference grows. So if the generated population is a
draw from one fixed distribution, N should converge. Growth past 120k would mean that something in
the instrument grows with P: rarer strata, finer tails, or how the chosen points spread across the
clusters.

## What is measured

`smallest_n_chosen(generated_population(points=240000, seed=0), AXES, seed=s,
ns=CHOSEN_NS + (19500, 25000))` at tolerance 0.05, for design seeds s = 0..4. The two extra rungs
come after 15,000 and change no answer at or below it. They are only there so that a result off
the top of the ladder can be told apart from a pass. As in the 120k cell, only the choosing varies:
the population is seed 0, the directions are seed 12345 and the weight fit is seed 999. The
240,000 population is a fresh generation, not a superset of the 120,000 one.

## Predictions

The power law through the two medians (6,800 at 20k and 11,500 at 120k) has an exponent of about
0.29. That gives about 14,200 at 240k, which passes on the 15,000 rung.

1. **Median rung: 15,000.** (~50%) Every seed lands in {11,500, 15,000, 19,500}. (~80%)
2. **At least one seed passes at 11,500.** (~55%) The rung is set by where one draw crosses the
   line, and at 120k three seeds out of five landed on 11,500.
3. **No seed runs off the ladder** (that is, no seed fails to pass at 25,000). (~90%)

## How it is read

- **Still growing:** the median rung is above 11,500 and fewer than two seeds land on 11,500. The
  page keeps "grows with the reference" and adds the 240k range.
- **Flattening:** the median rung is 11,500, or the 240k range overlaps the 120k range in at least
  two seeds. The page says the growth slows between 120k and 240k and that one doubling cannot
  establish convergence.
- **Off the ladder:** if any seed is still failing at 25,000, that seed is reported as "> 25,000"
  and is never read as a figure.

## Cost, priced before launch

At 120k each seed peaked at about 1.1 GB and took 63 to 69 minutes with four running at once. The
probe's 240k RSS sets how many run at a time. The rule is that the running seeds use no more than
about 70% of `resource_headroom.sample()["available_mb"]` taken at launch.

## Launch log (added after filing; nothing above it changed)

- **10:19, first launch: died empty.** The prior invocation ran the five seeds through a plain
  `xargs` inside its own tick. That turn ended and the seeds went with it. All five output files
  are zero bytes and there is no done marker (`/var/tmp/dvn240/`). No seed result exists, so nothing
  has been seen that could bias the reading rule.
- **12:25, relaunched as two systemd units**, `longjob-dvn240-seeds-a` (seeds 0, 1, 2) and
  `longjob-dvn240-seeds-b` (seeds 3, 4). They run one seed after another, in the locked worktree
  `/var/tmp/se-dvn240` at `fa7ac5168`. `tools/demand_vector_coverage.py` there is byte-identical
  to `b585d3733`. Admission held 20.8 GB already resident against a 23.0 GB ceiling (the termcost
  arms declared 11.2 GB), so only one seed at 1.5 GB fitted. Unit B waits for
  `regrade5-match-where-published-61109` to exit. The design is unchanged and only the
  parallelism differs. The pre-launch price assumed four seeds at once, so each seed's wall time
  is not comparable with the 120k cell's.
- **Results land in** `/var/tmp/dvn240/r2/s{0..4}.json`, written atomically, with `DONE_A` and
  `DONE_B` as markers. If a seed is missing when its unit has ended, read its `.err` and do not
  re-run it blind.
