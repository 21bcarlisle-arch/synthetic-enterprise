"""The company's SUBMISSION side of the payment seam -- leg 1 on the wire
(atom EP6_wall_protocol_typing, Q3).

WHY THIS IS ITS OWN MODULE. Every other company-side piece of this crossing
RECEIVES: `payment_observation_consumer` reads what arrives and turns it into
belief. Nothing sent. The collection request was the seam's oldest declared
shape and the one nothing had ever constructed -- `wall_channel_census`'s
conversation question read the payment seam as UNSOLICITED INBOUND for exactly
that reason, "the response role is live and NOTHING IN THIS BUILD EVER ASKS".
Emission is a different act from observation and gets its own file rather than a
method on the consumer, which would have made the company's one outbound message
a branch of the object that exists to listen.

WHY IT LIVES UNDER `company/interfaces/` AND NOT `company/billing/` (moved
2026-08-21, at the landing of the pass that wrote it). Written under billing, it
was imported by `background/live_payment_triad.py`, which `simulation/run_phase2b`
imports -- so it created a NEW INDIRECT wall crossing,
`simulation.run_phase2b -> company.billing.collection_submission`, and
`tests/architecture/test_epistemic_wall_indirect_ratchet.py` refused the commit
in the terms its own allowlist is written in: *"a NEW indirect crossing must be
cut rather than added here ... Cut it, or route it through `company.interfaces`."*
This module holds no billing rule -- it is a CODEC and nothing else, importing
only the company's own wall protocol and the published contracts -- so the seam
package is where it always belonged, and putting it there makes the edge exempt
because it genuinely IS a sanctioned seam crossing rather than because the
instrument stopped looking. The distinction matters: re-exporting a billing
module through `company/interfaces/` would have been the laundering shape KNIFE
pass 1 refused, and moving a file that carried business logic would have been
the same move wearing a rename.

WHAT CROSSES, AND WHY IT NEEDS NO EPISTEMIC-WALL DENYLIST. `CollectionRequest`
is COMPANY-OWNED DATA GOING OUT -- an account reference, a mandate reference, an
amount it invoiced, a rail it chose, a date it picked. The wall polices what
flows BACK (`payment_observable_seam`'s own header: "the epistemic wall polices
what flows BACK across the seam, not what the company already possesses and
sends out"), so the `FORBIDDEN_TRUTH_FIELDS` / `OBSERVABLE_PAYLOAD_FIELDS`
machinery that guards the response leg has no subject here. What this module
owes instead is the opposite discipline: it must not put on the wire anything
the company does not itself hold, and the payload's five fields are enumerated
below rather than reflected off the dataclass so that a field added to
`CollectionRequest` fails here instead of crossing unexamined.

THE TWO SIDES STAY INDEPENDENT CODE, which is what makes the far side's refusal
a check rather than a handshake with itself. This module encodes through the
company's own codec (`wall_protocol.encode_request`). The counterparty decodes
with `simulation.payment_seam_adapter.decode_collection_request`, which may not
import `company.*` at all and instead mirrors the published key set and refuses
against it -- the same shape `simulation/conversation_response.py` already uses,
and the only shape the wall permits.

NOT FRAMED, and named rather than left to be found. `frame_wire_message` /
`decode_framed_response` (pass 39) authenticate the COUNTERPARTY to the company
on the inbound leg. Nothing here authenticates the company to the bureau -- a
real Bacs submission carries a service user number and its own credential, and
this one carries neither. That is Q13's axis pointed the other way down the
wire, and it is the next thing this leg needs.
"""
from __future__ import annotations

from dataclasses import fields
from typing import Any, Dict

from company.interfaces.wall_protocol import encode_request
from interface.contracts.payment_observable_seam import CollectionRequest
from interface.contracts.wall_envelope import WallRequest

#: The exact key set of a collection request's PAYLOAD on the wire. Enumerated,
#: never derived from `dataclasses.fields(CollectionRequest)`: a set computed
#: from its own subject widens whenever the subject widens and could never
#: catch a field being added, which is the R15 TAUTOLOGY pattern this seam's
#: response-side declaration already guards against for the same reason.
COLLECTION_REQUEST_WIRE_FIELDS: tuple[str, ...] = (
    "account_id",
    "mandate_ref",
    "amount_gbp",
    "rail",
    "requested_collection_date",
)


class CollectionSubmissionError(ValueError):
    """This company refused to put a submission on the wire."""


def encode_collection_payload(payload: CollectionRequest) -> Dict[str, Any]:
    """One collection request payload, serialised.

    REFUSES a payload whose field set is not exactly the declared one, in both
    directions. A MISSING field would mean the contract shrank under this
    module without it noticing; an EXTRA one would mean a field was added to
    `CollectionRequest` and reached the wire without anyone deciding it should.
    The second is the one that matters and it is the fail-open direction: a
    reflected encoder would have carried it silently."""
    if not isinstance(payload, CollectionRequest):
        raise CollectionSubmissionError(
            f"expected a CollectionRequest, got {type(payload).__name__} -- this "
            "seam submits collections and nothing else"
        )
    declared = set(COLLECTION_REQUEST_WIRE_FIELDS)
    actual = {f.name for f in fields(payload)}
    if actual != declared:
        raise CollectionSubmissionError(
            f"CollectionRequest fields {sorted(actual)} are not the declared wire "
            f"fields {sorted(declared)} -- a field added to the payload must be "
            "declared here before it can cross"
        )
    return {
        "account_id": payload.account_id,
        "mandate_ref": payload.mandate_ref,
        "amount_gbp": float(payload.amount_gbp),
        "rail": payload.rail.value,
        "requested_collection_date": payload.requested_collection_date.isoformat(),
    }


def encode_collection_request(request: WallRequest) -> Dict[str, Any]:
    """Leg 1 on the wire: the company's submission, envelope and all.

    The vintage stamp comes from `wall_protocol.encode_request`, which puts
    `schema_version` on every envelope it builds -- so a submission cannot cross
    without saying which release of the contract it was written against."""
    if not isinstance(request, WallRequest):
        raise CollectionSubmissionError(
            f"expected a WallRequest, got {type(request).__name__}"
        )
    return encode_request(request, encode_payload=encode_collection_payload)
