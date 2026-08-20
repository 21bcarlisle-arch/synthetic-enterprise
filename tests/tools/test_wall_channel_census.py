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

def test_every_declared_channel_has_an_enumerator():
    """THE ATOM'S EXIT CRITERION, asserted rather than described."""
    assert wcc.channels_without_an_enumerator() == []
    assert set(wcc.ENUMERATORS) == set(wcc.CHANNEL_IDS)


def test_MUTATION_a_channel_with_no_enumerator_is_named_and_refuses_the_census(monkeypatch, tree):
    """The defect: a channel is declared and nothing can see it. The criterion must catch it."""
    crippled = dict(wcc.ENUMERATORS)
    del crippled["E_structural_protocol"]
    monkeypatch.setattr(wcc, "ENUMERATORS", crippled)

    assert wcc.channels_without_an_enumerator() == ["E_structural_protocol"]
    with pytest.raises(wcc.CensusUnavailable, match="no enumerator"):
        _census(tree)


def test_the_six_channels_are_the_six_the_census_found():
    """The declared channel set is the census's own, not a set that drifted to fit the tool."""
    assert wcc.CHANNEL_IDS == (
        "A_direct_import",
        "B_indirect_import",
        "C_envelope",
        "D_typed_port",
        "E_structural_protocol",
        "F_published_artefact",
    )
    # A and B are reported for coverage and enforced elsewhere -- see the module docstring.
    assert wcc.FROZEN_CHANNEL_IDS == (
        "C_envelope",
        "D_typed_port",
        "E_structural_protocol",
        "F_published_artefact",
    )


# ── 1. each enumerator finds its own channel's member ────────────────────────────────────────

def test_the_clean_tree_reads_exactly_one_member_per_frozen_channel(tree):
    current = _census(tree)
    assert current["C_envelope"] == {
        "company.billing.payment_observation_consumer -> interface.contracts.payment_observable_seam",
        "interface.contracts.payment_observable_seam -> interface.contracts.wall_envelope",
    }
    assert current["D_typed_port"] == {
        "tools.meter_read_port -> simulation.run_phase4c_on_phase2b"
    }
    assert current["E_structural_protocol"] == {
        "company/billing/monthly_bill_assembly.py -> ReadArrival"
    }
    assert current["F_published_artefact"] == {"bills -> saas/reporting/annual_report.py"}


def test_a_clean_tree_passes_its_own_baseline(tree):
    """R15 requires the PASS direction be shown: a control that cannot pass is worth nothing."""
    verdict = wcc.check(_census(tree), _baseline_of(tree))
    assert verdict.ok
    assert verdict.report() == "every frozen channel matches its list exactly."


# ── 2. one mutation per channel -- the guard must FIRE ───────────────────────────────────────

def test_MUTATION_a_new_envelope_importer_fails_channel_C(tree):
    baseline = _baseline_of(tree)
    _write(tree, "company/comms/conversation_generator.py", """
        from interface.contracts.wall_envelope import WallRequest
    """)
    verdict = wcc.check(_census(tree), baseline)
    assert not verdict.ok
    assert verdict.new["C_envelope"] == [
        "company.comms.conversation_generator -> interface.contracts.wall_envelope"
    ]


def test_MUTATION_a_new_port_importer_fails_channel_D(tree):
    baseline = _baseline_of(tree)
    _write(tree, "company/trading/credit_limits.py", """
        from tools.meter_read_port import MeterReadMessage
    """)
    verdict = wcc.check(_census(tree), baseline)
    assert not verdict.ok
    assert verdict.new["D_typed_port"] == [
        "tools.meter_read_port -> company.trading.credit_limits"
    ]


def test_MUTATION_a_SIXTH_port_appearing_is_a_new_member_not_an_invisible_one(tree):
    """The ports are discovered from the tree, so a port nobody listed still gets counted.

    The defect this rules out: a hardcoded five-port list, which would make the sixth port -- the
    only one anybody would add by mistake -- the one member the channel cannot see.
    """
    baseline = _baseline_of(tree)
    _write(tree, "tools/settlement_port.py", '"""a sixth port."""\n')
    _write(tree, "simulation/run_phase2b.py", """
        from tools.settlement_port import SettlementMessage
    """)
    verdict = wcc.check(_census(tree), baseline)
    assert not verdict.ok
    assert verdict.new["D_typed_port"] == ["tools.settlement_port -> simulation.run_phase2b"]


def test_MUTATION_a_new_structural_protocol_fails_channel_E(tree):
    baseline = _baseline_of(tree)
    _write(tree, "saas/property_model.py", """
        import typing


        class PropertyFeed(typing.Protocol):
            pass
    """)
    verdict = wcc.check(_census(tree), baseline)
    assert not verdict.ok
    assert verdict.new["E_structural_protocol"] == ["saas/property_model.py -> PropertyFeed"]


def test_MUTATION_a_new_artefact_key_reader_fails_channel_F(tree):
    baseline = _baseline_of(tree)
    _write(tree, "company/finance/board_dashboard.py", """
        def headline(run_output):
            return run_output.get("ledger_pnl")
    """)
    verdict = wcc.check(_census(tree), baseline)
    assert not verdict.ok
    assert verdict.new["F_published_artefact"] == [
        "ledger_pnl -> company/finance/board_dashboard.py"
    ]


def test_MUTATION_a_second_key_read_by_an_EXISTING_reader_fails_channel_F(tree):
    """Widening happens inside a file that is already on the list, not only by adding files."""
    baseline = _baseline_of(tree)
    _write(tree, "saas/reporting/annual_report.py", """
        def render(phase2b):
            return phase2b["bills"], phase2b["meter_read_log"]
    """)
    verdict = wcc.check(_census(tree), baseline)
    assert not verdict.ok
    assert verdict.new["F_published_artefact"] == [
        "meter_read_log -> saas/reporting/annual_report.py"
    ]


# ── 3. the null controls -- move the sample, not the law ─────────────────────────────────────

def test_NULL_CONTROL_an_unrelated_module_does_not_move_any_channel(tree):
    """A change to the same trees that is not a crossing must leave every channel where it was."""
    before = _census(tree)
    _write(tree, "company/finance/bad_debt_reconciliation.py", """
        import json
        from company.billing import monthly_bill_assembly


        def reconcile(rows):
            return json.dumps(sorted(rows))
    """)
    assert _census(tree) == before


def test_NULL_CONTROL_a_key_read_on_the_WORLD_side_is_not_a_channel_F_member(tree):
    """Channel F's subject is the BUSINESS side reading published output, not any reader."""
    before = _census(tree)
    _write(tree, "simulation/run_phase2b.py", """
        def summarise(run_output):
            return run_output["meter_read_log"]
    """)
    assert _census(tree)["F_published_artefact"] == before["F_published_artefact"]


def test_NULL_CONTROL_a_string_that_is_not_a_published_key_is_not_a_member(tree):
    """The denominator is the artefact's own key set -- an arbitrary literal must not count."""
    before = _census(tree)
    _write(tree, "saas/reporting/segment_report.py", """
        def render(row):
            return row["not_a_published_key"]
    """)
    assert _census(tree)["F_published_artefact"] == before["F_published_artefact"]


def test_NULL_CONTROL_a_non_Protocol_class_is_not_a_channel_E_member(tree):
    before = _census(tree)
    _write(tree, "saas/reporting/css_statement.py", """
        from dataclasses import dataclass


        @dataclass
        class Statement:
            total_gbp: float
    """)
    assert _census(tree)["E_structural_protocol"] == before["E_structural_protocol"]


# ── 4. shrink is the direction that must PASS ────────────────────────────────────────────────

def test_a_paid_down_member_passes_and_is_reported_rather_than_silently_dropped(tree):
    """A shrink-only list must let the wall get better, and must SAY that it did.

    The failure this rules out is the count-pinned control that reds on its own success case: a
    crossing being cut is the outcome the whole programme is for, and a gate that fails on it is
    a gate that gets disabled the first week somebody cuts one.
    """
    baseline = _baseline_of(tree)
    (tree / "company/billing/monthly_bill_assembly.py").write_text("pass\n", encoding="utf-8")

    verdict = wcc.check(_census(tree), baseline)
    assert verdict.ok
    assert verdict.gone["E_structural_protocol"] == [
        "company/billing/monthly_bill_assembly.py -> ReadArrival"
    ]
    assert "paid down on E_structural_protocol" in verdict.report()


# ── 5. fail-closed -- an unavailable check is a FAILED check ─────────────────────────────────

def test_FAIL_CLOSED_an_empty_artefact_refuses_rather_than_reporting_a_clean_channel_F(tree):
    """An empty denominator makes channel F vacuously conformant. Refuse it."""
    with pytest.raises(wcc.CensusUnavailable, match="empty denominator"):
        _census(tree, artefact={})


def test_FAIL_CLOSED_an_artefact_absent_at_the_rev_raises(tmp_path):
    with pytest.raises(wcc.CensusUnavailable):
        wcc.artefact_at("HEAD", repo_root=tmp_path)


def test_FAIL_CLOSED_a_bogus_rev_raises_rather_than_returning_an_empty_artefact():
    with pytest.raises(wcc.CensusUnavailable):
        wcc.artefact_at("no-such-rev-0000000")


def test_FAIL_CLOSED_a_missing_baseline_raises(tmp_path):
    with pytest.raises(wcc.CensusUnavailable, match="unreadable"):
        wcc.load_baseline(tmp_path / "nope.json")


def test_FAIL_CLOSED_a_baseline_missing_a_frozen_channel_raises(tmp_path):
    """A partial baseline would wave through every member of the channel it omits."""
    path = tmp_path / "partial.json"
    path.write_text(json.dumps({"frozen": {"C_envelope": []}}), encoding="utf-8")
    with pytest.raises(wcc.CensusUnavailable, match="missing frozen channels"):
        wcc.load_baseline(path)


def test_FAIL_CLOSED_a_baseline_with_no_frozen_object_raises(tmp_path):
    path = tmp_path / "shapeless.json"
    path.write_text(json.dumps({"controls": []}), encoding="utf-8")
    with pytest.raises(wcc.CensusUnavailable, match="no `frozen` object"):
        wcc.load_baseline(path)


# ── 6. independence -- the two sides are not one side ────────────────────────────────────────

def test_the_baseline_is_a_FILE_and_editing_it_changes_the_verdict(tree, tmp_path):
    """TAUTOLOGY check: if the frozen list were re-derived from the tree it could never fail.

    Shown by moving ONLY the baseline: the tree is byte-identical across the two calls, and the
    verdict flips. So the comparison has a subject outside the reading it checks.
    """
    path = tmp_path / "baseline.json"
    path.write_text(
        json.dumps(wcc.freeze_payload(_census(tree), "fixture"), indent=2), encoding="utf-8"
    )
    assert wcc.check(_census(tree), wcc.load_baseline(path)).ok

    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["frozen"]["C_envelope"] = []
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    verdict = wcc.check(_census(tree), wcc.load_baseline(path))
    assert not verdict.ok
    assert len(verdict.new["C_envelope"]) == 2


# ── 7. the live tree -- the enforced ratchet ─────────────────────────────────────────────────

def test_THE_LIVE_WALL_HAS_NOT_GROWN():
    """The enforced check. A new member of any frozen channel fails here and nowhere else.

    Re-freeze with `python3 -m tools.wall_channel_census --worktree --freeze` ONLY after ruling
    the new member -- a freeze without a reason is an amnesty.
    """
    verdict = wcc.check(wcc.census_of_worktree(), wcc.load_baseline())
    assert verdict.ok, verdict.report()


def test_the_shipped_baseline_carries_its_provenance():
    """A frozen list with no record of when and against what is a list nobody can re-derive."""
    payload = json.loads(wcc.BASELINE_PATH.read_text(encoding="utf-8"))
    assert payload["_meta"]["atom"] == "EP6_wall_protocol_typing"
    assert payload["_meta"]["tool"] == "tools/wall_channel_census.py"
    assert set(payload["frozen"]) == set(wcc.FROZEN_CHANNEL_IDS)
    # A and B are reported so the coverage question is answerable in one place.
    assert set(payload["reported_not_frozen"]) == {"A_direct_import", "B_indirect_import"}


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


def test_a_conforming_tree_reports_its_one_wire_site_and_passes(wire_tree):
    verdict = wcc.wire_conformance(str(wire_tree))
    assert verdict.ok, verdict.report()
    assert len(verdict.carrying) == 1
    assert verdict.silent == []


def test_MUTATION_a_call_site_that_omits_the_flag_is_SILENT_and_fails(wire_tree):
    """THE REAL DEFECT, as a fixture: this is exactly the shape the three live sites had."""
    _write(wire_tree, "simulation/run_phase4c_on_phase2b.py", """
        from tools.meter_read_port import MeterReadMessage

        def run(messages):
            return [m.to_log_entry() for m in messages]
    """)
    verdict = wcc.wire_conformance(str(wire_tree))
    assert not verdict.ok
    assert len(verdict.silent) == 1
    assert "run_phase4c_on_phase2b.py" in verdict.silent[0]


def test_MUTATION_the_flag_passed_as_False_is_SILENT_not_conformant(wire_tree):
    """Naming the flag is not carrying the version -- a check on the keyword alone fails here."""
    _write(wire_tree, "simulation/run_phase4c_on_phase2b.py", """
        from tools.meter_read_port import MeterReadMessage

        def run(messages):
            return [m.to_log_entry(include_schema_version=False) for m in messages]
    """)
    verdict = wcc.wire_conformance(str(wire_tree))
    assert not verdict.ok
    assert len(verdict.silent) == 1


def test_MUTATION_a_SECOND_caller_that_omits_the_flag_fails_while_the_first_still_carries(wire_tree):
    """One conforming site must not vouch for a non-conforming one."""
    _write(wire_tree, "simulation/run_phase2b.py", """
        from tools.meter_read_port import MeterReadMessage

        def run(messages):
            return [m.to_log_entry() for m in messages]
    """)
    verdict = wcc.wire_conformance(str(wire_tree))
    assert not verdict.ok
    assert len(verdict.carrying) == 1 and len(verdict.silent) == 1


def test_FAIL_CLOSED_deleting_the_flag_from_the_port_refuses_rather_than_passing(wire_tree):
    """THE CHEAPEST ROUTE-AROUND, refused. Removing the parameter makes every call site
    trivially 'conformant'; if that passed, the way to green this control would be to delete
    its subject."""
    _write(wire_tree, "tools/meter_read_port.py", """
        class MeterReadMessage:
            def to_log_entry(self) -> dict:
                return {"customer_id": self.customer_id}
    """)
    with pytest.raises(wcc.CensusUnavailable, match="none declares"):
        wcc.wire_conformance(str(wire_tree))


def test_FAIL_CLOSED_a_port_that_declares_the_flag_with_no_caller_refuses(wire_tree):
    """An empty denominator makes channel D vacuously conformant -- channel F's own doctrine."""
    _write(wire_tree, "simulation/run_phase4c_on_phase2b.py", """
        from tools.meter_read_port import MeterReadMessage
    """)
    with pytest.raises(wcc.CensusUnavailable, match="empty denominator"):
        wcc.wire_conformance(str(wire_tree))


def test_ZERO_PORTS_IS_NOT_REFUSED_because_it_is_this_atoms_success_case(tmp_path):
    """Channel D fully paid down is the goal, and a control pinned to a non-zero count reds on
    its own success case."""
    root = tmp_path / "repo"
    _write(root, "simulation/run_phase2b.py", '"""no ports anywhere."""\n')
    verdict = wcc.wire_conformance(str(root))
    assert verdict.ok
    assert verdict.carrying == [] and verdict.silent == []


def test_NULL_CONTROL_a_ports_own_nested_serialisation_is_not_a_wire_site(wire_tree):
    """`acquisition_funnel_port` calls `to_log_entry()` on its own FunnelStageMessage rows, whose
    serialiser takes no flag. That is one message building itself, not a crossing -- counting it
    would make this control permanently red for a reason its subject cannot fix."""
    _write(wire_tree, "tools/acquisition_funnel_port.py", """
        class FunnelStageMessage:
            def to_log_entry(self) -> dict:
                return {"stage": self.stage}


        class AcquisitionFunnelMessage:
            def to_log_entry(self, include_schema_version: bool = False) -> dict:
                return {"stages": [s.to_log_entry() for s in self.stages]}
    """)
    verdict = wcc.wire_conformance(str(wire_tree))
    assert verdict.ok, verdict.report()
    assert len(verdict.carrying) == 1


def test_NULL_CONTROL_an_unrelated_module_does_not_move_the_wire_verdict(wire_tree):
    """Move the sample, not the law."""
    before = wcc.wire_conformance(str(wire_tree))
    _write(wire_tree, "company/billing/unrelated.py", """
        def render(bills):
            return len(bills)
    """)
    assert wcc.wire_conformance(str(wire_tree)) == before


def test_NULL_CONTROL_a_plain_function_named_like_the_method_is_not_a_wire_site(wire_tree):
    """`simulation/meter_reads.py::read_event_to_log_entry` is a free function, not a message
    crossing. Matching on the bare name rather than an attribute call would swallow it."""
    before = wcc.wire_conformance(str(wire_tree))
    _write(wire_tree, "simulation/meter_reads.py", """
        def read_event_to_log_entry(event):
            return dict(event)

        def build(events):
            return [read_event_to_log_entry(e) for e in events]
    """)
    assert wcc.wire_conformance(str(wire_tree)) == before


def test_the_wire_check_reads_the_TREE_so_editing_a_call_site_flips_the_verdict(wire_tree):
    """INDEPENDENCE: the verdict's subject is program text on disk, not a value this module
    derives from itself. Move only the call site and the verdict must move with it."""
    assert wcc.wire_conformance(str(wire_tree)).ok
    _write(wire_tree, "simulation/run_phase4c_on_phase2b.py", """
        from tools.meter_read_port import MeterReadMessage

        def run(messages):
            return [m.to_log_entry() for m in messages]
    """)
    assert not wcc.wire_conformance(str(wire_tree)).ok


# ── 9. the artefact half -- observation, never a gate ────────────────────────────────────────

def test_wire_on_artefact_counts_rows_that_carry_a_version():
    coverage = wcc.wire_on_artefact({
        "meter_read_log": [{"customer_id": 1, "schema_version": "1.0"}, {"customer_id": 2}],
        "contact_centre_log": [{"schema_version": "1.0"}],
        "ledger_pnl": {"not": "a list"},
        "empty_log": [],
        "scalars": [1, 2, 3],
    })
    assert coverage["meter_read_log"] == (1, 2)
    assert coverage["contact_centre_log"] == (1, 1)
    # Not a list of dicts, so not a row population this question applies to.
    assert "ledger_pnl" not in coverage and "scalars" not in coverage
    # An empty list has no rows to carry anything -- reporting 0/0 would read as a failure.
    assert "empty_log" not in coverage


def test_the_artefact_half_is_NOT_wired_into_the_commit_gate():
    """Stated as a test because it is a DESIGN decision that could be silently reversed: the
    artefact is regenerated by a sim run, so flipping a call site cannot move a single row until
    the next run publishes. A gate on it reds the commit that repairs the defect and passes the
    one that introduced it -- the exact shape this file learned once already for channel F.
    """
    gate = Path("tools/pre_commit_test_gate.py").read_text(encoding="utf-8")
    assert "wire_on_artefact" not in gate
    assert "artefact_wire_conformance" not in gate


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


def test_the_publish_key_is_the_DICT_KEY_not_the_local_name(publish_tree):
    """The local list is `rows` and the artefact key is `meter_read_log`. A mapping that echoed
    the sink name would answer `rows` here and then find no such key in any artefact -- reporting
    the log as unobservable for ever, which reads identically to a wire that never went silent."""
    keys = wcc.wire_publish_keys(str(publish_tree))
    assert list(keys.values()) == ["meter_read_log"]


def test_a_conforming_artefact_passes_on_the_key_the_tree_named(publish_tree):
    verdict = wcc.artefact_wire_conformance(str(publish_tree), ARTEFACT_CARRYING)
    assert verdict.ok, verdict.report()
    assert verdict.carrying == {"meter_read_log": (1, 1)}


def test_MUTATION_rows_that_reach_the_artefact_without_the_version_are_SILENT(publish_tree):
    """THE DEFECT THIS HALF EXISTS FOR, and the one the code half is blind to: the call site still
    asks for the version -- `wire_conformance` is GREEN on this same tree -- and the published
    bytes do not carry it. That is the true state at HEAD b22698df8, where the code half passes on
    all three sites and this half is silent on all 1,996 rows."""
    assert wcc.wire_conformance(str(publish_tree)).ok
    verdict = wcc.artefact_wire_conformance(str(publish_tree), ARTEFACT_SILENT)
    assert not verdict.ok
    assert verdict.silent == {"meter_read_log": (0, 2)}
    assert "0/2" in verdict.report()


def test_MUTATION_a_PARTIALLY_carrying_log_is_silent_not_carrying(publish_tree):
    """Asserting the FIRST row carries a version is the cheap version of this check and it passes
    here. Every row must carry it, or a half-migrated publisher reads as done."""
    artefact = {"meter_read_log": [{"schema_version": "1.0"}, {"customer_id": 2}]}
    verdict = wcc.artefact_wire_conformance(str(publish_tree), artefact)
    assert not verdict.ok
    assert verdict.silent == {"meter_read_log": (1, 2)}


def test_FAIL_CLOSED_a_key_absent_from_the_artefact_is_UNOBSERVABLE_not_conformant(publish_tree):
    """"Could not look" and "found nothing" are the same number and opposite facts. An absent key
    must not fall out of the subject silently -- that is how a log that stopped being published
    becomes a passing check."""
    verdict = wcc.artefact_wire_conformance(str(publish_tree), {"other_log": [{"a": 1}]})
    assert not verdict.ok
    assert verdict.absent == ["meter_read_log"]


def test_FAIL_CLOSED_an_empty_published_list_is_UNOBSERVABLE_not_conformant(publish_tree):
    """Zero rows carry the version vacuously. Reporting 0/0 as conformant would make deleting the
    log the cheapest way to pass."""
    verdict = wcc.artefact_wire_conformance(str(publish_tree), {"meter_read_log": []})
    assert not verdict.ok
    assert verdict.absent == ["meter_read_log"]


def test_MUTATION_rows_that_reach_no_published_key_are_UNRESOLVED_not_dropped(publish_tree):
    """A SECOND caller returns its rows directly and puts them in no dict, so no artefact reading
    can speak for them. The verdict must go red on it even though the resolvable site beside it is
    perfectly conformant -- dropping the unresolvable one would shrink the subject to whatever the
    sink rule happens to recognise, which is an exclusion that makes the verdict green.

    This is the mutation that caught the first cut of `wire_publish_keys`: it iterated the sinks
    rather than the calls, so a site in a bare `return` was invisible instead of unresolved.
    """
    _write(publish_tree, "simulation/run_phase2b.py", """
        from tools.meter_read_port import MeterReadMessage

        def run(messages):
            return [m.to_log_entry(include_schema_version=True) for m in messages]
    """)
    verdict = wcc.artefact_wire_conformance(str(publish_tree), ARTEFACT_CARRYING)
    assert not verdict.ok
    assert verdict.carrying == {"meter_read_log": (1, 1)}
    assert len(verdict.unresolved) == 1
    assert "run_phase2b.py" in verdict.unresolved[0]


def test_FAIL_CLOSED_wire_sites_that_ALL_resolve_to_nothing_refuse_to_report(wire_tree):
    """The subject having been removed is a failed check, not a pass -- `wire_conformance`'s own
    doctrine applied to the mapping instead of the flag."""
    with pytest.raises(wcc.CensusUnavailable):
        wcc.artefact_wire_conformance(str(wire_tree), {})


def test_a_tree_with_NO_wire_sites_is_not_refused(tmp_path: Path):
    """Channel D fully paid down is this atom's success case; a control pinned to a non-zero count
    reds on its own success."""
    root = tmp_path / "repo"
    _write(root, "simulation/nothing.py", "X = 1\n")
    assert wcc.artefact_wire_conformance(str(root), {}).ok


def test_NULL_CONTROL_an_unrelated_published_key_does_not_move_the_verdict(publish_tree):
    """Move the sample, not the law: a second log in the artefact is not this subject."""
    before = wcc.artefact_wire_conformance(str(publish_tree), ARTEFACT_CARRYING)
    after = wcc.artefact_wire_conformance(
        str(publish_tree), {**ARTEFACT_CARRYING, "billing_log": [{"a": 1}]}
    )
    assert after == before


# ── 10. the live tree ────────────────────────────────────────────────────────────────────────

def test_THE_LIVE_WIRE_CARRIES_THE_VERSION():
    """The enforced check. Channel D's whole conformance by the 2026-08-15 census's definition.

    This test is RED at c728642c3 and every commit before it, naming the three live sites
    (run_phase2b.py, run_phase4c_on_phase2b.py x2) -- the mutation for this control is real repo
    history, not a fixture.
    """
    verdict = wcc.wire_conformance_at(worktree=True)
    assert verdict.ok, verdict.report()


def test_THE_LIVE_WIRE_SITES_ALL_RESOLVE_TO_A_PUBLISHED_KEY():
    """The live half of the SUBJECT, and deliberately not the live half of the ANSWER.

    Asserting the live artefact is green would be the gate section 9 refuses: the artefact is a
    past sim run's output, so a fresh checkout holds the bytes committed at HEAD -- 0 of 1,996
    rows -- and the test would red on a tree with nothing wrong with it. What IS stable, because
    it is read from program text alone, is that every wire site still resolves to the key its rows
    are published under. That is the part that rots silently: a refactor that moves the rows into
    a helper leaves the code half green, the artefact half with an empty subject, and no reader
    any the wiser.
    """
    keys = wcc.wire_publish_keys(str(wcc.PROJECT_DIR))
    assert keys, "no wire call sites found on the live tree -- the subject has gone"
    unresolved = sorted(site for site, key in keys.items() if key is None)
    assert not unresolved, f"wire sites publishing under no artefact key: {unresolved}"
    assert set(keys.values()) == {
        "acquisition_funnel_log", "meter_read_log", "contact_centre_log",
    }, keys


# ── 11. the CALLER refuses, it does not merely print ─────────────────────────────────────────
#
# Section 10 proves the enumerator's verdict is right. That is not the same claim as "a commit
# carrying a silent crossing is refused", and the difference is not hypothetical: this check
# shipped for one commit in a REPORTING branch that printed the same true verdict and returned
# ok. A control whose caller discards its verdict is a control that cannot fail, so the caller
# gets its own mutation.

def _gate_wire_branch(monkeypatch, *, wire: wcc.WireVerdict):
    """Run `_wall_channel_census_check` with the census and channel-C halves forced GREEN and the
    channel-D wire half forced to `wire`, so the verdict is attributable to that half alone.

    CHANNEL C IS FORCED HERE FOR THE SAME REASON THE CENSUS IS, and it was added when channel C
    armed (2026-08-20 pass 23). Left real, it would run against the fixture's fake index tree
    `"0"*40`, raise, and hit its own fail-closed branch -- at which point the NULL CONTROL below
    would fail while looking like a defect in channel D. Every half of a multi-part step has to be
    pinned for any one of them to be a subject.
    """
    from tools import pre_commit_test_gate as gate

    monkeypatch.setattr(gate, "_index_tree", lambda: "0" * 40)
    monkeypatch.setattr(wcc, "census_at", lambda tree, root: {})
    monkeypatch.setattr(wcc, "load_baseline", lambda *a, **k: {})
    monkeypatch.setattr(wcc, "check", lambda *a, **k: _AlwaysOk())
    monkeypatch.setattr(wcc, "wire_conformance_at", lambda **k: wire)
    monkeypatch.setattr(wcc, "envelope_wire_conformance_at", lambda **k: _conformant_C())
    # The step short-circuits when no Python is staged, so the sample must contain some.
    return gate._wall_channel_census_check(["simulation/anything.py"])


class _AlwaysOk:
    ok = True

    def report(self) -> str:  # pragma: no cover -- only reached if the test itself is wrong
        return "census forced green by the fixture"


def test_MUTATION_the_GATE_refuses_a_tree_whose_wire_is_silent(monkeypatch):
    """The named defect: a commit puts a port message on the wire without its version.

    The 2026-08-19 reporting branch returned (True, ...) on exactly this input.
    """
    silent = wcc.WireVerdict(carrying=["a.py -> 10"], silent=["b.py -> 20"])
    ok, detail = _gate_wire_branch(monkeypatch, wire=silent)
    assert not ok, f"the gate accepted a silent crossing: {detail}"
    assert "b.py -> 20" in detail, "the refusal must carry the diagnostic payload (R5)"


def test_NULL_CONTROL_the_GATE_passes_a_conformant_wire(monkeypatch):
    """Move the sample, not the law: same caller, same forced-green census, only the wire
    verdict changes. Without this the mutation above is satisfied by a gate that refuses
    everything."""
    ok, detail = _gate_wire_branch(
        monkeypatch, wire=wcc.WireVerdict(carrying=["a.py -> 10"], silent=[])
    )
    assert ok, detail
    assert "1 wire site(s) carry the version" in detail


def test_FAIL_CLOSED_the_GATE_refuses_when_the_wire_check_itself_raises(monkeypatch):
    """An unavailable check is a FAILED check (R15's third killer pattern)."""
    from tools import pre_commit_test_gate as gate

    monkeypatch.setattr(gate, "_index_tree", lambda: "0" * 40)
    monkeypatch.setattr(wcc, "census_at", lambda tree, root: {})
    monkeypatch.setattr(wcc, "load_baseline", lambda *a, **k: {})
    monkeypatch.setattr(wcc, "check", lambda *a, **k: _AlwaysOk())

    def _boom(**kwargs):
        raise RuntimeError("git is not available")

    monkeypatch.setattr(wcc, "wire_conformance_at", _boom)
    ok, detail = gate._wall_channel_census_check(["simulation/anything.py"])
    assert not ok and "RAISED" in detail and "git is not available" in detail


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


def test_an_artefact_committed_BEFORE_its_producer_is_reported_as_PREDATING(git_tree):
    """The state at HEAD on 2026-08-20, and the whole reason this exists: the migration landed
    after the last publish, so 0 of 1,996 rows is stale bytes and not a broken wire."""
    _commit(git_tree, wcc.ARTEFACT_REL, '{"meter_read_log": []}\n', "publish")
    _commit(git_tree, PRODUCER, "x = 1\n", "the wire lands")

    prov = wcc.artefact_provenance([PRODUCER], rev="HEAD", repo_root=git_tree)

    assert prov.predates == [PRODUCER]
    assert prov.staleness_explains_silence
    assert not prov.undetermined
    assert "STALE BYTES" in prov.report()


def test_MUTATION_an_artefact_committed_AFTER_its_producer_is_NOT_excused_as_stale(git_tree):
    """Move the sample, not the law. A verdict that says "stale" whichever way the commits went
    would excuse every genuinely broken wire while looking exactly as helpful, so the same two
    files in the opposite order must produce the opposite reading."""
    _commit(git_tree, PRODUCER, "x = 1\n", "the wire lands")
    _commit(git_tree, wcc.ARTEFACT_REL, '{"meter_read_log": []}\n', "publish")

    prov = wcc.artefact_provenance([PRODUCER], rev="HEAD", repo_root=git_tree)

    assert prov.predates == []
    assert not prov.staleness_explains_silence
    assert prov.determined
    assert "NOT explained by staleness" in prov.report()


def test_the_BOUNDARY_case_of_one_commit_carrying_both_is_not_staleness(git_tree):
    """Artefact and producer in the SAME commit is the value the rule is most easily wrong about.
    There is no commit order between them, so staleness is not available as an excuse -- and
    `_strictly_precedes` must return False rather than the None it returns for a real fork."""
    _write(git_tree, wcc.ARTEFACT_REL, '{"meter_read_log": []}\n')
    _write(git_tree, PRODUCER, "x = 1\n")
    _git(git_tree, "add", "-A")
    _git(git_tree, "commit", "-q", "-m", "both at once")

    prov = wcc.artefact_provenance([PRODUCER], rev="HEAD", repo_root=git_tree)

    assert prov.predates == [] and prov.undetermined == []
    assert prov.determined


def test_MUTATION_a_producer_git_cannot_date_is_UNDETERMINED_not_current(git_tree):
    """FAIL-OPEN, R15's second killer. A producer path with no commit touching it returns None
    from `_last_commit_touching`; if that were dropped, an empty `predates` would read as the
    reassuring "no older than any producer" on a question git never answered."""
    _commit(git_tree, wcc.ARTEFACT_REL, '{"meter_read_log": []}\n', "publish")

    prov = wcc.artefact_provenance([PRODUCER], rev="HEAD", repo_root=git_tree)

    assert prov.undetermined == [PRODUCER]
    assert not prov.determined
    assert not prov.staleness_explains_silence
    assert "UNDETERMINED" in prov.report()
    assert "NOT explained by staleness" not in prov.report()


def test_FAIL_CLOSED_an_artefact_with_no_commit_is_UNDETERMINED_not_current(git_tree):
    """The artefact side of the same fail-open: producers dated, artefact never committed."""
    _commit(git_tree, PRODUCER, "x = 1\n", "the wire lands")

    prov = wcc.artefact_provenance([PRODUCER], rev="HEAD", repo_root=git_tree)

    assert prov.artefact_commit is None
    assert prov.undetermined == [PRODUCER] and not prov.determined
    assert wcc.ARTEFACT_REL in prov.report() or "UNDETERMINED" in prov.report()


def test_NO_WIRE_SITES_reports_no_producer_rather_than_a_clean_bill(git_tree):
    """Channel D fully paid down is this atom's SUCCESS case, so an empty producer set is not
    refused -- but it must not print the sentence that convicts a silent log either, because
    there is no subject to convict."""
    _commit(git_tree, wcc.ARTEFACT_REL, '{"meter_read_log": []}\n', "publish")

    prov = wcc.artefact_provenance([], rev="HEAD", repo_root=git_tree)

    assert not prov.determined and not prov.staleness_explains_silence
    assert "no wire site" in prov.report()
    assert "NOT explained by staleness" not in prov.report()


def test_INDEPENDENCE_the_verdict_does_not_move_when_the_artefacts_ROWS_change(git_tree):
    """TAUTOLOGY, R15's first killer. This reading exists to be checked AGAINST the row counts,
    so it must not be computed from them: the same commit order with rows that carry the version
    and rows that do not must give the identical verdict."""
    _commit(git_tree, wcc.ARTEFACT_REL, '{"meter_read_log": [{"schema_version": 1}]}\n', "publish")
    _commit(git_tree, PRODUCER, "x = 1\n", "the wire lands")
    carrying = wcc.artefact_provenance([PRODUCER], rev="HEAD", repo_root=git_tree)

    _commit(git_tree, wcc.ARTEFACT_REL, '{"meter_read_log": [{}]}\n', "republish, silent")
    silent = wcc.artefact_provenance([PRODUCER], rev="HEAD", repo_root=git_tree)

    # The rows changed from carrying to silent and the PROVENANCE moved for the other reason --
    # the republish is a later commit than the producer. Contents never entered either verdict.
    assert carrying.predates == [PRODUCER]
    assert silent.predates == [] and silent.determined


def test_the_report_REFUSES_to_claim_production_on_its_own_green_case(git_tree):
    """The honest half. "Not older than its producers" is a commit-order bound and is NOT the
    production stamp WORKER_FINDING_THE_PUBLISHED_ARTEFACT_CARRIES_NO_PRODUCTION_STAMP_2026-08-15
    says is missing -- a publisher running pre-migration code commits fresh bytes and lands here.
    If this line is ever dropped the report starts asserting something it cannot know."""
    _commit(git_tree, PRODUCER, "x = 1\n", "the wire lands")
    _commit(git_tree, wcc.ARTEFACT_REL, '{"meter_read_log": []}\n', "publish")

    report = wcc.artefact_provenance([PRODUCER], rev="HEAD", repo_root=git_tree).report()

    assert "NOT a production stamp" in report
    assert "COMMIT-ORDER bound" in report


def test_a_DIRTY_worktree_artefact_is_UNDETERMINED_rather_than_dated_by_its_path(git_tree):
    """Worktree mode meets uncommitted bytes on this shared tree every time a daemon has run.
    Dating them by the commit that last touched their PATH would compare a file nobody committed
    against code that may postdate it -- wrong in the reassuring direction, on every such tree."""
    _commit(git_tree, PRODUCER, "x = 1\n", "the wire lands")
    _commit(git_tree, wcc.ARTEFACT_REL, '{"meter_read_log": []}\n', "publish")
    _write(git_tree, wcc.ARTEFACT_REL, '{"meter_read_log": [{}]}\n')  # a daemon republishes

    prov = wcc.artefact_provenance_at(worktree=True, repo_root=git_tree)

    assert not prov.determined and "uncommitted" in (prov.reason or "")
    assert "NOT explained by staleness" not in prov.report()


def test_the_PRODUCERS_are_derived_from_the_wire_sites_not_declared(tmp_path: Path):
    """A declared list of the three live emitters would leave a FOURTH port's emitter undated and
    unlisted on the day it lands -- the hardcoded-five this module's own docstring refuses. So the
    subject is asked of a tree whose emitter shares no name with any live one, and the answer must
    be that module and not the live three."""
    root = tmp_path / "repo"
    _write(root, "tools/meter_read_port.py", PORT_WITH_FLAG)
    _write(root, "simulation/run_a_fourth_emitter.py", """
        from tools.meter_read_port import MeterReadMessage

        def run(messages):
            rows = [m.to_log_entry(include_schema_version=True) for m in messages]
            return {"a_fourth_log": rows}
    """)

    assert wcc.producer_paths_of(str(root)) == ["simulation/run_a_fourth_emitter.py"]


def test_THE_LIVE_ARTEFACT_IS_DATED_AGAINST_ITS_PRODUCERS():
    """The live reading, and deliberately not a live assertion of WHICH way it goes.

    Which way it goes is a property of when the last sim run published, so pinning it would red on
    a tree with nothing wrong with it -- section 10's reason. What must hold on every tree is that
    the question is ANSWERABLE: producers found, artefact dated, nothing undetermined. That is the
    part that rots silently, because a producer moving to a new module leaves this undetermined
    and the report reverts to the unreadable state this section exists to end.
    """
    prov = wcc.artefact_provenance_at(rev="HEAD")

    assert prov.producers, "no producers derived from the live wire sites -- the subject has gone"
    assert prov.determined, prov.report()


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


def test_a_conforming_envelope_seam_is_reported_wire_borne_and_passes(envelope_tree):
    verdict = wcc.envelope_wire_conformance(str(envelope_tree))

    assert verdict.wire_borne == [PAYMENT_SEAM]
    assert verdict.in_process == [] and verdict.half_wired == []
    assert verdict.ok, verdict.report()


def test_the_VERSIONLESS_envelope_module_is_reported_not_scored(envelope_tree):
    """`wall_envelope` defines the shape; it is not a crossing and has no version of its own.

    Counting it as a failure would make the control permanently red for a reason its subject
    cannot fix, and dropping it silently would hide a NEW seam that forgot its version -- which is
    why it lands in a named bucket rather than either.
    """
    verdict = wcc.envelope_wire_conformance(str(envelope_tree))

    assert verdict.unversioned == ["interface.contracts.wall_envelope"]
    assert "interface.contracts.wall_envelope" not in verdict.in_process
    assert "declares no SCHEMA_VERSION" in verdict.report()


def test_MUTATION_an_IN_PROCESS_seam_fails_even_though_its_envelope_declares_a_version(
    envelope_tree,
):
    """THE DOCTRINE MUTATION, run rather than asserted.

    The seam keeps its `SCHEMA_VERSION`, keeps its importers, and keeps every structural property
    a version-presence check could see. Only the transport is removed. A control asking "does the
    envelope carry a version" stays green through exactly this edit; this one must go red.
    """
    _write(envelope_tree, "simulation/payment_seam_adapter.py", """
        from interface.contracts.payment_observable_seam import SCHEMA_VERSION

        def emit(response):
            return [response]
    """)
    _write(envelope_tree, "company/billing/payment_observation_consumer.py", """
        from interface.contracts.payment_observable_seam import PaymentNotification

        def consume(response):
            return response.payload
    """)
    verdict = wcc.envelope_wire_conformance(str(envelope_tree))

    assert verdict.in_process == [PAYMENT_SEAM]
    assert not verdict.ok
    assert "IN-PROCESS" in verdict.report()
    # The version is still declared and still imported -- the field was never the subject.
    assert wcc._seam_version(str(envelope_tree), PAYMENT_SEAM) == 1


def test_MUTATION_an_encoder_with_no_decoder_is_HALF_WIRED_not_conformant(envelope_tree):
    """Strictly worse than in-process and must not read as better: bytes are produced in the wire
    form and nothing on the far side ever version-checks them, so the crossing LOOKS transported.
    """
    _write(envelope_tree, "company/billing/payment_observation_consumer.py", """
        from interface.contracts.payment_observable_seam import PaymentNotification

        def consume(response):
            return response.payload
    """)
    verdict = wcc.envelope_wire_conformance(str(envelope_tree))

    assert verdict.half_wired == [(PAYMENT_SEAM, "ENCODED")]
    assert not verdict.ok
    assert "ENCODED ONLY" in verdict.report()


def test_MUTATION_a_decoder_with_no_encoder_is_HALF_WIRED_the_other_way(envelope_tree):
    """The opposite half, so the bucket is about which side is missing and not about which edit
    the fixture happened to make."""
    _write(envelope_tree, "simulation/payment_seam_adapter.py", """
        from interface.contracts.payment_observable_seam import SCHEMA_VERSION

        def emit(response):
            return [response]
    """)
    verdict = wcc.envelope_wire_conformance(str(envelope_tree))

    assert verdict.half_wired == [(PAYMENT_SEAM, "DECODED")]
    assert not verdict.ok


def test_MUTATION_a_SECOND_seam_crossing_in_process_fails_while_the_first_stays_wire_borne(
    envelope_tree,
):
    """The live shape at HEAD, in miniature: one migrated seam and one that never was. A verdict
    that collapsed to a single boolean would report the whole channel green on the first."""
    _write(envelope_tree, "interface/contracts/conversation_seam.py", """
        from interface.contracts.wall_envelope import WallRequest

        SCHEMA_VERSION = 1
    """)
    _write(envelope_tree, "company/comms/conversation_generator.py", """
        from interface.contracts.conversation_seam import ConversationRequest

        def ask(req):
            return req
    """)
    verdict = wcc.envelope_wire_conformance(str(envelope_tree))

    assert verdict.wire_borne == [PAYMENT_SEAM]
    assert verdict.in_process == ["interface.contracts.conversation_seam"]
    assert not verdict.ok


def test_BOUNDARY_a_dict_one_key_short_of_the_wire_form_is_NOT_an_encode_site(envelope_tree):
    """The value the rule is most easily wrong about. `absence is never agreement` is the
    envelope's own law: a message missing one required key is one the far side must REFUSE, so
    accepting it here would certify as transported exactly the crossing that cannot land.
    """
    _write(envelope_tree, "simulation/payment_seam_adapter.py", """
        from interface.contracts.payment_observable_seam import SCHEMA_VERSION

        def encode_wall_response(response):
            return {
                "correlation_id": response.correlation_id,
                "status": response.status.value,
                "schema_version": SCHEMA_VERSION,
                "observed_at": response.observed_at.isoformat(),
                "valid_time": None,
                "payload": None,
            }
    """)
    verdict = wcc.envelope_wire_conformance(str(envelope_tree))

    assert verdict.half_wired == [(PAYMENT_SEAM, "DECODED")]


def test_BOUNDARY_a_dict_with_an_EXTRA_key_is_not_the_wire_form_either(envelope_tree):
    """The other side of the same boundary -- a superset is a different message, not a lenient
    pass, and a control that accepted supersets would credit any dict that happened to contain
    seven familiar names."""
    _write(envelope_tree, "simulation/payment_seam_adapter.py", WIRE_ENCODER.replace(
        '"error": None,', '"error": None,\n            "internal_note": "x",',
    ))
    verdict = wcc.envelope_wire_conformance(str(envelope_tree))

    assert verdict.half_wired == [(PAYMENT_SEAM, "DECODED")]


def test_the_REQUEST_wire_form_counts_as_an_encode_site_too(envelope_tree):
    """Both declared shapes, not just the response one the live tree happens to use. A seam whose
    crossing is request-borne would otherwise be reported unwired for ever."""
    _write(envelope_tree, "simulation/payment_seam_adapter.py", """
        from interface.contracts.payment_observable_seam import SCHEMA_VERSION

        def encode_wall_request(request):
            return {
                "correlation_id": request.correlation_id,
                "request_type": request.request_type,
                "schema_version": SCHEMA_VERSION,
                "as_of": request.as_of.isoformat(),
                "emitted_at": request.emitted_at.isoformat(),
                "payload": None,
            }
    """)
    verdict = wcc.envelope_wire_conformance(str(envelope_tree))

    assert verdict.wire_borne == [PAYMENT_SEAM]


def test_NULL_CONTROL_a_module_emitting_the_wire_shape_but_importing_NO_seam_credits_nothing(
    envelope_tree,
):
    """Move the sample, not the law. Importing the seam is what ties a wire form to the crossing
    it belongs to -- without it, any module anywhere could green a seam it has never touched."""
    _write(envelope_tree, "simulation/payment_seam_adapter.py", """
        def encode_wall_response(response):
            return {
                "correlation_id": 1, "status": "OK", "schema_version": 1,
                "observed_at": "x", "valid_time": None, "payload": None, "error": None,
            }
    """)
    verdict = wcc.envelope_wire_conformance(str(envelope_tree))

    assert verdict.half_wired == [(PAYMENT_SEAM, "DECODED")]


def test_NULL_CONTROL_importing_the_codec_without_a_decode_name_is_not_a_decode_site(
    envelope_tree,
):
    """The codec exports more than its decoders. Crediting the module edge alone would make every
    importer of the wall protocol a decode site, including one that only reads a constant."""
    _write(envelope_tree, "company/billing/payment_observation_consumer.py", """
        from company.interfaces.wall_protocol import RESPONSE_WIRE_FIELDS
        from interface.contracts.payment_observable_seam import PaymentNotification

        def consume(response):
            return sorted(RESPONSE_WIRE_FIELDS)
    """)
    verdict = wcc.envelope_wire_conformance(str(envelope_tree))

    assert verdict.half_wired == [(PAYMENT_SEAM, "ENCODED")]


def test_NULL_CONTROL_an_unrelated_module_does_not_move_the_channel_C_verdict(envelope_tree):
    before = wcc.envelope_wire_conformance(str(envelope_tree))
    _write(envelope_tree, "company/crm/renewals_book.py", """
        def renew(book):
            return {"a": 1, "b": 2}
    """)
    after = wcc.envelope_wire_conformance(str(envelope_tree))

    assert after == before


def test_INDEPENDENCE_the_wire_form_comes_from_the_CODEC_not_from_the_encoder(envelope_tree):
    """R15 TAUTOLOGY. If the shape were derived from the encoder, no edit to the codec could ever
    move the verdict and the two sides would agree with each other for ever.

    Widening the codec's declared response form ALONE reds the seam -- the encoder is now emitting
    a message the contract no longer describes. Widening BOTH restores it, which is what proves
    the reading tracks the contract rather than either module's own text.
    """
    widened = CODEC_SOURCE.replace('"payload", "error"}', '"payload", "error", "trace_id"}')
    _write(envelope_tree, "company/interfaces/wall_protocol.py", widened)
    assert wcc.envelope_wire_conformance(str(envelope_tree)).half_wired == [
        (PAYMENT_SEAM, "DECODED")
    ]

    _write(envelope_tree, "simulation/payment_seam_adapter.py", WIRE_ENCODER.replace(
        '"error": None,', '"error": None,\n            "trace_id": response.correlation_id,',
    ))
    assert wcc.envelope_wire_conformance(str(envelope_tree)).wire_borne == [PAYMENT_SEAM]


def test_FAIL_CLOSED_an_absent_codec_refuses_rather_than_reporting_every_seam_in_process(
    envelope_tree,
):
    """The loudest of the three, because it is the reassuring failure: with no shapes to match,
    every seam reads as in-process and the report looks like a diligent control finding a lot."""
    (envelope_tree / "company/interfaces/wall_protocol.py").unlink()

    with pytest.raises(wcc.CensusUnavailable, match="unreadable"):
        wcc.envelope_wire_conformance(str(envelope_tree))


def test_FAIL_CLOSED_a_codec_missing_a_wire_field_constant_refuses(envelope_tree):
    _write(envelope_tree, "company/interfaces/wall_protocol.py", """
        RESPONSE_WIRE_FIELDS = frozenset({"correlation_id"})

        def decode_response(message):
            return message
    """)
    with pytest.raises(wcc.CensusUnavailable, match="REQUEST_WIRE_FIELDS"):
        wcc.envelope_wire_conformance(str(envelope_tree))


def test_FAIL_CLOSED_a_computed_wire_field_constant_refuses_rather_than_matching_nothing(
    envelope_tree,
):
    """A constant built at runtime is not readable from the AST, and treating that as an empty
    shape would silently disable the encoder match while the control kept reporting."""
    _write(envelope_tree, "company/interfaces/wall_protocol.py", CODEC_SOURCE.replace(
        'REQUEST_WIRE_FIELDS = frozenset(\n        {"correlation_id", "request_type", '
        '"schema_version", "as_of", "emitted_at", "payload"}\n    )',
        "REQUEST_WIRE_FIELDS = frozenset(RESPONSE_WIRE_FIELDS)",
    ))
    with pytest.raises(wcc.CensusUnavailable, match="REQUEST_WIRE_FIELDS"):
        wcc.envelope_wire_conformance(str(envelope_tree))


def test_FAIL_CLOSED_seams_that_ALL_lose_their_version_constant_refuse(envelope_tree):
    """Deleting `SCHEMA_VERSION` is the cheapest way to make this check pass -- every seam would
    fall into the reported-not-scored bucket and the verdict would be vacuously ok."""
    _write(envelope_tree, "interface/contracts/payment_observable_seam.py", """
        from interface.contracts.wall_envelope import WallResponse
    """)
    with pytest.raises(wcc.CensusUnavailable, match="SCHEMA_VERSION"):
        wcc.envelope_wire_conformance(str(envelope_tree))


def test_ZERO_ENVELOPE_SEAMS_IS_NOT_REFUSED_because_it_is_this_atoms_success_case(tmp_path):
    """A fully paid-down envelope channel reads as clean, not as broken. A control pinned to a
    non-zero count reds on its own success case -- the same doctrine channel D's zero-ports branch
    follows, and the reason neither is written as `assert seams`."""
    root = tmp_path / "repo"
    _write(root, "company/billing/monthly_bill_assembly.py", "def bill():\n    return 1\n")

    verdict = wcc.envelope_wire_conformance(str(root))

    assert verdict.ok and not verdict.wire_borne and not verdict.in_process


def test_channel_C_IS_wired_into_the_commit_gate_and_the_condition_that_allowed_it_is_recorded():
    """A DESIGN decision that could be silently reversed, so it is a test -- now in the ARMED
    direction, which is the edit its own previous form named as the way to arm it.

    WHAT THIS TEST USED TO SAY, kept because the reason it flipped is the record. Passes 19-22
    asserted `"envelope_wire_conformance" not in gate`: two of the three live seams were
    in-process, so gating channel C would have refused EVERY commit in the repo including the ones
    that migrate a seam -- pass 13's landing-order defect, which this file had already learned
    once. The condition was "it becomes a gate in the commit that makes it satisfiable", and pass
    22 was the first commit at which `envelope_wire_conformance_at(rev="HEAD").ok` was True.

    THIS IS THE STRUCTURAL HALF ONLY. That the symbol appears in the gate is not evidence the
    verdict is USED -- a caller that computes a verdict and discards it is precisely the failure
    section 16 exists to close, and it is section 16's mutations, not this assertion, that prove
    the refusal is real. This one guards the cheaper reversal: deleting the call entirely.
    """
    gate = Path("tools/pre_commit_test_gate.py").read_text(encoding="utf-8")
    assert "envelope_wire_conformance_at" in gate, (
        "channel C's conformance check has been unwired from the commit gate -- an un-armed "
        "control that reports a true verdict nothing acts on is a control that cannot fail"
    )


# ── 14. the live tree -- the reading, and deliberately not the answer ─────────────────────────

def test_THE_LIVE_CHANNEL_C_QUESTION_IS_ANSWERABLE():
    """ANSWERABLE, not GREEN, and the distinction is pass 18's: pinning the live verdict would red
    a tree with nothing wrong with it the moment a seam is migrated or added. What must hold is
    that the question can be ASKED of the live wall -- seams derived, versions read, transport
    resolved without a refusal. The answer itself is reported by the CLI and moves with the build.
    """
    verdict = wcc.envelope_wire_conformance_at(worktree=True)
    scored = verdict.wire_borne + verdict.in_process + [s for s, _ in verdict.half_wired]

    assert scored, "no versioned channel C seam on the live tree -- the subject has gone"
    assert verdict.wire_borne, (
        "no live envelope crossing is wire-borne, so the control has never been shown answering "
        "in its own success direction: " + verdict.report()
    )


def test_THE_LIVE_ENVELOPE_MODULE_IS_THE_ONLY_UNVERSIONED_SEAM():
    """The bucket that must not quietly fill up. A NEW seam landing without a `SCHEMA_VERSION`
    would join `wall_envelope` here and be excused from the conformance question entirely, which
    is the one way this control could go silent while still printing."""
    verdict = wcc.envelope_wire_conformance_at(worktree=True)

    assert verdict.unversioned == ["interface.contracts.wall_envelope"], verdict.report()


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


def test_a_seam_wired_on_BOTH_legs_is_wire_borne_and_names_each_leg(two_leg_tree):
    """The success case, and the null control every mutation below is measured against."""
    verdict = wcc.envelope_wire_conformance(str(two_leg_tree))

    assert TWO_LEG_SEAM in verdict.wire_borne, verdict.report()
    assert (TWO_LEG_SEAM, "request", "wire") in verdict.leg_states
    assert (TWO_LEG_SEAM, "response", "wire") in verdict.leg_states
    assert verdict.ok, verdict.report()


def test_MUTATION_THE_ONE_THIS_SECTION_EXISTS_FOR_a_seam_wired_on_ONE_leg_is_not_wire_borne(
    two_leg_tree,
):
    """THE LEG-GRANULARITY MUTATION, run rather than asserted.

    The response leg keeps its encoder and its decoder. Only the REQUEST leg's transport is removed
    -- the company stops calling `encode_request` and hands the payload over as an object, which is
    exactly what an unmigrated leg looks like. The seam still has an encoder and a decoder among its
    importers, so the leg-blind rule this replaced reported it wire-borne and green. This must go
    red, and must name the request leg as the reason.
    """
    _write(two_leg_tree, "company/comms/conversation_generator.py", """
        from company.interfaces.wall_protocol import decode_response
        from interface.contracts.conversation_seam import InboundReply, OutboundMessage

        def send(body, emitted_at):
            return OutboundMessage()

        def observe(wire):
            reply = InboundReply()
            return decode_response(wire), reply
    """)
    verdict = wcc.envelope_wire_conformance(str(two_leg_tree))

    assert TWO_LEG_SEAM not in verdict.wire_borne, verdict.report()
    assert (TWO_LEG_SEAM, "request", "DECODED-only") in verdict.leg_states
    assert (TWO_LEG_SEAM, "response", "wire") in verdict.leg_states
    assert not verdict.ok


def test_MUTATION_removing_the_RESPONSE_legs_transport_reds_the_same_seam(two_leg_tree):
    """The mirror of the above, so the control is shown answering on either leg and not just the
    one the fixture happens to make easiest."""
    _write(two_leg_tree, "simulation/conversation_response.py", """
        from interface.contracts.conversation_seam import SCHEMA_VERSION

        _REQUEST_WIRE_FIELDS = frozenset(
            {"correlation_id", "request_type", "schema_version", "as_of", "emitted_at", "payload"}
        )

        def decode_wire_request(wire):
            if set(wire) != _REQUEST_WIRE_FIELDS:
                raise ValueError("refused")
            return wire

        def respond(request):
            return {"version": SCHEMA_VERSION}
    """)
    verdict = wcc.envelope_wire_conformance(str(two_leg_tree))

    assert TWO_LEG_SEAM not in verdict.wire_borne, verdict.report()
    assert (TWO_LEG_SEAM, "response", "DECODED-only") in verdict.leg_states


def test_MUTATION_wiring_only_a_DORMANT_leg_cannot_flip_a_seam_to_wire_borne(two_leg_tree):
    """THE MIGRATION THIS CONTROL EXISTS TO SIT IN FRONT OF.

    A seam whose live leg is in-process and whose other leg is declared-but-never-sent. Wiring the
    DORMANT leg is the cheapest possible edit that a seam-level count would reward: it adds a real
    encoder and a real decoder for a real declared leg. The verdict must not move, because no
    crossing was migrated -- the live leg is still on the call frame.
    """
    _write(two_leg_tree, "company/comms/conversation_generator.py", """
        from company.interfaces.wall_protocol import encode_request
        from interface.contracts.conversation_seam import InboundReply, OutboundMessage

        def send(body, emitted_at):
            return encode_request(OutboundMessage(), emitted_at)

        def observe(obj):
            return InboundReply(), obj
    """)
    _write(two_leg_tree, "simulation/conversation_response.py", """
        from interface.contracts.conversation_seam import SCHEMA_VERSION

        _REQUEST_WIRE_FIELDS = frozenset(
            {"correlation_id", "request_type", "schema_version", "as_of", "emitted_at", "payload"}
        )

        def decode_wire_request(wire):
            if set(wire) != _REQUEST_WIRE_FIELDS:
                raise ValueError("refused")
            return wire
    """)
    verdict = wcc.envelope_wire_conformance(str(two_leg_tree))

    assert TWO_LEG_SEAM not in verdict.wire_borne, verdict.report()
    assert (TWO_LEG_SEAM, "request", "wire") in verdict.leg_states
    assert (TWO_LEG_SEAM, "response", "IN-PROCESS") in verdict.leg_states


def test_a_DECLARED_leg_this_build_never_sends_is_reported_dormant_and_not_red(two_leg_tree):
    """DORMANT IS A THIRD ANSWER, and it has to be, for `unversioned`'s reason.

    `payment_observable_seam` declares a `CollectionRequest` no module anywhere constructs: the
    contract describes a message this build does not yet exchange. Transport evidence alone cannot
    tell that from an unmigrated crossing -- both are "never encoded, never decoded" -- so scoring
    it would make the control permanently red for a reason its subject cannot fix without deleting
    the contract, which is the shape of a control that gets tuned away.
    """
    _write(two_leg_tree, "company/comms/conversation_generator.py", """
        from company.interfaces.wall_protocol import decode_response
        from interface.contracts.conversation_seam import InboundReply

        def observe(wire):
            reply = InboundReply()
            return decode_response(wire), reply
    """)
    verdict = wcc.envelope_wire_conformance(str(two_leg_tree))

    assert (TWO_LEG_SEAM, "request") in verdict.dormant_legs, verdict.report()
    assert (TWO_LEG_SEAM, "request", "dormant") in verdict.leg_states
    assert TWO_LEG_SEAM in verdict.wire_borne, verdict.report()
    assert "never sends" in verdict.report()


def test_NULL_CONTROL_the_same_leg_becomes_IN_PROCESS_the_moment_its_payload_is_CONSTRUCTED(
    two_leg_tree,
):
    """THE CONTROL THAT ISOLATES DORMANCY FROM THE WRAPPING.

    Identical to the test above in every respect except one statement: somebody builds the request
    payload. Nothing about the transport changes -- there is still no encoder and no decoder for
    that leg. If the dormant reading survived this, "dormant" would just be a name for "unwired"
    and the previous test would be excusing the defect rather than classifying it.
    """
    _write(two_leg_tree, "company/comms/conversation_generator.py", """
        from company.interfaces.wall_protocol import decode_response
        from interface.contracts.conversation_seam import InboundReply, OutboundMessage

        def send(body):
            return OutboundMessage()

        def observe(wire):
            reply = InboundReply()
            return decode_response(wire), reply
    """)
    verdict = wcc.envelope_wire_conformance(str(two_leg_tree))

    assert (TWO_LEG_SEAM, "request") not in verdict.dormant_legs, verdict.report()
    # SCORED and red. The counterparty's mirror still refuses that leg, so its honest state is
    # DECODED-only rather than IN-PROCESS -- what the null control isolates is the move OUT of the
    # unscored bucket, which is the only thing constructing the payload changed.
    assert (TWO_LEG_SEAM, "request", "DECODED-only") in verdict.leg_states
    assert TWO_LEG_SEAM not in verdict.wire_borne


def test_the_COMPANY_side_encoder_is_recognised_though_it_builds_no_dict(two_leg_tree):
    """The company calls `encode_request`; matching encoders by emitted SHAPE alone sees nothing.

    This is not a hypothetical: it is how `conversation_generator.generate_wire_request` is written,
    and a shape-only detector reported that wired leg as DECODED-only. The company end is the one
    that MUST use the codec, so failing to see it red-lists the correct architecture.
    """
    company = (two_leg_tree / "company/comms/conversation_generator.py").read_text()
    assert "{" not in company.split("def send")[1].split("def observe")[0]

    verdict = wcc.envelope_wire_conformance(str(two_leg_tree))

    assert (TWO_LEG_SEAM, "request", "wire") in verdict.leg_states, verdict.report()


def test_the_COUNTERPARTY_side_decoder_is_recognised_though_it_imports_no_codec(two_leg_tree):
    """The mirror case, and the wall is the reason it exists: `simulation/**` may not import
    `company.*`, so the counterparty CANNOT decode through the codec. Recognising decoders only by
    that import would red-list every counterparty refusal for obeying the wall."""
    world = (two_leg_tree / "simulation/conversation_response.py").read_text()
    assert "company" not in world

    verdict = wcc.envelope_wire_conformance(str(two_leg_tree))

    assert (TWO_LEG_SEAM, "response", "wire") in verdict.leg_states, verdict.report()


def test_MUTATION_a_module_that_encodes_AND_mirrors_cannot_certify_its_OWN_leg(two_leg_tree):
    """A WIRE HAS TWO ENDS, and the mirror half of the decoder rule is what makes self-certifying
    reachable: one module emitting the shape and also restating the key set satisfies "an encoder
    exists" and "a decoder exists" by itself, while nothing ever crosses.
    """
    _write(two_leg_tree, "company/comms/conversation_generator.py", """
        from interface.contracts.conversation_seam import InboundReply, OutboundMessage

        _RESPONSE_WIRE_FIELDS = frozenset(
            {"correlation_id", "status", "schema_version", "observed_at", "valid_time",
             "payload", "error"}
        )

        def roundtrip(reply):
            OutboundMessage()
            wire = {
                "correlation_id": reply.correlation_id,
                "status": "OK",
                "schema_version": 1,
                "observed_at": None,
                "valid_time": None,
                "payload": None,
                "error": None,
            }
            assert set(wire) == _RESPONSE_WIRE_FIELDS
            return InboundReply()
    """)
    _write(two_leg_tree, "simulation/conversation_response.py", '"""no transport."""\n')
    verdict = wcc.envelope_wire_conformance(str(two_leg_tree))

    assert TWO_LEG_SEAM not in verdict.wire_borne, verdict.report()
    # ONE END, not none: the module really does emit the shape, so the honest state is ENCODED-only.
    # What the distinctness rule refuses is letting its own mirror count as the far end.
    assert (TWO_LEG_SEAM, "response", "ENCODED-only") in verdict.leg_states


def test_MUTATION_deleting_a_seams_leg_ALIASES_is_reported_rather_than_scored_leniently(
    two_leg_tree,
):
    """THE FAIL-OPEN THIS DESIGN CREATES, named and caught.

    Leg ownership is read from the seam's own `WallRequest[...]` specialisations, so deleting them
    is a one-line edit that makes the leg-aware rule inapplicable. Falling back to the leg-blind
    rule is correct -- it is never weaker than the reading this replaced -- but it must not happen
    QUIETLY, or the cheapest way to silence a red leg becomes deleting the line that declares it.
    """
    _write(two_leg_tree, "interface/contracts/conversation_seam.py", """
        from interface.contracts.wall_envelope import WallRequest, WallResponse

        SCHEMA_VERSION = 1

        class OutboundMessage:
            pass

        class InboundReply:
            pass
    """)
    verdict = wcc.envelope_wire_conformance(str(two_leg_tree))

    assert TWO_LEG_SEAM in verdict.legless, verdict.report()
    assert "legs are unknown" in verdict.report()
    assert not [s for s, _leg, _st in verdict.leg_states if s == TWO_LEG_SEAM]


def test_NULL_CONTROL_an_unrelated_module_does_not_move_any_leg_state(two_leg_tree):
    before = wcc.envelope_wire_conformance(str(two_leg_tree))
    _write(two_leg_tree, "company/crm/renewals_book.py", """
        def renew(book):
            return {"a": 1, "b": 2}
    """)

    assert wcc.envelope_wire_conformance(str(two_leg_tree)) == before


def test_THE_LIVE_SEAMS_ALL_DECLARE_THEIR_LEGS():
    """The `legless` bucket, on the live tree, and the reason it is a live test rather than only a
    fixture one: a real seam dropping its specialisations would silently revert THIS ATOM'S OWN
    control to the leg-blind reading it was built to replace, and every fixture test above would
    still pass."""
    verdict = wcc.envelope_wire_conformance_at(worktree=True)

    assert verdict.legless == (), verdict.report()


def test_THE_LIVE_PER_LEG_QUESTION_IS_ANSWERABLE():
    """ANSWERABLE, not GREEN -- section 14's distinction, one level down. Pinning WHICH legs are
    wired would red the commit that migrates the last one. What must hold is that every scored seam
    resolves to a per-leg state, because a seam falling out of `leg_states` is the reading going
    quiet while the report still prints.
    """
    verdict = wcc.envelope_wire_conformance_at(worktree=True)
    scored = set(verdict.wire_borne + verdict.in_process + [s for s, _ in verdict.half_wired])
    with_legs = {s for s, _leg, _state in verdict.leg_states}

    assert scored, "no versioned channel C seam on the live tree -- the subject has gone"
    assert scored <= with_legs, verdict.report()
    assert any(
        state == "wire" for _s, _leg, state in verdict.leg_states
    ), "no live leg is wire-borne, so the per-leg control has never answered in its success "
    "direction: " + verdict.report()


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

    monkeypatch.setattr(gate, "_index_tree", lambda: "0" * 40)
    monkeypatch.setattr(wcc, "census_at", lambda tree, root: {})
    monkeypatch.setattr(wcc, "load_baseline", lambda *a, **k: {})
    monkeypatch.setattr(wcc, "check", lambda *a, **k: _AlwaysOk())
    monkeypatch.setattr(
        wcc, "wire_conformance_at", lambda **k: wcc.WireVerdict(carrying=["a.py -> 10"], silent=[])
    )
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


def test_NULL_CONTROL_the_GATE_passes_a_conformant_channel_C(monkeypatch):
    """Move the sample, not the law. Without this, every mutation below is satisfied by a gate
    that refuses everything -- which is the failure mode of an over-tightened control, not a
    control."""
    ok, detail = _gate_envelope_branch(monkeypatch, envelope=_conformant_C())
    assert ok, detail
    assert "channel C's 1 of 1 scored seam(s) cross on a wire" in detail


def test_MUTATION_the_GATE_refuses_a_tree_whose_envelope_crossing_is_IN_PROCESS(monkeypatch):
    """The named defect, and the atom's entire subject: an envelope handed over as a Python
    object, whose `schema_version` is never encoded, never decoded and never refused.

    This is the verdict the reporting branch of passes 19-22 printed while returning ok.
    """
    ok, detail = _gate_envelope_branch(
        monkeypatch,
        envelope=wcc.EnvelopeWireVerdict(
            wire_borne=[], half_wired=[],
            in_process=["interface.contracts.flex_observable_seam"],
            unversioned=[],
            leg_states=(
                ("interface.contracts.flex_observable_seam", "response", "IN-PROCESS"),
            ),
        ),
    )
    assert not ok, f"the gate accepted an in-process envelope crossing: {detail}"
    assert "flex_observable_seam" in detail, "the refusal must carry the payload (R5)"
    assert "IN-PROCESS" in detail


def test_MUTATION_the_GATE_refuses_a_HALF_WIRED_seam_which_only_LOOKS_transported(monkeypatch):
    """The worse of the two failures, and the one a laxer gate would credit as progress.

    A seam with an encoder and no decoder puts bytes in the declared wire form that nothing
    version-checks. Scoring it as partial progress -- refusing only `in_process` -- would accept
    exactly the migration that lands its encoder and forgets its far side, which is indistinguish-
    able from a working wire until a counterparty changes version.
    """
    ok, detail = _gate_envelope_branch(
        monkeypatch,
        envelope=wcc.EnvelopeWireVerdict(
            wire_borne=[], half_wired=[("interface.contracts.conversation_seam", "ENCODED")],
            in_process=[], unversioned=[],
            leg_states=(
                ("interface.contracts.conversation_seam", "request", "ENCODED-only"),
            ),
        ),
    )
    assert not ok, f"the gate accepted a half-wired seam: {detail}"
    assert "ENCODED ONLY" in detail and "conversation_seam" in detail


def test_FAIL_CLOSED_the_GATE_refuses_when_channel_Cs_check_itself_raises(monkeypatch):
    """An unavailable check is a FAILED check (R15's third killer pattern).

    `envelope_wire_conformance` raises rather than reporting an empty subject when the codec's
    wire field sets are unreadable or every seam has lost its version constant -- both of which
    are exactly what a tree being quietly emptied looks like. Swallowing that raise would turn the
    loudest failure the enumerator has into the quietest.
    """
    from tools import pre_commit_test_gate as gate

    monkeypatch.setattr(gate, "_index_tree", lambda: "0" * 40)
    monkeypatch.setattr(wcc, "census_at", lambda tree, root: {})
    monkeypatch.setattr(wcc, "load_baseline", lambda *a, **k: {})
    monkeypatch.setattr(wcc, "check", lambda *a, **k: _AlwaysOk())
    monkeypatch.setattr(
        wcc, "wire_conformance_at", lambda **k: wcc.WireVerdict(carrying=["a.py -> 10"], silent=[])
    )

    def _boom(**kwargs):
        raise wcc.CensusUnavailable("every channel C seam has lost its SCHEMA_VERSION")

    monkeypatch.setattr(wcc, "envelope_wire_conformance_at", _boom)
    ok, detail = gate._wall_channel_census_check(["simulation/anything.py"])
    assert not ok
    assert "channel-C wire check RAISED" in detail
    assert "lost its SCHEMA_VERSION" in detail, "the refusal must name what went unread (R5)"


def test_the_UNSCORED_buckets_cannot_wedge_a_lane(monkeypatch):
    """DORMANT and UNVERSIONED legs are facts about a CONTRACT, never defects in a crossing.

    `payment_observable_seam` declares a request leg this build never sends, and `wall_envelope`
    declares no version because it defines the shape rather than crossing it. Scoring either would
    make the gate permanently red for a reason no lane can repair without deleting a contract --
    which is the shape of a control that gets tuned away, and the reason both are reported instead.
    """
    ok, detail = _gate_envelope_branch(
        monkeypatch,
        envelope=wcc.EnvelopeWireVerdict(
            wire_borne=[], half_wired=[], in_process=[],
            unversioned=["interface.contracts.wall_envelope"],
            dormant_legs=(("interface.contracts.payment_observable_seam", "request"),),
            leg_states=(
                ("interface.contracts.payment_observable_seam", "request", "dormant"),
            ),
        ),
    )
    assert ok, f"an unscored bucket refused a commit: {detail}"
    assert "channel C's 0 of 0 scored seam(s)" in detail


def test_the_LEG_BLIND_FALLBACK_is_reported_by_the_GATE_and_not_swallowed(monkeypatch):
    """The quiet-downgrade guard, and it is a REPORT rather than a refusal on purpose.

    Leg ownership is read from a seam's own `WallRequest[...]`/`WallResponse[...]` aliases, so a
    one-line delete makes the leg-aware rule inapplicable and the verdict silently falls back to
    the leg-blind rule of section 13. That fallback is never WEAKER than the reading it replaced,
    so refusing on it would red a tree with nothing wrong with it -- but if the gate says nothing,
    deleting the alias becomes the cheapest way to downgrade this control, and the one place a
    lane would actually have seen it is the one place that stayed green and quiet.
    """
    ok, detail = _gate_envelope_branch(
        monkeypatch,
        envelope=_conformant_C(legless=("interface.contracts.conversation_seam",)),
    )
    assert ok, detail
    assert "LEG-BLIND FALLBACK on 1 seam(s)" in detail
    assert "conversation_seam" in detail


def test_NULL_CONTROL_no_fallback_notice_when_every_seam_owns_its_legs(monkeypatch):
    """Isolates the notice above from the wrapping: same caller, same green verdict, only the
    `legless` bucket moves. Without it, a gate that always printed the notice would pass."""
    ok, detail = _gate_envelope_branch(monkeypatch, envelope=_conformant_C())
    assert ok, detail
    assert "LEG-BLIND FALLBACK" not in detail


def test_THE_LIVE_TREE_PASSES_THE_ARMED_CHANNEL_C_GATE():
    """The condition for arming, asserted on the live tree rather than argued in a record.

    Deliberately the ANSWER and not merely the SUBJECT, which is the opposite of section 14's
    choice and for a reason that only becomes true once the check gates: from this commit on, a
    tree whose channel C is red cannot be committed at all, so a test asserting it is green can no
    longer red a tree that is legitimately mid-migration -- there is no such tree. This is the
    proof that the gate armed above is satisfiable by the repo it was armed in.
    """
    verdict = wcc.envelope_wire_conformance_at(worktree=True)
    assert verdict.ok, verdict.report()
    assert not verdict.legless, (
        "a seam has lost its leg aliases and the control has silently fallen back to the "
        "leg-blind rule: " + verdict.report()
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


def test_the_written_out_digest_and_the_fixtures_surface_actually_correspond(pin_tree):
    """THE NULL CONTROL. Without this, every refusal below could be the literal being wrong
    rather than the mutation being detected, and the whole battery would prove nothing."""
    surface = wcc.declared_surface(str(pin_tree), PIN_SEAM)

    assert wcc.surface_digest(surface) == PIN_TREE_DIGEST


def test_a_surface_matching_its_pinned_version_passes(pin_tree, pinned):
    verdict = wcc.surface_pin_conformance(str(pin_tree))

    assert verdict.pinned == (PIN_SEAM,)
    assert verdict.drifted == () and verdict.unpinned == () and verdict.undeclared == ()
    assert verdict.ok, verdict.report()


def test_MUTATION_a_field_ADDED_without_a_version_bump_is_DRIFTED(pin_tree, pinned):
    """THE DOCTRINE MUTATION -- the exact edit the atom's own record named as the residual risk:
    "I added a field and the test went red / I added the field name to the tuple and it went
    green". Here the tuple edit is made and the version is left at 1. The seam's own controls
    (the mirror against its dataclass, the AST literal guard, the denylist) are all satisfied by
    this edit. This one must not be."""
    _write(pin_tree, "interface/contracts/payment_observable_seam.py", """
        from interface.contracts.wall_envelope import WallResponse

        SCHEMA_VERSION = 1

        OBSERVABLE_PAYLOAD_FIELDS: dict[str, tuple[str, ...]] = {
            "PaymentNotification": (
                "notification_id",
                "amount_gbp",
                "received_on",
                "customer_true_balance_gbp",
            ),
        }
    """)
    verdict = wcc.surface_pin_conformance(str(pin_tree))

    assert [seam for seam, *_ in verdict.drifted] == [PIN_SEAM]
    assert not verdict.ok
    assert "DRIFTED" in verdict.report()
    # The version is untouched -- a version-PRESENCE check stays green through this edit.
    assert wcc._seam_version(str(pin_tree), PIN_SEAM) == 1


def test_MUTATION_a_field_REMOVED_without_a_version_bump_is_also_DRIFTED(pin_tree, pinned):
    """NARROWING IS A SCHEMA CHANGE TOO, and it breaks the counterparty rather than the wall --
    a decoder that requires `amount_gbp` under v1 now gets v1 without it. A ratchet that only
    fired on growth would call this repair."""
    _write(pin_tree, "interface/contracts/payment_observable_seam.py", """
        from interface.contracts.wall_envelope import WallResponse

        SCHEMA_VERSION = 1

        OBSERVABLE_PAYLOAD_FIELDS: dict[str, tuple[str, ...]] = {
            "PaymentNotification": (
                "notification_id",
                "received_on",
            ),
        }
    """)
    verdict = wcc.surface_pin_conformance(str(pin_tree))

    assert [seam for seam, *_ in verdict.drifted] == [PIN_SEAM]
    assert not verdict.ok


def test_a_REORDERED_surface_is_NOT_drift_because_the_wire_form_is_a_mapping(pin_tree, pinned):
    """THE DELIBERATE NON-FIRING CASE. Field order is not a schema fact -- the envelope carries a
    mapping. A control that reddened on a cosmetic re-order would be tuned away, and the real
    edit would go with it."""
    _write(pin_tree, "interface/contracts/payment_observable_seam.py", """
        from interface.contracts.wall_envelope import WallResponse

        SCHEMA_VERSION = 1

        OBSERVABLE_PAYLOAD_FIELDS: dict[str, tuple[str, ...]] = {
            "PaymentNotification": (
                "received_on",
                "notification_id",
                "amount_gbp",
            ),
        }
    """)
    verdict = wcc.surface_pin_conformance(str(pin_tree))

    assert verdict.pinned == (PIN_SEAM,)
    assert verdict.ok, verdict.report()


def test_MUTATION_bumping_the_version_without_RE_PINNING_is_UNPINNED(pin_tree, pinned):
    """The other half of the same discipline. A bumped version is a DECLARED schema change and is
    allowed -- but it must not be allowed to pass unnoticed, or the pin table decays into a record
    of what someone once thought while the wire says something else."""
    _write(pin_tree, "interface/contracts/payment_observable_seam.py", """
        from interface.contracts.wall_envelope import WallResponse

        SCHEMA_VERSION = 2

        OBSERVABLE_PAYLOAD_FIELDS: dict[str, tuple[str, ...]] = {
            "PaymentNotification": (
                "notification_id",
                "amount_gbp",
                "received_on",
            ),
        }
    """)
    verdict = wcc.surface_pin_conformance(str(pin_tree))

    assert verdict.unpinned == ((PIN_SEAM, 2),)
    assert not verdict.ok
    assert "UNPINNED" in verdict.report()


def test_FAIL_CLOSED_a_seam_absent_from_the_pins_is_UNPINNED_and_not_skipped(
    pin_tree, monkeypatch
):
    """R15 FAIL-OPEN. A `.get()` that returned None and `continue`d would make the check pass
    vacuously on exactly the seam nobody has pinned -- the unbounded case, reported as green.
    A fourth seam landing tomorrow must land RED."""
    monkeypatch.setattr(wcc, "SURFACE_PINS", {})

    verdict = wcc.surface_pin_conformance(str(pin_tree))

    assert verdict.unpinned == ((PIN_SEAM, 1),)
    assert verdict.pinned == ()
    assert not verdict.ok


def test_FAIL_CLOSED_a_versioned_seam_with_a_COMPUTED_surface_is_UNDECLARED(pin_tree, pinned):
    """R15 TAUTOLOGY, at the subject's end. A surface derived from the dataclasses it certifies
    widens whenever they widen. The census cannot pin such a thing, and "cannot read it" must
    read as a failure, not as absence."""
    _write(pin_tree, "interface/contracts/payment_observable_seam.py", """
        from dataclasses import fields

        from interface.contracts.wall_envelope import WallResponse

        SCHEMA_VERSION = 1

        OBSERVABLE_PAYLOAD_FIELDS = {
            payload.__name__: tuple(f.name for f in fields(payload))
            for payload in ()
        }
    """)
    verdict = wcc.surface_pin_conformance(str(pin_tree))

    assert verdict.undeclared == (PIN_SEAM,)
    assert not verdict.ok
    assert "UNDECLARED" in verdict.report()


def test_the_VERSIONLESS_envelope_module_is_reported_and_not_scored(pin_tree, pinned):
    """`wall_envelope` defines the shape and is not a crossing -- it has no version to mean
    anything by. Scoring it would keep this red for a reason its subject cannot fix; dropping it
    silently would hide a new seam that forgot its version."""
    verdict = wcc.surface_pin_conformance(str(pin_tree))

    assert verdict.versionless == ("interface.contracts.wall_envelope",)
    assert verdict.ok
    assert "no version to mean anything by" in verdict.report()


def test_FAIL_CLOSED_an_unreadable_seam_RAISES_rather_than_reading_as_undeclared(pin_tree):
    """R15 FAIL-SILENT. "I could not parse it" and "it declares nothing" are different facts and
    only one of them is the seam's own doing."""
    (pin_tree / "interface/contracts/payment_observable_seam.py").write_text(
        "def broken(:\n", encoding="utf-8"
    )
    with pytest.raises(wcc.CensusUnavailable):
        wcc.declared_surface(str(pin_tree), PIN_SEAM)


def test_the_pins_are_LITERAL_and_not_derived_from_the_surfaces_they_pin():
    """R15 TAUTOLOGY, at the instrument's end -- the same guard each contract carries over its
    own closed set. A pin computed from the declaration would move with it and could never fire,
    and the separation between instrument and subject is the whole control."""
    import ast

    source = (Path(wcc.__file__).parent.parent / "tools" / "wall_channel_census.py").read_text()
    node = next(
        n for n in ast.walk(ast.parse(source))
        if isinstance(n, ast.AnnAssign) and getattr(n.target, "id", None) == "SURFACE_PINS"
    )
    assert isinstance(node.value, ast.Dict), "SURFACE_PINS must be a literal declaration"
    for entry in node.value.values:
        assert isinstance(entry, ast.Tuple), "each pin must be a literal (version, digest)"
        version, digest = entry.elts
        assert isinstance(version, ast.Constant) and isinstance(version.value, int)
        assert isinstance(digest, ast.Constant) and isinstance(digest.value, str)


def test_the_REAL_seams_are_pinned_and_still_mean_what_their_versions_say():
    """The live reading, against the real tree rather than a fixture. This is what makes the
    pins above real values rather than decoration -- if a surface moves without its version, this
    is the test that reds, and the CLI returns 1 with it."""
    verdict = wcc.surface_pin_conformance(str(wcc.PROJECT_DIR))

    assert verdict.ok, verdict.report()
    assert len(verdict.pinned) == 3, verdict.report()
    assert not verdict.unpinned, (
        "a channel C seam has landed with no pin, so its observable surface can widen "
        "silently: " + verdict.report()
    )


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


@pytest.fixture()
def belt_tree(tmp_path: Path) -> Path:
    """One versioned seam declaring a literal denylist, one module refusing on it.

    One seam on purpose, the `pin_tree` fixture's reason: with exactly one, "the mutation
    removed the belt" and "the check never found a seam" cannot be confused.
    """
    root = tmp_path / "repo"
    _write(root, "interface/contracts/wall_envelope.py", '"""the envelope shape."""\n')
    _write(root, "interface/contracts/payment_observable_seam.py", _belt_seam_source())
    _write(root, "simulation/payment_seam_adapter.py", _ENFORCING_ADAPTER)
    return root


def test_the_fixtures_belt_is_declared_AND_refused_on_so_the_green_case_is_real(belt_tree):
    """THE NULL CONTROL. Without it every refusal below could be the fixture never having had a
    working belt in the first place, and the battery would prove nothing about detection."""
    assert wcc.declared_second_belt(str(belt_tree), BELT_SEAM) == ("result", "ability")
    assert wcc.belt_enforcers(str(belt_tree), BELT_SEAM) == ("simulation/payment_seam_adapter.py",)


def test_a_seam_with_an_enforced_denylist_passes(belt_tree):
    verdict = wcc.second_belt_conformance(str(belt_tree))

    assert verdict.belted == ((BELT_SEAM, 2, ("simulation/payment_seam_adapter.py",)),)
    assert verdict.unbelted == () and verdict.unenforced == ()
    assert verdict.ok, verdict.report()


def test_MUTATION_the_seam_declares_NO_denylist_and_is_UNBELTED(belt_tree):
    """THE DOCTRINE MUTATION -- the exact state pass 26 found on the real payment seam, where
    the closed set was the only belt on the widest of the three crossings. The version is
    untouched and the closed set is untouched, so the surface pins stay green through this."""
    _write(belt_tree, "interface/contracts/payment_observable_seam.py", """
        from interface.contracts.wall_envelope import WallResponse

        SCHEMA_VERSION = 1

        OBSERVABLE_PAYLOAD_FIELDS: dict[str, tuple[str, ...]] = {
            "PaymentNotification": ("notification_id", "amount_gbp"),
        }
    """)
    verdict = wcc.second_belt_conformance(str(belt_tree))

    assert verdict.unbelted == (BELT_SEAM,)
    assert not verdict.ok
    assert "UNBELTED" in verdict.report()
    assert wcc._seam_version(str(belt_tree), BELT_SEAM) == 1


def test_FAIL_OPEN_an_EMPTY_denylist_is_UNBELTED_and_not_a_belt(belt_tree):
    """R15 FAIL-OPEN. A tuple with no names in it refuses nothing, and it is what "delete the
    awkward entries" leaves behind -- a declaration that reads as present to any check that only
    asks whether the constant exists."""
    _write(belt_tree, "interface/contracts/payment_observable_seam.py", _belt_seam_source("()"))

    verdict = wcc.second_belt_conformance(str(belt_tree))

    assert verdict.unbelted == (BELT_SEAM,)
    assert not verdict.ok


def test_FAIL_CLOSED_a_COMPUTED_denylist_is_UNBELTED(belt_tree):
    """R15 TAUTOLOGY at the subject's end, and the same reading `declared_surface` takes: a
    denylist derived from the thing it guards moves with it. The census cannot vouch for what it
    cannot read, and unreadable must not score as present."""
    _write(
        belt_tree,
        "interface/contracts/payment_observable_seam.py",
        _belt_seam_source("tuple(n for n in _TRUTH_NAMES)"),
    )
    verdict = wcc.second_belt_conformance(str(belt_tree))

    assert verdict.unbelted == (BELT_SEAM,)
    assert not verdict.ok


def test_MUTATION_a_denylist_NOTHING_refuses_on_is_UNENFORCED(belt_tree):
    """THE SECOND FAIL-OPEN, and the one a symbol-presence check cannot see. The declaration is
    real, non-empty and literal; the codec imports it and never acts on it. A denylist nothing
    reads is a comment, and the seam's own tests would still pass over it."""
    _write(belt_tree, "simulation/payment_seam_adapter.py", """
        from interface.contracts.payment_observable_seam import FORBIDDEN_TRUTH_FIELDS

        KNOWN_LEAKS = FORBIDDEN_TRUTH_FIELDS

        def encode(payload, names):
            return payload
    """)
    verdict = wcc.second_belt_conformance(str(belt_tree))

    assert verdict.unenforced == ((BELT_SEAM, 2),)
    assert verdict.belted == ()
    assert not verdict.ok
    assert "UNENFORCED" in verdict.report()


def test_a_belt_only_the_TESTS_consult_is_UNENFORCED(belt_tree):
    """Tests are out of scope by construction (`CENSUS_DIRS` has no `tests/`), and this pins that
    it is the right scope rather than an oversight: a belt checked only in a test stops nothing
    at the crossing, which is where the payload actually goes past."""
    # The adapter still IMPORTS the seam -- otherwise the seam leaves channel C altogether and
    # this would pass for the wrong reason, measuring a crossing that no longer exists.
    _write(belt_tree, "simulation/payment_seam_adapter.py", """
        from interface.contracts.payment_observable_seam import SCHEMA_VERSION

        def encode(payload, names):
            return payload
    """)
    _write(belt_tree, "tests/simulation/test_payment_seam_adapter.py", _ENFORCING_ADAPTER)

    verdict = wcc.second_belt_conformance(str(belt_tree))

    assert verdict.unenforced == ((BELT_SEAM, 2),)
    assert not verdict.ok


def test_an_enforcer_that_imports_the_belt_from_ANOTHER_seam_does_not_count(belt_tree):
    """The claim carries a LOCATION. Two seams can both name their denylist
    `FORBIDDEN_TRUTH_FIELDS`, so a check that matched on the NAME alone would let one seam's
    enforcement vouch for another's -- and the unbelted seam is exactly the one that would be
    vouched for."""
    _write(belt_tree, "interface/contracts/other_seam.py", """
        SCHEMA_VERSION = 1

        OBSERVABLE_PAYLOAD_FIELDS: dict[str, tuple[str, ...]] = {"Other": ("a",)}

        FORBIDDEN_TRUTH_FIELDS: tuple[str, ...] = ("truth",)
    """)
    # The adapter imports BOTH seams -- the payment one so the crossing still exists to be
    # scored, the other one for the belt it refuses on. That is the confusable shape.
    _write(belt_tree, "simulation/payment_seam_adapter.py", """
        from interface.contracts.other_seam import FORBIDDEN_TRUTH_FIELDS
        from interface.contracts.payment_observable_seam import SCHEMA_VERSION

        def encode(payload, names):
            if set(names) & set(FORBIDDEN_TRUTH_FIELDS):
                raise ValueError(names)
            return payload
    """)
    assert wcc.belt_enforcers(str(belt_tree), BELT_SEAM) == ()

    verdict = wcc.second_belt_conformance(str(belt_tree))

    assert (BELT_SEAM, 2) in verdict.unenforced
    assert not verdict.ok


def test_the_VERSIONLESS_envelope_module_is_reported_and_not_scored_by_the_belt(belt_tree):
    """`wall_envelope` defines the shape and is not a crossing, so it has nothing to leak. Same
    honest member the wire check and the surface pins both carry."""
    verdict = wcc.second_belt_conformance(str(belt_tree))

    assert verdict.versionless == ("interface.contracts.wall_envelope",)
    assert "not a crossing this question is about" in verdict.report()


def test_FAIL_CLOSED_an_unreadable_seam_RAISES_rather_than_reading_as_unbelted(belt_tree):
    """R15 FAIL-SILENT. "I could not parse it" and "it declares no belt" are different facts and
    only one of them is the seam's own doing -- and the wrong one is silently greener."""
    (belt_tree / "interface/contracts/payment_observable_seam.py").write_text(
        "def broken(:\n", encoding="utf-8"
    )
    with pytest.raises(wcc.CensusUnavailable):
        wcc.declared_second_belt(str(belt_tree), BELT_SEAM)


def test_the_REAL_seams_all_carry_a_belt_something_refuses_on():
    """The live reading, against the real tree rather than a fixture. This is what makes the
    check a value rather than decoration -- a fourth seam landing without a belt reds here, and
    the CLI returns 1 with it."""
    verdict = wcc.second_belt_conformance(str(wcc.PROJECT_DIR))

    assert verdict.ok, verdict.report()
    assert len(verdict.belted) == 3, verdict.report()
    assert not verdict.unbelted, (
        "a channel C seam has landed with no truth-field denylist, so its closed set is its "
        "only belt: " + verdict.report()
    )


def test_the_belt_check_is_part_of_the_CLIs_exit_code():
    """R11's no-orphan-transitions rule, applied to a control: a check whose red changes nothing
    is not a gate. Read off the source rather than by running the CLI, which takes minutes."""
    import ast

    source = (Path(wcc.__file__).parent.parent / "tools" / "wall_channel_census.py").read_text()
    returns = [
        ast.unparse(n.value) for n in ast.walk(ast.parse(source))
        if isinstance(n, ast.Return) and n.value is not None
    ]
    assert any("second_belt.ok" in r for r in returns), (
        "second_belt_conformance reports but does not gate -- its red would be a printed line "
        "nothing acts on"
    )
