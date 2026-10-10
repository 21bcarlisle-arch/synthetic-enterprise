**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The draw's refusals, and its draws of parked atoms, reach only the supervisor journal

*Console seat, 2026-10-07, from the triage of the delivery seat's carried "what it got wrong" items
(`docs/direction/wrong_triage.yaml`). Three carried items share one cause, so they share this home.*

## The cause

The supervisor decides what is drawable, and when it refuses or keeps drawing something the seat
did not expect, it says so in its own journal. The seat steers from its brief, and the brief does
not read that journal. `atoms_stalled_with_reason` in `background/delivery_seat.py` now prints a
stop reason for stalled atoms that were drawn or are in focus. That is one leg. Refusals of Lane 0
items, and exclusions of atoms that are in neither set, still reach nobody.

## The three defects

1. **The held-work check refuses a Lane 0 item when its prose names a held file**, even when the
   held work is not the item's work. The refusal goes to the supervisor log only, so a focus item
   is never drawn and the seat is not told. On 2026-10-04 two of four focus items were lost this
   way. Carried as `the-held-work-check-refuses-by-prose-and-tells-only-the-log`, 27 listings.

2. **The coupled-triad gate excludes an atom from every BUILD draw, and says so only in the
   journal.** PB4 cost 2,275 wasted draws this way. W2_34, then nine more twinless L3 targets
   (fixed by `873d09651` and `6314e5bc8`), then W2_20 on 2026-10-07 (`8af70203f`), which reached
   the seat only because a worker wrote it into a finding. Carried as
   `a-coupled-triad-refusal-reaches-only-the-supervisor-log`, 10 listings.

3. **A parked atom is still drawn.** `_record_atom_draw_and_check_stall` increments
   `consecutive_unchanged` once per real draw. H45 (parked 2026-10-04) went from 950 to 1,266, and
   PB4 from 2,417 to 2,837, while PB4's work went through Lane 0 slices. Whether each draw spawns a
   tick is not established. Carried as `a-parked-atom-is-still-drawn`, 11 listings.

## What done means

- Every draw refusal of a focus item, Lane 0 or atom, with its reason, is in the brief the next
  orientation reads.
- A parked atom is not drawn, or the brief says why it was. The first step is to measure what one
  of these draws costs: one tick, or one counter bump.

Each leg needs a control that can fail: a focus item refused by the held-work check that must
appear in the brief, and a parked atom in a fixture map that the draw must not select.

## Outcome, defect 1 (worker, 2026-10-10)

Built under focus item `a-held-work-refusal-of-a-focus-item-reaches-the-brief`. Defects 2 and 3
remain open.

**The refusal now reaches the brief.** `delivery_lane.draw` writes every held-work refusal to
`docs/observability/.delivery_lane_claims.refusals.json`. Each row records the id, holder,
artefact, contested subject, first and last refusal, and a count. The file is gitignored like
the draw ledger beside it. `delivery_seat.build_brief` carries the refusals as
`previous_focus_refused`. `_prompt` prints them directly under "did last stretch's focus reach the
draw", so a focus item that was walked past no longer reads as one the draw passed over.

**The path leg refuses only on a path the item asks to change.** `held_grade` refuses when a
held path sits under an explicit change verb (`_paths_asked_to_change`, using the same
nearest-governor walk as `_path_roles`). A held path the prose names under a read verb, or under
no verb, is context. The item is drawn anyway, and the doorbell prints
`HELD-WORK CHECK, CONTEXT ONLY, NOT REFUSED` with the holder named. The identifier leg is
unchanged.

**Why the change vocabulary's own subject side was not enough.** `_path_roles` counts an
ungoverned path as a subject, because the ledger must fail by under-crediting. On the
2026-10-09 evidence that reading is exactly backwards. In
`the-seats-direction-record-reaches-origin`, `docs/direction/DIRECTION.yaml` is ungoverned
("Origin's docs/direction/DIRECTION.yaml is still the 14:20 record"), so `_path_roles` reads it as
a subject. Its real work, `background/delivery_seat.py`, is governed by `from`, so it reads as a
mention. So the refusal at 21:28Z was not justified: the contested path was context. Under the
new rule it is annotated, not refused.

**The cost, measured before landing.** Across the distinct focus items in the last 30 revisions
of `DIRECTION.yaml` (65 items, 108 confirmed path mentions), 45 mentions sit under an explicit
change verb. 19 items name paths but would never refuse on the path leg. For those items a live
holder now produces an annotated draw instead of a refusal. That is the side this check is
allowed to be wrong on. A wrong refusal is silent and repeats on every draw, while a wrong draw
happens once and the doorbell names the holder.

**Controls** (`tests/background/test_delivery_lane.py`). In
`test_a_context_only_mention_is_drawn_and_a_path_it_asks_to_change_is_still_refused`, the
evidence item is drawn while an edit of the same held file is refused. It reds under both
`asked = set(shared_paths)` and `asked = set()`.
`test_a_held_work_refusal_reaches_the_seats_brief` reds when `record_held_refusals` is dropped
from `draw`, and when the `previous_focus_refused` block is dropped from `_prompt`.

## 2026-10-10: a held path is graded by its copy, not only by being there

**The defect.** cf8706023 made refusals visible, and the first one it showed was false.
`the-arrears-like-for-like-is-a-tracked-tool` was refused 58 times. The last refusal was at
02:25Z, and the work had already landed by another route as 84d782864. The holder was
`.claude/worktrees/agent-a5cc99fa24f34feed`. Its only claim to `docs/market_research/debt_and_collections.md`
was an UNTRACKED copy last written at 2026-10-05 03:39, of a file origin has tracked for days.

**Why the lease called it live.** Its `.se_worktree_owner` names pid 2197437, the interactive
worker session that has been running since 2026-09-25. That session's `renew_claims.sh` touches every marker naming it,
every ten minutes. Measured 2026-10-10 ~04:00: 101 worktrees read as live holders, 99 of them on that
one pid. Between them they hold 355 paths, 10 of which are untracked copies of paths origin
tracks. So the lease says the session is alive. It does not say the worktree is being worked.

**The repair** (`background/delivery_lane.py`). `_worktree_subject` now grades each held path's
copy: untracked or not, whether origin/main tracks the path, and its mtime. `_stale_copy` names two
shapes as a stale sibling:
1. an untracked copy of a path origin/main tracks;
2. a copy last written before the item's own `written_at`.

A stale asked-to-change path does not refuse. It goes to the doorbell as
`HELD-WORK CHECK, CONTEXT ONLY` with the text `holds a STALE copy of <path> (<reason>)`. A modified
tracked copy written after the item still refuses, and so does a copy that cannot be graded. Replayed
against the live holders, the 2026-10-10 item now draws, annotated.

**Control.** `test_a_stale_sibling_copy_is_drawn_and_named_and_a_live_modified_copy_still_refuses`
reaches both branches in one walk. It reds under refuse-always (`_stale_copy` returns `""`) and
under refuse-never (`_stale_copy` always returns a reason). Both mutations were run.

**What this does not reach.** Focus rows in `DIRECTION.yaml` carry no `written_at`, so only shape 1
reaches them. A MODIFIED tracked copy in one of the 99 renewed worktrees, idle since September,
still refuses any focus item that asks to change that path. The remedy is to stamp a `written_at`
on focus rows, which the direction writer owns. I did not reap the worktree.

## 2026-10-10: focus rows now carry `written_at` (item `focus-rows-carry-a-written-at-so-a-stale-held-copy-is-graded-by-age`)

`delivery_seat.stamp_focus_written_at` runs on the seat's record path after the session's record
is validated and before it is parsed and committed. A row whose id, `what` and `why` match the
previous record keeps that row's stamp; a new or reworded row is stamped with the orientation's
time. An unchanged row the previous record never dated stays UNDATED, so the age leg cannot grade
it and it refuses as before. That is deliberate. A stamp later than the true writing would grade a
live holder's earlier write as stale and release a refusal it should keep. So today's four rows
gain a date only when they are reworded or replaced, and the records become dated as the focus
turns over. Nothing is backfilled. A record with no stamp to move is not rewritten.
`_stale_copy` reads the stamp through `unreachable_focus` unchanged. The control
`test_a_focus_row_is_dated_when_written_and_keeps_its_date_while_unchanged` covers new, kept,
reworded and undated rows in one stamp, plus the age leg's release and refusal. It reds under
no-carry, carry-always, and dropping the `why` comparison.
