**Severity:** ADVISORY · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Result: the world-D value arms retaken at the belief commit, partial (arms graded, floor pending)

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
