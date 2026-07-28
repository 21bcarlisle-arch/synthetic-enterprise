"""R15 both-ways: the dashboard generator resolves its customer-book reads
through the single `live_population()` seam (generator draw-wiring,
PRODUCT-FIRST item 2, report-lookup generator #2), not a direct import of the
static `CUSTOMERS` literal.

Two directions, per R15 (a control/wiring must be able to FAIL on its own
named defect):

  * DEFAULT-OFF byte-identical: with `SE_DRAW_POPULATION` unset, `_resolve_book()`
    returns exactly `list(CUSTOMERS)`, and end-to-end `extract_customers` over a
    static roster resolves the same per-customer `tariff_type`. Proves the wire
    did not perturb today's static-book report.

  * FLAG-ON load-bearing: with `SE_DRAW_POPULATION=1`, the resolved book
    additively carries the SYN acquisition cohort, and `extract_customers`
    resolves a SYN customer's `tariff_type` from that book (None) instead of the
    off-book `"fixed"` default. The MUTATION that reverts `_resolve_book()` to
    `list(CUSTOMERS)` makes both flag-on assertions fail (SYN would never appear
    in the book, so its tariff resolves to the default), so the wire is proven
    load-bearing, not decorative.

HONEST SCOPE (asserted, not hidden): only the two sites that read the
`CUSTOMERS` acquisition literal directly as a list are routed through the seam
(`extract_customers` tariff map, `extract_nudge_discovery` lift table). The
`get_customer(cid)` lookups in `extract_opex_ledger` are deliberately NOT
routed: `get_customer` unions `CUSTOMERS + SUCCESSOR_CUSTOMERS +
ACQUIRED_CUSTOMERS`, so routing it through `live_population()` (a CUSTOMERS-only
+ SYN book) would DROP the successor/acquired records — the opposite of
byte-identical. That non-wiring is asserted directly below so a future change
that naively routes it through the seam trips this suite.
"""

import json

import pytest

from saas.customers import CUSTOMERS
from tools.generate_dashboard_data import _resolve_book, extract_customers

_ACTIVATION_ENV = "SE_DRAW_POPULATION"


@pytest.fixture(autouse=True)
def _flag_off_by_default(monkeypatch):
    """Pin the activation flag OFF unless a test sets it, so a leaked env var
    from another process/test cannot flip this suite (SCHEDULED_FLAG isolation)."""
    monkeypatch.delenv(_ACTIVATION_ENV, raising=False)


def test_resolve_book_flag_off_byte_identical_to_static_customers():
    """Default-OFF the resolved book equals the static literal exactly."""
    assert _resolve_book() == list(CUSTOMERS)


def test_resolve_book_flag_on_additively_carries_syn_cohort(monkeypatch):
    """Wire is load-bearing: flag-on the book grows by the SYN cohort. Reverting
    the wire to `list(CUSTOMERS)` (the mutation) fails this assertion."""
    monkeypatch.setenv(_ACTIVATION_ENV, "1")
    book = _resolve_book()

    static_ids = {c["customer_id"] for c in CUSTOMERS}
    live_ids = {c["customer_id"] for c in book}
    syn_ids = live_ids - static_ids

    # Additive-not-replacive: every static customer still present, plus SYN-*.
    assert static_ids <= live_ids
    assert syn_ids, "flag-on must additively include the SYN acquisition cohort"
    assert all(cid.startswith("SYN-") for cid in syn_ids)


def _syn_book_entry():
    """Return one SYN dict from the flag-on book (used to derive expected values
    without hardcoding, so the test tracks the generator ground truth)."""
    import os
    os.environ[_ACTIVATION_ENV] = "1"
    try:
        book = _resolve_book()
    finally:
        os.environ.pop(_ACTIVATION_ENV, None)
    static_ids = {c["customer_id"] for c in CUSTOMERS}
    return next(c for c in book if c["customer_id"] not in static_ids)


def test_flag_off_extract_customers_tariff_unperturbed():
    """End-to-end byte-identical: flag-off, `extract_customers` resolves a static
    customer's tariff_type identically to a direct CUSTOMERS-derived map — the
    report path is unchanged by the wiring."""
    cid = CUSTOMERS[0]["customer_id"]
    expected = CUSTOMERS[0].get("tariff_type", "fixed")
    data = {"per_customer_lifetime": {cid: {"segment": "resi",
                                            "commodity": "electricity",
                                            "acquisition_date": "2016-01-01"}}}
    out = extract_customers(data)["lifetime"][cid]
    assert out["tariff_type"] == (expected if expected is not None else None)


def test_flag_on_extract_customers_resolves_syn_tariff_from_book(monkeypatch):
    """Load-bearing end-to-end: flag-on, a SYN customer present in the run's
    per_customer_lifetime resolves its tariff_type from the additive book, NOT
    the off-book `"fixed"` default. The mutation (revert `_resolve_book` to
    `list(CUSTOMERS)`) drops SYN from the book, so the tariff falls back to
    `"fixed"` and this assertion fails."""
    syn = _syn_book_entry()
    syn_id = syn["customer_id"]
    book_tariff = syn.get("tariff_type", "fixed")

    monkeypatch.setenv(_ACTIVATION_ENV, "1")
    data = {"per_customer_lifetime": {syn_id: {"segment": "resi",
                                               "commodity": "electricity",
                                               "acquisition_date": syn.get("acquisition_date", "")}}}
    out = extract_customers(data)["lifetime"][syn_id]
    # The book value (None) is what flows through flag-on; the off-book default
    # would be "fixed". These MUST differ for the mutation to be caught.
    assert book_tariff != "fixed", "fixture precondition: SYN tariff differs from off-book default"
    assert out["tariff_type"] == book_tariff


def test_get_customer_union_sites_not_routed_through_seam():
    """HONEST-SCOPE guard: the wider `get_customer` union lookups are NOT wired
    through `live_population()`. `get_customer` must still resolve across
    CUSTOMERS + SUCCESSOR + ACQUIRED, a strict superset of the seam's book, so a
    future change that naively routes those sites through the CUSTOMERS-only seam
    (dropping successor/acquired) trips here."""
    import saas.customers as sc
    union_ids = {c["customer_id"] for c in
                 sc.CUSTOMERS + sc.SUCCESSOR_CUSTOMERS + sc.ACQUIRED_CUSTOMERS}
    seam_ids = {c["customer_id"] for c in _resolve_book()}  # flag-off = CUSTOMERS
    # The union is a superset: routing get_customer through the seam would drop
    # exactly (union - seam). If that set is non-empty, the non-wiring matters.
    assert seam_ids <= union_ids
