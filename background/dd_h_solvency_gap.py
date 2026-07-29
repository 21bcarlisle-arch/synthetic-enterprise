"""DD-H (atom DD_seasonal_cashflow_physics) -- the solvency belief-vs-truth GAP
organ, the HARNESS/close_to_learn sibling of the DD2/DD3 physics.

THE GAP, in one line. A supplier running level (fixed) direct debit collects
the same amount every month while its customers consume seasonally, so it sits
on a pile of held customer credit that peaks in autumn (DD2,
`simulation/dd_balance_book.py`). That held credit is *other people's money owed
back* -- a liability, not profit (DD3, `company/finance/double_entry.py`). The
company's NAIVE books (management_accounts) still count that cash inside equity,
so the company BELIEVES it is more solvent than it is. This organ measures that
blindness:

    BELIEF  = naive_total_equity_gbp   (equity treating held credit as own money)
    TRUTH   = true_total_equity_gbp    (equity net of held credit owed back)
    gap_gbp = BELIEF - TRUTH           (== the held customer credit)
    gap     = gap_gbp / BELIEF         (fraction of believed equity that is
                                        actually owed back; 0=none, >=1=the
                                        cash-rich-but-insolvent tell)

That belief-vs-truth gap IS the score (COUPLED_TRIAD doctrine: "the gap is the
score"). gap=0 means the company holds no seasonal credit and its books are
honest; 0<gap<1 is the honest steady state (some of believed equity is owed
back); gap>=1 means the held credit meets or exceeds believed equity -- the
company is cash-rich but balance-sheet-insolvent, and DD3's own
`cash_rich_but_insolvent` tell fires at exactly that boundary (true_equity<0).

THE WALL (CLAUDE.md Architectural Laws). This is HARNESS code, so it lives in
`background/` -- the ONLY layer permitted to hold the company's belief and the
adjusted truth side by side to compute a gap (COUPLED_TRIAD_DESIGN.md 1.3),
identical to `background/gap_metric.py` / `background/live_payment_triad.py`. It
is GAP-ONLY: it READS the already-published run output and WRITES only its own
gap ledger + the morning digest line. It NEVER writes a figure back into any
`company/` or `saas/` financial (the company never sees its own solvency score),
and it reads no SIM internals -- the naive/adjusted equities it consumes are
both company-observable book values (`saas/reporting/annual_report.py`
`_compute_dd3_held_credit_balance_sheet`, which names DD-H as its consumer).

R15 FAIL-CLOSED (both ways, the doctrine's three killer patterns):
  * FAIL-OPEN guard -- non-finite belief/truth/held-credit is REJECTED
    (`ValueError`), never coerced to zero (a zeroed input would read as
    "perfectly solvent", flattering).
  * FAIL-SILENT guard -- a missing/empty DD3 block yields an explicit
    `not-measurable` row, NEVER a fabricated gap=0 (absence is not solvency).
  * TAUTOLOGY guard -- the gap is computed from the belief AND the truth held
    separately and cross-checked (`belief - truth == held_credit`), rejecting a
    block where the held credit was silently zeroed while the two equities
    diverge; the score is not the restated held-credit figure alone.

DETERMINISM (C-S2). No wall-clock, no randomness. `measured_at` /
`run_git_commit` are passed IN by the caller (`record_gap`) -- this module never
calls a clock. `retro_gap_line` is a PURE read+format with no side effect.

SEVERANCE (mirrors daily_self_note §2). This module has NO path into the draw
and the draw never reads it: it is never imported by `supervisor.py` /
`find_work`, and no number it computes feeds priority, reward, selection, or
scheduling. R12: the gap is a DIAGNOSTIC, never a target -- it must never appear
in a fidelity/maturity/product-quality claim, only in the morning note and its
own history ledger.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping, Optional

PROJECT_DIR = Path(__file__).resolve().parent.parent
RUN_OUTPUT_PATH = PROJECT_DIR / "docs" / "reports" / "run_output_latest.json"
GAP_LEDGER_PATH = PROJECT_DIR / "docs" / "observability" / "dd_h_solvency_gap_ledger.json"

# Consistency tolerance for the tautology cross-check (belief - truth vs held
# credit). The DD3 view rounds each field to the penny, so up to ~1.5p of
# rounding is legitimate; anything larger means the block is internally
# inconsistent (a zeroed/mismatched field) and must not be scored.
_CONSISTENCY_EPS_GBP = 0.02


class SolvencyGapUnmeasurable(ValueError):
    """Raised when the DD3 view is present but internally inconsistent or
    carries a non-finite figure -- an R15 FAIL-CLOSED refusal to fabricate a
    gap from bad inputs, distinct from the honest 'block absent' case (which
    returns a not-measurable row, never raises)."""


def _finite(x: Any, name: str) -> float:
    """Coerce to float and REJECT non-finite (R15 FAIL-OPEN guard). Never
    silently maps NaN/inf/None to zero."""
    if x is None:
        raise SolvencyGapUnmeasurable(f"{name} is missing (None)")
    try:
        v = float(x)
    except (TypeError, ValueError) as e:
        raise SolvencyGapUnmeasurable(f"{name} is not a number: {x!r}") from e
    if not math.isfinite(v):
        raise SolvencyGapUnmeasurable(f"{name} is not finite: {v!r}")
    return v


def compute_solvency_gap(dd3_block: Mapping[str, Any]) -> dict[str, Any]:
    """Compute the belief-vs-truth solvency gap from a DD3
    `balance_sheet_with_held_credit` block.

    Reads the belief (`naive_total_equity_gbp`) and the truth
    (`true_total_equity_gbp`) SEPARATELY -- not the held-credit figure alone --
    and cross-checks their difference against `customer_credit_held_gbp`
    (TAUTOLOGY guard). Raises `SolvencyGapUnmeasurable` on non-finite or
    internally-inconsistent inputs (FAIL-CLOSED); the caller decides whether an
    ABSENT block is a not-measurable row.

    Returns a dict: belief_equity_gbp, truth_equity_gbp, held_credit_gbp,
    gap_gbp, gap_normalised (None when belief<=0, undefined-by-division but the
    raw gap and the tell are still reported), cash_rich_but_insolvent (recomputed
    here from the equities, NOT copied from the block -- independence), as_at_month.
    """
    belief = _finite(dd3_block.get("naive_total_equity_gbp"), "naive_total_equity_gbp")
    truth = _finite(dd3_block.get("true_total_equity_gbp"), "true_total_equity_gbp")
    held = _finite(dd3_block.get("customer_credit_held_gbp"), "customer_credit_held_gbp")

    if held < 0.0:
        # Held credit is a positive-balances-only aggregate (DD3 rejects a
        # negative net). A negative here means a corrupt block, not a liability.
        raise SolvencyGapUnmeasurable(f"held credit must be >= 0, got {held}")

    gap_gbp = belief - truth
    # TAUTOLOGY / consistency guard: the belief-truth difference IS the held
    # credit by construction (DD3 moves exactly the held credit from equity to
    # liability). If the block's own held-credit field disagrees, one of the
    # three was silently altered -- refuse to score rather than trust a derived
    # single figure.
    if abs(gap_gbp - held) > _CONSISTENCY_EPS_GBP:
        raise SolvencyGapUnmeasurable(
            f"inconsistent DD3 block: belief-truth={gap_gbp:.4f} but held_credit={held:.4f} "
            f"(diff {abs(gap_gbp - held):.4f} > {_CONSISTENCY_EPS_GBP})"
        )

    # Normalise by the BELIEF (what the company thinks it is worth): the fraction
    # of believed equity that is actually other people's money owed back. 0 =
    # honest, >=1 = the cash-rich-but-insolvent tell. Undefined when the company
    # already believes itself worthless/negative (belief<=0) -- report None and
    # lean on the raw gap + tell there rather than a divide-by-~zero artefact.
    gap_normalised: Optional[float]
    if belief > 0.0:
        gap_normalised = round(gap_gbp / belief, 6)
    else:
        gap_normalised = None

    # cash-rich-but-insolvent: believed solvent (belief>0) yet truly insolvent
    # (truth<0). Recomputed from the equities here (independence) -- never copied
    # from the block, so a flipped block flag cannot corrupt the organ.
    cash_rich_but_insolvent = (belief > 0.0) and (truth < 0.0)

    return {
        "belief_equity_gbp": round(belief, 2),
        "truth_equity_gbp": round(truth, 2),
        "held_credit_gbp": round(held, 2),
        "gap_gbp": round(gap_gbp, 2),
        "gap_normalised": gap_normalised,
        "cash_rich_but_insolvent": cash_rich_but_insolvent,
        "as_at_month": dd3_block.get("as_at_month") or dd3_block.get("peak_month"),
    }


def _extract_dd3_block(run_output: Mapping[str, Any]) -> Optional[dict[str, Any]]:
    """Locate the DD3 `dd3_held_credit_balance_sheet` block anywhere in the run
    output (it is nested under the report-data section). Returns None when the
    run carried no such block -- the honest 'not yet instrumented / no ledger
    events' case, distinct from a malformed block."""
    stack: list[Any] = [run_output]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            block = node.get("dd3_held_credit_balance_sheet")
            if isinstance(block, dict) and block:
                return block
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    return None


def measure_from_run_output(
    run_output_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Read the latest published run output and compute the solvency gap.

    Returns a row dict with `measurable: True` and the gap fields on success, or
    `measurable: False` + a `reason` when the DD3 block is absent/unreadable
    (FAIL-SILENT guard: an honest not-measurable row, never a fabricated gap=0).
    A malformed-but-present block propagates `SolvencyGapUnmeasurable` from
    `compute_solvency_gap` -- that is a defect to surface, not to swallow."""
    path = run_output_path or RUN_OUTPUT_PATH
    try:
        run_output = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return {"measurable": False, "reason": f"run output unreadable: {e}"}
    if not isinstance(run_output, dict):
        return {"measurable": False, "reason": "run output is not an object"}
    block = _extract_dd3_block(run_output)
    if block is None:
        return {
            "measurable": False,
            "reason": "no dd3_held_credit_balance_sheet block in latest run output "
            "(DD3 view absent -- no ledger events / balance book, or a pre-DD3 run)",
        }
    row = compute_solvency_gap(block)
    row["measurable"] = True
    return row


def retro_gap_line(run_output_path: Optional[Path] = None) -> str:
    """One-line solvency belief-vs-truth summary for the morning self-note. PURE
    (no side effect) and fail-closed: any read/parse/consistency error returns an
    honest RED string, never a fabricated number."""
    try:
        row = measure_from_run_output(run_output_path)
    except SolvencyGapUnmeasurable as e:
        return f"solvency belief-vs-truth gap NOT MEASURABLE (malformed DD3 view: {e})"
    except Exception as e:  # noqa: BLE001 -- fail-closed, honest RED line
        return f"solvency belief-vs-truth gap NOT MEASURABLE (read error: {e})"
    if not row.get("measurable"):
        return f"solvency belief-vs-truth gap: not yet measurable — {row.get('reason', 'unknown')}"
    gn = row["gap_normalised"]
    gn_txt = "n/a (believed equity <= 0)" if gn is None else f"{gn:.3f}"
    tell = " ⚠ CASH-RICH-BUT-INSOLVENT" if row["cash_rich_but_insolvent"] else ""
    month = row.get("as_at_month") or "peak"
    return (
        f"solvency belief-vs-truth gap (0=books honest, >=1=insolvent tell): {gn_txt} "
        f"— believed equity £{row['belief_equity_gbp']:,.0f} vs true £{row['truth_equity_gbp']:,.0f}, "
        f"held customer credit £{row['held_credit_gbp']:,.0f} owed back at {month}{tell}"
    )


def _load_ledger(ledger_path: Path) -> list[dict[str, Any]]:
    try:
        data = json.loads(ledger_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return data if isinstance(data, list) else []


def record_gap(
    *,
    measured_at: str,
    run_git_commit: Optional[str] = None,
    run_output_path: Optional[Path] = None,
    ledger_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Measure the current gap and APPEND a dated row to the history ledger, so a
    per-digest gap accumulates over time. Determinism (C-S2): the caller supplies
    `measured_at`/`run_git_commit`; this function never calls a clock. Returns the
    row it appended (measurable or not -- a not-measurable row is recorded too, so
    the honest absence is legible in history rather than a silent skip)."""
    lp = ledger_path or GAP_LEDGER_PATH
    row = measure_from_run_output(run_output_path)
    row["measured_at"] = measured_at
    row["run_git_commit"] = run_git_commit
    rows = _load_ledger(lp)
    rows.append(row)
    lp.parent.mkdir(parents=True, exist_ok=True)
    lp.write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")
    return row


def main() -> None:
    print(retro_gap_line())


if __name__ == "__main__":
    main()
