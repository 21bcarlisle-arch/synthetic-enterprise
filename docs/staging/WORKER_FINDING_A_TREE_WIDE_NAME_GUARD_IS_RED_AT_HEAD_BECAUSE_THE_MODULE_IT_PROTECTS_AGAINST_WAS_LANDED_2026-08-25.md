**Severity:** LATENT · **Lane:** H_harness · **Rank:** after the pricing thread

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
