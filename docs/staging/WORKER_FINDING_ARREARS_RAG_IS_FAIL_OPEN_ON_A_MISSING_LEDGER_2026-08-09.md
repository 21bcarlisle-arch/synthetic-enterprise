# WORKER FINDING — the arrears RAG column reads GREEN when its data source is absent

**Date:** 2026-08-09
**Found by:** worker, during KNIFE pass 1 (`KNIFE1_reporting_cycle`) byte-identity verification
**Class:** R15 FAIL-OPEN (passes on missing/unreadable input)
**Status:** QUEUED — not fixed on sight (SELF-INTERRUPT DISCIPLINE; outside KNIFE1's `file_scope`)

## The finding

`saas/reporting/annual_report.py::_build_plausibility_rag_section` (the
`| Year | Complaint rate% | ... | Arrears rate% | A.Bench hi | A.RAG |` table)
sources its arrears numerator from a file on disk:

```python
_ledger_path = _PROJECT / "site" / "state" / "billing_ledger.json"
try:
    _ledger = _json.loads(_ledger_path.read_text())
    ...
except (FileNotFoundError, _json.JSONDecodeError):
    pass          # <-- _arrears_by_year stays {}
```

On a missing or malformed ledger, `_arrears_by_year` stays empty, so
`arrears_count` is 0 for every year. Because `n_active > 0` is still true, the
`else: arrears_rate = None` / `"n/a"` branch is NOT taken. The report instead
prints a confident, fully-populated column:

```
| 2016 | 6.09% | 6% | ~ | 0.0% | 8% | OK |
...
**Arrears:** 10 of 10 years GREEN (DESNZ I&C baseline <8% normal, <12% crisis).
```

**Absent data renders as a perfect compliance record.** The observed-correct
figures on the same input are 7.7%–46.2%, i.e. **2 of 10 years GREEN, 6 RED** —
close to the exact inverse of what the fail-open path prints.

## Evidence (observed, not inferred)

Both renders below are `generate_annual_report()` over the *same*
`docs/reports/run_output_latest.json`, differing only in whether `_PROJECT`
resolved to a directory containing `site/state/billing_ledger.json`:

| `_PROJECT` resolves to | Arrears column | Verdict line |
|---|---|---|
| real repo root (ledger present) | 7.7 / 21.4 / 20.0 / 29.4 / 11.1 / 33.3 / 15.4 / 30.8 / 46.2 / 0.0 | `2 of 10 years GREEN` |
| a directory with no ledger | `0.0%` ×10 | `10 of 10 years GREEN` |

The second row is not hypothetical — it is what the function actually produced
when handed a `_PROJECT` whose `site/state/billing_ledger.json` did not exist.

## Why it matters beyond the instance

1. **It is the R15 FAIL-OPEN pattern verbatim**: the checker passes when its
   input is unavailable. An unavailable check is a FAILED check, not a green one.
2. **The distinguishing value is `0.0%`, which is also a legitimate reading.**
   2025 genuinely renders `0.0%` with the ledger present. So the fail-open
   output is *indistinguishable by eye* from a real all-clear — there is no
   tell in the rendered artefact.
3. **`generate_annual_report()` is documented as pure and is not.** Its
   docstring calls it "a pure function over `extract_report_data()`'s result";
   it in fact reads repo-relative disk state via a `__file__`-derived
   `_PROJECT`. Any caller rendering from a saved JSON in a different working
   tree (a worktree, a fork, a CI checkout, a `/tmp` copy) silently gets the
   fail-open column. This is also a portability-debt hit: the renderer cannot
   be moved without dragging an implicit path dependency behind it.

## Suggested fix (not applied)

Distinguish *absent* from *zero* — the ledger's absence must reach the reader:

- On `FileNotFoundError` / `JSONDecodeError`, set a `ledger_available = False`
  flag; render the arrears cells as `n/a` and the verdict line as
  "arrears not assessed — billing ledger unavailable", never as GREEN.
- Add the R15 mutation proof the class requires: point the renderer at a tree
  with no ledger and assert the section does **not** contain `GREEN`/`OK`
  arrears cells. That test is what makes this control able to fail.
- Consider passing the ledger in as an argument (restoring actual purity)
  rather than reading `_PROJECT` inside the renderer.

## Scope note

Deliberately NOT fixed in KNIFE pass 1. That pass is a CYCLE problem with a
byte-identical-output wall; changing a rendered figure inside it would have
destroyed the very check that surfaced this. `annual_report.py` is in KNIFE1's
`file_scope` for import-plumbing only. This wants its own atom.

## Related

- Sibling finding from the same pass:
  `WORKER_FINDING_STALE_ORCHESTRATION_CARVE_OUT_2026-08-09.md`
- Class precedent: fail-open control patterns; a control that cannot fail is
  worse than none (R15).
