"""R15 both-ways: the HH-data generator draws its book through the
`live_population()` seam (generator draw-wiring, PRODUCT-FIRST item 2,
remaining step #2), not the static `CUSTOMERS` literal.

Two directions, per R15 (a control/wiring must be able to FAIL on its own
named defect):

  * DEFAULT-OFF byte-identical: with `SE_DRAW_POPULATION` unset, the book the
    generator resolves is exactly `list(CUSTOMERS)` and the HH selection is
    unchanged. Proves the wiring did not perturb today's static-book output.

  * FLAG-ON load-bearing: with `SE_DRAW_POPULATION=1`, the resolved book
    additively carries the SYN acquisition cohort and `build_properties(book)`
    builds records for it WITHOUT KeyError (integration of the landed SYN
    property derivation). MUTATION that reverts the wire to the static
    `CUSTOMERS` literal makes this fail — the SYN cohort would never appear —
    so the wire is proven load-bearing, not decorative.

HONEST SEAM PROPERTY (asserted, not hidden): SYN dicts carry no `metering`
field, so `is_hh_customer` selects none of them. The additive cohort reaches
the `book`/`properties` but NOT the written HH files. That is a documented
seam property (SYN HH metering + consumption files are a downstream
activation-time follow-on), not a wiring bug.

generate_for_customer is stubbed so no CSV files are written.
"""

import pytest

import tools.generate_hh_data as ghd
from saas.customers import CUSTOMERS
from simulation.hh_consumption import is_hh_customer

_ACTIVATION_ENV = "SE_DRAW_POPULATION"


@pytest.fixture(autouse=True)
def _no_disk_writes(monkeypatch):
    """Stub the per-customer CSV writer — this suite tests book resolution and
    property building, never file output."""
    monkeypatch.setattr(ghd, "generate_for_customer", lambda c, properties: None)


@pytest.fixture(autouse=True)
def _flag_off_by_default(monkeypatch):
    """Pin the activation flag OFF unless a test sets it, so a leaked env var
    from another process/test cannot flip this suite (SCHEDULED_FLAG isolation)."""
    monkeypatch.delenv(_ACTIVATION_ENV, raising=False)


def test_flag_off_book_is_byte_identical_to_static_customers():
    result = ghd.main()
    # The resolved book equals the static literal, same content and order.
    assert result["book"] == list(CUSTOMERS)
    # HH selection identical to reading CUSTOMERS directly.
    assert result["hh_customers"] == [c for c in CUSTOMERS if is_hh_customer(c)]


def test_flag_on_book_additively_carries_syn_cohort(monkeypatch):
    """Wire is load-bearing: flag-on the book grows by the SYN cohort. Reverting
    the wire to `book = CUSTOMERS` (the mutation) fails this assertion."""
    monkeypatch.setenv(_ACTIVATION_ENV, "1")
    result = ghd.main()

    static_ids = {c["customer_id"] for c in CUSTOMERS}
    live_ids = {c["customer_id"] for c in result["book"]}
    syn_ids = live_ids - static_ids

    # Additive-not-replacive: every static customer still present, plus SYN-*.
    assert static_ids <= live_ids
    assert syn_ids, "flag-on must additively include the SYN acquisition cohort"
    assert all(cid.startswith("SYN-") for cid in syn_ids)


def test_flag_on_build_properties_covers_syn_without_keyerror(monkeypatch):
    """Integration of the landed SYN property model: build_properties over the
    live book builds records for the SYN cohort (no `home_type` KeyError)."""
    monkeypatch.setenv(_ACTIVATION_ENV, "1")
    result = ghd.main()  # would raise KeyError pre-property-model if it regressed

    # build_properties returns a dict keyed by customer_id.
    prop_ids = set(result["properties"].keys())
    static_ids = {c["customer_id"] for c in CUSTOMERS}
    syn_ids = {c["customer_id"] for c in result["book"]} - static_ids
    resi_elec_syn = {
        c["customer_id"]
        for c in result["book"]
        if c["customer_id"] in syn_ids and c.get("commodity") == "electricity"
    }
    # Every residential-electricity SYN customer got a property record built.
    assert resi_elec_syn <= prop_ids


def test_flag_on_hh_selection_unchanged_syn_not_metered(monkeypatch):
    """HONEST seam property: SYN dicts carry no `metering`, so the additive
    cohort does NOT reach the HH selection/output. The richer population lives
    in book/properties here, not the written HH files."""
    monkeypatch.setenv(_ACTIVATION_ENV, "1")
    result = ghd.main()

    hh_ids = {c["customer_id"] for c in result["hh_customers"]}
    static_hh = {c["customer_id"] for c in CUSTOMERS if is_hh_customer(c)}
    assert hh_ids == static_hh  # no SYN entered the HH selection
