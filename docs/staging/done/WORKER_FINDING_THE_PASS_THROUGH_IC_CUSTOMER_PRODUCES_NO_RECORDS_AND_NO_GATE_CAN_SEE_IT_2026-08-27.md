**Severity:** LATENT · **Lane:** H_harness

# The pass-through I&C customer produces no settlement records, and no gate can see it

`C_IC3` — the 4 GWh pass-through industrial site — produces **zero** settlement records in a
full fast-mode run. The only test that asserts otherwise is excluded from every gate in the
repository, so this has been free to rot.

## Class registration

Belongs to `no_caller_and_never_runs`. The control exists, is correct, and is switched out of
every path that would run it.

## Observed

Running the test alone against the tree at `f1557cb39` (9m19s, full pipeline, `SIM_FAST_MODE=1`):

```
tests/simulation/test_phase40a_pass_through.py:248: AssertionError
E   AssertionError: C_IC3 should have settlement records in fast mode
E   assert 0 > 0
E    +  where 0 = len([])
```

**`C_IC3` appears nowhere in the run's output** — not in the term walk, not in a churn or loss
line, nowhere. It is not leaving mid-window; it is never present. That is a different failure
from the `x599.6` churn-multiplier blow-up that `_bill_scale_for` was written to fix, and it
survives that fix.

The run reaches line 248 at all only because of the `gap_ledger_path` route landed alongside
this; before that the test died earlier, at `live_ledger_guard`. So the guard was masking this
assertion, and fixing the guard route is what exposed it.

## Why nothing caught it

`tests/simulation/test_phase40a_pass_through.py` is excluded from **three** separate places:

| where | line |
|---|---|
| `background/process_run_complete.py` | 408 (publish gate `--ignore`) |
| `tools/head_green_census.py` | 80 |
| `tools/profile_test_suite.py` | 57 |

and it is additionally listed in `docs/observability/publish_gate_red_census.json`.

A file excluded from the publish gate, from the head-green census **and** from the suite
profiler has no path left on which it can fail. Its red is therefore not a signal anybody
receives — which is the definition of this class. The exclusions were presumably added for
runtime (this file costs ~9 minutes on one test), and that is a legitimate reason to move a test
off the hot path, but moving it off *every* path silently converts "slow control" into "no
control".

## What a fix has to do

1. **Diagnose the actual defect first** — establish whether `C_IC3` is absent from the fast-mode
   roster, filtered out before settlement, or dropped at a seam. R4: name the nearest working
   analogue (`C_IC1`/`C_IC2` are in the same roster and the sibling test passes) and state the
   diff. That comparison is the cheapest available and has not been done.
2. **Give the capability a control that runs somewhere.** If a 9-minute pipeline test cannot sit
   in the publish gate, it needs a cheaper subject — assert the roster/records seam directly
   rather than by running the whole decade — not a fourth exclusion.

**R15 note:** whatever replaces it must be mutation-tested by removing `C_IC3` from the roster
and confirming the new control reds. A control that passes because it, too, never sees `C_IC3`
would be this same finding again, one layer down.

**Not fixed here, deliberately** — SELF-INTERRUPT DISCIPLINE: queued as a finding rather than
chased on sight from a Lane 0 delivery turn whose subject was the three-arm A/B.
