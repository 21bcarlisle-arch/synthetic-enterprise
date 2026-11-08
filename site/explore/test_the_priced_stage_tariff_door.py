"""The household page's Priced stage prints the tariff of the bill it reads, not the account's name.

Eighth cold read, N16 on the six-stage page (O33, O34): PROS-2016-0187 and SYN-2016-185 are billed
on fixed terms, and their pages printed "Tariff: Standard Variable (Electricity)" under "What the
supplier committed to". The name came from the account, and every account got the same one.
d14ff599e fixed the Explore cast. This is the same class on the page the cast links to.

This drives the page's own `stagePriced()` over every page in the book. It grades the printed
Tariff against `term_tariff_type` on the bill the panel says it read, so it does not trust the
generator's own label. Row: INV_HOUSEHOLD_PAGE_TARIFF_IS_THE_BILLED_TERM.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_the_committed_price_is_the_tariffs_not_one_bills import DATA, FROM, _render  # noqa: E402

_ROW = re.compile(r"<td>Tariff</td><td class=\"n\">([^<]*)</td>")
_KIND = {"fixed": "Fixed", "svt": "Standard Variable", "deemed": "Deemed", "flex": "Flexible",
         "pass_through": "Pass-through"}


def grade(page: dict, rendered: dict) -> tuple[str, str]:
    """('pass' | 'breach' | 'ungraded', why) for the Tariff row of one page's Priced panel."""
    row, read = _ROW.search(rendered["html"]), FROM.search(re.sub(r"<[^>]+>", " ", rendered["html"]))
    if not row or not read:
        return "ungraded", "no Tariff row or no bill named"
    bills = [i for i, d in zip(page.get("invoices") or (), rendered["dates"]) if d == read.group(1)]
    if not bills:
        return "ungraded", "the named bill is not on the page"
    term = bills[0].get("term_tariff_type")
    printed = row.group(1).strip()
    if term is None:
        return ("pass", "") if printed.startswith("Not recorded") else ("breach", f"{printed!r} on an unrecorded term")
    if not printed.startswith(_KIND[term]):
        return "breach", f"{printed!r} on a {term} bill"
    if f"({page.get('commodity', '').capitalize()})" not in printed:
        return "breach", f"{printed!r} on a {page.get('commodity')} page"
    return "pass", ""


def _page(term: str | None, label: str | None) -> dict:
    bill = {"date": "2016-06-30", "period_start": "2016-06-01", "period_end": "2016-06-30", "commodity": "electricity",
            "consumption_kwh": 100.0, "unit_rate_p_per_kwh": 6.0, "commodity_amount_gbp": 6.0,
            "standing_charge_gbp": 5.8, "days_in_period": 30, "standing_charge_gbp_per_day": 0.194,
            "non_commodity_amount_gbp": 5.0, "vat_gbp": 0.84, "amount_gbp": 17.64, "status": "PAID",
            "term_tariff_type": term, "tariff_name": label}
    return {"account_id": "T-1", "commodity": "electricity", "acquisition_date": "2016-06-01",
            "tariff_name": "Standard Variable (Electricity)", "invoices": [bill]}


def test_the_grader_reaches_every_outcome(tmp_path):
    """The account-level name the page used to print is a breach on a fixed bill; the bill's own label
    passes; a page with no bills is ungraded."""
    fixed, svt, none = _page("fixed", "Fixed (Electricity)"), _page("svt", "Standard Variable (Electricity)"), _page(None, None)
    old = _page("fixed", None)
    predates = _page("fixed", None)
    del predates["invoices"][0]["tariff_name"]
    rendered = _render([fixed, svt, none, old, {"account_id": "T-2", "invoices": []}, predates], tmp_path)
    assert [grade(p, r)[0] for p, r in zip([fixed, svt, none, old], rendered)] == ["pass", "pass", "pass", "breach"]
    assert grade({"account_id": "T-2", "invoices": []}, rendered[4])[0] == "ungraded"
    # A feed built before the generator wrote the field keeps the account's name, and that IS N16: still a breach.
    assert _ROW.search(rendered[5]["html"]).group(1) == "Standard Variable (Electricity)"
    assert grade(predates, rendered[5])[0] == "breach"


def test_every_page_prints_the_term_of_the_bill_it_reads(tmp_path):
    pages_dir = DATA / "customers"
    if not pages_dir.is_dir():
        pytest.skip(f"no per-customer pages at {pages_dir}")
    pages = [d for f in sorted(pages_dir.glob("*.json")) for d in [json.loads(f.read_text())]
             if isinstance(d, dict) and d.get("invoices")]
    assert len(pages) > 100, "the book read is too small to say anything"
    if not any("tariff_name" in i for p in pages for i in p["invoices"]):
        pytest.skip("the committed feed predates per-bill tariff_name (tools/generate_invoice_data.py writes it on "
                    "every bill), so the page still prints the account's name and N16 stays live until the next publish")
    verdicts = [(p["account_id"], *grade(p, r)) for p, r in zip(pages, _render(pages, tmp_path))]
    breaches = [v for v in verdicts if v[1] == "breach"]
    print(f"INV_HOUSEHOLD_PAGE_TARIFF pages={len(verdicts)} pass={sum(v[1] == 'pass' for v in verdicts)} "
          f"breach={len(breaches)} ungraded={sum(v[1] == 'ungraded' for v in verdicts)}")
    assert not breaches, f"{len(breaches)} of {len(verdicts)} pages: {breaches[:5]}"
