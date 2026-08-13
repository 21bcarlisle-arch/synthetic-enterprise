"""WALLED_INTERFACES reference-flow conversion (W4_1_typed_adapters, third flow).

Proves tools/contact_centre_port.py is a transport-shape change to already-
correct data: the typed ContactCentreMessage carries the existing
generate_contact_centre_log dict losslessly and exposes a versioned schema.
Fixtures are built from the REAL producer (simulation.contact_centre.
generate_contact_centre_log), not synthetic dicts -- mirroring the port-
conformance style of tests/tools/test_meter_read_port.py and
tests/tools/test_acquisition_funnel_port.py.

Unlike those two flows there is no SIM-internal ground-truth field to guard:
every contact-centre field is company-observable operational data (see the port
module docstring), so there is no observable-only-accessor test here -- its
absence is the correct, honest reflection of this seam.
"""
from simulation.contact_centre import generate_contact_centre_log
from tools.contact_centre_port import (
    SCHEMA_VERSION,
    ContactCentreMessage,
    ContactCentrePort,
)


def _sample_log() -> list[dict]:
    """A real contact-centre log from the real generator.

    2026-08-13: this used to hand the generator a synthetic `contact_model` with
    `contact_probability=1.0` -- the supplier's estimate, which is exactly what
    `WORKER_FINDING_THE_WORLDS_CONTACT_RATE_IS_THE_COMPANYS_ESTIMATE_2026-08-11`
    removed from this seam. The generator now takes BILLS and draws off the
    world's own propensity, so the fixture supplies bills.

    They are deliberately BAD bills -- illegible (`clarity_score` 0.05) and a
    doubled month (`bill_shock_pct` 1.0) -- across a wide book, because the
    contact rate is now the world's answer and no fixture can dial it to 1.0
    without reaching back through the wall. The book is sized so the log is
    comfortably non-empty and spans multiple channels; both properties are
    ASSERTED below rather than assumed, so a drift in the world's physics
    surfaces as a named failure instead of silently emptying these tests.
    """
    bills = [
        {
            "customer_id": f"CP{index:04d}",
            "period_end": f"2020-{month:02d}-28",
            "clarity_score": 0.05,
            "bill_shock_pct": 1.0,
        }
        for index in range(40)
        for month in range(1, 13)
    ]
    return generate_contact_centre_log(bills)


def test_round_trip_is_lossless_identity_on_existing_dict():
    log = _sample_log()
    assert log, "generator produced no contacts -- fixture is not exercising anything"
    round_tripped = [ContactCentreMessage.from_log_entry(e).to_log_entry() for e in log]
    # Default to_log_entry() must be byte-for-byte the pre-conversion entry so
    # the current downstream consumer of contact_centre_log is unaffected.
    assert round_tripped == log


def test_schema_version_present_and_defaulted():
    log = _sample_log()
    msg = ContactCentreMessage.from_log_entry(log[0])
    # Historical entries have no schema_version -- must default, not raise.
    assert "schema_version" not in log[0]
    assert msg.schema_version == SCHEMA_VERSION
    # Opt-in serialisation surfaces it on the versioned wire.
    assert msg.to_log_entry(include_schema_version=True)["schema_version"] == SCHEMA_VERSION
    assert "schema_version" not in msg.to_log_entry()


def test_from_log_entry_carries_every_field():
    entry = {
        "customer_id": "C7",
        "period_end": "2020-06-28",
        "channel": "email",
        "first_response_hours": 31.4,
        "breached_sla": True,
    }
    msg = ContactCentreMessage.from_log_entry(entry)
    assert msg.customer_id == "C7"
    assert msg.period_end == "2020-06-28"
    assert msg.channel == "email"
    assert msg.first_response_hours == 31.4
    assert msg.breached_sla is True


def test_channel_values_from_real_producer_are_in_known_set():
    channels = {ContactCentreMessage.from_log_entry(e).channel for e in _sample_log()}
    assert channels <= {"phone", "email", "webchat"}
    # The fixture's own claim, checked rather than asserted in prose: an empty
    # or single-channel log would make the membership check above a statement
    # about nothing, and it is the world's propensity -- not a dialled-in 1.0 --
    # that now decides how many events there are.
    assert len(channels) > 1, (
        f"the fixture book spanned only {channels or 'no channels at all'}; the "
        "membership check above proves nothing on a log this narrow"
    )


def test_port_is_runtime_checkable_protocol():
    class _SimContactCentreAdapter:
        def __init__(self, log):
            self._log = log

        def get_contact_events(self):
            return [ContactCentreMessage.from_log_entry(e) for e in self._log]

    adapter = _SimContactCentreAdapter(_sample_log())
    assert isinstance(adapter, ContactCentrePort)
    events = adapter.get_contact_events()
    assert events and all(isinstance(ev, ContactCentreMessage) for ev in events)

    class _NotAPort:
        pass

    assert not isinstance(_NotAPort(), ContactCentrePort)
