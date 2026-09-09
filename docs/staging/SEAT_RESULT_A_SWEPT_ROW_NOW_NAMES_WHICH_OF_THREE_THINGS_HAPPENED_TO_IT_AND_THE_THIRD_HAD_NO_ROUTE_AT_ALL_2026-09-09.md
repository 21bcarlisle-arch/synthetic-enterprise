**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — sixty-one-of-two-hundred-and-twenty-four-drawn-rows-can-never-bind-a-landing) · **Class:** controls_that_cannot_fail

# RESULT — a swept row names which of three things happened to it, and the third had no route at all

## The premise check was a false positive, and the item is live

The doorbell reported that the one commit this item cites — `420031dae` — is already an ancestor
of `origin/main`, and told me to re-measure before starting. It is an ancestor, and the item is
not spent: `420031dae` is cited as **evidence** (the commit that spent
`make-the-pages-two-selection-spreads-legible-now-that-they-sit-at-different-n`'s premise), not as
the deliverable. The premise check reads any sha in the prose as a thing the item is waiting on,
and an item whose subject is *a defect demonstrated by a landed commit* will always trip it. Noted
rather than fixed — the check is cheap and right far more often than it is wrong here.

## What the null meant, and why one number was three

61 of 224 rows in `docs/observability/.delivery_lane_claims.draws.json` read
`last_landing_at: null`. `drawn_without_landing` — the join the orientation opens with, second key
of the brief so a truncation cannot reach it — reported every one of them under one sentence:
*"drawn, given its window, and NOTHING LANDED … CHECK `git status` FOR THESE BEFORE STARTING
ANYTHING NEW."* Three different situations wear that null:

| | what happened | route before this |
|---|---|---|
| `not_done` | nobody did it — the real miss, and the only one that sentence is about | (the residual) |
| `landed_elsewhere` | worked and committed under a name that read better | `--landed-under`, since 2026-09-07 |
| `premise_spent` | drawn against a condition already true; nothing left to deliver | **none at all** |

The third is the one with no route. `record_landing` refuses an id whose claim was swept, and by
100 minutes after the draw every such id's claim HAS been swept — so an item that was drawn against
a premise something else had already spent could never bind anything, and its row stayed an
unexplained miss forever. The lane's own doorbell has printed the premise check since 2026-09-05
and told the reader to *"say so in `docs/staging/` and release the claim"*; the ledger row it came
from could not hear that sentence.

## What was built

**`background/delivery_lane.note_premise_spent(focus_id, commit, reason)`** — CLI
`--premise-spent FOCUS_ID COMMIT REASON`. The third disposition, and **the join is against git,
not against the caller**: `commit` must resolve here AND be an ancestor of `origin/main`. A
caller free-typing a plausible sha would turn the quietest disposition into a way to make a real
miss disappear, so the assertion the caller controls is *which* commit; whether it is in the
published record is git's answer. `reason` is required — a disposition with no reason is the null
it replaces wearing a better name. Five refusals, each naming itself: never drawn; already
delivered (the stronger fact is not overwritten by the weaker one); empty reason; unresolvable
commit; unpublished spender.

**`background/delivery_lane.disposition_of(focus_id)`** — the row-level reader, and the single
definition of the three. `drawn_without_landing` consumes it and now returns `disposition` and
`evidence` on every row it hands back.

**`background/delivery_seat._prompt`** — the sentence the orienting session actually reads names
each row's disposition and counts `git status` only over the `not_done` ones.

### One branch I nearly shipped that could not be taken

The first draft asserted all three dispositions through `drawn_without_landing`. It went red, and
it was right to: `--landed-under` writes a landing instant, so a credited row **leaves that list
by construction** and `landed_elsewhere` is unreachable there. Rather than reach for the list, the
three-way reader moved to `disposition_of`, which is asked about a *row* and where all three are
live. The list reading now names the two it can see, and a control asserts it can only ever
return those two. R15's fourth shape, caught by a partition control before it landed rather than
after.

## Keyed to the property, never to 61

Nothing asserts 61, or 224, or that the number falls. The property is: **every row the reading
returns names which of the three it was, and the residual is the shape carrying no evidence** — so
a row goes quiet only when a join against something on disk says it may. A control pinned to
today's 61 would go green when the sweep merely got *quieter*, which is the defect being fixed
wearing a better name.

## Controls, and the mutation round

`tests/background/test_a_swept_row_names_which_of_the_three_dispositions_it_was.py`, 8 tests, two
of them partition controls over the whole outcome space (a function that refused everything, or a
reader that answered one value always, reds on both). **Ten mutations, ten reds:**

| mutation | fires |
|---|---|
| drop the `reason` requirement | ✅ |
| drop the ancestor-of-`origin/main` join | ✅ |
| drop the "resolves to a commit" check | ✅ |
| drop the "was never drawn" guard | ✅ |
| drop the already-delivered guard | ✅ |
| reader answers `NOT_DONE` always | ✅ (2 tests) |
| reader answers `PREMISE_SPENT` always | ✅ (3 tests) |
| let a stale `landed_under` settle a NEW window | ✅ |
| collapse `DELIVERED` into `NOT_DONE` | ✅ |
| drop the evidence string from `premise_spent` | ✅ |

The non-ancestor branch is reached through a **stricter** fake `_git` (it answers two questions
from a table and refuses everything else, so it can only make the subject refuse *more* than real
git would), with a **poison round** — the same fake, ancestor answer flipped, must ACCEPT — because
"refused" is otherwise ambiguous between *the ancestor test fired* and *the fake declined to
speak*. The accepted path runs against real git: `origin/main`'s own sha is an ancestor of
`origin/main` by identity, on any machine, forever.

## Applied to the live ledger

The reading was 9 rows, all unnamed. It is now 7, every one named:

- `the-published-inversion-must-carry-its-attribution-on-the-page-not-only-in-the-tree` →
  **`premise_spent` by `b16281092`**, which landed the attribution 1.7h *before* the row was drawn
  again. The row's own earlier landing IS that commit.
- `find-where-the-renewal-rule-prices-up-the-households-it-then-loses` → **`landed_elsewhere`**,
  credited from `give-the-renewal-objective-the-departure-term-it-has-never-had`.
- `every-surface-that-still-says-our-advantage-is-selection-must-answer-the-nine-seed-floor` →
  **`landed_elsewhere`**, credited from
  `land-the-nine-seed-floor-by-the-three-pointer-recipe-and-own-it-to-the-rendered-selection-leg`.

The remaining 6 are `not_done` and stay loud. `some-id` among them is a test artefact that reached
the live ledger — worth a look, and not this turn's subject.

## What is next

- The five remaining `not_done` rows are unexamined, not proven missed. Each needs the same join
  or an honest `not_done`; that is the work that actually drives 61 down, and it is per-row.
- `some-id` in the live draw ledger means a test wrote to the shared store. Small, and a real
  containment question.
- Nothing here watches the register. If disposing of rows becomes a way to keep the dial quiet,
  the evidence field is where that shows — every disposition points at a commit or a lender row.

## Two reds at HEAD I did not cause and did not touch

`tests/background/test_seat_guard_daemons.py::test_every_main_entrypoint_is_guarded` (ten
`background/*.py` `__main__` blocks with no `refuse_if_foreign`, all absent at HEAD too) and
`tests/background/test_staging_root_resurrection_watch.py::test_the_landing_tool_actually_brackets_its_gate`
(the bracket is no longer inside `surgical_land._land_once`). Neither is in this change's blast
radius; both are recorded here because they will refuse somebody's land.
