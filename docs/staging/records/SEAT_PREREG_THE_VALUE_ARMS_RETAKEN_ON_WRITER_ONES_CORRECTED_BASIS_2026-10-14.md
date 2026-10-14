**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout`

# The value arms re-taken on writer 1's corrected basis: pre-registration, written before any leg ran

*2026-10-14, worker (direction `the-save-stayers-fix-runs-on-a-freed-box-and-lands-on-its-one-variable-evidence`, step 1).
This supersedes the floor legs of `docs/staging/records/SEAT_PREREG_THE_VALUE_ARMS_RETAKEN_ON_THE_TERM_COST_BASE_2026-10-13.md`,
which were stopped ungraded. The reasons are recorded at the end of that file.*

## Premise

- The `t` floor legs ran at `05f9f3347`, which lacks `87e9f4245` (writer 1's unit-rate margin basis and the
  save's one floor). Any floor taken there grades a writer 1 basis that has already been replaced.
- Leg 1 of `t` (`value_cycle_ab_s1_three_arm_20261013t.json`) is graded. It stays a reading at `05f9f3347`
  and is not re-used as the partner of a floor taken on a different base.
- **Do not start before the stayers control has read.** While line 76 of
  `tests/simulation/test_a_save_is_not_paid_for_by_the_stayers.py` is red, every save figure is
  unreadable against the director's 2026-10-08 condition. If the rival-ledger fix (`simulation/run_phase2b.py`)
  lands, pin at or after that commit as well.

## What runs, priced at the measured rate

The worktree is pinned at origin, at or after `87e9f4245` (and the stayers fix, if it landed). One book pass
on the 400-founder book costs about **4.2 h**. That is measured: floor a ran three passes in 12 h 58 min.
A floor seed is **three** passes, because `noise_floor` runs `run_value_cycle_ab(level_arm=True)`. The
`t` file priced a floor leg at 3.7 h, and it was 25 h.

| leg | passes | expect |
|---|---:|---:|
| 1 `--level-arm` | 3 | ~6 h (`t` leg 1 took 5 h 44 min, about 1.9 h per pass. Floor passes ran at 4.2 h beside other resident jobs and with a patched draw. Which rate holds is not established) |
| floor, 2 seeds per leg (the floor refuses one) | 6 per leg | ~25 h per leg |

The four-seed floor is about 50 h of box time, and each pass peaks at about 11.2 GB, so legs run serially.
**Before launching, decide whether the four-seed floor is worth 50 h** against what else needs the box.
If not, the smallest run that answers T6 is one two-seed leg. That is honest about n=2, and it says so
on the page. Each leg is its own `launch_long_job` unit with `--expect-minutes` priced from this table,
not from the `t` file.

## Predictions (against `t` leg 1 where one exists)

| # | quantity | prediction | confidence |
|---|---|---|---|
| U1 | `value_advantage_gbp` in leg 1 | stays positive (t: 4,652) | 0.60 |
| U2 | value-arm realised median `level_gbp_per_mwh` | within £5/MWh of t's 57.00 | 0.55 |
| U3 | folded floor `selection_gbp` mean | positive, and `selection_distinguishable_from_zero` true | 0.50 |
| U4 | folded floor `selection_gbp` sd | above `r`'s 1,770. The book is 2.8x larger | 0.65 |

U1 and U2 are below the `t` file's confidence. `87e9f4245` moves writer 1's target, and the realised
fixed-term margin it learns from still reads high (median 8.5% against 1.67%, `f6e806b8f`).

## What done means

The legs run and are graded beside U1-U4. The page pair in `tools/generate_value_arms_data.py` moves
only when a floor is graded on the same base as its leg 1.

## Decision on the floor's size, written 2026-10-14 16:20 BST before any leg launched

*Delivery seat, drawn item `retake-the-value-arms-on-writer-ones-corrected-basis`.*

**Not launched yet.** At 16:14 both `longjob-stayers-fix-one-variable` (the stayers pytest) and
`longjob-stayers-probe-and-bisect` (origin probe, then a first-parent bisect `ed9aa25eb..55701bb84`)
were active. The box is theirs, and the pin depends on whether the fix lands. The launch is handed on.

**One two-seed floor leg, not four seeds.** R5 says to run the smallest thing that answers the question.
U3 asks whether the folded `selection_gbp` mean is positive and distinguishable from zero. A two-seed leg
gives that answer at n=2, and the page says it is n=2. A 50 h four-seed floor would hold the box for more
than two days, which is a large bet on a basis whose leg 1 has not read yet. The second leg is decided now,
by this rule, before the first result is known:
- **if** leg A grades `selection_distinguishable_from_zero` **false**, or its mean's sign is the opposite
  of U1's leg-1 sign, run leg B (seeds disjoint from A's) and grade the four seeds folded;
- **otherwise**, stop at n=2 and publish the pair with its n=2 bound.

**Order and pricing** (from the table above, priced at the slow rate, because under-pricing is the fatal
direction): leg 1 `--level-arm` `--expect-minutes 760` (3 passes x 4.2 h), then floor leg A
`--expect-minutes 1520` (6 passes x 4.2 h). Serial: each pass peaks at about 11.2 GB. If leg 1 runs at
t's 1.9 h per pass, record the measured rate and re-price leg A from it before launching.
