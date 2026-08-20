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


def test_the_fixtures_belt_is_declared_AND_refused_on_so_the_green_case_is_real(belt_tree):
    """THE NULL CONTROL. Without it every refusal below could be the fixture never having had a
    working belt in the first place, and the battery would prove nothing about detection."""
    assert wcc.declared_second_belt(str(belt_tree), BELT_SEAM) == ("result", "ability")
    assert wcc.belt_enforcers(str(belt_tree), BELT_SEAM) == (_CONSUMER_REL, _ADAPTER_REL)


def test_the_two_SIDES_are_separately_observable_in_the_fixture(belt_tree):
    """THE SECOND NULL CONTROL, and the one the per-side mutations below rest on. If both
    enforcers landed in the same bucket, "the company side went missing" and "the world side
    went missing" would be the same observation and neither mutation would prove anything."""
    sides = wcc.belt_enforcer_sides(str(belt_tree), BELT_SEAM)

    assert sides.company == (_CONSUMER_REL,)
    assert sides.world == (_ADAPTER_REL,)
    assert sides.neither == ()
    assert sides.both and sides.missing == ""


def test_a_seam_with_a_denylist_enforced_on_BOTH_SIDES_passes(belt_tree):
    verdict = wcc.second_belt_conformance(str(belt_tree))

    assert verdict.belted == ((BELT_SEAM, 2, (_CONSUMER_REL,), (_ADAPTER_REL,)),)
    assert verdict.unbelted == () and verdict.unenforced == () and verdict.one_sided == ()
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


_INERT_CODEC = """
    from interface.contracts.payment_observable_seam import FORBIDDEN_TRUTH_FIELDS

    KNOWN_LEAKS = FORBIDDEN_TRUTH_FIELDS

    def crosses(payload, names):
        return payload
"""


def test_MUTATION_a_denylist_NOTHING_refuses_on_is_UNENFORCED(belt_tree):
    """THE SECOND FAIL-OPEN, and the one a symbol-presence check cannot see. The declaration is
    real, non-empty and literal; both codecs import it and neither acts on it. A denylist
    nothing reads is a comment, and the seam's own tests would still pass over it."""
    _write(belt_tree, _ADAPTER_REL, _INERT_CODEC)
    _write(belt_tree, _CONSUMER_REL, _INERT_CODEC)

    verdict = wcc.second_belt_conformance(str(belt_tree))

    assert verdict.unenforced == ((BELT_SEAM, 2, ()),)
    assert verdict.belted == () and verdict.one_sided == ()
    assert not verdict.ok
    assert "UNENFORCED" in verdict.report()


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


def test_MUTATION_a_belt_refused_on_only_by_the_WORLD_side_is_ONE_SIDED(belt_tree):
    """THE DOCTRINE MUTATION -- the exact state of the real `conversation_seam` at HEAD before
    this pass, reproduced in a fixture. The declaration is real, non-empty and literal, and the
    ENCODE side genuinely refuses on it, so every per-seam question above stays green through
    this. What is missing is the end that decides whether a leak is BELIEVED, which at go-live
    is the only end of this crossing the company still owns."""
    _write(belt_tree, _CONSUMER_REL, _INERT_CODEC)

    verdict = wcc.second_belt_conformance(str(belt_tree))

    assert verdict.one_sided == ((BELT_SEAM, 2, "company", (_ADAPTER_REL,)),)
    assert verdict.belted == () and verdict.unbelted == () and verdict.unenforced == ()
    assert not verdict.ok
    assert "ONE-SIDED" in verdict.report()
    assert "nothing on the company side" in verdict.report()


def test_MUTATION_a_belt_refused_on_only_by_the_COMPANY_side_is_ONE_SIDED(belt_tree):
    """THE MIRROR, and the reason the test above measures the SIDE rather than the file. A world
    that can ship an unrefused trait field is a defect in the same class even when the company
    would catch it, because the encode end is what stops a leak being SENT."""
    _write(belt_tree, _ADAPTER_REL, _INERT_CODEC)

    verdict = wcc.second_belt_conformance(str(belt_tree))

    assert verdict.one_sided == ((BELT_SEAM, 2, "world", (_CONSUMER_REL,)),)
    assert verdict.belted == ()
    assert not verdict.ok
    assert "nothing on the world side" in verdict.report()


def test_FAIL_CLOSED_a_refusal_by_a_BRIDGE_module_is_on_NEITHER_side(belt_tree):
    """R15 FAIL-OPEN, at the boundary of the new question. `belt_enforcers` walks `CENSUS_DIRS`,
    which includes `tools` / `background` / `interface` because channel D's ports live there --
    so a check that counted "two enforcers" rather than "two SIDES" would read this tree as
    fully belted. The payload does not travel through a bridge module on its way from the world
    to the company, so its refusal defends neither side, and the bare side stays bare."""
    _write(belt_tree, _CONSUMER_REL, _INERT_CODEC)
    _write(belt_tree, "tools/payment_wire_audit.py", _ENFORCING_BRIDGE)

    sides = wcc.belt_enforcer_sides(str(belt_tree), BELT_SEAM)
    assert sides.neither == ("tools/payment_wire_audit.py",)
    assert sides.company == ()

    verdict = wcc.second_belt_conformance(str(belt_tree))
    assert verdict.one_sided == ((BELT_SEAM, 2, "company", (_ADAPTER_REL,)),)
    assert not verdict.ok


def test_a_belt_refused_on_ONLY_off_the_wall_is_UNENFORCED_and_the_report_says_where(belt_tree):
    """The same fail-closed reading with BOTH SIDES inert. `unenforced` is the honest bucket --
    nothing on either side refuses -- but the off-wall refusal is a real fact and is reported,
    so the reader is not sent hunting for a `FORBIDDEN_TRUTH_FIELDS` the grep will find."""
    _write(belt_tree, _ADAPTER_REL, _INERT_CODEC)
    _write(belt_tree, _CONSUMER_REL, _INERT_CODEC)
    _write(belt_tree, "tools/payment_wire_audit.py", _ENFORCING_BRIDGE)

    verdict = wcc.second_belt_conformance(str(belt_tree))

    assert verdict.unenforced == ((BELT_SEAM, 2, ("tools/payment_wire_audit.py",)),)
    assert not verdict.ok
    assert "refused only off-wall by tools/payment_wire_audit.py" in verdict.report()


def test_the_SIDES_come_from_the_WALLS_OWN_definition_of_its_two_sides():
    """INDEPENDENCE. The side split is `tools.epistemic_wall`'s `COMPANY_PACKAGES` /
    `SIM_PACKAGES` -- the constants the wall walker itself is built on -- and not a list this
    census respells. A package added to a side there is a side here the same day; a census with
    its own copy would drift, and drift silently toward green (an unrecognised package reads as
    neither side, which is the fail-closed direction only while the two agree)."""
    from tools.epistemic_wall import COMPANY_PACKAGES, SIM_PACKAGES

    assert wcc.COMPANY_PACKAGES is COMPANY_PACKAGES
    assert wcc.SIM_PACKAGES is SIM_PACKAGES
    for pkg in COMPANY_PACKAGES:
        assert wcc._enforcer_side(f"{pkg}/whatever/mod.py") == "company"
    for pkg in SIM_PACKAGES:
        assert wcc._enforcer_side(f"{pkg}/whatever/mod.py") == "world"
    for pkg in ("tools", "background", "interface"):
        assert wcc._enforcer_side(f"{pkg}/whatever/mod.py") is None


def test_a_belt_only_the_TESTS_consult_is_UNENFORCED(belt_tree):
    """Tests are out of scope by construction (`CENSUS_DIRS` has no `tests/`), and this pins that
    it is the right scope rather than an oversight: a belt checked only in a test stops nothing
    at the crossing, which is where the payload actually goes past."""
    # Both codecs still IMPORT the seam -- otherwise the seam leaves channel C altogether and
    # this would pass for the wrong reason, measuring a crossing that no longer exists.
    version_only = """
        from interface.contracts.payment_observable_seam import SCHEMA_VERSION

        def crosses(payload, names):
            return payload
    """
    _write(belt_tree, _ADAPTER_REL, version_only)
    _write(belt_tree, _CONSUMER_REL, version_only)
    _write(belt_tree, "tests/simulation/test_payment_seam_adapter.py", _ENFORCING_ADAPTER)
    _write(belt_tree, "tests/company/billing/test_payment_consumer.py", _ENFORCING_CONSUMER)

    verdict = wcc.second_belt_conformance(str(belt_tree))

    assert verdict.unenforced == ((BELT_SEAM, 2, ()),)
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
    # Both codecs import BOTH seams -- the payment one so the crossing still exists to be
    # scored, the other one for the belt they refuse on. That is the confusable shape, and it is
    # applied to each side so neither can vouch for the other either.
    borrowed_belt = """
        from interface.contracts.other_seam import FORBIDDEN_TRUTH_FIELDS
        from interface.contracts.payment_observable_seam import SCHEMA_VERSION

        def crosses(payload, names):
            if set(names) & set(FORBIDDEN_TRUTH_FIELDS):
                raise ValueError(names)
            return payload
    """
    _write(belt_tree, _ADAPTER_REL, borrowed_belt)
    _write(belt_tree, _CONSUMER_REL, borrowed_belt)
    assert wcc.belt_enforcers(str(belt_tree), BELT_SEAM) == ()

    verdict = wcc.second_belt_conformance(str(belt_tree))

    assert (BELT_SEAM, 2, ()) in verdict.unenforced
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


def test_the_REAL_seams_all_carry_a_belt_BOTH_LEGS_refuse_on():
    """The live reading, against the real tree rather than a fixture. This is what makes the
    check a value rather than decoration -- a fourth seam landing without a belt reds here, a
    third seam losing a SIDE reds here, and the CLI returns 1 with either."""
    verdict = wcc.second_belt_conformance(str(wcc.PROJECT_DIR))

    assert verdict.ok, verdict.report()
    assert len(verdict.belted) == 3, verdict.report()
    assert not verdict.unbelted, (
        "a channel C seam has landed with no truth-field denylist, so its closed set is its "
        "only belt: " + verdict.report()
    )
    assert not verdict.one_sided, (
        "a channel C seam is belted on one side of the wall only -- and if the bare side is the "
        "company's, it is the end of the crossing that survives go-live: " + verdict.report()
    )
    # Named rather than counted: a per-side claim carries a location, and this is the assertion
    # that would red if a repair moved to a module that merely happens to sit on the right side.
    sides = {seam: (company, world) for seam, _n, company, world in verdict.belted}
    assert sides["interface.contracts.conversation_seam"] == (
        ("company/comms/susceptibility_estimator.py",),
        ("simulation/conversation_response.py",),
    ), verdict.report()


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


def test_a_world_class_satisfying_a_business_Protocol_is_read_as_a_crossing(protocol_tree):
    verdict = wcc.structural_satisfaction(str(protocol_tree))
    assert verdict.crossings == {
        "company/billing/monthly_bill_assembly.py -> ReadArrival": (
            "simulation/meter_reads.py::MeterReadEvent",
        )
    }, verdict.report()
    assert verdict.internal == ()


def test_a_clean_tree_passes_its_own_satisfaction_baseline(protocol_tree):
    drift = wcc.check_satisfaction(
        wcc.structural_satisfaction(str(protocol_tree)), _satisfaction_baseline(protocol_tree)
    )
    assert drift.ok, drift.report()


def test_MUTATION_the_world_renaming_a_field_is_DRIFT_and_fails(protocol_tree):
    """THE DEFECT THIS CONTROL EXISTS FOR, and the one nothing else in the repo can see.

    The company still declares the Protocol; the world class no longer has `status`. Structural
    typing means no import fails and no decode fails -- the company just reads an attribute that
    is not there any more.
    """
    baseline = _satisfaction_baseline(protocol_tree)
    _write(protocol_tree, "simulation/meter_reads.py", """
        class MeterReadEvent:
            customer_id: str
            read_status: str
            consecutive_estimated_count: int
    """)
    drift = wcc.check_satisfaction(wcc.structural_satisfaction(str(protocol_tree)), baseline)
    assert not drift.ok, drift.report()
    assert drift.drifted == {
        "company/billing/monthly_bill_assembly.py -> ReadArrival": (
            "simulation/meter_reads.py::MeterReadEvent",
        )
    }
    assert not drift.appeared, "a rename is drift, not a new crossing: " + drift.report()


def test_MUTATION_a_NEW_world_satisfier_is_an_unexamined_crossing_and_fails(protocol_tree):
    baseline = _satisfaction_baseline(protocol_tree)
    _write(protocol_tree, "simulation/second_feed.py", """
        class SecondReadEvent:
            status: str
            consecutive_estimated_count: int
    """)
    drift = wcc.check_satisfaction(wcc.structural_satisfaction(str(protocol_tree)), baseline)
    assert not drift.ok, drift.report()
    assert drift.appeared == {
        "company/billing/monthly_bill_assembly.py -> ReadArrival": (
            "simulation/second_feed.py::SecondReadEvent",
        )
    }
    assert not drift.drifted, "the original satisfier still satisfies: " + drift.report()


def test_FAIL_OPEN_an_empty_world_population_refuses_rather_than_reporting_no_crossings(
    protocol_tree,
):
    """THIS CONTROL'S FAIL-OPEN, named and closed.

    With no world classes every Protocol reads as company-internal, which prints the reassuring
    answer -- "nothing crosses structurally" -- from a measurement that looked at nothing.
    """
    (protocol_tree / "simulation" / "meter_reads.py").unlink()
    with pytest.raises(wcc.CensusUnavailable, match="empty satisfier population"):
        wcc.structural_satisfaction(str(protocol_tree))


def test_FAIL_CLOSED_a_memberless_Protocol_refuses_rather_than_being_satisfied_by_everything(
    protocol_tree,
):
    """Emptying the Protocol is the cheapest way to make this check say whatever you want: a
    requirement of no members is a subset of every class in the tree."""
    _write(protocol_tree, "company/billing/monthly_bill_assembly.py", """
        from typing import Protocol


        class ReadArrival(Protocol):
            ...
    """)
    with pytest.raises(wcc.CensusUnavailable, match="declare no members"):
        wcc.structural_satisfaction(str(protocol_tree))


def test_NULL_CONTROL_a_COMPANY_side_class_satisfying_the_Protocol_is_NOT_a_crossing(
    protocol_tree,
):
    """Moves the sample, not the law. Without this pin the control is satisfiable by a company
    test double and would report crossings that do not exist -- and `SATISFIER_DIRS` would be
    free to widen to `WALL_DIRS`, which contains both sides of the wall."""
    baseline = _satisfaction_baseline(protocol_tree)
    _write(protocol_tree, "company/billing/fake_feed.py", """
        class CompanySideDouble:
            status: str
            consecutive_estimated_count: int
    """)
    verdict = wcc.structural_satisfaction(str(protocol_tree))
    assert verdict.crossings == baseline, verdict.report()
    assert wcc.check_satisfaction(verdict, baseline).ok


def test_NULL_CONTROL_an_unrelated_world_class_does_not_become_a_satisfier(protocol_tree):
    baseline = _satisfaction_baseline(protocol_tree)
    _write(protocol_tree, "simulation/weather.py", """
        class WeatherHour:
            temperature_c: float
    """)
    assert wcc.check_satisfaction(
        wcc.structural_satisfaction(str(protocol_tree)), baseline
    ).ok


def test_a_Protocol_that_LEAVES_the_tree_is_paid_down_and_passes(protocol_tree):
    """The success case must not red, or the control gets relaxed and takes the real reds with
    it. A satisfier vanishing WITH its Protocol is a paydown; vanishing WITHOUT it is drift."""
    baseline = _satisfaction_baseline(protocol_tree)
    _write(protocol_tree, "company/billing/monthly_bill_assembly.py", '"""no Protocol now."""\n')
    drift = wcc.check_satisfaction(wcc.structural_satisfaction(str(protocol_tree)), baseline)
    assert drift.ok, drift.report()
    assert drift.paid_down == ("company/billing/monthly_bill_assembly.py -> ReadArrival",)


def test_FAIL_CLOSED_a_baseline_with_no_satisfaction_object_raises(tmp_path):
    path = tmp_path / "no_key.json"
    path.write_text(json.dumps({"frozen": {}}), encoding="utf-8")
    with pytest.raises(wcc.CensusUnavailable, match="has no `E_structural_satisfaction`"):
        wcc.load_satisfaction_baseline(path)


def test_THE_LIVE_WALL_HAS_NOT_DRIFTED():
    """The shipped reading, against the shipped baseline. This is the one that gates."""
    verdict = wcc.structural_satisfaction_at(worktree=True)
    drift = wcc.check_satisfaction(verdict, wcc.load_satisfaction_baseline())
    assert drift.ok, drift.report()


def test_the_satisfaction_check_is_part_of_the_CLIs_exit_code():
    """R11's no-orphan-transitions rule: a check whose red changes nothing is not a gate."""
    import ast

    source = (Path(wcc.__file__).parent.parent / "tools" / "wall_channel_census.py").read_text()
    returns = [
        ast.unparse(n.value) for n in ast.walk(ast.parse(source))
        if isinstance(n, ast.Return) and n.value is not None
    ]
    assert any("drift.ok" in r for r in returns), (
        "structural_satisfaction reports but does not gate -- its red would be a printed line "
        "nothing acts on"
    )


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


def test_NULL_CONTROL_the_GATE_passes_a_conformant_channel_E(monkeypatch):
    """Move the sample, not the law: without this, every mutation below is satisfied by a gate
    that refuses everything."""
    ok, detail = _gate_satisfaction_branch(
        monkeypatch, verdict=_conformant_E(), baseline=dict(_conformant_E().crossings)
    )
    assert ok, detail
    assert "channel E's 1 structural crossing(s)" in detail, detail


def test_MUTATION_the_GATE_refuses_a_tree_whose_world_class_DRIFTED(monkeypatch):
    """THE DEFECT, at the gate: the Protocol is still declared, the frozen satisfier no longer
    satisfies it, and no import or decode anywhere in the repo breaks."""
    ok, detail = _gate_satisfaction_branch(
        monkeypatch,
        verdict=wcc.SatisfactionVerdict(crossings={}, internal=("company/b.py -> Feed",)),
        baseline=dict(_conformant_E().crossings),
    )
    assert not ok, "a drifted structural crossing was allowed to commit"
    assert "DRIFTED on channel E" in detail and "simulation/w.py::Impl" in detail, (
        "the refusal must carry the diagnostic payload (R5): " + detail
    )


def test_MUTATION_the_GATE_refuses_an_unexamined_NEW_structural_crossing(monkeypatch):
    ok, detail = _gate_satisfaction_branch(
        monkeypatch,
        verdict=wcc.SatisfactionVerdict(
            crossings={"company/b.py -> Feed": ("simulation/w.py::Impl", "simulation/w.py::New")},
            internal=(),
        ),
        baseline=dict(_conformant_E().crossings),
    )
    assert not ok, "a new structural crossing committed without being looked at"
    assert "NEW structural crossing" in detail and "simulation/w.py::New" in detail, detail


def test_FAIL_CLOSED_the_GATE_refuses_when_the_channel_E_reading_RAISES(monkeypatch):
    """R15 FAIL-SILENT: an unavailable check is a FAILED check. Without this branch, deleting the
    SIM trees -- which makes `structural_satisfaction` refuse -- would be a way to commit."""
    def _boom(**kwargs):
        raise wcc.CensusUnavailable("empty satisfier population")

    from tools import pre_commit_test_gate as gate

    _pin_the_other_halves(monkeypatch)
    monkeypatch.setattr(wcc, "structural_satisfaction_at", _boom)
    ok, detail = gate._wall_channel_census_check(["simulation/anything.py"])
    assert not ok and "channel-E satisfaction RAISED" in detail, detail


def test_the_GATE_names_channel_E_in_its_own_source(monkeypatch):
    """The arming, asserted against the file rather than described in a record -- the check pass 24
    had to run a git-grep for because a landing defect and a control defect read identically."""
    source = (Path(wcc.__file__).parent.parent / "tools" / "pre_commit_test_gate.py").read_text()
    assert "structural_satisfaction_at" in source and "drift.ok" in source, (
        "channel E's conformance is not wired into the commit gate"
    )


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


def test_the_nested_surface_of_a_read_key_is_pinned_and_an_unread_key_is_not():
    verdict = wcc.nested_schema(_artefact(), _readers())
    assert verdict.pins["bills"] == ("period_end", "total_amount_gbp")
    assert verdict.unread == ("private_blob",), (
        "a key no business module reads is not a crossing and must not be pinned"
    )


def test_NULL_CONTROL_an_unmutated_artefact_passes_its_own_baseline():
    """Move the sample, not the law: without this every mutation below is satisfied by a control
    that reds on everything."""
    drift = wcc.check_nested_schema(wcc.nested_schema(_artefact(), _readers()), _frozen())
    assert drift.ok, drift.report()


def test_MUTATION_a_NEW_nested_field_under_a_READ_key_is_WIDENING_and_fails():
    """THE DEFECT: the top-level key set does not move, the reader set does not move, the width
    does not move, and a ground-truth field is now published to a business reader."""
    art = _artefact()
    art["bills"][0]["true_hidden_margin_gbp"] = 1.0
    drift = wcc.check_nested_schema(wcc.nested_schema(art, _readers()), _frozen())
    assert not drift.ok, "a widened published blob was allowed through"
    assert drift.widened == {"bills": ("true_hidden_margin_gbp",)}, drift.report()
    assert "WIDENED on channel F" in drift.report() and "true_hidden_margin_gbp" in drift.report()


def test_MUTATION_a_RENAMED_nested_field_fails_because_the_new_name_is_an_addition():
    """This is what keeps narrowing-tolerance from being a hole: rename fires on the ADD half."""
    art = _artefact()
    for row in art["bills"]:
        row["settled_actual_gbp"] = row.pop("total_amount_gbp")
    drift = wcc.check_nested_schema(wcc.nested_schema(art, _readers()), _frozen())
    assert not drift.ok and drift.widened == {"bills": ("settled_actual_gbp",)}, drift.report()


def test_MUTATION_a_key_acquiring_its_FIRST_business_reader_is_a_new_crossing_and_fails():
    art = _artefact()
    readers = _readers() | {"private_blob -> company/portal/app.py"}
    drift = wcc.check_nested_schema(wcc.nested_schema(art, readers), _frozen())
    assert not drift.ok and drift.newly_read == ("private_blob",), drift.report()
    assert "NEW crossing on channel F" in drift.report()


def test_FAIL_OPEN_an_artefact_with_no_top_level_keys_REFUSES():
    """R15 FAIL-OPEN: an empty denominator makes channel F vacuously conformant."""
    with pytest.raises(wcc.CensusUnavailable, match="empty denominator"):
        wcc.nested_schema({}, _readers())


def test_FAIL_OPEN_zero_business_readers_REFUSES_rather_than_reporting_no_crossings():
    """The reassuring answer -- 'no nested field crosses' -- from a measurement that looked at
    nothing. This is exactly what a broken `enumerate_f` would hand this function."""
    with pytest.raises(wcc.CensusUnavailable, match="looked at nothing"):
        wcc.nested_schema(_artefact(), set())


def test_NULL_CONTROL_a_new_field_under_an_UNREAD_key_does_NOT_fail():
    """The subject is the WALL CROSSING, not the artefact at large. Without this pin the control
    reds on published data no business module can see, which is nobody's wall defect."""
    art = _artefact()
    art["private_blob"]["another_field"] = 2
    drift = wcc.check_nested_schema(wcc.nested_schema(art, _readers()), _frozen())
    assert drift.ok, "a change behind no reader was scored as a crossing: " + drift.report()


def test_NULL_CONTROL_population_churn_in_an_id_map_does_NOT_fail():
    """THE NOISE SOURCE THAT WOULD HAVE KILLED THIS CONTROL, and the reason `_is_id_map` exists.

    Measured across 8 committed artefacts: `churn_risk: +SYN-2021-001 -C1_2` is population churn
    and no wall event at all. A control that reds every time a customer joins gets relaxed, and
    takes the real reds with it.
    """
    art = _artefact()
    art["clv_snapshots"].pop("C1")
    art["clv_snapshots"]["SYN-9999-NEW"] = {"clv_gbp": 90.0, "as_of": "2024-01"}
    drift = wcc.check_nested_schema(wcc.nested_schema(art, _readers()), _frozen())
    assert drift.ok, "population churn was read as a schema change: " + drift.report()


def test_a_map_contributes_its_VALUES_schema_and_not_its_own_keys():
    """The discriminator, asserted directly rather than only through the null control."""
    verdict = wcc.nested_schema(_artefact(), _readers())
    assert verdict.pins["clv_snapshots"] == ("as_of", "clv_gbp"), verdict.pins["clv_snapshots"]
    assert "C1" not in verdict.pins["clv_snapshots"], "an identifier key was pinned as schema"


def test_the_schema_walk_is_EXHAUSTIVE_so_the_reading_does_not_depend_on_dict_ORDER():
    """R15 mutation 6 falsified the first cut of this walk, which sampled 5 map values: removing
    one customer shifted the sample window and `years` gained two field names from churn alone."""
    art = _artefact()
    art["clv_snapshots"] = {
        f"C{i}": {"clv_gbp": float(i), "as_of": "2024-01", **({"rare_field": 1} if i == 99 else {})}
        for i in range(100)
    }
    fields = wcc.nested_schema(art, _readers()).pins["clv_snapshots"]
    assert "rare_field" in fields, (
        "a field on the LAST map value was missed, so the reading depends on iteration order"
    )


def test_a_NARROWED_blob_is_a_paydown_and_passes():
    """A control that reds on its own success case gets relaxed."""
    art = _artefact()
    for row in art["bills"]:
        row.pop("total_amount_gbp")
    drift = wcc.check_nested_schema(wcc.nested_schema(art, _readers()), _frozen())
    assert drift.ok and drift.narrowed == {"bills": ("total_amount_gbp",)}, drift.report()


def test_a_key_that_LEAVES_the_artefact_is_paid_down_and_passes():
    art = _artefact()
    frozen = _frozen()
    art.pop("clv_snapshots")
    drift = wcc.check_nested_schema(wcc.nested_schema(art, _readers()), frozen)
    assert drift.ok and drift.paid_down == ("clv_snapshots",), drift.report()


def test_FAIL_CLOSED_a_baseline_with_no_nested_schema_object_raises(tmp_path: Path):
    path = tmp_path / "baseline.json"
    path.write_text(json.dumps({"frozen": {}}), encoding="utf-8")
    with pytest.raises(wcc.CensusUnavailable, match="no `F_nested_schema` object"):
        wcc.load_nested_schema_baseline(path)


def test_THE_LIVE_CHANNEL_F_SURFACE_HAS_NOT_WIDENED():
    """The control against the real tree, which is what makes the fixtures above evidence about
    this repo rather than about a fixture."""
    verdict = wcc.nested_schema_at(rev="HEAD")
    drift = wcc.check_nested_schema(verdict, wcc.load_nested_schema_baseline())
    assert drift.ok, drift.report()


def test_the_nested_surface_check_is_part_of_the_CLIs_exit_code():
    """R11's no-orphan-transitions rule: a check whose red changes nothing is not a gate."""
    import ast

    source = (Path(wcc.__file__).parent.parent / "tools" / "wall_channel_census.py").read_text()
    returns = [
        ast.unparse(n.value) for n in ast.walk(ast.parse(source))
        if isinstance(n, ast.Return) and n.value is not None
    ]
    assert any("nested_drift.ok" in r for r in returns), (
        "the nested surface reports but does not gate -- its red would be a printed line "
        "nothing acts on"
    )


# ── the GATE's channel-F branch ──────────────────────────────────────────────────────────────

def _gate_nested_branch(monkeypatch, *, verdict, baseline):
    from tools import pre_commit_test_gate as gate

    _pin_the_other_halves(monkeypatch)
    monkeypatch.setattr(wcc, "nested_schema_at", lambda **k: verdict)
    monkeypatch.setattr(wcc, "load_nested_schema_baseline", lambda *a, **k: baseline)
    return gate._wall_channel_census_check(["simulation/anything.py"])


def test_NULL_CONTROL_the_GATE_passes_a_conformant_channel_F(monkeypatch):
    ok, detail = _gate_nested_branch(
        monkeypatch, verdict=_conformant_F(), baseline=dict(_conformant_F().pins)
    )
    assert ok, detail
    assert "channel F's 1 read artefact key(s)" in detail, detail


def test_MUTATION_the_GATE_refuses_a_WIDENED_published_blob(monkeypatch):
    """THE DEFECT, at the gate: a ground-truth field added to a published blob, with the
    top-level key set, the reader set and the width all unmoved."""
    ok, detail = _gate_nested_branch(
        monkeypatch,
        verdict=wcc.NestedSchemaVerdict(
            pins={"bills": ("period_end", "total_amount_gbp", "true_hidden_margin_gbp")},
            unread=(),
        ),
        baseline=dict(_conformant_F().pins),
    )
    assert not ok, "a widened published blob was allowed to commit"
    assert "WIDENED on channel F" in detail and "true_hidden_margin_gbp" in detail, (
        "the refusal must carry the diagnostic payload (R5): " + detail
    )


def test_MUTATION_the_GATE_refuses_a_key_with_its_FIRST_business_reader(monkeypatch):
    ok, detail = _gate_nested_branch(
        monkeypatch,
        verdict=wcc.NestedSchemaVerdict(
            pins={"bills": ("period_end", "total_amount_gbp"), "private_blob": ("secret",)},
            unread=(),
        ),
        baseline=dict(_conformant_F().pins),
    )
    assert not ok and "NEW crossing on channel F" in detail and "private_blob" in detail, detail


def test_NULL_CONTROL_the_GATE_tolerates_a_NARROWED_blob(monkeypatch):
    ok, detail = _gate_nested_branch(
        monkeypatch,
        verdict=wcc.NestedSchemaVerdict(pins={"bills": ("period_end",)}, unread=()),
        baseline=dict(_conformant_F().pins),
    )
    assert ok, "a paydown was refused, which is the control reding on its own success case: " + detail


def test_FAIL_CLOSED_the_GATE_refuses_when_the_channel_F_reading_RAISES(monkeypatch):
    """R15 FAIL-SILENT: an unavailable check is a FAILED check."""
    def _boom(**kwargs):
        raise wcc.CensusUnavailable("no artefact key is read business-side")

    from tools import pre_commit_test_gate as gate

    _pin_the_other_halves(monkeypatch)
    monkeypatch.setattr(wcc, "nested_schema_at", _boom)
    ok, detail = gate._wall_channel_census_check(["simulation/anything.py"])
    assert not ok and "channel-F nested surface RAISED" in detail, detail


def test_the_GATE_names_channel_F_in_its_own_source(monkeypatch):
    """The arming, asserted against the file rather than described in a record."""
    source = (Path(wcc.__file__).parent.parent / "tools" / "pre_commit_test_gate.py").read_text()
    assert "nested_schema_at" in source and "nested_drift.ok" in source, (
        "channel F's conformance is not wired into the commit gate"
    )


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


def test_a_seam_whose_BOTH_ROLES_are_live_is_conversant(two_leg_tree):
    """The success case, and the null control every mutation below is measured against.

    It matters that this is REACHABLE on a fixture: the live tree is red, so without a green case
    the control would never have been shown answering in its own success direction, and a control
    that has only ever said no is indistinguishable from one that can only say no.
    """
    verdict = wcc.seam_conversation_conformance(str(two_leg_tree))

    assert TWO_LEG_SEAM in verdict.conversant, verdict.report()
    assert verdict.ok, verdict.report()
    assert "both roles live" in verdict.report()


def test_MUTATION_a_seam_nobody_ever_ASKS_is_UNSOLICITED_INBOUND(two_leg_tree):
    """THE DEFECT THE COLD-EYES WALK FOUND, on the fixture, one statement away from the green case.

    The company stops constructing the request payload -- exactly the edit section 15 makes in
    `test_a_DORMANT_leg_is_neither_wired_nor_unwired`, which asserts the transport question still
    credits this seam as wire-borne. Here the same tree reds, and the assertion below proves the
    two verdicts genuinely disagree on ONE tree rather than on two differently-built ones.
    """
    _write(two_leg_tree, "company/comms/conversation_generator.py", """
        from company.interfaces.wall_protocol import decode_response
        from interface.contracts.conversation_seam import InboundReply

        def observe(wire):
            reply = InboundReply()
            return decode_response(wire), reply
    """)
    verdict = wcc.seam_conversation_conformance(str(two_leg_tree))

    assert verdict.unsolicited == (TWO_LEG_SEAM,), verdict.report()
    assert TWO_LEG_SEAM not in verdict.conversant
    assert not verdict.ok, verdict.report()
    assert "NOTHING IN THIS BUILD EVER ASKS" in verdict.report()
    # THE DISAGREEMENT, ASSERTED. Same root, same moment: the transport question says this seam is
    # fully wire-borne and the conversation question says nobody asks. If this ever stops being
    # true, one of the two controls has silently absorbed the other's question.
    assert TWO_LEG_SEAM in wcc.envelope_wire_conformance(str(two_leg_tree)).wire_borne


def test_MUTATION_deleting_the_REQUEST_DECLARATION_does_not_shed_the_finding(two_leg_tree):
    """THE CHEAPEST WAY TO MAKE THIS PASS, refused -- and it is one line.

    A rule keyed on "a declared leg that is dormant" would go quiet the moment the seam deleted its
    `WallRequest[...]` specialisation: no declared leg, no dormant leg, no finding. That edit makes
    the architecture WORSE (the contract stops even claiming an ask) while scoring as a repair,
    which is the R15 mutation that deletes the subject instead of moving it. Role LIVENESS is the
    unit precisely so this lands in the same bucket as leaving it dormant.
    """
    _write(two_leg_tree, "interface/contracts/conversation_seam.py", """
        from interface.contracts.wall_envelope import WallResponse

        SCHEMA_VERSION = 1

        class InboundReply:
            pass

        ReplyWallResponse = WallResponse[InboundReply]
    """)
    verdict = wcc.seam_conversation_conformance(str(two_leg_tree))

    assert verdict.unsolicited == (TWO_LEG_SEAM,), (
        "deleting the request declaration shed the finding, so the seam that made the defect "
        "worse scored as having repaired it: " + verdict.report()
    )
    assert TWO_LEG_SEAM not in verdict.legless, (
        "a seam specialising ONE envelope has a known role set, not an unknown one -- excusing it "
        "as legless would be the same escape by a different door: " + verdict.report()
    )


def test_MUTATION_a_seam_nobody_ever_ANSWERS_is_UNANSWERED_not_unsolicited(two_leg_tree):
    """The mirror, and it must not collapse into the bucket beside it: asking into silence and
    being spoken to unasked are opposite defects with opposite repairs, and a verdict that called
    both "not conversant" would send the reader to the wrong end of the wall."""
    _write(two_leg_tree, "company/comms/conversation_generator.py", """
        from company.interfaces.wall_protocol import encode_request
        from interface.contracts.conversation_seam import OutboundMessage

        def send(body, emitted_at):
            return encode_request(OutboundMessage(), emitted_at)
    """)
    verdict = wcc.seam_conversation_conformance(str(two_leg_tree))

    assert verdict.unanswered == (TWO_LEG_SEAM,), verdict.report()
    assert verdict.unsolicited == (), verdict.report()
    assert not verdict.ok
    assert "asks into silence" in verdict.report()


def test_MUTATION_a_seam_live_at_NEITHER_end_is_SILENT_where_the_transport_question_drops_it(
    two_leg_tree,
):
    """The bucket `envelope_wire_conformance` explicitly `continue`s past -- "no crossing, so
    nothing to red". Here it is scored, which is the whole reason this question is separate."""
    _write(two_leg_tree, "company/comms/conversation_generator.py", '"""nobody plays either part."""\n')
    verdict = wcc.seam_conversation_conformance(str(two_leg_tree))

    assert verdict.silent == (TWO_LEG_SEAM,), verdict.report()
    assert not verdict.ok
    # The transport question drops it entirely -- present in neither the pass bucket nor a fail one.
    transport = wcc.envelope_wire_conformance(str(two_leg_tree))
    assert TWO_LEG_SEAM not in transport.wire_borne
    assert TWO_LEG_SEAM not in transport.in_process
    assert TWO_LEG_SEAM not in [s for s, _ in transport.half_wired]


def test_NULL_CONTROL_an_unrelated_module_constructing_an_unrelated_type_moves_nothing(
    two_leg_tree,
):
    """The sample moves, the law does not. Without this, every mutation above is consistent with a
    control that reds on any edit at all."""
    before = wcc.seam_conversation_conformance(str(two_leg_tree))
    _write(two_leg_tree, "company/comms/unrelated.py", """
        class SomethingElse:
            pass

        def build():
            return SomethingElse()
    """)

    assert wcc.seam_conversation_conformance(str(two_leg_tree)) == before


def test_NULL_CONTROL_the_UNVERSIONED_envelope_module_is_reported_not_scored(two_leg_tree):
    """`wall_envelope` defines the shape and is not a crossing. Scoring it would red every tree
    that has an envelope at all, which is a control reding on the existence of its own subject."""
    verdict = wcc.seam_conversation_conformance(str(two_leg_tree))

    assert "interface.contracts.wall_envelope" in verdict.versionless, verdict.report()
    assert "interface.contracts.wall_envelope" not in verdict.silent


def test_ZERO_ENVELOPE_SEAMS_IS_NOT_REFUSED_BY_THE_CONVERSATION_QUESTION_EITHER(tmp_path):
    """A fully paid-down envelope channel is a legitimate reading. A control pinned to a non-zero
    count reds on its own success case -- the rule the transport question states and this follows.

    NAMED DISTINCTLY FROM SECTION 13'S EQUIVALENT ON PURPOSE. The two started life sharing a name,
    and a duplicate `def` at module scope does not fail: Python rebinds it and pytest collects only
    the second, so the transport question's zero-seam branch would have stopped being tested with
    nothing anywhere reporting a loss. Caught by ruff F811, which is why that ratchet is worth its
    noise.
    """
    root = tmp_path / "empty"
    (root / "company").mkdir(parents=True)

    verdict = wcc.seam_conversation_conformance(str(root))

    assert verdict.ok and verdict == wcc.ConversationVerdict()


def test_FAIL_CLOSED_seams_that_ALL_lose_their_version_refuse_rather_than_reporting_clean(
    two_leg_tree,
):
    """R15 FAIL-SILENT. Deleting `SCHEMA_VERSION` from every seam would empty all four scored
    buckets and print a tidy "0 of 0" -- the subject removed, reported as a pass."""
    for rel in [
        "interface/contracts/conversation_seam.py",
        "interface/contracts/payment_observable_seam.py",
    ]:
        path = two_leg_tree / rel
        if path.exists():
            path.write_text(
                "\n".join(
                    line for line in path.read_text().splitlines()
                    if "SCHEMA_VERSION" not in line
                ) + "\n",
                encoding="utf-8",
            )

    with pytest.raises(wcc.CensusUnavailable, match="has been removed"):
        wcc.seam_conversation_conformance(str(two_leg_tree))


# ── 22b. the live reading -- RED, and recorded as the L3 blocker it is ────────────────────────


def test_THE_LIVE_WALL_IS_UNSOLICITED_ON_EXACTLY_THE_TWO_SEAMS_THE_WALK_NAMED():
    """THE FINDING, PINNED. This test is GREEN while the wall is WRONG, and that is deliberate.

    The control cannot gate yet -- two of three live seams carry the defect, so refusing on it
    would refuse the commits that repair it (this module's own twice-learned landing-order rule).
    What can be done without wedging the tree is to pin the population, SHRINK-ONLY: a third seam
    acquiring the shape reds here on the day it lands, and a repair passes. That is the same
    discipline as the census baseline beside it, and it is what stops "reported" decaying into
    "narrated".

    WHEN THIS GOES GREEN the assertion below fails, and that is the correct moment to move the
    check into the CLI's return and this test into `assert verdict.ok`.
    """
    verdict = wcc.seam_conversation_conformance_at(worktree=True)
    known_unsolicited = {
        "interface.contracts.flex_observable_seam",
        "interface.contracts.payment_observable_seam",
    }

    assert set(verdict.unsolicited) <= known_unsolicited, (
        "a NEW channel C seam models unsolicited inbound as a reply to a request nothing sends -- "
        "the shape the cold-eyes walk of 2026-08-20 named in advance: " + verdict.report()
    )
    assert not verdict.unanswered, (
        "a live seam now asks into silence, which no live seam did when this was written: "
        + verdict.report()
    )
    assert not verdict.silent, (
        "a live seam is live at neither end: " + verdict.report()
    )
    assert verdict.conversant == ("interface.contracts.conversation_seam",), (
        "the one genuinely two-way conversation on the wall has changed, which is either the "
        "repair this control exists to invite or a regression: " + verdict.report()
    )


def test_the_conversation_check_is_REPORTED_by_the_CLI_and_deliberately_NOT_in_its_exit_code():
    """R11's no-orphan-transitions rule needs its opposite stated too: a check that cannot yet be
    satisfied must not gate, but it MUST reach a reader, or "reports and does not gate" is just a
    name for dead code. Read off the source rather than by running the CLI, which takes minutes."""
    import ast

    source = (Path(wcc.__file__).parent.parent / "tools" / "wall_channel_census.py").read_text()
    tree = ast.parse(source)
    printed = [
        ast.unparse(n)
        for n in ast.walk(tree)
        if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "print"
    ]
    returns = [
        ast.unparse(n.value) for n in ast.walk(tree)
        if isinstance(n, ast.Return) and n.value is not None
    ]

    assert any("conversations.report()" in p for p in printed), (
        "the conversation verdict reaches no reader -- a control nobody sees is not reporting"
    )
    assert not any("conversations.ok" in r for r in returns), (
        "the conversation check has been wired into the exit code while the live wall still "
        "fails it, which refuses every commit including its own repair. Arm it in the same "
        "commit that makes it satisfiable -- and delete this assertion then."
    )


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


def test_a_vocabulary_whose_members_are_all_SAID_and_HEARD_is_live(status_tree):
    """The success case, and the null control every mutation below is measured against."""
    verdict = wcc.status_liveness_conformance(str(status_tree))

    assert verdict.live == ("OK", "TIMEOUT"), verdict.report()
    assert not verdict.unheard and not verdict.unspoken and not verdict.uninhabited
    assert verdict.ok, verdict.report()
    assert "2 of 2" in verdict.report()


def test_MUTATION_a_member_with_a_READER_and_no_WRITER_is_UNSPOKEN(status_tree):
    """THE DEFECT PASSES 33 AND 34'S PROPOSED REPAIR WOULD HAVE BUILT, run rather than argued.

    "Give TIMEOUT a reader" applied to the live tree produces exactly this tree: the branch
    exists, and nothing in the build can take it. R11's orphan transition pointed at the release
    half -- a hold whose release triggers nothing. It must not read as a repair.
    """
    _write(status_tree, "simulation/payment_seam_adapter.py", """
        from interface.contracts.wall_envelope import WallResponse, WallStatus

        def emit(fact):
            return WallResponse(status=WallStatus.OK, payload=fact)
    """)
    verdict = wcc.status_liveness_conformance(str(status_tree))

    assert verdict.unspoken == ("TIMEOUT",), verdict.report()
    assert verdict.live == ("OK",)
    assert not verdict.ok, verdict.report()
    assert "A reader for an event this build cannot produce" in verdict.report()


def test_MUTATION_a_member_with_a_WRITER_and_no_READER_is_UNHEARD_and_does_not_collapse(
    status_tree,
):
    """The mirror, and the assertion that matters is that it does NOT land in `unspoken`.

    These are opposite defects with opposite repairs -- one needs a reader, one needs a writer --
    and a control that sorted both into one bucket would name the wrong half of the work. This is
    `NOT_KNOWABLE_YET`'s live bucket, which no pass has named either.
    """
    _write(status_tree, "company/billing/payment_observation_consumer.py", """
        from interface.contracts.wall_envelope import WallStatus

        def observe(response):
            if response.status == WallStatus.OK:
                return response.payload
            return None
    """)
    verdict = wcc.status_liveness_conformance(str(status_tree))

    assert verdict.unheard == ("TIMEOUT",), verdict.report()
    assert "TIMEOUT" not in verdict.unspoken
    assert not verdict.ok
    assert "collapses it into every other non-OK member" in verdict.report()


def test_MUTATION_a_member_nobody_says_and_nobody_hears_is_UNINHABITED(status_tree):
    """TIMEOUT's and ERROR's actual bucket on the live tree, reproduced on the fixture."""
    _write(status_tree, "simulation/payment_seam_adapter.py", """
        from interface.contracts.wall_envelope import WallResponse, WallStatus

        def emit(fact):
            return WallResponse(status=WallStatus.OK, payload=fact)
    """)
    _write(status_tree, "company/billing/payment_observation_consumer.py", """
        from interface.contracts.wall_envelope import WallStatus

        def observe(response):
            if response.status == WallStatus.OK:
                return response.payload
            return None
    """)
    verdict = wcc.status_liveness_conformance(str(status_tree))

    assert verdict.uninhabited == ("TIMEOUT",), verdict.report()
    assert not verdict.ok
    assert "Writer first, then reader -- a reader alone is a dead arm" in verdict.report()


def test_R15_TAUTOLOGY_the_declaring_module_cannot_inhabit_its_own_vocabulary(status_tree):
    """The contract validating its own invariants is NOT the wall using the member.

    `WallResponse.__post_init__` compares against `ERROR` to enforce that an ERROR carries an
    `ErrorDetail`. Counting that as a reader would derive the checked value from the source it
    checks, and every member would be born live the moment someone wrote a payload invariant for
    it -- the vocabulary certifying itself. The fixture's envelope already compares `OK`; adding
    `ERROR` the same way must move nothing.
    """
    _write(status_tree, STATUS_ENVELOPE, """
        from enum import Enum

        class WallStatus(str, Enum):
            OK = "OK"
            TIMEOUT = "TIMEOUT"
            ERROR = "ERROR"

        class WallResponse:
            def __post_init__(self):
                if self.status == WallStatus.OK and self.payload is None:
                    raise ValueError("OK must carry a payload")
                if self.status == WallStatus.ERROR and self.error is None:
                    raise ValueError("ERROR must carry an ErrorDetail")
                if self.status != WallStatus.ERROR and self.error is not None:
                    raise ValueError("only ERROR carries an error")
    """)
    verdict = wcc.status_liveness_conformance(str(status_tree))

    assert verdict.uninhabited == ("ERROR",), verdict.report()
    assert "ERROR" not in verdict.unspoken, (
        "the declaring module's own payload invariant has been counted as a reader, so the "
        "contract can now certify its own vocabulary live"
    )
    assert verdict.live == ("OK", "TIMEOUT")


def test_a_MATCH_arm_counts_as_HEARING_the_member_and_not_as_saying_it(status_tree):
    """A fail-open with a shelf life, closed before it opened.

    `match` is the idiomatic way to branch on an enum, and it puts the member in a position that
    is not a `Compare`. Read naively, the first consumer rewritten from `if status != OK` to a
    four-arm `match` would flip every member it reads from HEARD to SAID -- and the verdict would
    have gone greener as the code got better. A control that misreads the repair it is asking for
    is not asking for it.
    """
    _write(status_tree, "company/billing/payment_observation_consumer.py", """
        from interface.contracts.wall_envelope import WallStatus

        def observe(response):
            match response.status:
                case WallStatus.TIMEOUT:
                    return "last known value, flagged stale"
                case WallStatus.OK:
                    return response.payload
            return None
    """)
    verdict = wcc.status_liveness_conformance(str(status_tree))

    assert verdict.live == ("OK", "TIMEOUT"), verdict.report()
    spoken = dict(verdict.spoken_in)
    assert "company.billing.payment_observation_consumer" not in spoken.get("TIMEOUT", ()), (
        "a match arm has been counted as SAYING the status -- the consumer is now inhabiting the "
        "member it merely reads, and rewriting an if-chain as a match would score as a repair"
    )


def test_NULL_CONTROL_an_unrelated_enum_with_the_same_member_names_moves_nothing(status_tree):
    """Moves the sample, not the law: same member names, different vocabulary."""
    before = wcc.status_liveness_conformance(str(status_tree))
    _write(status_tree, "company/interfaces/recorded_sim_interface.py", """
        from enum import Enum

        class ReplayStatus(str, Enum):
            OK = "OK"
            TIMEOUT = "TIMEOUT"

        def replay(record):
            if record.status == ReplayStatus.TIMEOUT:
                return None
            return ReplayStatus.OK
    """)
    after = wcc.status_liveness_conformance(str(status_tree))

    assert after == before, after.report()


def test_a_member_declared_TOMORROW_lands_SCORED_without_editing_this_control(status_tree):
    """The population is DERIVED, so a fifth member owns this question on the day it lands.

    A listed population would have let a new member arrive unscored and unnoticed, which is the
    failure the seam questions above are derived to avoid.
    """
    _write(status_tree, STATUS_ENVELOPE, """
        from enum import Enum

        class WallStatus(str, Enum):
            OK = "OK"
            TIMEOUT = "TIMEOUT"
            SUPERSEDED = "SUPERSEDED"
    """)
    verdict = wcc.status_liveness_conformance(str(status_tree))

    assert verdict.uninhabited == ("SUPERSEDED",), verdict.report()
    assert not verdict.ok


def test_MUTATION_deleting_TIMEOUT_is_INVISIBLE_here_and_REFUSED_by_the_floor(status_tree):
    """THE BLIND SPOT, PINNED IN ONE FUNCTION RATHER THAN DESCRIBED IN A DOCSTRING.

    This control derives its population from the declaration it measures, so deleting a member
    does not move the finding -- it removes the subject and leaves. That is the R15 mutation that
    deletes the subject instead of mutating it, and here it would score as a full repair: a wall
    that can no longer say "the answer did not arrive" reports a clean 1 of 1.

    Both halves are asserted together so the pairing cannot rot apart: the liveness question goes
    GREEN on this tree, and `missing_from_status_floor` refuses it. If the first assertion ever
    starts failing, this control has grown the ability to see a deletion and the floor may be
    reconsidered -- until then the floor is the only thing standing between the finding and a
    one-line edit that makes the architecture worse.
    """
    _write(status_tree, STATUS_ENVELOPE, """
        from enum import Enum

        class WallStatus(str, Enum):
            OK = "OK"
    """)
    _write(status_tree, "simulation/payment_seam_adapter.py", """
        from interface.contracts.wall_envelope import WallResponse, WallStatus

        def emit(fact):
            return WallResponse(status=WallStatus.OK, payload=fact)
    """)
    _write(status_tree, "company/billing/payment_observation_consumer.py", """
        from interface.contracts.wall_envelope import WallStatus

        def observe(response):
            if response.status == WallStatus.OK:
                return response.payload
            return None
    """)
    verdict = wcc.status_liveness_conformance(str(status_tree))

    assert verdict.ok, (
        "the liveness question has become able to see a deleted member; if that is real, this "
        "test's premise is gone and the floor's necessity should be re-argued: " + verdict.report()
    )
    assert wcc.missing_from_status_floor(str(status_tree)) == ("TIMEOUT", "ERROR", "NOT_KNOWABLE_YET")


def test_FAIL_CLOSED_an_absent_declaring_module_is_a_FAILED_check(status_tree):
    (status_tree / STATUS_ENVELOPE).unlink()

    with pytest.raises(wcc.CensusUnavailable, match="absent or unparseable"):
        wcc.status_liveness_conformance(str(status_tree))


def test_FAIL_CLOSED_a_missing_enum_is_a_FAILED_check_not_an_empty_vocabulary(status_tree):
    _write(status_tree, STATUS_ENVELOPE, '"""the envelope shape, and no status vocabulary."""\n')

    with pytest.raises(wcc.CensusUnavailable, match="is not declared"):
        wcc.status_liveness_conformance(str(status_tree))


def test_FAIL_CLOSED_an_EMPTY_vocabulary_is_REFUSED_unlike_a_paid_down_seam_channel(status_tree):
    """The one place this file's zero-is-fine rule is deliberately inverted, and why.

    `seam_conversation_conformance` returns an empty verdict on zero seams because a fully
    paid-down envelope channel is a legitimate success case, and a control pinned to a non-zero
    count reds on its own success. A vocabulary emptied of members is not the same event: nothing
    was paid down, the wall simply lost the ability to say anything. `0 of 0` would be the
    cheapest pass available and the worst outcome for the contract.
    """
    _write(status_tree, STATUS_ENVELOPE, """
        from enum import Enum

        class WallStatus(str, Enum):
            pass
    """)
    with pytest.raises(wcc.CensusUnavailable, match="declares no members"):
        wcc.status_liveness_conformance(str(status_tree))


# ── 23b. the live reading -- RED at 2 of 4, and recorded as the L3 blocker it is ───────────────


def test_the_LIVE_status_vocabulary_is_inhabited_TWO_OF_FOUR(  # noqa: E501
):
    """THE FINDING, pinned so it cannot decay into narration, and it is not what pass 34 expected.

    The blocker pass 34 handed forward was one item: `WallStatus.TIMEOUT` has no reader. The
    measurement said the wall is worse off than that in one direction and differently off in
    another:

      * TIMEOUT is UNINHABITED, not merely unread -- nothing says it either, so the reader that
        pass 33 and 34 both proposed would have been a dead arm.
      * ERROR is in the SAME bucket and was named by no pass.
      * NOT_KNOWABLE_YET was UNHEARD -- the world said it and both consumers collapsed it into
        not-OK, so the honest answer the envelope's docstring is proudest of was discarded on
        arrival. REPAIRED in pass 36: `company.billing.payment_observation_consumer` now records
        it as an `UnresolvedCrossing` and distinguishes it from the two members that say
        something about the exchange rather than the fact. The repair was not the reader alone --
        the state it reads had no EXIT, because a non-OK answer burned the correlation_id the
        envelope's own restatement rule sends the resolution on.

    THE RATCHET TIGHTENED WITH THE REPAIR, which is the point of writing it as a ratchet and not
    as a count: `live` is now GROW-ONLY (a member that goes live cannot quietly go back), the red
    buckets stay SHRINK-ONLY, and `unheard` is now asserted EMPTY rather than bounded -- a member
    the world says and nobody distinguishes reds here on the day it lands.

    WHAT KEEPS THIS RED, and it is one piece of work with an ordering inside it: TIMEOUT and ERROR
    are uninhabited, so each needs a WRITER before a reader. WHEN THIS GOES GREEN the assertions
    below fail, and that is the correct moment to move `statuses.ok` into the CLI's return and
    this test into `assert verdict.ok`.

    WHAT THIS DOES NOT SAY, because the control is repo-wide and side-blind by construction:
    NOT_KNOWABLE_YET reads as live off ONE reader on ONE seam. `company/market/flex_participation`
    still collapses it, and that seam is UNSOLICITED INBOUND (`seam_conversation_conformance`),
    so its own repair sits behind the conversation repair, not behind this one.
    """
    verdict = wcc.status_liveness_conformance_at(worktree=True)

    assert set(verdict.live) >= {"OK", "NOT_KNOWABLE_YET"}, (
        "a member that was live is no longer both said and acted on: " + verdict.report()
    )
    assert set(verdict.uninhabited) <= {"TIMEOUT", "ERROR"}, (
        "a NEW status member is declared that nothing says and nothing acts on: " + verdict.report()
    )
    assert not verdict.unheard, (
        "a status member is said by the world and distinguished by nobody: " + verdict.report()
    )
    assert not verdict.unspoken, (
        "a reader now branches on a member this build cannot produce -- the dead arm this "
        "control exists to stop being built: " + verdict.report()
    )


def test_the_LIVE_status_floor_is_intact_and_this_one_GATES():
    """The floor is satisfiable at HEAD, which is why it is wired into the CLI's exit code in the
    same commit that adds it -- this file's own rule for when a check may become a gate."""
    assert wcc.missing_from_status_floor_at(worktree=True) == ()
    assert set(wcc.STATUS_VOCABULARY_FLOOR) == {"OK", "TIMEOUT", "ERROR", "NOT_KNOWABLE_YET"}


def test_the_status_check_REPORTS_and_the_status_FLOOR_gates_and_both_reach_a_reader():
    """The two halves land together and are wired DIFFERENTLY on purpose. Read off the source
    rather than by running the CLI, which takes minutes."""
    import ast

    source = (Path(wcc.__file__).parent.parent / "tools" / "wall_channel_census.py").read_text()
    tree = ast.parse(source)
    printed = [
        ast.unparse(n)
        for n in ast.walk(tree)
        if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "print"
    ]
    returns = [
        ast.unparse(n.value) for n in ast.walk(tree)
        if isinstance(n, ast.Return) and n.value is not None
    ]

    assert any("statuses.report()" in p for p in printed), (
        "the status verdict reaches no reader -- a control nobody sees is not reporting"
    )
    assert not any("statuses.ok" in r for r in returns), (
        "the status liveness check has been wired into the exit code while three of four members "
        "still fail it, which refuses every commit including its own repair. Arm it in the same "
        "commit that makes it satisfiable -- and delete this assertion then."
    )
    assert any("floor_gaps" in ast.unparse(n) for n in ast.walk(tree) if isinstance(n, ast.If)), (
        "the status FLOOR no longer gates -- it is satisfiable at HEAD, so reporting-only would "
        "leave the liveness question's cheapest repair (delete the member) unrefused"
    )
