**Severity:** RECORD · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: of the map-touching commits, how many move a `level_current` VALUE?

Written BEFORE the measurement, to size the reach of the trigger I am about to build:
`next_step_gate` will ask for a `NEXT:` trailer when the staged diff moves an atom's
`level_current`. That is only worth building if a map commit usually IS a level move.

## What is already established (not a prediction)

A line-level diff over the last **120** first-parent commits touching
`docs/design/maturity_map.yaml` finds **32** that add and remove a line containing
`level_current`. That number is an OVER-COUNT by construction: one of the five examples it
returned is `level_current: 2 # L0->L2 …STOPS AT 2 ON` → `level_current: 2 # …HELD AT 2 by its`
(`2cc924ed9`) — the same value, a rewritten trailing comment.

## The prediction

Parsing the VALUE out of both blobs instead of diffing the line, over the same 120 commits, I
predict **20–26** commits move at least one `level_current` value — i.e. that **6 to 12** of the
32 are comment-only edits on a level line.

I also predict at least one commit in the window moves a value **DOWN** (a level withdrawn), which
is why the trigger will be keyed to "changed", not to `level_promotion_gate.level_increases`.

## Why it is written down

If the answer is near 32, the line diff was fine and the value parse bought nothing but a comment
in the code. If it is far below 20, a map commit is mostly bookkeeping and the trigger's reach is
smaller than the map's commit rate suggests — which belongs in the finding, not in a footnote.

The reach of the trigger on the CURRENT trunk is separately bounded and already known: the map has
not been committed for 245 first-parent commits, so this trigger fires on nothing today. That is
not what this pre-registration is about and it is not repaired by this work.

---

## THE RESULT, kept beside the prediction. BOTH PREDICTIONS WERE WRONG.

Measured 2026-09-25 over the same 120 first-parent commits touching the map, parsing
`level_current` out of BOTH map halves at each commit and its parent
(`level_promotion_gate.atom_levels` over `maturity_map_store.MAP_PARTS_REL`):

* **31 move a value**, not 20–26. So **exactly one** of the 32 line-diff hits is a comment-only
  edit — `2cc924ed9`, the one I had already looked at. The value parse bought one commit over the
  line diff across 120, not six to twelve.
* **0 moves are downward.** I predicted at least one.

### What that changes and what it does not

It does not change the key. The trigger stays keyed to *"the value changed"* rather than to
`level_promotion_gate.level_increases`, for the reason the map cannot supply: a control pinned to
today's answer (all moves have been upward, all level lines that changed were real moves) goes
green when the code becomes more honest and red when the claim rots. `2cc924ed9` is a real,
in-the-record instance of the comment-only edit, so the false positive the line diff would produce
is demonstrated rather than hypothetical — it is the negative arm of
`test_a_comment_rewritten_on_a_level_line_is_NOT_a_move`.

It does change what I can claim about the downward branch: **history does not exercise it**, so the
control that proves it reachable is the only evidence it works, and `test_a_level_WITHDRAWN_is_a
_move_too` is written against a constructed pair for exactly that reason.

It also means "a map commit is a level move" is a much better approximation than I expected: 31 of
120 map-touching commits move a level, and the other 89 touch the map without moving one. A trigger
keyed to *the map being staged* would therefore fire on ~4x the traffic and ask for a successor on
89 commits that advanced nothing. That is the argument for the value parse, and it is a different
argument from the one I wrote above.
