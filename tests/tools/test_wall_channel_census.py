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
