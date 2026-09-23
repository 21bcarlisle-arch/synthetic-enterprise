**Severity:** RECORDED · **Lane:** HARNESS · **Epoch:** unassigned · **Atom:** unminted

# PRE-REGISTRATION — which channel is the sediment, and which of the alarm's two remedies applies

Written **before** the attribution is run. `background.staging_rooms.sediment_violations()` is the
one red left on the reconciled shared tree: 266 filed into the staging root over 7 days against 258
dispositioned, net +8. The control names two candidate remedies and rules out a third:

> *"The remedy is not a bigger folder: it is fewer channels that file, or a disposition route for
> the ones that do."*

Which of the two it is is a question about **who files**, and nobody has looked. This file is the
prediction; the answer goes beside it.

## The measurement I am about to run

Attribute the window's `--diff-filter=AD --no-renames` root events by producer prefix
(`WORKER_FINDING_REPEATING_ALARM_`, `WORKER_FINDING_`, `WORKER_RESULT_`, `SEAT_RESULT_`,
`SEAT_FINDING_`, `SEAT_PREREG_`, `DIRECTOR_CONSOLE_`, `CLASS_`, other), and for each family report
`filed`, `dispositioned`, `net`, plus whether it already has a room (`reference/`, `console/`,
`records/`, `done/`, `in_progress/`, `fyi/`, `exhaust/`, `drafts/`).

## Predictions

1. **The REPEATING_ALARM family — the item's named first suspect — is NOT the net.** Its net over
   the window is ≤ +2. It is high-VOLUME because it regenerates, but a regenerated document is
   filed and cleared under the *same name*, and `root_flow` deliberately counts a name on both
   sides when it is added and deleted inside the window. Volume and sediment are different
   quantities and this family is the clearest place they come apart.
2. **The net is carried by the RESULT families** (`SEAT_RESULT_*` + `WORKER_RESULT_*` together),
   which I predict are >35% of the 266 filed and carry a combined net of **at least +6** of the +8.
3. **At least one family files and never disposes** — `filed > 0`, `dispositioned == 0`.
4. **The answer is "a disposition route", not "fewer channels".** A RESULT document is the written
   outcome of a turn: it is a *record of work already done*, it cannot be actioned, and therefore it
   can never leave the queue by being drawn. That is D2 for the fourth time — after `reference/`
   (a register), `console/` (a transcript) and pre-registrations — and the remedy each previous
   time was a room, not a silenced producer. Suppressing the channel would be suppressing the
   evidence the seat works.

## What would refute each

1. REPEATING_ALARM net > +2 → refuted; the alarm family really is accreting distinct names and
   `alarm_repetition.py`'s one-document-per-firing has a leak.
2. RESULT combined net < +6, or another family larger → refuted; say which family it actually is.
3. Every family with `filed > 0` also has `dispositioned > 0` → refuted; there is no dead-end
   channel and the sediment is a rate mismatch spread across all of them, which is a harder problem
   and a different remedy.
4. If the positive-net family turns out to be *regenerated* rather than *authored*, the answer is
   "fewer channels" and prediction 4 is refuted.

## What done means for the work this precedes

A family whose documents cannot be actioned is routed out of the work channel by a spanning room
with a population floor, exactly as `reference/` and `console/` were — and the route is **enforced
in code, not in prose**, because a disposition decided only in prose is re-litigated forever. The
sediment leg going green is the consequence, not the goal: a green keyed to today's +8 would be the
control-pinned-to-today's-answer failure this repo has paid for repeatedly.
