**Severity:** BLOCKING · **Lane:** H_harness · **Class:** publish_gate_and_wedge

**Discharged:** `background/supervisor.py` (`WEDGE_KINDS_NO_TEST_JUDGED`, `_wedge_no_test_judged_clause`, wired into `_publish_gate_wedge_active`), `tests/background/test_publish_gate_wedge_draw.py::test_a_commit_did_not_land_episode_countermands_the_find_the_red_test_opening`, `::test_every_no_test_judged_kind_countermands`, `::test_mutation_a_test_regression_episode_keeps_the_find_the_red_test_opening`, `::test_mutation_one_test_regression_among_them_is_enough_to_stay_silent`, `::test_mutation_an_unreadable_or_unrecognised_kind_stays_silent`, `::test_mutation_a_citable_blocking_payload_outranks_the_kind_label`, `::test_depth_unknown_is_the_only_clause_the_countermand_can_displace`, `::test_the_publishers_kinds_and_the_supervisors_set_have_not_drifted` — the RUNG-1 draw now reads the `kind` field the publisher has been writing for it since 2026-08-19.

## The finding

The publisher classifies its own failures. Three sites set `kind` explicitly, and each carries a
comment saying what the label is FOR:

- `process_run_complete._record_publish_gate_outcome`, rc=77 → `kind="commit_did_not_land"`:
  *"NAMED, not left to `_classify_gate_failure`, which would read rc=77 as 'test_regression' and
  send the RUNG-1 draw hunting a red test that is not the cause."*
- the same function, rc=78 → `kind="gate_timeout"`: *"NAMED for the same reason as the code
  above ... would read rc=78 as 'test_regression' and send the RUNG-1 draw hunting a red test
  that does not exist."*
- `background_worker.process_leftover_run_markers` → `kind="deadline_kill"`, under the third
  statement of the same sentence.

The intent is written down three times. **The draw the intent is about never read the field.**
`_publish_gate_wedge_active` reads `reason`, `rc`, `ts`, `git_hash`, `cited_findings`,
`blocking_tests`, `red_census` and `total_red` from each failure — and not `kind`. So its fixed
opening stood unconditionally:

> DIAGNOSE the failing test with evidence (R9): run the exact gate `SIM_FAST_MODE=1 python3 -m
> pytest tests/ -m 'not operational' <heavy-ignores>` ... FIX the red test

## Observed, not inferred

`docs/observability/.publish_gate_state.json` at 07:53Z on 2026-08-27:

```
"episode_failures": 4, "blocking_tests": [], "total_red": 0, "red_census": "fail_fast_only",
4 × {"kind": "commit_did_not_land", "rc": 77, "git_hash": "f4b0b6334"}
```

Four failures, zero accused. The real cause was in the publisher's own log tail both times, and
neither is a test — `docs/observability/sim-runner-log.md`:

- 05:28Z and 06:39Z — `orphan-ratchet: THIS COMMIT ADDS WORK THAT NOTHING RUNS.` naming
  `sim.neso_embedded_generation`, `tools.ep13_embedded_generation_bound`, `tools.wait_for`.
  New modules swept into the publish commit by another lane's uncommitted work, unfrozen.
- 07:13Z — `[test-gate] ❌ FINDING-CLASS CONSOLIDATION BROKEN -- COMMIT REFUSED.` on a stale
  severity header in `CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md`.

Both gates verified GREEN at HEAD when this was drawn (`python3 tools/orphan_ratchet.py` → rc 0;
`python3 -m background.finding_classes --check` → `check: PASS (0 failures)`), so the instance
causes had already been repaired by the lanes that introduced them. What had not been repaired is
the draw that sends priority-zero work to look for them in the wrong place.

## Why this is the class and not an instance

`_record_commit_refusal_reds` already handles the case where the hook chain names a test: it
writes `census="hook_chain"`, and `_wedge_depth_clause` has a clause for it that says *"do NOT go
looking for a red in the publish scope."* That clause is correct and it is unreachable on this
path — a non-test gate names no node id, so the function logs *"recording NO blocking test ... the
refusal was a non-test gate"* and writes nothing. The record is honest; it just has no reader.

The cost is not only the wasted ~10-minute suite run. It comes back GREEN, which reads as a
self-clearing wedge, so the refusing gate is never named and the next cycle refuses again. Twelve
consecutive episodes on 2026-08-25 (12.2 hours of no publishing), four on 2026-08-27.

This is the LABEL-WITHOUT-A-READER shape — the sibling of the class this repo already catalogues
under "a control that cannot fail". Here the control could not be heard.

## The repair

`_wedge_no_test_judged_clause(failures, payload_citable)` prints a countermand naming the recorded
kind, pointing at the publisher log tail where the refusing gate names itself, and instructing the
worker to re-run THAT gate alone against the working tree before repairing anything (the hook
chain stops at the first refusal, so a second gate may be behind it).

It also SUPPRESSES `depth_clause` rather than arguing with it. Two instructions in one payload
with the contradicting one last — "there is no red" followed by "enumerate the reds, run the
gate's argv without `-x`" — is exactly how the 2026-08-27 draw read, and the second one is the run
this clause exists to prevent. Safe because the countermand requires an uncitable payload, which
already forces census/total to `None`/0, so `_wedge_depth_clause` can only be returning its DEPTH
UNKNOWN default. Nothing that could name a red is suppressed; pinned by
`test_depth_unknown_is_the_only_clause_the_countermand_can_displace`.

## R15 — both ways, and the fail-safe direction is argued not assumed

The dangerous direction is FIRING WRONGLY: telling a worker not to look for a red that is there.
Staying silent only costs a suite run. So every ambiguity is a reason to stay quiet, and the
clause needs **unanimity** among the in-window failures — not a majority, not the last entry. A
wedge that is half `test_regression` is a wedge with a red in it.

| mutation | result |
|---|---|
| clause always returns `""` (the pre-fix behaviour) | 5 reds, incl. both MUST-FIRE tests |
| any-match instead of unanimity, `payload_citable` ignored | 2 reds: the mixed-episode and citable-payload guards |

Silence proven for: an ordinary `test_regression` episode; one `test_regression` among four; a
missing / empty / non-string / unrecognised future kind; and a citable live blocking record (a
named red outranks any kind label). `test_the_publishers_kinds_and_the_supervisors_set_have_not_
drifted` reads the producer modules' literals, so a fourth no-test-judged kind added there and not
here fails by name rather than silently restoring the defect (R10).

## Live payload after the fix

Rendered against the real `.publish_gate_state.json`, the draw now carries
`NO TEST WAS EVER JUDGED IN THIS EPISODE -- THE OPENING INSTRUCTION ABOVE DOES NOT APPLY`, names
`commit_did_not_land`, points at `sim-runner-log.md`, and no longer contains
"run the gate's argv without `-x`".
