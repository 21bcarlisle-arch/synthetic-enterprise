# WORKER REPORT — the staleness oracle was blind in the one dimension that drifted

**Severity:** BLOCKING · **Lane:** H_harness

**Date:** 2026-08-10 · **Found by:** scheduled worker tick, rung-1 publish-gate wedge
**Closed at:** `b2f0fc8f8` (pushed; `origin/main` verified equal)
**Class:** derived-artefact staleness — **third** occurrence. R3 two-strike already spent on the
repair mechanism (`WORKER_FINDING_A_REPAIR_DOWNSTREAM_OF_ITS_OWN_GATE_CANNOT_LAND_2026-08-10`).

**Discharged:** `tests/background/test_forward_attachment_register.py::test_an_annotation_only_drift_is_stale_though_every_PAIR_is_intact`, `tests/background/test_forward_attachment_register.py::test_live_rendering_is_current` — the oracle repair had landed in August with no falsifier of its own; this tick pinned it, and reverting the oracle to pairs-only makes the new test the only one of the file's 20 that fails. The residue this report names — a repair that cannot land while the gate it repairs is red — is NOT discharged here and stays open under its own finding. 20 green, 2026-08-12.

## The wedge, in one line

`tests/background/test_forward_attachment_register.py::test_live_rendering_is_current` red at HEAD
for ~1000 min / **98 consecutive failures**, blocking all publishing with 56 `run_complete_*`
markers queued.

## Cause (observed, R9)

The D19 map bump — `level_current 0 -> 2`, `loop_stage build -> harden` — changed **one rendered
annotation line** in `docs/design/FORWARD_ATTACHMENT_LEDGER.md`:

```
-_epoch 3 · lane D_billing_metering · L0→L2 · build_
+_epoch 3 · lane D_billing_metering · L2→L2 · harden_
```

Every `(atom_id, source)` **pair** was unchanged. That is the whole finding:

- the blocking test asserts **whole-text equality** against a fresh derivation;
- `forward_attachment_register.check()` compared only **pairs** — a strict SUBSET;
- `background/derived_artefact_register.py` drives that `--check` as its **staleness oracle**.

So the self-healing repair built to close this very class asked a question that could not see the
staleness, reported nothing stale, and HEAD stayed red for 98 cycles.

**A repair is only as good as its oracle. The oracle must assert everything its blocking test does.**

## R15 proof — on the real defect, not a synthetic mutation

Against HEAD's own stale ledger, in a clean checkout:

| oracle | rc | output |
|---|---|---|
| before (pairs only) | **0** | `13 attachment(s) across 10 atom(s); 0 violation(s).` |
| after (whole-text)  | **1** | `VIOLATION stale_rendering: ... differs from a fresh derivation` |

The old oracle reports **zero violations on the exact file that reds the gate**. Fail-open, proven.

## Fix

`check()` now makes whole-text comparison the **last word**; pair-level violations are kept because
they name a fabricated or dropped row precisely, but they are no longer the only thing between
drift and the gate. Plus the regenerated ledger line that unreds HEAD.

Verified: **19/19 green** in a clean `git archive HEAD` export of `b2f0fc8f8`, and the hardened
`--check` returns rc=0 there.

## A phantom second cause — method note worth keeping

A full-gate run in a plain `git archive HEAD | tar -x` export produced a *second* failure:
`test_blocked_atom_visibility.py::test_the_real_staleness_clocks...` with
`RuntimeError: git blame --line-porcelain failed: fatal: not a git repository`.

**This is an artefact of the reproduction, not a defect at HEAD** — the export has no `.git`, so
`tools/map_assertion_provenance.py` cannot blame. The real gate builds a standalone repo. Confirmed
by ordering: `blocked_atom_visibility` sorts *before* `forward_attachment` and 344 tests ran in the
real gate, so it passed there.

To reproduce a gate red faithfully, rebuild the checkout the way
`process_run_complete._make_checkout_a_repo` does: `git init`, write the real repo's
`objects/info/alternates`, raw SHA into `.git/HEAD`, `git read-tree <sha>`, then symlink `sim/cache`
and `node_modules`. Without that, a run manufactures failures that do not exist at HEAD.

## The SECOND cause, found only by running the full gate (`3975775e0`)

The gate runs `-x`. Fixing the first red does not tell you HEAD is green — so the full suite was run
against the fixed HEAD, and a second blocker was sitting behind it:
`tests/background/test_publish_gate_disk_preflight.py`, **3 failed / 5 passed**.

At HEAD the anti-vacuity tripwire armed on `prc.tempfile.mkdtemp`. Since OPS2 the HEAD checkout is
**reused**, so the ordinary path takes the reused-checkout lock and calls `_prepare_reused_checkout`
— `mkdtemp` is never reached. Every test asserting the guard is PASSED (ample space, unmeasurable
space, zero-threshold mutation) fails `DID NOT RAISE`.

**It only passes when another publisher happens to hold the lock** and the throwaway `mkdtemp` path
is taken — which is why the real gate never saw it: the gate always runs while its own parent
publisher holds that lock. A tripwire whose firing depends on concurrent lock state is not a control.

Re-armed on `_head_sha`, called on **both** paths. 8/8 green.

## A live landmine, defused

`tests/background/test_publish_gate_blocking_payload.py` was sitting **staged in the shared index**
with its code counterpart (`background/process_run_complete.py`, +125 lines) still uncommitted.
Against HEAD's code it is **11 errors**. Any process doing a plain `git commit` with no pathspec
would have landed it alone and re-wedged publishing instantly.

Unstaged (file untouched on disk). Restore with
`git add tests/background/test_publish_gate_blocking_payload.py` — but land it **with** its code.
That lane's work is coherent as a unit (53 passed with the working-tree module + its tests), but
`background/supervisor.py` is also modified and may hold the reader; landing the writer alone would
be a publish-with-no-consumer seam. Left for its own lane.

## Still open — NOT closed by this commit

The repair remains **downstream of the gate it exists to unwedge**: it writes correct bytes, but the
publish path commits only after a green gate, and the staleness *is* what reds the gate. An oracle
fix makes the repair *see* the problem; it does not let it *land* the fix. Until the repair can
commit independently of the gate's verdict, this class recurs on every derived-artefact drift.
That item stays filed and undischarged.
