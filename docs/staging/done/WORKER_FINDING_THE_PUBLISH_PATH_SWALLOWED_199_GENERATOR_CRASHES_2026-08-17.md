# [WORKER FINDING] The publish path swallowed 199 generator crashes and served a frozen artefact for four days

**Severity:** BLOCKING · **Lane:** H_harness
**Found:** 2026-08-17 worker tick, at BUILD on `W2_17_dual_fuel_leg_clv_attribution` (not in the finding that minted it)
**Subject:** `background/process_run_complete.py` (the per-generator `except Exception: log(...)` blocks), `tools/generate_customer_sample.py:226-229`

## What was found

`process_run_complete.py` wraps each site-data generator in its own
`try / except Exception` and, on failure, calls `log()` and continues:

```python
    try:
        from tools.generate_customer_data import generate as gen_cust
        gen_cust(json_path)
        log("Generated site/data/customers/ JSON")
    except Exception as exc:
        log("Customer data generation failed: {}".format(exc))
```

No alarm, no NTFY, no gate, no non-zero exit — and, critically, **no removal of the
artefact the failed step was supposed to refresh**. The previous run's output stays on
the publish path and keeps being served.

`observed-with-evidence` — counted from `docs/observability/sim-runner-log.md`:

| step | total failures logged | `__round__` crashes | first `__round__` crash |
|---|---|---|---|
| Customer data generation | 130 | **99** | 2026-08-13 21:53 UTC |
| Customer sample generation | 131 | **100** | 2026-08-13 21:53 UTC |
| Billing ledger generation | 32 | 0 | — |
| Live portfolio generation | 31 | 0 | — |
| Invoice data generation | 31 | 0 | — |

199 crashes of one shape, on every publish, from 2026-08-13 21:53 to 2026-08-17 10:41 —
**a little under four days**. `site/data/customers/*.json` was last actually written by
the publish path at commit `528c2559e` (2026-08-13 19:21), 2h32m before the first crash.
Everything the customer pages served after that was that frozen snapshot.

## Why nobody saw it

The staleness was invisible from every direction that normally catches it:

* **The artefact existed and parsed.** `_retire_departed_artefacts` only removes accounts
  absent from a run that SUCCEEDED, so a crashed run retires nothing and disturbs nothing.
* **The figures were plausible.** The frozen snapshot carried a full lifetime-value book
  (C1 `clv_gbp` 2840.5, C_IC3 3137524.98). A blank page gets noticed; a stale-but-complete
  one does not.
* **The controls read the frozen file and were satisfied by it.**
  `site/customers/test_wall_exhibit.py`'s vacuity guard asserted the closed household
  carried live forward-looking figures — and it did, because it was reading the 2026-08-13
  snapshot. The control was green *because* publishing was broken. It went red the moment
  the generator was fixed and wrote the current run's real values.
* **R2's shape, on a document.** The fix that produced the crash (`build_clv` returning
  `clv_gbp: null` for accounts no longer supplied) was committed and green; it simply never
  reached the artefact, and nothing checks that it did.

## Root cause of the crash itself

`round(clv_data.get("clv_gbp", 0), 2)` — the `.get(k, 0)` default handles a MISSING key but
not a key PRESENT AND NULL. Once `build_clv` began recording `clv_gbp: null` for the five
no-longer-supplied accounts (C1, C3, C4, C5, C6 — all `still_supplied: false`, which is
correct behaviour), every publish raised `TypeError: type NoneType doesn't define
__round__ method`.

The `generate_customer_data.py` half is **fixed and landed** by `W2_17` in this same
commit. **`tools/generate_customer_sample.py:226-229` carries the identical defect and is
NOT fixed** — it is outside `W2_17`'s `file_scope`, and it is still crashing on every
publish (100 of the 199). Registered here rather than fixed on sight, per
SELF_INTERRUPT_DISCIPLINE.

## Why this is BLOCKING and not LATENT

The damage is not hypothetical and not internal: `poesys.net` served four days of
per-customer figures that the company's own current run does not produce, under a
present-day data stamp. That is the R11 defect (the published value is not the computed
value) reached through a channel R11's own checks cannot see, because they verify the
rendered value against the published FILE and the file was internally consistent.

The class is wider than these two generators. Nine `except Exception: log(...)` blocks sit
on the publish path; each one converts a publish failure into a silently frozen artefact,
and four of them have fired for other reasons (32 + 31 + 31 + 1 + 1 times).

## What would close it (R10 — the class, not the instance)

1. A publish step that fails must make its own staleness **visible**, not just logged: the
   step's artefacts fail their freshness assertion, or the publish is marked degraded and
   NTFYs on the state transition (R5).
2. A control that reads a published artefact must assert that artefact's **production
   stamp is from the current run** — otherwise, as here, the control's subject is a file
   the publish path stopped maintaining. (Overlaps
   `WORKER_FINDING_THE_PUBLISHED_ARTEFACT_CARRIES_NO_PRODUCTION_STAMP_2026-08-15`.)
3. The `.get(k, 0)`-on-a-nullable-field shape should be swept repo-wide, not patched twice:
   `_round_or_none` in `tools/generate_customer_data.py` is the landed form.

R15 note: the control that *should* have caught this (the wall-exhibit vacuity guard) was
not merely absent — it was **actively green on the frozen file**. A control whose subject
is an artefact that stopped being written passes forever. That is killer pattern 3
(fail-silent) reached through the subject rather than through the checker.
