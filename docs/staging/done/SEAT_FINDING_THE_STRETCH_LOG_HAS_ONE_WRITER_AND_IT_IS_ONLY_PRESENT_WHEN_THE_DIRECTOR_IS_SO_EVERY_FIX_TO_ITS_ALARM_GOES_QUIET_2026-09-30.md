**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The stretch log has one writer, and it is only present when the director is — so every fix to its alarm goes quiet within a week

**2026-09-30, on the director's instruction: "Don't patch it again. Find why every fix to it goes quiet
within a week."**

## The pattern, measured

| stoppage | silent days | what resumed it | the fix made then | what the fix changed |
|---|---|---|---|---|
| after 09-07 | 09-08..09 | the director noticing (09-10) | `eb12cbeb1` / 09-10 | the alarm's CHANNEL (log → `notify`) |
| after 09-10 | 09-11..15 | the director present (09-16) | 09-16 | the alarm's HOST (publisher → supervisor tick) |
| after 09-18 | 09-19..22 | the director present (09-23) | `1d38d1d81` / 09-18 | the alarm's TRIGGER (completion → clock) |
| after 09-25 | 09-26..30 | — | — | — |

**Every fix changed the detector or the alarm. None changed who writes.**

Every entry in the log's history was written by an INTERACTIVE session in this seat. Across
September, no entry was written on a day with no director console session (09-11, 09-20..22,
09-28), and most console days have none either (09-01..05, 08, 09, 15, 19, 26, 27, 29, 30): the
interactive seat writes one only when it closes a stage-sized piece of its own. The autonomous turns
— about 95% of the burn (worker_tick and seat_executor, `tools/tick_burn_rate.py`) — have no duty to
write it.

## Why the alarm cannot close the gap, by construction

- **Detection works.** `python3 tools/stretch_log.py --check` today: ESCALATED, 121.4h and 330
  commits since the last entry, the largest gap the log has had.
- **It pages once, then is suppressed by design.** `raise_stretch_report_owed` keys the page to the
  newest entry's stamp, so a log that stays silent is an unchanged state: 2,139 consecutive firings
  without a state change, paging suppressed since 2026-09-17.
- **The escalation is routed back to the absent writer.** Its staged finding
  (`WORKER_FINDING_REPEATING_ALARM_STRETCH_LOG_2026-09-17.md`, 14 days) appears in the supervisor
  log 2,813 times as "Work identified for the **pull-loop** to deliver". The pull-loop is the
  INTERACTIVE seat's Stop hook, so it delivers only when the director is at the console. Even then
  the finding is one name in a comma list of "unprocessed staging", behind a primary item (37 owed
  reds).

So a fix lands on a day the director is present, the interactive seat is writing, and the log looks
fixed. When he steps away, the only writer is gone. The alarm pages once, goes quiet on purpose,
and hands its work to the queue of the session that is not running. **Within a week is simply how
long it takes the director to be away for a few days.**

## The reflection the log exists to hold is already written — somewhere else

The delivery seat's ORIENTATION (`background/delivery_seat.py`, autonomous, every 3h) writes exactly
what the log is for — `thesis_read` (what the stretch MEANS, "say plainly if it went backwards"),
`wrong` (what the machine got wrong, graded against last stretch), `not_now` (what was rejected and
why) — and every one is appended to `docs/direction/decisions.jsonl`: **14 orientations since 09-25,
232 rows in all.** Its charter forbids it to write any other file, so it cannot write the stretch
log. Two records of the same reflection exist. The one with an always-present writer is not the one
the check reads.

## What would close it (recommended, not built in this commit)

**Make the always-present writer the log's writer.** Each orientation appends its `thesis_read`,
`wrong` and `not_now` to the stretch log as a dated entry (append-only, one writer), rendered from
the `decisions.jsonl` row it already writes. The interactive seat keeps adding entries when it closes
a piece. The `--check` then reads a log whose writer cannot be absent, and a check that goes ESCALATED
means orientation itself stopped, which is a real fault rather than the director being away.
Rejected alternative: retire the log and read `decisions.jsonl` directly. That loses the one
readable page the director reads, and the check that reads it.

The general lesson, for anything else built this way: **an alarm whose remedy is a person must route
to a writer who is always present, or it is a notification about the director's absence.**

## Disposition (2026-09-30) — enacted

The recommended remedy is built: 46ddd0e9d made each oriented run the log's writer. The commit that
archives this document makes skipped runs write too and routes the page to the seat, and it delays
the clock page to two orientation periods so the healthy writer's own lateness does not page.
Details are in `done/WORKER_FINDING_REPEATING_ALARM_STRETCH_LOG_2026-09-17.md`.
