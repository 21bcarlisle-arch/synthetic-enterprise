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
    # ACTIVATION 2026-08-13: unset now means ON (committed curriculum,
    # docs/design/curriculum/population_draw_activation.json). These OFF-path
    # invariants are unchanged -- they now STATE the state they test instead of
    # inheriting it from a default that the director has since moved.
    monkeypatch.setenv(_ACTIVATION_ENV, "0")
    # PB3 EXIT (b2), 2026-08-25: the same discipline for the OTHER flag, and the
    # reason is the change that made it necessary. `live_population()` used to
    # resolve the net-new campaign INSIDE its `draw_population_enabled()` branch,
    # so pinning the draw off pinned growth off with it and every assertion below
    # got `SE_GROW_BOOK` for free. The two flags are now independent -- (b2)
    # required it, because an arrival flag that also governs whether the company
    # can WIN a customer makes "the book must still be able to grow with the
    # arrival stream emptied" unanswerable -- so a suite that means "no draw" has
    # to say "no draw" rather than inherit it. Tests that want the campaign set
    # `SE_GROW_BOOK=1` themselves and override this.
    monkeypatch.setenv("SE_GROW_BOOK", "0")


def _served_static_roster():
    """The static roster AS THE RUN SERVES IT — the literal minus the suspended segments.

    THE BASELINE MOVED WHEN THE DIRECTOR MOVED IT (2026-08-24), and this suite went on
    measuring against the old one. `live_population` now filters `CUSTOMERS` through
    `served_segments()` before anything else touches the book, so the whole literal is no
    longer what any consumer sees: five I&C accounts (`C_IC1`..`C_IC4`, `C_IC3g`) are
    suspended, and 13 of the 18 are served.

    `_resolve_book() == list(CUSTOMERS)` therefore asserted a state the director had
    ordered changed. It is the "control that asserts the model stays bad" shape: the
    assertion reds not because the wire regressed but because the business did what it was
    told. Both tests below are re-aimed at the served roster, which is what "byte-identical
    to today's static-book report" has meant since the suspension landed.

    Derived, never listed: hardcoding the five IDs here would be a second copy of
    `served_segments()`, wrong the first time the director suspends or restores a segment.
    """
    from simulation.live_population import _serves, served_segments

    served = served_segments()
    return [c for c in CUSTOMERS if _serves(c, served)]


def test_the_suspension_is_actually_biting_on_this_roster():
    """NON-VACUITY, and the independence leg (R15 TAUTOLOGY).

    Every assertion below compares the wire against `_served_static_roster()`, which is
    built from the same predicate `live_population` uses — so on its own it would pass just
    as happily if the filter became a no-op and the suite silently went back to measuring
    the whole literal. This states the suspension's effect DIRECTLY instead: business
    accounts absent, residential accounts present, and the served book strictly smaller than
    the roster it came from.
    """
    served = _served_static_roster()
    assert len(served) < len(CUSTOMERS), "the filter is a no-op -- the baseline is untrustworthy"
    assert served, "the filter removed everything -- an empty book proves nothing below"
    assert not any(c["segment"] in {"ic", "sme"} for c in served), \
        "a suspended segment is being served"
    assert any(c["segment"] == "resi" for c in served), "the filter took the resi book too"


def test_resolve_book_flag_off_byte_identical_to_static_customers():
    """Default-OFF the resolved book equals the static roster the run actually serves."""
    assert _resolve_book() == _served_static_roster()


def test_resolve_book_flag_on_additively_carries_syn_cohort(monkeypatch):
    """Wire is load-bearing: flag-on the book grows by the SYN cohort. Reverting
    the wire to `list(CUSTOMERS)` (the mutation) fails this assertion.

    `SE_GROW_BOOK=0` pins PB3's net-new campaign OFF so this measures the DRAW seam and
    nothing else. Without it the assertion read "every addition starts with SYN-", which was
    true while the draw was the only source of additions and stopped being true the moment
    the growth mandate was activated (2026-08-24) — and it WEDGED PUBLISHING, because this
    file is inside the publish gate's blocking set. The subject here is the wire being
    load-bearing, not how many sources feed it; a second source makes that untestable rather
    than false. `test_resolve_book_carries_the_WON_accounts_too` below is where the campaign's
    additions are asserted.
    """
    monkeypatch.setenv(_ACTIVATION_ENV, "1")
    monkeypatch.setenv("SE_GROW_BOOK", "0")
    book = _resolve_book()

    # SERVED, not the whole literal (2026-08-24 suspension; see `_served_static_roster`).
    # As `CUSTOMERS`, `static_ids <= live_ids` demanded the book carry five accounts the
    # director had suspended -- the additivity claim asserted against a roster the run no
    # longer serves.
    static_ids = {c["customer_id"] for c in _served_static_roster()}
    live_ids = {c["customer_id"] for c in book}
    syn_ids = live_ids - static_ids

    # Additive-not-replacive: every static customer still present, plus SYN-*.
    assert static_ids <= live_ids
    assert syn_ids, "flag-on must additively include the SYN acquisition cohort"
    assert all(cid.startswith("SYN-") for cid in syn_ids)


def test_resolve_book_carries_the_WON_accounts_too(monkeypatch):
    """The dashboard's book is the one a READER sees, so it has to carry PB3's wins.

    This seam is what `generate_dashboard_data` resolves the published book from. If it
    carried the drawn trickle and not the accounts the funnel won, every per-customer figure
    on the site would be computed over a book the company does not have — the class of
    inconsistency that matters more here than any total.
    """
    monkeypatch.setenv(_ACTIVATION_ENV, "1")
    monkeypatch.setenv("SE_GROW_BOOK", "1")
    ids = {c["customer_id"] for c in _resolve_book()}
    assert {i for i in ids if i.startswith("PROS-")}, (
        "the published book must include the accounts the campaign won"
    )
    assert {i for i in ids if i.startswith("SYN-")}, "and the drawn trickle as well"


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
    # ACTIVATION 2026-08-13: this used to hand-copy the union as
    # CUSTOMERS + SUCCESSOR + ACQUIRED. That copy went stale the moment a FOURTH
    # book (DRAWN_CUSTOMERS) was registered -- the exact drift this file's own
    # header warns about. Assert the PROPERTY instead of a copy of the sum: what
    # the guard has always meant is "get_customer resolves a superset of the
    # seam's book", so ask get_customer, which cannot drift from itself.
    union_ids = {c["customer_id"] for c in
                 sc.CUSTOMERS + sc.SUCCESSOR_CUSTOMERS + sc.ACQUIRED_CUSTOMERS
                 + sc.DRAWN_CUSTOMERS}
    seam_ids = {c["customer_id"] for c in _resolve_book()}
    assert seam_ids <= union_ids
    # Stronger, and the form that survives a fifth book: every point the seam
    # hands out must actually RESOLVE. A naive re-route that dropped
    # successor/acquired would still trip the subset check above; this trips if
    # the lookup silently stops covering something the seam serves.
    assert all(sc.get_customer(cid) is not None for cid in seam_ids)
