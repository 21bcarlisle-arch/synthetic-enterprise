**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — a landing under a different id)

# A landing under a different id now reaches the row that was drawn

*Seat, 2026-09-07. Lane 0 delivery.*

## The premise, re-measured before starting

Live at draw time, not inherited from the item's prose:

```
docs/observability/.delivery_lane_claims.draws.json
  the-lane-0-chain-counter-...              first_drawn_at set, last_landing_at NULL
  six-dd-level-collection-controls-...      first_drawn_at set, last_landing_at NULL
```

Both were still on the missed list. The premise stood. The ordinary route was then tried, and it
refused — which is the actual finding:

```
$ python3 -m background.delivery_lane --landed the-lane-0-chain-counter-... --commit ee3498cc0
bound NOTHING: it is NOT CLAIMED -- nothing holds a deadline for it
```

## What was wrong

Two items were drawn separately (04:11, 04:41), worked together, and landed in **one** commit —
`ee3498cc0`, at `origin/main` — bound to a **third** id,
`two-of-three-drawn-focus-items-were-finished-and-never-left-the-working-tree`.

`record_landing` is gated on the **claims** store, where "not claimed" is the right answer: there
is no deadline left to inform. But the **draw ledger** is a different store asking a different
question — what was handed out, and what came of it — it survives release by construction, and it
is the store `drawn_without_landing` reads for the orientation's most urgent heading. `sweep_stale`
empties the claims store at 100 minutes, so by the time this shape exists at all — *finish late,
land under a name that reads better* — the only route to the second store was already shut.

**The ledger could not tell "never landed" from "landed under another name."** Every future
orientation re-opens work that is done, and it gets worse as the row count grows.

## The repair

`background/delivery_lane.note_landing_under(focus_id, other_id)` — CLI `--landed-under`. It writes
the draw ledger **only**: no claim is taken, no deadline restarts, no draw instant moves.

It is a **join between two facts already on disk**, not an assertion by the caller, and that is what
makes it safe to let it remove a row from the seat's most urgent list. Four refusals, each naming
itself:

| refused when | because |
|---|---|
| `focus_id` has no row | there is no draw for a landing to reach |
| `other_id == focus_id` | self-credit is the free eraser |
| `other_id` holds no landing | a row cannot lend what it does not have |
| that landing predates `focus_id`'s first draw | older work is somebody else's — the same rule as `--landed` |

The row then carries `landed_under: <other_id>` beside the credited instant: **the one-line reason
it has no landing of its own**, so an audit of why an item left the missed list has something to
follow. Fails **closed** — an unwritable ledger reads as a refusal, unlike the reader beside it,
because the caller prints this answer and a silent success would train the next seat to stop
checking.

## The live effect

```
before: 6 ids drawn in the last day with no landing
after:  4     (only the two intended rows changed; 133 rows in, 133 out)
```

The four that remain are genuinely unlanded and are other lanes': the electricity-only decision
instrument, the four contradicted rows, the level-zero check's blind spot — and `some-id`, below.

## Reachability

`tests/background/test_a_landing_under_a_different_id_reaches_the_row_that_was_drawn.py`, 9 passed.
**Poison round run before the claim**, seven mutations, every one fires; source restored
bit-identical and re-run green.

| mutation | result |
|---|---|
| drop the predates-the-draw guard | 1 failed |
| drop the cannot-lend-itself guard | 2 failed |
| drop the empty-lender guard | 2 failed |
| drop the never-drawn guard | 2 failed |
| stop writing `landed_under` | 1 failed |
| report success on every path | 8 failed |
| move the draw instant on credit | 1 failed |

The first attempt at the predates-the-draw mutation reported **target not present exactly once**
(count 3 — `record_landing` carries the same line). A "survived" there would have been a patch that
never applied grading a different function. It was re-run against a unique target.

The end-to-end leg asserts a **difference** over one ledger: before the credit both real rows are
named, after it only the uncredited one. Asserting the after-state alone would pass on a reader
that had stopped reporting anything. It also caught a real interaction — a `now` a day past the
landing is a day and a half past the draws, and the 24h horizon drops both rows, which reads as the
credit working while nothing has been credited.

## Also landed: the previous turn's mechanism, which was still in the working tree

`drawn_without_landing`, its nine controls, its `delivery_seat` reach and its result doc were
written on 2026-09-07 and **never committed** — the same defect they describe, one level up.
Nothing at HEAD referenced them, so this lands them as-is. `background/delivery_seat.py` also
carried the level-zero lane's `_by_reason`/`ungradable_named` work; that is **not** in this commit
(`tools/isolate_hunks.py --keep 3..7`, verified: HEAD + 60 lines, zero occurrences of `_by_reason`).

## Also fixed: the weekly rhythm was wedging every lane's commit

`finding_severity` scans `docs/staging/` root **by filesystem**, not by filename, and exits 1 on any
document with no severity header. `weekly_rhythm._finding_body` had one; `_step_body` did not. So
`WEEKLY_RHYTHM_MONDAY_RANKING_2026-09-07.md` — written by a daemon, on schedule, with nothing wrong
— took the cheap gate to exit 1 and refused **every lane's commit**, including this one. The
rhythm's own product wedged the tree it exists to organise.

`_step_body` now emits `**Severity:** RECORDED` — recorded, not latent, because an open step is
scheduled work and it is `_finding_body` that raises the LATENT finding once the step is actually
late; classifying the step doc as a defect would put a healthy rhythm in the latent count every
week. The live document was repaired in place. The control grades the body with **the real gate's
own parser**, not a regex of its own — a control asserting the header string would pass on a header
the gate cannot parse, which is the entire failure mode. Both mutations fire.

## What this surfaced that I did not fix, and what I cannot yet say

`some-id` sits in the **live** draw ledger and has been named to the orientation as missed work for
17 hours. It is a test fixture id. The only occurrence of that literal in the tree is a
monkeypatched draw string in `tests/background/test_dispatch_is_the_claim.py:200` — and that test
takes an `_isolate` fixture and simulates an `ImportError` on `delivery_lane`, so on the face of it
it cannot be the writer. **I cannot yet say how it got there.** It will age out of the 24h horizon
on its own; the route that put it in a production store will not. Not attributed, not guessed.

## Done means

A brief whose stale-draw list contains nothing whose work is already at origin. It now does, and
the next time this shape occurs the route to say so exists and refuses four ways.
