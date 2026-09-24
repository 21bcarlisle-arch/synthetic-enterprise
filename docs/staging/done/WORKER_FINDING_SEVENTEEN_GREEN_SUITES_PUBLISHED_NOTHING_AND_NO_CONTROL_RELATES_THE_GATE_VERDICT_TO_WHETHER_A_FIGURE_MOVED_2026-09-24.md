**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

# Seventeen green suites published nothing, and no control relates the gate's verdict to whether a figure moved

Filed from the Lane 0 item
`the-publisher-has-been-silent-53-hours-and-each-cleared-cause-named-another`, which asked for one
finding naming the sequence of distinct causes this single wedge presented. The sequence is real,
but it is not the finding. **The finding is that the wedge's two longest stretches were GREEN.**

## The window, from the gate's own log

`docs/observability/.publish_gate_state.json` at the time of reading: `last_clean_publish`
2026-09-21 18:15 UTC, `wedge_since` 2026-09-21 20:40 UTC, `episode_failures` 40,
**`episode_clean_publishes` 0**.

`docs/observability/publish_gate_duration.jsonl` holds exactly 40 runs in that window, and they fall
into three contiguous blocks with no interleaving at all:

| Block | Span | Runs | `outcome` |
|---|---|---|---|
| 1 | 2026-09-21 20:39 → 2026-09-22 05:21 | 5 | **all `pass`** |
| 2 | 2026-09-22 07:29 → 2026-09-23 00:44 | 23 | all `fail` |
| 3 | 2026-09-23 01:44 → 2026-09-24 01:11 | 12 | **all `pass`** |

**17 of the 40 runs passed. None of them published.** The wedge opened one minute after a `pass`
(20:39 run, `wedge_since` 20:40) and was still open after twelve consecutive `pass` runs.

## The sequence of causes, since it was asked for

Each block is a different cause, and clearing each one revealed the next:

1. **Block 1 — no test involved.** The suite was green for 8.7 hours and the wedge had already
   begun. This is the stretch the item's phrase *"a dead test citation"* points at: the state file
   still carries `citation_at_head_reason` = *"no red is named on this failure, so there is no
   citation to re-ask"*.
2. **Block 2 — genuine reds**, 17.3 hours, the site lane's failures. This is the only block a
   failing test explains.
3. **Block 3 — `behind_origin`**, 24.5 hours and counting, green throughout.
   `background/origin_reconcile` refused with `REFUSED_CONFLICT` on 74 paths.

A fourth cause is live and is in none of the three: `docs/observability/.publish_step_state.json`
reads `degraded: true` with `failing_steps` `["Customer data generation", "Customer sample
generation"]`, which no `cause` in `background/publish_cause.py` names.

**So a failing test accounts for 17.3 of the wedge's 54.5 hours — 32%.** Two thirds of the outage
happened while the instrument that looks like the publisher's health said `pass`.

## Why nothing noticed

`outcome` in `publish_gate_duration.jsonl` records **whether the publisher's scoped suite passed**.
`last_clean_publish` records **whether a figure reached origin**. They are different quantities, and
nothing in the repository compares them.

That is what let this run for 54 hours. Every automatic reader was looking at the first one:

- The duration log's own bands (`band: ok`, `headroom_ratio: 0.69`, `cadence_band:
  within_cadence`) grade the suite's *runtime*, and were `ok` on all 40 runs including the 23 reds.
- The heartbeat published "alive" three times in the last 3.1 hours of the wedge — it is keyed to
  the publisher *running*, not to the publisher *landing*.
- `blocking_tests` is `[]` and stays `[]` through both green blocks, which reads as health.

The three `not_established` fields in the state file (`citation_at_head`, `fork_state`,
`red_at_head`) are the one honest part of the surface: each carries a reason saying so explicitly
(*"This is not evidence that HEAD is green."*). They fail closed and say so. Nothing above them does.

## The control this earns, keyed to the property

Not "the suite is green" and not "the wedge is under N hours" — both are today's-answer keys that go
green the moment someone fixes an instance. The property is the **relation**:

> A run whose `outcome` is `pass` must advance `last_clean_publish`, or name a cause for why it did
> not.

A green suite that leaves `last_clean_publish` untouched and writes no `cause` is the defect, and it
is the state all 17 green runs were in. This is one leg over the existing pair of fields, not a new
register: it needs no new artefact, and it can fail — Block 1 and Block 3 are 17 recorded instances
that would have reddened it, so it is falsifiable against history rather than against a future.

**Deliberately not built here.** The wedge itself was the drawn work and is being cleared in the
same turn by resolving the 74-path fork; building the control in the same commit would make the
attribution impossible if anything downstream moved. One variable.

## A prediction, filed before its answer is known

If the control above is built and run against the 40 records in this window, it reds on exactly the
17 `pass` runs and is silent on the 23 `fail` runs. If it reds on fewer than 17, `last_clean_publish`
moved during the wedge without the state file recording a clean publish, and the two fields disagree
about their own subject — which would be a second, worse finding.
