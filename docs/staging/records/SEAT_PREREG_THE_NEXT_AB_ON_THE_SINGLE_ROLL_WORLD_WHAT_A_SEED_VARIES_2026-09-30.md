# Prereg: the next value-cycle A/B on the single-roll world — what a seed varies, and so how many

**Severity:** RECORDED · **Lane:** A_strategy_governance · **Item:** `prereg-the-next-ab-on-the-repaired-world-keyed-by-lineage` · **Status:** **LAUNCHED 2026-09-30T04:10:47Z** as `longjob-ab6-single-roll`; bridge B started 04:26:47Z (launch record at the foot).

## Why this exists

The ab5 family (`records/SEAT_RESULT_THE_DECIDED_DIFFERENTLY_SIGN_OVER_FIVE_SEEDS_ON_ONE_WEATHER_STORE_2026-09-29.md`, and its lineage follow-up `records/SEAT_PREREG_THE_LINEAGE_KEYED_DECIDED_DIFFERENTLY_SIGN_ON_FOUR_UNSEEN_SEEDS_2026-09-30.md`, still running) has two problems. It is graded at `b79e2c0e8`, which is before the single-roll repair (`19a58b44d`, where a resi renewal is decided once). And its key is by account, so its lineage fold was post-hoc. The unseen-seed run fixes the second problem but not the first. It also inherits the design question this record answers first: **what does a seed vary in this design?** Increment 3 found 33333 replicating to the penny, which suggested more seeds might buy almost nothing. That has now been measured.

## What a seed varies in the ab5 design (measured 2026-09-30 from runB, runA1, runA2 — five seeds)

`/var/tmp/se-ab6-out/seed_census.py` (sha256 `dd7b12c4…98a`) was run over `/var/tmp/se-ab5-out/run{B,A1,A2}.json`. Accounts are grouped by lineage root (`saas.customers.SUCCESSOR_CUSTOMERS`, which is the same at both pins).

- **What the seed re-draws.** `redraw_key = elasticity`, `redraw_scope = all`. The seed changes only each household's price-elasticity weight, and that draw is reached only behind an offered rate (298–303 draws from 69–70 accounts). **The renewal dice are NOT re-drawn.** `churn_roll_for_renewal` hashes `account_term` and takes no seed, so every account rolls the same number on every seed. For example, 0098 rolls 0.3763, C5 0.2812 and SYN-2016-015 0.6402 on all five seeds. A seed only moves `p_retain` around a fixed roll, so an outcome changes only for an account whose `p_retain` straddles its own roll across seeds.
- **120 of 163 lineages are identical to the penny** on all five seeds. They carry **+£863.63** of value-minus-level on every seed, and 39 of them are decided-differently (+£864.58). This is most of D, and it is **one realisation of every renewal roll**: n = 1 on the quantity that matters.
- **43 lineages vary, and they fall into a few discrete states, not a spread.** 0098 is a level-arm switch of ±£5,836 (it churns on 11111 and 44444). C5's value-arm churn is a two-state switch (22222 and 44444), and 19 small lineages move in lockstep with it (range-sum £122). SYN-2016-015 has three states (range £259). Only three lineages vary continuously (C8, PROS-2017-0183, PROS-2016-0129; £39 in total).
- **D_lin ex-0098's seed spread is one account.** It is sd £133.98 over five seeds. Remove SYN-2016-015 and it falls to **£33.38**. Remove the four continuous movers as well and it falls to £12.33. SYN-2016-015's `p_retain` straddles its roll in both arms (0.601–0.644 against 0.6402; on 88888 the value arm misses it by 0.0001), so it is ~94% of the variance.

**So, in this design, a seed estimates the chance that a handful of near-threshold accounts flip. It says nothing about whether the +£864 would survive a different roll.** The five-seed t-CI [+£843, +£1,176] is an honest interval over elasticity draws and a dishonest one over the world. More elasticity seeds cannot change that: the answer on this key is already "positive" from two seeds. **The varying part is too small to carry a verdict, so what must vary is the churn roll itself.**

## The design

- **Code:** HEAD `a322166cc`, pinned at `/var/tmp/se-ab6-a322166cc` (detached and `git worktree lock`ed, reason recorded). It includes the single-roll repair `19a58b44d`, and also `936d30be5` (a dual-fuel household pays both fuels one way), `bc16b269b` (the engagement factor stops double-counting its prior), `629b6306f` and `decabc703`. **So the code moves as well as the key, and that is why there is a bridge leg.**
- **Weather store:** `weather_store_digest()` at the pin reads `e11451b5…d242`, the same store as ab5.
- **Key:** D_lin, exactly as in the unseen-seed prereg (lineage root; DECIDED if any member decided differently; ex-0098). The grader is `/var/tmp/se-ab6-out/grade_lineage.py` (sha256 `71b82d07…65df7`). It is ab5's grader with only PIN changed. Reproduced on the five seen seeds: mean +£1,009.68, sd £133.98 (it matches).
- **Legs, strictly serial** (two `--level-arm` legs cannot be co-resident on this box, per `24ae94c05`; each is 2 seeds because `noise_floor` refuses one):
  1. **Bridge B:** `--level-arm --noise-floor-seeds 33333,44444 --redraw-key elasticity` gives `runB6.json`. These are the same seeds and key as ab5, at HEAD, so the only variable is the code. 33333 is in the C5-renewed state and 44444 in the C5-churned state with 0098 churned.
  2. **Pilot P1:** `--level-arm --noise-floor-seeds 61001,61002 --redraw-key churn_roll` gives `runP1.json`.
  3. **Pilot P2:** the same with `61003,61004`, giving `runP2.json`.
- **What a seed varies under `churn_roll`:** every renewal roll of every account that reaches a renewal point (~70 accounts and ~230–265 rolls, from the size-term floor at `a35c798a2`). Both arms share the roll within a seed, so D stays paired. Elasticity is held at the production draw. Home-move timing, arrivals, the book's composition and the non-renewal departure branch are **not** varied. A seed under this key is "one more draw of who renews", and nothing else.
- **Cost:** ~93 min per seed at an ~11.2 GB declared peak (the admission figure from `24ae94c05`), so ~9.3h for six seeds serially.

## How the seed count is derived (from the varying part only, before any extension)

After P1 and P2 (four churn-roll seeds), take the pilot's D_lin mean m and sd s. **n\*** is the smallest n with t₀.₉₇₅,ₙ₋₁ · s / √n ≤ |m|. It is also reported with |m| replaced by the ab5 reference £1,009.68.

- **n\* ≤ 12:** extend in 2-seed legs (61005…) to n\* and grade. The ceiling of 12 is a compute choice, not a domain number: ~18.6h, about three continuations, and the same order as increment 3's "~12 needed" on the old key.
- **n\* > 12:** **stop.** The answer is *"under its own renewal noise, this book cannot sign D"*. The next design varies the **book**, not the seed: a longer window, or a funnel that offers renewals more widely. Only ~70 of 164 settled accounts ever renew here, and `run_value_cycle_ab`'s `REDRAW_KEYS` note already names the funnel as the constraint no key reaches.

## Predictions (fixed before launch; nothing below has been run)

| id | line | prediction | refuted if |
|---|---|---|---|
| **B1** | bridge, per seed: D_lin at HEAD − D_lin at ab5 (33333: +£1,038.66; 44444: +£784.65) | \|Δ\| < £300 on both | either \|Δ\| ≥ £300. The code change then moved D by more than ab5's whole seed spread, and the ab5 grade does not describe HEAD |
| **B2** | bridge: lineages whose difference is identical to the penny against the same ab5 seed | fewer than 120 of ~163 (`936d30be5` re-routes dual-fuel gas payments, and there are 80 dual-fuel accounts) | ≥ 150 identical. The world change did not reach the A/B, so the bridge was nearly free and B1 is weak evidence |
| **P1** | pilot: D_lin sd across the four churn-roll seeds | **£1,500 to £8,000** (point guess £4,000). Anchors: the size-term floor's blind-leg net-margin sd under the same key was £6,649 (6 seeds, `a35c798a2`), and one flip of 0098 alone is £5,836 | sd < £1,500 (the rolls matter less than one account's switch suggests) or > £8,000 |
| **P2** | n\* at the pilot's own mean | **> 12, so the verdict is "stop, vary the book"** (~70%) | n\* ≤ 12 |
| **P3** | the share of the pilot's D_lin variance held by its single largest lineage | < 50%. Under roll redraw, many accounts flip, not one | ≥ 50%. The churn-roll key then collapses back to a few switches, and the book is too thin whatever the key |
| P4 (context) | pilot D_lin sign | 2–3 of 4 positive | not graded |

**Plain answer rule.** If n\* ≤ 12 and the extended t-CI excludes zero, the answer is **yes**: on what it decided differently, and over its own renewal noise, the per-customer arm beats flat rules at HEAD. If n\* > 12, the answer is **we cannot say on this book**, and that is a result, not a failure. Either way the ab5 "+£1,000, CI clear of zero" is re-labelled as conditional on one set of renewal rolls. **Confidence:** B1 ~60%, B2 ~65%, P1 ~70%, P2 ~70%, P3 ~75%.

**What would make this the wrong test.** If the bridge fails B1 badly (|Δ| > £1,000), HEAD is a different company, and the pilot measures HEAD's D, not ab5's. That is still the right thing to measure, but the ab5 line must then be closed as "graded at a superseded world", not carried forward. If `noise_floor` on `churn_roll` reports `churn_rolls_redrawn = 0` on any seed, the repair has moved the roll off the patched symbol. The leg must refuse (the tool raises), and this prereg is void until the symbol is re-found.

## Launch conditions (all must hold; none holds a director's decision except the last)

1. `longjob-ab5-lineage-unseen` has exited (it is the same box and has the same 11.2–11.8 GB peak).
2. `git -C /var/tmp/se-ab6-a322166cc diff --quiet a322166cc -- . ':!docs'`, and the pin is still locked.
3. `weather_store_digest()` in the pin equals `e11451b5…d242`.
4. Launch through `background.launch_long_job` as one unit running B, then P1, then P2, with each leg gated on its predecessor through `tools.wait_for` (deadline ≤ 21,600 s, the tool's ceiling; ab5's first launch refused on 43,200). The unit declares the 11,200 MB peak so the admission and `sim-runner`'s per-cycle ask (`a1ba7b753`) can see it.
5. **The next steer says launch.** This item was scoped as a pre-registration only.

Grading: `seed_census.py runB6.json` against ab5 (B1, B2), then `grade_lineage.py runP1.json runP2.json` plus the n\* computation above (P1–P3).

## Launch record (2026-09-30, delivery seat, item `stop-the-old-design-after-one-pair-and-launch-ab6`)

**Conditions, each re-asked at launch:**
1. **The lineage unit has exited: HOLDS, by gating.** ab6 was launched at 04:10:47Z with `--wait-for-pid 2295586`, the L1 leg's `run_value_cycle_ab`. That puts its 11,200 MB declaration on the shared register before the PB6 waiter could race for the same moment. L1 exited 0 at 04:26:21Z. `longjob-ab5-lineage-unseen` was stopped at 04:26:43Z. legs6.sh's own resident check then waited 15 s for L2's pid 2941018 to die with that unit. So no two value-cycle A/Bs were ever co-resident.
2. **Pin clean and locked: HOLDS.** `git -C /var/tmp/se-ab6-a322166cc diff --quiet a322166cc -- . ':!docs'` returned 0. HEAD is `a322166cc0…`, detached and `locked` ("ab6 prereg pin: lineage-keyed D on the single-roll world, churn-roll redraw").
3. **Weather store: HOLDS.** `weather_store_digest()` in the pin equals `e11451b5…d242`. It was read by the seat before launch, and again by legs6.sh at B's start (logged).
4. **One unit, B→P1→P2, peak declared: HOLDS.** The unit is `longjob-ab6-single-roll`, running `/var/tmp/se-ab6-out/legs6.sh` (sha256 `519b1a84…2e4b`). Each leg re-checks conditions 2–3 and runs only if its predecessor exited 0 and wrote its artefact. The unit was launched through `background.launch_long_job --peak-mb 11200`. Admission read: 7,494 MB resident + 11,200 = 18,694 of 23,008 MB, with pid 2295586's 11,798 MB excluded as waited-on. The cgroup is its own (verified). The artefact the unit declares is `runP2.json`; B and P1 write `runB6.json` and `runP1.json`. The log is `/var/tmp/se-ab6-out/run6.log`.
5. **The steer: this item.**

**Grader pins, recorded in full.** `grade_lineage.py` is `71b82d0737c21631420bb41399ccdf12407550655929e75aae7e0bdfd5a65df7`, which matches above. `seed_census.py` is `dd7b12c4c655a1a9b33064c16919f5d298231c2de80320dcef2423d6e0099e8a`. The "…98a" abbreviation above is a transcription slip, not a changed file: its mtime (01:45:43Z) predates this record's commit `7413b3ea2` (02:00:16Z).

**One co-residence, admitted and not prevented.** When legsL.sh exited, the PB6 re-centred null arm's waiter fired too. `launch_long_job` admitted `longjob-pb6-null-arm-recentred-prior-run` (declared 6,500 MB) at 04:26:52Z beside ab6's declared 11,200, because the two fit the budget after L1's 11.8 GB left. A PB6 arm is ~30 min, and it overlaps only the start of bridge B, which is well below its peak then. **If B dies of OOM**, legs6.sh stops at B (rc 94) and P1/P2 do not run. The remedy is to relaunch the same unit once the PB6 arm has exited. It is not a change to this design.

**Next:** grade B (B1, B2) when `runB6.json` exists (~3h after 04:26Z), then P1–P3 and n\* when `runP2.json` exists (~9.3h). That is handed on through `seat_continuation`.

## Bridge graded (2026-09-30 ~07:50Z, delivery seat, item `grade-the-ab6-bridge-leg-once-runb6-exists`)

**What was run.** Leg B exited rc=0 at 07:27:14Z (`run6.log`). The weather digest at B's start was `e11451b5…d242`. `runB6.json` has sha256 `b73d4c36…a9e2`. `grade_lineage.py` (`71b82d07…`, matches) was run on `runB6.json`, and ab5's own grader on `/var/tmp/se-ab5-out/runB.json` (the same seeds). `seed_census.py` (`dd7b12c4…`, matches) was run on `runB6.json`. `seed_census.py` keys rows by seed, so it cannot compare one seed across two pins. The per-lineage cross-pin comparison is therefore `/var/tmp/se-ab6-out/bridge_cmp.py` (sha256 `0e3880d6…1a776ffa`; it roots lineages through the ab6 pin's `SUCCESSOR_CUSTOMERS`, exactly as `seed_census.py` does).

| id | prediction | result | grade |
|---|---|---|---|
| **B1** | \|Δ D_lin\| < £300 on both seeds | 33333: +£813.63 − £1,038.66 = **−£225.03**. 44444: +£284.02 − £784.65 = **−£500.63** | **REFUTED** (on 44444). The miss is not > £1,000, so the ab5 line does **not** close as "graded at a superseded world" |
| **B2** | fewer than 120 of ~163 lineages identical to the penny against the same ab5 seed | **112 of 163** on each seed (51 moved) | **HOLDS**. The world change reached the A/B |

**Where the move is.** No lineage changed its DECIDED flag and none appeared or vanished, on either seed. So the move is not a switch. It is drift spread across roughly 50 lineages, and nearly all of it is the **level arm's net rising** while the value arm mostly holds. On 44444: C5 −£154 (L +£154, V unchanged), C9 −£57, C8 −£55, SYN-2016-064 −£55, SYN-2016-055 −£48, PROS-2020-0304 −£42. The top five give −£369 of the −£499 ex-0098. On 33333 the same lineages move the same way at about half the size (C5 −£77, SYN-2016-064 −£35, C9 −£30). 0098 barely moves (−£17 and −£0.4). *Why 44444 moves about twice as much on the same lineages, I cannot yet say.* 44444 is the seed in which C5 churns in the value arm and 0098 churns in the level arm, so a state-dependent path through one of the five commits (`936d30be5` re-routes dual-fuel gas, `bc16b269b` the engagement prior) is the candidate. No one-commit bisection has been run.

**What this means for the ab5 line.** ab5's D_lin grade does not describe HEAD within ab5's own seed spread (sd £133.98). HEAD's D_lin is lower by £225–£500 per seed, and the drop runs one way on both seeds, through the level arm. Read literally, the ab5 five-seed mean of +£1,009.68 is about +£510 to +£785 at HEAD, and both HEAD bridge seeds are still positive (+£814, +£284). That is not a grade: two seeds, and the per-seed shift itself differs by £276. **So ab5's "+£1,000, CI clear of zero" is re-labelled as conditional on `b79e2c0e8` and on one set of renewal rolls, and it is not carried into the pilot's reading.** The pilot's n\* is computed from P1+P2's own mean, as pre-registered. The alternative with |m| = £1,009.68 is now known to overstate HEAD's effect and is reported only as context.

**Correction, beside the claim.** The B1 confidence was ~60%, and it missed. "Refuted if either \|Δ\| ≥ £300" holds on one seed, by £200. The P-legs are untouched by this: P1 started on the same pin and digest right after B exited.

## Pilots graded (2026-09-30 ~13:50Z, autonomous worker, item `grade-ab6-bridge-and-pilots`)

**What was run.** Leg P2 exited rc=0 at 13:39:49Z (`run6.log`). P1 had exited at 10:30:00Z. Artefacts: `runP1.json` sha256 `690784f2…317d`, `runP2.json` sha256 `2e311968…bba7`. `grade_lineage.py` (`71b82d07…65df7`, matches) was run on both. Its weather-digest line reads `{e11451b5…d242}`, which equals the launch digest. The n\* and variance-share arithmetic is `/var/tmp/se-ab6-out/grade_p3.py` (sha256 `45e1864e…1cdf`). It uses grade_lineage's lineage rooting and DECIDED rule, copied unchanged, and computes n\* by the definition above.

**The re-draw reached every seed.** The prereg's `churn_rolls_redrawn` is the key-neutral `draws_redrawn` in the artefact. It is > 0 on all four seeds, and `held = 0` on each:

| seed | draws_redrawn | accounts_redrawn | D_lin ex-0098 | 0098 lineage (excluded) |
|---|---|---|---|---|
| 61001 | 346 | 71 | **−£1,199.15** | −£83.55 |
| 61002 | 374 | 72 | **−£6,758.07** | −£5,984.12 |
| 61003 | 393 | 70 | **−£3,070.89** | −£225.89 |
| 61004 | 376 | 72 | **−£1,242.19** | −£273.69 |

The DECIDED set is the same 69 lineages on all four seeds. A_lin is small and positive on each (+£16.52 to +£216.97). There are no roster-only lineages.

**Pilot: mean −£3,067.58, sd £2,610.41, 95% t-CI [−£7,221.33, +£1,086.17].**

| id | prediction | result | grade |
|---|---|---|---|
| **P1** | D_lin sd across the four seeds is £1,500–£8,000 (point guess £4,000) | **£2,610.41** | **HOLDS** |
| **P2** | n\* at the pilot's own mean > 12, so "stop, vary the book" (~70%) | **n\* = 6** (t₀.₉₇₅,₅ · 2,610.41/√6 = £2,740 ≤ £3,067.58). At the ab5 reference \|m\| = £1,009.68, which the bridge showed overstates HEAD and is context only: n\* = 29 | **REFUTED** |
| **P3** | the single largest lineage holds < 50% of the pilot's D_lin variance | **C6: 79.1%** on the measure the ab5 section used (1 − var(D − L)/var(D)). SYN-2016-034 is 76.8% and C5 46.7%. On own-variance share, var(L)/var(D), the figures are C6 37.1%, SYN-2016-034 37.2% and C5 25.8% | **REFUTED** on the prereg's own measure |
| P4 (context) | 2–3 of 4 positive | **0 of 4 positive** (sign p = 0.125) | not graded; the prediction missed |

**What P3 is and is not.** 67 of the 69 DECIDED lineages vary across the four seeds, so the renewal-roll key does reach the book widely. But the variance is held by a few switches: C6 (−£2,825 on 61002, +£794 on 61004, £0 otherwise), SYN-2016-034 (−£3,229 on 61002) and C5 (+£169 to +£2,845). C6 and SYN-2016-034 both land on seed 61002, and so does 0098's −£5,984. That is why their removal shares overlap and sum to more than 100%. With four seeds, a variance share is itself very loose. So "the key collapses back to a few switches" is the reading the prereg named, and it holds on this sample. It is not yet a property of the book.

**The sign.** Under the elasticity key, the bridge at this same pin read +£813.63 and +£284.02 (33333, 44444) on the fixed production rolls. Under four independent draws of those rolls, it reads negative on every draw, and by more than either bridge value. So the ab5/bridge positive was one realisation of the renewal rolls, and it was a favourable one for the value arm. *Why the value arm loses on these draws, I cannot yet say.* The largest movers are single-account churn switches (C6 and SYN-2016-034 on 61002), but no per-account attribution has been run. **Correction, beside the claim:** P4's "2–3 of 4 positive" and the ab5 line's "+£1,000, CI clear of zero" both assumed a positive centre. On the churn-roll key the centre is not positive.

**What the answer describes.** It describes the **pin `a322166cc`**, not origin/main. One commit on origin since the pin touches `company/` or `simulation/`: `4380002bd` (2026-09-30 14:09 +0100, "land the 19 receipted commits stranded on the shared tree's HEAD…"). It changes `company/crm/competitive_pressure.py`, `company/crm/enriched_churn_estimate.py`, `company/interfaces/sim_interface.py`, `simulation/household.py`, `simulation/household_physical_layer.py` and `simulation/run_phase4c_on_phase2b.py`. The code-bearing replays inside it include `f9b04ddc7` and `46b78123f` (PB6: the engagement prior is re-centred at no effect, and the seam stops booking a no-account lookup as direct debit) and `c5e30c230` (a leaving household's gas leg is a leaver). The first two move the company's churn estimate, which feeds `p_retain`, and `p_retain` is exactly what the churn roll is compared against. So a re-grade at origin is a different world, and this grade does not transfer to it without a bridge.

**Consequence under the rule above: n\* = 6 ≤ 12, so extend.** Seeds 61001–61004 are done, so the extension is one 2-seed leg, **X1: 61005,61006, `churn_roll`**, on the same pin and weather store. It runs as `/var/tmp/se-ab6-out/legs6x.sh` (sha256 `d1ad196c…d23e`). That script is legs6.sh's per-leg pin and digest checks, verbatim, with the leg line changed and one repair to the resident check. **The repair: legs6.sh's resident check matches prompts, not only runs.** `pgrep -f "tools.run_value_cycle_ab"` is unanchored, and `.` matches `/`. The first X1 launch (13:41:25Z) therefore sat waiting on pid 202737, which is a Claude seat whose prompt text names `tools/run_value_cycle_ab.py`. My own session matched too. It would have waited up to 6h and then refused with rc 91. I stopped my own unit after ~30 s, before any leg started (log kept as `runX1.falsestart.log`). legs6x.sh anchors the pattern to the leg's argv (`^python3 -m tools\.run_value_cycle_ab`), and it relaunched at 13:42:02Z. legs6.sh got lucky: at its launch it waited only on real runs. The same pattern in any copy of it can stall for hours on a prompt. X1 is pid 313621. Its log shows the pin clean and the weather digest `e11451b5…d242` at start. The unit is `longjob-ab6-extension-x1`, launched through `background.launch_long_job --peak-mb 11200`. At launch it was admitted at 6,035 MB resident + 11,200 = 17,235 of 23,008 MB. It writes `/var/tmp/se-ab6-out/runX1.json` and logs to `runX1.log`, and takes ~3h. **The book-varying design (`SEAT_PREREG_THE_AB_THAT_VARIES_THE_BOOK_NOT_THE_SEED_2026-09-30.md`, and its EP17 amendment `19ca27dbc`) is not triggered by this result**, and nothing here runs `--book-seeds` or writes the activation file.

**Predictions for X1, filed before it launched:**

| id | prediction | refuted if |
|---|---|---|
| **X1a** | both X1 seeds' D_lin ex-0098 < 0 (~65%) | either ≥ 0 |
| **X1b** | the six-seed 95% t-CI excludes zero, on the negative side (~55%) | the CI contains zero, or excludes it on the positive side |
| **X1c** | the six-seed sd stays in £1,500–£8,000 (~80%) | outside |

**The plain answer, fixed before X1 reads.** If X1b holds, the answer at the pin is **no**. On what it decided differently, and over its own renewal noise, the per-customer arm **loses** to flat rules, and the ab5 positive was the fixed roll. If the CI contains zero at n = 6, the answer is **"cannot say on this book under its own renewal noise"**. The next step is then the book-varying prereg above, not more seeds: n\* was computed from a four-seed sd, and the prereg's ceiling is not re-opened after the fact.

**Grading X1:** `grade_lineage.py runP1.json runP2.json runX1.json` and `grade_p3.py` over the same three artefacts.

## X1 graded (2026-09-30 ~17:45Z, delivery seat, item `grade-ab6-extension-x1-r2`)

**What was run.** Leg X1 (61005, 61006, `churn_roll`) exited rc=0 at 16:49:40Z (`runX1.log`), and its weather digest at start was `e11451b5…d242`. The artefact is `runX1.json`, sha256 `50dba3de…`. It was graded unchanged by `grade_lineage.py` (`71b82d07…65df7`) and `grade_p3.py` (`45e1864e…1cdf`), over `runP1.json runP2.json runX1.json`. The launch script `legs6x.sh` hashes to `d1ad196c…d23e`, which matches the launch record. grade_lineage's digest line reads `equals launch digest: True`.

**The re-draw reached both new seeds.** 61005 has draws_redrawn 365 and accounts_redrawn 72. 61006 has 362 and 71. The DECIDED set is the same 69 lineages on all six seeds.

| seed | draws_redrawn | D_lin ex-0098 | 0098 lineage (excluded) | A_lin |
|---|---|---|---|---|
| 61005 | 365 | **−£2,202.11** | −£198.36 | −£4.19 |
| 61006 | 362 | **+£216.48** | £0.00 | −£26.43 |

**Six seeds: mean −£2,375.99, sd £2,412.76, 95% t-CI [−£4,908.03, +£156.05]. 1 of 6 positive (sign p = 0.219).**

| id | prediction | result | grade |
|---|---|---|---|
| **X1a** | both X1 seeds' D_lin ex-0098 < 0 (~65%) | 61005 −£2,202.11, **61006 +£216.48** | **REFUTED** |
| **X1b** | the six-seed 95% t-CI excludes zero on the negative side (~55%) | **[−£4,908.03, +£156.05] contains zero** | **REFUTED** |
| **X1c** | the six-seed sd stays in £1,500–£8,000 (~80%) | **£2,412.76** | **HOLDS** |

**The plain answer, as fixed above before X1 read: at the pin `a322166cc`, we cannot say on this book under its own renewal noise** whether per-customer choosing beats flat rules on what it decided differently. The centre is negative: 5 of 6 seeds are negative and the mean is −£2,376. So the ab5 "+£1,000, CI clear of zero" stays re-labelled as one favourable roll. It is not a win, and on six rolls it is not a signed loss either. The next step is the book-varying design, not more seeds: `SEAT_PREREG_THE_AB_THAT_VARIES_THE_BOOK_NOT_THE_SEED_2026-09-30.md` and its EP17 amendment `19ca27dbc`.

**Two things that are true and could be read the wrong way.**
1. **n\* at the six-seed moments is 7.** That is one seed more than was run. The stopping rule was fixed at four seeds. Adding seeds after reading the CI until it clears zero is optional stopping, and this section's rule forbids it. No seventh seed is launched. The figure is recorded, not acted on.
2. **The book-varying prereg's own trigger does not literally fire.** Its rule 2 and launch condition 1 key on *n\*_r > 12*. The six-seed n\*_r is 7, and the four-seed n\*_r was 6. This record reaches the book design by a different branch, the one fixed above: the CI contains zero at the extension's end. The two records were written for the same question from opposite ends, and neither covered n\* ≤ 12 with the extended CI still containing zero. That gap is named here rather than papered over. Either way, the book pilot launches only on the director's ruling, recorded as `docs/design/curriculum/varied_population_draw_activation.json` (EP17, R13). The seat has not written that file and does not run `--book-seeds`.

**What the six seeds say about where the variance lives.** 67 of 69 lineages vary. By removal share (1 − var(D − L)/var(D)), the largest are SYN-2016-034 at 66.9%, C6 at 47.8% and C5 at 42.6%. The shares overlap because they co-move on 61002. So P3's refutation stands on six seeds: the roll key reaches the book widely, but a handful of single-account switches carry the spread. *Why the value arm loses on most draws, I still cannot say*, because no per-account attribution has been run. As before, this describes the pin, not origin/main: the PB6 churn-estimate commits in `4380002bd` sit between them.

## Where the loss comes from: per-account attribution (2026-09-30 ~18:55Z, autonomous worker, item `grade-x1-and-attribute-the-loss`)

The X1 grade and the plain answer are in the section above (`32c04d778`). Nothing new was run for this section. `/var/tmp/se-ab6-out/attribute_x1.py` (sha256 `018ae094…49da8`) reads the same three artefacts (`runP1.json runP2.json runX1.json`), and it uses grade_lineage's rooting and its 0098 exclusion, copied unchanged. In the artefact, `believed_p_retain` is `p_retain(m*)`, which is the company's retention belief at the margin it chose (`company/pricing/value_based_renewal.py` `decide_margin` at the pin). So the belief and the world's `p_retain` below are read at the **same offer**. One limit: the artefact logs the world's `p_retain` and the roll for the **first renewal only**. A switch at a later renewal is identified by tenure (`bills_issued`, `left_at`) and by the margins the two arms quoted, not by p against roll.

**The named lineages (margins are £/MWh; V is the value arm, L the flat arm):**

| seed | lineage | diff V−L | the renewal where the arms part | V offer | L offer | world p_retain V / L vs roll | outcome V / L | company's belief at V's offer |
|---|---|---|---|---|---|---|---|---|
| 61002 | C6 (+C6_2) | **−£2,825** | C6 2018-04-01; C6_2 2020-03-31 | margin 123.25 (rate 248.44); 101.75 (217.66) | 36.25 (161.44); 36.25 (152.16) | not logged (later renewals) | V loses C6 in 2018 and C6_2 in 2020; L keeps C6 to 2019 and C6_2 to 2024 | 0.558; 0.628 |
| 61002 | SYN-2016-034 | **−£3,229** | 2021-05-02 (fourth renewal) | margin 44.00 (rate 185.27); V had climbed 22→35→41→44 | 36.25 (177.52) | not logged | V loses the customer 2021; L keeps them to the end (110 bills against 61) | **0.911** |
| 61002 | 0098 (excluded) | −£5,984 | 2017-03-23 | margin **12.50** (rate 138.45) | 36.25 (162.20) | 0.760 / 0.571, roll 0.610 | **V keeps**, L loses | 0.326 |
| 61005 | C6 (largest \|diff\|) | **+£2,193** | none: same tenure in both arms | margins 53→117→156 | 34 flat | 0.629 / 0.704, roll 0.625 | both renew; both lose C6_2 in 2020 | 0.379→0.554→0.635 |
| 61006 | SYN-2016-062 (largest \|diff\|) | **+£2,999** | 2017-08-31 | margin 23.75 (rate 126.20) | 30.00 (132.45) | 0.8203 / 0.7973, roll **0.7983** | **V keeps** (107 bills), L loses (13) | 0.577 |

**What the population says (six seeds, DECIDED accounts, ex-0098).** Each account's V−L is split by whether the two arms kept it for the same number of bills. The three classes reconcile exactly to the graded mean: −6,046.56 + 2,870.48 + 800.09 = −2,375.99.

| class | six-seed mean | per seed (n, £) |
|---|---|---|
| V loses a customer L keeps | **−£6,046.56** | 61001 (7, −5,288) · 61002 (6, −7,442) · 61003 (5, −3,923) · 61004 (4, −4,806) · 61005 (6, −7,200) · 61006 (7, −7,620) |
| V keeps a customer L loses | **+£2,870.48** | (1, +3,409) · (1, +1,345) · (0, 0) · (1, +749) · (3, +4,084) · (5, +7,635) |
| same tenure in both arms (pure price) | **+£800.09** | (63, +680) · (65, −661) · (65, +852) · (67, +2,815) · (63, +914) · (59, +201) |

**What the offers were:**
- At first renewals (411 paired), V quoted above L on 237 of them, by a mean of **+£25.48/MWh**. That cost a mean of −0.0316 in world `p_retain`, and it produced 11 switches where V lost and L kept, against 0 the other way.
- V quoted below L on 168, by a mean of −£8.08. That gave +0.0142 in `p_retain` and 3 switches where V kept, against 0 the other way.
- The expected counts are 237 × 0.0316 ≈ 7.5 and 168 × 0.0142 ≈ 2.4. So 11 against 3 is what the offers predict. **It is not an unlucky roll.**

**What the company believed:**
- At V's own offer, the company's belief has a mean of 0.629, against a world mean of 0.683.
- **Across accounts, the correlation between the belief and the world's `p_retain` is −0.257.** Discrimination AUC by seed is 0.579, 0.496, 0.450, 0.419, 0.348 and 0.624, with a mean of **0.486**.
- SYN-2016-034 is the sharpest single case. The company put its retention at 0.911 when it quoted +£7.75 over flat, and the world took the customer away.

**The cause, stated plainly: mispriced retention, which is the company's churn estimate.** It is not the offer as such. On accounts whose tenure the offer did not change, the per-customer margin earns **+£800 per seed**, positive on 5 of 6 seeds. The whole of the negative centre is tenure switches. V's raises go to customers without regard to who will actually stay, because the estimate that should steer them cannot rank stayers above leavers: its AUC is ~0.49 and its correlation with the world's `p_retain` at the same offer is negative. So the optimiser is maximising `p_retain(m) × contribution` over a `p_retain` that carries no ranking information. That is the failure `value_based_renewal`'s own docstring names: "if that model is noise, the grid search maximises noise". **The candidate is the PB6 re-centring already on origin**: `f9b04ddc7` and `46b78123f`, inside `4380002bd`, which re-centre the engagement prior at no effect and stop booking a no-account lookup as direct debit. Both move exactly this estimate, and neither is in the pin `a322166cc`.

**What I cannot say.**
1. Whether PB6 fixes the **ranking** or only the **level**. A re-centred prior moves the mean belief (0.629 against the world's 0.683). A negative correlation is a ranking defect, and a re-centring need not touch it. The one-variable test is the bridge this record already owes: the same six rolls at origin, with the pin as control. This section runs nothing and does not launch it.
2. How the estimate's own price slope compares with the world's. The artefact carries only `p_retain(m*)`, not the curve. The world's paired response averages −0.00102 per £/MWh, but it is very uneven: on 61002, C5's `p_retain` falls from 0.510 to 0.065 on +£22.75. Whether the company's curve is too flat for the customers who react that way is a second candidate, and it is not measured here.
3. Why 0098 is a V win on retention (a £12.50 margin kept them) and still a −£5,984 loss. That is a credit/arrears question, not a churn one. It stays excluded, as before.

**What the next build should be.** Before anyone builds on the grade, re-read the retention estimate's discrimination at origin (after PB6). The AUC and the belief-against-world correlation above are the reading to beat, and the artefact's `scored_decisions` already carries them, so this needs a bridge run and no new instrument. The book-varying design stays the director's (EP17). Nothing here writes `varied_population_draw_activation.json`.
