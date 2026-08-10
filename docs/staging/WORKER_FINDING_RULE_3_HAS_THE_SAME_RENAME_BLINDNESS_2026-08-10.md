# FINDING — the size ratchet's rule 3 has the same rename blindness rule 2b just lost

**Class:** fail-open (R15 killer pattern 2 — passes on missing state)
**Found:** 2026-08-10, KNIFE3 step 10, while fixing the *rule 2b* half of the same defect
**Disposition:** QUEUED (SELF_INTERRUPT_DISCIPLINE — the machine is not blocked)

## The defect

`tools/size_ratchet.py::evaluate` rule 3 (`RULE_TOUCHED_FILE_GREW`) is:

```python
if path in touched and path in head_lines and count > head_lines[path]:
```

`head_lines` is keyed by path at HEAD. A file that arrives via `git mv` is **not** in it, so the
`path in head_lines` clause is False and rule 3 **cannot fire on a renamed file** — the rule whose
whole purpose is that the ratchet *drains* debt instead of freezing it is silently switched off for
exactly the commits that move code around.

This is the identical blindness that step 10a fixed for rule 2b
(`WORKER_FINDING_A_PURE_RENAME_READS_AS_A_NEW_OVERSIZED_FUNCTION_2026-08-10.md`), in the opposite
direction: rule 2b was too STRICT on a rename (it minted every function as new), rule 3 is too LAX
(it waves the growth through). One map fixes both — `size_ratchet_gate.staged_renames()` already
exists and is already passed to `evaluate()`; rule 3 simply does not consult it.

## Declared, because this commit benefited from it

KNIFE3 step 10 renamed `simulation/run_segments.py` → `tools/run_segments.py` and grew it by 28
lines, then trimmed to +14. **Rule 3 did not fire on either.** The growth was caught only by rule 1,
and only because the frozen baseline key was carried across the rename by hand. Had the file been
comfortably under its baseline, a rename-plus-growth would have been invisible to the rule built to
catch growth.

Stating it here rather than leaving it in the warn log: a pass that benefits from a fail-open it
noticed and did not fix must say so, or the next reader reads silence as absence.

## The fix, when drawn

Resolve `head_lines` through the same rename map:

```python
prior = path if path in head_lines else renames.get(path, path)
if path in touched and prior in head_lines and count > head_lines[prior]:
```

**R15, both ways, and the vacuity guard is the interesting half:** the fires-test is a `git mv` plus
an appended line (must red); the clears-test is a pure `git mv` with zero content change (must stay
green — a rename is not growth). Mirror the pair already landed in
`tests/tools/test_size_ratchet_gate.py::test_a_pure_rename_does_not_mint_its_functions_as_new`.

## The class, stated once

**Any rule keyed on a path's state at HEAD is blind to a rename until it is told about the rename.**
`evaluate()` has four rules and a clone ceiling; rules 1 and 2 read `baseline["files"]` (a frozen
artefact, correctly independent of git's view and repaired by hand at each move), rule 2b is now
rename-aware, rule 3 is not. That is the whole census — no fourth case hiding.
