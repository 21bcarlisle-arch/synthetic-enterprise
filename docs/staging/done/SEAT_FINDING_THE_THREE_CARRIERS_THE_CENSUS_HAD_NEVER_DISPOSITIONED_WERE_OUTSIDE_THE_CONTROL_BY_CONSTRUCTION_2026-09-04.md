# SEAT FINDING — the three carriers the census had never dispositioned were outside the control by construction

**Date:** 2026-09-04
**Class:** R10 (an absurdity is fixed as a class, not an instance) · R15 fail-silent
**Severity:** BLOCKING · **Lane:** H_harness — `self_clearing_alarm_census --check` was exiting 1 at
HEAD, and one of the three carriers could stop the simulation producer from starting at all.
**Status:** REPAIRED in this commit for all three. The residual is named at the bottom and is not
repaired.
**Pre-registration:** `docs/staging/records/SEAT_PREREGISTRATION_WHAT_THE_THREE_UNDISPOSITIONED_CARRIERS_DO_ACROSS_THE_PARTITION_2026-09-04.md`
— written before anything was run. All four predictions held; where one over-reached, that is
recorded below rather than quietly dropped.

---

## What was drawn, and what I found already done

The seat's direction: sweep every guard the self-clearing-alarm census enumerates for the
ABSENT-vs-PRESENT-BUT-UNREADABLE conflation found in `guard_episode`, printing the verdict across
the whole partition of prior states.

`9810e2bdd` — landed by another lane hours earlier, already in this tree — had done that for the
**eight `real` rows**, built `background/episode_prior.py`, and left a residual it named honestly. So
the first job was not to rebuild it. It was to find what its subject excluded.

## The finding: a derived subject has a blind spot exactly where the derivation reads nothing

`test_episode_prior_partition.py` derives its subject from the census's own `real` rows —
deliberately, and it is the right design, so that a new carrier of the class fails there rather than
joining it quietly. But a carrier with **no disposition row at all** is in no verdict set. It is not
in `real`, so it is outside that control **by construction**, and no amount of care inside the
control can reach it.

`background/self_clearing_alarm_census.py --check` was exiting **1** at HEAD (`23c63e296`), naming
exactly those carriers, and had been:

    .weekly_rhythm.json            background/weekly_rhythm.py
    .seat_continuation.json        background/seat_continuation.py
    .sim_next_run_not_before.json  background/sim_runner.py

Three carriers, in the tree, that neither the census's disposition check nor the partition control
had ever looked at. All three carried the conflation. Two of them raised on a member of the
partition — the identical `json.loads`-accepts-a-list crash fixed in three other carriers the day
before, still live in these for the reason above.

**The red WAS the finding.** The census's teeth had been reporting this in a sentence nobody had
read, and the fix for a red that names three files is not to disposition them — it is to go and look
at what they do.

## The partition, measured

Every table has a **control leg with a readable prior**, because "absent differs from unreadable" is
satisfiable by a carrier that answers the same thing to everything. The first draft of the rhythm
table had no such leg and read as seven identical BOOTSTRAPs — including for the healthy prior,
because the step name in my fixture was not a step. That control is the only reason I knew the table
was worthless.

**1. `weekly_rhythm.tick`** — prior = a step opened 2026-09-01, three days late:

| prior | action | due_on | days_late |
|---|---|---|---|
| OPEN EPISODE (control) | `FINDING` | 2026-09-01 | **3** |
| missing file | `BOOTSTRAP` | 2026-09-07 | — |
| corrupt / truncated | `BOOTSTRAP` | 2026-09-07 | — |
| `null` / `[1, 2, 3]` / unknown step | `BOOTSTRAP` | 2026-09-07 | — |

`due_on` is an episode start and `days_late` is the severity read straight off it. An unreadable
baton moved the start **forward**, reset the lateness to zero, and the same write destroyed the
evidence — the 2026-08-09 self-clearing shape, in the one mechanism whose whole job is to notice
that a step did not fire.

**2. `seat_continuation`** — prior = two live continuations, then one `hand_off`:

| prior | `_load` | `live` | store after the hand-off |
|---|---|---|---|
| LIVE PRIOR (control) | 2 | 2 | `['alpha', 'beta', 'gamma']` |
| missing file | 0 | 0 | `['gamma']` — correct |
| corrupt / `null` | 0 | 0 | `['gamma']` — **two destroyed** |
| `[1, 2, 3]` | — | — | **AttributeError: 'int' object has no attribute 'get'** |

**The reader was never what was wrong.** `_load` degrading to `[]` is correct and stays —
`delivery_lane.draw` documents that a lane which can throw takes every other lane down with it, and
`test_a_BROKEN_store_costs_the_seat_its_handoff_and_never_the_machine_its_tick` pins that. What was
wrong is that `[]` was the **whole answer**, so `hand_off` — `_load()`, append, `_save()` — wrote a
one-entry store over a store it merely could not parse. This is the only copy. And a JSON list of
non-mappings passed the loader's outer `isinstance(raw, list)` check, so `live()` raised on the
draw's own path: checking only the outer type let a shape the module cannot use through as data.

**3. `sim_runner.pause_owed_from_a_previous_process`:**

| prior | before |
|---|---|
| LIVE PAUSE (control) | `(600.0, 'resuming the between-run pause…')` |
| missing file | `(0.0, 'no deadline was recorded by a previous process')` |
| corrupt | `(0.0, 'the recorded deadline file is not readable JSON')` |
| `[1, 2, 3]` | **AttributeError: 'list' object has no attribute 'get'** |
| present, unreadable (a directory, a permission error) | `(0.0, 'no deadline was recorded by a previous process')` — **false** |

That call is the **first statement of `sim_runner.main()`, outside every `try` in the module**. So a
one-line non-mapping in a bookkeeping file the producer writes itself did not cost one early run —
it stopped the producer daemon from starting. The function's docstring claimed it failed toward
running "in every direction: no file, unreadable file, corrupt JSON, a non-instant". Two of those
directions raised, and a fifth lied about which one it met.

## What was done about each, and why they are not the same repair

Deliberately not one reflex applied three times — what an alarm should DO about a lost memory is a
per-control judgement, and guessing it produces controls nobody chose.

* **`weekly_rhythm`** — both still rebuild: the rhythm must keep running, and this module's own rule
  is that it never files a document about itself. What differs is the **record**. An unreadable
  baton is preserved beside the baton and the rebuild is stamped `prior_unreadable`. That flag is on
  the **persisted record**, not only in the return value, because `daily_self_note` calls `tick()`
  as a passenger, discards what it returns and swallows what it raises — so the module's stated plan
  ("rebuilt and reported in the tick's own output") reached nobody. An argued design defeated one
  level up by its caller.
* **`seat_continuation`** — repaired at the **writer**, not the reader. `hand_off` moves the
  unreadable bytes aside before writing and records where they went. The loader's element check is
  now deep enough to refuse a list of non-mappings.
* **`sim_runner`** — routed through `episode_prior`; the `0.0` and the asymmetry argument behind it
  are unchanged, and the reason now names what it actually met. Three states, three distinct
  reasons: absent, unreadable, and readable-but-without-the-key.

## The scope error the `benign` verdict was hiding

**`benign` answers one question — "can a write shorten an episode?" — and was being read as a clean
bill of health for the file.** `.seat_continuation.json` is genuinely benign on the census's
question (nothing reads an age for severity; the six-hour window is a fixed offer window, not an
outage clock) and had the **worst** absent-vs-unreadable defect of the three. Those are consistent,
and that is the point: one verdict cannot answer a question it never asked.

Recorded as `_verdicts._scope_of_benign` in the dispositions file, and the three rows swept here
carry a `loader` field saying what the answer is. **A row without one has not been asked, which is a
gap and not a pass** — the honest `None` rather than the plausible number.

## The controls

`tests/background/test_undispositioned_carriers_absent_vs_unreadable.py`, 27 legs. Every leg asserts
the two answers **DIFFER**, never that they match — a control pinning them to one branch holds the
defect green while reading as deliberate, which is exactly how `prev=None` survived two lanes'
repairs. Each carrier has a **reachability leg** proving a readable prior reaches a third answer.

Mutation-proved, all six fire:

| mutation | result |
|---|---|
| `weekly_rhythm`: unreadable → ABSENT | FIRED |
| `weekly_rhythm`: stop preserving the bytes | FIRED |
| `seat_continuation`: `hand_off` ignores the verdict | FIRED |
| `seat_continuation`: outer `isinstance` only | FIRED |
| `sim_runner`: restore `(raw or {}).get(...)` | FIRED |
| `sim_runner`: absent reason for an unreadable file | FIRED |

Promoting `.weekly_rhythm.json` to `real` made
`test_episode_prior_partition::test_every_real_census_hit_is_covered` go red — **the prior lane's
anti-narrowing rung working exactly as built**, on the first new `real` row since it landed. It is
exempted there by citation to the sibling control, and the exemption **asserts that file is on
disk** rather than taking the row's word, which is the same discipline `unguarded_real_hits` applies
to the census's own `guard` field.

## Where my pre-registration over-reached, kept beside the result

I predicted `{"unrelated": 1}` would be present-but-unreadable for all three. It is for the baton
(a mapping whose `step` is not a step) and the store (not a list of entries), and it is **not** for
the deadline: that is a perfectly readable state that does not carry the key, which is a **third**
answer. Treating three facts as two would have been this sweep's own defect wearing the other coat,
so the control now pins all three (`test_a_deadline_file_missing_only_its_key_is_a_third_answer`)
rather than the two I set out with.

## Also fixed on the way

`.sim_producer_state.json` was `real`, said `guard: guarded`, and cited **no test that exists** — so
`unguarded_real_hits` refused to take its word for it, and was right to. The guard and its tests
were both there; the citation was the missing half. Now cited.

`--check` at HEAD went from **rc=1 to rc=0**, and honestly: every row it names is dispositioned,
every `real` row is guarded by a test on disk.

## Residual, named rather than glossed

**UPDATE, same turn, kept beside the claim rather than revised away:** the first two of these were
measured immediately after this landed, and both were real —
`SEAT_FINDING_THE_SEND_ONCE_MEMORY_LOST_EVERY_ID_TO_A_FILE_IT_COULD_NOT_READ_2026-09-04.md`. The
`.sent_ntfy_ids.json` consequence is worse than the guess below: not "every id re-sent" but our own
outbound read as INBOUND, which stages a message carrying the director's authority that he never
sent. The prediction that the shape was there was right; the prediction of what it cost was wrong,
and understated.

**The other 34 `benign` rows have not been asked the loader question.** This turn swept the three
that were undispositioned; the `loader` field exists so the gap is visible, and it is empty for
every row I did not measure. The shape to look for is a read-modify-write over a state file —
`.sent_ntfy_ids.json` (send-once semantics: an unreadable set means every id re-sent),
`.dispatcher_seen.json` and `.staging_watcher_seen.json` (seen-sets: re-processing),
`.notify_transitions.json` (an edge re-fired). None of those shorten an episode, all of them are
benign on the census's question, and that is precisely why nothing has looked. **That is the next
item on this class**, and it is not guessed here.

**A rebuilt baton is not a recovered step.** The bytes are kept and the loss is visible; the open
step is still not restored. Adopting the prior lane's posture verbatim: what changed is that the
record no longer *claims* a cold start it never observed.
