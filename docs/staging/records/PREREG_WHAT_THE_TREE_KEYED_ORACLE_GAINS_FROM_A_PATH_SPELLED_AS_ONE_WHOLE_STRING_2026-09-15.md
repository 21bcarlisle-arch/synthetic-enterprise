# PREREG — what the TREE-keyed oracle gains from a path spelled as ONE WHOLE STRING

**Written 2026-09-15 by the delivery seat, BEFORE the population was counted or the matcher
changed.** Lane 0, claim `the-tree-keyed-generated-oracle-is-blind-to-a-path-spelled-as-one-whole-string`.

The previous sequence was four frames on the WRITE-keyed oracle (helper +8, signature default +9,
instance attribute +1, named segment +4). This is the first one on the **tree-keyed** oracle, and it
was found in passing by the last of those: §6 of
`docs/staging/done/SEAT_FINDING_A_NAMED_PATH_SEGMENT_IS_THE_ONE_DOOR_BOTH_ORACLES_WERE_BLIND_TO_2026-09-15.md`.

---

## 1. The defect, stated so it can be wrong

`generated_artefacts()` matches a **(parent, child) segment pair**:

```python
for a, b in GENERATED_TREES:
    if a in parts and b in parts:
        found.update(f"{a}/{b}/{s}" for s in parts if s.endswith(ARTEFACT_SUFFIXES))
```

`parts` is the string constants of ONE assignment. So `PROJECT / "docs" / "observability" /
"canon_drift.json"` is seen and `DEFAULT_REPORT = "docs/observability/canon_drift.json"`
(`tools/canon_drift_check.py:111`) is not — the artefact sits squarely inside a `GENERATED_TREES`
member and the matcher cannot spell it.

## 2. What I am measuring

Over the same five `SCANNED_TREES`, every **string constant in an assignment** that starts with a
`GENERATED_TREES` prefix + `/` and ends in an `ARTEFACT_SUFFIXES` member. Call that set `WHOLE`.
The population of the defect is `WHOLE - generated_artefacts()`.

Secondarily, and only to record it rather than to act on it: the same scan over **every** string
constant, not only ones in an assignment, so the finding says what a wider scope would have swept
instead of leaving it as an unasked question.

## 3. The predictions

Each is marked HELD or FALSIFIED in the finding, beside the result, whichever way it goes.

| # | Prediction |
|---|---|
| Q1 | `WHOLE` has **14** members, accepting 5–30. |
| Q2 | `WHOLE - generated_artefacts()` — the actual population — is **9**, accepting 3–20. |
| Q3 | `docs/observability/canon_drift.json` is in that difference. (The one named live instance; if this fails the finding's premise is wrong.) |
| Q4 | **The GATE verdict does not move at all.** `gate_violations()` is byte-identical before and after, and more strongly: no widening of `generated_artefacts()` can ever move it, because `offends()` already returns True for every entry under a generated-tree PREFIX and every member the tree-keyed oracle can produce is under one. The membership test `s in generated` is **subsumed**. If that holds, the drawn item's stated consequence — "a file_scope entry that silently starves its atom" — is FALSE for the gate half, and the real consumer is the reconciler union. |
| Q5 | The union `origin_reconcile._split_generated` reads **moves**, by strictly FEWER than Q2, because `canon_drift.json` is already in the union via `written_artefacts` (the named-segment frame added it). I predict **≥2** paths that NEITHER oracle had. |
| Q6 | **0** of the additions need a `WRITTEN_BUT_NOT_REPRODUCIBLE`-shaped carve-out. Reason: that list exists for paths a module rewrites whose CONTENT no run reproduces, and its four live members under a scanned suffix are all outside the three generated trees. A path inside `site/data/` or `docs/observability/` is a photograph of a run by the definition of `GENERATED_TREES`. |
| Q7 | The all-constants scan of §2's second paragraph adds **≤3** further paths over the assignment-only scan. If it adds many more, the assignment scope is a real limit and not just the inherited technique, and that is the next door. |

## 4. What I will do with each answer

- **Q2 = 0** — the defect is a single instance already covered by the sibling oracle, the matcher
  is not changed, and the finding says so. That is a real outcome, not a failure.
- **Q4 FALSIFIED** — the gate DOES move, which would mean an atom's file_scope is being newly
  refused. Then the change is commit-blocking and the frozen debt list has to be re-measured
  against the wider set before it lands, because a freeze keyed to the narrow set would read STALE.
- **Q6 FALSIFIED** — each such path is carved out explicitly, with the reason beside it, exactly as
  the write-keyed oracle's list does.

## 5. The done condition

`generated_artefacts()` sees a whole-string path; a control that FAILS with the old matcher
restored (mutation-proven, not asserted); the union movement measured and recorded; and the finding
carries every prediction above with its verdict.
