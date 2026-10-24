# Pre-registration: C30, the letter plus re-fix on the company side, across book seeds

*Delivery seat (worker), 2026-10-24. Claim `c30-letter-refix-company-side-across-book-seeds`.
Written before any arm below was launched. Follows the Result section of
`SEAT_PREREG_C30_ARM_C_WHOSE_GAIN_OFFSETS_THE_REFIX_MARGIN_2026-10-24.md`.*

## Question

On the default book, B − A = −£389 to the company. That figure is two transfers that nearly cancel:
the letter's 9 exits (C − A = −£8,252) and the re-fix keeping 5 leavers (B − C = +£7,864), each
about £270 per customer-year. So the sign of ΔC rests on 14 named customers on one path. **Across
independent books, is ΔC = B − A bounded away from zero in either direction, or does its sign
depend on the cast?**

## Arms

Three arms per seed. All of them run at **0481ad381**, the commit the default-book triple ran on,
so that book is the fourth seed and not a different code base. The worktree is detached at
`/var/tmp/c30-seeds-wt` and the script is `/var/tmp/c30-seeds-out/arm2.py`, unchanged.

- **A:** no letter, re-fix on (`instrument none`, `on`).
- **B:** `cmoc_letter` once per stint, re-fix on (`cmoc_letter`, `on`).
- **C:** `cmoc_letter` once per stint, re-fix off (`cmoc_letter`, `off`).

The seeds are **61101, 61102 and 61103**, set through `SE_POPULATION_SEED`. All three are in the
director's 2026-10-10 EP17 record (`docs/design/curriculum/varied_population_draw_activation.json`).
The book stays the production 400-founder shape and the full window. Each job goes through
`background.launch_long_job` at its declared peak, so the box decides how many run at once.

## What is measured

Per seed: `total_net` for B − A, C − A and B − C; sends; re-fixes; SVT departures by cause; and the
per-customer exit table (`exits.py`) for A↔C and C↔B, giving customer-years lost and kept. The
director's condition 1 asks for founders and campaign wins separately, so the named movers are
split by id prefix: `SYN-` founders, against `PROS-`/`OCC-` wins.

## Predictions

1. **C − A < 0 on every seed.** The letter alone costs the company, through 4–15 `price_position`
   exits per seed.
2. **B − C > 0 on every seed.** The re-fix keeps 2–8 households who leave in C.
3. **Value per customer-year is £200–£350 on every seed, in both transfers.** The default book gave
   £268 and £275.
4. **The sign of ΔC = B − A is NOT the same on all four books,** and |ΔC| < £5,000 on each. My
   reason: on the default book it is the difference of two transfers of similar size, and the
   customer counts move by several per seed. Refutation: all four books have the same sign. If all
   four are negative, the letter-plus-re-fix is shown to cost the company. If all four are positive,
   that is still market share taken from rivals, not value created (M2).
5. **The mean ΔC over the four books lies within ±£3,000 of zero.**

## What done means

The triple has run on all three seeds at one commit. Each prediction is graded beside itself, and
every difference is attributed to named customers or explicitly left unattributed. The reading on
M2 states whether the company side's sign is established. If it is not, it gives the bound the
four books earn.

## Status (2026-10-24, before any arm finished)

The nine arms were queued at about 05:45 as `longjob-c30-s6110{1,2,3}-{a,b,c}`, through
`launch_long_job` at a 7,000 MB peak. The box admits about two at a time, so the full set needs
about 4–5 hours. Each writes `/var/tmp/c30-seeds-out/{A,B,C}_<seed>.json`. A dead arm is relaunched
with the argv stored for it in `docs/observability/.launch_records.json`.

**Grading:** `python3 -I /var/tmp/c30-seeds-out/grade_seeds.py default 61101 61102 61103`. That
prints B − A, C − A and B − C, the customer-years moved, £ per customer-year and the mover counts
(founders and wins) for every book. `default` reads the arm C triple in `/var/tmp/c30-arms-out/`.

**One counting rule across all four books.** `grade_seeds.py` takes each customer's first
electricity exit and counts a customer who never leaves up to 2026-01-01. On the default book that
gives 33.7 customer-years (C − A) and 37.8 (B − C), or £245 and £208 each. The arm C record
reported 30.85 and 34.91, or £268 and £275, by a rule it did not state. So prediction 3 is graded
on the script's rule for all four books, the default book included.

## Status (2026-10-24 ~07:30, no arm has computed)

**None of the nine arms ran.** They sat QUEUED behind `head-green-census.service` (12 GB) and the
"landings come before experiments" holds. At 07:06 every one of them was refused: `/var/tmp/c30-seeds-wt`
had been deleted while they waited, and the launcher declines a workdir that is gone. No artefact
exists, so no prediction above has been tested.

**Relaunched behind section 14, on purpose.** The worktree is recreated at 0481ad381 and is now
`git worktree lock`ed with a reason. The seat's newest order (continuation
`the-queued-runs-compute-and-the-thesis-run-goes-first`) puts the section 14 clean-book re-take ahead
of these arms, and that driver may not share the box with jobs writing `c30-seeds-out`. Its
`c30-seeds-out` wait passed at 06:06 only because nothing was running, not because these arms had
finished. If the arms started now, they would overlap it. So `/var/tmp/c30-seeds-out/chain.sh`
(unit `longjob-c30-seeds-chain`, queued through `launch_long_job`) waits on the driver's pid 1615133
through `tools.wait_for`, for up to six 6-hour deadlines. It then queues the nine arms with the
05:45 argv unchanged and skips any arm whose artefact already exists. **Cost:** the result arrives
after section 14, which needs about 11 hours including E6, instead of in about 5.
**Reverse:** `systemctl --user stop longjob-c30-seeds-chain longjob-c30-seeds-chain-queued`, then
run `chain.sh` with a pid that has already exited.

Grading is unchanged. When `A/B/C_6110{1,2,3}.json` all exist, run `grade_seeds.py` as above.

## Status (2026-10-24 ~07:40, the arms ran and every one died at startup)

**The chain did not hold.** `tools.wait_for --pid 1615133` returned NEVER_STARTED at 06:22Z: that
pid was already gone, and the section 14 driver had not yet been relaunched (it started at 06:26Z
as pid 2413933). So the nine arms launched at 06:22Z, ahead of section 14, which is the order the
seat had ruled out.

**All nine died before computing anything,** with the same error on every arm:
`DwellingNotDrawn: 'SYN-2016-011' is supplied but the world drew no dwelling for it` (seeds 61101
and 61102), and the same for `'SYN-2016-036'` (61103). No artefact was written, so no prediction is
tested yet. The logs are kept as `/var/tmp/c30-seeds-out/{A,B,C}_<seed>.0622-dwelling-not-drawn.log`.

**Cause: a world defect, not this experiment.** `run_phase2b` draws its book at
`SE_POPULATION_SEED`, but it calls `live_dwellings()`, `live_drawn_households()` and
`campaign_quotes_paid_for()` with no argument. `_live_homes` and `campaign_quotes_paid_for` then
fell back to `_DEFAULT_BASE_SEED`, so the dwelling register held the default book's founders. This
is the failure `run_base_seed()` was written to prevent (S1, 2026-08-27). The default book cannot
hit it, because it uses the same seed on both paths. Under a seed, the campaign's acquisition spend
would also have been the default book's quotes, booked against the seeded book. That would have
gone straight into the `total_net` this prereg differences, **if** the dwelling guard had not
stopped the run first.

**Fix, landed separately:** both fallbacks now read `run_base_seed()`.
`tests/simulation/test_the_population_seed_switch.py::test_a_seeded_books_registers_are_drawn_at_its_seed`
is red on the old code (DwellingNotDrawn) and green on the new. A smoke run on the patched
measurement worktree builds every property: 547 for seed 61101 (a book of 1,007 accounts) and 546
for seed 61103 (998 accounts).

**The arms are now one commit off 0481ad381, and that is stated rather than hidden.**
`/var/tmp/c30-seeds-wt` is 0481ad381 plus that `live_population.py` patch and nothing else. For the
default book (seed 20260724) the patch is a no-op, because `run_base_seed()` returns the default
when no seed is set. So the default triple in `/var/tmp/c30-arms-out/` is still the fourth book at
the same effective code.

**Relaunched behind section 14, through a waiter that this time holds a live pid.**
`/var/tmp/c30-seeds-relaunch/chain2.sh` runs as unit `longjob-c30-seeds-chain2` and waits on pid
2413933, `drive.sh`. The driver waits on any process whose command line contains `c30-seeds-out`,
so the chain is kept outside that directory and its argv never names it. Otherwise the two would
deadlock. Before queuing anything, the chain also refuses if the worktree lacks the fix. The arms
are `longjob-c30-s6110{1,2,3}-{a,b,c}-r2`, with the 05:45 argv unchanged. **Expected:** section 14
runs eight arms one at a time, about 75 minutes each, so the C30 artefacts arrive roughly 10–14
hours from now. **Reverse:** `systemctl --user stop longjob-c30-seeds-chain2
longjob-c30-seeds-chain2-queued`.

The predictions above are unchanged and still ungraded. They were written before any arm computed,
and none has computed yet.
