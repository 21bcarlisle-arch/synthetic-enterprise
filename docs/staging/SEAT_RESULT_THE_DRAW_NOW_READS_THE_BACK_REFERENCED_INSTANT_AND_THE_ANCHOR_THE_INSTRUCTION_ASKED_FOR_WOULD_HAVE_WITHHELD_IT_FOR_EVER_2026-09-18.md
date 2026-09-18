**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, the
draw's embargo guard

# The draw now reads the back-referenced instant — and the anchor the instruction asked for would have withheld the item for ever

**Filed:** 2026-09-18 · **Claim id:** `the-draw-cannot-read-an-instant-the-disposition-already-can`
**Subject:** `background/delivery_lane.py::embargoed_until`, `::_prose_anchor`,
`::_without_quoted_spans`, `::_back_referenced_start`
**Established against:** `38f9ff0cb` (working tree at the draw; `background/delivery_lane.py`
identical to HEAD before this change)

---

## What was asked, and what landed

The draw's guard `_embargoed` read `_EMBARGO` — the dated grammar — and nothing else, while
`_back_referenced_start` (the third live spelling, *"ETA near 03:58; do not draw this before then"*)
was wired only to the after-the-fact disposition that stamps `premise_not_yet_ripe`. So the lane
could say precisely why `read-the-next12-twelve-alone-once-the-0358-run-settles` was hopeless from
the moment it was handed out at 00:07 on 2026-09-18, and could not decline to hand it out. One
100-minute window, spent.

Both spellings are now read at draw time, by the same resolver, and `--embargoed` names both.
Proven on the real record rather than on a fixture: at the actual 00:07 draw the burning item now
reads HELD until 03:58, at 04:30 it reads drawable, and at 21:00 it still reads drawable.

## Two things the one-line wire could not have survived, and both were found by measuring

**1. The instructed anchor is the defect it was meant to prevent. `now` cannot work here.**

The drawn item says to anchor on `now` "rather than on a draw that has not happened". The
resolution rule is *the first occurrence of that clock time at or after the anchor* — an ETA is in
its item's future by construction. Anchored on `now` that rule never stops being satisfied: at 03:00
a 03:58 stamp resolves to 03:58 today and the item is correctly withheld; at 04:30 it re-resolves to
03:58 **tomorrow** and the item is withheld again — at that draw, and at every draw after it, for
ever. That is not a missed stamp costing one invocation. It is the silent permanent withholding of
work that `embargoed_until`'s own docstring calls the worse of the two failures and that `draw`'s
six-day walkover already paid for once.

The anchor must be a fixed instant in the past, and the only honest one is **when the prose was
written**. Both stores can answer: a continuation entry carries `written_at`; a focus row is
re-derived wholesale at each orientation, so the direction record's `oriented_at` is when its prose
was written — and `unreachable_focus` already returns nothing once that record goes stale, so an
anchor read that way is never older than the row it dates. No anchor means no back-referenced
embargo, which is the fail-open side.

*The prediction this refutes was the instruction's own, and it is left standing beside the result:
the instruction reasoned correctly that the disposition's anchor was unavailable to the draw, and
then named the one substitute that cannot expire.*

**2. Without a use/mention guard, this repair's own claim embargoes itself.**

`embargoed_until` argues that the dated grammar "cannot manufacture a false embargo from rhetoric
about the past" — true, because a quoted **date** is absolute and has been and gone. A quoted
date-**less** clock has no such protection: it re-resolves into the future against whatever anchor it
meets, so a sentence *about* the grammar is indistinguishable from the grammar itself.

Measured over the live continuation store (282 entries, 2026-09-18) — exactly two carry the
spelling, and they are the discriminating pair:

| entry | text at the instruction | quote marks in the whole entry | correct reading |
|---|---|---|---|
| `read-the-next12-...-0358-run-settles` | `... ETA near 03:58; do not draw this before then, the file will not exist` | **none** | HELD until 03:58 |
| `the-draw-cannot-read-an-instant-...` | ``resolves "ETA near 03:58; do not draw this before then" and has exactly ONE caller`` | `"` around the phrase | drawable |

`_without_quoted_spans` blanks balanced single-line `"…"` and `` `…` `` spans with spaces of equal
length — equal length because the resolver looks *backward* from the instruction by character count,
so the reach must keep measuring the same prose. Its failure directions are asymmetric in the right
way: blanking too much leaves no candidate and resolves to `None` (fail open, one invocation), while
an unterminated quote pairs with nothing and blanks nothing, so a stray `"` earlier in an item
cannot silently disarm a real instruction later in it.

Without it, the very claim this work was done under would have been withheld until 03:58 the
following morning — a guard whose first live application is to refuse the work that built it.

## The control, and what each mutation kills

`tests/background/test_the_draw_reads_the_back_referenced_instant_the_disposition_already_read.py`,
six legs. Every mutation was run, and each fires the leg written for it:

| mutation | fires |
|---|---|
| only the dated grammar is honoured (delete the wire) | 5 of 6 legs |
| anchor on `now` instead of when the prose was written | the anchor leg, the fail-open leg |
| drop `_without_quoted_spans` | the partition leg, the use/mention leg, the reader leg |
| drop the focus-row anchor (`written_at` only) | the focus-store leg |

**The anchor leg's first draft did not fire on its own mutation**, and that is worth recording
because the reason generalises. It advanced only the `now` *argument* — and `_embargoed(item, now +
offset)` hands its instant to the **comparison**, never to the **resolution**, so a resolver reading
`time.time()` answered identically at all four offsets. The mutation was still caught, by a
different leg for a different reason, which is exactly the flattering reading a mutation pass must
not accept. The leg now moves `delivery_lane.time.time` past the stamp, which is the only thing that
tells a fixed anchor from a moving one.

## One limit, named rather than left to be discovered

A focus row's anchor is the orientation that wrote it. If the seat copies back-referenced prose
forward into a **later** orientation after its instant has passed, the stamp is honoured again
against the new `oriented_at`. That is one wasted withholding per orientation, bounded by the
three-hour re-derivation and visible in `--embargoed`; it is not the unbounded case above. The
remedy if it ever fires is for the seat to drop a spent stamp when it re-writes the row, not for the
reader to start guessing which occurrence the author meant.

## Unrelated, found while running the neighbouring suites

`tests/background/test_a_window_that_closed_before_its_own_subject_existed_says_so.py` has **three
red legs at HEAD** — `test_THE_PARTITION_...`, `test_A_WINDOW_WITH_USABLE_TIME_...`,
`test_PROSE_THAT_STATES_NOTHING_...`. All three expect `evidence == ""` where
`disposition_of` now returns a `CANNOT ANSWER, not 'nothing landed'` string. Confirmed pre-existing
by running the identical suite against the unmodified file: same three, same assertions. Another
lane widened the residual's evidence and did not re-key these legs. Not touched here.
