**Severity:** ADVISORY · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Result: the world-D value arms retaken at the belief commit, arms and floor graded, pointers moved

**Claim:** `grade-the-value-arms-retake-once-both-artefacts-exist`. Grades
`SEAT_PREREG_THE_VALUE_ARMS_RETAKEN_AT_THE_BELIEF_COMMIT_2026-10-02.md`. Written 2026-10-02 ~19:45Z.

## What ran, and what did not

- The pin is `0cc052102` ("the churn belief reads the offer's gap to the published default"). It
  reached origin at 15:20Z. The three-arm ran there and exited **rc=0** at 17:16Z with an 8.47 GB
  peak, writing `/var/tmp/se-retake-belief/value_cycle_ab_s1_three_arm_20261002c.json`.
- **The noise floor was REFUSED** by `run_value_cycle_ab`'s own headroom check at 17:16Z, so the
  unit exited **88**. The floor needed 33,600 MB and the guest could offer 19,677 MB, because two
  legs of `longjob-depth-vs-width` were co-resident. The unit's `resource_headroom.admit` had
  admitted the floor on the *declared budget*, while the tool's check counts *running floor legs at
  their measured peak*. Those two gates disagree whenever another lane is mid-floor. That is not a
  defect, because the inner check is the stricter and correct one, but the unit only learns the
  answer after it has been admitted.
- The refusal artefact has been kept as
  `value_cycle_ab_s1_noise_floor_20261002c.REFUSED_1716Z.json`. It was moved aside so that
  `run.sh`'s `-s` skip does not read it as a finished floor.
- **Relaunched with the cause fixed (serialised behind the co-resident job):**
  `longjob-value-arms-retake-at-the-belief-floor` waits on pid 825465. That pid is
  `longjob-depth-vs-width-w125b`, with three serial seed-pair legs, the first started 19:14Z. The
  relaunch then re-runs the same `run.sh`, which skips the existing worktree and three-arm and runs
  only the 11111/22222/33333 `--redraw-mode all` floor at the same pin. Expect it in the early
  hours of 2026-10-03.

## Grades (three-arm only; Q1's seed-for-seed leg and Q3 wait for the floor)

| | 1002b (`f18e8b5dc`) | 1002c (`0cc052102`) |
|---|---|---|
| level used (value arm's median margin) | £49.2/MWh | **£60.0/MWh** |
| control net | £85,910 | £88,408 |
| whole advantage | +£14,856 | **+£11,493** |
| level leg | +£15,115 | **+£15,701** |
| selection | −£259 | **−£4,208** |
| renewals priced, value / level arm | 95 / 92 | 116 / 111 |
| declined renewals (no lawful predictable offer) | 1 | 2 |
| PROS-2016-0098's share of selection | −£5,613 | −£8,136 |

- **Q0: recorded, and the prediction is REFUTED.** `producing_commit` is the pin, `0cc052102`, so
  that half holds. The world digest is **unchanged at `cf823b185f8ca51c`** (homes `35f8efe8ff02f245`).
  The pre-registration predicted it would differ. It cannot differ: the digest identifies the
  departure-level anchors and the home stock, and `DECLINE_A_FIX_ABOVE_THE_DEFAULT` is a behaviour
  switch that changes neither. **Finding:** two runs sharing this digest are NOT the same world
  when a behaviour switch differs between them. The digest's own `what_this_does_not_cover` names
  the homes and does not name behaviour switches. The pin, not the digest, is what separates
  1002b from 1002c.
- **Q1: the bold part is REFUTED on the arms alone.** The level leg is +£15,701. That is above the
  1002b floor minimum of £12,400 and above 1002b's own +£15,115. It did not fall. This is
  refutation shape (a): the refusals did not bind on the level arm's margin. **Confound I did not
  pre-register:** the level itself moved from £49.2 to £60.0/MWh, because it is the value arm's own
  median margin, and the belief changed what the value arm charges. So the level arm is not the
  same arm across the two runs. Level-arm gross margin rose by £18.3k while its bad debt fell
  £0.8k. The seed-for-seed leg is graded when the floor exists.
- **Q2: HOLDS.** The whole advantage is +£11,493, positive and smaller than 1002b's, as predicted.
  It is smaller because selection fell, not because the level leg fell. That is the opposite of
  the mechanism the pre-registration gave.
- **Q3: pending (the floor).** The single-world selection, −£4,208, is worse than 1002b's −£259.
  One account, PROS-2016-0098, carries −£8,136 of it, which is 193% of the total. In 1002b it
  carried −£5,613 of −£259. Without that account, selection is positive in both runs. Whatever the
  floor shows, the selection reading is dominated by one account's level-arm vs value-arm
  difference, and a seed mean will average that rather than explain it. That account is the next
  thing to read: what the value arm priced it at against the level arm, and whether it churned in
  one arm and not the other.
- **Read, same turn. PROS-2016-0098 is a bad-debt account, not a pricing outcome.** All three
  arms used the same 2017-03-23 roll of 0.3763.
  - At the flat £60 level, the 2017 renewal's retention probability was 0.064. The account churned
    at once with £325 net and no write-off.
  - The value arm priced the account at an £11.5 margin. It stayed, was billed 69 times and wrote
    off £11,241 at close, for −£7,811 net.
  - The control arm kept it to 2021 and wrote off £8,660, for −£5,950 net.

  So "selection" here is the level arm pricing a future write-off out of the book by accident. The
  churn belief cannot see credit risk, so the value arm cannot select on it. A seed mean over
  this will read as the value arm choosing badly, and that is the wrong cause. The selection
  verdict should be read with and without arrears write-offs before anyone calls its sign.

## Not done yet, deliberately

The artefacts have not been copied into `docs/observability/`, and the `CURRENT_WORLD_*_PATH`
pointers have not been moved. They move together as one world, and publishing the 1002c arms
against the 1002b floor would bound a figure from one world with a spread from another. That step
belongs to whoever grades the floor.

## Floor status, 2026-10-02 20:40Z: WAITING, not relaunched

The floor (11111/22222/33333, `--redraw-mode all`, pin 0cc052102) has not run and has not refused
a second time. `longjob-value-arms-retake-at-the-belief-floor` waited for w125b and found it gone.
Its `run.sh` then reached `admit_and_run.py noise_floor` (pid 1146451) at 20:32Z, and that has been
DEFERRED since then by `resource_headroom.admit`. The reason: depth-vs-width relaunched as
`longjob-depth-vs-width-w125c-20261002` with 14,500 MB declared, and 14,900 + 11,200 is more than
the 23,008 MB budget.

The draw expected a second refusal, "the same collision". That will not happen through this route.
The gate that now holds the floor is the memory ledger, not a unit name or a pid. It follows any
declared long job whatever it is called. w125c's three width pairs run serially inside one unit,
so its declaration stays in place between legs and nothing can interleave. A floor leg's own
headroom check would still refuse (exit 88) if an UNDECLARED `run_value_cycle_ab` were resident
when it is admitted. That fails closed, and `longjob-value-arms-1002c-floor-handoff` (waiting on
pid 886397) hands the grading on, or the relaunch if it refused, as soon as the unit exits.

A relaunch keyed to `pgrep` would do no better here. It would also orphan that handoff waiter. So I
left it alone. The admission deadline is 2026-10-04 02:12Z. w125c started at 20:21Z with three
full-window 1.25x pairs. Depth pairs took about 2h each, so w125c should take 7 to 10h. Then the
floor runs about 3 x 53 min. So the floor should land around 06:00 to 10:00Z on 2026-10-03, well
inside the deadline. Q1 seed leg, Q3 and the -£3,499 re-ask are graded by the handed-off item. The
pointers still stay at 1002b until then.

## Floor status, 2026-10-03 00:00Z: RUNNING. It took the first width-pair boundary

Claim `the-1002c-floor-runs-at-the-first-width-pair-boundary`.

- w125c's first pair (`width125_61001_61002.json`, 958 KB) exited rc=0 at 23:53:21Z, with a 13.4 GB
  peak. That was 3h32m for a 1.25x full-window pair, and seed 61001 alone took 6,195 s. The
  unit had started pair two (61003,61004) in the same second. `systemctl --user stop
  longjob-depth-vs-width-w125c-20261002` killed it within seconds. No pair-two artefact
  exists, so `legs_dw.sh`'s `-s` skip re-runs that pair whole.
- At 23:54:36Z the serialised floor unit found no resident leg. It was admitted at 11,200 MB,
  and `run_value_cycle_ab --level-arm --noise-floor-seeds 11111,22222,33333 --redraw-mode all`
  is resident at pin `0cc052102` (pid 1933972). **If it is still resident at the next
  orientation, it is RUNNING. Do not relaunch it.** `longjob-value-arms-1002c-floor-handoff-2`
  still waits on the unit and hands the grading on when it exits.
- Depth-vs-width was relaunched as `longjob-depth-vs-width-w125d-20261003`, with the same
  `legs_dw.sh` and log `legs_dw_w4.log`. **The first launch failed in under a second.** The
  preamble asked `wait_for` for a 43,200 s deadline, and `wait_for` refuses anything above its
  21,600 s ceiling. In this case `legs_dw.sh` would have printed `REFUSED: wait on <pid>` and
  exited 91 before running any leg. So the unit would have died the moment it had to queue
  behind something, which is the only job its preamble has. It was never exercised before,
  because w125c launched onto an empty box. The preamble now re-asks twice for 21,600 s per
  resident leg, and w125d is waiting on pid 1933972.

### Pre-registered before the floor's answer: selection without write-offs (792fcf31d's split)

The 2026-10-02 pre-registration does not cover the split, so it is registered here. The
reference points are: the 1002b floor's churn-pricing part, which is +7,446 / +6,352 / −1 (mean
+4,599), and the 1002c arms run's +5,475.

- **S1.** On every 1002c floor seed, PROS-2016-0098 is the only account whose selection changes
  sign when write-offs are removed, as it was on all three 1002b seeds and in both arms runs.
- **S2.** With write-offs, selection is negative on all three seeds. Q3's "not all on one side
  of zero" is therefore predicted REFUTED. The credit part on each seed is within £1,000 of the
  arms run's −£9,683, because 0098 sits in the held book and every redraw reaches it the same
  way.
- **S3.** Without write-offs, the seed mean is positive, between +£2,000 and +£8,000. At least
  one seed is under +£1,000, as 33333 was in 1002b, so n = 3 still cannot call its sign.

## The floor, graded 2026-10-03 (claim `grade-the-1002c-floor-and-move-the-current-world-pointers`)

The serialised floor exited **rc=0** at 02:53:15Z with an 8.48 GB peak. It wrote
`value_cycle_ab_s1_noise_floor_20261002c.json` at `0cc052102`, on seeds 11111/22222/33333 with
`--redraw-mode all`, and it carries no `floor_run_refused`. The world digest is `cf823b185f8ca51c`,
as in the arms run.

| seed | level leg 1002b → **1002c** | selection 1002b → **1002c** | 1002c churn-pricing part | 1002c credit part |
|---|---|---|---|---|
| 11111 | £14,607 → **£15,332** | −£404 → **−£4,208** | +£5,475 | −£9,683 |
| 22222 | £12,400 → **£13,964** | −£1,314 → **−£2,470** | +£7,444 | −£9,915 |
| 33333 | £19,728 → **£15,322** | −£7,542 → **−£5,551** | +£4,342 | −£9,892 |
| mean | £15,578 → £14,873 | −£3,087 → **−£4,076** (SEM £892, 4.57 SEMs from zero against a 4.30 bar) | **+£5,754** | −£9,830 |

The split method is 792fcf31d's: each arm's arrears lines reconcile to its net on all 124
accounts. Re-run over the 1002b floor, the script reproduces that record's +7,446 / +6,352 / −1,
so the instrument is the same one.

- **Q1, seed-for-seed leg: REFUTED.** The level leg rose on 11111 and 22222 and fell only on
  33333. The 1002c floor's minimum is £13,964, which is above the 1002b minimum of £12,400. Together
  with the arms-run grade above, the level leg did not fall out of the old band on any reading.
  This is refutation shape (a). As recorded above, the level itself moved from about £49 to
  £60/MWh, so the level arm is not the same arm across the two commits.
- **Q3: REFUTED on both halves.** The seed mean, −£4,076, is below −£3,087, not above it. All three
  seeds are on the same side of zero. This is refutation shape (b), but the split shows it is not
  the belief choosing worse. On the churn-pricing part the 1002c seed mean (+£5,754) is ABOVE
  1002b's (+£4,599). The fall in published selection comes from the credit part, −£9,830 against
  about −£7,690, and that is PROS-2016-0098's write-off growing.
- **S1: HOLDS.** On every seed, PROS-2016-0098 is the only account that changes sign when
  write-offs are removed. Its selection is −£8,136 with write-offs and +£1,756 without, on all three
  seeds. The elasticity redraw does not reach it.
- **S2: HOLDS.** With write-offs, selection is negative on all three seeds. Each seed's credit part
  is within £232 of the arms run's −£9,683.
- **S3: the mean HOLDS and the weak-seed clause is REFUTED.** Without write-offs, the seed mean is
  +£5,754, inside the predicted +£2,000 to +£8,000. But no seed is under +£1,000; the lowest is
  +£4,342. The churn-pricing part is positive on every draw.

**What the floor licenses.** By the generator's own bar, the published selection leg now has a
negative sign (4.57 SEMs against 4.30). That sign belongs to one household's bad debt. The value
arm cannot see arrears (`SEAT_FINDING_THE_VALUE_ARM_CANNOT_SEE_ARREARS_..._2026-10-02.md`), and the
flat level priced that household away by accident. On churn pricing, the per-customer arm beats
the flat level on all three draws. Until the page publishes the churn/credit split per leg, any
signed selection verdict reads as the wrong cause. The page names this in words beside the figures
(`changed_since_the_last_reading`).

## Pointers moved, and the reading is withdrawn by mechanism

Both 20261002c artefacts are now in `docs/observability/`. `CURRENT_WORLD_THREE_ARM_PATH` and
`CURRENT_WORLD_NOISE_FLOOR_PATH` move onto them together. The page now names the four changes since
`f18e8b5dc` (757c8cada, 822218441, 28eb35ec7 and the belief at 0cc052102) and the write-off cause,
in a feed field that Capabilities renders. That field carries no figure, so it cannot disagree with
the feed.

**`is_heads_code` reads False at publish (step 5 of the pre-registration).** Ten
`simulation/`/`company/` paths moved after the pin. They include `value_based_renewal.py`,
`renewal_rate_chain.py`, `arrears_engine.py` and `payment_observation_consumer.py`, which is the
arrears forward landing. So the page publishes the 1002c figures and withdraws both the currency
claim and the verdict, and this is fail-closed as intended. **A retake at a HEAD that contains the
arrears forward is the next honest reading.** That retake is the one that can show whether seeing
arrears closes the credit part.

Two controls were keyed to the live pointers and needed one leg to withhold. Both are now pinned to
the dated 1002b pair, the way `earlier` was already pinned:
`site/test_the_baseline_comparison_reaches_the_reader.py::_feed_whose_current_world_block_speaks`
(the mirror's poison round is a no-op when both legs resolve) and
`tests/tools/test_generate_value_arms_data.py::test_the_creation_leg_carries_its_own_live_world_bound_and_not_the_advantages`.

## The split is on the page (2026-10-03, claim `publish-selection-split-into-churn-pricing-and-credit`)

`tools/generate_value_arms_data.py::_selection_split` publishes `current_world.selection_split`
from the current-world floor, per seed. It uses the method above: per account and arm, churn
pricing is `pre_4c_net + placeholder_bad_debt_released`, and credit is net minus that. It refuses,
naming the seed, if the two parts do not rebuild that seed's `selection_gbp` to the penny, if an
arm's lines do not reconcile, or if the floor is from another world. Capabilities renders it under
the re-draw band (`#arms-redraw`). Reading at 1002c, reproduced exactly from the table above:
churn pricing +£5,753.65 (sem £906.41, 6.3 sems against the 4.30 bar), credit −£9,829.96 (sem
£73.70). PROS-2016-0098 holds 99.8% to 102.2% of the credit part on every draw. The split
inherits the floor's code withdrawal: its signs are shown with the same "verdict withdrawn for
which code drew the bound" line as the legs. Door:
`site/test_the_baseline_comparison_reaches_the_reader.py::test_the_selection_legs_two_parts_reach_the_reader_on_every_draw`.
Dropping the credit column from the door reds it and the partition rung, both checked with the change staged.

**Still stale, and not fixed here:** `selection_leg.root_cause.statement` (from the 2026-09-27
record) still says the residual is a coin flip on whether 0098 crosses its roll, with the level
arm keeping it on one seed. At 1002c the level arm churns it on every seed, and the credit part is
nearly constant across draws. The split is now the accurate reading, and the two sit side by side on
the page. Rewriting or withdrawing `_SELECTION_SWITCH` is the next item for the seat to rank.
