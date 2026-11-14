**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The shared tree is held behind origin only by the seat's unlanded orientation record (2026-11-14)

*Worker, LANE 0 draw `the-shared-checkout-reaches-origin`.*

**Premise, re-measured 04:00Z.** It holds. The shared tree is 44 behind origin/main and 0 ahead, and it
lacks c29205f25 and 1778f1ce6. The draw counted 33 overlapping paths. By 04:00 there were 38 (dirty
locally AND changed on origin): 19 byte-identical to origin's blob and 19 that differ.

**Done is not reached.** After this landing, `origin_reconcile` is held by 3 paths. All three are the
seat's own orientation record, which the brief leaves to the seat: `docs/direction/DIRECTION.yaml`,
`docs/direction/decisions.jsonl` and `docs/status/SEAT_STRETCH_LOG.md`. Before this work it was held by 9.
The reconciler proves or carries the other 25 itself (twins, the earlier revision of the map, generated
output, untracked drafts, and live edits that merge cleanly).

## The 19 differing paths, one verdict each

Method: a 3-way merge of each local copy (base HEAD, theirs origin/main), the nearest origin revision,
mtimes, and `origin_reconcile`'s own classes (run read-only first, then for real).

**Superseded, preserved and then cleared here: the 13 Nov 06:42–07:23 shared-tree draft of the
director's 13 Nov site steer.** Origin landed the same steer later the same day, in its own form:
`f4f825b8b` (a plain lead, an empty fixes list no longer reads as an empty week, the usage reading moved
to advisor/done), `227872c15` (per household per year, belief skill first) and `aab22df9d` (the
steer archived with its Done section). Where the draft differs, origin chose differently and did not
omit anything:

| path | local vs origin | verdict |
|---|---|---|
| `tools/capabilities_page_figures.py` | draft `_per_year` lead and a per-commit list in the fixes strip; origin has `_per_household_year` and `render_per_household`, and prints the count of model commits | superseded |
| `tests/tools/test_capabilities_page_figures.py` | tests of the draft's lead | superseded with it |
| `tools/generate_capabilities_door.py` | draft `landed_in_window` feed field; origin's field is `commits_to_the_model` | superseded |
| `tools/generate_value_arms_data.py` | draft `_per_household_year` and `_belief_skill`; origin has both (`:17557`, `belief_against_control_outcomes`) | superseded. Carrying it would have defined the function twice |
| `site/data/value_arms.json`, `site/capabilities/index.html` | the draft's render | generated output, superseded |
| `docs/design/capabilities_fixed_this_week.json` | 3 fix rows in the draft's wording; origin added its own 3 for the same fixes | superseded |
| `docs/staging/advisor/done/DIRECTOR_READING_USAGE_62PCT_…_2026-11-13.md` (staged add, plus a third index version) | intermediate archive text; origin's has the actioned section | superseded |
| `docs/staging/advisor/done/DIRECTOR_STEER_THE_SITE_MUST_SAY_PLAINLY_…_2026-11-13.md` (staged add, plus a third index version) | "Progress" section; origin's reads "Done" | superseded |
| `docs/design/LEVEL_DD_AREA_MAP_2026-11-11.md` | +12 lines saying old-credit-netted-at-close "has no holder"; origin moved that subject to `REPAYMENT_POSTING_AREA_MAP_2026-11-14.md` | superseded. Its finding is still open in staging root |

Preserved before clearing. Recovery is `git show <ref>:<path>`, and every path was read back first:

- disk bytes of all 10: `refs/preserved/origin-reconcile-superseded-draft/the-13-nov-capabilities-draft-2026-11-14` (a5756befc6)
- the two staged index blobs (a third version, equal to neither disk nor HEAD):
  `…-2026-11-14-staged-DIRECTOR_READING_USAGE_62PCT_FRIDAY_0600` (blob d8f57b8f2) and
  `…-2026-11-14-staged-DIRECTOR_STEER_THE_SITE_MUST_SAY_PLAINLY` (blob ce80ff53f)

The tracked files took HEAD's bytes, and the two staged adds left the index and the disk. The
fast-forward installs origin's copies. Their staged deletions of the advisor root copies match origin,
which deletes them too.

**Superseded; the reconciler clears these itself. Nothing was done by hand:**

- `docs/design/maturity_map.yaml`: byte-equal to origin's 98ba0292e, an earlier origin revision.
- `docs/staging/records/SEAT_RECORD_WHAT_THE_INSULATION_CHANGE_CAN_MOVE_…_2026-11-13.md` (untracked): equal to 83991f5fe, before the A/B table was filled.
- `docs/staging/done/SEAT_FINDING_THE_WEEKLY_MONDAY_RANKING_DID_NOT_FIRE_2026-10-19.md` and `…TWO_DUAL_FUEL_MOVER_TESTS_RED_…_2026-11-02.md` (untracked): origin's copies are these plus their Done sections.
- `docs/staging/SEAT_FINDING_THE_CRISIS_BAD_DEBT_CONTROL_…_2026-10-14.md`: archived here into done/ (that copy equals HEAD's root blob), while origin's f3d88c1fe5 added a 13 Nov section that keeps it OPEN. Origin's state stands. The done/ copy is an untracked orphan, and the reconciler preserves it before removing it.
- `docs/observability/open_question_register.json`, `site/data/delivery.json`: producer output.

**Holds bytes origin does not, left in place for the seat (the brief: leave DIRECTION.yaml to the seat):**

- `docs/direction/DIRECTION.yaml` (5 conflicts), `docs/direction/decisions.jsonl` (6 lines: the 13 Nov
  21:24, 14 Nov 00:23 and 03:24 orientations) and `docs/status/SEAT_STRETCH_LOG.md` (144 lines: the same
  orientations). These are one record. Landing the two logs without the yaml would split it, and the
  seat's next landing would then conflict with mine, so none was landed here. This is the
  open `REPEATING_ALARM_DELIVERY_SEAT_THE_DIRECTION_RECORD_DID_NOT_REACH_ORIGIN` class: the 00:24 record
  was refused at 01:29 and has not reached origin. `site/data/delivery.json` is regenerated from it.

## What closes it

When the seat lands its orientation record onto origin (the yaml merged against origin's 22:1x
revision; both logs are append-only, so they take origin's lines plus these), the three become twins.
The next `python3 -m background.origin_reconcile` then fast-forwards, because every other blocker is in a
class it already clears. No other lane's bytes are needed. Re-measure with `python3 -m
background.origin_reconcile --check`.
