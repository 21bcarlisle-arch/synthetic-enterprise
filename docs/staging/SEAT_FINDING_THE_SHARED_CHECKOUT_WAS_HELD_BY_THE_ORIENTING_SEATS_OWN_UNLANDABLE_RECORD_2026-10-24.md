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
