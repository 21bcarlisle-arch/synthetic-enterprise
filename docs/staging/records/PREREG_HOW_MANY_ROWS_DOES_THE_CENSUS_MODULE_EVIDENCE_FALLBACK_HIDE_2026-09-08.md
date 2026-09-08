**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# PREREG — how many rows does the census's module-evidence fallback hide?

A census whose dismissal rule is fail-open in one direction reports a clean tree it has not looked
at. The floor it freezes is then a floor over the population it can see. Answered by
`SEAT_RESULT_THE_CENSUS_DISMISSAL_RULE_WAS_FAIL_OPEN_AND_THE_SCOPE_IS_NOW_THE_WHOLE_CLASS_2026-09-08.md`.

**Written 2026-09-08, BEFORE the measurement, by the delivery seat working
`substring-scan-census-tools-and-background-population`.**

---

## What prompted it

The drawn work was to read the ~30 rows `tools/substring_source_scan_census.py --scope tools
background` returns and route or dismiss each. The census's own docstring (line ~110) names the two
rows "worth a reader first": `tools/canon_drift_check.py` and `tools/capability_index.py`.

**Neither is in the output.** Both read Python source and match it by substring:

* `canon_drift_check.probe_text_in_file()` — `phrase in text` where `text = _normalise(
  path.read_text(...))` and the path comes from `spec["file"]`, a value out of
  `docs/design/canon_claims.yaml`;
* `canon_drift_check.evaluate()` — `_normalise(claim.anchor) not in _normalise(page.read_text(...))`;
* `capability_index._wire_edges()` — reads each test file and hands the text to
  `_path_references()`, which regex-matches it.

So the docstring's own worked example is a claim the census refutes, and the question is which of the
two is wrong.

## The two candidate causes, established by reading before any counting

**(A) THE MODULE-EVIDENCE FALLBACK IS FAIL-OPEN.** `census()` does
`evidence = _path_evidence(scope) or module_evidence`. The docstring's rule 3 and its FAIL-CLOSED
paragraph both say a scan whose path evidence is ABSENT is `unknown` and counts as a member. The
fallback contradicts that: a scope with no evidence of its own inherits the module's, and the module
of `canon_drift_check.py` carries `docs/design/canon_claims.yaml` and
`docs/observability/canon_drift.json` — so `_subject_of` returns `non-python` and both scans are
dismissed. The fallback was added to fix the OPPOSITE defect (concatenating scope and module evidence
made a `site/*.html` test report as a Python scan). Fixing a false positive introduced a false
negative, and only the false positive got a comment.

This matters beyond the spelling: `probe_text_in_file`'s subject is named in a YAML register, not in
the code, so no evidence a source-level census can gather will ever say what it reads. `unknown` is
the correct verdict and the fallback is what takes it away.

**(B) TAINT DOES NOT CROSS A CALL BOUNDARY.** `_tainted_names` is per-scope and grows only from
assignments. `capability_index._wire_edges` reads the file; `_path_references(text, ...)` does the
matching with `text` as a PARAMETER. Neither scope is a member on its own — the reader has no
`read_text`, the reader-of-file has no match — so a scanner split across two functions is invisible
to the census however plainly it scans. `_root_parameter` already concedes this shape exists for
paths; nothing does the equivalent for text.

## Predictions, recorded before running anything

Fix (A) only — drop the fallback, so an empty scope evidence yields `unknown`:

1. `tests/` grows **between 5 and 25 new rows** over the frozen 117. Point estimate **12**.
2. `tools background` grows **between 3 and 15**. Point estimate **7**.
3. `canon_drift_check.probe_text_in_file` and `canon_drift_check.evaluate` are both among the new
   `tools` rows. **This one is near-certain and is not the interesting part of the prediction** —
   it is the worked example that motivated the fix, so it must appear or the diagnosis is wrong.
4. **No row is LOST.** The fallback can only ever narrow, so removing it is monotone. If any row
   disappears, prediction (A) is wrong about the mechanism and I stop and re-read.

Fix (B) is NOT measured in this turn and no count is predicted for it. It needs an interprocedural
rule, that is a bigger change than the disposition pass this claim was drawn for, and a census that
grows two ways at once cannot attribute either.

## What would refute the diagnosis

* (A) yields **zero** new rows anywhere — then the fallback is not reachable and I have misread
  `census()`.
* The counts move but `canon_drift_check` is still absent — then the dismissal is happening
  somewhere other than `_subject_of`, and prediction 3 was the control that caught me.
* A row is lost — see 4.

## What is NOT claimed

That every new row is a real member. The census is documented as allowed to be wrong towards
reporting, and `unknown` means "we did not manage to look", never "this scans Python". The rows are
a READING LIST, and the disposition pass this prereg sits inside is what turns them into a verdict.
