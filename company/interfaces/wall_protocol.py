"""The company's WIRE protocol for the wall envelope (atom EP6_wall_protocol_typing).

`interface/contracts/wall_envelope.py` (atom W4_4) already gives the wall its
typed, versioned message SHAPE -- `WallRequest[P]` / `WallResponse[R]`, with
`schema_version` a required field on both, `correlation_id` the sole link
between a request and a response that is its own event in time, and a
`__post_init__` that refuses a malformed envelope at construction.

What did not exist, and is the whole of this module, is the WIRE. Every
envelope in this repository is an in-process Python object handed straight to
its consumer; nothing ever serialised one. The 2026-08-18 path trace recorded
the consequence precisely: population of `schema_version` is complete and
structurally guaranteed at all ten construction sites, and the value has never
left the process -- "not a switch that is off, a wire that was never built".
A version field that is never transmitted cannot be negotiated, and version
negotiation is the property EP6 exists to provide.

WHY THIS LIVES ON THE COMPANY SIDE. The atom's claim is that "a mock
counterparty and a real one are indistinguishable to the company". Whether that
holds is decided at the point where the company DECODES what arrived, because
that is the only place a real endpoint and an in-process call differ in a way
the company can observe. A real counterparty hands over bytes; today's SIM hands
over an object. Put the codec here and both arrive as the same typed envelope,
having passed the same refusals -- which is what "indistinguishable" has to mean
if it is to be testable rather than hoped for. The envelope stays shared in
`interface/`; this module reads it and never widens it.

WHAT THE COMPANY LEARNS BY DECODING: nothing it did not already receive. This
is transport, not an observable. The payload is opaque to it -- callers supply
their own crossing's payload codec as an argument -- so no SIM internal can
enter through this module that was not already inside the envelope handed to it.

--------------------------------------------------------------------------
THE ONE RULE THIS MODULE ENFORCES: ABSENCE IS NEVER AGREEMENT.
--------------------------------------------------------------------------

A wire message must state every field of its envelope, including its nulls, and
must state its `schema_version`. A missing key is REFUSED -- never defaulted,
never inferred, never filled in from what this process happens to believe today.

That refusal is aimed at a named, measured defect in the sibling pattern rather
than at a hypothetical. `tools/*_port.py`'s `from_log_entry` reads
`entry.get("schema_version", SCHEMA_VERSION)` -- the reader's OWN module
constant, at read time. Today that is harmless because one version exists. The
first bump to "2.0" silently relabels every archived v1.0 entry as 2.0, because
an absent field and an agreeing field are the same bytes. A version field that
cannot disagree is not a version field, and a decoder that supplies the answer
it is checking is R15's FAIL-OPEN pattern in its purest form.

So: an absent key and an explicit null are different facts here, and this
decoder refuses to conflate them. Unknown keys are refused for the mirror-image
reason -- if a later schema adds a field, the version number is how a decoder
finds out, not silent tolerance of bytes it does not understand.

--------------------------------------------------------------------------
AND, SINCE PASS 39: A MESSAGE WHOSE SENDER THIS BUILD CANNOT NAME IS REFUSED.
--------------------------------------------------------------------------

The 2026-08-20 blind review went straight at this atom's headline claim -- "a
mock counterparty and a real one are indistinguishable to the company" -- and
answered it with the objection that made it a DISQUALIFYING question (Q13):
indistinguishability had been achieved by the identity check being ABSENT from
the path, which is a control gap and not an abstraction. It was true, and
measured: a repo-wide search for SMKI, DIP signing, DTN participant identity,
mutual TLS or client certificates found the concept only in
`background/one_way_door.py`, i.e. modelled solely as a RESERVED REAL-WORLD ACT
and never as a verified property of a message. Everything above this line would
decode a perfectly-formed envelope from absolutely anybody.

So the wire gains a TRANSPORT FRAME around the envelope, and the frame states
WHO IS SPEAKING. Identity is deliberately not an envelope field: in the real
networks this seam stands in for (DTN, the DIP, Bacstel-IP) the participant is
established by the CHANNEL -- a certificate, a signed header -- and the business
document inside knows nothing about it. Putting it in the envelope would also
have widened `interface/contracts/wall_envelope.py`, which this module is not
allowed to do and should not want to.

WHAT IS AND IS NOT MODELLED, said plainly so the next reader does not have to
infer it. What is modelled is the REFUSAL: an unregistered sender, a sender
presenting the wrong credential, and a sender speaking a schema version it is
not on, are three distinguishable rejections at the port, below any company
logic. What is NOT modelled is the cryptography -- there is no certificate
chain and no signature over the bytes, and a credential presented in the clear
would be worthless on a real network. The control being built here is the one
the review said was missing, which is the CHECK, not the cipher.

NOT A TAUTOLOGY (R15). The registry below holds a FINGERPRINT; the credential
itself lives in the counterparty's own module and never crosses into this one.
Neither side derives its value from the other at runtime, so a counterparty
that rotates its credential without telling this company breaks the seam --
which is the correct outcome, and the reason this is a check rather than a
handshake with itself.

PER-COUNTERPARTY VERSIONS, which is the other half of what the registry buys
(the review's Q10). `SUPPORTED_SCHEMA_VERSIONS` says what this BUILD can read;
a registry entry says what one COUNTERPARTY is currently on. With only the
first, every market release is a big-bang cutover and two versions of one
interface cannot run concurrently -- which is not how a DTC/SEC/BSC release
lands, since the counterparties cut over on their own dates. With both, being
on v2 with one participant while still on v1 with another is one row of a table
rather than a redesign. Q10 is NOT thereby answered in full and this module
does not claim it is: the wire FIELD SETS below are still version-blind, so
this build understands exactly one dialect and the table can currently only
express which participants are on it.

SCOPE, still deliberately narrow (SIMPLICITY GUARD; the atom's own origin_note
forbids a protocol cathedral by name). One frozen table, one wrapper shape, no
plugin lookup, no transport, no retry policy, no new message types. The payload
codec is a function ARGUMENT, not a registered type, so adding a crossing
requires no edit here.
"""
from __future__ import annotations

import datetime as dt
import hmac
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from types import MappingProxyType
from typing import Any, Callable, Mapping, Optional, Tuple, TypeVar

from interface.contracts.wall_envelope import (
    ErrorDetail,
    WallInterim,
    WallNotification,
    WallRequest,
    WallResponse,
    WallStatus,
)

__all__ = [
    "SUPPORTED_SCHEMA_VERSIONS",
    "WIRE_VOCABULARY_BY_VERSION",
    "REQUEST_WIRE_FIELDS",
    "RESPONSE_WIRE_FIELDS",
    "INTERIM_WIRE_FIELDS",
    "NOTIFICATION_WIRE_FIELDS",
    "FRAME_WIRE_FIELDS",
    "CounterpartyNature",
    "CounterpartyRecord",
    "COUNTERPARTY_REGISTRY",
    "DeploymentPosture",
    "DECLARED_POSTURE",
    "assert_registry_fit_for_posture",
    "WallProtocolError",
    "encode_request",
    "decode_request",
    "encode_response",
    "decode_response",
    "encode_interim",
    "decode_interim",
    "encode_notification",
    "decode_notification",
    "decode_frame",
    "decode_framed_response",
    "decode_framed_interim",
    "decode_framed_notification",
]

P = TypeVar("P")
R = TypeVar("R")
IT = TypeVar("IT")
N = TypeVar("N")

#: The exact key set of a request on the wire. Derived from nothing -- it is
#: stated here and asserted against the dataclass in the test suite, so a field
#: added to the envelope reds the suite instead of silently never crossing.
REQUEST_WIRE_FIELDS: frozenset[str] = frozenset(
    {"correlation_id", "request_type", "schema_version", "as_of", "emitted_at", "payload"}
)

#: The exact key set of a response on the wire. `payload`, `valid_time` and
#: `error` are frequently null and their keys are still REQUIRED: see the
#: module docstring on absence-is-never-agreement.
RESPONSE_WIRE_FIELDS: frozenset[str] = frozenset(
    {
        "correlation_id",
        "status",
        "schema_version",
        "observed_at",
        "valid_time",
        "payload",
        "error",
    }
)

#: The exact key set of an INTERIM leg on the wire (`WallInterim`, pass 44).
#: `leg` and `interim_type` are what distinguish it from a response; there is
#: no `status` key and its absence is load-bearing -- see the dataclass.
INTERIM_WIRE_FIELDS: frozenset[str] = frozenset(
    {"correlation_id", "leg", "interim_type", "schema_version", "observed_at", "payload"}
)

#: The exact key set of an unsolicited NOTIFICATION on the wire
#: (`WallNotification`, pass 43). It carries `sender` as a DOCUMENT field as
#: well as being framed by one: `sequence` is a position in one counterparty's
#: own stream, so a notification separated from its frame is still orderable.
NOTIFICATION_WIRE_FIELDS: frozenset[str] = frozenset(
    {
        "notification_id",
        "notification_type",
        "schema_version",
        "sender",
        "sequence",
        "observed_at",
        "valid_time",
        "payload",
    }
)


# ---------------------------------------------------------------------------
# THE WIRE VOCABULARY OF EACH RELEASE (EP6 pass 47, the review's Q10)
# ---------------------------------------------------------------------------
#
# Until this table existed the field sets above were VERSION-BLIND: one flat key
# set per message kind, applied to every version alike. Q10's remaining item said
# so exactly -- "this build understands exactly ONE wire dialect ... the table can
# currently only express WHICH participants are on v1, never run a genuine v1/v2
# pair. A release weekend cannot be rehearsed until the field sets are keyed by
# version." This is that keying.
#
# WHAT ACTUALLY DIFFERS BETWEEN v1 AND v2, said plainly, because a version table
# whose versions are identical is theatre and would deserve the name. The two
# releases differ in their MESSAGE VOCABULARY, not in the fields of a shared
# message: v1 is the original two-leg wall and can say ASK and ANSWER; v2 is the
# release that added the two new legs -- `WallNotification` (pass 43, TELL) and
# `WallInterim` (pass 44, NOT YET FINISHED). A participant still on v1 therefore
# cannot send this build an interim or a notification AT ALL, and one that tries
# is refused MESSAGE_TYPE_NOT_IN_VERSION rather than decoded.
#
# THE REQUEST AND RESPONSE KEY SETS ARE BYTE-IDENTICAL ACROSS v1 AND v2, and that
# is a FACT ABOUT THIS BUILD'S RELEASE HISTORY rather than a gap in the mechanism:
# no release here has changed a field on an existing message, and inventing one so
# the table looked busier would be fabricating a dialect. This is also how real
# DTC/SEC/BSC releases usually land -- new flows are added, existing documents are
# left alone, precisely so counterparties can cut over on their own dates. When a
# release DOES change a field set, it lands as a new row in this table rather than
# as an edit to the constants above, and both sets go on being read at once.
_V1_VOCABULARY: Mapping[str, frozenset[str]] = MappingProxyType(
    {"request": REQUEST_WIRE_FIELDS, "response": RESPONSE_WIRE_FIELDS}
)

_V2_VOCABULARY: Mapping[str, frozenset[str]] = MappingProxyType(
    {
        "request": REQUEST_WIRE_FIELDS,
        "response": RESPONSE_WIRE_FIELDS,
        "interim": INTERIM_WIRE_FIELDS,
        "notification": NOTIFICATION_WIRE_FIELDS,
    }
)

#: Schema version -> the message kinds that version defines -> that kind's exact
#: key set. This is the sole authority on both questions, which is why
#: `SUPPORTED_SCHEMA_VERSIONS` is DERIVED from it below rather than stated
#: alongside it: a version this build can read is exactly a version whose dialect
#: it knows, and two independent statements of that could drift apart silently.
WIRE_VOCABULARY_BY_VERSION: Mapping[int, Mapping[str, frozenset[str]]] = MappingProxyType(
    {1: _V1_VOCABULARY, 2: _V2_VOCABULARY}
)

#: Envelope schema versions this company build can read. A `schema_version`
#: outside this set is refused as UNSUPPORTED_VERSION -- distinguishably from
#: an absent one, because "you speak a dialect I do not know" and "you did not
#: say what you speak" are different failures and call for different repairs.
# TWO RELEASES AT ONCE (EP6 pass 44). The payment seam went to v2 when it grew
# the interim leg. This build reads BOTH: a release that dropped the previous
# version would refuse every message already in flight on the day it shipped,
# which is precisely the big-bang cutover the review's Q10 names as the failing
# answer. What this constant says is what this BUILD can read at all; which
# release a given participant is actually on is `CounterpartyRecord.
# speaks_schema_versions`, and the two are different facts.
SUPPORTED_SCHEMA_VERSIONS: frozenset[int] = frozenset(WIRE_VOCABULARY_BY_VERSION)


#: The exact key set of a TRANSPORT FRAME. `envelope` carries the message
#: above; `sender` and `credential` are what the channel asserts about who is
#: speaking. Three keys, all required -- an unsigned frame is not a frame, and
#: absence is never agreement here either.
FRAME_WIRE_FIELDS: frozenset[str] = frozenset({"sender", "credential", "envelope"})


class CounterpartyNature(str, Enum):
    """Whether a registry row names a REAL market participant or a STAND-IN.

    This is a property of the COUNTERPARTY, not of the deployment: "BACS-BUREAU-01
    is impersonated by a module in this repository" stays true whatever machine
    the company is started on. The deployment supplies the other half
    (`DeploymentPosture`), and only the two together decide whether startup is
    allowed -- which is the point, because a single value carrying both facts
    would be the config flag Q14 names as the failing answer.
    """

    REAL = "real"
    STAND_IN = "stand_in"


class DeploymentPosture(str, Enum):
    """Where this process believes it is running.

    Deliberately two values and no `TEST`/`STAGING` middle: the question Q14 asks
    is binary -- may a stand-in speak to this company or may it not -- and every
    additional name is another value somebody has to remember to exclude.
    """

    SIMULATION = "simulation"
    PRODUCTION = "production"


#: What THIS checkout is. The whole company runs against a simulated
#: counterparty, so the honest declaration is SIMULATION and the mechanism below
#: is the thing that bites on the day it is not.
#:
#: THIS CONSTANT IS NOT THE CONTROL, and saying so matters, because a posture
#: declared in the same shipping unit as the code that reads it is exactly the
#: "config flag and good intentions" the blind review's Q14 refuses. Two
#: independent things keep it honest, and neither is this line:
#:   * SEGREGATION -- the stand-in's credential exists only in `simulation/`, a
#:     tree `company/` may not import (`tools/epistemic_verifier`,
#:     `tests/architecture/test_epistemic_wall_ratchet.py`). A production
#:     artefact that ships `company/` without `simulation/` has no speaker.
#:   * NON-FORGEABILITY -- segregation removes the speaker and NOT the trust:
#:     the registry below still ships a fingerprint the stand-in can satisfy.
#:     `test_the_declared_nature_of_every_row_matches_the_tree` hashes the
#:     credential literals actually present under `simulation/` and reds if any
#:     row a stand-in can speak for is labelled REAL. Relabelling a row to slip
#:     past the assertion below therefore fails the suite instead of the seam.
DECLARED_POSTURE: "DeploymentPosture" = DeploymentPosture.SIMULATION


@dataclass(frozen=True)
class CounterpartyRecord:
    """What this company build accepts FROM one named counterparty.

    `credential_sha256` is a FINGERPRINT, never the credential: this module is
    the receiver, and a receiver that stores what it is checking is the R15
    TAUTOLOGY pattern one layer down. The counterparty holds its own secret in
    its own code, exactly as a real participant holds its own key.

    `speaks_schema_versions` is this counterparty's CURRENT release, which is a
    different fact from `SUPPORTED_SCHEMA_VERSIONS` (what this build can read at
    all). A version in the second but not the first is a message from a
    participant that has not cut over yet -- readable, and still wrong.

    `nature` says whether the participant on the other end is real or a
    stand-in. REQUIRED, with no default: a row that does not say is a row nobody
    decided about, and `assert_registry_fit_for_posture` reads any value it does
    not recognise as STAND_IN rather than waving it through -- absence is never
    agreement here either.
    """

    credential_sha256: str
    speaks_schema_versions: frozenset[int]
    nature: CounterpartyNature


#: The company's counterparty on the payment observable seam -- its bank/Bacs
#: bureau. One entry, because one crossing is framed today (see the module
#: docstring): a registry row for a participant that never sends would be a
#: line nobody maintains and a control nothing exercises.
PAYMENT_SEAM_SENDER = "BACS-BUREAU-01"

#: Every counterparty this build will accept a message from. A sender absent
#: from this mapping is REFUSED -- there is deliberately no default record and
#: no wildcard, because a registry with a fallback is a registry that cannot
#: say no.
COUNTERPARTY_REGISTRY: Mapping[str, CounterpartyRecord] = MappingProxyType(
    {
        PAYMENT_SEAM_SENDER: CounterpartyRecord(
            credential_sha256=(
                "639aca59b3a720c287d0473294933e0bb86c75173c6f0aedaaa5cbd376eda12a"
            ),
            speaks_schema_versions=frozenset({1, 2}),
            # A module in this repository holds the credential this fingerprint
            # is of (`simulation/payment_seam_adapter.py::PARTICIPANT_CREDENTIAL`).
            # Labelling it anything else reds the cross-check named on
            # DECLARED_POSTURE above.
            nature=CounterpartyNature.STAND_IN,
        ),
    }
)


def assert_registry_fit_for_posture(
    posture: Any,
    *,
    registry: Mapping[str, CounterpartyRecord] = COUNTERPARTY_REGISTRY,
) -> None:
    """The startup assertion: refuse to run a stand-in counterparty in production.

    THE RESIDUE THIS EXISTS FOR. Environment segregation stops the stand-in
    SPEAKING (it is not shipped), and does nothing whatever about the company
    still TRUSTING it: `COUNTERPARTY_REGISTRY` ships inside `company/` and would
    reach production intact, fingerprint and all. Anyone who then learned one
    string from a public repository would be a bank. So the check is not "can the
    stand-in be reached" -- it is "does this build still accept one".

    FAIL-CLOSED, AND THE DIRECTION IS THE WHOLE DESIGN. A posture this function
    does not recognise -- `None`, `""`, `"prod"`, `"PRODUCTION"`, a typo'd
    `"simulaton"`, an int, a list -- is read as PRODUCTION, the strictest
    reading, so no malformed value can ever WEAKEN the check. The R15 FAIL-OPEN
    pattern here would be an unreadable posture meaning "assume simulation", and
    that is precisely the reading a stand-in reaches production through: "I could
    not tell where I am" is not a licence to trust an impersonator. A record
    whose `nature` is not a `CounterpartyNature` is read the same way, for the
    same reason.

    NO VALUE MEANS SKIP. `registry` is injectable so a test can build a
    multi-participant world without mutating a module constant under a live
    suite -- the same justification `decode_frame` carries -- and it is not a
    permission dial: an empty registry has no stand-in to refuse because it
    accepts nobody at all, which is the safe end, not the open one.

    Raises `WallProtocolError("STAND_IN_IN_PRODUCTION", ...)` naming every
    offending participant, because "one of your counterparties is fake" without
    saying which is a message that costs an outage to act on.
    """
    # IDENTITY, not equality. `DeploymentPosture` is a str-Enum, so `== "simulation"`
    # would let the bare string through -- and a bare string is what an unvalidated
    # config read produces. Only the enum member itself relaxes the check.
    if posture is DeploymentPosture.SIMULATION:
        return
    offenders = sorted(
        sender
        for sender, record in registry.items()
        if getattr(record, "nature", None) is not CounterpartyNature.REAL
    )
    if not offenders:
        return
    named = ", ".join(repr(s) for s in offenders)
    read_as = (
        "declared PRODUCTION"
        if posture is DeploymentPosture.PRODUCTION
        else f"posture {posture!r}, which this build does not recognise and "
        f"therefore reads as PRODUCTION"
    )
    raise WallProtocolError(
        "STAND_IN_IN_PRODUCTION",
        f"refusing to start under {read_as}: the counterparty registry still "
        f"accepts messages from {named}, which this build does not hold as a "
        f"real market participant -- remove the row, or do not call this "
        f"deployment production",
    )


class WallProtocolError(ValueError):
    """A message that did not cross. Carries a machine-readable ``reason`` so a
    caller can tell a malformed counterparty apart from an unknown dialect
    without parsing prose, and so tests can assert WHICH refusal fired rather
    than merely that something raised.

    Reasons:
      ``NOT_A_MESSAGE``        -- the wire value is not a mapping at all.
      ``MISSING_FIELD``        -- a required key is absent (incl. schema_version).
      ``UNKNOWN_FIELD``        -- a key this schema version does not define.
      ``MALFORMED_FIELD``      -- a key is present with an unusable value.
      ``UNSUPPORTED_VERSION``  -- a version outside SUPPORTED_SCHEMA_VERSIONS.
      ``MESSAGE_TYPE_NOT_IN_VERSION`` -- the version is one this build reads, and
                                 that RELEASE defines no such message kind (an
                                 interim or a notification stamped v1). Distinct
                                 from UNSUPPORTED_VERSION because the dialect is
                                 known; it simply has no way to say this.
      ``CONTRACT_VIOLATION``   -- well-formed on the wire, but the envelope's own
                                 invariants reject it (e.g. an OK with no
                                 payload). Raised so a bad message NEVER reaches
                                 company logic as a half-built object.
      ``UNKNOWN_SENDER``       -- the frame names a participant this build has
                                 no registry entry for.
      ``BAD_CREDENTIAL``       -- the participant is known and did not prove it.
      ``VERSION_NOT_SPOKEN``   -- this build can read the dialect; THIS sender is
                                 not on that release.
      ``SENDER_MISMATCH``      -- the authenticated frame and the notification
                                 inside it name different senders, so the
                                 document's `sequence` belongs to someone
                                 else's stream.
      ``STAND_IN_IN_PRODUCTION`` -- raised at STARTUP, not on a message: this
                                 build was asked to run in production while its
                                 registry still accepts a stand-in counterparty.

    The middle three are separate reasons on purpose. "I have never heard of
    you", "you are not who you say you are" and "you have not cut over yet"
    call for three different repairs -- a registry entry, a credential
    rotation, and a release schedule -- and a single AUTH_FAILED would hide
    which.
    """

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(f"{reason}: {message}")
        self.reason = reason


# ---------------------------------------------------------------------------
# field-level codecs. Each refuses rather than coerces.
# ---------------------------------------------------------------------------


def _require_mapping(wire: Any, what: str) -> Mapping[str, Any]:
    if not isinstance(wire, Mapping):
        raise WallProtocolError(
            "NOT_A_MESSAGE", f"{what} must be a mapping, got {type(wire).__name__}"
        )
    return wire


def _require_exact_fields(wire: Mapping[str, Any], expected: frozenset[str], what: str) -> None:
    present = frozenset(wire)
    missing = sorted(expected - present)
    if missing:
        raise WallProtocolError(
            "MISSING_FIELD",
            f"{what} omits required field(s) {missing} -- an absent field is never "
            "read as agreement with this process's own defaults",
        )
    unknown = sorted(present - expected)
    if unknown:
        raise WallProtocolError(
            "UNKNOWN_FIELD",
            f"{what} carries field(s) {unknown} that schema version(s) "
            f"{sorted(SUPPORTED_SCHEMA_VERSIONS)} do not define",
        )


def _decode_schema_version(raw: Any) -> int:
    # bool is an int subclass; a True here is a malformed version, not v1.
    if not isinstance(raw, int) or isinstance(raw, bool):
        raise WallProtocolError(
            "MALFORMED_FIELD", f"schema_version must be an int, got {raw!r}"
        )
    if raw not in SUPPORTED_SCHEMA_VERSIONS:
        raise WallProtocolError(
            "UNSUPPORTED_VERSION",
            f"schema_version {raw} is not one of {sorted(SUPPORTED_SCHEMA_VERSIONS)}",
        )
    return raw


def _require_vocabulary(wire: Any, kind: str, what: str) -> Tuple[Mapping[str, Any], int]:
    """Refuse, or return (the message, its decoded version).

    THE ORDER IS THE WHOLE POINT, and it is the reverse of what this module did
    before pass 47. The version is read FIRST, and only then is the key set it
    implies enforced -- because which fields are legal is a fact ABOUT a release,
    and a decoder that judges the fields before it knows the dialect is checking
    a message against a schema its sender never claimed to be speaking.

    The consequence is a deliberate change in which error wins: a message that
    is both on an unknown version and carrying an unknown field now reports
    UNSUPPORTED_VERSION, not UNKNOWN_FIELD. That is the honest report -- the
    field may well be perfectly legal in the release it came from, and this
    build has no way to know, so blaming the field would be an overclaim.

    `schema_version`'s own absence is still MISSING_FIELD, and is checked here
    rather than by the key-set pass, because that pass can no longer run: there
    is no key set to run it against until this value is known.
    """
    message = _require_mapping(wire, what)
    if "schema_version" not in message:
        raise WallProtocolError(
            "MISSING_FIELD",
            f"{what} omits required field ['schema_version'] -- nothing else about "
            "it can be judged, because which fields this message is allowed to "
            "carry is a fact about the release it is speaking",
        )
    version = _decode_schema_version(message["schema_version"])
    vocabulary = WIRE_VOCABULARY_BY_VERSION[version]
    expected = vocabulary.get(kind)
    if expected is None:
        raise WallProtocolError(
            "MESSAGE_TYPE_NOT_IN_VERSION",
            f"schema_version {version} defines no {kind!r} message -- it speaks "
            f"{sorted(vocabulary)}, so a counterparty on that release cannot have "
            f"sent one and this build will not read it as though it had",
        )
    _require_exact_fields(message, expected, f"{what} (schema_version {version})")
    return message, version


def _require_version_speaks(version: Any, kind: str) -> None:
    """The ENCODE-side half of the vocabulary table, and it is not decoration.

    An encoder that can emit a message its own decoder would refuse is the
    fail-open shape this module exists to avoid: the bytes would leave here
    looking legal and be rejected at the far end, where the reason is hardest to
    recover. Both directions read the ONE table above, so a release that gains
    or loses a message kind changes what can be sent and what can be received in
    the same edit -- they cannot drift apart.
    """
    decoded = _decode_schema_version(version)
    vocabulary = WIRE_VOCABULARY_BY_VERSION[decoded]
    if kind not in vocabulary:
        raise WallProtocolError(
            "MESSAGE_TYPE_NOT_IN_VERSION",
            f"cannot encode a {kind!r} stamped schema_version {decoded} -- that "
            f"release speaks {sorted(vocabulary)}, and bytes this build's own "
            "decoder would refuse are not bytes it should put on a wire",
        )


def _decode_int(raw: Any, field: str, *, minimum: Optional[int] = None) -> int:
    # bool is an int subclass; a True here is a malformed ordinal, not a 1.
    if not isinstance(raw, int) or isinstance(raw, bool):
        raise WallProtocolError(
            "MALFORMED_FIELD", f"{field} must be an int, got {raw!r}"
        )
    if minimum is not None and raw < minimum:
        raise WallProtocolError(
            "MALFORMED_FIELD", f"{field} must be >= {minimum}, got {raw!r}"
        )
    return raw


def _decode_correlation_id(raw: Any) -> str:
    if not isinstance(raw, str) or not raw:
        raise WallProtocolError(
            "MALFORMED_FIELD",
            f"correlation_id must be a non-empty str, got {raw!r} -- it is both the "
            "idempotency key and the only link to the response",
        )
    return raw


def _decode_str(raw: Any, field: str) -> str:
    if not isinstance(raw, str) or not raw:
        raise WallProtocolError(
            "MALFORMED_FIELD", f"{field} must be a non-empty str, got {raw!r}"
        )
    return raw


def _encode_datetime(value: dt.datetime, field: str) -> str:
    if not isinstance(value, dt.datetime):
        raise WallProtocolError(
            "MALFORMED_FIELD", f"{field} must be a datetime, got {type(value).__name__}"
        )
    return value.isoformat()


def _decode_datetime(raw: Any, field: str) -> dt.datetime:
    if not isinstance(raw, str):
        raise WallProtocolError(
            "MALFORMED_FIELD", f"{field} must be an ISO-8601 str, got {raw!r}"
        )
    try:
        return dt.datetime.fromisoformat(raw)
    except ValueError as exc:
        raise WallProtocolError("MALFORMED_FIELD", f"{field} is not ISO-8601: {raw!r}") from exc


def _encode_date(value: Optional[dt.date], field: str) -> Optional[str]:
    if value is None:
        return None
    # datetime is a date subclass; valid_time is a DATE and must not smuggle a time.
    if not isinstance(value, dt.date) or isinstance(value, dt.datetime):
        raise WallProtocolError(
            "MALFORMED_FIELD", f"{field} must be a date or None, got {type(value).__name__}"
        )
    return value.isoformat()


def _decode_date(raw: Any, field: str) -> Optional[dt.date]:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise WallProtocolError(
            "MALFORMED_FIELD", f"{field} must be an ISO-8601 date str or null, got {raw!r}"
        )
    try:
        return dt.date.fromisoformat(raw)
    except ValueError as exc:
        raise WallProtocolError("MALFORMED_FIELD", f"{field} is not an ISO date: {raw!r}") from exc


def _decode_status(raw: Any) -> WallStatus:
    if not isinstance(raw, str):
        raise WallProtocolError("MALFORMED_FIELD", f"status must be a str, got {raw!r}")
    try:
        return WallStatus(raw)
    except ValueError as exc:
        raise WallProtocolError(
            "MALFORMED_FIELD",
            f"status {raw!r} is not one of {[s.value for s in WallStatus]}",
        ) from exc


def _encode_error(error: Optional[ErrorDetail]) -> Optional[dict[str, str]]:
    if error is None:
        return None
    if not isinstance(error, ErrorDetail):
        raise WallProtocolError(
            "MALFORMED_FIELD", f"error must be an ErrorDetail or None, got {type(error).__name__}"
        )
    return {"code": error.code, "message": error.message}


def _decode_error(raw: Any) -> Optional[ErrorDetail]:
    if raw is None:
        return None
    wire = _require_mapping(raw, "error")
    _require_exact_fields(wire, frozenset({"code", "message"}), "error")
    return ErrorDetail(
        code=_decode_str(wire["code"], "error.code"),
        message=_decode_str(wire["message"], "error.message"),
    )


# ---------------------------------------------------------------------------
# the four public codecs
# ---------------------------------------------------------------------------


def encode_request(
    request: WallRequest[P], *, encode_payload: Callable[[P], Any]
) -> dict[str, Any]:
    """Serialise a request onto the wire, vintage stamp included, always.

    ``encode_payload`` is REQUIRED and has no default: every crossing states how
    its own payload crosses. There is deliberately no fallback that would
    stringify or `dataclasses.asdict` an unknown payload, because a codec that
    can serialise anything is a codec that can leak anything.
    """
    if not isinstance(request, WallRequest):
        raise WallProtocolError(
            "NOT_A_MESSAGE", f"expected a WallRequest, got {type(request).__name__}"
        )
    _require_version_speaks(request.schema_version, "request")
    return {
        "correlation_id": request.correlation_id,
        "request_type": request.request_type,
        "schema_version": request.schema_version,
        "as_of": _encode_datetime(request.as_of, "as_of"),
        "emitted_at": _encode_datetime(request.emitted_at, "emitted_at"),
        "payload": encode_payload(request.payload),
    }


def decode_request(
    wire: Any, *, decode_payload: Callable[[Any], P]
) -> WallRequest[P]:
    """Parse a request off the wire, or refuse it. Never defaults a field."""
    message, version = _require_vocabulary(wire, "request", "request")
    try:
        return WallRequest(
            correlation_id=_decode_correlation_id(message["correlation_id"]),
            request_type=_decode_str(message["request_type"], "request_type"),
            schema_version=version,
            as_of=_decode_datetime(message["as_of"], "as_of"),
            emitted_at=_decode_datetime(message["emitted_at"], "emitted_at"),
            payload=decode_payload(message["payload"]),
        )
    except ValueError as exc:
        if isinstance(exc, WallProtocolError):
            raise
        raise WallProtocolError("CONTRACT_VIOLATION", str(exc)) from exc


def encode_response(
    response: WallResponse[R], *, encode_payload: Callable[[R], Any]
) -> dict[str, Any]:
    """Serialise a response onto the wire, vintage stamp included, always.

    Both bitemporal coordinates cross: ``observed_at`` (when this answer became
    known) and ``valid_time`` (what period it is about). A restatement is a new
    message with a later ``observed_at`` for the same ``valid_time``; that is
    only expressible if both actually reach the receiver, which is why neither
    is optional on the wire.
    """
    if not isinstance(response, WallResponse):
        raise WallProtocolError(
            "NOT_A_MESSAGE", f"expected a WallResponse, got {type(response).__name__}"
        )
    _require_version_speaks(response.schema_version, "response")
    return {
        "correlation_id": response.correlation_id,
        "status": response.status.value,
        "schema_version": response.schema_version,
        "observed_at": _encode_datetime(response.observed_at, "observed_at"),
        "valid_time": _encode_date(response.valid_time, "valid_time"),
        "payload": None if response.payload is None else encode_payload(response.payload),
        "error": _encode_error(response.error),
    }


def decode_response(
    wire: Any, *, decode_payload: Callable[[Any], R]
) -> WallResponse[R]:
    """Parse a response off the wire, or refuse it.

    A message that is well-formed but violates the envelope's own invariants
    (an OK carrying no payload, a TIMEOUT carrying one) is re-raised as
    CONTRACT_VIOLATION rather than escaping as a bare ValueError, so a caller
    has exactly one exception type to handle at the seam and a malformed
    counterparty can never hand company logic a half-built object.
    """
    message, version = _require_vocabulary(wire, "response", "response")
    raw_payload = message["payload"]
    try:
        return WallResponse(
            correlation_id=_decode_correlation_id(message["correlation_id"]),
            status=_decode_status(message["status"]),
            schema_version=version,
            observed_at=_decode_datetime(message["observed_at"], "observed_at"),
            valid_time=_decode_date(message["valid_time"], "valid_time"),
            payload=None if raw_payload is None else decode_payload(raw_payload),
            error=_decode_error(message["error"]),
        )
    except ValueError as exc:
        if isinstance(exc, WallProtocolError):
            raise
        raise WallProtocolError("CONTRACT_VIOLATION", str(exc)) from exc


# ---------------------------------------------------------------------------
# the v2 vocabulary: the two legs that only the later release can speak
# ---------------------------------------------------------------------------
#
# Both shapes existed as in-process Python objects with live consumers before
# this pass and NEITHER had a wire -- the precise defect the module docstring
# describes for `schema_version` itself ("not a switch that is off, a wire that
# was never built"). A primitive that cannot be serialised cannot arrive from a
# real counterparty, so until here the conversation and the unsolicited stream
# were company-side constructions that no wire could deliver.


def encode_interim(
    interim: WallInterim[IT], *, encode_payload: Callable[[IT], Any]
) -> dict[str, Any]:
    """Serialise a non-terminal leg onto the wire.

    Refused if stamped with a version whose vocabulary has no interim, so an
    encoder cannot manufacture bytes that this build's own decoder would
    correctly reject -- the two directions are held to one table.
    """
    if not isinstance(interim, WallInterim):
        raise WallProtocolError(
            "NOT_A_MESSAGE", f"expected a WallInterim, got {type(interim).__name__}"
        )
    _require_version_speaks(interim.schema_version, "interim")
    return {
        "correlation_id": interim.correlation_id,
        "leg": interim.leg,
        "interim_type": interim.interim_type,
        "schema_version": interim.schema_version,
        "observed_at": _encode_datetime(interim.observed_at, "observed_at"),
        "payload": encode_payload(interim.payload),
    }


def decode_interim(
    wire: Any, *, decode_payload: Callable[[Any], IT]
) -> WallInterim[IT]:
    """Parse a non-terminal leg off the wire, or refuse it.

    A v1 message never reaches the body of this function: v1's vocabulary has no
    interim, so `_require_vocabulary` raises MESSAGE_TYPE_NOT_IN_VERSION. That
    refusal is the release weekend made testable -- a counterparty that has not
    cut over cannot tell this build an exchange is still in progress, because on
    its release there is no way to say it.
    """
    message, version = _require_vocabulary(wire, "interim", "interim")
    try:
        return WallInterim(
            correlation_id=_decode_correlation_id(message["correlation_id"]),
            leg=_decode_int(message["leg"], "leg"),
            interim_type=_decode_str(message["interim_type"], "interim_type"),
            schema_version=version,
            observed_at=_decode_datetime(message["observed_at"], "observed_at"),
            payload=decode_payload(message["payload"]),
        )
    except ValueError as exc:
        if isinstance(exc, WallProtocolError):
            raise
        raise WallProtocolError("CONTRACT_VIOLATION", str(exc)) from exc


def encode_notification(
    notification: WallNotification[N], *, encode_payload: Callable[[N], Any]
) -> dict[str, Any]:
    """Serialise an unsolicited inbound message onto the wire."""
    if not isinstance(notification, WallNotification):
        raise WallProtocolError(
            "NOT_A_MESSAGE",
            f"expected a WallNotification, got {type(notification).__name__}",
        )
    _require_version_speaks(notification.schema_version, "notification")
    return {
        "notification_id": notification.notification_id,
        "notification_type": notification.notification_type,
        "schema_version": notification.schema_version,
        "sender": notification.sender,
        "sequence": notification.sequence,
        "observed_at": _encode_datetime(notification.observed_at, "observed_at"),
        "valid_time": _encode_date(notification.valid_time, "valid_time"),
        "payload": encode_payload(notification.payload),
    }


def decode_notification(
    wire: Any, *, decode_payload: Callable[[Any], N]
) -> WallNotification[N]:
    """Parse an unsolicited inbound message off the wire, or refuse it."""
    message, version = _require_vocabulary(wire, "notification", "notification")
    try:
        return WallNotification(
            notification_id=_decode_str(message["notification_id"], "notification_id"),
            notification_type=_decode_str(
                message["notification_type"], "notification_type"
            ),
            schema_version=version,
            sender=_decode_str(message["sender"], "sender"),
            sequence=_decode_int(message["sequence"], "sequence"),
            observed_at=_decode_datetime(message["observed_at"], "observed_at"),
            valid_time=_decode_date(message["valid_time"], "valid_time"),
            payload=decode_payload(message["payload"]),
        )
    except ValueError as exc:
        if isinstance(exc, WallProtocolError):
            raise
        raise WallProtocolError("CONTRACT_VIOLATION", str(exc)) from exc


# ---------------------------------------------------------------------------
# the transport frame: who is speaking, checked before anything is believed
# ---------------------------------------------------------------------------


def _verify_frame(
    wire: Any, registry: Mapping[str, CounterpartyRecord]
) -> Tuple[str, CounterpartyRecord, Mapping[str, Any]]:
    """Refuse, or return (sender, that sender's record, the envelope inside).

    The order is the point: nothing about the envelope is read until the frame
    around it has named a participant this build knows and that participant has
    proved it. A decoder that parses first and authenticates afterwards has
    already done the work an unknown sender wanted done."""
    frame = _require_mapping(wire, "frame")
    _require_exact_fields(frame, FRAME_WIRE_FIELDS, "frame")
    sender = _decode_str(frame["sender"], "sender")
    credential = _decode_str(frame["credential"], "credential")

    record = registry.get(sender)
    if record is None:
        raise WallProtocolError(
            "UNKNOWN_SENDER",
            f"no registry entry for participant {sender!r} -- a message is not "
            "accepted because it is well-formed, and there is no default record",
        )
    presented = sha256(credential.encode("utf-8")).hexdigest()
    if not hmac.compare_digest(presented, record.credential_sha256):
        raise WallProtocolError(
            "BAD_CREDENTIAL",
            f"participant {sender!r} did not present the credential this build "
            "holds a fingerprint for",
        )
    envelope = _require_mapping(frame["envelope"], "frame.envelope")
    return sender, record, envelope


def decode_frame(
    wire: Any, *, registry: Mapping[str, CounterpartyRecord] = COUNTERPARTY_REGISTRY
) -> Tuple[str, Mapping[str, Any]]:
    """Verify the transport frame and hand back (sender, envelope-on-the-wire).

    ``registry`` exists so a test can build a two-participant world without
    mutating a module constant under a live suite; production callers pass
    nothing and get `COUNTERPARTY_REGISTRY`. It is not a permission dial --
    there is no value of it that means "skip the check", because an empty
    registry refuses everything rather than accepting everything.
    """
    sender, _record, envelope = _verify_frame(wire, registry)
    return sender, envelope


def decode_framed_response(
    wire: Any,
    *,
    decode_payload: Callable[[Any], R],
    registry: Mapping[str, CounterpartyRecord] = COUNTERPARTY_REGISTRY,
) -> Tuple[str, WallResponse[R]]:
    """Parse a response that arrived inside a transport frame, or refuse it.

    Returns the VERIFIED sender alongside the response, rather than dropping it:
    a consumer that cannot say which counterparty told it something cannot
    later tell two counterparties apart, and this is the only point in the path
    where that fact exists.

    THE PER-SENDER VERSION CHECK RUNS LAST, after the envelope has decoded. It
    could be done by peeking at the raw `schema_version` key first, and that is
    exactly the `entry.get(...)` shape this module was built to refuse: the
    value would not yet have been proven to be an int, in the supported set, or
    present at all. So the build-wide refusal happens first on a validated
    field, and the per-sender one on the value that survived it.
    """
    sender, record, envelope = _verify_frame(wire, registry)
    response = decode_response(envelope, decode_payload=decode_payload)
    _require_sender_speaks(sender, record, response.schema_version)
    return sender, response


def _require_sender_speaks(
    sender: str, record: CounterpartyRecord, version: int
) -> None:
    """The per-COUNTERPARTY version refusal, shared by every framed decoder.

    Distinct from UNSUPPORTED_VERSION on purpose: "this build cannot read that
    dialect" and "that participant is not on that release" are different facts
    with different repairs -- change the build, or wait for their cutover.
    """
    if version not in record.speaks_schema_versions:
        raise WallProtocolError(
            "VERSION_NOT_SPOKEN",
            f"participant {sender!r} sent schema_version {version}, "
            f"and this build has it on {sorted(record.speaks_schema_versions)} -- "
            "readable by this build, and not this counterparty's current release",
        )


def decode_framed_interim(
    wire: Any,
    *,
    decode_payload: Callable[[Any], IT],
    registry: Mapping[str, CounterpartyRecord] = COUNTERPARTY_REGISTRY,
) -> Tuple[str, WallInterim[IT]]:
    """Parse an interim leg that arrived inside a transport frame, or refuse it.

    TWO INDEPENDENT VERSION REFUSALS STACK HERE, and they catch different
    counterparties. `decode_interim` refuses an interim stamped v1 because that
    RELEASE has no such message; this then refuses one stamped v2 from a sender
    the registry has on v1 only, because that PARTICIPANT has not cut over. The
    first is about the dialect, the second about who is speaking it, and a
    build that could only make the first check would accept an interim from a
    counterparty that cannot produce one.
    """
    sender, record, envelope = _verify_frame(wire, registry)
    interim = decode_interim(envelope, decode_payload=decode_payload)
    _require_sender_speaks(sender, record, interim.schema_version)
    return sender, interim


def decode_framed_notification(
    wire: Any,
    *,
    decode_payload: Callable[[Any], N],
    registry: Mapping[str, CounterpartyRecord] = COUNTERPARTY_REGISTRY,
) -> Tuple[str, WallNotification[N]]:
    """Parse an unsolicited notification that arrived framed, or refuse it.

    A NOTIFICATION NAMES ITS SENDER TWICE -- once in the frame the channel
    asserts, once as a document field -- and the two must agree. They are not
    the same claim: the frame's sender is authenticated against a credential
    fingerprint, the document's is just bytes the message carries so that
    `sequence` remains meaningful once the frame is gone. A mismatch means an
    authenticated participant is relaying another's stream position, which would
    corrupt exactly the per-sender ordering the field exists to support.
    """
    sender, record, envelope = _verify_frame(wire, registry)
    notification = decode_notification(envelope, decode_payload=decode_payload)
    _require_sender_speaks(sender, record, notification.schema_version)
    if notification.sender != sender:
        raise WallProtocolError(
            "SENDER_MISMATCH",
            f"frame is authenticated as {sender!r} and the notification inside "
            f"claims sender {notification.sender!r} -- `sequence` is a position "
            "in ONE counterparty's stream, so a relayed one is not orderable",
        )
    return sender, notification
