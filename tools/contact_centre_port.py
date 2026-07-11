"""ContactCentrePort -- structural interface + versioned message for the
customer-contact flow crossing the SIM/company seam (a contact-centre message
bus / omnichannel event stream in a real deployment): one first-response event
per bill-driven customer contact, with its channel and first-response latency.

Third reference-flow conversion of the WALLED_INTERFACES programme
(docs/design/WALLED_INTERFACES_SKETCH.md "Customer contact in/out" row,
maturity_map atom W4_1_typed_adapters). Same adapter pattern as
tools/meter_read_port.py::MeterReadPort (the first reference flow),
tools/acquisition_funnel_port.py::AcquisitionFunnelPort (the second),
tools/market_data_port.py::MarketDataPort (Phase PV) and
tools/credit_bureau_port.py::CreditBureauPort: a `runtime_checkable` Protocol
adapters satisfy without inheritance, plus a frozen, schema-versioned message
dataclass. Going live becomes swapping the sim adapter for a real omnichannel
contact-centre bus (Genesys/Twilio-style CTI + email/webchat) behind this
unchanged Protocol, not a rewrite.

This is a SHAPE change to already-correct data, not new business logic. The
message carries exactly the fields simulation/contact_centre.py already emits
into each `contact_centre_log` entry (see generate_contact_centre_log /
ContactEvent) -- {customer_id, period_end, channel, first_response_hours,
breached_sla} -- losslessly, plus a `schema_version`. `from_log_entry` /
`to_log_entry` round-trip is the identity on the existing dict, so the current
downstream consumer of `contact_centre_log` (saas/reporting/annual_report.py's
SLC 25C first-response-SLA-breach compliance check) is unaffected.

Field-shape honesty note: the WALLED_INTERFACES_SKETCH table illustrates this
crossing as `CustomerMessage {channel, direction, customer_id, correlation_id}`.
That is illustrative only and does NOT match the real producer -- as with the
prior two conversions, the sketch's field names were a guess. The actual
crossing dict has no `direction` and no `correlation_id`; it carries
`period_end`, `first_response_hours` and `breached_sla` instead. These messages
mirror the REAL producer, not the sketch.

Epistemic boundary (CLAUDE.md Architectural Law #2 -- the company cannot see
inside the SIM): unlike meter reads (`true_consumption_kwh`) and the acquisition
funnel (`credit_bureau_true_creditworthy`), there is NO SIM-internal / company-
observable split here. Every field is the supplier's OWN contact-centre
operational record: the company knows which of its customers contacted it, on
what channel, how long its own first response took, and whether its own SLA was
breached. No hidden ground-truth field crosses this seam (only contacts that
actually occurred appear in the log at all -- the underlying contact_probability
roll is not carried), so no observable-only accessor is needed. This is stated
plainly rather than inventing a distinction that does not exist.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

# Bump on any breaking change to the message field set / semantics. New readers
# should tolerate an unfamiliar version rather than assume 1.0's exact shape.
SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class ContactCentreMessage:
    """One customer contact-centre first-response event as a versioned typed
    message.

    Field set mirrors the `contact_centre_log` entry simulation/contact_centre.py
    emits exactly (only `occurred=True` events are logged, so channel /
    first_response_hours / breached_sla are always populated), so the crossing
    is a transport-shape change only. All fields are company-observable contact-
    centre operational data -- see the module docstring's epistemic note; there
    is no SIM-internal ground-truth field for this flow.
    """

    customer_id: str
    period_end: str
    channel: str  # "phone" | "email" | "webchat"
    first_response_hours: float
    breached_sla: bool
    schema_version: str = SCHEMA_VERSION

    @classmethod
    def from_log_entry(cls, entry: dict) -> "ContactCentreMessage":
        """Build a message from an existing contact_centre_log dict.

        Absent `schema_version` (all pre-conversion data) defaults to
        SCHEMA_VERSION, so historical run outputs load unchanged.
        """
        return cls(
            customer_id=entry["customer_id"],
            period_end=entry["period_end"],
            channel=entry["channel"],
            first_response_hours=entry["first_response_hours"],
            breached_sla=entry["breached_sla"],
            schema_version=entry.get("schema_version", SCHEMA_VERSION),
        )

    def to_log_entry(self, include_schema_version: bool = False) -> dict:
        """Serialise back to the plain JSON-serialisable dict shape existing
        consumers expect. `include_schema_version` is opt-in so the default
        output is byte-for-byte the pre-conversion `contact_centre_log` entry
        (lossless identity round-trip); callers migrating to the versioned wire
        can set it True.
        """
        entry = {
            "customer_id": self.customer_id,
            "period_end": self.period_end,
            "channel": self.channel,
            "first_response_hours": self.first_response_hours,
            "breached_sla": self.breached_sla,
        }
        if include_schema_version:
            entry["schema_version"] = self.schema_version
        return entry


@runtime_checkable
class ContactCentrePort(Protocol):
    """Structural interface for a customer-contact event source. The sim adapter
    wraps the `contact_centre_log` simulation/run_phase4c_on_phase2b.py produces
    via simulation.contact_centre.generate_contact_centre_log; a real deployment
    slots an omnichannel contact-centre bus adapter in behind this same signature
    with zero consumer-layer changes.
    """

    def get_contact_events(self) -> list[ContactCentreMessage]: ...
