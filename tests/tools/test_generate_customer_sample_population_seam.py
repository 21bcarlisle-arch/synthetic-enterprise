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
    monkeypatch.delenv(_ACTIVATION_ENV, raising=False)


def test_resolve_book_flag_off_byte_identical_to_static_customers():
    """Default-OFF the resolved lookup book equals the static literal exactly."""
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


def test_flag_on_syn_dict_carries_commodity_but_not_property_fields(monkeypatch):
    """HONEST seam property: the lookup reads commodity / home_type / smart_meter.
    A SYN dict carries `commodity` (a saas-shaped observable) but NOT the
    property fields (home_type/smart_meter) — those belong to the property-model
    generator, not this report-lookup one. Documents why the flag-on output
    effect here is book membership (uniformity), not enriched property columns."""
    monkeypatch.setenv(_ACTIVATION_ENV, "1")
    book = _resolve_book()
    static_ids = {c["customer_id"] for c in CUSTOMERS}
    syn_dicts = [c for c in book if c["customer_id"] not in static_ids]
    assert syn_dicts, "expected at least one SYN dict flag-on"
    d = syn_dicts[0]
    assert "commodity" in d  # observable the lookup CAN resolve
    assert "home_type" not in d and "smart_meter" not in d  # property-model's job


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
