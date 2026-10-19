# Pre-registration: the decision probe writes a dual household's gas leg, and C35 per household merges

**Written 2026-10-19 ~15:40 BST, before any probe was run on the changed code.** Claim
`the-decision-probe-writes-a-dual-households-gas-leg-at-its-electricity-roll` (Lane 0, seat). Starts
from N3 of `SEAT_PREREG_SWITCHING_NBA_PER_HOUSEHOLD_ON_THE_STANDING_POLICY_CHANGES_NO_DECISION_IN_ANY_RUN_2026-10-19.md`
and the finding
`docs/staging/SEAT_FINDING_THE_DECISION_PROBE_SEES_A_DUAL_HOUSEHOLD_ONLY_THROUGH_ITS_ELECTRICITY_LEG_SO_C35_PER_HOUSEHOLD_MERGES_NOTHING_2026-10-19.md`.

## What the change is, and one correction to the item

**The item's mechanism is wrong in one detail.** It says to emit the gas leg at the electricity roll
"from the offer the probe already holds". The probe does not hold one at that point. The run pops
terms from a heap ordered `(term_start, cid)`, and `X` sorts before `Xg`, so a dual household's gas
leg is priced *after* its electricity roll (`simulation/run_phase2b.py`, the riding-leg comment at
the `commodity != _decision_leg` branch). So the change works the other way round. The electricity
roll records its row and the household's own records. When the same billing account's gas leg is
priced on the same term start, the probe writes that leg's row there (`riding_leg_row`), marked
`rides_on`, with:

- its own offers under every rule, its base, and its annual MWh from the household's records;
- its own stayer's bill, because the world's decline-a-fix rule does reach the riding leg;
- the world's P(stay) **copied from the electricity row it rides on.** That is the world's own rule:
  the household's departure is drawn once, on electricity, at that leg's offer.

`retention_rise_count` reads the gas default from the company's own door
(`published_default_rate_ex_vat`), so the row does not need to carry it.

**What this cannot do (stated before measuring).** A household that leaves at its electricity roll
never has its gas leg priced, because the run skips a churned household's other leg at the top of
the loop. So that leg gets no row. The probe cannot price it without rebuilding the run's gas-term
state, which would be an invented offer. **So the per-household reading covers dual households that
stayed on the reference path, not all dual households.** C35 targets households at risk of
leaving, so this is a selection the reading must state, not a footnote. At `8b6fea024`, the publish
run's `account_state_log` against the old probe's rows gives 77 of the 129 dual electricity rows a
gas term on the same start (39 fixed, 38 SVT), and all 77 renewed. The other 52 churned.

The probe's printed scores (`score_value_vs_flat` and the rest) stay over the rolled legs only, so
they are comparable with every earlier probe. The riding legs are in `rows` and are counted in
`riding_legs`.

## Predictions, for one probe at the landing sha (default book, no `--world`)

The base has moved past `8b6fea024`. It now includes the B7 sole-occupant death exits and other
commits, so electricity rows are predicted as a range, not to the digit.

- **G1. Riding gas rows: 55 to 95.** Every one is `commodity == "gas"`, with a `rides_on` that equals
  its billing account's electricity row on the same `term_start`. **0** riding rows belong to a
  household whose electricity roll that date was a departure (by construction).
- **G2. Rolled rows: 165 to 200**, of which 4 or fewer are gas (founders' gas-only legs, as before).
- **G3. `retention_rise_count`, off:** decisions = all rows. **On (`--per-household`):** decisions =
  all rows − riding rows, exactly. Every riding row merges with its electricity row and nothing else
  merges. If this identity fails, the probe or the grouping is wrong, and nothing below is read.
- **G4. On ≤ off in rescued count**, because a pair that is two cases off is one case on.
- **G5. On the paired households only** (same set both ways), "needs no rise" is at least as large
  on as off per household. The merged state has the summed margin, so a hazard cut is worth more
  against a give-up taken once. Refusals for a rise above the headroom fall on as against off on the
  electricity legs of those households. Confidence is moderate. A refutation here would mean the
  gas default's headroom is smaller than the margin it adds.
- **G6. The C34 floor still refuses at least 95% of cases, off and on.** Nothing here changes the
  floor's shape.
- **G7. Pre-2019 rows ("no default") are unchanged in kind.** Riding rows dated before 2019 refuse
  on "no default", as their electricity rows do.

**What would refute the mechanism.** G1 at 0 would mean gas terms do not start on their electricity
leg's date at HEAD. G3 failing would mean the merge key, `(billing_account, term_start)`, is not what
the probe writes.

## Grade

*(filled after the run, beside the predictions, without revising them)*

**Not yet gradable (17:15 BST, worker).** The first full probe on the changed code (`/var/tmp/gasleg`)
never finished. It was a child of the 16:05 seat turn, and it died with that turn when
`seat-executor.service` exited at 16:49. Its log stops at 2020-04-07 and it wrote no `probe.json`.
It was relaunched at 17:12 BST as the systemd unit `longjob-gasleg-probe-2fe180d52`, so it now
survives its launcher. It runs in a clean worktree at origin/main `2fe180d52`, which contains
`608c0d0fa`, on the default book. Output goes to `/var/tmp/se-gasleg-grade-out/probe.json`. The
last full probe took 3 h at a 3.6 GB peak, so expect it around 20:15–20:45 BST. To grade, run
`cd /var/tmp/se-gasleg-grade && python3 /var/tmp/se-gasleg-grade-out/grade.py
/home/rich/synthetic-enterprise/docs/reports/run_output_ad8afadc5_20261019T132751Z.json`, then read G1–G7 against its lines. The predictions above are unchanged.

**Graded 2026-10-19 ~21:30 BST (worker).** The unit `longjob-gasleg-probe-2fe180d52` finished at
20:20 BST. It ran for 3 h 8 min with a 5.9 GB peak, against the 3.6 GB the last probe used. It
wrote `probe.json`. The grading worktree had been reaped, so it was re-created at `2fe180d52`.
`grade.py` was then run as written, against `run_output_ad8afadc5_20261019T132751Z.json`. A second
script (`/tmp/gasleg_extra.py`) made the per-leg splits that G1, G5 and G7 need.

- **G1 (riding gas rows 55–95, all gas, each riding its own electricity roll): HELD.** There are 75
  riding rows, all gas. All 75 have a `rides_on` equal to the `customer_id` of an electricity roll
  on the same billing account and `term_start`, and 0 ride without that roll. The "0 on a departure"
  leg is **by construction, not measured.** The probe row does not carry the reference path's
  departure, and I did not join it to `account_state_log`.
- **G2 (rolled 165–200, ≤4 gas): WRONG by one on gas.** There are 182 rolled rows, inside the
  range: 177 electricity and **5 gas**. I did not check which account the fifth gas-only roll is.
- **G3 (off decisions = rows, on = rows − riding, exactly): HELD.** Off gives 257 = 257. On gives
  182 = 257 − 75, the same on both hazard ends. Every riding row merged with its roll, and nothing
  else merged. The two partitions add up: 193+420+151+4+3 = 771 = 3×257, and 142+294+105+5 = 546 =
  3×182.
- **G4 (rescued on ≤ off): HELD.** On is 142 and off is 193, at both hazard ends.
- **G5 (paired households: "needs no rise" on ≥ off; headroom refusals on < off on the electricity
  legs): HELD, narrowly.** Over the 75 paired households (full window; the cut year is the same):
  - "needs no rise": 2 on, against 1 off across both legs and 0 off on the electricity legs alone.
  - Refusals at or above the headroom (`the rise our side needs` + `no rise within the headroom`):
    35 on, against 37 off on the electricity legs alone. The gas legs alone have 47.
  - **Rescued on per household is 62/225, exactly what the electricity legs alone rescued off
    (62/225).** The gas legs alone rescue 51/225. Merging adds no rescues beyond the electricity
    leg on this book. I cannot yet say whether it is the same 62 cases.
- **G6 (C34's floor refuses ≥95%, off and on): HELD.** I used the same arithmetic as J1 in
  `SEAT_PREREG_B11_C35_C34_ON_THE_FIRST_PUBLISHED_DUAL_FUEL_RUN_2026-10-18.md`: cases − needs no
  rise − no rise within the headroom. Off: 771 − 4 − 3 = 764/771 = 99.1%. On: 546 − 5 − 0 = 541/546
  = 99.1%. That is the record's formula, not a run of the C34 caller.
- **G7 (pre-2019 riding rows refuse on "no default", as their electricity rows do): HELD.** 42 of
  the 75 riding rows date before 2019. All 42 have no published gas default, and all 42 of their
  electricity rolls have no electricity default. All 33 riding rows from 2019 on have a gas default.

**Per-household reading.** It covers only dual households that stayed through the electricity roll.
The 52-of-129 share that left at the roll at `8b6fea024` has no gas row, as stated above. C35
rescues 142/546 (26.0%) of cases on and 193/771 (25.0%) off, at both hazard ends. Off is over
257 rows. On is over 182 decisions, which is 75 households, each counted once.
`next_best_action_decides_per_household` is now gradable. On this book it changes the count of
decisions, not the rate at which a decision is rescued.
