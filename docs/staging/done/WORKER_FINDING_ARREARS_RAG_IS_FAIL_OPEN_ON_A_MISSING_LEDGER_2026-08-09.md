# WORKER FINDING — the arrears RAG column reads GREEN when its data source is absent

**Severity:** BLOCKING · **Lane:** C_customer_ops

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

---

## RESOLVED 2026-08-12 — closed as a CLASS, not an instance (R10)

**Status:** FIXED. Drawn by the scheduled tick as the lane's live BLOCKING finding.

### The census found three surfaces, not one

The finding named `annual_report.py`. Grepping the resource rather than the symptom
found the same `except: pass` around the same file on two more:

| Surface | Artefact | Fail-open output |
|---|---|---|
| `saas/reporting/annual_report.py::_section_population_anchoring` | `ANNUAL_REPORT.md` | `10 of 10 years GREEN` |
| `tools/generate_dashboard_data.py::extract_arrears_case_load` | `dashboard.json` | `status: "green"` |
| `tools/population_anchor.py::_arrears_check_by_year` | `population_anchoring.json` | `rag: "GREEN"` |

**And two live tests asserted the fail-open as correct behaviour** —
`test_no_ledger_file_returns_zero_cases` (`assert row["status"] == "green"`) and
`test_generate_handles_missing_billing_ledger` (`assert rag == "GREEN"`). The defect
was not merely unguarded; it was pinned. Both are now the mutation proof, with the
old assertion quoted in the docstring so the reversal is legible.

A third test, `test_zero_active_customers_gives_unknown_status`, wrote no ledger while
claiming to exercise the zero-denominator branch — it was travelling the missing-ledger
path and only appeared to pin the branch it names. Given a ledger, it now does.

### The mechanism

`saas/reporting/arrears_ledger.py` — one reader, returning an `ArrearsLedgerView`
that carries `available` as its own field. Callers branch on it; they cannot infer
availability from the emptiness of `arrears_by_year`, because the unavailable case and
the genuine no-arrears case are both empty. That indistinguishability is what made the
bug invisible (2025 legitimately renders 0.0%).

Closed failure modes: missing file, unreadable path, a directory where the file should
be, malformed JSON, a non-object payload, **and a parsed ledger carrying no customers**
— the last deliberately, since an empty ledger cannot source a numerator over a
non-zero active population any more than a missing file can, and treating it as
available would leave the same absurdity reachable through a second door.

Each surface now reports rather than swallows: the report prints
`arrears not assessed -- billing ledger unavailable` (NOT "0 of 10 years GREEN", which
reads as a measured bad result); the dashboard reports `status: "unavailable"`, kept
distinct from the pre-existing `"unknown"` (a *denominator* problem); the gate reports
`rag: "UNAVAILABLE"` plus `meta.arrears_ledger_available`.

### R15 — the controls fire on their own named defect

`tests/saas/test_arrears_ledger_unavailable_is_not_green.py`, 19 tests. Two mutations
run against it, both restored after:

- **Mutation 1** — `_unavailable()` returns `available=True` (the fail-open restored at
  the shared reader): **9 failures**, across all three surfaces plus the reader.
- **Mutation 2** — `_section_population_anchoring` stops branching on availability (the
  original defect, exactly): **1 failure**, precisely the report's own test.

The class guard has teeth in both directions: a vacuity guard asserts the three known
surfaces still match the class signature (so the guard cannot pass for the wrong
reason), and the four exempt files are re-checked every run against that signature, so
the allowlist cannot quietly absorb a real instance.

The class signature is structural, not a grep convenience: every surface in the class
reads the ledger **and** `active_customer_ids` — an arrears count over a population
denominator. Every surface outside it renders one named customer's own cases, where an
absent ledger yields an empty panel rather than a false all-clear. The first guard
written here keyed on "reads `arrears_history`" and caught four renderers that are not
in the class; that subject was wrong and was narrowed.

### No published figure moved

The ledger is present, so the live render is unchanged — verified against the real
`docs/reports/run_output_latest.json`:

```
| 2016 | 6.09% | 6% | ~ | 7.7% | 8% | OK |   ...   | 2024 | 5.08% | 6% | OK | 46.2% | 8% | ! |
**Arrears:** 2 of 10 years GREEN (DESNZ I&C baseline <8% normal, <12% crisis).
```

That is byte-for-byte the finding's own "observed-correct" column
(7.7 / 21.4 / 20.0 / 29.4 / 11.1 / 33.3 / 15.4 / 30.8 / 46.2 / 0.0, two GREEN).

### Also addressed from the finding's suggested fix

`_section_population_anchoring` now takes `ledger_path`, restoring the purity its
docstring always claimed. That is what makes the mutation expressible at all: the
renderer can be pointed at a tree without a ledger and be *seen* not to go green.

### Left open, deliberately

- **`overall_rag` in `population_anchoring.json` still ignores arrears entirely** — an
  UNAVAILABLE or RED arrears year does not move it. That is pre-existing and separate
  from this finding (arrears has always been advisory there); widening it silently
  inside a fail-open fix would be the accretion OPERATIONAL_LAYER_DESIGN forbids.
- A sibling defect found while here and QUEUED, not fixed on sight:
  `WORKER_FINDING_A_PUBLISHED_ARREARS_ROW_READS_A_KEY_THAT_IS_NOT_EMITTED_2026-08-12.md`
  — the shadow page renders `arrears_pct`, a key nothing emits, and has published
  `0.00%` for every year against real values of 30.8% and 46.2%.
