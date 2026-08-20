"""THE CONVERSATION SEAM, CROSSED (atom EP6_wall_protocol_typing, 2026-08-20).

The two codec-side test files each prove one half in isolation, on purpose:
encoding with a module and decoding with the same module would be an R15
TAUTOLOGY -- green through any schema change, because both halves changed
together. THIS file is the only place the two are put in the same room, and it
is the only place that can answer the atom's actual claim: *a mock counterparty
and a real one are indistinguishable to the company*.

It is also the R11-shaped half. A codec nothing calls is a built-and-dark
capability; what makes this crossing real is that `background/
conversation_gap_ledger.py` -- the harness that publishes the belief-vs-truth
gap -- now trains the company's estimator through the wire and not through an
in-process object. So the published gap is measured against a company that only
ever saw an encoded, version-checked envelope.

Named for `conversation_gap_ledger.py`'s stem so `pre_commit_test_gate.
tests_for` maps that module to these tests; before this file it mapped to none.
"""
import datetime as dt

import pytest

from background import conversation_gap_ledger as gl
from company.comms.conversation_generator import ConversationGenerator, CustomerSegment
from company.comms.susceptibility_estimator import SusceptibilityEstimator
from company.interfaces.wall_protocol import WallProtocolError
from interface.contracts.conversation_seam import Product, Situation
from simulation import conversation_response as cr

AS_OF = dt.datetime(2026, 1, 1, 9, 0)
EMITTED_AT = dt.datetime(2026, 1, 1, 9, 30)


def _imported_roots(rel_path: str) -> set:
    """The top-level package of every module `rel_path` imports, from its AST."""
    import ast
    import pathlib

    tree = ast.parse(pathlib.Path(rel_path).read_text())
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def _company_request(customer="c1", step=5, situation=Situation.RENEWAL):
    return ConversationGenerator().generate_wire_request(
        customer, CustomerSegment(), situation, Product.DUAL_FUEL, step,
        as_of=AS_OF, emitted_at=EMITTED_AT,
    )


# ---------------------------------------------------------------------------
# The crossing, end to end, in both directions.
# ---------------------------------------------------------------------------


def test_the_companys_bytes_are_readable_by_the_counterparty():
    """Leg one: the company encodes with ITS codec, the world decodes with
    ITS OWN, and neither imports the other. What makes them agree is the
    contract and only the contract."""
    request = cr.decode_wire_request(_company_request())
    assert request.payload.message_id == "c1:renewal:5"
    assert request.payload.situation is Situation.RENEWAL
    assert request.schema_version == 1


def test_the_counterpartys_bytes_are_readable_by_the_company():
    """Leg two, and the load-bearing one: the world's observable comes back as
    bytes and the company's belief moves. Nothing in this chain hands over a
    Python envelope."""
    wire_request = _company_request()
    wire_response = cr.respond_to_wire_request("c1", wire_request)
    message = cr.decode_wire_request(wire_request).payload

    estimator = SusceptibilityEstimator()
    assert estimator.observe_wire("c1", message, wire_response) is True
    assert estimator.posterior_report("c1")["framing_means"]


def test_the_whole_crossing_survives_json():
    """The wire form has to be bytes-shaped in fact and not by intention: a
    round trip through JSON must change nothing on either leg. This is what
    stops an enum, a datetime or a dataclass hiding in the "wire" message."""
    import json

    wire_request = json.loads(json.dumps(_company_request()))
    wire_response = json.loads(json.dumps(cr.respond_to_wire_request("c1", wire_request)))
    message = cr.decode_wire_request(wire_request).payload
    assert SusceptibilityEstimator().observe_wire("c1", message, wire_response) is True


def test_the_company_is_indistinguishable_between_a_wire_and_an_object_counterparty():
    """THE ATOM'S CLAIM, as a test. Two companies, same customer, same message:
    one is handed the observable as an object, the other as bytes. Their
    beliefs must be identical -- if the transport moves the belief at all, then
    a mock and a real counterparty are NOT indistinguishable, whatever the
    envelope says."""
    wire_request = _company_request()
    message = cr.decode_wire_request(wire_request).payload

    over_wire = SusceptibilityEstimator()
    over_wire.observe_wire("c1", message, cr.respond_to_wire_request("c1", wire_request))

    in_process = SusceptibilityEstimator()
    in_process.observe_response("c1", message, cr.respond("c1", message))

    assert over_wire.posterior_report("c1") == in_process.posterior_report("c1")


def test_the_two_sides_never_import_each_other():
    """The independence the round trip above rests on, asserted structurally.
    If either side ever imported the other's codec, every test in this file
    would keep passing while proving nothing.

    READ FROM THE AST, not by scanning for lines that start with `import`: a
    docstring in either module can wrap onto a line beginning "from ``x``",
    and a control that a stray sentence can turn red is a control that gets
    weakened until it is meaningless."""
    assert _imported_roots("simulation/conversation_response.py").isdisjoint(
        {"company", "saas"}
    )
    for company_module in (
        "company/comms/susceptibility_estimator.py",
        "company/comms/conversation_generator.py",
    ):
        assert _imported_roots(company_module).isdisjoint({"simulation", "sim"}), company_module


# ---------------------------------------------------------------------------
# The wire is the LIVE path, not a spare one.
# ---------------------------------------------------------------------------


def test_the_live_gap_ledger_trains_through_the_wire():
    """R11-shaped: not "a codec exists" but "the shipped path uses it". The
    training loop is driven with the company's `observe_wire` monkeypatched to
    refuse; if the harness were still handing over objects, the refusal would
    never fire and this test would pass for the wrong reason -- so the
    assertion is that it DID fire."""
    calls = []

    def refuse(self, customer_id, message, wire):
        calls.append((customer_id, wire))
        raise WallProtocolError("MISSING_FIELD", "refused by the test")

    original = SusceptibilityEstimator.observe_wire
    SusceptibilityEstimator.observe_wire = refuse
    try:
        with pytest.raises(WallProtocolError):
            gl._train_estimator(
                SusceptibilityEstimator(), ["c1"], Situation.RENEWAL,
                Product.DUAL_FUEL, rounds=1,
            )
    finally:
        SusceptibilityEstimator.observe_wire = original

    assert calls, "the live training loop never crossed the wire"
    assert set(calls[0][1]) == {
        "correlation_id", "status", "schema_version",
        "observed_at", "valid_time", "payload", "error",
    }


def test_the_live_training_loop_still_moves_the_belief_over_the_wire():
    """The other side of the same coin: with nothing patched, the wire path
    actually trains. A transport that refuses everything would satisfy the test
    above and teach the company nothing."""
    estimator = SusceptibilityEstimator()
    gl._train_estimator(estimator, ["c1", "c2"], Situation.RENEWAL, Product.DUAL_FUEL, rounds=3)
    means = estimator.posterior_report("c1")["framing_means"]
    assert means, "no framing evidence reached the belief over the wire"
    # Every framing value the harness explored is represented -- so the wire
    # carried the whole exploration, not one message that happened through.
    assert len(means) > 1


def test_the_envelope_clock_is_fixed_so_two_runs_produce_the_same_bytes():
    """C-S2 idempotent replay, at transport depth. If the harness stamped the
    envelope from the system clock, two identical runs would emit different
    messages and the published gap would stop being reproducible from
    (customer, message) alone."""
    first = SusceptibilityEstimator()
    second = SusceptibilityEstimator()
    gl._train_estimator(first, ["c1"], Situation.RENEWAL, Product.DUAL_FUEL, rounds=2)
    gl._train_estimator(second, ["c1"], Situation.RENEWAL, Product.DUAL_FUEL, rounds=2)
    assert first.posterior_report("c1") == second.posterior_report("c1")


def test_R15_MUTATION_a_counterparty_on_a_future_schema_is_refused_not_absorbed():
    """THE PROPERTY THE WHOLE ATOM IS FOR, and the one that was untestable
    while the envelope crossed as an object: a counterparty that bumps its
    schema must be REFUSED by a company that does not speak it.

    Before this pass, `schema_version` was populated at construction and read
    by nobody, so a v2 counterparty and a v1 one produced identical behaviour
    -- the version could not disagree, and a version that cannot disagree is
    not a version. Here the v2 message is refused distinguishably from a
    malformed one, which is what makes negotiation possible at all.

    NULL CONTROL: the same message at v1 is accepted, so the refusal is the
    VERSION and not the mutation of the dict.
    """
    wire_request = _company_request()
    message = cr.decode_wire_request(wire_request).payload
    response = cr.respond_to_wire_request("c1", wire_request)

    future = dict(response)
    future["schema_version"] = 2                      # the mutation
    control = dict(response)                          # the null control

    with pytest.raises(WallProtocolError) as exc:
        SusceptibilityEstimator().observe_wire("c1", message, future)
    assert exc.value.reason == "UNSUPPORTED_VERSION"
    assert SusceptibilityEstimator().observe_wire("c1", message, control) is True


def test_R15_MUTATION_a_counterparty_that_stops_stating_its_version_is_refused():
    """The FAIL-OPEN twin: a counterparty that drops the field entirely must be
    refused too, and with a DIFFERENT reason. "You did not say what you speak"
    and "you speak a dialect I do not know" call for different repairs, and a
    protocol that conflates them tells its operator nothing."""
    wire_request = _company_request()
    message = cr.decode_wire_request(wire_request).payload
    silent = dict(cr.respond_to_wire_request("c1", wire_request))
    del silent["schema_version"]

    with pytest.raises(WallProtocolError) as exc:
        SusceptibilityEstimator().observe_wire("c1", message, silent)
    assert exc.value.reason == "MISSING_FIELD"


def test_R15_MUTATION_a_counterparty_widening_the_payload_is_refused_at_the_wall():
    """The smuggling route: a counterparty that starts sending the hidden
    susceptibility scalar alongside the observables. The envelope is perfectly
    well-formed, so only a payload-depth refusal catches it -- and it must,
    because a company that folded that number into its belief would be reading
    ground truth, not inferring it.

    THE REASON CHANGED AT EP6 PASS 28 AND THE CHANGE IS THE POINT. This used to
    read `UNKNOWN_FIELD` -- the company's DERIVED key set refusing a name it did
    not recognise, which was the only check this leg had. It now reads
    CONTRACT_VIOLATION, because the seam's own `FORBIDDEN_TRUTH_FIELDS` is
    consulted first and says what was actually wrong: not "I do not know this
    field" but "you may never send me that". The distinction is load-bearing at
    go-live, when the counterparty is a real CRM and the derived set is the one
    thing that widens by itself.
    """
    wire_request = _company_request()
    message = cr.decode_wire_request(wire_request).payload
    leaky = cr.respond_to_wire_request("c1", wire_request)
    leaky["payload"]["fields"]["tone_susceptibility"] = 0.87   # the mutation

    with pytest.raises(WallProtocolError) as exc:
        SusceptibilityEstimator().observe_wire("c1", message, leaky)
    assert exc.value.reason == "CONTRACT_VIOLATION"
    assert "tone_susceptibility" in str(exc.value)


def test_NULL_CONTROL_a_counterparty_widening_with_an_INNOCENT_name_trips_the_OTHER_belt():
    """Without this, the test above cannot tell "the denylist fired" from
    "anything unusual is refused", and the belt could be measuring nothing. A
    name the contract has never heard of and the denylist has never named is
    still refused -- by the closed set, with the closed set's own reason. The
    two belts stay separately observable, each with a case only it can pass."""
    from interface.contracts.conversation_seam import FORBIDDEN_TRUTH_FIELDS

    wire_request = _company_request()
    message = cr.decode_wire_request(wire_request).payload
    odd = cr.respond_to_wire_request("c1", wire_request)
    odd["payload"]["fields"]["segment_score"] = 0.87

    assert "segment_score" not in FORBIDDEN_TRUTH_FIELDS
    with pytest.raises(WallProtocolError) as exc:
        SusceptibilityEstimator().observe_wire("c1", message, odd)
    assert exc.value.reason == "UNKNOWN_FIELD"
