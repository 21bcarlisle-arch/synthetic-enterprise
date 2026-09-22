**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION — widening `path_note` to `_ITEM_PROSE_KEYS`

A draw-time annotation widens its reach. Fail-open on both sides of the change; no production
number moves.

**Written 2026-09-22, BEFORE any of the measurements below were run.** Claim id
`the-draws-path-note-reads-only-what-and-why-so-53-entries-name-paths-it-cannot-see`.

## The premise, re-measured

`f0bc14599` is an ancestor of `origin/main` and this worktree's HEAD equals `origin/main`
(0 ahead, 0 behind). That commit landed the **orientation door** and the **hand-off door**, both of
which reach `_ITEM_PROSE_KEYS` through `direction_path_check._item_text`. It did **not** touch
`delivery_lane.path_note`, which at `background/delivery_lane.py:3823` still reads:

```python
text = "{} {}".format(item.get("what") or "", item.get("why") or "")
```

So the premise is **LIVE**, not spent. The draw's duplicate-work note names
`the-draws-path-note-reads-only-what-and-why-so-53-entries-name-paths-it-cannot-see` as a rival
claim — that is **this draw's own id**, already in
`docs/observability/.seat_work_in_hand.json` with an empty `paths` list and a note that is this
item's own `what` truncated at 200 chars. Not a rival. Carrying on.

## What I do not know, and am predicting before I look

**P1 — the population.** The item asserts 72 live continuation entries name a tracked path in
`done_means`/`note`, and that 53 of those name it in neither `what` nor `why`. The continuation
store is a **live store with an expiry**, so today's count is not the count the item was written
against. *Prediction: re-measuring today gives a blind count within ±15 of 53, and the ratio
blind/naming stays above 0.6.*

**P2 — does `_MAX_GRADED_PATHS` (24) need revisiting?** Widening the text can only increase the
resolvable-path count per item. *Prediction: **no**. Across the live store, zero items exceed 24
resolvable paths even after widening, so `dropped` stays 0 everywhere and the bound is not reached.
If any item does exceed it, the note already prints the dropped count rather than truncating
silently, so the failure mode is loud and the constant still does not need to move.*

**P3 — the unresolved-token count.** `done_means` and `note` prose is where `docs/staging/`,
`background/delivery_lane._disposition` and `tools/surgical_land` live — directory tokens and
dotted module references, neither of which resolve to a file. *Prediction: the widening adds MORE
unresolved tokens than resolvable ones — median per-item delta in unresolved strictly greater than
median per-item delta in resolvable — so the "N further path-shaped token(s)" sentence gets
materially louder and is the part of the note most changed.*

**P4 — cost.** `_path_verdict` shells out to git per path against the shared tree. *Prediction: the
widening at least doubles the mean graded-path count per item, and therefore at least doubles
`path_note`'s wall-clock. I predict the widened worst case on the live store stays under 5s.*

## What done means

1. `path_note` builds its text from `_ITEM_PROSE_KEYS`, not from a hand-rolled `what + why`.
2. A control that can actually fail: an item whose path is named ONLY in `done_means` is graded.
   Mutating the key tuple back to `("what", "why")` must red it.
3. P1–P4 answered on the live store, with refutations written beside the predictions above.

Results: `SEAT_RESULT_*_2026-09-22.md`, same subject.
