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
