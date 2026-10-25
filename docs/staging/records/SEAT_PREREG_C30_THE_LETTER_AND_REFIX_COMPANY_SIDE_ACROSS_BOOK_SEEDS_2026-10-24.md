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

## Status (2026-10-25 ~06:30, all nine arms re-run at one commit, 9bb30c4de5)

**Why the r2 artefacts are not graded:** B_61102 and C_61102 r2 died on an undrawn occupant id. The
cause was a home move dated on a term boundary, which dropped the vacated meter. 9bb30c4de5 fixes
it, and its message says every run with home moves changes. Grading 61101 and 61103 at 0481ad381+patch
against 61102 at 9bb30c4de5 would count a world change as an advice effect, so all nine arms run at
9bb30c4de5 (worktree `/var/tmp/c30-61102-fix-wt`, locked) and write to
`/var/tmp/c30-seeds-out/at-9bb30c4de5/`.

**The commit's prediction, tested on A_61102 (no letter, so the policy is the default):** A_61102
should differ between the two commits, because the fix admits meters the old run dropped.
Prediction recorded at 9bb30c4de5, before this comparison: a nonzero difference. **Result:
it held.**

| A_61102 | 0481ad381+patch | 9bb30c4de5 | Δ |
|---|---|---|---|
| total_net | £545,810 | £560,251 | **+£14,441** |
| svt_departures | 273 (all `svt_inertia`) | 273 (all `svt_inertia`) | 0 |
| customers with an SVT decision | 636 | 643 | +7 |
| SVT decisions | 8,635 | 8,747 | +112 |
| electricity accounts at start (log) | 559 | 559 | 0 |

The fix changes the arm with no letter by **£14,441**. That is larger than any between-arm
difference this prereg grades: £8,252 for the letter alone on the default book, and −£389 for ΔC.
So a mixed-commit grade would have been mostly world change. The departure count is unchanged,
because the admitted households are incoming occupants on the book, not new SVT exits.
"Accounts" here means the starting electricity roster, which the fix cannot touch. The +7 are most
likely occupants admitted later. That is inferred, not traced.

**Running:** `longjob-c30-s6110{1,3}-{a,b,c}-at9bb`, the 05:45 argv unchanged. They are queued
through `launch_long_job` and admitted as memory allows (7 GB each), about 50 minutes per arm. The
61102 triple at 9bb30c4de5 already exists. **The grade is queued on the files, not on a time:** unit
`longjob-c30-grade-at9bb` runs `at-9bb30c4de5/grade_when_done.sh`. It waits on every `arm2.py`
process, refuses if any of the six artefacts is missing, then writes `grade_seeds.py 61101 61102
61103` to `at-9bb30c4de5/grade.txt`. **Reverse:** `systemctl --user stop
'longjob-c30-*-at9bb*' longjob-c30-grade-at9bb longjob-c30-grade-at9bb-queued`.

The predictions above are still ungraded. They were written before any arm at this commit computed.

## Result (2026-10-25, three seeds at 9bb30c4de5; predictions above unedited)

`at-9bb30c4de5/grade.txt` was written at 08:15Z by `longjob-c30-grade-at9bb`, after all six new arms
finished (the 61102 triple was already there). The household side H was computed with the
default-book pair's own rule (`c30-arms-out/grade.py`: Σ over withdrawn default segments of
(default rate − fix rate) × EAC × days, ex VAT, energy only). Each re-fixed household was then split
by whether it leaves in C and stays in B.

| seed | B − A (ΔC) | C − A (letter) | B − C (re-fix) | sends B / C | re-fixes | `price_position` exits B / C | cust-yrs C−A | cust-yrs B−C | £/yr C−A | £/yr B−C |
|---|---|---|---|---|---|---|---|---|---|---|
| 61101 | **−£5,851** | −£7,211 | +£1,360 | 807 / 793 | 21 | 7 / 7 | −30.66 | +28.76 | 235 | 47 |
| 61102 | **−£9,919** | −£6,345 | −£3,574 | 789 / 782 | 12 | 7 / 7 | −20.87 | 0.00 | 304 | — |
| 61103 | **−£4,865** | −£3,975 | −£890 | 758 / 747 | 16 | 8 / 8 | −22.03 | +4.25 | 180 | −209 |
| default (0481ad381) | −£389 | −£8,252 | +£7,864 | 803 / 786 | 20 | 9 / 9 | −33.7 | +37.8 | 245 | 208 |

Movers by kind (founder `SYN-` / win `PROS-`,`OCC-`): C−A 3/4, 4/3, 5/3; B−C 3/2, 0/0, 0/1.

**The default book is one commit behind the seeds.** It ran at 0481ad381, and 9bb30c4de5 changes
every run with a home move on a term boundary (+£14,441 on A_61102 alone). Its within-book ΔC is
internally consistent, but it is not the same code as the three seeds. So predictions 4 and 5 are
graded on the three seeds at one commit, and the four-book figure is given beside them, labelled.

1. **C − A < 0 on every seed: held.** −£7,211, −£6,345, −£3,975. The 7–8 `price_position` exits
   per seed fall inside 4–15. The letter alone costs the company on all four books.
2. **B − C > 0 on every seed, keeping 2–8 households: REFUTED.** It holds on 61101 only (+£1,360).
   There the re-fix keeps 4 re-fixed households (OCC-88f15d013e04, PROS-2016-0203, SYN-2016-260 and
   -517), and SYN-2016-283 drifts on the path. On 61102 it keeps **nobody**, and B − C is −£3,574.
   On 61103 it keeps one (PROS-2016-0153, 4.25 years), and B − C is −£890.
3. **£200–£350 per customer-year in both transfers: REFUTED.** The letter's transfer is close:
   £235, £304 and £180. 61103 misses low, and the default book gave £245 on the script's rule. The
   re-fix's transfer is not a per-customer quantity on these seeds: £47, undefined (0 years) and
   −£209. The default book's "two transfers at one rate" was a property of that cast.
4. **The sign of ΔC differs across books, with |ΔC| < £5,000 each: REFUTED.** It is negative on all
   three seeds, and on the default book too, at its own commit. |ΔC| is above £5,000 on 61101 and
   61102.
5. **Mean ΔC within ±£3,000 of zero: REFUTED.** The three-seed mean is −£6,878 (range −£9,919 to
   −£4,865), and the four-book mean is −£5,256.

**Why I was wrong.** I generalised from the default book, where the re-fix kept 5 leavers and almost
exactly cancelled the letter's 9 exits. Across seeds, the letter's cost is steady: £4–7k, through
7–8 named exits, every time. What the re-fix keeps depends on the cast: 4, 0 and 1 households. The
default book's 5 was the high end, so ΔC ≈ 0 there was luck of composition, not balance.

**What is not attributed (F11).** B − C was meant to be the re-fix margin given up (≈ H) plus the
retention it buys. Pricing the retained years at the same seed's C − A rate gives the residual
nothing explains:

| seed | retention at C−A £/yr | − H | expected B − C | observed | **unattributed** |
|---|---|---|---|---|---|
| 61101 | +£6,759 | −£1,320 | +£5,439 | +£1,360 | **−£4,079** |
| 61102 | £0 | −£896 | −£896 | −£3,574 | **−£2,678** |
| 61103 | +£765 | −£1,442 | −£677 | −£890 | **−£213** |

On 61102 no customer moves between B and C, yet B − C is four times H. So the re-fix carries a
company cost beyond the margin it gives away: hedging, pricing or another path knock-on. The arm C
record read the default book's 3% agreement as "knock-ons small beside the customer count". **That
is refuted on two of three seeds.** It is unattributed, not explained, and it is the next read
(below).

## The household side (M2)

| seed | H, all re-fixes | to stayers (default is the right counterfactual) | to retained households (rival's tariff is the counterfactual, so H overstates) | H + ΔC |
|---|---|---|---|---|
| 61101 | £1,320 (21) | £1,134 (17) | £186 (4) | −£4,531 |
| 61102 | £896 (12) | £896 (12) | £0 (0) | −£9,023 |
| 61103 | £1,442 (16) | £1,410 (15) | £32 (1) | −£3,422 |

No re-fix leaves a household worse off (0 negative rows on every seed). The re-fix refuses 6–9
offers a seed because the fix would sit above the default it would replace. That refusal works as
written. **GAP, unchanged:** the saving of the 7–8 letter leavers at a rival is not recorded by the
world. Their side is unmeasured, not zero, so H + ΔC is not a total.

## Reading on M2

- **The company side's sign is established at the strength three seeds earn.** The letter plus
  re-fix costs the company on 3 of 3 seeds at one commit, by £4.9k–£9.9k (mean −£6,878), and on
  the default book at its own commit. Three same-sign draws would happen 1 time in 8 under a coin
  flip, so this is a direction, not a tight bound. **Erring against the thesis (F11), the reading
  is: as built, the letter plus re-fix transfers value away from the company, and it is not shown
  to create any.**
- **The households who stay gain £0.9k–£1.4k a book** from the re-fix, and none of them loses. That
  is real, but it is a transfer from the company (M2: "Transfer is not creation"). It is smaller
  than what the company loses, except where the leavers' unmeasured gain at rivals would close the
  gap.
- **The arm C record's advice, "the re-fix is what makes the letter defensible", does not survive
  the seeds.** It defended the letter on 61101 alone, partly, and not on 61102 or 61103.

## Next (one variable)

The −£2.7k on 61102, with no customer moving between B and C, is the cleanest place to find the
re-fix's unattributed cost. The next read is a per-month `total_net` difference B − C on 61102
from the two artefacts already on disk, if they carry it, or from one instrumented re-run if they
do not. That shows whether the cost sits in the fix windows (hedge or pricing) or after them. The
default book at 9bb30c4de5 (three arms, about 50 minutes each) would put the fourth book on the
seeds' commit. That is lower value, because 3 of 3 already agree in sign.
