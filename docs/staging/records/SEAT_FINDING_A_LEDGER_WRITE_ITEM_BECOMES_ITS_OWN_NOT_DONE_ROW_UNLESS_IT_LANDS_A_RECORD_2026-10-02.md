**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery · **Claim:** `bind-the-ledger-row-of-a-bind-that-was-a-ledger-write`

# A ledger-write item becomes its own `not_done` row unless it lands a record

**Done.** `bind-the-spent-tou-lane-0-row` now reads `premise_spent` on `8c29e03d9`, written by
`python3 -m background.delivery_lane --premise-spent bind-the-spent-tou-lane-0-row 8c29e03d9 <reason>`
at 18:59Z on 2026-10-02. Its subject row, `the-tou-first-bill-is-graded-against-the-cap-at-its-assumed-split`,
already read `premise_spent` on the same commit (written 14:20Z). I re-read both in
`delivery_seat._drawn_never_landed(now)` straight after the write. Both rows now read
`premise_spent`, and the only `not_done` row left in the horizon is
`grade-the-value-arms-retaken-at-the-belief-commit`.

**Draw notes.** The draw flagged `8c29e03d9` as already on origin. That is correct and is
what this item records: the disposition, not a fresh piece of work. The duplicate-work note
named this same id. Its `claimed_at` (18:58:45Z) is this draw's own write. `ps` showed only this
process carrying the prompt and no rival `surgical_land` on the subject, so no `--landed-under`
or `--release` of a second id applies. `background/delivery_lane.py` at HEAD is identical to
origin/main, so the writer that ran is the trunk's.

**The regress.** This is the second generation of one shape. A row whose work was a ledger write
has no commit for `--landed` to find. So the brief lists it as `not_done`, and the item minted to
dispose of it is *also* a ledger write. That new item lands nothing in turn, and the next brief
lists it. This file is the commit that breaks the chain for this generation. A fix to the class
would let `--premise-spent` or `--landed-under` close the drawing claim's own row in the same call.
That change is not made here: it is a change to the binder's semantics, and the item asked for
nothing else.
