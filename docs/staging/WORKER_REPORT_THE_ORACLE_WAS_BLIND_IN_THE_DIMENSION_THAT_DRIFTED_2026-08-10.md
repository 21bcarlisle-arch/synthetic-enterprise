# WORKER REPORT — the staleness oracle was blind in the one dimension that drifted

**Date:** 2026-08-10 · **Found by:** scheduled worker tick, rung-1 publish-gate wedge
**Closed at:** `b2f0fc8f8` (pushed; `origin/main` verified equal)
**Class:** derived-artefact staleness — **third** occurrence. R3 two-strike already spent on the
repair mechanism (`WORKER_FINDING_A_REPAIR_DOWNSTREAM_OF_ITS_OWN_GATE_CANNOT_LAND_2026-08-10`).

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

## Still open — NOT closed by this commit

The repair remains **downstream of the gate it exists to unwedge**: it writes correct bytes, but the
publish path commits only after a green gate, and the staleness *is* what reds the gate. An oracle
fix makes the repair *see* the problem; it does not let it *land* the fix. Until the repair can
commit independently of the gate's verdict, this class recurs on every derived-artefact drift.
That item stays filed and undischarged.
