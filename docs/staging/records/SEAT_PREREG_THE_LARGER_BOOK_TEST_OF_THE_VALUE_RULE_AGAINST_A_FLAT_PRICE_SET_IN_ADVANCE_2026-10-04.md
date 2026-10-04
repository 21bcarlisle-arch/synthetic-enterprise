# The larger-book test of the value rule against a flat price set in advance

**Pre-registered 2026-10-04 by the delivery seat, before any run is launched.** Item
`the-larger-book-test-is-designed-before-the-refit-lands`. Nothing below has been run on the
refitted world. Every SNR here is a projection from the four runs that already exist.

## Why

`SEAT_PREREG_THE_VALUE_RULE_AGAINST_A_FLAT_PRICE_SET_IN_ADVANCE_2026-10-04.md` (graded with
191448824) is the first flat baseline a supplier could really have run. Against the harder
ex-ante chooser, capped beats it on one path of four and ties on three. That record ends with "too
few decisions to tell". This record prices the fix. It asks what a decisive run costs, which lever
buys it, and who is allowed to pull that lever.

## The power table

Script: `/var/tmp/se-probe-out/larger_book_power.py`. Output: `larger_book_power.txt`. It is run
on the four term-probe rows with origin's `tools/decision_probe` (`ex_ante_levels`, `with_level`,
`expected_term_margin_gbp`, `score`). On each path the "harder chooser" is the one capped beats by
less. Scored decisions are 2018-2025, as before.

| path | harder chooser | n | accounts | capped − chooser, GBP | SD | SNR | edge per decision | n for SNR 2 |
|---|---|---|---|---|---|---|---|---|
| default | E-belief | 57 | 35 | +528 | 226 | 2.34 | 9.27 | 42 |
| 61001 | E-belief | 57 | 36 | +69 | 357 | 0.19 | 1.21 | 6,059 |
| 61002 | E-true | 56 | 33 | +99 | 107 | 0.93 | 1.78 | 261 |
| 61003 | E-belief | 56 | 37 | +29 | 304 | 0.09 | 0.51 | 25,391 |

SNR at N scored decisions, holding each path's own edge and SD per decision. This assumes the
extra decisions come from **independent households**:

| path | 56 | 112 | 224 | 448 | 896 | 1,792 |
|---|---|---|---|---|---|---|
| default | 2.32 | 3.28 | 4.64 | 6.56 | 9.28 | 13.12 |
| 61001 | 0.19 | 0.27 | 0.38 | 0.53 | 0.75 | 1.07 |
| 61002 | 0.93 | 1.32 | 1.86 | 2.63 | 3.72 | 5.26 |
| 61003 | 0.09 | 0.13 | 0.18 | 0.25 | 0.36 | 0.51 |

**The four paths disagree by a factor of 18 in edge per decision, and they are ONE book.** They
share 27 of 41 accounts. Only the renewal dice differ. So the edge is not a property of the rule
alone. It depends on which households happen to renew in which year. The question has to be asked
of the pooled edge, over book noise as well as dice noise:

- **Pooled over the four paths:** mean total +181 GBP over ~56 decisions, **3.2 GBP a decision**.
  The SD comes from resampling accounts jointly across all four paths: 212. **SNR 0.85.**
- **Pooling dice paths barely helps.** The per-account edge correlates across paths at 0.12-0.93,
  mean 0.43. From the joint SD, ρ ≈ 0.52 (RMS single-path SD 265). If the four paths were
  independent, their mean would have SD ~124 and SNR ~1.5. They are not, and it has SD 212.
- **What one book of ~41 households can ever say:** with infinitely many dice paths, the SD falls
  only to 265 × √0.52 ≈ 191. **The SNR ceiling on this book is ≈ 0.95.** No number of roll seeds
  clears 2.

**A caveat on the projection, stated now.** If a larger book lets the flat chooser learn faster in
its first book year, the edge shrinks toward its 2019-2025 value. That value is
+392 / +4 / +159 / −72 against E-belief, a pooled 121 over ~49 decisions, or **2.5 GBP a decision**.
Every projection below then reads about 25% low in SNR.

## The levers, and what each costs on this guest

These costs come from the tools' own arguments and past runs. Guest memory is
`resource_headroom.sample()`: 24,032 MB total and 11,364 MB available when this was written. A probe
at today's book takes **33-36 min and peaks at 5.0-5.1 GB RSS** (`term_*.time`, four runs).

| lever | how it is set | decisions it adds | projected SNR on the pooled edge | cost | who may pull it |
|---|---|---|---|---|---|
| **More roll seeds** | `decision_probe --roll-seed S`, a real argument | none: it is the same ~41 households | ≤ 0.95 at any K (ceiling above) | 36 min, 5.1 GB each | the seat |
| **Longer window** | `--world neso_central --end-year 2029`. `main()` refuses `--world` without `--end-year` | 103 against 82 decisions in total, measured (`probe_world2029.json`), so ~+21 scored, on the same accounts | ×1.17 at most, so ~1.0, on a SYNTHETIC forward world | 53 min, 6.05 GB (measured) | the seat. But past 2025 the world is a scenario, not the record |
| **Settle more of the won book** | no argument. Rebind `net_new_acquisition.SETTLEMENT_CUSTOMER_YEAR_BUDGET` in-process, as `tools/settlement_ceiling_probe.py:147` does. The function reads it at call time (line 1146 note) | The campaign won **497** accounts and settles **53** (`book_growth_campaign.json`: 0.1236). Settled wins give 18-19 scored decisions a path, 0.35 a win. All 497 → ~173 + 38 founder ≈ **211 scored** | single path ≈ 0.68 × √(211/56) ≈ **1.3**. Two dice paths, ρ 0.52: ≈1.5. Ceiling ≈1.8 | ~3,250 customer-years. Memory curve `settlement_ceiling_slope_20260921.json`: 4.37 MB/cy, so **≈14.7 GB** a path. Wall slope 1.9-2.4 s/cy × 1.74 probe/report ratio, so **≈2.6-2.8 h** a path | the seat: a compute budget, not a commercial one. But 14.7 GB is above the 11.4 GB available now |
| **Independent books** | `live_population(base_seed=S)`. The probe has **no route** to it: `run_phase2b` assembles `CUSTOMERS` at import. `run_value_cycle_ab --book-seeds` has one, behind an EP17 refusal | K × 56 from **independent** households and casts | 0.68 × √K: K=9 → 2.04, **K=12 → 2.36** | 36 min, 5.1 GB each, serial. **K=12 ≈ 7.2 box-hours** | **the director** (`EP17_varied_population_draw`, R13 curriculum; `docs/design/curriculum/varied_population_draw_activation.json` does not exist) |

**Verdict on the levers.** Nothing the seat can pull alone separates the pooled edge. Roll seeds hit
a ceiling of 0.95. The longer window adds 20% of decisions on the same households, in a scenario
world. Settling the whole won book is the strongest seat-owned lever. It reaches about 1.3 a path,
at ~14.7 GB, which does not fit the guest beside the daemons now. **Only independent books
separate it, and the book seed is the director's.** At today's book size they are also the
cheapest per unit of SNR²: 0.46 a book in 0.6 h, against ~1.7 for a whole-book path in 2.7 h.
Small books also fit in memory beside everything else.

## The design

**Stage A: the seat's, launched on the refit. A re-take, not the decisive run.** The record this
one follows said its figures would be re-taken when the QEP refit lands. Stage A is that re-take,
as four paths at the default book. It re-grades E1-E5 on the refitted world and re-measures ρ, so
Stage B's power is priced on the world it will run in.

**Stage B: the decisive run, on the director's ruling.** Twelve independent books, each a full
`decision_probe` pass over `live_population(base_seed=S)`, with renewal dice at roll seed S. The A/B
uses the same convention, because founder ids are positional, and a shared id under two casts
would otherwise take the same dice. Seeds **61101-61112**.

### What is compared (unchanged from the record this follows)

- **Rows:** every probed renewal. **Scored:** decision years 2018-2025 only. A decision is CLOSED
  at `term_start + 365 days`.
- **Comparators:**
  - **E-true**: a flat level re-chosen each year from closed decisions, on the world's P(stay).
  - **E-belief**: the same, on the company's own belief.
  - **Hindsight**: the best single grid level on the scored rows.
  The harder ex-ante chooser on each book is the one capped beats by less.
- **Scoring:** `expected_term_margin_gbp`, term basis. Per book: `decision_probe.ex_ante_scores`.
- **The Stage B statistic:** the mean over books of (capped − harder chooser), with a t-interval
  on the between-book SD, df = K−1. Books ARE independent samples, so this time they are pooled.
  The per-book account bootstrap is reported beside it.

### Predictions, written before any run

- **L1 (Stage A).** On the refitted world, the pooled four-path SNR of capped − harder chooser stays
  **below 2**. Held at 85%. This is the "one book cannot say" claim, made where it can fail.
- **L2 (Stage A).** The cross-path per-account correlation ρ stays in 0.3-0.7. Held at 70%. Below
  0.3, dice pooling is worth more than this record says, and Stage A is extended with roll seeds
  before Stage B is pressed.
- **L3 (Stage B).** The mean over 12 books of capped − harder chooser is **positive**. Held at 70%.
- **L4 (Stage B), the decisive one.** Its t-interval excludes zero (|t| ≥ 2.2, df 11). **Held at
  45%.** The projection says 2.36, and the shrinking-edge caveat says 1.8. I do not know which
  applies.
- **L5 (Stage B).** The between-book SD of the per-book total is **larger** than the mean in-book
  account-bootstrap SD (~265). Different casts add variance that one book's bootstrap cannot see.
  Held at 60%.

If L4 fails with the mean positive, the answer is "on books of this size, over cast and dice noise,
choosing per customer is not separable from a flat price set in advance, at 12 books". The next
lever is book SIZE (`FOUNDER_BOOK.yaml`, the settlement budget). That goes to the director as a
priced menu, never as a run.

## Which world

**The QEP-refitted origin commit, whose base contains ba320e2d2.** ba320e2d2 (a clean account is
priced the same however it pays; `own_book` the default) is already an ancestor of origin/main
(checked at 7f6c66329). The refit's world change is not yet on origin. 6b9c13e87 says "the world
change waits on its arms", and dec33ff4e and 3771794a5 are the arms re-take. Launch condition 1
below names the commit.

## Launch

### Conditions. Each is checked at launch, not assumed

1. The QEP refit's world change is an ancestor of `origin/main`. The run's base is recorded as that
   origin sha, and it contains ba320e2d2 (`git merge-base --is-ancestor`).
2. Stage A only: `resource_headroom.sample()["available_mb"]` ≥ 7,100. That is the declared peak
   plus 2 GB.
3. Stage B only:
   - `docs/design/curriculum/varied_population_draw_activation.json` exists, is activated with the
     director's words, and lists 61101-61112.
   - `tools/decision_probe` has a `--book-seed` argument that refuses through the same check
     `run_value_cycle_ab.book_seed_authorisation_refusal` makes.

   **The argument exists (2026-10-04).** `python3 -m tools.decision_probe --book-seed N` asks
   `tools.book_seed_authorisation.book_seed_authorisation_refusal`, the A/B's own check lifted into
   a module that assembles no book (`run_value_cycle_ab` now delegates to it), then rebinds
   `live_population._DEFAULT_BASE_SEED` before `probe()` imports `simulation.run_phase2b`. It
   refuses if that module is already imported, and refuses after the run if `_RUN_BASE_SEED` is
   not the seed asked for. Run today with 61101 it refuses, naming the absent record. Control:
   `tests/tools/test_the_decision_probe_takes_a_book_seed_only_with_the_directors_record.py`,
   refused and admitted in one test. So condition 3 now waits only on his record.

### Stage A launch attempt, 2026-10-04 11:52Z: premise_not_yet_ripe, nothing launched

Drawn as `stage-a-of-the-larger-book-test-runs-on-the-refitted-world`. Condition 2 held:
available_mb was 15,299. **Condition 1 failed.** origin/main `7b1330fac` holds only the refit's
fit and arms commits (6b9c13e87, dec33ff4e, 3771794a5). The world change is still the patch in
`docs/design/UNLANDED_QEP_LEVEL_ANCHOR_REFIT_2026-10-04.md`, and `world_level_identity` at origin
is still the pre-refit `cf823b185f8ca51c`. The landing is in flight. The seat-executor's
`surgical_land` ("The level anchor is refitted onto DESNZ QEP 2.7.1 and the value arms are
re-taken in that world") ran in `/var/tmp/se-seat-executor` 11:31-11:46Z. It exited without
a commit, and its paths, including both `20261004r` artefacts, are still staged there. Stage A was
not run on the pre-refit world. The next draw re-checks condition 1 against origin. Once the refit
commit is an ancestor, the command below is unchanged.

### Stage A launched, 2026-10-04 14:02Z, on the refitted world

Drawn again under the same id. **Condition 1 held.** The refit's world change landed as
b9ede156f (`world_level_identity` cf823b185f8ca51c → cdba75ebb9197b33). The run's base is origin
`0859ac1a3`, and both b9ede156f and ba320e2d2 are its ancestors. **Condition 2 held:** available_mb
was 12,199. The heads-arms re-take (`longjob-heads-arms-retake`, declared 11,200 MB) was resident
at 7.7 GB at the time. The launcher admitted 12,884 MB resident plus 6,500 MB declared, which is
19,384 MB against 23,008 MB.

The command below is run unchanged. It is wrapped in `/var/tmp/se-stageA-handoff.sh`, which is
strictly serial, in the locked worktree `/var/tmp/se-stageA` at the base. It runs as unit
`longjob-stage-a-qep-probe` via `background.launch_long_job` and not via `setsid`, because a
tick's cgroup teardown kills a `setsid` child. The queue log is `/var/tmp/se-probe-out/qep_queue.log`,
and the last artefact is `probe_qep_61003.json`. E1-E5, ρ and L1/L2 are graded when all four
passes exit (≈16:30Z), under the continuation `grade-stage-a-of-the-larger-book-test`.

### Stage A, exact command. It passes `decision_probe.main`'s argument checks today

The only refusal is `--world` without `--end-year`, and neither is given.

```
cd <origin worktree at the refit sha>
for s in default 61001 61002 61003; do
  a=""; [ $s = default ] || a="--roll-seed $s"
  /usr/bin/time -v -o /var/tmp/se-probe-out/qep_$s.time \
    python3 -m tools.decision_probe --out /var/tmp/se-probe-out/probe_qep_$s.json $a \
    > /var/tmp/se-probe-out/qep_$s.log 2>&1
done
```

Strictly serial. Launch it with `setsid` (a bounded tick's child dies with it).
**Declared peak: 5,100 MB RSS (cgroup ~6.5 GB). Wall: 4 × 36 min ≈ 2.4 h.**

### Stage B, exact command. It passes once condition 3 holds

```
for S in $(seq 61101 61112); do
  /usr/bin/time -v -o /var/tmp/se-probe-out/book_$S.time \
    python3 -m tools.decision_probe --book-seed $S --roll-seed $S \
      --out /var/tmp/se-probe-out/probe_book_$S.json > /var/tmp/se-probe-out/book_$S.log 2>&1
done
```

Strictly serial, in legs of at most 6 books (~3.6 h each), so each leg ends inside a continuation.
**Declared peak: 5,100 MB RSS a book. Wall: 12 × 36 min ≈ 7.2 box-hours.** The time is at
today's book size. A different cast can draw a different number of customer-years under the same
1,050 budget, so each book's `.time` is read against this declaration, and a book above 6,000 MB
stops the leg.

## What this means for the thesis now

Before any run, the claim the existing evidence supports is narrower than "inference beats
average". **On the only book this company has, no amount of re-running can tell a per-customer rule
from a flat price set in advance from its own book.** The SNR ceiling is about 0.95. The one path
that cleared, the default, is one of four draws of the same households. Whether the method beats
average is a question about books like this one. It can be asked only across books, and the cast of
books is the director's to grant. The ask, priced at 7.2 box-hours with the Stage A re-take first,
is raised on `for_the_director`.

## Stage A grading (2026-10-04, 16:50Z, item `grade-stage-a-of-the-larger-book-test`)

**Base:** origin `0859ac1a3` (contains the refit b9ede156f and ba320e2d2). The run is the command
above, unchanged: four serial passes, `ALL DONE 15:59:08Z`. Scored offline with that base's
`tools.decision_probe.ex_ante_scores`. Scripts and raw output are in
`/var/tmp/se-probe-out/stage_a_{grade,split}.{py,txt}` (the power script's method, re-pointed at
`probe_qep_*.json`).

**Memory and time.** The peak RSS was 4,882 / 4,846 / 4,739 / 4,951 MB (default, 61001, 61002,
61003). **All four peaks were under the declared 5,100 MB.** Wall times were 28-30 min a pass,
against 36 declared.

### Levels chosen, GBP/MWh

| path | hindsight | E-true 2018 / 19 / 20 / 21 / 24 / 25 | E-belief by year |
|---|---|---|---|
| default | 45 | 95 / 30 / 30 / 30 / 40 / 40 | 50 / 40 / 25 / 50 / 55 / 55 |
| 61001 | 45 | 95 / 30 / 35 / 40 / 45 / 45 | 50 / 45 / 40 / 50 / 50 / 50 |
| 61002 | 55 | 95 / 30 / 30 / 50 / 50 / 50 | 50 / 45 / 40 / 50 / 50 / 50 |
| 61003 | 50 | 95 / 30 / 30 / 35 / 50 / 50 | 50 / 40 / 30 / 50 / 55 / 55 |

### Scores: capped value rule minus the flat level, term basis, 2018-2025, GBP (SNR)

| path | n | − E-true | − E-belief | hindsight − E-true | verdict vs the harder chooser |
|---|---|---|---|---|---|
| default | 58 | **+767 (3.05)** | +814 (3.14) | +476 (2.23) | **BEATS** (E-true, SNR 3.05) |
| 61001 | 53 | +630 (1.86) | **+52 (0.23)** | +627 (1.91) | **TIES** (E-belief, SNR 0.23) |
| 61002 | 50 | +647 (2.71) | **+270 (2.28)** | +563 (2.71) | **BEATS** (E-belief, SNR 2.28) |
| 61003 | 57 | +714 (2.54) | **+598 (2.14)** | +499 (2.20) | **BEATS** (E-belief, SNR 2.14) |

**Pre-refit: beats on one path, ties on three. Refitted base: beats on three, ties on one.**

### L1 and L2

- **L1 FAILED.** The pooled four-path SNR of capped − harder chooser is **2.38**: a mean total of
  +421.6 GBP over ~54.5 decisions (7.7 GBP a decision), with a joint-account SD of 177.3. I predicted
  below 2 at 85%. The "one book cannot say" claim is false on this base. **The SNR ceiling on this
  book was 0.95 and is now ≈2.67** (RMS single-path SD 226, ρ 0.49).
- **L2 HELD.** The pairwise per-account ρ is 0.34-0.76, mean **0.53**. ρ from the joint SD is
  **0.49**. Dice pooling is worth what the record said, so there is no roll-seed extension.

**How far it holds.** Drop the first book year (2018, chosen on two closed decisions) and the pooled
SNR is **1.56** (+303 over ~40 decisions, joint SD 195). 2018 is ~28% of the edge. Before the refit
it was most of it. So the edge now persists after the book has a year in it, at the same ~7.5 GBP a
decision, but **2019-2025 alone does not clear 2.** On 61001 it is −22 (SNR 0.09).

**What this does NOT establish.** The SD is an in-book account bootstrap. It sees dice and
account-sampling noise, not CAST noise: these are 42 households, 28 shared by all four paths. "Beats
on this book" is now separable. "Beats on books like this one" is still Stage B's question, and L5
says the between-book SD is larger.

**Attribution: I cannot yet say.** The two bases are 96 commits apart (`4bf859f0b..0859ac1a3`). They
touch the refit (`departure_level_anchor`), `plan_offer_response` (+162), `collections_journey`,
`default_belief`, `run_phase2b` and `decision_probe` itself. The edge per decision rose from 3.2 to
7.7 GBP, and the E-true early levels moved from 15/55 to 95/30 on three paths. The one-variable
check is the old book on the new code with the pre-refit anchor. It is not run, and nothing here
depends on it.

### E1-E5, re-graded against the record this follows (harder chooser read as there)

| | pre-refit (`4bf859f0b`) | refitted (`0859ac1a3`) |
|---|---|---|
| **E1** (E-true off hindsight by ≥10 in some year, ≥2/4) | HELD 4/4 | **HELD 4/4.** 2018 is 95 everywhere, against 45-55 |
| **E2** (capped − E-true > 0 on ≥3/4) | HELD 4/4 | **HELD 4/4**: +767, +630, +647, +714 |
| **E3** (SNR vs E-true < 2 on every path) | FAILED, 1 path above | **FAILED, 3 above** (3.05, 2.71, 2.54; 61001 1.86) |
| **E4** (− E-belief ≥ − E-true on every path) | FAILED, holds on 61002 only | **FAILED, holds on default only** |
| **E5** (hindsight − E-true < 300 on ≥3/4) | FAILED, 1/4 | **FAILED, 0/4**: 476, 627, 563, 499 |

**E4 and E5 point the same way as before, more strongly.** E-true's first two levels (95, then 30)
are the noisiest choice in the table, and E-belief's smooth belief is the harder comparator on
three paths.

### What it does to Stage B

Stage B's power was priced on a single-book SNR of 0.68. On this base, the single-path SNR on the
pooled edge is ≈1.86 (full window) or ≈1.23 (2019-25). Let s be that SNR shrunk by the unknown
ratio of between-book to in-book SD. The t-test at K books then reads:

| s | K=4 | K=6 | K=8 | K=12 | t crit (K=12, df 11) |
|---|---|---|---|---|---|
| 1.86 (between = in-book) | 3.73 | 4.57 | 5.27 | 6.46 | 2.20 |
| 1.24 (1.5× in-book, or the 2019-25 edge) | 2.49 | 3.04 | 3.51 | 4.30 | 2.20 |
| 0.93 (2× in-book) | 1.86 | 2.28 | 2.64 | 3.23 | 2.20 |
| 0.62 (2019-25 edge, 2× in-book) | 1.24 | 1.52 | 1.75 | 2.15 | 2.20 |

**Twelve books stay the right ask.** It is the only size that clears the threshold over three of
these four rows, and it misses the fourth only narrowly. Fewer books save box-hours by betting on a
between-book SD nobody has measured. L4's 45% was priced on 1.8-2.4. On this base it projects 2.2-6.5.
The `for_the_director` row `whether-per-customer-pricing-beats-a-flat` quoted the old ceiling (0.95).
That is a plain factual error, corrected in the same landing.

**Disposition:** Stage A is graded and its worktree `/var/tmp/se-stageA` is removed.
