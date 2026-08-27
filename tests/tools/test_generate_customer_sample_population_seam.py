"""R15 both-ways: the customer-sample generator resolves its lookup book
through the single `live_population()` seam (generator draw-wiring,
PRODUCT-FIRST item 2, report-lookup generator), not a direct import of the
static `CUSTOMERS` literal.

Two directions, per R15 (a control/wiring must be able to FAIL on its own
named defect):

  * DEFAULT-OFF byte-identical: with `SE_DRAW_POPULATION` unset, `_resolve_book()`
    returns exactly `list(CUSTOMERS)`, and end-to-end generate() over the static
    roster still resolves the same per-customer observables (home_type /
    smart_meter). Proves the wire did not perturb today's static-book report.

  * FLAG-ON load-bearing: with `SE_DRAW_POPULATION=1`, the resolved book
    additively carries the SYN acquisition cohort. The MUTATION that reverts
    `_resolve_book()` to `list(CUSTOMERS)` makes this fail (SYN would never
    appear), so the wire is proven load-bearing, not decorative.

HONEST SEAM PROPERTY (asserted, not hidden — this is a REPORT-LOOKUP generator,
not an output-enrichment one): the generator's lookup reads `commodity`,
`home_type`, `smart_meter` from each raw dict. A SYN dict carries `commodity`
but NOT `home_type`/`smart_meter` (those are the HH/property-model generator's
concern, wired separately). And this generator only enriches customers that
already appear in the run's `per_customer_lifetime`; SYN customers do not enter
a run until the held director-reserved flip wires the run entrypoints. So the
flag-on effect HERE is book MEMBERSHIP (uniformity — one seam, no lingering
direct `CUSTOMERS` import before the flip), not a changed published figure. The
test asserts that property directly rather than over-claiming a richer output.
"""

import json

import pytest

from saas.customers import CUSTOMERS
from tools.generate_customer_sample import _resolve_book, generate

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




# THE STATIC ROSTER IS NO LONGER THE SERVED BOOK (2026-08-27).
#
# These comparisons read `CUSTOMERS` -- the hand-authored roster -- as "what the book is without
# a draw". That held until the director suspended the I&C segment on 2026-08-24
# (docs/design/curriculum/served_segments.json): C_IC1..C_IC4 are still IN the roster, because
# the company must remain ABLE to onboard an industrial account, and are no longer on the book it
# serves. Every assertion below that said `== list(CUSTOMERS)` or `static_ids <= live_ids` was
# therefore comparing the served book against a superset of itself.
#
# `_served_static()` re-derives the served subset FROM THE CURRICULUM, not from the function under
# test, so the mutation each of these tests defends still fires: reverting the wire to
# `list(CUSTOMERS)` puts the four industrial accounts back and the comparison fails.
def _served_static():
    """The static roster minus whatever segments the curriculum currently suspends."""
    from simulation.live_population import _serves, served_segments
    served = served_segments()
    return [c for c in CUSTOMERS if _serves(c, served)]


def test_resolve_book_flag_off_byte_identical_to_static_customers():
    """Default-OFF the resolved lookup book equals the SERVED static roster exactly."""
    assert _resolve_book() == _served_static()


def test_resolve_book_flag_on_additively_carries_syn_cohort(monkeypatch):
    """Wire is load-bearing: flag-on the book grows by the SYN cohort. Reverting
    the wire to `list(CUSTOMERS)` (the mutation) fails this assertion."""
    monkeypatch.setenv(_ACTIVATION_ENV, "1")
    book = _resolve_book()

    static_ids = {c["customer_id"] for c in _served_static()}
    live_ids = {c["customer_id"] for c in book}
    syn_ids = live_ids - static_ids

    # Additive-not-replacive: every SERVED static customer still present, plus SYN-*.
    assert static_ids <= live_ids
    assert syn_ids, "flag-on must additively include the SYN acquisition cohort"
    assert all(cid.startswith("SYN-") for cid in syn_ids)


def test_flag_on_syn_dict_carries_commodity_but_not_property_fields(monkeypatch):
    """HONEST seam property: the lookup reads commodity / home_type / smart_meter.
    A SYN dict carries `commodity` (a saas-shaped observable) but NOT the
    property fields (home_type/smart_meter) — those belong to the property-model
    generator, not this report-lookup one. Documents why the flag-on output
    effect here is book membership (uniformity), not enriched property columns."""
    monkeypatch.setenv(_ACTIVATION_ENV, "1")
    book = _resolve_book()
    static_ids = {c["customer_id"] for c in _served_static()}
    syn_dicts = [c for c in book if c["customer_id"] not in static_ids]
    assert syn_dicts, "expected at least one SYN dict flag-on"
    d = syn_dicts[0]
    assert "commodity" in d  # observable the lookup CAN resolve
    # `home_type` remains the property model's job. `smart_meter` LEFT this list on 2026-08-25:
    # commit f8dc54ef8 ("every customer the funnel has ever won arrived with no meter, so 249 of
    # 264 accounts silently read as traditional") gave the drawn shape its own meter, drawn from
    # DESNZ penetration in `population_draw._draw_smart_meter`. It is now a drawn observable, not
    # a hand-authored property field, so a SYN dict carrying it is correct. The same correction
    # was owed in `tests/saas/test_drawn_customer_shape_class.py::STATIC_ONLY_FIELDS`.
    assert "home_type" not in d
    assert "smart_meter" in d


def _minimal_run(tmp_path, customers):
    run = {
        "per_customer_lifetime": customers,
        "by_billing_account": {},
        "customer_events": [],
        "basis_risk_by_billing_account": {},
        "churn_accuracy_by_billing_account": {},
        "per_customer_behavioral": {},
        "years": {},
        "feedback_survey_log": [],
        "reputation_events_log": [],
        "nudge_physics_log": [],
    }
    run_json = tmp_path / "run.json"
    run_json.write_text(json.dumps(run))
    return run_json


def test_flag_off_static_customer_report_path_unperturbed(tmp_path):
    """End-to-end byte-identical guarantee: flag-off, a static customer (C1)
    still resolves its home_type/smart_meter from the raw record via the seam —
    the report path is unchanged by the wiring."""
    customers = {
        "C1": {"segment": "resi", "commodity": "electricity",
               "acquisition_date": "2016-01-01",
               "revenue_gbp": 100.0, "gross_gbp": 50.0, "net_gbp": 20.0},
    }
    run_json = _minimal_run(tmp_path, customers)
    out_path = tmp_path / "customer_sample.json"
    state_path = tmp_path / "state_customer_sample.json"
    generate(str(run_json), out_path=str(out_path), state_path=str(state_path))
    c1 = json.loads(out_path.read_text())["customers"]["C1"]
    assert c1["home_type"] == "urban_flat"
    assert c1["smart_meter"] is True
