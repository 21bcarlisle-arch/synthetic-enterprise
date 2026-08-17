# [WORKER-REPORT] H42 — the wedge alarm's suspects now come from the red (2026-08-10)

**Severity:** RECORDED · **Lane:** H_harness

**Atom:** `H42_wedge_suspect_list_rederived_from_the_red`, L0 → L2, one tick.
**Ratified by:** `DIRECTOR_NOTE_SUSPECT_LIST_REDERIVATION_2026-08-10` (the 12:32 report's
recommendation). **Lane:** H_harness. **Store record:**
`docs/design/simplifications/H42_wedge_suspect_list_rederived_from_the_red.yaml`.

## What was wrong, restated in one line

The alarm's "also filed and unactioned in staging" block was `filed_findings()` — staging's eight
most recently modified `WORKER_FINDING_*.md`, ranked by mtime, linked to the failure printed above
them by nothing. Measured 0/8 in five consecutive episodes; priced by the director at twenty
minutes of every responder's time per episode.

## What landed

`filed_findings()` is **deleted**. The suspect block is derived from the one fact the alarm already
knows for certain — the blocking node id in `.last_gate_blocking_tests.json`:

| step | function | note |
|---|---|---|
| the red's test files | `blocking_test_files()` | every recorded form: `FAILED p::t`, `ERROR p - msg`, bare |
| its blame surface | `first_party_imports()` | `ast` over the test's SOURCE, never an import — the module that wedged the gate may be the one that cannot be imported. Repo packages only |
| what changed there | `blame_commits()` | `git log`, 7 days, bounded |
| which filed findings are relevant | `linked_findings()` | findings whose TEXT names something on that trail — a link, not a filing date |

The state contract the supervisor's RUNG-1 draw reads (`cited_findings`) is **unchanged**; only what
fills it moved. "FILED FINDINGS ALREADY HOLDING THE SUSPECTS — draw these FIRST" is now a true
sentence rather than an instruction to dispose of eight irrelevant documents.

## Exit criteria, against evidence

**(1) No recorded blocking test ⇒ no suspect list.** `wedge_suspects()` returns `{}` and the alarm
prints no suspect block and cites nothing. `_blocking_clause`'s "never degrades to a guess" was
extended, not re-argued.

**(4) Fail-silent.** Unreadable, malformed and STALE gate state all reach the reader as
`BLOCKING TEST: UNRECORDED` via the existing `last_blocking_tests` — never as "no suspects".
Parametrised over all three cases.

**(2) R15 both ways — three mutations DRIVEN, each shown killing a NAMED test:**

| mutation | named test that died | run |
|---|---|---|
| re-point the citation at mtime (reinstate recency) | `test_mutation_reinstating_the_recency_ranking_dies_here` | 4 failed / 37 passed |
| fabricate a suspect when the blocking test is unrecorded | `test_mutation_emitting_suspects_with_no_recorded_blocking_test_dies_here` | 2 failed / 18 passed |
| score an unmeasurable episode as a hit | `test_an_unmeasurable_change_set_is_not_a_hit` | 1 failed / 19 passed |

**(3) The hit rate is MEASURED and carried.** Every evidenced episode close appends to
`.wedge_suspect_hit_rate.json`; every payload carries the running rate, including
`SUSPECT HIT RATE: not yet measured`. The measurement is deliberately **narrower** than the human
0/8 it replaces and the phrase says so: *"the repair touched a path this alarm had NAMED."* Three
outcomes, one hit — *no list emitted* and *unmeasurable change set* both record `hit=None` and move
neither numerator nor denominator, so the ledger cannot flatter itself. R12 is written into the
phrase: a diagnostic, never a target, and it says out loud that a rate stuck at 0 means this
re-derivation is as useless as the list it replaced.

## Dogfooded on the repo's actual current red

Run against the red that is wedging the publish gate right now (`AO12`, per
`WORKER_FINDING_A_MINT_DECLARES_STORE_FIELDS_IT_NEVER_WRITES_2026-08-10`):

```
blocking : FAILED tests/design/test_atom_notes_store.py::test_declarations_match_the_store
modules  : tools/simplifications_store.py
commits  : 4fccacf39 Unwedge publishing: the H41 caller landed, its callee did not
           3151734db H32: rehome the map's narrative notes -- and repay the ratchet amnesty at 400K
           3d2718a57 [CCM] Simplifications store extraction (retro FM-1)
linked   : WORKER_FINDING_A_MINT_DECLARES_STORE_FIELDS_IT_NEVER_WRITES_2026-08-10.md  (+4)
```

The finding that *actually names this wedge's cause* is in the citation list. It was **not** in the
recency list the old mechanism would have produced. This is one observation, not the metric — the
metric is the ledger, and it starts at "not yet measured" rather than at a claim.

## Two controls fired on this change and were paid, not silenced

* **The self-clearing-alarm census** flagged `.last_gate_blocking_tests.json` and
  `.wedge_suspect_hit_rate.json` as undispositioned hits. Both dispositioned `benign` **with the
  reason** in `docs/design/self_clearing_alarm_dispositions.json`: neither carries an
  episode-scoped field, and the blocking record's staleness fails in the SAFE direction — it makes
  the page say *less*, never an episode look *shorter*.
* **`test_background_worker`'s retry exit test** broke, and the cause is worth recording:
  `background_worker.subprocess` *is* the stdlib module object, so `monkeypatch.setattr(...,
  "run", ...)` is a **global** patch that caught the new read-only `git log`. The test now filters
  to publisher invocations, which is what "attempts at this marker" always meant. Its named
  mutation (skip markers already failed on) still kills it.

## A leak this change caught in the act — worth generalising

Adding a second state path to the recorder made
`tests/background/test_episode_monotonic_guard.py` write
`docs/observability/.wedge_suspect_hit_rate.json` **into the live tree**: a test manufacturing the
evidence a control reports on. It had isolated `PUBLISH_GATE_STATE_FILE` and `STAGING_DIR` — the
paths that test happened to need, not the paths the recorder is known to use. Fixed here with an
autouse fixture over all of them, and the leaked file deleted.

**The class (queued, not fixed on sight, per SELF-INTERRUPT DISCIPLINE):** any test driving a real
recorder isolates the state files it *thought of*, so every new state path silently re-opens the
leak. The mechanical fix is a conftest-level guard that fails a test which writes under
`docs/observability/` — filed separately rather than widened into this atom.

## What this does not do

It cannot say the suspects are **right**, only that they came from the red. That question is what
the hit-rate ledger exists to answer over the next episodes.

**Draw order.** The director's note sequenced this after the folded-site verification. The
supervisor drew it on the scheduled tick; Rule 0 treats draw order as a DIAL, so it was built
rather than held. The sequencing bought nothing here — disjoint `file_scope`, no shared surface.

## Left standing, deliberately

`AO12_scale_probe_10k` remains red on both store-declaration tests (the second of the two atoms
named in the mint-declares finding). H42 was one of them and is now green because it was the drawn
atom and its evidence is real. AO12's is not mine to author, and inventing it to green a suite is
the exact defect that test exists to catch.
