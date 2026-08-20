**Severity:** LATENT · **Lane:** H_harness

# The gate refuses with a 4000-character tail, and one SyntaxWarning fills all of it

Everything below is `observed-with-evidence` unless labelled `inferred` (R9).
MEASURED AT: HEAD `d7213b989`, during the EP6 pass-31 landing that became `7270fad07`.

## What happened

`tools/surgical_land.py::_land_once` refuses a red gate with
`"GATE RED on the resulting tree (rc={}).\n{}".format(rc, output[-4000:])` (line 714). The
tail is meant to be the diagnostic. On this landing it carried **zero diagnostic characters**.

`saas/reporting/annual_report.py:7952` contains `churn\_estimate` inside an f-string, which
emits `SyntaxWarning: "\_" is an invalid escape sequence` on every import. The census tests
under `tests/tools/test_wall_channel_census.py` build a temp checkout of HEAD per test, so the
module is re-imported many times and each import prints a **four-line** warning block to
stderr. Twelve such blocks were the last 4000 characters. The refusal I actually received was
30 lines: one `[surgical-land] REFUSED` header, 27 lines of the same warning, and the two
`[test-gate]` lines.

The information I needed existed and was thrown away one frame up:

- `run_gate` (line 515-533) returns `r.returncode, (r.stdout or "") + (r.stderr or "")` — the
  **full** output, including pytest's `-q` summary.
- The `[test-gate] 22 test file(s): ...` selection line and the five `FAILED
  tests/tools/test_wall_channel_census.py::...` lines were in `stdout`.
- pytest's summary reaches stdout; the SyntaxWarnings reach stderr. Concatenating them puts
  **stdout first**, so slicing the TAIL systematically keeps the noise and drops the verdict.
  That ordering is what makes this reproducible rather than unlucky.

Reconstructing the five failing test names cost one extra full gate cycle (~2 minutes of
pytest plus a tar extract), driven by hand through `surgical_land`'s own internals.

## Why this is a class, not an instance

The R10 reading: fixing `annual_report.py:7952` would make this landing legible and leave the
mechanism intact. The defect is not the warning — it is that **a refusal's diagnostic is
selected by position in a stream whose noise is unbounded and whose signal is bounded**. Any
future import-time warning in any module a selected test touches reproduces it exactly.

Note the shape (R15 doctrine): the control did its job — it correctly refused a genuinely red
tree. What failed is the control's *account of itself*. A control that cannot say why it fired
is one an operator learns to bypass, which is the failure mode `HOOK-BYPASS IS A WALL` exists
to prevent. That makes this a diagnostic-integrity defect, not a cosmetic one.

## What the fix has to do, stated so it can be falsified

Not "print more". `output[-4000:]` should become a **selection**, not a slice:

1. Prefer the lines that decide the verdict — `FAILED `/`ERROR `, pytest's
   `N failed, M passed` summary line, and the `[test-gate]` lines — over positional recency.
2. Keep a bounded tail as the fallback for a refusal with no recognisable verdict lines, so
   the change cannot fail-open into printing nothing.
3. R15: mutation-test it against a stream whose last 4000 characters are pure warning noise
   and whose `FAILED` lines sit 200 lines earlier. That fixture is exactly this incident and
   the current code fails it. A null control — a refusal whose tail *does* contain the verdict
   — must still print the verdict, or the fix is a rewrite of the noise rather than a
   selection of the signal.

## Second, separate observation, recorded not actioned

`tools/pre_commit_test_gate.py` is where EP6's channel-C and now channel-E conformance checks
are ARMED, but it is not in EP6's `file_scope` (which names
`company/interfaces/wall_protocol.py`, `tests/company/interfaces/test_wall_protocol.py`,
`tools/wall_channel_census.py`, `tests/tools/test_wall_channel_census.py`). A pathspec built
from `file_scope` therefore omits the arming and the atom's own R15 proofs fail on the
resulting tree — which is precisely what happened here, and cost the first gate cycle. This is
the same shape as
`WORKER_FINDING_AN_ATOMS_LANDABLE_SET_IS_FIVE_FILES_WIDER_THAN_ITS_FILE_SCOPE_2026-08-19.md`
and is left to that finding rather than duplicated into a fix here.
