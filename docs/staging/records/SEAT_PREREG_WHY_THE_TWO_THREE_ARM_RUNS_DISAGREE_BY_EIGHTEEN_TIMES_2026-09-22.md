**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION — why the two three-arm runs in world `39a192ce04c1eda8` disagree by eighteen times

**Filed:** 2026-09-22, before the verifying measurement, under Lane 0 delivery
`the-arms-page-cannot-say-whether-the-advantage-is-choosing-or-the-price-level`.

PRE-REGISTRATION, 2026-09-22, before the verifying measurement.

WHAT I HAVE ALREADY SEEN (declared, so it is not claimed as predicted):
  level_vs_selection on the two runs, both from columns already on disk.
  0908: value_adv 17738.64 = level_adv 17468.44 + selection 270.21; level_gbp_per_mwh 20.0
  0918: value_adv  4579.23 = level_adv   252.21 + selection 4327.01; level_gbp_per_mwh 41.0
  level_arm_net: 157608.98 -> 158059.09 (+0.29%)
  By subtraction only (NOT yet read from the artefacts' own control fields),
  control_arm net: ~140140.54 -> ~157806.88 (+12.6%).

WHAT I DO NOT KNOW AND AM PREDICTING:

P1. The artefacts' own control-arm net figures will confirm the subtraction:
    control net rose ~12-13% between the runs while level-arm net moved <1%.
    PREDICT: CONFIRMED.

P2. Therefore the 18x share disagreement is carried by the CONTROL (do-nothing)
    arm, not by either priced arm. PREDICT: the level leg's 69x collapse is
    >90% attributable to the control arm's rise, <10% to the level arm.

P3. The level constant's move 20 -> 41 GBP/MWh is NOT the cause of the level
    leg's collapse, and points the WRONG WAY: a higher flat margin should raise
    the level arm's net, and the level arm's net did rise slightly.
    PREDICT: the level constant is a passenger, not a driver.

P4. (the one that decides whether the item's remedy works) The level constant is
    derived WITHIN each run from the value arm's own realised median margin
    (`level_source` says so). If that is right, re-running "at ONE commit over
    ONE book" does NOT fix the comparison, because the level arm's price level is
    re-derived from whatever the value arm does in that run -- it is endogenous,
    and it is a FOURTH mover the drawn item does not name (it names book, commit,
    arm code). PREDICT: endogenous, confirmed by reading the derivation.

P5. Seed families: no floor artefact on disk carries the 0918 arms' producing
    commit b329e702b7. PREDICT: confirmed -- so no same-commit bound for the
    fixed-population run exists today, and the page's error bar cannot be taken
    on the same commit as the figure it bounds without a new run.

IF P1-P4 HOLD, the drawn item's stated remedy is insufficient and its diagnosis
incomplete, and that is the finding -- not the re-run.
