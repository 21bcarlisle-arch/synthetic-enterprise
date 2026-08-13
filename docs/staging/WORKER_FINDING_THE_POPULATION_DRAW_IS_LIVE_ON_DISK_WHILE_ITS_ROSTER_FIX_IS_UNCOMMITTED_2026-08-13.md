# [WORKER-FINDING] A curriculum activation goes live from disk before the code that serves it (2026-08-13)

**Severity:** LATENT · **Lane:** W2_customer_generator

**Status:** the INSTANCE closed under me while I was writing this up — commit `9158e8ce4` landed
the roster fix at 06:53 UTC, about fifteen minutes after I observed the red. The CLASS is
untouched and is what this document is for. Filed at LATENT, not BLOCKING, because there is no
live red left to hold a lane: reporting a closed instance as a blocker would be a false blocker.
Found while trying to R11-verify
`WORKER_REPORT_THE_TWO_PRICING_LOOPS_ARE_NOW_ONE_CHAIN_2026-08-13.md` against the published
annual report and finding the artefact frozen.

## The observation (`observed-with-evidence`, `docs/observability/sim-runner-log.md`)

Seven consecutive sim runs failed across five different HEADs, two distinct causes:

```
- [2026-08-13 05:29 UTC] Run FAILED (rc=1) after 121s     KeyError: 'epc_rating'
- [2026-08-13 05:36 UTC] Run FAILED (rc=1) after 119s
- [2026-08-13 05:43 UTC] Run FAILED (rc=1) after 119s
- [2026-08-13 05:52 UTC] Run FAILED (rc=1) after 257s     KeyError: 'SYN-2021-001'
- [2026-08-13 06:01 UTC] Run FAILED (rc=1) after 259s
- [2026-08-13 06:11 UTC] Run FAILED (rc=1) after 261s
- [2026-08-13 06:20 UTC] Run FAILED (rc=1) after 258s
```

```
File "saas/reporting/annual_report.py", line 120, in _build_clv_snapshots
  cts_to_year = build_cost_to_serve(records_to_year, CUSTOMERS + SUCCESSOR_CUSTOMERS)
File "saas/cost_to_serve.py", line 152, in build_cost_to_serve
  segment = segment_by_customer[customer_id]
KeyError: 'SYN-2021-001'
```

`build_cost_to_serve` documents *"Raises KeyError if a settlement record references a customer_id
not present in `customers`"* — it behaved exactly as designed. Nothing was broken; two halves of
one change were simply not landed together.

## The class: a config half that needs no commit to fire

* **Live from disk immediately:** `docs/design/curriculum/population_draw_activation.json`. The
  runner reads config off the working tree, so the drawn book was ACTIVE — `SYN-2021-*` records
  reaching the reducer — from the moment the file existed.
* **Live only once committed:** the roster fix in `_build_clv_snapshots`. At the time of the
  failures it was written and correct in the working tree and absent from HEAD; the runner
  executes committed code, so for 61 minutes the world was drawing a population the reporting
  path had no roster for.

**That asymmetry is the class, and it is structural:** an activation artefact takes effect with
no commit, its code path takes effect only with one, so the two halves *cannot* be landed
atomically by construction. Every `docs/design/curriculum/*_activation.json` has this shape. The
instance is closed; the next activation has the same hole waiting.

**Class fix (R10 — an instance fix does not close this):** the activation reader refuses to arm
an activation whose required code path is not present at HEAD — i.e. arming is conditional on
the committed tree, not on a file existing on disk. That turns a silent 61-minute outage into a
refusal with a reason at arming time, and it is checkable in the reader rather than relied upon
as discipline.

## Still open

The `epc_rating` failures before 05:52 are a **second, earlier cause on the same lane** and are
not explained by the roster fix. Nothing here confirms they are closed. Whoever picks this up
should verify one green end-to-end run rather than reading the disappearance of `SYN-2021-001`
as the whole recovery — the two causes were never the same bug.

## Cost, for the record

`docs/reports/ANNUAL_REPORT.md`, `LATEST.md` and `dashboard.json` were frozen for the whole
window, so no repair to any published figure could be R11-verified against its artefact — which
is how this was found rather than by anyone watching the runner.
