"""R15 both-ways: the SYN-safe settlement entrypoints resolve their customer
book through the single ``live_population()`` seam (generator draw-wiring,
PRODUCT-FIRST item 2 — the last non-walled draw before the held director-reserved
flip), not a direct import of the static ``CUSTOMERS`` literal.

Scope — the three PURE-settlement entrypoints named SYN-SAFE in the doc's
blast-radius map: ``run_phase0c``, ``run_phase1c``, ``run_phase1c_full_window``.
Each iterates its book ONLY through ``customer_to_settlement_input(customer)``,
which reads exactly ``customer_id`` + ``acquisition_date`` — both fields the SYN
shape carries. So wiring these needs no property-model hardening (unlike the HH /
dashboard generators), and the flag-on book is settleable as-is.

Two directions, per R15 (a wire must be able to FAIL on its own named defect):

  * DEFAULT-OFF byte-identical: with ``SE_DRAW_POPULATION`` unset, each module's
    ``_resolve_book()`` returns exactly ``list(CUSTOMERS)`` — proves the wire did
    not perturb today's static-book settlement run.

  * FLAG-ON load-bearing: with ``SE_DRAW_POPULATION=1``, the resolved book
    additively carries the SYN acquisition cohort, and every SYN dict carries the
    two settlement-input fields (so the settlement path consumes it without a
    KeyError). The MUTATION that reverts ``_resolve_book()`` to ``list(CUSTOMERS)``
    makes the flag-on assertion fail (SYN would never appear), proving the wire is
    load-bearing, not decorative.
"""

import pytest

from saas.customers import CUSTOMERS, customer_to_settlement_input
from simulation.run_phase0c import _resolve_book as resolve_0c
from simulation.run_phase1c import _resolve_book as resolve_1c
from simulation.run_phase1c_full_window import _resolve_book as resolve_1c_fw

_ACTIVATION_ENV = "SE_DRAW_POPULATION"

_RESOLVERS = pytest.mark.parametrize(
    "resolve",
    [resolve_0c, resolve_1c, resolve_1c_fw],
    ids=["run_phase0c", "run_phase1c", "run_phase1c_full_window"],
)


@pytest.fixture(autouse=True)
def _flag_off_by_default(monkeypatch):
    """Pin the activation flag OFF unless a test sets it, so a leaked env var
    from another process/test cannot flip this suite (SCHEDULED_FLAG isolation)."""
    monkeypatch.delenv(_ACTIVATION_ENV, raising=False)


@_RESOLVERS
def test_resolve_book_flag_off_byte_identical_to_static_customers(resolve):
    """Default-OFF the resolved settlement book equals the static literal exactly."""
    assert resolve() == list(CUSTOMERS)


@_RESOLVERS
def test_resolve_book_flag_on_additively_carries_syn_cohort(resolve, monkeypatch):
    """Wire is load-bearing: flag-on the book grows by the SYN cohort. Reverting
    the wire to ``list(CUSTOMERS)`` (the mutation) fails this assertion."""
    monkeypatch.setenv(_ACTIVATION_ENV, "1")
    book = resolve()

    static_ids = {c["customer_id"] for c in CUSTOMERS}
    live_ids = {c["customer_id"] for c in book}
    syn_ids = live_ids - static_ids

    # Additive-not-replacive: every static customer still present, plus SYN-*.
    assert static_ids <= live_ids
    assert syn_ids, "flag-on must additively include the SYN acquisition cohort"
    assert all(cid.startswith("SYN-") for cid in syn_ids)


@_RESOLVERS
def test_flag_on_syn_dicts_are_settlement_safe(resolve, monkeypatch):
    """The reason these entrypoints are SYN-safe: ``customer_to_settlement_input``
    reads only ``customer_id`` + ``acquisition_date``, and every flag-on SYN dict
    carries both — so the settlement path consumes the additive cohort without a
    KeyError (no property-model hardening needed here, unlike the HH generators)."""
    monkeypatch.setenv(_ACTIVATION_ENV, "1")
    book = resolve()
    static_ids = {c["customer_id"] for c in CUSTOMERS}
    syn_dicts = [c for c in book if c["customer_id"] not in static_ids]
    assert syn_dicts, "expected at least one SYN dict flag-on"
    for d in syn_dicts:
        si = customer_to_settlement_input(d)  # must not KeyError
        assert si["customer_id"] == d["customer_id"]
        assert si["acquisition_date"]  # non-empty ISO date
