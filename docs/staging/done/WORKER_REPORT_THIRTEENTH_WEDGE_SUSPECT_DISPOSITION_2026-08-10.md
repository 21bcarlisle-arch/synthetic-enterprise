# [WORKER-REPORT] The thirteenth wedge: eight cited suspects, none of them the cause (2026-08-10)

**Tick:** scheduled worker tick, 2026-08-10 ~11:30 UTC. **Rung:** 1 (publish-gate wedge, PRIORITY ZERO).
**Episode:** 112 consecutive failures, `wedge_since` 2026-08-09 ~16:30 UTC.

## The measured cause (R9, `observed-with-evidence`)

Already named and fixed by the preceding tick in `4fccacf39` — this tick's job was to **verify** it,
not to re-find it. Reproduced independently before reading that commit message:

```
$ cd /tmp/publish-gate-head-reused          # the gate's own checkout, then at 1c6e87ff9
$ SIM_FAST_MODE=1 python3 -m pytest tests/background/test_forward_discovery_draw.py -q
8 failed, 15 passed
```

All eight fail on the same assertion, `sup._is_drained_and_gated() is True`. Bisecting the rungs
under the test's own gating fixture showed **every** rung returning falsy while the predicate still
answered `False` — so the refusal was not a rung at all. The final statement is
`return _rule0_harden_draw() is not None`, and calling it directly:

```
File ".../background/supervisor.py", line 1057, in _atom_evidence
    return _atom_store.records_for_atom(str(aid)).get("evidence")
AttributeError: module 'tools.simplifications_store' has no attribute 'records_for_atom'
```

Confirmed at the commit level, not inferred:

| commit | `def records_for_atom` in `tools/simplifications_store.py` |
|---|---|
| `1c6e87ff9` (parent) | **0** — absent |
| `4fccacf39` (HEAD)   | **1** — present (+221 lines) |

`_is_drained_and_gated` ends `except Exception: return False` (fail-safe toward work), so the
AttributeError never surfaced as an import error — the rest predicate merely answered `False`. That
is why the gate named a test about *resting* whose subject has nothing to do with the atom store,
and why the episode ran 112 cycles pointing at the wrong file.

## Disposition of the eight cited suspects: RE-FROZEN, with provenance

The wedge self-refill cited eight filed findings as "already holding the suspects". **None of them is
this cause.** Each is a real, separately-filed QUEUED finding, and each stays queued — re-frozen here
so the next tick does not re-draw them as wedge suspects:

| finding | class | why it is not this cause |
|---|---|---|
| `TREE_DIVERGENCE_FAILS_OPEN_TO_A_CLEAN_TREE` | R15 fail-open | measures squatting; never reaches the rest predicate |
| `TWO_UNIMPORTABLE_PHASE2A_MODULES` | dead code | both modules are inside `PUBLISH_GATE_HEAVY_IGNORES`' neighbours and are imported by nothing the gate collects |
| `WRITE_TIME_GATE_FIELD_SWALLOW` | control false-positive | commit-time gate, not suite-time |
| `THE_PRE_COMMIT_GATE_MAPS_NO_TESTS_TO_A_DATA_FILE` | coverage hole | would have caught a *data* change; this was a missing Python callee |
| `THE_SECOND_DIRECTION_NEEDS_ITS_OWN_POPULATION` | denominator defect | D11/D12 measurement, caught in-build, never published |
| `THE_WEDGE_ALARM_IS_DISARMED_BY_RUNS_THAT_PUBLISH_NOTHING` | alarm accounting | measures wedges; cannot cause one |
| `THE_MODELS_STORAGE_HEATER_IS_NOT_ONE` | world fidelity gap | `W1_12`, no gate surface |
| `THE_NAIVE_ARM_KEEPS_THE_LIVE_TONE` | counterfactual contamination | published diagnostic, not a control |

**The lesson worth keeping** (this is the third episode where the citation list mis-pointed): the
wedge self-refill cites findings by *recency and topic*, not by any link to the failing node ID. A
suspect list assembled that way is a reading list, not a diagnosis — and here it cost cycles, because
the actual cause was reachable in one step from the named test by *calling the rungs the assertion
depends on* rather than by reading the eight docs it recommended. Draw order should be: reproduce the
named node, bisect its assertion, **then** consult the citation list.

## Verification of HEAD

The fix landed at 11:30:28, **one minute after** the in-flight gate run (pytest started 11:29) had
already materialised the parent commit — so no gate run had yet judged HEAD, and the wedge state file
still showed the parent's reds. This tick built a faithful HEAD checkout (`git archive` + alternates +
the `sim/cache`/`node_modules` overlay, matching `_prepare_reused_checkout`) and ran the exact
`publish_gate_pytest_argv` there. Result recorded below.
