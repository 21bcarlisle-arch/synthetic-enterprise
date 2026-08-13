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
