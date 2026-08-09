# WORKER FINDING — the epistemic verifier still exempts the crossing that no longer exists

**Date:** 2026-08-09
**Found by:** worker, during KNIFE pass 1 (`KNIFE1_reporting_cycle`)
**Class:** stale carve-out / latent fail-open (an exemption outliving the thing it exempted)
**Status:** QUEUED — not fixed on sight (outside KNIFE1's `file_scope`; one-hotspot-per-pass is a director wall)

## The finding

`tools/epistemic_verifier.py` carries:

```python
# SIM runner imports allowed in saas/reporting/ (structural orchestration, not epistemic).
# These run the SIM as a data source -- they do not read SIM internals into company state.
APPROVED_ORCHESTRATION = [
    "simulation.run_phase4c_on_phase2b",
    "simulation.run_segments",
]
```

Those two names are **exactly** the two class-(a) edges KNIFE pass 1 deleted.
As of this pass, `LEGACY_COMPANY_READS_SIM` is empty and neither reporting
module names `simulation` in any form. The carve-out now exempts a crossing
that does not exist.

## Why it is worth an atom rather than a shrug

A dead exemption is not inert — it is a **pre-authorised re-entry**. If either
import came back in `saas/reporting/`, this verifier would wave it through with
the comment "structural orchestration, not epistemic" — the same reasoning that
justified the crossing before the pass established it was avoidable. The pass
proved the premise false: both were CLI *composition*, and composition belongs
above both layers (`tools/run_annual_report.py`, `tools/run_segment_report.py`),
not inside the business layer.

**This is not currently an open hole.** `tests/architecture/
test_epistemic_wall_ratchet.py::test_no_new_company_reads_sim` now runs against
an EMPTY allowlist, so any new `saas -> simulation` edge is a hard failure with
no grandfathering left to hide behind, and its mutation proof still fires
(verified this pass, 12/12 green). The ratchet is the live guard; the verifier
carve-out is a redundant *second* opinion that would disagree with it. The
defect is the disagreement, not an unguarded direction.

## Suggested fix (not applied)

- Delete `APPROVED_ORCHESTRATION` and its two entries, plus the branch that
  consults it.
- If a genuine orchestration exemption is ever needed again, it should be
  expressed once — in the ratchet's allowlist, the single definition of "a
  crossing" — not as a second, independently-drifting register. KNIFE pass 3
  already owns "lift `build_edges` / `company_reads_sim` / `sim_reads_company`
  into a shared module so the ratchet, the KNIFE ledger and the passes read ONE
  definition"; **this carve-out is a fourth reader of that same concept and
  should be folded into that extraction.**

## Scope note

`tools/epistemic_verifier.py` is not in KNIFE1's `file_scope`
(`annual_report.py`, `segment_report.py`, `run_phase4c_on_phase2b.py`,
`run_segments.py`, `test_epistemic_wall_ratchet.py`). KNIFE3
(`KNIFE3_wall_crossing_paydown`) owns the shared-definition extraction and is
the natural home. Recommend attaching this to KNIFE3 rather than minting a
standalone atom.

## Related

- Sibling finding from the same pass:
  `WORKER_FINDING_ARREARS_RAG_IS_FAIL_OPEN_ON_A_MISSING_LEDGER_2026-08-09.md`
