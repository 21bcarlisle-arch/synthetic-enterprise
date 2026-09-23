**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the draw's path check reads all four prose fields now, and the noise I predicted it would
add is the opposite of what it added

**Filed:** 2026-09-22. Drawn as Lane 0 delivery,
`the-draws-path-note-reads-only-what-and-why-so-53-entries-name-paths-it-cannot-see`.
Pre-registration: `docs/staging/records/SEAT_PREREG_WIDENING_THE_PATH_NOTE_TO_THE_CANONICAL_PROSE_FIELDS_2026-09-22.md`,
written before any measurement below.

## The premise was live, and the "rival claim" was this draw's own id

The draw's premise check reported `f0bc14599` already an ancestor of `origin/main`. It is — and it
is not this work. That commit landed the **orientation door** and the **hand-off door**, both of
which read the canonical tuple through `direction_path_check._item_text`. It never touched
`delivery_lane.path_note`, which still hand-rolled `"{} {}".format(item.get("what"),
item.get("why"))`. Premise **live**, not spent.

The duplicate-work check named
`the-draws-path-note-reads-only-what-and-why-so-53-entries-name-paths-it-cannot-see` as a live rival
holding the id. That is **this item's own id**: the store row's `note` is this item's own `what`
truncated at 200 characters and its `paths` list is empty. Not a rival, and no disposition taken.

## The defect, measured on the live store

360 continuation entries. **54 of them name a tracked path in `done_means` or `note` that appears in
neither `what` nor `why` — 68 such paths — and the draw's path check could see none of them.** Of
the 3 entries live at the moment of measuring, 3 were blind. The item predicted 53; the difference is
that its criterion is per-PATH, and an entry naming path A in `what` and path B in `done_means` is
not blind as an entry but has a wholly invisible path. **P1 CONFIRMED** (54 against 53).

The blind field is the worst one to be blind in. `done_means` is where *"done means the row is in
`docs/design/maturity_map.yaml`"* lives — so the field the note dropped is the one carrying the
artefact the tick has to touch.

## P3 REFUTED, and in the opposite direction

I predicted `done_means`/`note` prose — full of `docs/staging/` and dotted module names — would add
**more unresolved tokens than resolvable paths**, making the "N further path-shaped token(s)"
sentence the loudest part of the change. Over the 54 affected entries:

| | median delta | mean delta |
|---|---|---|
| resolvable paths | **+1** | **+1.26** |
| unresolved tokens | **0** | **+0.48** |

The widening makes the note **more useful, not noisier** — it adds roughly two and a half real
paths for every unresolvable token. My reasoning was wrong about where directory tokens live: the
standing `docs/staging/` vocabulary is in `what`, which the narrow read already carried, so it was
already counted and the widening does not add it twice.

## P2 CONFIRMED — `_MAX_GRADED_PATHS` was not touched, and the measurement is why

The widest item on the live store resolves **12** paths, against a bound of **24**, and the widening
did not change that number — the widest item names its paths in `what`. No item on the store exceeds
24 path-shaped tokens under either reading. The bound is not near. Had it been, the note already
prints what it dropped rather than truncating silently, so the failure mode is loud either way.

## P4 CONFIRMED — the cost did not move

Same item, like for like: **0.53s narrow, 0.48s wide** (min of 3, after warm-up). The prediction was
"at least doubles, stays under 5s"; the doubling did not happen, because the paths were already
being graded — the widening changes WHICH item's paths are found, not how many the worst case has.

## A second finding: the canonical tuple had no guard anywhere

`_ITEM_PROSE_KEYS` is shared by three doors. Narrowing it back to `("what", "why")` and running the
two sibling doors' own suites — `test_the_direction_record_is_graded_before_it_is_filed.py` and
`test_the_hand_off_store_grades_what_it_hands_on.py` — gives **19 passed**. Neither door's suite can
tell whether the tuple it depends on has been narrowed under it.

The mutation is caught by the two new legs in
`tests/background/test_the_draw_classifies_the_paths_it_names.py` and **by no other leg in the
tree** — which is the unflattering reading and the correct one: the defect was live and unguarded,
and that guard did not previously exist at any of the three doors.

`test_every_prose_field_an_item_carries_reaches_the_classifier` is one assert over the whole key
partition rather than a leg per field, because four legs each pass against a reader that merely
SWAPPED which pair of keys it reads, and the mutation to catch is exactly a subset.

## What landed

* `background/delivery_lane.py` — `path_note` builds its text from `_ITEM_PROSE_KEYS`; docstring
  records the measurement, the refuted prediction and why the cap was not raised.
* `tests/background/test_the_draw_classifies_the_paths_it_names.py` — two legs, mutation-proven.

## What was still owed, and was then closed in the same turn

Written above before the second increment: *"the tuple guard covers `path_note` only. The
orientation and hand-off doors reach the same tuple and would go silently narrow with it."* That is
now closed. `test_the_canonical_prose_tuple_cannot_be_narrowed_under_this_door` in
`tests/background/test_the_direction_record_is_graded_before_it_is_filed.py` grades an item whose
subject paths sit **only** in `done_means` and `note`, and asserts both reach `grade_item`'s
`to_change`. Under the same narrowing mutation it reds, alone, naming both paths; restored, 32 pass
across all three doors' suites.

It is asserted on `to_change` and deliberately **not** on a concern CLASS: the classes are
heuristics over the item's text, and a leg routed through them would be measuring the heuristic
while reporting it as reach.

The hand-off door has no leg of its own, and does not need one — it reaches the tuple through the
same `direction_path_check._item_text` this leg now covers. What remains genuinely uncovered is
nothing in this family.
