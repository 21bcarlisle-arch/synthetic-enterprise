# [WORKER-FINDING] The publisher wrote the stamp with one commit's code and judged it with another's, twenty-five minutes apart (2026-09-01)

**Severity:** BLOCKING (this was the live wedge) · **Lane:** H_harness

**Found:** 2026-09-01, RUNG-1 scheduled tick drawn to a 673-minute publish-gate wedge. The draw
said "there is no red test to find" and pointed at the refusing gate's own banner in the
publisher log tail. It was right that no test was red, and the banner named the refusal but not
its cause: the cause is not in the tree at all, it is in *when* a running process read the tree.
**Disposition:** DIAGNOSED AND FIXED — born archived, existing class `publish_gate_and_wedge`.
**Class:** `publish_gate_and_wedge` (19th ruling). Not a new class.

## What refused

`docs/observability/sim-runner-log.md`, 03:05 UTC, immediately above `Commit/push failed`:

```
Provenance stamp skipped (non-fatal): REFUSING TO PUBLISH A FALSE PROVENANCE --
  showing_run.population is missing ...
Auto-process publish REFUSED -- REFUSING TO PUBLISH A FALSE PROVENANCE: (4 violations)
Commit/push failed (provenance_refused)
```

Not a pre-commit hook. `background/publish_provenance.publishable_violations` — the publisher's
own fail-closed provenance guard, refusing a stamp the publisher itself had just written.

## Why it refused, established from timestamps

| UTC | Event |
|---|---|
| 02:37 | `d95c659e3` is main. Its `record_verified` call site passes **no** `population`; its `publish_provenance` does **not** require one. Consistent pair. |
| ~02:40 | Publisher process starts, loads `process_run_complete.py` **at d95c659e3**. |
| 02:49 | `d9b9dd2f3` merges origin's 23 commits, bringing `31def55aa` — which rewrites **both sides**: population now REQUIRED and now SUPPLIED. Both files rewritten on disk. |
| 03:05 | The still-running 02:40 process reaches `_process()` and executes a **function-scope** `from background import publish_provenance`. First import in that process, so `sys.modules` binds the **02:49** module. |

Old call site, new checker. The stamp was written without `population` by code that never knew
the field existed, and judged by code that requires it. Verified directly:

```
$ git show d95c659e3:background/process_run_complete.py | grep -A3 record_verified
        _state = _prov.record_verified(
            run_id=json_path.name, git_commit=git_hash,
            generated_at=(data.get("meta") or {}).get("generated_at"))   # <- no population
$ git show d95c659e3:background/publish_provenance.py | grep -c "population is missing"
0
$ git merge-base --is-ancestor 31def55aa d95c659e3  ->  NO (arrived only via the 02:49 merge)
```

**Neither commit is defective.** Each is internally consistent. Only the pair is impossible, and
the pair existed only inside one process, for one cycle.

## Why this class of wedge reads as self-clearing and repeats

Every symptom points away from the cause. The scoped suite is green — because the tree is fine.
`git status` is clean of anything relevant. Re-running the gate's pytest argv costs ~10 minutes
and comes back green, which is the exact trap the draw warned about. The next cycle, launched
after the merge, is a consistent pair and publishes normally — so the wedge "heals" without
anyone learning anything, and the episode is available to repeat on the next merge that touches
both sides of any call in the publish path.

A publish cycle here runs ~25 minutes (02:40 → 03:05) in a tree several lanes land into. A
lazy import inside that path is a read of the tree at an arbitrary point 25 minutes after the
process's own code was read. That is not exotic; it is the normal condition here.

Same shape as `f5a9004c2` ("the wedge detector has been reporting from a module it loaded six
days before the repair") and `1280c6313` ("the thing that ran was not the thing that was
reviewed"). Third instance in a day. `background/boot_sha.py` already generalises this for
**daemons** (boot SHA vs HEAD), and it does not reach here: the publisher is a short-lived
subprocess, and the skew is *intra*-process — its own source versus a module it imports later.

## The repair

`background/process_run_complete.py`: `publish_provenance` is now bound in the module-scope
import block, and the five function-scope imports rebind that one object. `sys.modules` caches
on first import, so where the first import happens decides which generation the process gets;
at module scope it is pinned to the process's own generation. An old process now writes an
old-shape stamp — correct by its own code, publishable by its own checker — and the next cycle
upgrades it. The mixed pair is what could not be made to work.

This does not try to stop the tree changing under a running publisher. It makes the publisher
consistent with itself, which is the only property it can actually hold.

## The control

`tests/background/test_published_provenance_is_real.py`, two tests, keyed to the property (one
generation of the module per process) and not to today's line numbers:

* `test_the_checker_sees_a_function_scope_import` — FIRES on the defective shape.
* `test_the_publisher_binds_one_generation_of_its_provenance_module` — SILENT on current source,
  and refuses a **vacuous** pass: deleting the binding entirely is also red.

**Mutation-proved against the real defect, not a synthetic one.** Run against
`git show HEAD:background/process_run_complete.py` (the pre-fix source), the checker returns
function-scope imports at lines `[4789, 4809, 4871, 4906, 6353]` and `module_scope=False` — the
five sites that were live. Not an equivalence.

## What is NOT established

* Whether the earlier failures of this 15-failure episode share this cause. Only the 03:05
  failure was diagnosed to a mechanism; the earlier ones are recorded as `commit_did_not_land`
  with their own banners, and I did not read them. **I cannot yet say** the episode had one
  cause, and this finding does not claim it.
* Whether other lazy imports in the publish path can produce the same skew across a different
  pair. Almost certainly yes in principle; not measured, and not fixed here. The fix is scoped
  to the pair that actually refused.
