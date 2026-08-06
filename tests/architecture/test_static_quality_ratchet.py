"""Static-quality ratchets — ruff baseline + mypy baseline (STATIC tier).

WHY THIS EXISTS
---------------
`ruff check .` (the `lint` half of `make check`) currently reports ~2,421
pre-existing errors, so the lint step is a permanent red wall: it blocks the
whole `check` target, which means new lint sins land invisibly behind the
existing noise — nobody re-reads a 2,421-line failure. Separately, the repo has
no type checker AT ALL, so nothing measures type health or stops it decaying.

This module makes BOTH measurable and UN-REGRESSABLE without fixing a single
pre-existing error, using the same dated, shrink-only ratchet the project
already applies to the epistemic wall (see
tests/architecture/test_epistemic_wall_ratchet.py for the house idiom). Two
independent ratchets live here:

  * RUFF RATCHET — a dated baseline {rule_code: count} frozen from today's tree.
    A NEW rule code (count > 0, not in the baseline) fails. An EXISTING code
    whose count rises above its baseline fails (a regression). A code whose
    count FALLS below its baseline fails as STALE until the baseline is
    shrunk to match — so the baseline can only ratchet down, never silently
    absorb a fix without recording it.

  * MYPY RATCHET — the same three-way shape, keyed by module path
    {module_path: error_count}, over a deliberately PERMISSIVE mypy.ini (a
    FLOOR, not a purity crusade). New files must be type-clean (0 errors); an
    existing module may not regress past its frozen count; a module that
    improves must be re-frozen.

Neither ratchet fixes anything. They freeze the debt at today's level and make
every future delta visible and reviewable — exactly what the lint wall and the
absent type checker cannot do.

DETERMINISM / VERSIONING (READ BEFORE UPGRADING A TOOL)
-------------------------------------------------------
A lint/type baseline is only meaningful PER TOOL VERSION: ruff and mypy add,
rename, and re-scope rules between releases, so the same tree yields different
counts under different versions. The tool versions are therefore PINNED here
(RUFF_PIN / MYPY_PIN) and `test_tool_versions_are_pinned` fails loudly with a
one-line upgrade instruction on any drift. **Upgrading ruff or mypy means
re-freezing BOTH the pin and the affected baseline in the SAME PR** — never bump
one without the other. The mypy baseline also depends on mypy.ini (repo root);
changing that config invalidates the baseline the same way a version bump does.

mypy has a SECOND determinism hazard ruff does not: its error count for our code
changes with whether a third-party library is installed WITH type information
(numpy/pandas ship py.typed), because that makes mypy type-check every
expression and annotation touching it — errors that vanish when the library is
absent. To make the baseline a function of OUR code alone, `mypy_counts_for`
passes `--no-site-packages`, mypy's purpose-built flag for exactly this: it
stops mypy discovering installed PEP 561 packages, so every third-party import
resolves as missing -> `Any` (via ignore_missing_imports) whatever the ambient
env has installed, while typeshed's stdlib stubs (bundled inside mypy) and
first-party source are unaffected. Unlike a `--python-executable`-to-a-bare-venv
dodge, this does not leak an installed library's types back in through
first-party annotations. The baseline therefore holds WITH numpy/pandas
installed (verified) and without them. To reproduce the baseline by hand:

    mypy --config-file mypy.ini --no-site-packages \
        company saas sim simulation background tools

R15 (CONTROLS_THAT_CANNOT_FAIL) — every assertion below is paired with a
mutation proof: a synthetic violation (in-memory blast-radius tests) and a real
one written to a tmp tree and run through the actual tool, each proving the
control reds EXACTLY the new-violation assertion and nothing else (not the
stale-entry check, not the sibling ratchet).

Dependencies: pytest + the pinned ruff/mypy CLIs + Python stdlib only. No
project imports, so this suite runs even when the app's runtime deps are absent.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from functools import lru_cache
from importlib import metadata
from pathlib import Path

# --------------------------------------------------------------------------
# Pins, scope, and paths.
# --------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
MYPY_CONFIG = REPO_ROOT / "mypy.ini"
MAKEFILE = REPO_ROOT / "Makefile"

# Tool versions the baselines below are frozen against. A baseline is only valid
# for the exact version it was frozen under (see the module docstring).
RUFF_PIN = "0.16.1"
MYPY_PIN = "2.3.0"

# Date the baselines were frozen. Both baselines are shrink-only from here.
BASELINE_DATE = "2026-08-06"

# The mypy scope: the six behaviour-bearing source packages. tests/ is
# deliberately excluded (test files are not the product's type surface, and
# this very file lives there). Kept in sync with mypy.ini's coverage.
MYPY_SCOPE = ("company", "saas", "sim", "simulation", "background", "tools")


# --------------------------------------------------------------------------
# RUFF BASELINE — dated {rule_code: count}, frozen 2026-08-06.
#
# SHRINK-ONLY. To pay down debt: fix the violations, then LOWER the count here
# (or delete the entry when it hits 0). Never RAISE a count or ADD a code to
# silence the suite — a new/rising code is a real new lint sin; fix it instead.
#
# Top-10 offenders on the freeze date (also in the PR body):
#   I001 unsorted-imports .............. 1392
#   F401 unused-import .................  280
#   E402 module-import-not-at-top ......  194
#   F841 unused-variable ...............  130
#   E741 ambiguous-variable-name .......  108
#   F811 redefined-while-unused ........   95
#   E702 multiple-statements-semicolon .   76
#   E701 multiple-statements-colon .....   45
#   F541 f-string-missing-placeholders .   28
#   E401 multiple-imports-on-one-line ..   21
# `invalid-syntax` (1) is a Python-3.12-only f-string in
# company/trading/emir_reporting_register.py — the same file mypy.ini excludes.
# --------------------------------------------------------------------------
RUFF_BASELINE: dict[str, int] = {
    "I001": 1392,
    "F401": 280,
    "E402": 194,
    "F841": 130,
    "E741": 108,
    "F811": 95,
    "E702": 76,
    "E701": 45,
    "F541": 28,
    "E401": 21,
    "E731": 19,
    "W293": 19,
    "E722": 5,
    "W291": 3,
    "W292": 2,
    "E713": 1,
    "F601": 1,
    "W605": 1,
    "invalid-syntax": 1,
}
RUFF_BASELINE_TOTAL = 2421


# --------------------------------------------------------------------------
# MYPY BASELINE — dated {module_path: error_count}, frozen 2026-08-06 under the
# permissive mypy.ini via `mypy --no-site-packages` (third-party libs -> Any,
# so the census is identical whether or not numpy/pandas are installed).
# SHRINK-ONLY, same rules as the ruff baseline.
#
# Top-10 offending modules on the freeze date (also in the PR body):
#   simulation/run_phase2b.py .............. 94
#   background/weather_demand_triad.py ..... 46
#   background/weather_price_triad.py ...... 31
#   saas/reporting/annual_report.py ........ 25
#   company/crm/property_discovery.py ...... 16
#   background/flex_dispatch_triad.py ...... 13
#   background/harness_exit_criterion.py ... 13
#   background/daily_self_note.py .......... 11
#   company/regulatory/ico_breach_register.py 11
#   tools/couple_w2_11_d5.py ............... 11
# --------------------------------------------------------------------------
MYPY_BASELINE: dict[str, int] = {
    "simulation/run_phase2b.py": 94,
    "background/weather_demand_triad.py": 46,
    "background/weather_price_triad.py": 31,
    "saas/reporting/annual_report.py": 25,
    "company/crm/property_discovery.py": 16,
    "background/flex_dispatch_triad.py": 13,
    "background/harness_exit_criterion.py": 13,
    "background/daily_self_note.py": 11,
    "company/regulatory/ico_breach_register.py": 11,
    "tools/couple_w2_11_d5.py": 11,
    "tools/fabric_settlement_gap.py": 11,
    "simulation/life_events.py": 10,
    "company/billing/account_closure.py": 9,
    "company/regulatory/sar_register.py": 9,
    "company/regulatory/ebss_register.py": 8,
    "company/crm/energy_profile.py": 7,
    "background/fabric_gap_ledger.py": 6,
    "tools/couple_fabric.py": 6,
    "company/billing/ppm_debt_loading.py": 5,
    "company/market/market_share_estimator.py": 5,
    "company/regulatory/fuel_mix_disclosure.py": 5,
    "saas/customers.py": 5,
    "saas/reporting/css_statement.py": 5,
    "simulation/run_phase4c_on_phase2b.py": 5,
    "company/portal/app.py": 4,
    "company/risk/liquidity_stress_test.py": 4,
    "sim/market_index_history.py": 4,
    "simulation/arrears_engine.py": 4,
    "simulation/run_phase3b_recalibration.py": 4,
    "simulation/run_scenario.py": 4,
    "background/build_executor.py": 3,
    "background/fidelity_grid_scorer.py": 3,
    "background/interactive_session_probe.py": 3,
    "company/finance/double_entry.py": 3,
    "company/governance/approval_interface.py": 3,
    "simulation/renewals.py": 3,
    "simulation/run_phase0b.py": 3,
    "simulation/weather_inputs.py": 3,
    "tools/profile_test_suite.py": 3,
    "background/director_input_log.py": 2,
    "background/fork_reconciler.py": 2,
    "background/naive_organ.py": 2,
    "background/refresh_elexon_ssp_rolling.py": 2,
    "background/run_manifest.py": 2,
    "background/supervisor.py": 2,
    "company/analytics/churn_accuracy_report.py": 2,
    "company/billing/pre_bill_validation.py": 2,
    "company/comms/susceptibility_estimator.py": 2,
    "company/compliance/domain_invariants.py": 2,
    "company/crm/change_of_tenancy_register.py": 2,
    "company/finance/credit_limit_book.py": 2,
    "company/trading/hedge_decision.py": 2,
    "saas/property_model.py": 2,
    "simulation/fabric_demand_path.py": 2,
    "simulation/live_population.py": 2,
    "simulation/payment_seam_adapter.py": 2,
    "simulation/run_phase0c.py": 2,
    "simulation/run_phase1c_renewals.py": 2,
    "simulation/run_phase1d.py": 2,
    "simulation/run_phase2a_repriced.py": 2,
    "simulation/run_segments.py": 2,
    "tools/revenue_sanity_check.py": 2,
    "tools/select_impacted_tests.py": 2,
    "background/action_needed.py": 1,
    "background/autonomous_runner.py": 1,
    "background/bad_debt_reconciliation_run.py": 1,
    "background/fork_salvage.py": 1,
    "background/gate_authorization.py": 1,
    "background/ntfy_responder.py": 1,
    "background/schedule_reconciler.py": 1,
    "background/segmentation_testability_ledger.py": 1,
    "background/staging_disposition.py": 1,
    "background/staging_watcher.py": 1,
    "background/stop_control_audit.py": 1,
    "background/worker_seat.py": 1,
    "background/worker_tick.py": 1,
    "company/billing/payment_behaviour.py": 1,
    "company/billing/payment_ledger.py": 1,
    "company/billing/whd_register.py": 1,
    "company/compliance/green_claims_audit.py": 1,
    "company/crm/ancillary_products.py": 1,
    "company/crm/clv_calculator.py": 1,
    "company/crm/complaints.py": 1,
    "company/crm/credit_scoring.py": 1,
    "company/crm/decarb_recommender.py": 1,
    "company/crm/life_event_detector.py": 1,
    "company/crm/notification_prefs.py": 1,
    "company/crm/renewal_conversion.py": 1,
    "company/crm/renewals_book.py": 1,
    "company/crm/self_rationing_detector.py": 1,
    "company/crm/service_ticket.py": 1,
    "company/finance/credit_facility.py": 1,
    "company/finance/period_reconciliation.py": 1,
    "company/finance/working_capital.py": 1,
    "company/interfaces/sim_interface.py": 1,
    "company/market/bsuos_ledger.py": 1,
    "company/market/curve_monitor.py": 1,
    "company/market/flex_participation.py": 1,
    "company/market/gas_imbalance_ledger.py": 1,
    "company/market/hedge_performance.py": 1,
    "company/market/mop_appointment_register.py": 1,
    "company/pricing/ncc_forecast_register.py": 1,
    "company/pricing/renewal_pricing_engine.py": 1,
    "company/pricing/thermal_inference.py": 1,
    "company/pricing/tou_migration_scenario.py": 1,
    "company/pricing/weather_normalisation_belief.py": 1,
    "company/regulatory/capacity_market.py": 1,
    "company/regulatory/price_cap.py": 1,
    "company/risk/risk_appetite.py": 1,
    "company/sustainability/environmental_impact.py": 1,
    "company/trading/credit_limits.py": 1,
    "company/trading/risk_limits.py": 1,
    "sim/flex_dispatch.py": 1,
    "sim/scenario/spine.py": 1,
    "simulation/credit_refund_events.py": 1,
    "simulation/dd_collection_book.py": 1,
    "simulation/population_coverage.py": 1,
    "simulation/run_merit_order_reconstructibility.py": 1,
    "simulation/run_phase1c.py": 1,
    "simulation/run_phase1c_full_window.py": 1,
    "simulation/run_phase2a.py": 1,
    "simulation/run_phase3b_calibration.py": 1,
    "simulation/run_phase3b_regression.py": 1,
    "simulation/settlement_run_series.py": 1,
    "simulation/triad.py": 1,
    "tools/abolished_block_classes.py": 1,
    "tools/epistemic_verifier.py": 1,
    "tools/fetch_weather_data.py": 1,
    "tools/generate_director_data.py": 1,
    "tools/generate_evidence_data.py": 1,
    "tools/generate_fidelity_data.py": 1,
    "tools/generate_phases_json.py": 1,
    "tools/generate_test_mix_data.py": 1,
    "tools/merge_atom_status.py": 1,
    "tools/mutate_printed_figure_rederivation.py": 1,
    "tools/pre_commit_test_gate.py": 1,
    "tools/project_portfolio_to_2026.py": 1,
    "tools/site_lane_gate.py": 1,
    "tools/tenure_adoption_sensitivity.py": 1,
}
MYPY_BASELINE_TOTAL = 542


# --------------------------------------------------------------------------
# Generic ratchet arithmetic — shared by both ratchets, exercised by the
# R15 mutation tests. Pure functions over {key: count} maps.
# --------------------------------------------------------------------------

def keys_exceeding_baseline(
    baseline: dict[str, int], counts: dict[str, int]
) -> dict[str, tuple[int, int]]:
    """Baseline keys whose CURRENT count is above the frozen count (regression).

    Returns {key: (baseline_count, current_count)}.
    """
    return {
        k: (baseline[k], counts.get(k, 0))
        for k in baseline
        if counts.get(k, 0) > baseline[k]
    }


def new_keys(baseline: dict[str, int], counts: dict[str, int]) -> dict[str, int]:
    """Keys present now (count > 0) but ABSENT from the baseline.

    For ruff these are unknown new rule codes; for mypy they are new files that
    must be type-clean. Returns {key: current_count}.
    """
    return {k: v for k, v in counts.items() if v > 0 and k not in baseline}


def stale_keys(
    baseline: dict[str, int], counts: dict[str, int]
) -> dict[str, tuple[int, int]]:
    """Baseline keys whose CURRENT count is below the frozen count (stale).

    The debt was paid down but the baseline was not shrunk to match. Returns
    {key: (baseline_count, current_count)}; forces the ratchet to only shrink.
    """
    return {
        k: (baseline[k], counts.get(k, 0))
        for k in baseline
        if counts.get(k, 0) < baseline[k]
    }


def _merge(baseline: dict[str, int], delta: dict[str, int]) -> dict[str, int]:
    """baseline + delta, additively (used to simulate a landed violation)."""
    merged = dict(baseline)
    for k, v in delta.items():
        merged[k] = merged.get(k, 0) + v
    return merged


# --------------------------------------------------------------------------
# Makefile scope derivation — the ruff ratchet checks EXACTLY what `make check`
# lints. We read (never modify) the Makefile so the two cannot drift silently.
# --------------------------------------------------------------------------

def makefile_lint_scope() -> list[str]:
    """Positional paths passed to `ruff check` in the Makefile `lint:` target.

    Reads the recipe of the `lint:` target and extracts the arguments to
    `ruff check` that are not flags. Today that is exactly `.` (whole repo).
    """
    lines = MAKEFILE.read_text(encoding="utf-8").splitlines()
    recipe: list[str] = []
    in_lint = False
    for line in lines:
        if re.match(r"^lint:", line):
            in_lint = True
            continue
        if in_lint:
            if line.startswith("\t"):
                recipe.append(line.strip())
            else:
                break  # a blank line or the next target ends the recipe
    for cmd in recipe:
        m = re.match(r"ruff\s+check\s+(.*)$", cmd)
        if m:
            return [a for a in m.group(1).split() if not a.startswith("-")]
    raise AssertionError("could not find a `ruff check` command in Makefile lint target")


# --------------------------------------------------------------------------
# Running the tools programmatically.
# --------------------------------------------------------------------------

def _installed_version(dist: str) -> str:
    return metadata.version(dist)


def ruff_counts_for(paths: list[str], cwd: Path, extra_args: list[str] | None = None) -> dict[str, int]:
    """Run `ruff check <paths> --output-format=json` and count findings by code.

    Parameterised by cwd + paths so the R15 tmp-tree fixture can point it at a
    synthetic tree. Exit code 1 (findings present) is expected and fine; any
    other non-zero code is a real invocation error and raises.
    """
    cmd = [sys.executable, "-m", "ruff", "check", *paths, "--output-format=json"]
    if extra_args:
        cmd += extra_args
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    if proc.returncode not in (0, 1):
        raise RuntimeError(
            f"ruff invocation failed (exit {proc.returncode}):\n{proc.stderr}"
        )
    counts: dict[str, int] = {}
    for item in json.loads(proc.stdout or "[]"):
        # This pinned ruff emits code='invalid-syntax' for syntax errors; guard
        # a null code for forward-safety by mapping it to the same bucket.
        code = item.get("code") or "invalid-syntax"
        counts[code] = counts.get(code, 0) + 1
    return counts


_MYPY_ERROR_LINE = re.compile(r"^(?P<path>.+?\.py)(?::\d+)?: error:")


def mypy_counts_from_output(text: str) -> dict[str, int]:
    """Count mypy `error:` lines per source file (notes/summaries ignored)."""
    counts: dict[str, int] = {}
    for line in text.splitlines():
        m = _MYPY_ERROR_LINE.match(line)
        if m:
            path = m.group("path")
            counts[path] = counts.get(path, 0) + 1
    return counts


def mypy_counts_for(paths: list[str], cwd: Path, config: Path = MYPY_CONFIG) -> dict[str, int]:
    """Run mypy with the repo config over `paths` and count errors per module.

    Passes `--no-site-packages` so mypy never discovers installed PEP 561
    third-party packages (numpy, pandas, ...): every third-party import resolves
    as missing -> `Any` (via ignore_missing_imports), regardless of what the
    ambient environment has installed, while typeshed's stdlib stubs (bundled
    inside mypy) and first-party source are unaffected. That makes the per-module
    baseline a function of our code + the pinned mypy version + mypy.ini ALONE.
    A throwaway cache dir (cleaned up) keeps the repo clean and the run
    order-independent. Exit code 1 (errors found) is expected.
    """
    cache_dir = tempfile.mkdtemp(prefix="mypy-ratchet-cache-")
    try:
        cmd = [
            sys.executable, "-m", "mypy",
            "--config-file", str(config),
            "--no-site-packages",
            "--no-incremental",
            "--cache-dir", cache_dir,
            *paths,
        ]
        proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
        # mypy: 0 = clean, 1 = type errors found, 2 = fatal (bad config, crash).
        if proc.returncode not in (0, 1):
            raise RuntimeError(
                f"mypy invocation failed (exit {proc.returncode}):\n"
                f"{proc.stdout}\n{proc.stderr}"
            )
        return mypy_counts_from_output(proc.stdout)
    finally:
        shutil.rmtree(cache_dir, ignore_errors=True)


@lru_cache(maxsize=1)
def real_ruff_counts() -> dict[str, int]:
    return ruff_counts_for(makefile_lint_scope(), REPO_ROOT)


@lru_cache(maxsize=1)
def real_mypy_counts() -> dict[str, int]:
    return mypy_counts_for(list(MYPY_SCOPE), REPO_ROOT)


def _fmt_exceed(d: dict[str, tuple[int, int]]) -> str:
    return "\n".join(
        f"    {k}: baseline {b}, now {c}" for k, (b, c) in sorted(d.items())
    )


def _fmt_new(d: dict[str, int]) -> str:
    return "\n".join(f"    {k}: now {c}" for k, c in sorted(d.items()))


# ==========================================================================
# Version pins — the baselines are only valid for these exact versions.
# ==========================================================================

def test_tool_versions_are_pinned():
    """ruff and mypy must match the versions the baselines were frozen under.

    A version drift silently invalidates every count below, so it fails LOUDLY
    with the one-line fix.
    """
    ruff_v = _installed_version("ruff")
    mypy_v = _installed_version("mypy")
    assert ruff_v == RUFF_PIN, (
        f"ruff {ruff_v} installed but baselines frozen for {RUFF_PIN}. "
        f"FIX: `pip install ruff=={RUFF_PIN}` to reproduce, OR upgrade the pin "
        f"AND re-freeze RUFF_BASELINE in the SAME PR (a baseline is per-version)."
    )
    assert mypy_v == MYPY_PIN, (
        f"mypy {mypy_v} installed but baselines frozen for {MYPY_PIN}. "
        f"FIX: `pip install mypy=={MYPY_PIN}` to reproduce, OR upgrade the pin "
        f"AND re-freeze MYPY_BASELINE in the SAME PR (a baseline is per-version)."
    )


def test_mypy_config_present():
    """The permissive floor config the mypy baseline depends on must exist."""
    assert MYPY_CONFIG.is_file(), f"missing type-check floor config: {MYPY_CONFIG}"


def test_ruff_scope_is_the_make_check_scope():
    """The ratchet lints exactly what `make check` lints (today: the whole repo)."""
    scope = makefile_lint_scope()
    assert scope == ["."], (
        f"Makefile `lint:` scope changed to {scope!r}; the ruff baseline was "
        f"frozen over `ruff check .`. Re-derive and re-freeze RUFF_BASELINE."
    )


# ==========================================================================
# RUFF RATCHET — regression / new-code / stale, on today's tree.
# ==========================================================================

def test_ruff_no_rule_exceeds_baseline():
    """No known rule code may exceed its frozen count (a regression)."""
    exceed = keys_exceeding_baseline(RUFF_BASELINE, real_ruff_counts())
    assert not exceed, (
        "NEW ruff violations pushed a rule code ABOVE its dated baseline "
        f"(frozen {BASELINE_DATE}). Fix the new violations — do not raise the "
        "baseline:\n" + _fmt_exceed(exceed)
    )


def test_ruff_no_unknown_new_rule_codes():
    """A rule code absent from the baseline must be at 0 (no new sin class)."""
    new = new_keys(RUFF_BASELINE, real_ruff_counts())
    assert not new, (
        "NEW ruff rule code(s) not present in the dated baseline appeared. Fix "
        "the violations; add a code here only as a deliberate, reviewed "
        "grandfathering (it should shrink, not grow):\n" + _fmt_new(new)
    )


def test_ruff_no_stale_baseline_entries():
    """A baseline code whose count fell must be shrunk (shrink-only ratchet)."""
    stale = stale_keys(RUFF_BASELINE, real_ruff_counts())
    assert not stale, (
        "STALE ruff baseline entries — these codes have FEWER violations than "
        "frozen. Good news, but you must LOWER (or delete) their baseline counts "
        "so the ratchet holds the new floor:\n" + _fmt_exceed(stale)
    )


def test_ruff_baseline_matches_frozen_census():
    """On today's tree the ruff counts equal the frozen baseline exactly."""
    counts = real_ruff_counts()
    assert counts == RUFF_BASELINE, (
        "ruff census drifted from the frozen baseline. Diff:\n"
        f"  only-now : { {k: counts[k] for k in counts.keys() - RUFF_BASELINE.keys()} }\n"
        f"  only-base: { {k: RUFF_BASELINE[k] for k in RUFF_BASELINE.keys() - counts.keys()} }\n"
        f"  changed  : { {k: (RUFF_BASELINE[k], counts[k]) for k in RUFF_BASELINE.keys() & counts.keys() if RUFF_BASELINE[k] != counts[k]} }"
    )
    assert sum(counts.values()) == RUFF_BASELINE_TOTAL


# ==========================================================================
# MYPY RATCHET — regression / new-file / stale, on today's tree.
# ==========================================================================

def test_mypy_no_module_exceeds_baseline():
    """No baselined module may exceed its frozen error count (a regression)."""
    exceed = keys_exceeding_baseline(MYPY_BASELINE, real_mypy_counts())
    assert not exceed, (
        "mypy type errors ROSE above the dated baseline in these modules "
        f"(frozen {BASELINE_DATE}). Fix the new type errors — do not raise the "
        "baseline:\n" + _fmt_exceed(exceed)
    )


def test_mypy_new_files_are_type_clean():
    """A module absent from the baseline (a new file) must have 0 type errors."""
    new = new_keys(MYPY_BASELINE, real_mypy_counts())
    assert not new, (
        "NEW module(s) not in the mypy baseline carry type errors. New files "
        "must be type-clean under the permissive floor:\n" + _fmt_new(new)
    )


def test_mypy_no_stale_baseline_entries():
    """A module whose error count fell must be shrunk (shrink-only ratchet)."""
    stale = stale_keys(MYPY_BASELINE, real_mypy_counts())
    assert not stale, (
        "STALE mypy baseline entries — these modules have FEWER type errors than "
        "frozen. LOWER (or delete) their baseline counts to hold the new "
        "floor:\n" + _fmt_exceed(stale)
    )


def test_mypy_baseline_matches_frozen_census():
    """On today's tree the mypy counts equal the frozen baseline exactly."""
    counts = real_mypy_counts()
    assert counts == MYPY_BASELINE, (
        "mypy census drifted from the frozen baseline. Diff:\n"
        f"  only-now : { {k: counts[k] for k in counts.keys() - MYPY_BASELINE.keys()} }\n"
        f"  only-base: { {k: MYPY_BASELINE[k] for k in MYPY_BASELINE.keys() - counts.keys()} }\n"
        f"  changed  : { {k: (MYPY_BASELINE[k], counts[k]) for k in MYPY_BASELINE.keys() & counts.keys() if MYPY_BASELINE[k] != counts[k]} }"
    )
    assert sum(counts.values()) == MYPY_BASELINE_TOTAL


# ==========================================================================
# R15 MUTATION PROOFS — in-memory blast radius (a control must be able to FAIL).
#
# Each proof injects ONE synthetic delta and asserts it reds EXACTLY the
# intended check and NOTHING else — not the sibling checks, not the other
# ratchet. Without these, a check that always passes would look identical to
# one that works.
# ==========================================================================

# --- ruff: a brand-new rule code lands ---
def test_mutation_ruff_new_code_reds_only_new_check():
    mutated = _merge(RUFF_BASELINE, {"B008": 1})  # B008 not in select -> never natural
    assert new_keys(RUFF_BASELINE, mutated) == {"B008": 1}
    assert not keys_exceeding_baseline(RUFF_BASELINE, mutated)  # existing codes untouched
    assert not stale_keys(RUFF_BASELINE, mutated)               # adding never staleifies


# --- ruff: an existing code regresses above baseline ---
def test_mutation_ruff_regression_reds_only_exceeds_check():
    mutated = _merge(RUFF_BASELINE, {"F401": 1})  # 280 -> 281
    assert keys_exceeding_baseline(RUFF_BASELINE, mutated) == {"F401": (280, 281)}
    assert not new_keys(RUFF_BASELINE, mutated)
    assert not stale_keys(RUFF_BASELINE, mutated)


# --- ruff: a fixed code leaves a stale (un-shrunk) baseline entry ---
def test_mutation_ruff_stale_reds_only_stale_check():
    mutated = dict(RUFF_BASELINE)
    mutated["F401"] = 279  # one unused import removed but baseline not shrunk
    assert stale_keys(RUFF_BASELINE, mutated) == {"F401": (280, 279)}
    assert not keys_exceeding_baseline(RUFF_BASELINE, mutated)
    assert not new_keys(RUFF_BASELINE, mutated)


# --- mypy: mirror the three, keyed by module path ---
def test_mutation_mypy_new_file_reds_only_new_check():
    mutated = _merge(MYPY_BASELINE, {"company/brand_new_module.py": 1})
    assert new_keys(MYPY_BASELINE, mutated) == {"company/brand_new_module.py": 1}
    assert not keys_exceeding_baseline(MYPY_BASELINE, mutated)
    assert not stale_keys(MYPY_BASELINE, mutated)


def test_mutation_mypy_regression_reds_only_exceeds_check():
    mutated = _merge(MYPY_BASELINE, {"saas/customers.py": 1})  # 5 -> 6
    assert keys_exceeding_baseline(MYPY_BASELINE, mutated) == {"saas/customers.py": (5, 6)}
    assert not new_keys(MYPY_BASELINE, mutated)
    assert not stale_keys(MYPY_BASELINE, mutated)


def test_mutation_mypy_stale_reds_only_stale_check():
    mutated = dict(MYPY_BASELINE)
    mutated["saas/customers.py"] = 4  # improved but baseline not shrunk
    assert stale_keys(MYPY_BASELINE, mutated) == {"saas/customers.py": (5, 4)}
    assert not keys_exceeding_baseline(MYPY_BASELINE, mutated)
    assert not new_keys(MYPY_BASELINE, mutated)


# ==========================================================================
# R15 MUTATION PROOFS — on-disk (close the fail-open gap where the parser is
# correct but the TOOL never actually produced the finding). A synthetic
# violation is written to a tmp tree and run through the REAL tool; the parsed
# result must red EXACTLY the new-violation assertion and nothing else.
# ==========================================================================

def test_mutation_ruff_ondisk_violation_is_detected_and_reds_only_new_violation(tmp_path):
    """A real unused import in a tmp file -> ruff -> F401 -> reds only the
    regression assertion (F401 is a baselined code), never stale/new."""
    (tmp_path / "rogue.py").write_text("import os\n")  # unused import -> F401
    tmp_counts = ruff_counts_for(["rogue.py"], tmp_path)
    # 1) The real ruff CLI + our JSON parser actually surfaced the violation.
    assert tmp_counts.get("F401", 0) >= 1, (
        f"expected ruff to flag F401 on disk; got {tmp_counts}"
    )
    assert set(tmp_counts) == {"F401"}, f"tmp file should yield only F401, got {tmp_counts}"
    # 2) Landed on the real tree, it reds EXACTLY the exceeds-baseline check.
    mutated = _merge(RUFF_BASELINE, tmp_counts)
    assert keys_exceeding_baseline(RUFF_BASELINE, mutated) == {"F401": (280, 281)}
    assert not new_keys(RUFF_BASELINE, mutated)
    assert not stale_keys(RUFF_BASELINE, mutated)


def test_mutation_mypy_ondisk_type_error_is_detected_and_reds_only_new_violation(tmp_path):
    """A real type error in a tmp file -> mypy -> one error -> reds only the
    new-file assertion (a new module must be type-clean), never stale/exceeds."""
    module = tmp_path / "rogue.py"
    module.write_text("def f(x: int) -> str:\n    return x\n")  # int where str expected
    tmp_counts = mypy_counts_for(["rogue.py"], tmp_path)
    # 1) The real mypy CLI + our parser actually surfaced the type error.
    assert sum(tmp_counts.values()) >= 1, (
        f"expected mypy to flag a type error on disk; got {tmp_counts}"
    )
    assert set(tmp_counts) == {"rogue.py"}, f"only the tmp module should error, got {tmp_counts}"
    # 2) Landed on the real tree, it reds EXACTLY the new-file check (rogue.py is
    #    absent from the baseline).
    mutated = _merge(MYPY_BASELINE, tmp_counts)
    assert new_keys(MYPY_BASELINE, mutated) == {"rogue.py": tmp_counts["rogue.py"]}
    assert not keys_exceeding_baseline(MYPY_BASELINE, mutated)
    assert not stale_keys(MYPY_BASELINE, mutated)
