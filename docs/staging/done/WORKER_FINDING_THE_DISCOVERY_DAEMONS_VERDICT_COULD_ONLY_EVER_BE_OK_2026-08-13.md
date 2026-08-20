# WORKER FINDING — the discovery daemon's verdict could only ever be "ok"

**Severity:** LATENT · **Lane:** H_harness

**Date:** 2026-08-13 · **Found by:** the director's "restart or formally retire it, no third state"
instruction, which required deciding whether the daemon was worth restarting

## Observed

`background/discovery_agent.py::_assess_assumption()` scores each assumption like this:

```python
response = _call_qwen(prompt, max_tokens=150)
verdict = "ok"
note = "Qwen assessment unavailable"

if response:
    verdict_match = re.search(r"VERDICT:\s*(ok|warning|critical)", response, re.IGNORECASE)
    ...
```

`_call_qwen` returns `""` on a non-zero curl exit, a timeout, a JSON decode error, or **any**
exception — it catches bare `Exception` and falls through to `return ""`. So every one of those
paths reaches the caller as `verdict = "ok"`.

An absent model scores every assumption as realistic. So does a malformed response, a truncated
one, and one where the verdict line simply does not match the regex.

**The record is consistent with that.** `docs/observability/discovery-log.md` holds **106 completed
cycles** from 2026-06-19 to 2026-08-10. Warnings raised: **0**. Criticals raised: **0**. Not one
cycle in nearly two months ever returned anything but "ok", across every assumption it looked at.

Two further facts that bound what those 106 cycles are worth:

1. **It checked 10 of 176.** Each cycle logs "176 assumptions to review" and then reviews `max_rows=10`
   — the rows matching the three `HIGH_PRIORITY_ASSUMPTIONS` name prefixes. The other 166 were counted
   in the log line and never assessed.
2. **It still uses `/no_think`.** `docs/PROJECT_OVERVIEW.md` (Phase 6) records that this suffix
   convention "doesn't reliably suppress qwen3's reasoning mode on this server — a live call came back
   with an empty `response` (the whole answer sitting unused in a separate `thinking` field)". The
   fix was the explicit `"think": false` API parameter. That fix was applied to
   `company/compliance/internal_audit.py` and never back-ported here. The known-empty-response mode
   lands on exactly the `if response:` branch above.

## Why it matters

This is R15's **FAIL-OPEN** killer pattern (passes on missing/zero/empty/malformed) sitting in a
control whose entire job was to tell us when a sim assumption had drifted from reality. R15's
verdict on that shape is not "weak control", it is: *a control that cannot fail is worse than none*,
because it is read as evidence. Two months of "0 critical" reads like assurance that the assumptions
are sound. It is not evidence of that, and never was.

The daemon is **not** the whole loss here — the honest statement is that the *scheduled
re-validation of `ASSUMPTIONS.md` has never actually worked*, from 2026-06-19 onward. Retiring the
daemon does not open that gap. It stops the gap being invisible.

## Disposition

**RETIRED**, 2026-08-13, by director instruction ("restart or formally retire it, no third state").
Recorded in `background/process_manifest.yaml` with both reasons: this fail-open verdict path, and
the fact that its only model path (`_call_qwen` → qwen3:14b) was deliberately evicted by the
2026-08-10 MEMORY_CLEANSE to reclaim 5.1GB on a 16GB box already 3.8GB into swap. Restarting it
would have reloaded a 5.5GB model 6-hourly to run a check that cannot fail.

The code is retired, not deleted. The manifest's `flip:` field states the price of revival, so a
future restart cannot quietly re-arm the same defect:

1. Make the verdict **FAIL-CLOSED** — an unavailable model is a FAILED check, not an "ok". The
   natural shape is a distinct `unavailable` severity that is loud, so a silent model outage
   reports as a broken instrument rather than a clean bill of health.
2. Adopt the explicit `"think": false` parameter, as `internal_audit.py` already does.
3. Decide honestly whether 10-of-176 is the intended scope or an unnoticed cap.

## What is NOT claimed

That any assumption in `ASSUMPTIONS.md` is actually wrong. Nothing here measured that. The claim is
only that the daemon's 106 "ok" verdicts are not evidence either way — the instrument could not have
said anything else.

---

## Cleared as a publish-gate wedge suspect, 2026-08-20 (archival provenance)

`.publish_gate_state.json` named this document in `cited_findings` for the whole 13-run wedge
episode of 2026-08-20, so every wedge doorbell for ~7 hours told the drawing seat to dispose of
it FIRST, before any product work. It was never the cause and could not have been.

**Observed-with-evidence (R9):** the episode's single red, recorded in the same state file, was
`tests/controls/test_control_mutation.py::test_dashboard_consistency_gate_fires_on_surface_disagreement`.
That test calls `tools/generate_dashboard_data.py::_check_consistency`. This finding's subject is
`background/discovery_agent.py::_assess_assumption`. No import path, no call path and no shared
fixture connects them; `background/discovery_agent.py` is not in the gate's argv at all, and the
daemon has been `state: retired` in `background/process_manifest.yaml` since 2026-08-13 — it does
not run, so it cannot red anything.

**Why it was cited anyway:** the alert's suspect ranking, not this document. Commit 159172f5e
records the mechanism — the suspect list is ranked by AST traversal depth with a cap of eight, and
this project's test convention puts the subject-under-test deeper than that cap can see, so the
ranker returned eight modules none of which could reach the red. `cited_findings` was populated
from the same ranking. Generalised as
`feedback_the_wedge_suspect_block_can_be_entirely_wrong_so_grep_the_failing_nodes_own_symbol_first`.

**Disposition unchanged:** RETIRED (above). The revival price in `process_manifest.yaml`'s `flip:`
field still stands, and clearing it as a wedge suspect neither revives it nor discharges the real
gap this document names — that the scheduled re-validation of `ASSUMPTIONS.md` has never worked.
Archived to `done/` because the disposition is complete, not because the wedge cleared.
