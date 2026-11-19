"""COUPLED-TRIAD runner for W2_36 (unbilled energy) <-> D48 (billing accuracy).

HARNESS code, outside the wall: it holds the world's true use beside the company's own figure.

WHAT THE GAP IS. Per account, BILLED-MINUS-USED energy in kWh over the account's whole book:
  - truth  t_a = sum of what its bills charged for (`total_consumption_kwh`) less the world's true
    use over the same periods (`meter_read_log[].true_consumption_kwh`, every period, actual reads
    included).
  - belief b_a = the company's own measure of the same thing, `-true_up_kwh` from
    `company.billing.billing_accuracy.account_billing_accuracy`: what its actual reads told it it
    had over- or under-billed. An open estimate run is not guessed (that module's rule), so it
    contributes 0 to the belief.
  - no-skill b0_a = s * estimated_kwh_a, where s is the book's mean billed-minus-used share per
    estimated kWh on the runs a read has closed. s is formed only from fields the company holds (its
    true-ups and its estimated bills), never from the graded truth.
  gap = mean|b - t| / mean|b0 - t|. 0 would be a supplier that knows its billing error exactly
  (a leak, for a wall-respecting pair), 1 one no better than the book-mean share.

WHAT IT CAN AND CANNOT SEE (measured on the af31e73fa7 book, 2026-11-08): on every closed run the
true-up equals the world's true-minus-billed to 1e-11, and on every actual-read bill billed equals
true use. So the whole gap is the open estimate runs and the runs closed on an estimated final bill
(K2's residual). Theft and meter faults (K4, K7) never reach this book's truth fields, and that
energy is invisible here, not absent.

W2_30 and W1_14 are paired with D48 too, but this number is the combined error of the household
shape, the weather and the estimator, so it is credited to neither. Their rows are written by
`tools/couple_d48_billing_gap.py`, which grades the shape and the weather apart; this runner never
touches them.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from background.gap_metric import (
    GAP_LEDGER_PATH,
    _normalise,
    _substream_seed,
    write_gap_entry,
)
from company.billing.billing_accuracy import account_billing_accuracy

PROJECT = Path(__file__).resolve().parent.parent
RUN_JSON = PROJECT / "docs" / "reports" / "run_output_latest.json"

WORLD_ATOM_ID = "W2_36_unbilled_energy_arises_the_way_it_does_in_reality"
TWIN_ATOM_ID = "D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used"
N_RESAMPLES = 2000


def account_errors(book: dict):
    """(rows, truth, belief, noskill, s) per account, from one run book."""
    bills = book["bills"]
    used = defaultdict(float)
    for r in book["meter_read_log"]:
        used[r["customer_id"]] += r["true_consumption_kwh"] or 0.0
    fuels = defaultdict(set)
    for b in bills:
        fuels[b["customer_id"]].add(b.get("commodity", "electricity"))
    mixed = [c for c, f in fuels.items() if len(f) > 1]
    if mixed:
        raise ValueError(f"accounts billing two fuels, kWh would be summed across them: {mixed[:5]}")
    rows = account_billing_accuracy(bills)
    closed_est = sum(r["estimated_kwh"] - r["open_estimated_kwh"]
                     - r["closed_on_estimated_final_kwh"] for r in rows)
    if closed_est <= 0:
        raise ValueError("no estimated kWh a read has closed: the no-skill share is undefined")
    s = -sum(r["true_up_kwh"] for r in rows) / closed_est
    truth = np.array([r["billed_kwh"] - used[r["account_id"]] for r in rows])
    belief = np.array([-r["true_up_kwh"] for r in rows])
    noskill = np.array([s * r["estimated_kwh"] for r in rows])
    return rows, truth, belief, noskill, s


def _ratio_ci(ec: np.ndarray, eb: np.ndarray, substream: str):
    rng = np.random.default_rng(_substream_seed(substream))
    n = ec.size
    samples = []
    for _ in range(N_RESAMPLES):
        idx = rng.integers(0, n, size=n)
        den = eb[idx].sum()
        if den > 0:
            samples.append(float(ec[idx].sum() / den))
    samples.sort()
    return [round(samples[int(0.025 * len(samples))], 4),
            round(samples[min(len(samples) - 1, int(0.975 * len(samples)))], 4)]


def _by_fuel(rows, ec: np.ndarray, eb: np.ndarray) -> dict:
    by_fuel = {}
    for fuel in ("electricity", "gas"):
        m = np.array([r["fuel"] == fuel for r in rows])
        if m.any():
            by_fuel[fuel] = {
                "n_accounts": int(m.sum()),
                "mae_company_kwh": round(float(ec[m].mean()), 2),
                "mae_noskill_kwh": round(float(eb[m].mean()), 2),
                "gap": round(float(ec[m].sum() / eb[m].sum()), 4) if eb[m].sum() else None,
                "gap_ci95": _ratio_ci(ec[m], eb[m], f"W2_36_D48_{fuel}"),
            }
    return by_fuel


def measure(book: dict):
    rows, truth, belief, noskill, s = account_errors(book)
    ec, eb = np.abs(belief - truth), np.abs(noskill - truth)
    use = float(sum(r["billed_kwh"] for r in rows) - truth.sum())
    by_fuel = _by_fuel(rows, ec, eb)
    open_kwh = sum(r["open_estimated_kwh"] for r in rows)
    final_kwh = sum(r["closed_on_estimated_final_kwh"] for r in rows)
    result = _normalise(
        float(ec.mean()), float(eb.mean()),
        (f"no-skill = every account assigned the book's mean billed-minus-used share per estimated "
         f"kWh on read-closed runs (s={s:.6f}, from the company's own true-ups and estimated bills, "
         f"never the graded truth) times its estimated kWh; MAE_noskill={eb.mean():.2f} kWh"),
        "prediction",
        components={
            "definition": ("per account, billed-minus-used kWh over its whole book: truth = billed "
                           "kWh less the world's true use over the same periods; belief = the "
                           "company's -true_up_kwh (billing_accuracy.account_billing_accuracy). "
                           "Gap = MAE(belief) / MAE(no-skill), in kWh, accounts unweighted."),
            "unit": "kWh per account (the ratio is dimensionless)",
            "n_accounts": len(rows),
            "n_accounts_with_estimated_bills": sum(r["estimated_bills"] > 0 for r in rows),
            "n_accounts_with_residual": int((ec > 0.01).sum()),
            "gap_ci95": _ratio_ci(ec, eb, "W2_36_D48_all"),
            "mae_company_kwh": round(float(ec.mean()), 2),
            "mae_noskill_kwh": round(float(eb.mean()), 2),
            "mae_company_share_of_use": round(float(ec.sum() / use), 5),
            "mae_noskill_share_of_use": round(float(eb.sum() / use), 5),
            "noskill_share_per_estimated_kwh": round(s, 6),
            "open_estimated_kwh": round(open_kwh, 1),
            "closed_on_estimated_final_kwh": round(final_kwh, 1),
            "by_fuel": by_fuel,
            "kinds_seen": "K2 residual: open estimate runs and runs closed on an estimated final",
            "kinds_not_seen": ("K4 meter faults and K7 theft: actual-read bills equal true use on "
                               "this book, so their energy never reaches the truth this reads"),
            "book_producing_commit": (book.get("producing_commit") or {}).get("commit"),
        },
        note=("how wrong the supplier is about its own billing: its read-measured billed-minus-used "
              "per account against the world's, normalised to a book-mean-share supplier. The "
              "whole residual is energy billed on estimates no actual read has yet corrected."),
    )
    return result


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book", default=str(RUN_JSON))
    ap.add_argument("--write-ledger", action="store_true")
    ap.add_argument("--ledger", default=str(GAP_LEDGER_PATH))
    args = ap.parse_args(argv)
    book = json.loads(Path(args.book).read_text(encoding="utf-8"))
    result = measure(book)
    c = result.components
    print(f"W2_36 <-> D48 on book {c['book_producing_commit']}: n={c['n_accounts']} "
          f"gap={result.gap:.4f} CI95={c['gap_ci95']} MAE {c['mae_company_kwh']} vs "
          f"{c['mae_noskill_kwh']} kWh; by fuel {json.dumps(c['by_fuel'])}")
    if args.write_ledger:
        measured_at = datetime.now(timezone.utc).isoformat()
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        # write_gap_entry merges one key and refuses a test process's write to the live ledger.
        write_gap_entry(WORLD_ATOM_ID, TWIN_ATOM_ID, result, measured_at=measured_at,
                        run_git_commit=commit, ledger_path=Path(args.ledger))
        print(f"ledger written: {WORLD_ATOM_ID}")


if __name__ == "__main__":
    main()
