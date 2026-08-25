**Severity:** RECORDED · **Lane:** H_harness · **Rank:** after the pricing thread

**Discharged:** `tests/company/core/test_commitment_actual_forecast.py` — the scan is scoped to the one module the control names, and the narrowing ships with its own falsifier: re-injecting each forbidden spelling into that module reds the guard, verified against the real file on disk and not only against an in-memory copy.

**Why LATENT and not BLOCKING, decided rather than defaulted.** BLOCKING means a control in the
area is untrustworthy. I cannot show that: the guard may be exactly right and `simulation/` in
genuine violation of a retired spelling — see the two readings below, which point opposite ways.
What is certain is that nothing published depends on the answer and no verdict on any figure
rests on it, which is LATENT's definition. Calling it BLOCKING would freeze H_harness level
raises on a control I have not shown to be wrong.

**Not fixed on sight, deliberately** (SELF_INTERRUPT_DISCIPLINE): the correct repair is either to
narrow another lane's control or to rename a published artefact key, and both are that lane's
call with EP1's history in front of them. Filed, not touched.

# `test_the_three_horizon_clv_name_does_not_return_to_this_module` is RED at HEAD, and it is red because a name it forbids tree-wide is now legitimately bound in `simulation/`

All claims `observed-with-evidence` unless marked.

## What is observed

    $ python3 -m pytest tests/company/core/test_commitment_actual_forecast.py \
        ::test_the_three_horizon_clv_name_does_not_return_to_this_module -q
    AssertionError: the three-horizon-CLV name is bound again as a symbol: ['three_horizon_clv']

Both files involved are CLEAN at HEAD (`git status --porcelain` empty for each), so this is not
one lane's uncommitted work reddening another's test. It is the committed tree.

The binding the guard found:

    simulation/run_phase4c_on_phase2b.py:512
        "three_horizon_clv": customer_value.three_horizon_clv.as_published_dict(),

`customer_value.three_horizon_clv` is an `ast.Attribute`, which is exactly what
`_bound_identifiers()` collects. The dict KEY beside it is a string literal and is not what
fires.

## Why the guard and the tree disagree

The control's own docstring scopes it to one module -- *"the three-horizon CLV name ... does not
return to THIS MODULE"* -- and its implementation scans **every `.py` in the working tree**
(`os.walk` from the repo root, 2,335 files). Those are different claims, and the tree only
started violating the wider one when `cbb2fd2d8` adopted and landed EP1's CLV work, which
publishes a field under precisely the forbidden spelling.

So there are two defensible readings and they lead to opposite repairs:

- the guard means what its docstring says, and its scope is too wide by accident. Repair: scope
  the scan to `company/core/commitment_actual_forecast.py`, and add the mutation (re-inject the
  name into that module) so the narrowed control is still proven to fire.
- the guard means what its code does -- the spelling `three_horizon_clv` is retired tree-wide in
  favour of EP1's `clv_three_horizon` -- and `simulation/` and `saas/reporting/annual_report.py`
  are still using the retired one. Repair: rename the attribute, which reaches a **published
  run-output key** that `annual_report._three_horizon_clv_section` reads, so it is an artefact
  contract change and not a rename.

`inferred`, not observed: that the first reading is the intended one. The docstring supports it
and the eight recorded collision passes do not obviously settle it.

## Why it has not stopped anything yet, and when it will

`pre_commit_test_gate` SELECTS tests by changed path. Five commits landed today over
`company/crm`, `company/pricing`, `simulation/` and `sim/` without ever selecting this file. The
first commit that touches `company/core/**` will select it and wedge, and the wedge will look
like that commit's fault.

## Evidence

- the pytest run above, at HEAD, both files clean.
- `tests/company/core/test_commitment_actual_forecast.py:411-458` -- `_SCAN_SKIP_DIRS` and
  `_bound_identifiers()`, `os.walk` from `_repo_root()`.
- `tests/company/core/test_commitment_actual_forecast.py:482` -- the forbidden set, assembled
  from fragments so the control's own source does not bind what it forbids.
- `git log -1 cbb2fd2d8` -- the EP1 landing that introduced the binding.
- `grep -rn three_horizon_clv --include=*.py .` -- 16 live bindings outside `.claude/`.

---

# 2026-08-25, resolved: reading one, and the tree settled it rather than the docstring

The finding above left two defensible readings and declined to pick. It was right to decline —
but the evidence that separates them was not the docstring, which is merely suggestive. It is
what the tree actually publishes.

## Which reading, and on what evidence

`three_horizon_clv` is not a retired spelling. It is EP1's LIVE, PUBLISHED one, at a different
level from the module name `clv_three_horizon.py`:

- `company/interfaces/customer_value.py:51` — the SEAM exports `build_three_horizon_clv_snapshots`.
- `company/analytics/customer_value_view.py:121` — the view's field is `three_horizon_clv: BookCLV`.
- `saas/reporting/annual_report.py:1700` — `_three_horizon_clv_section` renders a published run-output
  key of that exact name.
- `tools/couple_clv.py:250` — `EP1_BELIEF_FIELD = "three_horizon_clv_snapshots"`, the coupled-pair
  measurement's belief field.

Reading two would therefore have required renaming a published artefact key and the coupled-pair
belief field to satisfy a control — the inversion this project exists to avoid. And the guarded
module's own docstring says the name "now belongs unambiguously to `EP1_clv_three_horizon`", so
EP1 binding it is the rename WORKING, not failing. The tree-wide scan was asserting the undo of
the thing the control exists to protect.

## What was done

Scoped `_bound_identifiers()` to `company/core/commitment_actual_forecast.py` — the module the
control's name, docstring and assertion message all already claimed. No production code changed;
no published key moved.

**Nothing was lost by narrowing.** The retired PATH is held dead tree-wide by
`tests/company/analytics/test_clv_three_horizon.py::test_the_old_horizon_vocabulary_is_not_reintroduced_here`,
which greps the git index for `company/core/three_horizon_clv.py`. Path resurrection is that
control's job; name re-adoption inside this module is this one's. The two together cover what the
single over-wide scan was trying to cover alone.

## The anti-fail-open half had to be rebuilt, and that is the interesting part

The old floor was `_MIN_PY_FILES_SCANNED = 1800` — a corpus-collapse detector that only makes
sense for a tree walk. A one-file corpus cannot collapse by shrinking, so the FAIL-OPEN shape
arrives by a different route: the module is moved or renamed, `ast` yields nothing, and an empty
name set passes every membership test silently. Replaced with `_MUST_BE_BOUND` — the scan must
find `CommitmentActualForecastTracker` and `update_h3`, or the read did not happen — plus an
explicit unparseable/missing-file failure rather than a skip.

**Narrowing a control's scope is exactly the move that can leave it unable to fail**, which is why
the narrowing ships with its own mutation control rather than a claim.

## Evidence

- `test_the_name_guard_fires_when_the_name_is_re_injected_into_this_module` — each forbidden
  spelling injected separately, as a class definition and as an attribute read.
- Hand-verified against the REAL file, not only an in-memory copy: appending
  `class ThreeHorizonCLVTracker` to `company/core/commitment_actual_forecast.py` on disk reds
  `test_the_three_horizon_clv_name_does_not_return_to_this_module` (1 failed, 1 passed); file
  restored byte-identically, `git status --porcelain` clean.
- `python3 -m pytest tests/company/core/test_commitment_actual_forecast.py -q` — 50 passed,
  0.11s (was walking 2,335 files).
- 176 passed across `tests/company/core/`, the two CLV analytics suites, the customer-value seam
  and the annual-report CLV section.

## What this cost, and the general shape

Five commits landed today over `company/crm`, `company/pricing`, `simulation/` and `sim/` without
selecting this file, because `pre_commit_test_gate` selects by changed path. The first commit
touching `company/core/**` would have wedged and looked like that commit's fault. A control whose
SCOPE is wider than its CLAIM does not fail when it is wrong — it waits, and then fails against
whoever next walks past.
