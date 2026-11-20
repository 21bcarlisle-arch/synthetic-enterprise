# Three empty turns, then stop: the practice, and how the executor holds it

**Knowledge:** none -- this is practice for building the harness, not a market topic. It is published through the reading log (`docs/institutional/reading_log.md`, Osmani row of 20 Nov 2026) and read by `background/seat_executor.py` (`EMPTY_TURNS_BEFORE_STOP`).

**K8 page** for the "Also" item of the director's steer of 20 Nov
(`docs/staging/advisor/done/DIRECTOR_STEER_GATES_JUDGE_FROM_THE_BASE_PROPERTY_TESTS_FOR_BILLING_AND_DIFF_TRIGGERED_CHECKS_2026-11-20.md`),
built from `docs/staging/SEAT_FINDING_NOTHING_ON_THE_LIVE_EXECUTOR_STOPS_AFTER_THREE_FAILED_ROUNDS_AT_ONE_ITEM_2026-11-20.md`.

## 1. What practice says

- **"A failing check after three rounds brings in a human."** Addy Osmani, "How the Claude Code team
  thinks about verification" (17 Nov 2026), as relayed by the director's advisor. The number is the
  practitioner's. No published evidence was found that three is better than two or five; it is a
  convention, and this page treats it as one.
- **A loop needs a holder and a limit** (Mc Gowan, "Autonomy is not one slider", 20 Nov, same reading
  log). An agent that retries without limit is over-reach that never shows up as a complaint.

## 2. What is true here

The live route, `seat_executor.run_once`, logs `LANDED NOTHING` when the item's bound paths did not
move, and then offers the item again with no count. Over `docs/observability/seat-executor-log.md`
(2 Sep to 20 Nov, 1,923 graded turns over 1,332 ids), 34 ids reached three empty turns in a row. One
of them reached 43.

## 3. The pre-registration, graded

The finding filed two claims before the build: over the logged history, the rule (a) suppresses at
least 89 turns, and (b) refuses no id that later landed within its next three turns. Graded on
20 Nov by a one-off replay of the log, line by line per id (`LANDED NOTHING` counts, `FINISHED`
resets), the same counting `seat_executor.empty_streaks` now does live:

- **(a) holds.** 89 empty turns come after a third empty turn with no landing in between. Counting the
  deferred landing turns as well, the figure is 105.
- **(b) is refuted.** 16 of the 34 stopped ids landed within their next three turns: 11 on the
  fourth or fifth turn and 5 on the sixth. The rule would have held those 16 landings until the
  item was rewritten. The claim was wrong and stays here, next to its result.

The same replay at other thresholds:

| Stop after | Stops | Empty turns saved | Landings held for a rewrite | Stops never followed by a landing |
|---|---|---|---|---|
| 3 | 34 | 89 | 16 | 18 |
| 4 | 21 | 68 | 8 | 13 |
| 5 | 7 | 61 | 2 | 5 |
| 6 | 5 | 56 | 0 | 5 |

Most of the saving comes from a few long runs. A threshold of 5 keeps 69% of the saving (61 of 89)
and holds 2 landings instead of 16. The replay cannot show how much sooner a filed finding would
have produced those 16 landings. A "landing held" is a delay until someone looks, not a loss.

## 4. The design choices, and why

1. **The threshold is 3, because the steer says three.** Section 3 suggests 5 would hold fewer
   landings and keep most of the saving. But what a held landing costs is how long the item waits
   for its rewrite once the finding is filed, and the replay cannot see that. So this is not yet a
   question for the director. It is measured first (GAP below). The constant is in one place, so a
   change is one line.
2. **The count is read from the executor's own log, so there is no new store.** `LANDED NOTHING`
   adds one to an id's run and `FINISHED` (the bound paths moved) resets it to zero.
3. **The stop is a skip in `delivery_lane.next_item`, and it is not a deletion.** The skip works like
   an embargo: the walk goes on to the next item. It covers both the continuation source and the
   focus source, so dropping one of the two copies cannot bring the item back.
4. **What releases it is a rewrite or a landing. The clock never does.** The id is offered again
   when its row's `written_at` is later than the last empty turn (the seat rewrote it, or wrote a new
   continuation), or when a landing is bound to the id after that turn by another route. A clock
   expiry would bring back the 43-turn night, one window at a time.
5. **The third turn files one finding.** It goes through `alarm_repetition.escalate` with the key
   `three-empty-turns:<id>`, so every stopped id is listed in one living document. The document
   quotes the three `LANDED NOTHING` lines, and those lines carry the reason for each empty turn.
   That reason tells the reader whether the item was drawn before its input existed or was a fix
   that would not land.
6. **Not built: step 3 of the proposal**, which was to raise the stop in `for_the_director` when the
   cause is not an unhonoured `DO NOT DRAW BEFORE`. That would put a per-item alert on his path, and
   the operating model calls a new ceremony on his path a defect. The staging finding is the
   "human" in the practice. The seat's draw reads it.

## 5. GAPs

- **GAP:** whether three is the right number here (section 3). The measurement: after 14 days live,
  for each `STOPPED` line in `seat-executor-log.md`, the time until the id is offered again. If
  the stops wait hours on items that then land at once, propose 5 to the director with that table.
- **GAP:** the log cannot tell an empty turn from a turn that landed and did not bind its landing.
  The stop treats both the same way, and the filed reasons are how a reader tells them apart.
