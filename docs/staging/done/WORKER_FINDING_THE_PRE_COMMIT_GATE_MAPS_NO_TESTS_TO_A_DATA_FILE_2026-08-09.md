# [WORKER-FINDING] The pre-commit test gate maps ZERO tests to a non-`.py` file, so behaviour-determining IaC commits untested (2026-08-09)

**Severity:** BLOCKING · **Lane:** H_harness

**Found during:** the second publish-wedge unwedge — *by causing it*. My own manifest change passed
the pre-commit gate and wedged the publish gate on the very next cycle.
**Disposition:** QUEUED. Small, precise, and it has a working implementation to borrow from.

## Observed, with evidence

`tools/pre_commit_test_gate.py::tests_for()`:

```python
def tests_for(path: str) -> list[str]:
    p = Path(path)
    if p.suffix != ".py":
        return []
    ...
```

A changed non-`.py` file selects **no tests at all**. `background/process_manifest.yaml` is such a
file — and it is not incidental data. Its own header calls it *"the SINGLE authoritative manifest of
what SHOULD be running"*, the thing everything else DERIVES from, and the OPS1 design rule is that
**no behaviour-determining state may live outside the readable repo**. It is IaC by declaration.

`tests/background/test_process_reconciler.py` asserts **exact sets** computed from that file
(`test_systemd_owned_sessions_are_only_the_migrated_ones`, `test_startlist_is_enabled_dark_and_not_yet_migrated`).
So the manifest has real, tight test coverage that the gate will never select when the manifest is
what changed.

**The two selections, same session, as the discriminator:**

| commit | staged | gate selected |
|---|---|---|
| `6fb27763f` (changed `process_manifest.yaml`) | manifest + 7 `.py`/`.md` | 12 files — **`test_process_reconciler.py` absent** |
| `bafcfbfef` (changed `test_process_reconciler.py`) | that test file | 10 files — **`test_process_reconciler.py` present** |

The gate went green on the first, and the publish gate went red on it at 12:22 UTC
(`Publish-gate failure #1 (test_regression, rc=1)`), one cycle after I had cleared a ten-hour wedge.

## The fix already exists in this repo

`tools/select_impacted_tests.py` gets this exactly right, and says so in its own docstring (§33-34):

> *A changed file that is NOT a mappable repo `.py` module (a JSON/data/config/site file …) makes
> the selection UNSAFE-TO-NARROW -> it returns the [full suite]*

That is the correct policy — **cannot prove impact ⇒ do not narrow** — and it is R15's own doctrine
applied to test selection: a check that cannot answer must fail toward safety, not toward silence.
The pre-commit gate simply does not use it; it uses the shallow filename-convention `tests_for()`.

## What closing it looks like

1. Make `tests_for()` (or its caller) treat an unmappable staged path the way
   `select_impacted_tests` does: refuse to narrow. Reusing that module outright is the honest move —
   it is the same question, already answered and mutation-proven.
2. **R15 — the mutation it must fire on is this exact one:** stage a `process_manifest.yaml` edit
   that breaks `test_process_reconciler.py` and assert the gate refuses. Today it passes, so the
   control cannot fail on its own named defect.
3. Note the gap is **wider than YAML**: every `.json` config, every `docs/design/*.yaml` the code
   loads, and `maturity_map.yaml` are all in the same blind spot.

## Why it belongs with today's other two findings

All three are the same shape — a control whose *scope* was derived from a convenient proxy rather
than the real question:

* boot-SHA drift: population = a **declaration** (`launched_by`) instead of an observation.
* GHOST PUSHER: verdict = an **inference** (HEAD moved) instead of an attribution.
* this: coverage = a **filename suffix** instead of "what does this file actually affect".

Each is individually small. Together they are why a ten-hour outage alarmed as a fresh hour.

## Related

* `WORKER_FINDING_THE_STALENESS_DETECTOR_CANNOT_SEE_THE_DAEMONS_THAT_GO_STALE_2026-08-09.md`
* `WORKER_FINDING_THE_GHOST_PUSHER_GUARD_FIRES_ON_A_CONCURRENT_WRITER_2026-08-09.md`

— Worker finding, 2026-08-09, self-inflicted during the second publish-wedge episode.
