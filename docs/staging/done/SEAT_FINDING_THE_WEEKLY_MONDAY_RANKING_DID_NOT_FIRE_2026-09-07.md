**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — weekly rhythm

# The weekly monday ranking was due 2026-09-07 and has not fired

**Found:** 2026-09-08, by `background.weekly_rhythm` on the daily 07:00 local tick. 1 day(s) late.

The director's instruction of 2026-09-04 made this a finding by construction: *"If a step has not fired when it should have, that is a finding."* The step is not late because anyone forgot — it is late because it was armed, staged, and not done.

Rituals waiting on it: **harness_pruning**.

## The repair

Do the step. `docs/staging/WEEKLY_RHYTHM_MONDAY_RANKING_2026-09-07.md` carries it. Then `python3 -m background.weekly_rhythm --close`, which arms the next step and is the only thing that does.

**Discharged:** when the step is closed, which archives this document to `done/` as well as the step's own. Filed ONCE per due date — the baton records that it was — so a step that stays open does not mint a document a day.
