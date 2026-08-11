# WORKER FINDING — the publish wedge's remaining cause is a FULL-SUITE-ONLY failure that MOVES

**Filed:** 2026-08-09 ~20:55, worker seat. **Disposition:** FILED, NOT FIXED.
**Context:** the epistemic-wall cause of the wedge was closed by `450bf6903`
(pushed as `d6f894b6e`). The wedge did NOT clear. This names what is left.

## OBSERVED (R9, evidence first)

**The wall cause is gone.** Gate run 20:38–20:44 on post-fix HEAD:

```
1 failed, 22616 passed, 5 skipped, 1102 deselected, 14 xfailed,
4 subtests passed in 592.89s        (/tmp/gate_run.log, 20:43:51)
FAILED tests/tools/test_website_integrity_fix.py::
       test_process_run_complete_generates_insights_before_dashboard
E   ValueError: substring not found
```

No wall crossing appears anywhere in that run. One test out of 22,616 now holds
publishing.

**That test passes in isolation, on the same commit.** Clean `git archive HEAD`
extract of `d6f894b6e`:

```
tests/tools/test_website_integrity_fix.py::test_process_run_complete_generates_insights_before_dashboard
  1 passed in 0.07s
tests/tools/test_website_integrity_fix.py            34 passed in 20.46s
tests/background/test_process_run_complete.py
  + tests/tools/test_website_integrity_fix.py        94 passed in 10.24s
```

**The failing test is not stable between runs.** Two gate runs, two different
single failures, neither reproducible alone:

| run | failing test | error |
|---|---|---|
| 20:02:52 | `test_process_run_complete.py::test_main_success_flow` | `TypeError: data must be str, not MagicMock` |
| 20:43:51 | `test_website_integrity_fix.py::test_..._insights_before_dashboard` | `ValueError: substring not found` |

**Both failures are shaped like a leaked mock.** The first receives a `MagicMock`
where a `str` is required. The second is
`inspect.getsource(prc._process).index("generate_insights(data, git_hash)")` — a
literal source-text search, which cannot find its substring if `prc._process` has
been replaced by a patched object rather than the real function.

## INFERRED — labelled as such, NOT established

The remaining wedge is a **test-isolation defect**: some earlier test in the
22,616 leaves `background.process_run_complete` patched/reloaded, and whichever
downstream test touches it next fails. That would explain the failure MOVING
between runs while every candidate passes in isolation. **Not proven** — the
pollution source was not located; the two obvious suspects run clean together
(94 passed), so it lies elsewhere in the suite.

## WHY THIS MATTERS BEYOND THE INSTANCE

Fixing whichever test failed last would be an instance fix on a moving target and
is forbidden by R10 — the failure is a symptom of the pollution, not the defect.
The class is the isolation leak.

A second-order point: `test_..._insights_before_dashboard` asserts ordering by
searching the function's SOURCE TEXT for one exact call spelling. That control is
keyed to a single syntactic form — any reformatting or re-spelling of the call
breaks it without any behaviour changing, and it cannot distinguish "the ordering
is wrong" from "the text moved" or "the object is not the real function". Its
`ValueError` here means the latter. Worth an R15 look regardless of the pollution.

## RECOMMENDATION (not taken — this seat holds)

1. Locate the leak, do not patch the symptom: run the gate with `-p no:randomly`
   and `--tb=long`, and bisect the suite around the failing test
   (`pytest --lf` plus a widening prefix) to name the polluting module.
2. Re-shape the ordering control to compare the ordering of the actual calls
   rather than the position of a literal string.

Both are queued items, not interrupts (SELF-INTERRUPT DISCIPLINE) — but the
publish wedge is Rung-1 priority zero, so item 1 outranks product work while the
queue (25 markers, `wedge_since` 15:30:09) stays undrained.
