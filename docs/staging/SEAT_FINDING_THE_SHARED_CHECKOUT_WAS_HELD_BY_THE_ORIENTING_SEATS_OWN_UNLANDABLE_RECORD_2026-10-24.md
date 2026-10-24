**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The shared checkout was held 104 behind by the orienting seat's own record, which could not land for five orientations (2026-10-24)

## The premise, re-measured

Drawn as `the-shared-checkout-reaches-origin`. At 07:18Z the shared tree was 104 behind origin and 0
ahead, with 26 paths refusing the fast-forward. Read with `origin_reconcile`'s own per-path verdicts
(superseded, carried, and orphaned), 23 of the 26 the reconciler clears by itself. Three really held:

| path | why it held | owner |
|---|---|---|
| `tools/read_instruction_arms.py` | the D48 gas-floor draft. It landed in reworked form in 8473e7a1f, 14 lines not on origin, 5 conflicts | gas-floor lane, finished |
| `docs/status/SEAT_STRETCH_LOG.md` | 9 orientation entries not on origin, 1 conflict | `delivery-seat.service` |
| `docs/direction/DIRECTION.yaml` | 5 orientations' focus, 2 conflicts | `delivery-seat.service` |

The rival claim `a-movers-final-bill-is-measured-against-the-rules` is different work. It names
the same billing files only because they sat in the blocking list.

## The cause

`delivery-seat-log.md`, which records every orientation from 23 Oct 17:30Z to 24 Oct 05:32Z:
`landing refused (DirectionNotLanded): SEAT_STRETCH_LOG.md on origin/main is not kept whole by this
tree's copy (it is neither origin's copy nor the shared HEAD's copy plus one inserted block)`. The
check is right to refuse: the copy held several orientation blocks, and origin's stretch-log commits
from other lanes sat at the same insertion point. But nothing ever did the "hand landing that keeps
both sides". Each new orientation added another block, so the copy got further from "plus one
block". And because its files stayed dirty, every advance was refused. **That is a closed loop:**
the seat cannot land until the tree advances, and the tree cannot advance until the seat lands.

## What was done

- `tools/read_instruction_arms.py`: `refresh_to_head --base origin/main --write`, graded
  `refreshable [predates_landing_carrying_some]`. The bytes were preserved again under
  `refs/preserved/refresh-to-head/shared-checkout-reaches-origin-2026-10-24`, beside
  `refs/preserved/gas-floor-shared-copy/read_instruction_arms.py` (blob 0775076517).
- The direction record was hand-landed with both sides kept. Stretch log: origin's 12 entries and
  the shared copy's 9 orientations, interleaved newest-first by date. Entries carry dates only, so
  the order within a day is approximate. A line-multiset check shows no line from either side
  lost. `DIRECTION.yaml`: both conflicts were the same row (`switch-ons-that-pass-their-prereg`),
  resolved twice. Origin's resolution was kept, because the switch-on it reports has landed
  (82f4b20bc). The one row origin has that the copy drops, `your-22-oct-front-door-steer-lists`, was
  answered on 22 Oct and was aged out by the seat. `decisions.jsonl` and `wrong_triage.yaml` are
  the shared copy, since origin has not touched them since HEAD. `site/data/delivery.json` was
  regenerated against origin.

## What is still owed

The loop will close again at the next orientation that finds a stretch-log commit from another
lane on origin. The fix belongs in `delivery_seat.land_direction_on_origin`: when the refusal is
"not origin plus one block", the seat's own blocks are dated `## <date> — orientation:` entries.
Re-inserting them onto origin's copy is mechanical, so the seat could do the keep-both landing it
currently asks a person for. This is not built here.

## Reversal

`git revert` of the landing restores origin's copies. The shared copies the seat wrote are on the
shared disk until the advance, and the reconciler preserves them on its refs.

## Correction, same turn: on `DIRECTION.yaml` the copy wins, not origin

After the keep-both landing, `DIRECTION.yaml` was the only path still holding the advance. It
differed from origin in nothing but that one row's resolution wording and its `resolved:` date.
No door enacts "origin wins" on a YAML replacement (`refresh_to_head` grades it
`refused_replacement_no_landable_hunk` even with `--base-wins`), and the clock is short: the 08:20Z
orientation would find its stretch-log copy still not "HEAD plus one block" (it edits a line of
HEAD's copy, which was measured) and would refuse again. So the shared copy's bytes were landed
as they stand. The ruling is the same in both wordings. What is lost is the `resolved:
'2026-10-23'` date on `switch-ons-that-pass-their-prereg`. Nothing in `background/` or `tools/`
reads it.

`site/data/delivery.json` was refreshed on the shared tree under `--base-wins`, which the clock
admitted. Its bytes are preserved on `refs/preserved/refresh-to-head/shared-checkout-reaches-origin-delivery-json`.
The two `advisor/done/` copies are earlier-revision twins of 845c69188, a class
`origin_reconcile` clears by itself.

## The last holder was a staged rename, and that is a reconciler defect

With every copy graded clearable, `origin_reconcile` still refused, at 07:51Z and again at
07:56Z, on 13 paths. Its own detail named the cause: `clearing the byte-identical twin
advisor/done/DIRECTOR_READING_PLAN_TIER_LOWERED_USAGE_0PCT_2026-10-23.md failed (error: the following
file has staged content different from both the file and the HEAD)`. A worker tick on 23 Oct had
staged `git mv advisor/X advisor/done/X` for two advisor files and never committed. So the index
held HEAD's original blob at the `done/` path, the disk held origin's 845c69188 revision, and
`git rm` refuses that state without `-f`. Both blobs are in history (HEAD, and 845c69188), so
nothing was unique. `git restore --staged` on the two `done/` paths dropped the index entries and
left the disk alone. The next `origin_reconcile` returned **FAST_FORWARDED, 113 → 0**. It preserved
the stretch-log copy on `refs/preserved/origin-reconcile-superseded-live/origin-reconcile-6bf8e621af`
and carried `household_budget_w2_4.md`'s live edit across onto origin's copy.

**Owed:** the twin-clearing leg should unstage an index entry whose blob is HEAD's or an earlier
origin revision before it removes the path, instead of failing the whole all-or-nothing advance on
it. A staged-but-uncommitted `git mv` to `done/` is the advisor draw's normal shape, so this will recur.

**Paid, 2026-10-24.** `restore_tracked_twin` now asks `_staged_blob_refusal` about the index entry
before it touches a path. An index blob that equals the disk's or HEAD's at that path, that HEAD holds at
any path (a staged rename's source), or that origin wrote at that path is dropped (`git rm --cached
--force` for a staged add). Any other blob refuses that twin by name, and the index entry is left alone. This
incident's shape is reproduced in real git in
`tests/background/test_origin_reconcile_earlier_revision_twin.py`: before the fix it reproduced the
07:51Z refusal word for word, and after it the tree advances. A second test covers the other side of the partition: a novel
staged blob still holds the tree. Three mutations each fire: drop `--force`, drop the HEAD-tree leg,
or let the refusal always pass.
