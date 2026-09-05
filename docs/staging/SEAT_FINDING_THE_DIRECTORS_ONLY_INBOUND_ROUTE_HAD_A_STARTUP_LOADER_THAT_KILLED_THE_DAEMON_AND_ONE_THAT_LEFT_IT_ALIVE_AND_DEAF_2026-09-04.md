**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# The director's only inbound route had a startup loader that killed the daemon, and one that left it alive and deaf

Filed 2026-09-04 by the delivery seat under the Lane 0 claim
`ask-the-remaining-32-benign-census-rows-the-loader-question-2026-09-04`. **Fixed and landed in the
same commit as this finding.** Pre-registration, written before the measurement:
`SEAT_PREREGISTRATION_WHAT_THE_INBOUND_CHANNELS_THREE_UNASKED_CARRIERS_MUST_SHOW_2026-09-04.md`.

## What the direction asked, and where the answer moved

Sweep the unasked `benign` self-clearing-alarm census rows for the ABSENT-vs-PRESENT-BUT-UNREADABLE
conflation, **ranked by what the carrier's WRITER does** — a read-modify-write can destroy the
record where a pure reader only loses a suppression. Four carriers were named; two were swept
earlier the same day, leaving `.ntfy_responder_seen_hashes.json` and
`.last_processed_fingerprint.json`.

Reading `background/ntfy_responder.py` to rank the first of those changed the unit of work. That
one daemon holds **three** unasked carriers and they are not independent: they are the watermark,
the replay-dedup and the flood window on **the only inbound route the director has into this
machine**. So the thing to sweep was the channel, not the row.

## What was measured, before the repair

Whole partition — missing file · empty file · truncated · `null` · `[1, 2, 3]` · `{"other": 1}` ·
`["x", 2]` — each against a **CONTROL LEG holding a live prior**. The control leg is not
decoration: without it, "absent and unreadable differ" is satisfied by a loader that answers
UNREADABLE to everything, which on this channel means alarming on every start.

**`_load_since` — `.ntfy_responder_since.json`. The daemon did not start.**

| prior | answer |
|---|---|
| missing file | `time.time()` |
| empty file | `time.time()` |
| truncated | `time.time()` |
| `null` | **RAISED** `TypeError: 'NoneType' object is not subscriptable` |
| `[1, 2, 3]` | **RAISED** `TypeError: list indices must be integers` |
| `["x", 2]` | **RAISED** `TypeError: list indices must be integers` |
| `{"other": 1}` | `time.time()` |
| **CONTROL live prior** | `1234.5` |

`json.loads` accepts `null` and a list, so neither is a `JSONDecodeError`, neither was ever seen by
`except (json.JSONDecodeError, KeyError)`, and the subscript one line later is what raised. **That
call is the first statement of `main()` and there is no try above it.** A half-written watermark did
not cost one poll — the responder did not start at all, and the only symptom was the director's
messages not arriving from a machine that otherwise looked healthy. It is the
`.sim_next_run_not_before.json` shape, moved off the producer and onto the channel.

**`_load_seen_hashes` — `.ntfy_responder_seen_hashes.json`. The daemon stayed alive and went deaf.**

| prior | answer |
|---|---|
| missing / empty / truncated | `[]` |
| `null` | `None` — from a function annotated `-> list[str]` |
| `[1, 2, 3]` | `[1, 2, 3]` |
| `{"other": 1}` | `{'other': 1}` — a dict, from the same annotation |
| `["x", 2]` | `['x', 2]` |
| **CONTROL live prior** | `['aa', 'bb']` |

`check_once` opens with `set(seen_hashes)` on every successful poll, ahead of any message
filtering. `None` raised `TypeError` there; `main`'s loop catches every `Exception` and logs it, so
the responder **polled every 20 seconds forever, never advancing the watermark and never processing
a message** — and the log filled with a line that reads exactly like a transient network error. A
mapping survived `set()` and raised `AttributeError` on `seen_hashes.append(h)` instead: **only at
the moment a real message finally arrived.** The two list members did not raise at all — every hash
missed, and `_save_seen_hashes` then wrote the wrong things back. This carrier is a
read-modify-write, which is why it outranked the rest: a record it cannot read is a **wiped**
record.

**`_load_rate_state` — `.ntfy_responder_rate.json`. Already sound, and recorded anyway.** No member
raised; every unreadable one fell to `{"events": [], "last_alert": 0}`, because this loader already
screened `isinstance(state, dict)` — which is exactly what its two siblings lacked. The `-> dict` on
the others was an annotation; this one was a check.

**`_read_last_fingerprint` — `.last_processed_fingerprint.json`. Named by the direction as a
read-modify-write; it is not one.** No member raises, every one compares unequal to the freshly
computed fingerprint, and the branch taken is REPUBLISH — the safe direction. `_write_last_fingerprint`
overwrites with a computed value and never reads the file. Dispositioned as an honest pass with the
table, and left unrepaired deliberately: absent and unreadable drive the same branch and no caller
distinguishes them, so a verdict there would be a control watching nothing.

## The predictions, kept beside the results

All five pre-registered predictions held, including the one that this sweep would find nothing to
repair in the flood window and nothing to repair in the fingerprint. Two things the
pre-registration did not have: `["x", 2]` also raises in `_load_since` (the same subscript, so the
same cause), and `{"since": true}` passes a bare numeric check because `isinstance(True, int)` is
True. Both are in the controls.

## The repair

Each loader now returns `(value, verdict)` from `background/episode_prior`, so absent, unreadable
and readable are three answers rather than one, and **no member of the partition raises**:

- `_load_since` gains a **fourth** answer, `readable_without_watermark`: the file parsed and simply
  carries no `since`. Kept distinct because the remedies differ — unreadable bytes are worth
  preserving and that record is not.
- UNREADABLE still resumes from now, and that is **argued rather than defaulted**. Looking BACK on
  a lost watermark re-enters `_register_inbound_and_detect_flood`, trips the flood guard and
  quarantines the very messages the lookback was for. Re-EXECUTION is already defended by
  `claim_message`; the flood guard is not something a lost watermark should get to trigger. So the
  ACTION is the cold-start one and the ANSWER is not: `main` preserves the bytes so an operator can
  read the watermark back out, and alarms on the channel's own wire.
- `main` performs the two preservations **before** the first save, because both files are read once
  at startup and written back last-writer-wins every cycle.

## The helper the fourth call site was about to fork

`ntfy_utils`, `staging_watcher` and `dispatcher` each carried a byte-identical private
`_preserve_unreadable_*`, two of them with a docstring saying *"same shape as"* the first — a fork
of the fix history wearing a cross-reference. The responder would have been the fourth. It is now
`episode_prior.preserve_unreadable`, and all three delegate. The control is keyed to the
**property** (patch the central helper, all three must change their answer), not to the source
text, because a grep-for-the-call-site control goes green on a copy that merely looks like a
delegation.

## Controls, and how each was proven able to fail

`tests/background/test_the_inbound_channels_three_loaders.py` — 27 legs. Every leg asserts the two
answers **DIFFER**, never that they match, and each carrier carries a reachability null control
proving a live prior reaches a third answer. Mutation-proven, one at a time:

| mutant | legs that fired |
|---|---|
| restore the old `_load_since` body | 8 |
| restore the old `_load_seen_hashes` body | 6 |
| fold `_NO_WATERMARK` into UNREADABLE | 2 |
| drop the bool exclusion on the watermark | 1 |
| drop the `events`-is-a-list screen | 1 |
| re-inline any one `_preserve_unreadable_*` | 1 |

**A control whose failing branch damaged the thing it guards.** Running the re-inlining mutant
performed a real `Path.replace` and moved the live `background/.dispatcher_seen.json` out of the
working tree — the delegating version never touches disk because the spy intercepts, so this was
invisible until the mutation ran. The three module path globals are now redirected to `tmp_path`
first. Written up here rather than fixed quietly: a control that is only safe while it passes is
worth naming as a shape.

## What this leaves

28 `benign` census rows still carry no `loader` field, down from 31. The field is what makes the
remaining gap visible rather than assumed clean, and the ranking that found this one is the one to
carry on with: **ask what the WRITER does, and read the daemon rather than the row** — the row said
"a poll watermark, advancing it is the mechanism", and every word of that was true.
