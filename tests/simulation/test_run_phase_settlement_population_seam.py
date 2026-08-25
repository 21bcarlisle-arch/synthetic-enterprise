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
from tools.run_phase0c import _resolve_book as resolve_0c
from tools.run_phase1c import _resolve_book as resolve_1c
from tools.run_phase1c_full_window import _resolve_book as resolve_1c_fw

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
    added = live_ids - static_ids

    # Additive-not-replacive: every static customer still present, plus the drawn book.
    assert static_ids <= live_ids
    # THE SYN COHORT SPECIFICALLY, and it stays a separate assertion from the one below
    # because it is what makes this test able to fail: reverting the wire to
    # `list(CUSTOMERS)` (the named mutation) empties exactly this set.
    assert {cid for cid in added if cid.startswith("SYN-")}, (
        "flag-on must additively include the SYN acquisition cohort"
    )
    # TWO PREFIXES, NOT ONE, and this assertion was RED at HEAD until 2026-08-24 for a
    # reason worth stating rather than deleting. `SYN-` is the Profile-B trickle; `PROS-`
    # is an account the net-new campaign WON through the five-stage funnel (PB3, its own
    # id namespace by design so a prospect can never be confused with an account). The
    # campaign landed and this test still described a book with one drawn half, so it
    # failed on the shipped path and went on failing -- a control asserting the shape the
    # code had before the feature it was never updated for.
    assert all(cid.startswith(("SYN-", "PROS-")) for cid in added), sorted(added)


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
