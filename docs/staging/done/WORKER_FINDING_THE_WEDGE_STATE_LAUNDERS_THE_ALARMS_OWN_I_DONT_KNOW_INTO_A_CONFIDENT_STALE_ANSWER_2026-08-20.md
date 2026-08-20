**Severity:** BLOCKING · **Lane:** H_harness

**Discharged:** `background/supervisor.py`, `tests/background/test_publish_gate_wedge_draw.py::test_mutation_absent_record_withholds_the_cached_blocking_payload`, `tests/background/test_publish_gate_wedge_draw.py::test_mutation_stale_record_withholds_the_cached_blocking_payload`, `tests/background/test_publish_gate_wedge_draw.py::test_mutation_malformed_record_withholds_the_cached_blocking_payload`, `tests/background/test_publish_gate_wedge_draw.py::test_null_control_a_fresh_record_lets_the_payload_through` — repaired at READ time, which is the closure this document proposed: the RUNG-1 draw now asks the live record itself and lets its "I do not know" win over the persisted copy, so the cache must AGREE WITH the record rather than substitute for it.

## What was built, and why on the read side

The primary proposal, not the cheaper alternative. Stamping a freshness field beside the cached
list would have meant editing the gate's own writer module while a gate suite was live in this
working tree — the same hazard that made the finding above withhold its repair, and the reason it
had to withhold it twice. The reader is a different file, so the repair could land on a tree that
was busy. It is also the stronger of the two: a stamp is a second copy of the freshness fact and
can drift from the first, whereas asking the reader keeps the four-way honesty contract in exactly
one place. The helper deliberately DELEGATES to that reader rather than re-parsing the record.

Three things fall together when the record cannot warrant the payload, because all three were
copied out of it: the cited findings, the named blocking tests, and the census depth claim. The
draw still FIRES — a suspect-reader that could blind RUNG 1 to a real wedge would be strictly
worse than one that says nothing — and it now states out loud that it is withholding names it
cannot warrant, rather than repeating them as if it could.

## R15 — the three mutations the document specified, plus its null control

Run: `SIM_FAST_MODE=1 python3 -m pytest tests/background/test_publish_gate_wedge_draw.py -q` → 46
passed. Each leg was then put on trial against the PRE-REPAIR behaviour (the reader never
consulted, so the cached payload is always citable):

| assertion | repaired | pre-repair mutant |
| --- | --- | --- |
| cites the stale finding | False | **True** |
| withholding clause present | True | **False** |
| DEPTH UNKNOWN | True | **False** |
| claims the census enumerated the whole red set | — | **True** |

Every leg flips. The null control is the leg that matters most: a fresh, in-age record naming a
red node must still let the citation, the named-test count and the census depth through, so the
cheapest wrong repair — never citing anything at all — cannot pass.

## What this does NOT close

The write side is unchanged: the cached copy still carries no freshness stamp of its own, so any
FUTURE reader of `.publish_gate_state.json` that does not consult the record inherits the same
defect. That is a limitation recorded, not repaired. The reader named in this document — the
RUNG-1 draw, the one that was actually dispatching work — is the only consumer that existed, and
it is fixed; a stamp on the writer remains the right second belt whenever that module is next
touched on a quiet tree.

The seven findings this alarm cited are still not exonerated, exactly as the section below says.

# The wedge alarm's blocking-test reader answers "I don't know"; the state file the RUNG-1 draw actually reads answers with a test that is green

`last_blocking_tests()` was built with an explicit four-way honesty contract — its own docstring:

> `([], None)` is returned for absent, unreadable, malformed AND stale — all four mean the same
> thing to a reader, which is "this alarm does not know", and the alarm says so.

That contract is correct and it is currently in force. Its source record does not exist:

```
$ ls -la docs/observability/.last_gate_blocking_tests.json
ls: cannot access '.../.last_gate_blocking_tests.json': No such file or directory
```

So `last_blocking_tests()` answers `([], None)` today. But **no reader asks it.** The RUNG-1
unwedge draw reads `docs/observability/.publish_gate_state.json`, and that file still says:

```json
"blocking_tests": ["FAILED tests/saas/reporting/test_partial_year_clv_headline_guard.py::test_the_final_partial_year_still_values_the_book"],
"red_census": "fail_fast_only", "total_red": 1,
"suspects": {"modules": ["saas/reporting/annual_report.py"], "test_files": ["tests/saas/reporting/test_partial_year_clv_headline_guard.py"], "commits": [...]},
"cited_findings": [ ...7 findings... ]
```

## Observed-with-evidence

1. **The named red is green.** At HEAD `d5e03705e`, in the working tree the gate itself runs in:

   ```
   $ SIM_FAST_MODE=1 python3 -m pytest tests/saas/reporting/test_partial_year_clv_headline_guard.py -q --tb=short -p no:randomly
   9 passed in 2.94s
   ```

   `git log d22741ebc..HEAD -- tests/saas/reporting/test_partial_year_clv_headline_guard.py
   saas/reporting/annual_report.py` is **empty** — neither the test nor its module has moved since
   the repair, so the green is not a later accident.

2. **The pin predates the repair by an hour.** The three failures in `.publish_gate_state.json`
   are timestamped `14:07:37Z`, `14:37:18Z`, `15:07:13Z`, and `alerted_at` is `14:07:37Z`. The
   commit that repaired this red, `d22741ebc` ("...build_cost_to_serve stopped DERIVING
   net_margin_gbp and started READING it, and the two test fixtures ... were left uncommitted"),
   landed at `2026-08-20 16:10:35 +0100` = **15:10:35Z**. Every recorded failure is from a tree
   that did not contain the fixture halves.

3. **Nothing has re-derived the state since.** `blocking_tests`/`suspects`/`cited_findings` are
   re-read from `last_blocking_tests()` **only inside `record_publish_gate_failure`**
   (`process_run_complete.py:4734-4760`). Between failures the state file is frozen, and unlike
   the record it wraps it carries **no `ts` of its own and no age bound**. `wedge_since` is
   `07:58:34Z`; `episode_failures` is 14.

4. **It is dispatching work right now.** This tick's SCHEDULED-TICK doorbell carried the stale
   list verbatim — the seven `cited_findings` above, under "FILED FINDINGS ALREADY HOLDING THE
   SUSPECTS — draw these FIRST, before any product or HARDEN work". Commits `159172f5e` ("The
   wedge published eight suspects for thirteen runs and none of them...") and `7d5494610` ("The
   two findings the wedge alert told thirteen ticks to fix first...") are two earlier ticks that
   already spent themselves on the same list.

## The defect, stated as a class

**An honest "I don't know" is laundered into a confident answer by a downstream cache that
copies the value and drops the freshness.** `last_blocking_tests()` fails closed on four
distinct unknowns; `_write_publish_gate_state` persists the *answer* and not the *warrant*, so
the one surface the draw reads cannot distinguish "the last gate's red was X" from "no gate has
recorded a red since X was fixed". This is the same shape as
`feedback_a_control_keyed_on_a_lifetime_fact_is_blind_to_the_since_question` and
`feedback_the_record_can_outrun_the_code` — but sharper, because here the fresh, correct reader
already exists and is simply not consulted at read time.

## Not repaired in this tick, and why — stated rather than quietly skipped

The publish gate's own suite (`process_run_complete.py` PID 3066953, child pytest PID 3132509)
was **live in this working tree** for the whole of this tick. Editing
`background/process_run_complete.py` or `background/supervisor.py` while that suite imports them
would corrupt the in-flight run's result and manufacture the episode's 15th failure. So the
mechanism change is deliberately withheld, not forgotten.

## Proposed closure (mechanism, not instance)

Re-evaluate at **read** time, not write time. The reader that builds the RUNG-1 draw / doorbell
should call `last_blocking_tests()` itself and let its `([], None)` win over the persisted copy —
i.e. the state file becomes a cache that must *agree with* the live record, not a substitute for
it. Equivalent and cheaper: stamp `blocking_tests_ts` beside the list and apply
`GATE_BLOCKING_TESTS_MAX_AGE_SECONDS` on read.

**R15 — the control must be able to fail.** Three mutations, each on its own named defect:

- *fail-open on absence*: delete `.last_gate_blocking_tests.json`, leave a populated
  `.publish_gate_state.json` → the draw must emit **no** suspect list. (Today it emits one; this
  is the live defect and the mutation is currently the observed state.)
- *fail-open on staleness*: write the record with `ts` older than
  `GATE_BLOCKING_TESTS_MAX_AGE_SECONDS` → same expectation.
- *null control (the alarm must still work)*: write a fresh, in-age record naming a genuinely red
  node → the draw must name it. Without this leg the cheapest wrong repair — never emitting a
  suspect list at all — passes both legs above.

## Not-a-suspect-for

The seven findings this alarm cited are **not** exonerated by this document and are not claimed
to be closed by it — the claim here is only that *this alarm's citation of them is not evidence*,
because the citation was derived from a red that has since been repaired. Each still needs its
own disposition on its own merits.

## Open, and honestly unknown

Whether the gate is red at HEAD **at all** is not established by this document. The in-flight run
above is the first gate attempt on a tree containing `d22741ebc`; its outcome, not this record, is
what dates the end of the episode. `docs/observability/.last_tested_hash` reads `43766e01e`
(HEAD is `d5e03705e`), so no pass is on record for the current tree.
