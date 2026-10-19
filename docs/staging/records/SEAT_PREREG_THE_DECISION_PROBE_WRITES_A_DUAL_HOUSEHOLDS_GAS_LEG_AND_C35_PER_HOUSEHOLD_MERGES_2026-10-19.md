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
