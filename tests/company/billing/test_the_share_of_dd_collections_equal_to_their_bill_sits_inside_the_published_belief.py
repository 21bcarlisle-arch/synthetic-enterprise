"""N20, the book: no more of a run's direct debits collect exactly their bill than variable-DD
households can account for.

At least 70% of GB direct-debit households pay a level amount (derived lower bound,
docs/market_research/payments_and_direct_debit_2026-10-25.md, "What a level direct debit must be"),
so at most 30% of collections should equal the bill they settle. The 4669d77ddd book collected
96.3% at the bill. Row INV_DD_COLLECTIONS_EQUAL_TO_THE_BILL_WITHIN_THE_VARIABLE_DD_SHARE is the
blind statement of the same property; this is its one book-level leg, at the penny.

Keyed to the property, not to a book: a run that predates the level schedule (no
`level_dd_collections`) cannot show it, and says so rather than passing or failing on it.
"""
from pathlib import Path

import pytest

from tools.generate_billing_ledger import generate
from tools.run_output_store import as_plain_file, load_run_output, resolve_run_output

RUN = Path(__file__).resolve().parents[3] / "docs" / "reports" / "run_output_latest.json"
VARIABLE_DD_CEILING = 0.30  # 1 - the 0.70 derived lower bound on the level share, the page above


def share_equal_to_the_bill(ledger: dict) -> tuple[int, int]:
    """(successful DD collections equal to their invoice to the penny, all successful DD
    collections), over every account in a page ledger."""
    equal = n = 0
    for c in ledger["customers"].values():
        inv = {i["invoice_number"]: i for i in c.get("invoices", ())}
        for p in c.get("payments", ()):
            i = inv.get(p.get("invoice_number"))
            if p.get("method") != "direct_debit" or p.get("outcome") != "success" or i is None:
                continue
            n += 1
            equal += abs(p["amount_gbp"] - i["total_amount_gbp"]) < 0.005
    return equal, n


def test_the_share_of_dd_collections_equal_to_their_bill_is_at_most_the_variable_dd_share(tmp_path):
    if resolve_run_output(RUN) is None:
        pytest.fail(f"the run output is absent at {RUN} -- 'could not look' is not 'within'")
    if "level_dd_collections" not in load_run_output(RUN):
        pytest.xfail("cannot tell: the newest run predates the level DD schedule, so every DD it "
                     "holds was collected at its bill (96.3% on 4669d77ddd)")
    ledger = generate(as_plain_file(RUN, tmp_path), tmp_path / "ledger.json")
    equal, n = share_equal_to_the_bill(ledger)
    assert n, "no successful direct debit on the run: the leg was not exercised"
    assert equal / n <= VARIABLE_DD_CEILING, (equal, n, round(equal / n, 3))
