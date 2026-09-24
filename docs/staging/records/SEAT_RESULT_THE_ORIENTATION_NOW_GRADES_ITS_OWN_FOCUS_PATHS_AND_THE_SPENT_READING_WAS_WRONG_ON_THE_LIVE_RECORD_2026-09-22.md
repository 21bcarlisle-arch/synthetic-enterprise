**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [SEAT] The orientation now grades its own focus paths before filing them, and the "every path is landed ⇒ the ask is spent" reading was wrong on the live record

*2026-09-22, delivery seat, isolated worktree. Lane 0, claim
`the-orientation-writes-pile-items-blind-to-the-classifier-the-draw-now-runs`.*

---

## The one-sentence result

`background/direction_path_check.py` asks the landing door's own classifier about a focus item's
paths at the two moments the orientation can still act on the answer — while the next record is
being **written**, and after it is written but before it is **committed** — and the first thing it
established is that the reading the item commissioned it for, *"every named path grades `already
landed` ⇒ the ask is spent"*, is **false as a verdict** and is shipped as a measurement carrying its
own refutation instead.

---

## The premise, re-measured

The item cites `dca82c164` as already an ancestor of origin/main, which is correct and is not the
work: that commit is `delivery_lane.path_note`, the **read** half. The ask is the **write** half and
nothing had built it. The duplicate-work note named this item's own id in
`docs/observability/.seat_work_in_hand.json`; `claimed_at` is `1790060751.51` = 08:05:51, thirty
seconds before the draw printed, so it is this draw's own claim and not a rival. No concurrent
`surgical_land` was on the box. **Premise live, work done.**

## What was built

| | |
|---|---|
| `background/direction_path_check.py` | `grade_item` / `concerns` / `note` / CLI. Imports `_path_verdict`, `_path_roles`, `_NAMED_PATH` and `_ITEM_PROSE_KEYS` from `delivery_lane` — one classifier, not a second one. |
| `delivery_seat.build_brief` | new key `live_direction_path_concerns`, graded over the LIVE record: the items about to be carried forward or dropped. |
| `delivery_seat._prompt` | renders it as a **sentence above the JSON**, outside the 60k truncation, with the command to re-run it against a draft. |
| `delivery_seat.orient` | new row key `path_concerns` over the record the session **just wrote**, logged one line per concern, recorded, and **never refused**. |

The two legs answer different questions and both are needed: the brief cannot grade an item the
session invents this stretch, and the `orient` leg cannot reach the seat while it is still writing.

## The finding: the commissioning item's own rule is not sound

The item asked for *"an item whose every named path grades 'already landed' (its ask is spent before
it is filed)"*. Run against the live record at 08:2x, the one item it fires on is
`the-staging-archival-is-116-deletions-the-guard-itself-refuses` — and that item's ask is **not**
spent. Its change set is the single tracked module `background/staging_rooms.py`, which is indeed
identical to HEAD; its actual subject is 116 deletions under `docs/staging/`, a **directory**, and
git tracks no directories, so the item's real subject can never reach the role split at all.

So the concern ships as a measurement with the evidence that would overturn it travelling inside it
— the count of bare directory tokens the door has no opinion about — and says in its own text
*"THIS IS A MEASUREMENT AND NOT A VERDICT"*. Calling it spent would have been this project's
commonest publishing error performed by the control built to prevent it.

The **role split is what makes the note worth reading at all**: `already landed` is the ordinary
state of every committed file, so grading the union of change-paths and read-paths would fire on
nearly every item ever written.

## Predictions filed before measuring, and how they came out

1. *"7 of 7 file paths still grade `already landed`, as the item's why says."* **REFUTED.** At 08:10
   only 5 of 7 did. `simulation/net_new_acquisition.py` had been restored (its revert is gone) and
   `tools/generate_value_arms_data.py` now grades `dirty` rather than `predates landing`. Two of the
   six live reverts the record's rank 1 is about have been dealt with since 07:40 by another lane.
2. *"The `predates landing` + `isolate_hunks` remedy class fires on focus item 1."* **REFUTED for
   today's tree, for the same reason.** Item 1 names `tools/isolate_hunks.py` and did name a stale
   path at write time; with the revert restored, no live item reaches that class. The class is real
   and is proven on a fixture rather than on the record.

## The controls, and the two mutations that were silent

`tests/background/test_the_direction_record_is_graded_before_it_is_filed.py`, on a **real git repo**
holding one file of each state. The first test is the control over the **whole partition** — spent,
reverting-remedy, real-work and directory-subject in one record — because a checker that fires on
every item satisfies any per-class assertion written alone, and one that fires on none satisfies the
`real-work` leg.

Seven mutations were run. Five fired immediately. Two were silent and were **established, not
assumed**:

- **Grading the union of the roles was silent**, and the cause was the fixture, not an equivalence.
  The read-only test used a *mixed* sentence (one path changed, one read); under the union its
  change set is `{live, spent}`, which is not all-spent, so no concern fires either way. The union's
  reachable error is an item with **no change path at all**, where the correct reading has nothing
  to grade and the union reports the ask spent. Both fixtures are now in the test with that stated.
- **Dropping the re-run command from the prompt was silent because the patch never applied** — the
  literal spans two source lines. Re-applied properly, it reds.

## What is deliberately not here

No refusal. `commit_direction` runs whatever the check says, for `path_note`'s reason — an item
naming a spent path is often still the right work — and because a check that can wedge the
orientation when git hiccups is worse than no check, which is `background/direction.py`'s own
fail-soft argument.

No NTFY. The `nothing to land` class fires most stretches by construction; a notification that
fires most stretches is a notification nobody reads.

## Gates

`tests/background/` for delivery seat, direction contracts and the draw's own path classifier: 127
passed. `tests/design/` + the static quality ratchet: 161 passed. `ruff --select I001` and full
ruff on the new files: clean. The new control: 7 passed, 7 mutations, all firing.
