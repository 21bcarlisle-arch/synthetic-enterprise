"""D6 ORACLE — put the ageing criterion on trial.

Runs KNOWN-GOOD and KNOWN-BAD ageing beliefs through the UNCHANGED criterion
(`background.gap_metric.misapplication_gap`, called exactly as
`tools.couple_w2_11_d5.score_triad` calls it for the ageing dimension). Each
row's correct answer is known INDEPENDENTLY of the metric, so a disagreement
convicts the metric rather than the company.

Findings and their consequence: docs/design/D6_PAYMENT_AGEING_GAP_VALIDITY_DISCOVER.md
Pinned as characterization tests: tests/tools/test_d6_ageing_metric_shape.py

    PYTHONPATH=. python3 tools/d6_ageing_metric_oracle.py

Read-only: no disk writes, no clock, no RNG.
"""
from __future__ import annotations

from typing import List, Sequence, Tuple

from background.gap_metric import misapplication_gap

N_CURRENT = 1000
N_OVERDUE = 10
N_FALSE_POSITIVES = 15


def labels(n_current: int, n_overdue: int) -> List[str]:
    """Truth: `n_current` settled invoices + `n_overdue` genuinely 90+ invoices."""
    return ["current"] * n_current + ["90+"] * n_overdue


def belief_finds_all_arrears(n_current: int, n_overdue: int,
                             n_false_positives: int = N_FALSE_POSITIVES) -> List[str]:
    """A GOOD company: every real arrears case found, plus a small false-positive
    rate on the (much larger) settled population."""
    return (["90+"] * n_false_positives
            + ["current"] * (n_current - n_false_positives)
            + ["90+"] * n_overdue)


def oracle_rows() -> List[Tuple[str, Sequence[str], Sequence[str], str]]:
    """(name, truth, belief, what-is-true-independently-of-the-metric)."""
    truth = labels(N_CURRENT, N_OVERDUE)
    rows: List[Tuple[str, Sequence[str], Sequence[str], str]] = [
        ("A perfect ageing (0 miss, 0 false positive)",
         truth, list(truth), "best possible -> 0"),
        ("B no-skill baseline (call everything current)",
         truth, ["current"] * (N_CURRENT + N_OVERDUE), "the baseline -> exactly 1"),
        ("C finds ALL arrears, 1.5% false-positive rate",
         truth, belief_finds_all_arrears(N_CURRENT, N_OVERDUE),
         "STRICTLY BETTER than B (B misses every one)"),
        ("E off by ONE bucket on every overdue invoice",
         truth, ["current"] * N_CURRENT + ["60-90"] * N_OVERDUE,
         "much better than B"),
        ("E' totally blind on every overdue invoice",
         truth, ["current"] * (N_CURRENT + N_OVERDUE), "= B"),
    ]
    # D: company behaviour held LITERALLY FIXED, only the world's arrears
    # prevalence moves. A company-fidelity measure must not move here.
    for n_over in (5, 10, 20, 50, 100):
        rows.append((
            f"D company FIXED, arrears prevalence {n_over / (N_CURRENT + n_over):.2%}",
            labels(N_CURRENT, n_over),
            belief_finds_all_arrears(N_CURRENT, n_over),
            "identical company -> gap must not move",
        ))
    return rows


def main() -> None:
    print("D6 ORACLE -- background.gap_metric.misapplication_gap, unchanged\n")
    for name, truth, belief, expected in oracle_rows():
        g = misapplication_gap(list(truth), list(belief))
        n_overdue = sum(1 for t in truth if t != "current")
        print(f"{name:<52} n={g.components['n']:5d} truly_overdue={n_overdue:4d} "
              f"n_wrong={g.components['n_wrong']:4d} GAP={g.gap:7.4f}   "
              f"[independently: {expected}]")


if __name__ == "__main__":
    main()
