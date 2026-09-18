**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, the
residual's two voices

# The drawn item was already landed under its own id, and the red it left behind was a control pinned to the day's answer

**Filed:** 2026-09-18 · **Claim id:** `the-draw-cannot-read-an-instant-the-disposition-already-can`
**Subject:** `tests/background/test_a_window_that_closed_before_its_own_subject_existed_says_so.py`,
`background/delivery_lane.py::_nothing_answered`
**Established against:** `1c9ff21cc` (worktree HEAD at the draw; `896a286d8` and `2984864c7` both
ancestors of `origin/main`)

The three legs this repairs were red at HEAD before this landing and are green in it — the defect
and its repair are one commit, which is why this is RECORDED and not BLOCKING.

---

## 1. The drawn item was already landed, under this very id, 44 minutes before the draw

The duplicate-work check said one other live claim "may be this work under another name" and named
`the-draw-cannot-read-an-instant-the-disposition-already-can` — **this item's own id**, already held
in `.seat_work_in_hand.json`. It was not a rival under another name. It was a previous invocation of
this same claim that had already done the work, landed it, and not released.

`896a286d8` (2026-09-18 20:21:46, on `origin/main`, verified `git merge-base --is-ancestor`) wires
`_back_referenced_start` into `embargoed_until` and ships
`tests/background/test_the_draw_reads_the_back_referenced_instant_the_disposition_already_read.py`.

**I verified the DONE criteria rather than reading the commit message**, because a commit message is
a claim:

| DONE clause | Evidence |
|---|---|
| `draw()` withholds an item naming a future instant in either spelling | `test_the_draw_withholds_the_back_referenced_item_and_keeps_delivering` — green |
| `--embargoed` lists it with the instant it waits for | `test_the_reader_names_the_instant_a_back_referenced_item_waits_for` — green |
| a control reds if only the dated grammar is honoured | **mutation run here**: `if not dated_only:` → `if False:` ⇒ **5 of 6 legs red** |

The one leg surviving that mutation is `test_no_anchor_means_no_back_referenced_embargo`, and it is
a genuine **equivalence**, not a missing test: with no anchor there is no back-referenced embargo by
either route. Establishing which of the two it was is the rule; recording it here is the point.

**Disposition: the claim is discharged.** No `--landed-under` — that maps one id to another and this
landed under its own id.

## 2. What the prior turn left behind, and it is the interconnection defect

That turn's own message recorded, honestly, as NOT MINE: three legs of
`tests/background/test_a_window_that_closed_before_its_own_subject_existed_says_so.py` red at HEAD.
They are still red. **This is the shape CLAUDE.md reserves to the seat** — of what landed since the
last orientation, what else assumes it, and does the assumption still hold.

Commit `2984864c7` made `_nothing_answered` name its reason per branch. Its docstring states the
defect it ended: *"SILENCE AND 'WE LOOKED AND FOUND NOTHING' ARE DIFFERENT ANSWERS AND THE EMPTY
STRING WAS BOTH."* Three legs in the neighbouring suite asserted `evidence == ""` — the very silence
that repair abolished. **The code became more honest and the control went red.** That is exactly
backwards, and it is the failure CLAUDE.md names: *key a control to the property, not to today's
answer.*

The file was already internally inconsistent and nobody had read it as a whole:

- its **opening paragraph** (line 8) names `not_done` with an EMPTY EVIDENCE STRING as half the
  defect it exists to fix;
- its **header** (line 22) swears the file is "KEYED TO THE PROPERTY, NEVER TO TODAY'S ROW";
- `test_PROSE_THAT_STATES_NOTHING_...`'s **docstring** says the residual "stays LOUD", and its
  **body** asserted `evidence == ""` — it asserted silence in the same breath as demanding loudness.
- and one rung away, `test_every_disposition_names_what_was_checked.py::test_NO_RETURN_SITE_WRITES_AN_EMPTY_REASON_however_it_is_reached`
  asserts the direct negation, green, in the same directory.

Two suites in one directory asserted contradictory things about one function. Nothing could notice,
because each was green or red on its own terms and no reader held both.

## 3. The repair, and why it is a widening that is strictly stronger

No new control: the property already has a home (`test_every_disposition_names_what_was_checked.py`,
commit `2984864c7`). The three legs are re-keyed to the property each one's own docstring already
stated, via two discriminators on the residual's **two voices**:

- `_looked_and_found_nothing` — git was asked on this row's paths and came back empty. The one
  reading that means *workable, draw again*.
- `_could_not_ask` — the asking broke; a louder disposition may be true and was lost.

`evidence == ""` could not tell these apart — it was satisfied by both, which is precisely why the
empty string was the defect. The new legs are therefore **strictly stronger than what they replace**,
not a widening to green.

**Mutation (j), run in both directions, each firing the leg written for it and no other:**

| Mutation | Result |
|---|---|
| `if unanswered:` → `if False:` (raising branch loses its voice) | **1 red**: `test_PROSE_THAT_STATES_NOTHING_...` only |
| genuine-miss branch prefixed `CANNOT ANSWER` (voices collapse the other way) | **3 red**: partition, usable-window, prose-states-nothing |

Both mutations were reverted byte-exactly (`git status --porcelain background/delivery_lane.py`
empty). Note what the old assertions graded: **nothing**. They were red at HEAD unconditionally, so
neither mutation could have moved them. The gain is not that the reds went away — it is that these
legs are now green at HEAD and red under each collapse.

## 4. Prediction left standing beside its refutation

The prior turn's commit message predicted these three legs were pre-existing and unrelated
("confirmed by running the identical suite against the unmodified file"). **That was correct as to
cause and wrong as to ownership**: they are not unrelated: they are the downstream half of the same
`_nothing_answered` repair, and `2984864c7` should have carried them. Recorded here rather than
quietly folded in, and the header of the repaired file now carries the same correction beside the
mutation list.

## 5. Still owed — NOT claimed by this turn

`docs/staging/SEAT_RESULT_THE_DRAW_NOW_READS_THE_BACK_REFERENCED_INSTANT_...md` sits in the staging
root and is the prior turn's result for a claim now discharged. Its archival to `done/` is a
separate discharge and **is not performed here**: this turn did not verify its other clauses, and an
archival that outruns its verification is the failure that register exists to catch.
