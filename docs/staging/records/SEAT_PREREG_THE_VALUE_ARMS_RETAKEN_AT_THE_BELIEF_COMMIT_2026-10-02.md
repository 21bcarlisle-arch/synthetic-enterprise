**Severity:** ADVISORY · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Pre-registration: the world-D value arms retaken at the commit that lands the belief

**Claim:** `retake-the-value-arms-in-a-world-that-can-refuse`. **Written 2026-10-02, and the unit was launched at
14:54:58Z, before the pin exists.** The belief (`company/crm/churn_model.py` reads the offer against the published
default, `reference_rate_gbp_per_mwh`) is **not on origin/main yet**. `git grep` over `company/`
finds no such name. Claim `land-the-belief-reads-the-published-default-now-the-flip-is-on` is
landing it now from an isolated worktree. So the run cannot start yet, and it is not started by
hand.

## The unit

`longjob-value-arms-retake-at-the-belief` runs `/var/tmp/se-retake-belief/run.sh`:

1. It polls origin every 5 min. The pin is the origin commit that introduces
   `reference_rate_gbp_per_mwh` into `churn_model.py`. That is the same commit the belief lane is
   told to run its paired runs on.
2. It allows a 20-minute grace. The belief lane's own capped/uncapped runs grade P1–P4 of
   `SEAT_FINDING_THE_VALUE_ARMS_CHURN_BELIEF_..._2026-10-02.md`. They are that lane's DONE, so they
   get the box first.
3. It runs from a locked detached worktree `/var/tmp/se-retake-belief/wt` at the pin. It refuses if
   the worktree's HEAD is not the pin or if the pin lacks the belief.
4. It runs the 20261002b pair's two commands serially. The floor starts only when the arms exit
   0 with an artefact:
   - `run_value_cycle_ab --level-arm --out …/value_cycle_ab_s1_three_arm_20261002c.json`
   - `run_value_cycle_ab --level-arm --noise-floor-seeds 11111,22222,33333 --redraw-mode all
     --out …/value_cycle_ab_s1_noise_floor_20261002c.json`
5. Each world waits for `resource_headroom.admit` (8,400 MB for the arms, 11,200 MB for the floor,
   both the declared peaks of the 1002b pair). It then holds a `reservation` for its whole life,
   in the shared tree's ledger. The unit itself declares only a waiter's footprint, so a unit
   that is still waiting holds no budget against its neighbours.
6. The deadline is 30 h from launch. Every refusal exits with a named reason (81–88) in
   `/var/tmp/longjob-value-arms-retake-at-the-belief.log`.

**Seeds: 11111/22222/33333, not 61001–61003.** The item says "61001,61002,61003" and also "the
same invocation as the 20261002b pair". Those two instructions contradict each other. The 1002b
floor ran 11111/22222/33333 with `--redraw-mode all`, and 61001–61006 are the depth-vs-width
family, which uses `--redraw-key churn_roll`. A floor on other seeds and another redraw mode would
change two things at once against the spread it is graded against. This run keeps the 1002b
seeds, so each seed can be compared with itself across the two commits.

## What changes against `f18e8b5dc`, all at once

- `757c8cada`: a household that stays declines a fixed renewal above its default. The switch is
  on. In the 1002b world, 55 of 64 above-default fixes could not have been refused.
- `822218441` / `2cfea34b7`: an SVT conversion records a stayed decision on its journey again.
  This is the decline-and-stay splice.
- `28eb35ec7`: the acquisition no-offer rule prices both fuels ex-VAT against the default on the
  day. That changes which prospects are quoted.
- `09555ee17`: the fabric traces are reused across forced home-move legs.
- **The belief**: the churn belief reads the offer over the published default, not over the
  household's own last price.

**Four or more things move together, so no single move is attributable from this pair.** The
belief's own effect is isolated by the belief lane's with/without-diff runs on the same commit,
not by this run. What this run gives is the honest current-world reading the page has lacked
since `28eb35ec7`.

## Predictions

The 1002b reading was: whole advantage +£14,856; level leg +£15,115, floor £14,607 / £12,400 /
£19,728; selection −£259, floor −£404 / −£1,314 / −£7,542 (mean −£3,087). Control net was
£85,910.

- **Q0 (identity, recorded, not a thesis test).** `producing_commit` is the pin. The world digest
  differs from `cf823b185f8ca51c`, because the world's behaviour changed. If it does not differ,
  the digest is blind to `DECLINE_A_FIX_ABOVE_THE_DEFAULT`, and that is a finding.
- **Q1. The level leg falls, and it falls out of the old band.** The three-arm level leg is
  **below £12,400**, the 1002b floor minimum, **and above zero**. It also falls seed-for-seed on
  all three floor seeds. Mechanism: the level arm is the one that prices fixed renewals above the
  default, and a world that can refuse turns those renewals into SVT stays billed at the cap. The
  1002b level leg was partly booked on fixes no real household would have accepted. Held
  moderately. The size is a guess anchored on 55 refusable fixes at a few hundred pounds each, so
  "out of the band" is the bold part.
- **Q2. The whole advantage stays positive** in the three-arm run. It is held more weakly than in
  1002b, because Q1 removes most of what carried it.
- **Q3. Selection moves up but its sign is not resolved.** The floor's seed-mean selection is
  **above −£3,087**, and **the three seeds do not all land on the same side of zero**. The belief
  now ranks on the quantity the world prices, so its anti-ranking (r = −0.12) should weaken.
  n = 3 cannot call a sign, and the page keeps the selection verdict `withheld` whatever this
  shows.
- **Refutation shapes.** (a) If the level leg holds inside or above the 1002b band, the refusals
  did not bind on the level arm's margin. The next question is then where the 55 refused fixes
  went: they may sit in the control arm's book as much as in the level arm's. (b) If selection
  falls further below −£3,087, the belief change hurt choosing, or the decline switch removed the
  accounts the value arm chose well on. This pair cannot separate those two causes. The belief
  lane's paired runs can.

## When it ends

1. Grade Q0–Q3 in `SEAT_RESULT_…` beside this record.
2. Copy both artefacts into `docs/observability/`.
3. Move `CURRENT_WORLD_THREE_ARM_PATH` and `CURRENT_WORLD_NOISE_FLOOR_PATH` onto them.
4. The page names what changed: decline on, the journey decision, `28eb35ec7`, the belief.
5. If `is_heads_code` reads False by publish time, the page withdraws the reading by mechanism,
   as it does now. That is the fail-closed state.
6. If the unit is still running at the next orientation, say so and do not re-launch. `systemctl
   --user status longjob-value-arms-retake-at-the-belief` is the address.
