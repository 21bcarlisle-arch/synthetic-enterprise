# PREREG — what replacing the ORDER 60 mtime tie-break with an attention term does to the live band

**Severity: LOW** — a pre-registration owes nothing; it is the record that the prediction was
written before the answer was known. The finding it belongs to is the ORDER 60 inversion measured
in `15e61d604`.

Filed 2026-09-24 by the delivery seat, before running anything.

## The question

`background/staging_rooms.work_queue()` sorts by `(rank, mtime, path.name)` at all four sort
sites. For `KIND_ALARM` (rank 60) `mtime` is ascending, so **oldest write first**. An alarm
document is rewritten by its own machinery on every firing — `_note_still_live` appends a dated
line, `_refresh_counts` rewrites the header — so for this population mtime measures *how recently
the alarm wrote*, not *how long since anyone looked*. The two are anti-correlated: the condition
that fires most has the newest mtime and therefore sorts LAST.

The replacement term: **time since anyone LOOKED**, ascending on the instant of last attention, so
the longest-neglected document draws first.

The only recorded attention events on an alarm document are the re-ask lines under
`alarm_repetition.REASK_HEADING` (`## Re-asked`) — and that section is deliberately excluded from
`_observation_dates`, precisely so "somebody looked" cannot masquerade as "the condition held"
(the comment at `alarm_repetition.py:538`). A document that has never been re-asked has not been
looked at since it was FILED, so the fallback is the filing date in the filename, which no firing
moves.

**Measured before predicting, and stated because it makes the prediction sharper:** zero of the ten
live alarm documents in `docs/staging/` carry a `## Re-asked` section today. The re-ask landed
2026-09-23 and has not been applied to this population. So today the new term degenerates to
**filing date ascending, name breaking exact ties** — which is what the band's own docstring always
claimed mtime was giving it ("AGE decides within it") and never was.

## Predictions, written now

1. Under today's term (mtime asc) `DEADMAN_WORKTREE_UNDECLARED` is **10th of 10** in the band.
2. Under the attention term it is **2nd of 10** — filed 2026-09-15, one of five that day, second
   by name after `DEADMAN_ORIGIN_FORK`.
3. `OPERATIONAL_LAYER_SIGNAL` (filed 2026-09-23, the newest) moves to **10th of 10**.
4. The two orders are close to REVERSES of each other: I predict Spearman rank correlation
   between them is **negative**, and at least 7 of the 10 documents change position.
5. Editing the body of any one of these documents by hand — the seat repairing a header, which is
   what moved `SEAT_CONTINUITY` 30 → 34 in `15e61d604` — changes its position under the old term
   and does **not** change it under the new one.

## What would refute this

Prediction 4 is the one carrying the claim. If the correlation is positive, the two terms are not
anti-correlated on the live population and the argument for the swap rests on prediction 5 alone —
which is a real defect but a smaller one than "the loudest alarm is always last".

## What I will NOT pin

No control asserting "body text does not affect rank". That keys to today's answer and would red
the day the ranking becomes content-aware, which is the direction the map is going.
