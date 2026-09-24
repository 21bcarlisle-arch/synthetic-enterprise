# The spent reading is the wrong measurement at the hand-off door, and on the live record it fired backwards

**Severity:** RECORDED
**Lane:** `H_harness`

*Delivery seat, 2026-09-22, under claim
`the-hand-off-store-writes-items-blind-to-the-same-classifier-the-orientation-now-runs`.
Prediction filed before the measurement:
`docs/staging/records/PREREG_WHAT_THE_PATH_CLASSIFIER_SAYS_ABOUT_LIVE_HAND_OFFS_2026-09-22.md` —
the records room, because the root is the work queue and a prereg is not work anybody must pick up.*

---

## What was asked, and why it is not what shipped

`background/seat_continuation.py --hand-off` is the third and last door prose reaches the draw
through. `delivery_lane.path_note` (`dca82c164`) closed the READER's half; `direction_path_check`
(`95035ad29`) closed the ORIENTATION's. The item asked for the same classifier here, and said so
explicitly: *"this is a call and a rendered sentence rather than new logic."*

It is a call and a rendered sentence. It is **not** the same concern, and that is the finding.

## The measurement

`NOTHING_TO_LAND` fires when every path an item asks to be CHANGED is identical to HEAD. Graded
over the live continuation store:

| entries naming N change paths | 1 | 2 | 3 | 4+ | all |
|---|---|---|---|---|---|
| items | 100 | 82 | 37 | 46 | 265 |
| fire `NOTHING_TO_LAND` (08:47) | 84% | 67% | 59% | 48% | **69%** |
| geometric 0.84ⁿ for comparison | 84 | 71 | 59 | 50 | — |
| the same walk at ~08:30 | 71% | 43% | 32% | 33% | **50%** |

Two things are in that table.

**It is geometric in the number of paths named.** That is the signature of a property of the TREE —
each named file is independently ~84% clean, and the rule needs *all* of them clean — and not a
property of the item. An item that names four paths is not four times less likely to be spent.

**The base rate moved 19 points in 17 minutes, and that is the better evidence.** Nothing about the
358 hand-offs changed between the two walks. Another lane committed a batch, and files that had
been `dirty` became `already landed`. A reading that moves that far because somebody else ran `git
commit` is not telling you anything about the item it is attached to.

## Why it has to be this way

The two doors are asking about different things and the word `already landed` hides it.

- An **orientation** item can say *"land this pile"*. Its subject may be bytes that already exist
  on disk, so `already landed` can mean the ask is spent. That reading is sound and it shipped.
- A **hand-off** is written at the END of a turn, about work **not yet done**. `already landed` is
  the *expected precondition* — the file the next tick is being sent to write is of course
  identical to HEAD, because nobody has started.

Same tag, same classifier, opposite meaning. This is the project's recurring shape: *before
measuring a thing, say what it is.* The definition was inherited along with the code.

## It fired exactly backwards on the two live entries

This is the part that settles it, and it was not predicted.

- `restore-the-six-live-reverts-before-anything-regenerates-from-them` **is** a pile item — its ask
  genuinely can go spent, and it is the shape the concern exists for. It stayed **silent**, because
  one of its six paths was still dirty.
- `the-hand-off-store-writes-items-blind-...` — the item that commissioned this work — names one
  file it intends to write. The verdict is meaningless there. It **fired**.

A concern that is silent on the only item it could have helped and loud on the one it cannot is not
mistuned; it is measuring the wrong quantity.

## What shipped instead

`_hand_off_concerns` reuses `grade_item` unchanged — one classifier, not a second one — and selects
different classes at this door:

- **`HAND_OFF_STALE`** (new): a named path whose working copy is `predates landing` or `deleted`.
  The bytes are not what the prose describes, and the next tick reads that prose hours later and
  will trust it over the tree. Fires on **13 of 359 entries (3.6%)**.
- **`REVERTING_REMEDY`** (inherited, correct at any door): fires on **0** of the store today. Kept
  anyway — it costs nothing, it is the stricter of the two, and the row that names
  `tools.refresh_to_head` is the one worth having on the day a seat does write it.
- **`NOTHING_TO_LAND`**: dropped entirely, for the reason above.

The **role split** is dropped too, and deliberately: at the orientation door it is load-bearing,
because `already landed` on a read-only path is the ordinary state of every committed file. Here
the spent reading is gone, so the remaining question is whether the BYTES contradict the prose —
and a hand-off that sends the next tick to READ a stale copy has misled it exactly as badly as one
that sends it to write there.

## The half the draw cannot compute

`hand_off` now stores the reading on the entry, stamped. **Not as a verdict** — the draw grades the
tree fresh three lines up, and a second opinion kept from hours earlier would rot into a stale
literal beside a live one. Its only licence is the **difference**: `drift_note` reports what MOVED
between the writing and the draw, and says nothing where the two readings agree.

That is the question the item's own WHY is about and the one no reader of the tree alone can
answer: two of the six reverts focus item 1 named were repaired by another lane between 07:40 and
08:10, which is exactly the window a hand-off lives in. A path that went `dirty` → `already landed`
was landed by somebody while the item waited; one that went the other way has a lane in it now.

## Prediction versus result

| # | predicted | outcome |
|---|---|---|
| 1 | ≥3 live entries fire `NOTHING_TO_LAND`; the true fraction is "most of them" | **REFUTED.** There were only **2** live entries at all, so the prediction named a population that did not exist. Widened to the whole store the direction held (69%), but the number I would have defended was wrong and the count was not close. |
| 2 | `REVERTING_REMEDY` fires on none of them | **HELD** — 0 of 359. |
| 3 | My own drawn item fires, and its work is entirely real | **HELD**, and it turned out to be the sharp end: the *other* live entry, the one the concern exists for, stayed silent. |

Not predicted at all, and the two things that actually decided the design: the **geometric
structure** in path count, and the **inversion** on the two live entries. I predicted the
instrument would be noisy. It is worse than noisy — it is anti-correlated with the thing it names.

## Controls

`tests/background/test_the_hand_off_store_grades_what_it_hands_on.py`, on a real git repo carrying
one file of each state. First test is the inversion (the spent class must not appear at this door
for ANY shape); second is the whole partition in one control, because a checker that fires on
everything passes any per-class assertion written alone.

**10 mutations run, 10 fired.** One was silent on first application and was established rather than
assumed to be an equivalence: patching the quiet note to `"" or "<text>"` is a no-op in Python, so
the patch never changed behaviour. Re-applied as a bare `return ""`, it reds.

**A fail-open in this work was caught by its own control**, not by review: on a tree git could not
read, `grade_item` swallows its exception and returns a blank, so *"names no path"* and *"the tree
is unanswerable"* both arrived as zero rows — and the note said *"nothing contradicting the
prose"*, a clean verdict over a tree nobody could read. The reading now carries `readable: False`
and the note leads with **NOT a clean verdict**.

## What is left

The drift note is wired into `doorbell` and reads only entries written after this lands — every
entry in the store today predates it and carries no `path_reading`, so drift is silent until the
first hand-off written through the new door is drawn. That is correct and needs no backfill: a
reading manufactured now would claim to describe a tree from hours ago.
