# WORKER FINDING — CLAUDE.md is OVER ITS OWN HARD LIMIT at HEAD; the trim is uncommitted

**Filed:** 2026-08-09 ~23:00, worker seat. **Disposition:** FILED, NOT FIXED (the trim is
another lane's uncommitted edit; this seat holds).
**This is the FIFTH instance today of tree-green / HEAD-red.**

## OBSERVED (R9)

```
CLAUDE.md at HEAD (311eb95da)   35,750 chars   -> OVER the 35,000 hard limit
CLAUDE.md in the working tree   34,979 chars   -> under, by 21 chars
```

Against a FAITHFUL HEAD checkout — `git archive` + `_make_checkout_a_repo` +
`_overlay_untracked_data`, i.e. the gate's own construction, not a hand-rolled extract:

```
tests/tools/ (2,197 tests)   2 failed, 2195 passed
  FAILED tests/tools/test_claude_md_integrity.py::test_real_claude_md_within_hard_limit
  FAILED tests/tools/test_claude_md_integrity.py::test_full_check_passes_on_real_repo
```

Drop the working tree's CLAUDE.md into that same checkout and the file goes green:

```
tests/tools/test_claude_md_integrity.py   49 passed
```

`episode_failures` is now **58** (49 when the KNIFE2 landing closed the wall cause).

## THE TRIM IS COHERENT, NOT MID-EDIT

`git diff CLAUDE.md` is 8 insertions / 9 deletions — condensations, not deletions of rules:
the seven portability constraints' parenthetical examples collapse to "Seven constraints —
full text in the staged doc"; the deleted-permission-machinery list collapses from
file-by-file to categories; a stale build stamp is corrected (18,504 → 23,826 tests). No
rule loses its substance. It reads as a deliberate trim made precisely to get back under
the ceiling, and it lands 21 chars inside it.

## WHY THIS IS THE SAME CLASS, AGAIN

Fifth today: KNIFE1, KNIFE2, `14fbd32cd`, the `supply_book` reference, and now this. A lane
does the work, the working tree goes green, the lane exits without committing, and HEAD —
which is now the gate's subject — stays red. The control is not at fault; it is doing
exactly its job. What keeps failing is the LANDING.

Note the interaction with the ruling already on the record: CLAUDE.md's own rule says
*"CLAUDE.md hard limit: 35k chars / 200 lines. Stop and trim before anything else if
exceeded."* That rule was honoured — someone did stop and trim. It just never landed, which
is precisely the gap `OPS4_surgical_landing_tool` exists to close.

## RECOMMENDATION (not taken — this seat holds)

Commit the working tree's CLAUDE.md by pathspec. It is one file, it is coherent, it is
proven green in a faithful HEAD checkout (49 passed), and it unblocks the gate. No
redesign, no trim of my own — land what the other lane already wrote.

## BISECT (H38) STATUS — the premise moved

The bisect was granted against `test_website_integrity_fix.py::test_..._insights_before_
dashboard`. Two results:

1. **The polluter is not in `tests/tools/`.** That test PASSES with its entire 2,197-test
   directory in a faithful checkout.
2. **The blocking test has MOVED** — the current HEAD red is CLAUDE.md, not that test. The
   earlier "1 failed / 22,616" was measured on a tree two hours and several commits ago.

So H38's premise needs re-establishing against current HEAD before more bisecting: confirm
the pollution is still reachable at all, rather than bisect for a failure that a since-landed
commit may have removed. **A caution for whoever draws it:** my first attempt used a plain
`git archive` extract and produced **43 failures** that were pure artefacts of missing
untracked data. Use the gate's own checkout construction, or the bisect will chase ghosts.
