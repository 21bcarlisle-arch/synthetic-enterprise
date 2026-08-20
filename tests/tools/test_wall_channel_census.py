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
    """Run `_wall_channel_census_check` with the census half forced GREEN and the wire half
    forced to `wire`, so the returned verdict is attributable to the wire half alone."""
    from tools import pre_commit_test_gate as gate

    monkeypatch.setattr(gate, "_index_tree", lambda: "0" * 40)
    monkeypatch.setattr(wcc, "census_at", lambda tree, root: {})
    monkeypatch.setattr(wcc, "load_baseline", lambda *a, **k: {})
    monkeypatch.setattr(wcc, "check", lambda *a, **k: _AlwaysOk())
    monkeypatch.setattr(wcc, "wire_conformance_at", lambda **k: wire)
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
