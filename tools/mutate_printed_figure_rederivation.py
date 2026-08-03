#!/usr/bin/env python3
"""R15 mutation proof for D_printed_figure_rederivation.

A control that cannot fail is worse than none. This applies REAL mutations to
the SOURCE (never to the tests) and asserts that each one makes its OWN named
test fail while the rest of the suite stays green -- so every control is shown
to be load-bearing and independent, not merely present.

Reading the code does not find a tautology; mutating it does. This project has
now recorded two cases of R15's TAUTOLOGY pattern appearing INSIDE a test
written against R15 (`min(x) == min(x)` in H_GAP, a chunk-width constant
checked against itself in W1_6b), both found only this way.

Restore is by in-memory content, never `git checkout` -- these sources include
an untracked file, and a checkout-based restore has silently wiped an edit here
before.

Usage: python3 -m tools.mutate_printed_figure_rederivation
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
MONEY = PROJECT / "saas" / "money.py"
INVARIANTS = PROJECT / "company" / "compliance" / "domain_invariants.py"
SUITE = "tests/company/compliance/test_printed_figure_rederivation.py"

# (name, file, old, new, the test that MUST fire)
MUTATIONS = [
    (
        "money: display floor drops below the real-bill 2dp convention",
        MONEY,
        "    min_dp: int = RATE_DISPLAY_MIN_DP,",
        "    min_dp: int = 1,",
        "test_the_display_floor_holds",
    ),
    (
        "money: rate accepted without checking it reproduces the amount",
        MONEY,
        "        if reproduced == amount_dec:\n            return float(rate), dp",
        "        if True:\n            return float(rate), dp",
        "test_the_industrial_line_that_no_2dp_rate_can_express_PASSES_when_printed_honestly",
    ),
    (
        "money: non-finite quantity guard removed (NaN-blind fail-open)",
        MONEY,
        '    if not isfinite(qty):\n        raise MoneyBoundaryError(\n            f"{field}: non-finite quantity {qty!r} cannot carry a printed rate"\n        )',
        "    if False:\n        pass",
        "test_the_rate_boundary_fails_CLOSED_on_non_finite",
    ),
    (
        "money: precision cap fails OPEN -- prints an unusable rate instead of none",
        MONEY,
        "            return float(rate), dp\n    return None",
        "            return float(rate), dp\n    return float(rate), dp",
        "test_a_line_needing_more_than_the_cap_returns_None",
    ),
    (
        "invariant: the re-derivation comparison always passes (fail-open)",
        INVARIANTS,
        "        return reproduced == amount.quantize(Decimal(\"0.01\"), rounding=ROUND_HALF_UP)",
        "        return True",
        "test_the_named_defect_FIRES",
    ),
    (
        "invariant: a rate with nothing to multiply passes (fail-open)",
        INVARIANTS,
        "        if quantity is None or amount is None:\n            return False  # fail closed: a rate with nothing to multiply",
        "        if quantity is None or amount is None:\n            return True",
        "test_a_rate_with_nothing_to_multiply_FAILS_CLOSED",
    ),
    (
        "invariant: printed-rate precision guard removed (float residue passes)",
        INVARIANTS,
        "        if -rate.as_tuple().exponent > _MAX_PRINTED_RATE_DP:\n            return False  # fail closed: unquantized float residue on the page",
        "        if False:\n            return False",
        "test_float_residue_on_a_printed_rate_FAILS_CLOSED",
    ),
    (
        "invariant: non-finite figures read as clean (NaN-blind fail-open)",
        INVARIANTS,
        "    if not isfinite(fval):\n        return None\n    return Decimal(str(fval))",
        "    if False:\n        return None\n    return Decimal(str(fval))",
        "test_non_finite_and_unreadable_figures_FAIL_CLOSED",
    ),
    (
        "invariant: per-register rows no longer checked (the rendered rows)",
        INVARIANTS,
        "    registers = inv.get(\"registers\")\n    if isinstance(registers, list):",
        "    registers = None\n    if isinstance(registers, list):",
        "test_a_register_row_that_does_not_rederive_FIRES",
    ),
]


def run_suite():
    """Return (failed_test_names, returncode)."""
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", SUITE, "-q", "--no-header", "-p", "no:randomly"],
        cwd=PROJECT, capture_output=True, text=True,
    )
    failed = set()
    for line in proc.stdout.splitlines():
        if line.startswith("FAILED "):
            failed.add(line.split()[1].split("::")[1].split("[")[0])
    return failed, proc.returncode


def main() -> int:
    originals = {p: p.read_text() for p in {MONEY, INVARIANTS}}

    baseline_failed, rc = run_suite()
    if rc != 0:
        print("BASELINE IS NOT GREEN -- cannot prove anything.", baseline_failed)
        return 1
    print("baseline: green\n")

    problems = []
    try:
        for name, path, old, new, expected in MUTATIONS:
            src = originals[path]
            if src.count(old) != 1:
                problems.append(f"{name}: anchor matched {src.count(old)} times, expected 1")
                print(f"  !! {name}: ANCHOR NOT UNIQUE -- mutation not applied")
                continue
            path.write_text(src.replace(old, new, 1))
            failed, rc = run_suite()
            path.write_text(src)  # restore immediately

            if rc == 0:
                problems.append(f"{name}: NOTHING FAILED -- the control cannot fire")
                print(f"  !! {name}\n     NOTHING FAILED")
                continue
            if expected not in failed:
                problems.append(f"{name}: expected {expected}, got {sorted(failed)}")
                print(f"  !! {name}\n     expected {expected}, got {sorted(failed)}")
                continue
            others = failed - {expected}
            marker = "" if not others else f"  (also, collaterally: {sorted(others)})"
            print(f"  ok  {name}\n      -> {expected} FIRED{marker}")
    finally:
        for p, src in originals.items():
            p.write_text(src)

    restored_failed, rc = run_suite()
    if rc != 0:
        problems.append(f"BASELINE NOT RESTORED: {sorted(restored_failed)}")
    print("\nbaseline restored:", "green" if rc == 0 else "RED")

    if problems:
        print("\nR15 NOT DISCHARGED:")
        for p in problems:
            print("  -", p)
        return 1
    print(f"\nR15 DISCHARGED: {len(MUTATIONS)} mutations, each fired its own named test.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
