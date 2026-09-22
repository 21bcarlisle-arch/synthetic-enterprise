**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION — does widening `premise_note` gain more reach than it suppresses?

**Written 2026-09-22 BEFORE the measurement below, and after
`SEAT_RESULT_THE_PATH_NOTE_READS_ALL_FOUR_PROSE_FIELDS_NOW_...` landed at `0b1898452`/`14dc33969`.**

## Why this is not the same change as the one just landed

The drawn item said `path_note` was *"the only one of the three path doors still reading a narrower
field set than the canonical one"*. That is true — **of the path doors**. Grepping the narrow
literal at `origin/main` after landing finds it still present once, at
`background/delivery_lane.py:3372`, inside **`premise_note`** — a fourth door with the same
hand-rolled `what + why` whose subject is cited **commit SHAs**, not paths.

**It is NOT a safe copy of the same fix, and that is the whole reason this is pre-registered.**
`premise_note` fires only when **ALL** cited commits have reached `origin/main` — keyed to the
property *"nothing this item points at is still outstanding"*. Widening the text can therefore move
the verdict in **both** directions:

* **GAIN.** An item citing commits only in `done_means`/`note` currently cites *nothing* as far as
  this door can see, so it returns `""` and no premise note is possible at all.
* **LOSS.** An item already citing commits in `what`/`why` gains more citations; one unlanded
  addition flips `all arrived` to false and **suppresses a note that fires today**.

A suppressed premise note is the expensive direction — it is the annotation that stops a seat
re-deriving work already on origin, which the docstring records costing a seat turn three times in
three days.

## The population, measured before predicting the verdicts

362 continuation entries. **11 cite a commit in `done_means`/`note` that `what`/`why` do not.**
Of those 11, **6 cite no commit at all in `what`/`why`** (pure gain candidates) and **5 cite
commits in both** (suppression candidates).

## Predictions

**P1 — net direction.** *Gain exceeds loss: more entries acquire a premise note than lose one.*

**P2 — the loss is not zero.** *At least one of the 5 both-fields entries flips from firing to
silent under the widening.* If the loss is zero, the widening is unambiguous and lands as-is.

**P3 — the right fix if P2 holds.** *If widening suppresses a live note, the fix is NOT a plain
copy of `path_note`'s widening.* The property is "nothing this item points at is outstanding", and a
commit cited in `note` as context is exactly the case the docstring already says must not suppress.
I predict the correct shape is to widen the SEARCH and keep the VERDICT keyed to the narrow pair,
reporting the later-field citations separately rather than folding them into `all arrived`.

## What done means

The 11 entries' `premise_note` output compared narrow against wide, verdict-by-verdict; P1–P3
answered with refutations kept beside them; and either the widening landed or a named reason it
must not be, with the residue filed.
