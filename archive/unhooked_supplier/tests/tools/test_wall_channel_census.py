# ARCHIVED LEGS of tests/tools/test_wall_channel_census.py (archive increment 3b). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/tools/test_wall_channel_census.py.
"""R15 proof for `tools/wall_channel_census.py` -- the wall's per-channel enumerators.

WHAT IS BEING PROVEN, AND WHY IT NEEDS PROVING. The atom's exit criterion is not "the wall is
clean"; it is "every channel across the wall HAS AN ENUMERATOR" -- the form the 2026-08-15 census
chose precisely because the obvious criterion was unfalsifiable. A criterion of that shape has an
obvious failure mode of its own: an enumerator that returns a plausible set and would return the
same plausible set if the defect it exists to catch were present. So each of the four new
enumerators is shown FIRING on a new member of its own channel, and each is shown TOLERATING a
change to the same tree that is not a new member (the null control -- move the sample, not the
law). Without both directions "it returned a set" is not evidence of anything.

Every mutation is built in a synthetic tree, never by editing the repo, so the proofs are
independent of whatever the live tree happens to hold today.
"""
from __future__ import annotations

import ast
import json
import textwrap
from pathlib import Path

import pytest

from tools import wall_channel_census as wcc

# ── the synthetic tree ───────────────────────────────────────────────────────────────────────

def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")


@pytest.fixture()
def tree(tmp_path: Path) -> Path:
    """A miniature repo carrying exactly one member of each of channels C, D, E and F.

    One member per channel on purpose: with one, "the mutation added a member" and "the
    enumerator found a member it always finds" cannot be confused with each other.
    """
    root = tmp_path / "repo"
    _write(root, "interface/contracts/wall_envelope.py", '"""the envelope."""\n')
    _write(root, "interface/contracts/payment_observable_seam.py", """
        from interface.contracts.wall_envelope import WallRequest
    """)
    # channel C: one business-side importer of a seam.
    _write(root, "company/billing/payment_observation_consumer.py", """
        from interface.contracts.payment_observable_seam import PaymentNotification
    """)
    # channel D: one port and one importer of it.
    _write(root, "tools/meter_read_port.py", '"""a same-step port."""\n')
    _write(root, "simulation/run_phase4c_on_phase2b.py", """
        from tools.meter_read_port import MeterReadMessage
    """)
    # channel E: one business-side structural Protocol.
    _write(root, "company/billing/monthly_bill_assembly.py", """
        from typing import Protocol


        class ReadArrival(Protocol):
            pass
    """)
    # channel F: one business-side literal read of a published key.
    _write(root, "saas/reporting/annual_report.py", """
        def render(phase2b):
            return phase2b["bills"]
    """)
    return root


ARTEFACT = {"bills": [], "meter_read_log": [], "ledger_pnl": {}}


def _census(root: Path, artefact: dict | None = None) -> dict[str, set[str]]:
    return wcc.census(str(root), ARTEFACT if artefact is None else artefact)


def _baseline_of(root: Path, artefact: dict | None = None) -> dict[str, set[str]]:
    """The frozen list, taken from a clean tree. The comparison's other side."""
    current = _census(root, artefact)
    return {cid: set(current[cid]) for cid in wcc.FROZEN_CHANNEL_IDS}


# ── 0. the exit criterion itself ─────────────────────────────────────────────────────────────







# ── 1. each enumerator finds its own channel's member ────────────────────────────────────────





# ── 2. one mutation per channel -- the guard must FIRE ───────────────────────────────────────













# ── 3. the null controls -- move the sample, not the law ─────────────────────────────────────









# ── 4. shrink is the direction that must PASS ────────────────────────────────────────────────



# ── 5. fail-closed -- an unavailable check is a FAILED check ─────────────────────────────────













# ── 6. independence -- the two sides are not one side ────────────────────────────────────────



# ── 7. the live tree -- the enforced ratchet ─────────────────────────────────────────────────





# ── 8. channel D's wire conformance -- is the version actually ON THE WIRE? ───────────────────
# The census above counts who crosses. These cover the question a count cannot ask: a port can be
# a channel-D member, declare `schema_version`, and emit it nowhere. For four days every live call
# site took the `include_schema_version=False` default and channel D's own census could not tell.

PORT_WITH_FLAG = '''
    class MeterReadMessage:
        def to_log_entry(self, include_schema_version: bool = False) -> dict:
            entry = {"customer_id": self.customer_id}
            if include_schema_version:
                entry["schema_version"] = "1.0"
            return entry
'''


@pytest.fixture()
def wire_tree(tmp_path: Path) -> Path:
    """One port that CAN carry a version, and one caller that asks it to."""
    root = tmp_path / "repo"
    _write(root, "tools/meter_read_port.py", PORT_WITH_FLAG)
    _write(root, "simulation/run_phase4c_on_phase2b.py", """
        from tools.meter_read_port import MeterReadMessage

        def run(messages):
            return [m.to_log_entry(include_schema_version=True) for m in messages]
    """)
    return root
























# ── 9. the artefact half -- observation, never a gate ────────────────────────────────────────





# ── 9b. the artefact half's SUBJECT -- which keys are supposed to carry a version ─────────────
#
# `wire_on_artefact` alone cannot state channel D's claim, because "0 of 1600 rows" and "not a
# port log at all" are the same reading on it. These prove the subject is DERIVED from the tree
# and that the derivation is doing work rather than echoing a local variable name -- which the
# three live sites cannot show, since there the name and the published key happen to coincide.

@pytest.fixture()
def publish_tree(tmp_path: Path) -> Path:
    """A caller whose emitted rows land in a local list published under a DIFFERENT key."""
    root = tmp_path / "repo"
    _write(root, "tools/meter_read_port.py", PORT_WITH_FLAG)
    _write(root, "simulation/run_phase4c_on_phase2b.py", """
        from tools.meter_read_port import MeterReadMessage

        def run(messages):
            rows = [m.to_log_entry(include_schema_version=True) for m in messages]
            return {"meter_read_log": rows}
    """)
    return root


ARTEFACT_CARRYING = {"meter_read_log": [{"customer_id": 1, "schema_version": "1.0"}]}
ARTEFACT_SILENT = {"meter_read_log": [{"customer_id": 1}, {"customer_id": 2}]}






















# ── 10. the live tree ────────────────────────────────────────────────────────────────────────





# ── 11. the CALLER refuses, it does not merely print ─────────────────────────────────────────
#
# Section 10 proves the enumerator's verdict is right. That is not the same claim as "a commit
# carrying a silent crossing is refused", and the difference is not hypothetical: this check
# shipped for one commit in a REPORTING branch that printed the same true verdict and returned
# ok. A control whose caller discards its verdict is a control that cannot fail, so the caller
# gets its own mutation.

def _conformant_E() -> wcc.SatisfactionVerdict:
    """Channel E's success case: one Protocol, satisfied by one world class."""
    return wcc.SatisfactionVerdict(
        crossings={"company/b.py -> Feed": ("simulation/w.py::Impl",)}, internal=()
    )


def _conformant_F() -> wcc.NestedSchemaVerdict:
    """Channel F's success case: one read artefact key, publishing two nested field names."""
    return wcc.NestedSchemaVerdict(
        pins={"bills": ("period_end", "total_amount_gbp")}, unread=("private_blob",)
    )


def _pin_the_other_halves(monkeypatch) -> None:
    """Force every half of `_wall_channel_census_check` GREEN except the one under test.

    THE CLASS, stated once rather than re-learned per half: this gate step now runs FIVE checks
    and returns one verdict. Any half left real runs against the fixture's fake index tree
    `"0"*40`, raises, and hits its own fail-closed branch -- so "the gate refused" becomes evidence
    about whichever half happened to fail first, and a NULL CONTROL fails while looking like a
    defect in the half it was pointed at. Callers re-patch the one they are the subject of.

    `check_satisfaction` is left REAL and fed the reading's own crossings as its baseline, so the
    green path exercises the comparison rather than stubbing it out.
    """
    from tools import pre_commit_test_gate as gate

    monkeypatch.setattr(gate, "_index_tree", lambda: "0" * 40)
    monkeypatch.setattr(wcc, "census_at", lambda tree, root: {})
    monkeypatch.setattr(wcc, "load_baseline", lambda *a, **k: {})
    monkeypatch.setattr(wcc, "check", lambda *a, **k: _AlwaysOk())
    monkeypatch.setattr(wcc, "wire_conformance_at", lambda **k: wcc.WireVerdict(
        carrying=["a.py -> 10"], silent=[]
    ))
    monkeypatch.setattr(wcc, "envelope_wire_conformance_at", lambda **k: _conformant_C())
    monkeypatch.setattr(wcc, "structural_satisfaction_at", lambda **k: _conformant_E())
    monkeypatch.setattr(
        wcc, "load_satisfaction_baseline", lambda *a, **k: dict(_conformant_E().crossings)
    )
    monkeypatch.setattr(wcc, "nested_schema_at", lambda **k: _conformant_F())
    monkeypatch.setattr(
        wcc, "load_nested_schema_baseline", lambda *a, **k: dict(_conformant_F().pins)
    )
    # THE FIFTH HALF (2026-08-22 pass 65), pinned in the commit that armed it -- the fourth time
    # this fixture's own docstring has been proved right. Left real, the anchored-read check runs
    # `head_export` against the fake index tree `"0"*40`, raises, hits its own fail-closed branch,
    # and every NULL CONTROL above fails while looking like a defect in the half it was aimed at.
    monkeypatch.setattr(wcc, "anchored_read_conformance_at", lambda **k: _conformant_anchored())
    # THE SIXTH HALF (2026-08-22 pass 67), pinned in the commit that armed it -- the FIFTH time
    # this fixture's own docstring has been proved right, and pass 65 predicted the fourth in the
    # same words. Left real, the authenticated-decode check runs `head_export` against the fake
    # index tree `"0"*40`, raises, hits its own fail-closed branch, and every NULL CONTROL above
    # fails while looking like a defect in the half it was aimed at.
    monkeypatch.setattr(
        wcc, "authenticated_decode_conformance_at", lambda **k: _conformant_authenticated()
    )


def _gate_wire_branch(monkeypatch, *, wire: wcc.WireVerdict):
    """Run `_wall_channel_census_check` with the census and channel-C halves forced GREEN and the
    channel-D wire half forced to `wire`, so the verdict is attributable to that half alone.

    CHANNEL C IS FORCED HERE FOR THE SAME REASON THE CENSUS IS, and it was added when channel C
    armed (2026-08-20 pass 23). Left real, it would run against the fixture's fake index tree
    `"0"*40`, raise, and hit its own fail-closed branch -- at which point the NULL CONTROL below
    would fail while looking like a defect in channel D. Every half of a multi-part step has to be
    pinned for any one of them to be a subject. CHANNEL E was pinned for the same reason when it
    armed (2026-08-20 pass 30) -- the third time this fixture has learned the same lesson, which is
    why `_pin_the_other_halves` now exists rather than a fourth hand-written line.
    """
    from tools import pre_commit_test_gate as gate

    _pin_the_other_halves(monkeypatch)
    monkeypatch.setattr(wcc, "wire_conformance_at", lambda **k: wire)
    monkeypatch.setattr(wcc, "envelope_wire_conformance_at", lambda **k: _conformant_C())
    # The step short-circuits when no Python is staged, so the sample must contain some.
    return gate._wall_channel_census_check(["simulation/anything.py"])


class _AlwaysOk:
    ok = True

    def report(self) -> str:  # pragma: no cover -- only reached if the test itself is wrong
        return "census forced green by the fixture"








# ── 12. STALE ARTEFACT vs BROKEN WIRE -- the reading the report could not make ────────────────
#
# Section 9's two halves disagree at HEAD: the code half green on all three sites, the artefact
# half zero on all 1,996 rows. Pass 17 read that disagreement as proof of independence, which it
# is. What it is ALSO the shape of is a broken wire, and the report had no way to say which -- so
# the atom's own success case and its failure case printed identically. `artefact_provenance`
# separates them by commit order, and the proofs below are about the two ways that could go wrong:
# saying "stale" about everything (which excuses every real defect) and saying "current" when git
# could not actually answer (which convicts on an unread record).

def _git(root: Path, *args: str) -> str:
    import subprocess

    proc = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=True,
    )
    return proc.stdout.strip()


@pytest.fixture()
def git_tree(tmp_path: Path) -> Path:
    """A real repository, because commit ORDER is the subject and no fake can carry it."""
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@example.invalid")
    _git(root, "config", "user.name", "t")
    return root


def _commit(root: Path, rel: str, body: str, message: str) -> str:
    _write(root, rel, body)
    _git(root, "add", "--", rel)
    _git(root, "commit", "-q", "-m", message)
    return _git(root, "rev-parse", "HEAD")


PRODUCER = "simulation/run_phase2b.py"
























# ── 13. channel C's conformance -- does the envelope crossing become a MESSAGE? ───────────────
#
# THE TAUTOLOGY THIS SECTION EXISTS TO AVOID. `WallRequest`/`WallResponse` declare
# `schema_version` as a required field, so "an envelope crossing carries a version" is true by
# dataclass construction and a control asking it would be R15 TAUTOLOGY -- guaranteed by the same
# definition it checks, green on every tree that ever compiles. The falsifiable question is
# whether the envelope is ENCODED into the declared wire form by one side and DECODED back by the
# other, or merely handed across the call frame as a Python object whose version nobody reads.
# Every test below therefore mutates the TRANSPORT and never the field.

CODEC_SOURCE = """
    REQUEST_WIRE_FIELDS = frozenset(
        {"correlation_id", "request_type", "schema_version", "as_of", "emitted_at", "payload"}
    )
    RESPONSE_WIRE_FIELDS = frozenset(
        {"correlation_id", "status", "schema_version", "observed_at", "valid_time",
         "payload", "error"}
    )
    INTERIM_WIRE_FIELDS = frozenset(
        {"correlation_id", "leg", "interim_type", "schema_version", "observed_at", "payload"}
    )
    NOTIFICATION_WIRE_FIELDS = frozenset(
        {"notification_id", "notification_type", "schema_version", "sender", "sequence",
         "observed_at", "valid_time", "payload"}
    )

    def decode_response(message):
        return message

    def decode_request(message):
        return message
"""

#: The counterparty's own encoder: a dict literal whose key set IS `RESPONSE_WIRE_FIELDS`.
WIRE_ENCODER = """
    from interface.contracts.payment_observable_seam import SCHEMA_VERSION

    def encode_wall_response(response):
        return {
            "correlation_id": response.correlation_id,
            "status": response.status.value,
            "schema_version": SCHEMA_VERSION,
            "observed_at": response.observed_at.isoformat(),
            "valid_time": None,
            "payload": None,
            "error": None,
        }
"""

#: The company's decode site: imports the seam AND a decode entry point from the one codec.
WIRE_DECODER = """
    from company.interfaces.wall_protocol import decode_response
    from interface.contracts.payment_observable_seam import PaymentNotification

    def consume(wire):
        return decode_response(wire)
"""


@pytest.fixture()
def envelope_tree(tmp_path: Path) -> Path:
    """One versioned seam that IS wire-borne, and the versionless envelope module beside it.

    One conforming seam on purpose, for the `tree` fixture's reason: with exactly one, "the
    mutation broke the transport" and "the check never found a transport" cannot be confused.
    """
    root = tmp_path / "repo"
    _write(root, "company/interfaces/wall_protocol.py", CODEC_SOURCE)
    _write(root, "interface/contracts/wall_envelope.py", '"""the envelope shape."""\n')
    _write(root, "interface/contracts/payment_observable_seam.py", """
        from interface.contracts.wall_envelope import WallResponse

        SCHEMA_VERSION = 1
    """)
    _write(root, "simulation/payment_seam_adapter.py", WIRE_ENCODER)
    _write(root, "company/billing/payment_observation_consumer.py", WIRE_DECODER)
    return root


PAYMENT_SEAM = "interface.contracts.payment_observable_seam"








































# ── 14. the live tree -- the reading, and deliberately not the answer ─────────────────────────





# ── 15. channel C, PER LEG -- the seam is not the unit, the crossing is ───────────────────────
#
# WHY THE SEAM WAS THE WRONG UNIT. A seam resolves in two crossings separated in time: the company
# EMITS a `WallRequest` and later OBSERVES a `WallResponse`. Section 13 credited a seam as
# wire-borne on any one encoder and any one decoder ANYWHERE among its importers, so a seam with a
# wired response and a request still crossing the call frame read exactly like a seam with both
# wired. That is the atom's own defect surviving on the leg the instrument could not see, and it is
# what every mutation below moves.
#
# THE TWO DETECTION SHAPES PER SIDE are the other half of this section, and they are not a
# convenience. The wall FORBIDS the counterparty to import `company.*`, so it cannot use the
# company's codec and must mirror the contract's key set instead; the company owns that codec and
# calls it rather than hand-building bytes. A detector that knows only one shape per side red-lists
# a leg for being written the way the wall requires -- which is a false alarm on the architecture's
# own correct answer, and the most expensive kind, because the repair it invites is to break the
# wall.

TWO_LEG_SEAM = "interface.contracts.conversation_seam"

#: A seam declaring BOTH legs, each carrying a distinct payload type.
TWO_LEG_SEAM_SOURCE = """
    from interface.contracts.wall_envelope import WallRequest, WallResponse

    SCHEMA_VERSION = 1

    class OutboundMessage:
        pass

    class InboundReply:
        pass

    MessageWallRequest = WallRequest[OutboundMessage]
    ReplyWallResponse = WallResponse[InboundReply]
"""

#: The company end. Encodes the REQUEST through its own codec (the only lawful company shape) and
#: decodes the RESPONSE through the same codec. Constructs both payloads, so neither leg is dormant.
TWO_LEG_COMPANY = """
    from company.interfaces.wall_protocol import decode_response, encode_request
    from interface.contracts.conversation_seam import InboundReply, OutboundMessage

    def send(body, emitted_at):
        return encode_request(OutboundMessage(), emitted_at)

    def observe(wire):
        reply = InboundReply()
        return decode_response(wire), reply
"""

#: The counterparty end. May not import `company.*`: it mirrors the REQUEST key set to refuse
#: against, and hand-builds the RESPONSE dict.
TWO_LEG_WORLD = """
    from interface.contracts.conversation_seam import SCHEMA_VERSION

    _REQUEST_WIRE_FIELDS = frozenset(
        {"correlation_id", "request_type", "schema_version", "as_of", "emitted_at", "payload"}
    )

    def decode_wire_request(wire):
        if set(wire) != _REQUEST_WIRE_FIELDS:
            raise ValueError("refused")
        return wire

    def respond_over_wire(request):
        return {
            "correlation_id": request["correlation_id"],
            "status": "OK",
            "schema_version": SCHEMA_VERSION,
            "observed_at": None,
            "valid_time": None,
            "payload": None,
            "error": None,
        }
"""


@pytest.fixture()
def two_leg_tree(envelope_tree: Path) -> Path:
    """A second seam beside the payment one, fully wired on BOTH legs.

    Built as the conforming case on purpose: every mutation below removes exactly one leg's
    transport, so "the mutation broke this leg" can never be confused with "the check never found
    a transport at all" -- section 13's fixture reason, applied one level down.
    """
    _write(envelope_tree, "interface/contracts/conversation_seam.py", TWO_LEG_SEAM_SOURCE)
    _write(envelope_tree, "company/comms/conversation_generator.py", TWO_LEG_COMPANY)
    _write(envelope_tree, "simulation/conversation_response.py", TWO_LEG_WORLD)
    return envelope_tree




























# ── 15b. the wall has FOUR legs, and the census used to score two ─────────────────────────────
#
# THE FINDING THIS SECTION DISCHARGES (2026-08-21, "the wall census scores two legs of a four-leg
# wall"). `LEG_ENVELOPE_NAMES` carried two keys while `wall_envelope` had declared four primitives
# since pass 44, and `payment_observable_seam` had ALREADY made the declaration that table reads
# for both of the missing ones -- `AddacsWallNotification`, `BacsInputReportWallInterim`. Both
# resolved to None, and the crossing was dropped at `seam_legs` before any per-leg verdict formed.
#
# THE FAILURE MODE IS THE ONE THIS WHOLE FILE IS ABOUT, one level up from section 15's: not a leg
# scored wrong, but a leg OUTSIDE THE SUBJECT SET, which cannot be reported missing from it. The
# census ended `every frozen channel matches its list exactly` while answering for half the wall.
# So the tests below are not "does an interim leg pass" -- they are "can an interim leg FAIL",
# which is the only question a widened subject set actually settles.

FOUR_LEG_SEAM = "interface.contracts.conversation_seam"

#: The same seam as section 15, grown the two legs the wall gained at passes 43 and 44. Each leg
#: carries a DISTINCT payload type, so a leg's verdict can never be borrowed from its neighbour.
FOUR_LEG_SEAM_SOURCE = """
    from interface.contracts.wall_envelope import (
        WallInterim, WallNotification, WallRequest, WallResponse,
    )

    SCHEMA_VERSION = 1

    class OutboundMessage:
        pass

    class InboundReply:
        pass

    class ProgressNote:
        pass

    class UnsolicitedTell:
        pass

    MessageWallRequest = WallRequest[OutboundMessage]
    ReplyWallResponse = WallResponse[InboundReply]
    ProgressWallInterim = WallInterim[ProgressNote]
    TellWallNotification = WallNotification[UnsolicitedTell]
"""

#: The company end: decodes all four legs through the one codec it is allowed to own, and
#: constructs every payload type so no leg is scored dormant.
FOUR_LEG_COMPANY = """
    from company.interfaces.wall_protocol import (
        decode_interim, decode_notification, decode_response, encode_request,
    )
    from interface.contracts.conversation_seam import (
        InboundReply, OutboundMessage, ProgressNote, UnsolicitedTell,
    )

    def send(body, emitted_at):
        return encode_request(OutboundMessage(), emitted_at)

    def observe(wire):
        reply = InboundReply()
        return decode_response(wire), reply

    def observe_progress(wire):
        note = ProgressNote()
        return decode_interim(wire), note

    def observe_tell(wire):
        tell = UnsolicitedTell()
        return decode_notification(wire), tell
"""

#: The counterparty end: may not import `company.*`, so it hand-builds each leg's exact key set --
#: the same shape `simulation/payment_seam_adapter.py` really uses for both new legs.
FOUR_LEG_WORLD = """
    from interface.contracts.conversation_seam import SCHEMA_VERSION

    _REQUEST_WIRE_FIELDS = frozenset(
        {"correlation_id", "request_type", "schema_version", "as_of", "emitted_at", "payload"}
    )

    def decode_wire_request(wire):
        if set(wire) != _REQUEST_WIRE_FIELDS:
            raise ValueError("refused")
        return wire

    def respond_over_wire(request):
        return {
            "correlation_id": request["correlation_id"],
            "status": "OK",
            "schema_version": SCHEMA_VERSION,
            "observed_at": None,
            "valid_time": None,
            "payload": None,
            "error": None,
        }

    def interim_over_wire(request):
        return {
            "correlation_id": request["correlation_id"],
            "leg": "collection",
            "interim_type": "input_report",
            "schema_version": SCHEMA_VERSION,
            "observed_at": None,
            "payload": None,
        }

    def notify_over_wire():
        return {
            "notification_id": "n-1",
            "notification_type": "addacs",
            "schema_version": SCHEMA_VERSION,
            "sender": "world",
            "sequence": 1,
            "observed_at": None,
            "valid_time": None,
            "payload": None,
        }
"""


@pytest.fixture()
def four_leg_tree(envelope_tree: Path) -> Path:
    """A seam wired on all FOUR legs -- the null control every mutation below is measured against."""
    _write(envelope_tree, "interface/contracts/conversation_seam.py", FOUR_LEG_SEAM_SOURCE)
    _write(envelope_tree, "company/comms/conversation_generator.py", FOUR_LEG_COMPANY)
    _write(envelope_tree, "simulation/conversation_response.py", FOUR_LEG_WORLD)
    return envelope_tree














# ── 16. the CALLER refuses on channel C too -- arming the gate ────────────────────────────────
#
# Section 11 made this argument for channel D and it applies here unchanged: a control whose
# caller discards its verdict is a control that cannot fail. Channel C reported for four passes
# (19-22) while `_wall_channel_census_check` returned ok on every tree it convicted, and pass 22
# recorded that as a debt with a name rather than a decision -- "a met condition sitting un-armed
# is itself a control that cannot fail". These are the proofs that the arming is real.
#
# WHY IT COULD ONLY BE ARMED HERE. Pass 19 wrote the condition: channel C "becomes a gate in the
# same commit that makes it satisfiable, which is the only commit in which restoring it is
# honest". Before pass 22 at least one seam was IN-PROCESS at HEAD, so arming would have refused
# every commit in the repo, the publisher's included -- the landing-order defect that cost channel
# D passes 12-14. Measured at HEAD before this section was written: `ok=True`, `3 of 3`, in-process
# empty.
#
# THE MUTATIONS MOVE THE VERDICT AND NOTHING ELSE. Both other halves of the step (the census, and
# channel D's wire) are forced green by the fixture, so a refusal is attributable to channel C
# alone -- otherwise "the gate said no" would be evidence about whichever half happened to fail.

def _gate_envelope_branch(monkeypatch, *, envelope: wcc.EnvelopeWireVerdict):
    """Run `_wall_channel_census_check` with the census and channel-D halves forced GREEN and
    channel C forced to `envelope`, so the returned verdict is attributable to channel C alone."""
    from tools import pre_commit_test_gate as gate

    _pin_the_other_halves(monkeypatch)
    monkeypatch.setattr(wcc, "envelope_wire_conformance_at", lambda **k: envelope)
    # The step short-circuits when no Python is staged, so the sample must contain some.
    return gate._wall_channel_census_check(["simulation/anything.py"])


def _conformant_C(**kw) -> wcc.EnvelopeWireVerdict:
    """The success case: one seam, both legs on the wire. Every mutation below is this, moved."""
    return wcc.EnvelopeWireVerdict(
        wire_borne=["interface.contracts.conversation_seam"],
        half_wired=[], in_process=[], unversioned=[],
        leg_states=(
            ("interface.contracts.conversation_seam", "request", "wire"),
            ("interface.contracts.conversation_seam", "response", "wire"),
        ),
        **kw,
    )


















# ── channel C's second question: does a version still MEAN what it meant? ────────────────────
# Channel C's transport check reads 3 of 3 at HEAD. These tests are about the question that
# saturation exposes rather than answers: `SCHEMA_VERSION` is encoded into every envelope and
# REFUSED on mismatch by each decoder, so a version whose meaning moves silently makes the
# counterparty's check pass on a wrong assumption. Every mutation below leaves the version
# EXACTLY where it was -- that is the point, and it is what a version-presence check cannot see.

#: The digest of `pin_tree`'s unmutated surface, WRITTEN OUT rather than computed at fixture
#: time. A pin derived from the declaration it pins moves with its subject; the null control
#: below is what proves this literal and that declaration actually correspond.
PIN_TREE_DIGEST = "b3845700e7bd5b2d"

PIN_SEAM = "interface.contracts.payment_observable_seam"


@pytest.fixture()
def pin_tree(tmp_path: Path) -> Path:
    """One versioned seam declaring a literal observable surface, plus the versionless envelope.

    One pinned seam on purpose, the `tree` fixture's reason: with exactly one, "the mutation
    moved the surface" and "the check never found a surface" cannot be confused.
    """
    root = tmp_path / "repo"
    _write(root, "interface/contracts/wall_envelope.py", '"""the envelope shape."""\n')
    _write(root, "interface/contracts/payment_observable_seam.py", """
        from interface.contracts.wall_envelope import WallResponse

        SCHEMA_VERSION = 1

        OBSERVABLE_PAYLOAD_FIELDS: dict[str, tuple[str, ...]] = {
            "PaymentNotification": (
                "notification_id",
                "amount_gbp",
                "received_on",
            ),
        }
    """)
    _write(root, "simulation/payment_seam_adapter.py", """
        from interface.contracts.payment_observable_seam import SCHEMA_VERSION

        def emit(response):
            return [response]
    """)
    _write(root, "company/billing/payment_observation_consumer.py", """
        from interface.contracts.payment_observable_seam import PaymentNotification

        def consume(response):
            return response.payload
    """)
    return root


@pytest.fixture()
def pinned(monkeypatch) -> None:
    """Pin `pin_tree`'s seam at v1, so the mutations below face a pin written BEFORE them."""
    monkeypatch.setattr(wcc, "SURFACE_PINS", {PIN_SEAM: (1, PIN_TREE_DIGEST)})


























# ── channel C, the SECOND BELT: is there anything behind the closed set? ──────────────────────
# WHY THIS BATTERY EXISTS. Pass 26 found, by reading three files side by side, that one of the
# three seams had no `FORBIDDEN_TRUTH_FIELDS` at all. Nothing could have failed: the belt is a
# per-seam convention, and a convention is exactly what a fourth seam lands without. This asks
# the question in the INSTRUMENT, where it can fail on the day the hole arrives (R10 -- the
# class fails, not the instance somebody happened to notice).
#
# The mutations below leave the closed set and the version EXACTLY where they are. That is the
# point: every one of them is green to the surface pins and green to the wire check, because
# those ask different questions, and a seam can satisfy both while carrying no second belt.

BELT_SEAM = "interface.contracts.payment_observable_seam"


def _belt_seam_source(belt: str = '("result", "ability")') -> str:
    return f"""
        from interface.contracts.wall_envelope import WallResponse

        SCHEMA_VERSION = 1

        OBSERVABLE_PAYLOAD_FIELDS: dict[str, tuple[str, ...]] = {{
            "PaymentNotification": ("notification_id", "amount_gbp"),
        }}

        FORBIDDEN_TRUTH_FIELDS: tuple[str, ...] = {belt}
    """


_ENFORCING_ADAPTER = """
    from interface.contracts.payment_observable_seam import FORBIDDEN_TRUTH_FIELDS

    def encode(payload, names):
        leaking = sorted(set(names) & set(FORBIDDEN_TRUTH_FIELDS))
        if leaking:
            raise ValueError(leaking)
        return payload
"""

# The COMPANY side of the same crossing. Byte-for-byte a different module on the other side of
# the wall, not a copy of the adapter renamed: the whole question below is which SIDE a refusal
# sits on, so the two sides have to be separately removable.
_ENFORCING_CONSUMER = """
    from interface.contracts.payment_observable_seam import FORBIDDEN_TRUTH_FIELDS

    def decode(body):
        leaking = sorted(set(body) & set(FORBIDDEN_TRUTH_FIELDS))
        if leaking:
            raise ValueError(leaking)
        return body
"""

_ADAPTER_REL = "simulation/payment_seam_adapter.py"
_CONSUMER_REL = "company/billing/payment_observation_consumer.py"

# A module that refuses on the belt and is on NEITHER side -- `tools` is a BRIDGE package,
# walked by the census because channel D's ports live there. Used to pin that a bridge refusal
# does not redeem a bare side.
_ENFORCING_BRIDGE = """
    from interface.contracts.payment_observable_seam import FORBIDDEN_TRUTH_FIELDS

    def audit(names):
        if set(names) & set(FORBIDDEN_TRUTH_FIELDS):
            raise ValueError(names)
"""


@pytest.fixture()
def belt_tree(tmp_path: Path) -> Path:
    """One versioned seam declaring a literal denylist, refused on by BOTH SIDES of the wall.

    One seam on purpose, the `pin_tree` fixture's reason: with exactly one, "the mutation
    removed the belt" and "the check never found a seam" cannot be confused. TWO enforcers on
    purpose, one per side of the wall -- the green case has to be the state the real tree is
    actually required to be in, or every mutation below would be measured against a fixture that
    was already failing.
    """
    root = tmp_path / "repo"
    _write(root, "interface/contracts/wall_envelope.py", '"""the envelope shape."""\n')
    _write(root, "interface/contracts/payment_observable_seam.py", _belt_seam_source())
    _write(root, _ADAPTER_REL, _ENFORCING_ADAPTER)
    _write(root, _CONSUMER_REL, _ENFORCING_CONSUMER)
    return root














_INERT_CODEC = """
    from interface.contracts.payment_observable_seam import FORBIDDEN_TRUTH_FIELDS

    KNOWN_LEAKS = FORBIDDEN_TRUTH_FIELDS

    def crosses(payload, names):
        return payload
"""




# ── the PER-SIDE question (EP6 pass 28) ────────────────────────────────────────────────────────
# WHY THIS EXISTS AS ITS OWN BATTERY. The per-seam verdict above is satisfied by ONE enforcer
# anywhere, and on its first live run it REPORTED -- in its enforcer list, where nothing could
# fail on it -- that `conversation_seam` was belted by `simulation/conversation_response.py`
# alone. That is the seam carrying a customer's hidden latent traits, defended on the side the
# WORLD owns and bare on the side the COMPANY owns. A fact that can only be read off a list is
# not a control; these are the mutations that make it one.
#
# BOTH DIRECTIONS ARE MUTATED ON PURPOSE. With only the company-side removal, "one-sided"
# would be indistinguishable from "that particular fixture file went missing", and the check
# could be keyed on the wrong thing entirely while passing.
#
# SIDE IS NOT LEG. This file already uses "leg" for the request/response pair a seam owns
# (`seam_legs`). The axis below is which SIDE OF THE WALL a refusal sits on -- a seam can be
# wired on both legs and belted on one side, which is precisely the state pass 27 reported.
























# ── channel E's conformance: does a WORLD class actually satisfy the Protocol? ───────────────
#
# WHY THIS SECTION EXISTS (2026-08-20, pass 30). `enumerate_e` above answers a WIDTH -- how many
# business-side Protocols are declared. The census module's own docstring names the limitation
# that leaves: "Channel E's list is a SUPERSET ... not only those a world object satisfies." So
# the width cannot tell a real wall crossing from a company-internal interface, and it is blind to
# the failure mode SPECIFIC to structural typing: neither side declares the other, so a world-side
# class that drifts out of shape breaks NOTHING at import time. There is no `implements` clause to
# go stale, no envelope to fail decoding, no version to mismatch. Channels C and D cannot fail
# this way, which is why E needed its own question rather than a copy of theirs.
#
# The mutations below were each run first against a probe tree built from `git archive HEAD` --
# they are transcriptions of observed reds, not predictions of them.

@pytest.fixture()
def protocol_tree(tmp_path: Path) -> Path:
    """A miniature repo with ONE business-side Protocol and ONE world class satisfying it.

    Deliberately NOT the `tree` fixture above, whose `ReadArrival` is `pass` -- a memberless
    Protocol is refused by this control on purpose (see the vacuity test), so the width fixture
    cannot double as this one.
    """
    root = tmp_path / "repo"
    _write(root, "company/billing/monthly_bill_assembly.py", """
        from typing import Protocol


        class ReadArrival(Protocol):
            status: str
            consecutive_estimated_count: int
    """)
    _write(root, "simulation/meter_reads.py", """
        class MeterReadEvent:
            customer_id: str
            status: str
            consecutive_estimated_count: int
    """)
    return root


def _satisfaction_baseline(root: Path) -> dict[str, tuple[str, ...]]:
    return dict(wcc.structural_satisfaction(str(root)).crossings)


























# ── the GATE's channel-E branch ──────────────────────────────────────────────────────────────
#
# A CHECK THAT REPORTS IS NOT A GATE (R11, no orphan transitions). The CLI exit-code test above
# proves the reading reaches `main`'s return; this proves it reaches the thing that actually runs
# on every commit. The distinction is not academic here -- nobody types the CLI, and channel C
# spent passes 19-22 green in the tool and unarmed in the gate.
#
# THE MUTATIONS MOVE THE VERDICT AND NOTHING ELSE: the other three halves are forced green by
# `_pin_the_other_halves`, so a refusal is attributable to channel E alone.

def _gate_satisfaction_branch(monkeypatch, *, verdict, baseline):
    from tools import pre_commit_test_gate as gate

    _pin_the_other_halves(monkeypatch)
    monkeypatch.setattr(wcc, "structural_satisfaction_at", lambda **k: verdict)
    monkeypatch.setattr(wcc, "load_satisfaction_baseline", lambda *a, **k: baseline)
    return gate._wall_channel_census_check(["simulation/anything.py"])












# ── channel F's conformance: the nested surface under a read key ─────────────────────────────
#
# WHAT IS BEING PROVEN. `enumerate_f`'s unit is the (TOP-LEVEL key, business reader) pair -- a
# WIDTH, and channel F's only control before this. The blindness it carries was MEASURED on the
# live artefact before any of this was written: 93 top-level keys hide 693 distinct NESTED field
# names, and every ground-truth-shaped field that actually reaches the business side sits at
# depth >= 1 -- `true_consumption_kwh`, `true_commodity_amount_gbp` and `true_total_amount_gbp`
# read by `company/billing/monthly_bill_assembly.py`. Adding one moves NOTHING in the width.
#
# THE TWO NULL CONTROLS ARE THE POINT, and they are what this control's first cut failed. A pin
# over nested key names reds on population churn, because several published blobs are dicts keyed
# by customer id. A control that reds on ordinary work gets relaxed and takes the real reds with
# it. `_is_id_map` is what separates DATA keys from SCHEMA keys, and M6 is what proves it.

def _artefact() -> dict:
    """A miniature published artefact: one read blob, one map keyed by customer, one unread key."""
    return {
        "bills": [
            {"period_end": "2024-01-31", "total_amount_gbp": 42.0},
            {"period_end": "2024-02-29", "total_amount_gbp": 44.0},
        ],
        "clv_snapshots": {
            "C1": {"clv_gbp": 100.0, "as_of": "2024-01"},
            "C2": {"clv_gbp": 120.0, "as_of": "2024-01"},
        },
        "private_blob": {"nobody_reads_me": 1},
    }


def _readers() -> set[str]:
    """Channel F's width: `bills` and `clv_snapshots` are read business-side, `private_blob` not."""
    return {"bills -> saas/reporting/annual_report.py", "clv_snapshots -> company/portal/app.py"}


def _frozen(artefact: dict | None = None) -> dict[str, tuple[str, ...]]:
    return dict(wcc.nested_schema(artefact or _artefact(), _readers()).pins)








































# ── the GATE's channel-F branch ──────────────────────────────────────────────────────────────

def _gate_nested_branch(monkeypatch, *, verdict, baseline):
    from tools import pre_commit_test_gate as gate

    _pin_the_other_halves(monkeypatch)
    monkeypatch.setattr(wcc, "nested_schema_at", lambda **k: verdict)
    monkeypatch.setattr(wcc, "load_nested_schema_baseline", lambda *a, **k: baseline)
    return gate._wall_channel_census_check(["simulation/anything.py"])














# ── 22. channel C, per CONVERSATION -- does the exchange the seam declares happen? ────────────
#
# WHY THIS SECTION EXISTS (2026-08-20, pass 34). Section 15's fixture already contains the defect
# and section 15's own test asserts it passes: `test_a_DORMANT_leg_is_neither_wired_nor_unwired`
# leaves the request leg dormant and then asserts `TWO_LEG_SEAM in verdict.wire_borne`. That is
# the transport question being honest about its scope -- and it is also the exact reading the
# cold-eyes walk of pass 33 called out, having named the failure shape from five sentences of
# plain words before seeing any code: "'We model it as a response to a synthetic request' is a
# fail."
#
# So every mutation below is measured against the SAME fixture section 15 uses, and the pairing is
# the point: where section 15 asserts `wire_borne`, this section asserts RED on the same tree. Two
# controls, one subject, opposite verdicts, because they are asking different questions -- which is
# the only honest way to add a question to an instrument that is already saturated at 3 of 3.












NOTIFY_ONLY_SEAM = "interface.contracts.registration_loss_seam"


def _notify_only_tree(root: Path, *, sent: bool) -> Path:
    """A notification-only seam beside the two-leg one; `sent` says whether anybody builds it."""
    _write(root, "interface/contracts/registration_loss_seam.py", """
        from interface.contracts.wall_envelope import WallNotification

        SCHEMA_VERSION = 2

        class LossNotice:
            pass

        LossWallNotification = WallNotification[LossNotice]
    """)
    _write(root, "simulation/registration_loss_feed.py", """
        from interface.contracts.registration_loss_seam import LossNotice

        def emit():
            return LossNotice()
    """ if sent else """
        from interface.contracts.registration_loss_seam import LossNotice

        def is_loss(x):
            return isinstance(x, LossNotice)
    """)
    return root
















# ── 22b. the live reading -- RED, and recorded as the L3 blocker it is ────────────────────────






# ── 23. channel C, per STATUS -- does the vocabulary the wall declares have speakers? ─────────
#
# WHY THIS SECTION EXISTS (2026-08-20, pass 35). Passes 33 and 34 both closed carrying the same
# named L3 blocker in the same words: "give `WallStatus.TIMEOUT` a reader or delete it". Counting
# the producers instead of imagining them says that framing is one step off, and in exactly the
# way pass 33's prose was one step off from what pass 34 found in the code.
#
# TIMEOUT HAS NO WRITER EITHER, so "give it a reader" is a build item for a message this wall
# cannot send -- a dead arm on arrival. And `ERROR` is in the identical state and was named by
# nobody, across three passes looking straight at it: the miss sitting next to the hit, which is
# this atom's OWN recorded class from pass 29 (`nudge_uplift` named, `tone_uplift` missed, four
# lines apart). Two instances make it a class worth a control rather than a third careful reading.
#
# The green case is REACHABLE on the fixture below, which matters because the live tree is red at
# 1 of 4: a control that has only ever said no is indistinguishable from one that can only say no.


STATUS_ENVELOPE = "interface/contracts/wall_envelope.py"


@pytest.fixture()
def status_tree(tmp_path: Path) -> Path:
    """A wall whose two-member vocabulary is fully inhabited -- both members said AND acted on.

    TWO members and not four, for the `tree` fixture's reason: with a vocabulary this small,
    "the mutation killed a member" and "the check never saw that member" cannot be confused. The
    live enum's other two members arrive in the tests that are ABOUT arriving members.
    """
    root = tmp_path / "repo"
    _write(root, STATUS_ENVELOPE, """
        from enum import Enum

        class WallStatus(str, Enum):
            OK = "OK"
            TIMEOUT = "TIMEOUT"

        class WallResponse:
            def __post_init__(self):
                if self.status == WallStatus.OK and self.payload is None:
                    raise ValueError("OK must carry a payload")
    """)
    _write(root, "simulation/payment_seam_adapter.py", """
        from interface.contracts.wall_envelope import WallResponse, WallStatus

        def emit(fact, deadline_passed):
            if deadline_passed:
                return WallResponse(status=WallStatus.TIMEOUT, payload=None)
            return WallResponse(status=WallStatus.OK, payload=fact)
    """)
    _write(root, "company/billing/payment_observation_consumer.py", """
        from interface.contracts.wall_envelope import WallStatus

        def observe(response):
            if response.status == WallStatus.TIMEOUT:
                return "last known value, flagged stale"
            if response.status == WallStatus.OK:
                return response.payload
            return None
    """)
    return root


























# ── 23b. the live reading -- RED at 2 of 4, and recorded as the L3 blocker it is ───────────────








# ── 26. the ANCHORED READ -- a company-side feed read that never asks its own book ────────────
#
# WHY THIS SECTION EXISTS (2026-08-22, EP6 pass 65). Pass 64 landed the flex feeds' third belt:
# `FlexEnrolmentBook.observe_feed` runs the transport read and then admits the payload against the
# registrations this company HOLDS. The belt is proven. What was left owed, in pass 64's own
# closing paragraph, is that nothing refuses the NEXT reader: "a reader that called
# `observe_response_wire` directly would be unanchored again, and nothing refuses that.
# `tools.wall_channel_census` classifies whole FILES and cannot see it."
#
# So every mutation below is a NEW CALL SITE or a MOVED ONE in a tree where nothing else changes:
# no import edge moves, no envelope is bypassed, no version mismatches, and every other control in
# this file stays green on all of them. That invariance is the point -- it is what makes the call
# site the only unit that can express this question.

FLEX_REL = "company/market/flex_participation.py"
COS_REL = "company/crm/cos_process.py"

#: The second ANCHORED_FEEDS row in miniature, so every fixture below runs over both rows.
_COS_MODULE = """
    from company.interfaces.wall_protocol import decode_framed_notification


    def read_loss_wire(wire):
        sender, notification = decode_framed_notification(wire, decode_payload=_payload)
        return notification


    class CoSRegister:
        def _admit_loss(self, notification):
            return self._holds(notification.payload.supply_point_id)

        def receive_loss_wire(self, wire):
            notification = read_loss_wire(wire)
            if not self._admit_loss(notification):
                return False
            return True
"""

PSR_REL = "company/regulatory/priority_services_register.py"

#: The third ANCHORED_FEEDS row in miniature (2026-10-08), same shape as the second.
_PSR_MODULE = """
    from company.interfaces.wall_protocol import decode_framed_notification


    def read_registration_wire(wire):
        sender, notification = decode_framed_notification(wire, decode_payload=_payload)
        return notification


    class PriorityServicesRegister:
        def _admit(self, notification):
            return self._holds(notification.payload.supply_point_id)

        def receive_registration_wire(self, wire):
            notification = read_registration_wire(wire)
            if not self._admit(notification):
                return None
            return notification
"""

MOVE_REL = "company/crm/move_out_register.py"

#: The fourth ANCHORED_FEEDS row in miniature (2026-10-10), the PSR row's shape.
_MOVE_MODULE = """
    from company.interfaces.wall_protocol import decode_framed_notification


    def read_move_out_wire(wire):
        sender, notification = decode_framed_notification(wire, decode_payload=_payload)
        return notification


    class MoveOutRegister:
        def _admit(self, notification):
            return self._holds(notification.payload.supply_point_id)

        def receive_move_out_wire(self, wire):
            notification = read_move_out_wire(wire)
            if not self._admit(notification):
                return None
            return notification
"""

_FLEX_MODULE = """
    from company.interfaces.wall_protocol import decode_framed_response


    def observe_response_wire(wire, *, expect=None):
        sender, response = decode_framed_response(wire, decode_payload=_payload)
        return response.payload


    def observe_settlement_wire(messages):
        return [observe_response_wire(m, expect=Line) for m in messages]


    class FlexEnrolmentBook:
        def held_registrations(self):
            return self._held

        def _admit(self, payload):
            for held in self.held_registrations():
                if held.unit_id == payload.unit_id:
                    return payload
            raise UnheldRegistration("names no registration this company holds")

        def observe_feed(self, wire, *, expect=None):
            return self._admit(observe_response_wire(wire, expect=expect))

        def observe_settlement_feed(self, messages):
            return [self.observe_feed(m, expect=Line) for m in messages]
"""


@pytest.fixture()
def flex_tree(tmp_path: Path) -> Path:
    """A miniature repo carrying the pass-64 shape: two bookless module-level readers, one book,
    one anchoring method, and one honest outside consumer that goes through the book.

    The outside consumer is in the fixture rather than in a mutation on purpose -- without it,
    "the control reds on an outside caller" and "the control reds on any caller it has not seen
    before" are the same experiment.
    """
    root = tmp_path / "repo"
    _write(root, FLEX_REL, _FLEX_MODULE)
    _write(root, COS_REL, _COS_MODULE)
    _write(root, PSR_REL, _PSR_MODULE)
    _write(root, MOVE_REL, _MOVE_MODULE)
    _write(root, "company/interfaces/wall_protocol.py", """
        def decode_framed_response(wire, *, decode_payload):
            return "sender", wire
    """)
    _write(root, "background/flex_dispatch_triad.py", """
        from company.market.flex_participation import FlexEnrolmentBook


        def measure_l2(book: FlexEnrolmentBook, feed):
            return book.observe_settlement_feed(feed)
    """)
    return root


def _verdict(root: Path) -> "wcc.AnchoredReadVerdict":
    return wcc.anchored_read_conformance(str(root))








































# ── the GATE's anchored-read branch ──────────────────────────────────────────────────────────

def _gate_anchored_branch(monkeypatch, *, verdict):
    from tools import pre_commit_test_gate as gate

    _pin_the_other_halves(monkeypatch)
    monkeypatch.setattr(wcc, "anchored_read_conformance_at", lambda **k: verdict)
    return gate._wall_channel_census_check(["company/market/flex_participation.py"])


def _conformant_anchored() -> "wcc.AnchoredReadVerdict":
    return wcc.AnchoredReadVerdict(
        anchored=[f"{FLEX_REL}:1061 -> FlexEnrolmentBook.observe_feed -> observe_response_wire"],
        unanchored=[],
        readers=("observe_response_wire",),
        unbooked=(),
    )










# ── 27. the AUTHENTICATED DECODE -- a business read that never asks WHO sent this ─────────────
#
# WHY THIS SECTION EXISTS (2026-08-22, EP6 pass 67). Section 26 above asks whether a company-side
# read of a BOOKED feed goes through the book. This asks the question one layer below it, and the
# two are independent: a read can be perfectly booked and still have decoded a document from a
# process this company has never heard of, because a book admits a PAYLOAD and a frame
# authenticates a SENDER.
#
# THE BLINDNESS IS STRUCTURAL AND IT IS THIS FILE'S OWN. `LEG_DECODE_NAME` holds both spellings of
# each decoder in one tuple because pass 39 proved a single-name match reads a rename as a
# deletion. From that commit `decode_response` and `decode_framed_response` were the same decode
# to channel C -- and one of them authenticates. So every mutation below MOVES A CALL SITE BETWEEN
# THE TWO SPELLINGS in a tree where nothing else changes: same module, same leg, same version,
# same import edge. Every other control in this file stays green through all of them.

_AUTH_CODEC = """
    def _verify_frame(wire, registry):
        return wire["sender"], registry[wire["sender"]], wire["envelope"], wire["handed_over_at"]


    def decode_response(wire, *, decode_payload):
        return decode_payload(wire["payload"])


    def decode_framed_response(wire, *, decode_payload, registry=None):
        sender, _record, envelope, _at = _verify_frame(wire, registry or {})
        return sender, decode_response(envelope, decode_payload=decode_payload)


    def decode_request(wire, *, decode_payload):
        return decode_payload(wire["payload"])


    def decode_interim(wire, *, decode_payload):
        return decode_payload(wire["payload"])


    def decode_framed_interim(wire, *, decode_payload, registry=None):
        sender, _record, envelope, _at = _verify_frame(wire, registry or {})
        return sender, decode_interim(envelope, decode_payload=decode_payload)


    def decode_notification(wire, *, decode_payload):
        return decode_payload(wire["payload"])


    def decode_framed_notification(wire, *, decode_payload, registry=None):
        sender, _record, envelope, _at = _verify_frame(wire, registry or {})
        return sender, decode_notification(envelope, decode_payload=decode_payload)
"""


@pytest.fixture()
def auth_tree(tmp_path: Path) -> Path:
    """A miniature repo whose codec has both spellings of every decoder, and one honest business
    reader that takes the framed one.

    The honest reader is in the FIXTURE and not in a mutation, for the reason `flex_tree` gives:
    without it, "the control reds on a bare call" and "the control reds on any call it has not
    seen" would be the same experiment.
    """
    root = tmp_path / "repo"
    _write(root, wcc.CODEC_REL, _AUTH_CODEC)
    _write(root, "company/billing/honest_consumer.py", """
        from company.interfaces.wall_protocol import decode_framed_response


        def observe_wire(wire):
            sender, response = decode_framed_response(wire, decode_payload=dict)
            return response
    """)
    return root


def _auth(root: Path) -> "wcc.AuthenticatedDecodeVerdict":
    return wcc.authenticated_decode_conformance(str(root))




































# ── the GATE's authenticated-decode branch ───────────────────────────────────────────────────

def _conformant_authenticated() -> "wcc.AuthenticatedDecodeVerdict":
    return wcc.AuthenticatedDecodeVerdict(
        authenticated=["company/billing/x.py:1 -> observe_wire -> decode_framed_response"],
        unauthenticated=[],
        framed=("decode_framed_response",),
        bare=("decode_response",),
    )


def _gate_authenticated_branch(monkeypatch, *, verdict):
    from tools import pre_commit_test_gate as gate

    _pin_the_other_halves(monkeypatch)
    monkeypatch.setattr(wcc, "authenticated_decode_conformance_at", lambda **k: verdict)
    return gate._wall_channel_census_check(["company/comms/susceptibility_estimator.py"])












