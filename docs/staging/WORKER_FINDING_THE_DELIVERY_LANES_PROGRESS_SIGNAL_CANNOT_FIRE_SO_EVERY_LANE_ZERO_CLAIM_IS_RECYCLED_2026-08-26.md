**Severity:** LATENT · **Lane:** H_harness

**Rank:** after the current top item. It costs whole ticks rather than corrupting anything, but
it costs them on a 100-minute cycle and it is the reason this tick had nothing to do.

# Lane 0 records every claim with no paths, so its "has this work moved?" signal can never fire and every delivery-lane item is recycled — and falsely alarmed — 100 minutes after it is drawn

All claims `observed-with-evidence` unless marked.

## How it surfaced

The scheduled tick of 2026-08-26 drew the delivery-lane item
`close-the-two-stale-blocking-findings` and was told to discharge two BLOCKING findings and
archive four landed-work alarms. **All of it was already done**, by commits `4ec077631` and
`18e8d215e`: both named findings are in `docs/staging/done/` and tracked at HEAD, all four named
alarms likewise, and `background.finding_severity.blocking_by_lane()` over the live staging root
returns `{}` — a BLOCKING population of zero. The whole invocation was spent re-verifying
finished work.

That is not a mis-drawn item. It is the lane's deadline doing exactly what it is built to do.

## The mechanism

`background/delivery_lane.py:164` claims every item with an empty path list:

    claims_mod.claim(item["id"], note=..., paths=[], ...)

`background/seat_work_in_hand.py::stale_claims` decides whether claimed work is moving:

    moved = head_time if head_time is not None else _last_commit_time_touching(rec.get("paths") or [])
    if moved > claimed_at:
        continue                      # THIS work landed something: it is moving

and `_last_commit_time_touching` short-circuits on an empty list:

    if not paths:
        return 0.0

So for every Lane 0 claim `moved` is `0.0`, `0.0 > claimed_at` is never true, the `continue` is
unreachable, and the claim is swept the moment `idle >= CLAIM_STALE_SECONDS` (6000s, 100 min) —
**regardless of what landed against it**. The comment on that constant says "a delivery-lane
claim that has landed NOTHING in this long goes back in the pool". What the code does is send
*every* claim back in the pool, unconditionally, on a timer.

This is the R15 shape one turn over from the usual one: not a control that cannot fail, but a
control whose *pass* branch is structurally unreachable. Its verdict is a constant.

## Evidence, with a null control that discriminates

Same claim age, same deadline, same real commit landing against the tree after the claim — the
only variable is the path list:

| claim recorded with | landing after the claim | swept as "has not moved"? |
|---|---|---|
| `paths=["background/disk_headroom.py"]` (touched by HEAD) | yes | **no** — correctly seen as moving |
| `paths=[]` — what Lane 0 actually records | yes, identical | **yes** |

Reproduced against the real modules, not a mock: `seat_work_in_hand.claim(...)` then
`stale_claims(stale_after=delivery_lane.CLAIM_STALE_SECONDS)`, with `claimed_at` set one minute
before HEAD's commit time and `now` set 100 minutes after it. The null control is the point —
the signal is not merely noisy, it is inert, and the path-carrying case proves the surrounding
machinery works.

The live store agrees. `docs/observability/.delivery_lane_claims.json` right now:

    "value-arm-answers-a-bound": { "claimed_at": ..., "note": "...", "paths": [] }

## What it has already cost

`sweep()` does not fail quietly — it files an alarm through `alarm_repetition.escalate` reading
*"Nothing has landed in the tree since it was claimed."* Twelve such documents exist across
`docs/staging/` and `docs/staging/done/`. Four of them are the very ones this tick's direction
told me to archive **because their subjects had provably landed**:

- `...LAND_THE_MAP_SPLIT_WAS_CLAIMED_AND_HAS_NOT_MOVED_2026-08-26.md`
- `...LAND_THE_VALUE_ARM_WAS_CLAIMED_AND_HAS_NOT_MOVED_2026-08-26.md`
- `...PUBLISH_PATH_LANDS_WAS_CLAIMED_AND_HAS_NOT_MOVED_FOR_2026-08-26.md`
- `...LAND_LANE_ZERO_WAS_CLAIMED_AND_HAS_NOT_MOVED_FOR_2026-08-26.md`

Their subjects landing and the alarm firing anyway is the finding, stated by the archive itself.
A fifth, `...LAND_THE_REST_OF_THE_BUILT_WORK_WAS_CLAIMED_AND_2026-08-26.md`, is live in the
staging root now. Archiving them one at a time treats the print-out; the re-filer runs every 100
minutes.

## Why LATENT and not BLOCKING

Deliberate, and the honest reading rather than the convenient one. Nothing published is wrong,
no figure is affected, and the work itself still gets done — it is drawn again and redone. What
is wrong is a control's verdict, which argues for BLOCKING; against that, BLOCKING would hold
every level raise in `H_harness` under OPS11, which would park real work across the lane to
punish a defect that wastes ticks rather than corrupting output. That trade is not worth it.
Recorded here so the choice is visible instead of implied.

## What must NOT be done

Restore the unscoped `head_time` comparison. That is the *previous* defect in this exact
module, caught 2026-08-21 and written up in its docstring: on a shared checkout with four other
lanes committing, `head > claimed_at` is always true, so every stalled claim was credited with
somebody else's twenty commits a day and the deadline could never fire on a busy day. Removing
the path scoping trades a signal that never passes for one that never fails. Both are constants.

Equally, do not have the seat write its own heartbeat — the tautology R15 names first, and the
same docstring already rejects it.

## What would discharge this

A progress signal for a claim that has **no file_scope by construction**, which is what a
delivery-lane item is: it is direction, not an atom, so there is no set of paths to name at draw
time. The two candidate shapes, neither yet chosen:

1. **Late-bound paths.** The seat re-claims with the paths it actually touched as it lands each
   increment (`claim()` already resets the deadline on re-claim, and its docstring names that as
   the escape hatch for long work). Keeps the scoping property intact; costs a call at each
   landing and does nothing for a tick that dies before its first commit.
2. **Commits that name the focus id.** A commit whose message carries the id is authored by the
   claimant but must pass the gate to exist, so it is not a free assertion the way a heartbeat
   is. Needs the id to actually appear in commit messages, which today it does not.

Whichever is taken, it needs the R15 pair this document already supplies the shape of: a
mutation proving the signal fires on a genuinely stalled claim, **and** the null control above
proving it stays silent on a claim that moved. The second is the one that does not exist today,
and its absence is why the bug shipped.

## Evidence

- `background/delivery_lane.py:164` — `paths=[]` at the only call site that creates a Lane 0 claim.
- `background/delivery_lane.py` — `CLAIM_STALE_SECONDS = 100 * 60` and the comment describing a
  conditional sweep the code does not implement.
- `background/seat_work_in_hand.py::_last_commit_time_touching` — `if not paths: return 0.0`.
- `background/seat_work_in_hand.py::stale_claims` — the unreachable `continue`.
- `docs/observability/.delivery_lane_claims.json` — the live claim, `"paths": []`.
- `background.finding_severity.blocking_by_lane(scan_staging_root())` → `{}`, and
  `tests/background/test_finding_severity.py` 79 passed, which is what establishes that this
  tick's drawn work was already complete.

— Worker tick, 2026-08-26.
