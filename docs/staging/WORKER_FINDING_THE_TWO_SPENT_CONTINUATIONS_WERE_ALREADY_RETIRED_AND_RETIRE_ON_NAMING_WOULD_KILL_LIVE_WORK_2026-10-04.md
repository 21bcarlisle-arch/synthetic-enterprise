**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` — Lane 0 delivery

# The two "spent" continuations were already retired, and retire-on-naming would retire live work

Item: `retire-the-spent-continuations-before-they-are-drawn` (focus row two, orientation
2026-10-04T14:23Z). Disposition: **released; the mechanism it asked for is not built, because
measured on four to six days of origin it does more harm than the defect it targets.**

## 1. The premise is spent: both rows were retired by their holders within minutes

Read from `docs/observability/.seat_continuation.json` at 15:40Z:

| continuation | spending commit | commit (UTC) | `retired_at` (UTC) |
|---|---|---|---|
| `the-20261004r-floor-book-mismatch-is-explained` | `e83ef71ef` | 12:56:07 | 12:58:38 |
| `the-20261004r-arms-are-not-heads-code-seven-paths-moved` | `f5ee6000b` | 13:45:16 | 13:46:10 |

Neither is in `seat_continuation.live()`. Its only members are
`publish-the-20261004h-heads-arms-pair`, `grade-stage-a-of-the-larger-book-test` and this item. The
stretch-log line "two queued continuations outlived the commits that spent them" is wrong. The two
did not outlive the commits; each was retired one to two minutes after its commit landed. Nothing
needed releasing, so no store row was changed.

## 2. The mechanism, printed at real inputs before building it

The rule as directed: when a landing's message or paths name a continuation's id, or name the
staging doc it cites, retire that continuation with the sha. The replay matched every origin commit
against every non-tombstone row. It counted a firing only when the commit came after the row was
written and before the row was retired, because only those firings change anything.

**Leg A: the message names the id (4 days, 635 commits, 41 mentions).** About 12 firings land on
work that is still in flight. They are hand-off and progress mentions: "handed on as continuation
X", "carries", "waits for X to reach origin", "increment 1", "knowledge leg of X", "the rival
holds X". Examples include `c9e7f4af9`, which would have retired a row 4.6h before it finished;
`8cbda4280` 2.4h before; `4ed1fa774` 3.4h; and `62b791c10` and `a0f2496e9`, whose rows are still
not retired. Every firing on a commit that really finished its row came within minutes of the
holder's own retirement, so this leg catches **nothing** the holder had not already caught.

**Leg B: the paths touch a cited staging doc (6 days).** About 100 firings, mostly early ones. A
commit edits the cited finding to add a pre-registration, a progress note or a header re-chain
long before the work ends. Some rows are still open today. Restricting the leg to `records/` does
not help. `0fd40e81e`, the commit that LAUNCHED Stage A, modifies the cited prereg under
`records/`. Under leg B it would retire `grade-stage-a-of-the-larger-book-test`, which is live
now and cannot be done until Stage A ends. Only the narrowest form, a doc RENAMED INTO `records/`,
was clean. It fired twice (`e83ef71ef`, `0485b09ca`), and both times the holder retired the row
within minutes anyway.

**Against the recurrence it was meant to stop.** The F5 instance in the WHY was `4820efe96`, the
heartbeat item drawn after `3373f3523` landed it. That item is a DIRECTION focus row, not a
continuation. `3373f3523` names neither its id nor a staging doc, so neither leg would have fired.

So the rule's precision on in-flight work is poor, and every correct firing came after the holder
had already retired the row. Each premature retirement would take live work off the queue
silently. That is a worse failure than F5, which costs one tick and leaves a visible note.

## 3. What would reach the real F5 source (recommendation, not built)

The recurring F5 shape is a **focus row** whose work landed under a commit that does not mention
it. Only a judgement can link the two, not a string match. The cheap leg already exists: the
draw's PREMISE CHECK prints spent-looking cited commits. The open question is why the orientation
that wrote focus row two read a retired row as queued. If it read `--list` or a `what` it had
written itself, the fix belongs in the orientation's reading of the store, through `live()`. It
does not belong in a new retire path. That fix is worth one bounded look before anything is built.

## 4. Why the orientation read them as queued: it read raw rows, because the brief gave it none

*Added by `the-orientation-read-two-retired-continuations-as-queued`, read from the orienting
session's own transcript (`3e3ca5e4-…`, started 14:25:43Z, `oriented_at` 14:23:11Z).*

The brief (`delivery_seat.build_brief`) had **no key for the continuation store**. At 14:26:23Z the
session read the store by hand:

```
from background import seat_continuation as s
for e in s._load(): print({k: ... for k in ('id','focus_id','what','not_before','do_not_draw_before','written_at')})
```

That is the raw store, and the projection drops `retired_at`. Both rows printed exactly like the live
`publish-the-20261004h-heads-arms-pair` beside them. Focus-row tombstones were distinguishable only
because their `what` says "tombstone"; a retired real continuation has no such marker in the columns
printed. The stretch-log row "outlived the commits that spent them" follows directly. Neither
`--list` (which prints `FINISHED`) nor `live()` would have said so.

**Fix (landed with this section):** the brief now carries `continuation_queue`, built through
`seat_continuation.live()` and `retired()`, as its third key, and the prompt renders it as two lists:
what the draw will offer, and what was retired this stretch. Printed at the real 14:23Z inputs, it
lists 3 offered rows and puts both disputed ids under RETIRED (12:58:38Z, 13:46:10Z). Control:
`tests/background/test_delivery_seat.py::test_a_RETIRED_continuation_reaches_the_brief_as_finished_and_never_as_queued`.
It covers the whole partition (one row offered, one retired), and it fires when `offered` is built
from `_load()`.

The 14:23Z record itself (the stretch-log row and focus row two) is unlanded orientation output in the
shared tree. It is left to the next orientation's `previous_wrong` grading, not edited here.
