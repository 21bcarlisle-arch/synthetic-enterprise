# WORKER FINDING — a top-level import wedged every publish, and the smoke check used an entry mode nothing launches

**Severity:** BLOCKING · **Lane:** H_harness · **Disposition:** FIXED IN THIS TICK (RUNG 1, publish-gate wedge)

**Discharged:** `tests/background/test_declared_entrypoints_import_in_script_mode.py::test_entrypoint_imports_when_launched_as_a_script_path`

The severity states what this tick FOUND — every publish on the box was dead — not what it left.
The discharge above is the named falsifier, mutation-proven both ways in the table below.

**Found:** 2026-08-17 scheduled worker tick, drawn as the RUNG-1 publish-gate wedge item
(4 failures in-window, no pass at HEAD `0a3b39ee9`, episode counter 257).
**Subject:** `background/process_run_complete.py` line 16, landed by `0a3b39ee9`.
**Class:** publish-gate/wedge — the control that stops publishing, and what it stops on.
**Measured at:** HEAD `0a3b39ee9` plus this tick's tree. Everything below is
`observed-with-evidence` (R9); the one `inferred` claim is labelled where it appears.

## The measurement

The wedge was **not a red test**. The publish gate never ran. Every publish since 10:31Z died
at module import, before `main()` was reached — from `docs/observability/sim-runner-log.md`:

```
- [2026-08-17 10:44 UTC] Auto-process failed (rc=1) -- marker left for background_worker
  publisher stderr (last 40 lines):
Traceback (most recent call last):
  File "/home/rich/synthetic-enterprise/background/process_run_complete.py", line 16, in <module>
    from background.publish_step_ledger import PublishStepLedger
ModuleNotFoundError: No module named 'background'
```

Reproduced directly at HEAD:

```
$ python3 background/process_run_complete.py
ModuleNotFoundError: No module named 'background'
```

`0a3b39ee9` added `background/publish_step_ledger.py` (new file, `git ls-tree HEAD` confirms it
is committed — this is not a missing-file defect) and a **top-level** import of it. Both daemons
launch this module **as a script path**:

* `background/sim_runner.py:200` — `subprocess.run([sys.executable, str(processor), str(marker)], cwd=PROJECT_DIR)`
* `background/background_worker.py:399` — the same shape

Python seeds `sys.path[0]` from the **script's own directory**, never from cwd. Inside that
process the root is `background/`, so `import background` cannot resolve. `cwd=PROJECT_DIR` on
both call sites looks like it should prevent exactly this, and does nothing whatsoever.

The module already knew the rule. Three call sites (lines 3505, 3647, 4929) catch
`ModuleNotFoundError` and retry the flat name, each commented *"launched as `python3
background/process_run_complete.py`"*. A top-level import has no such second chance.

## Why it was invisible, and why the visibility was one day old

Two separate reasons, and the second is the one worth keeping.

**1. The swallow had only just been removed.** `0a3b39ee9` — the commit that introduced this
import — is also the commit that stopped the publish path swallowing its own crashes. Had the
order been reversed, this would have read as the 258th identical `rc=1` with no cause attached,
like the 257 before it. The traceback quoted above exists **because** of the commit that broke
this. That is the swallow-removal paying for itself within one cycle.

**2. The smoke check tested an entry mode nothing uses (R15, wrong subject).** A check did exist
and was GREEN throughout — `background/start_worker.sh:129`:

```
SMOKE_ERR="$(python3 -c 'import background.ntfy_utils, ..., background.process_run_complete' 2>&1)"
```

`-c` puts **cwd** on `sys.path`; `-m` puts the **root** on it. Both entry modes the repo checked
are immune to this defect by construction. The one entry mode the daemons actually use was
checked by nothing. The control and the daemons disagreed about how the module is entered, so
the control could not fail — R15 killer pattern, wrong subject.

## The fix, and why it is a path bootstrap and not a fourth try/except

`background/process_run_complete.py` now puts the repo root on `sys.path` **above** the import.
It is idempotent and a no-op under `-m`.

The try/except idiom used by the three older sites was deliberately **not** extended here. It is
per-import and it *defers* the failure — and the deferred form is already on record in the same
log, one cycle earlier:

```
  File ".../background/process_run_complete.py", line 2627, in generate_dashboard_json
NameError: name 'PublishStepLedger' is not defined
```

That is the same defect surfacing 2,600 lines downstream, inside dashboard generation, with the
true cause gone. A swallowed import is strictly worse than a loud one.

## The class control (R10 — the class fails automatically, not the instance)

`tests/background/test_declared_entrypoints_import_in_script_mode.py`. It executes each
entrypoint's **top level** in a faithful script-mode `sys.path` (script's own directory on the
path, cwd deliberately foreign) under a non-`__main__` name, so the import block runs and no
daemon starts.

The population is **derived, never hand-listed**, from two halves:

* `background/process_manifest.yaml` — every `command: python3 <x>.py`. A daemon declared
  tomorrow is covered the moment it is declared. `-m` launches are deliberately not collected.
* an AST sweep of `background/` and `tools/` for `subprocess.<run|Popen|...>([sys.executable,
  <a .py path>, ...])`. **This half is the one that matters**: the module that actually broke is
  a subprocess of two daemons and is *not in the manifest*. A manifest-only population would
  have been green through the entire outage.

16 entrypoints discovered; 16 pass.

### R15 — mutation-tested both ways, this tick

| Mutation | Result |
|---|---|
| `sys.path` bootstrap removed from `process_run_complete.py` | **FAILS by name**: `test_entrypoint_imports_when_launched_as_a_script_path[background/process_run_complete.py]`, `ModuleNotFoundError: No module named 'background'` |
| AST discovery half blinded (manifest half left intact) | **FAILS**: `test_the_discovery_itself_found_the_population` — `background/process_run_complete.py` no longer in the population |
| unmutated | 16 passed |

The second mutation is the fail-open guard, and it is the one that proves the census is not
vacuous: it demonstrates *by execution* that the manifest half alone is blind to the module that
caused this wedge.

## What this does not claim

* It does not claim the episode's earlier 257 failures share this cause — they predate this
  import and their causes were swallowed. **`inferred`**: they are a different, older stack.
  This finding closes the failure at HEAD, not the episode's history.
* It does not change the gate's scope, subject, deselections, or state files.
* `start_worker.sh`'s smoke check is left exactly as it is. It is not wrong, it is *narrow*, and
  the new test covers what it cannot reach. Widening a shell smoke check to spawn 16 subprocesses
  at every worker start would buy nothing the test suite does not already own.
