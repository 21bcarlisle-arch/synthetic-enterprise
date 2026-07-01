"""Tests for ADR Register (Phase EE)."""
import datetime as dt
import pytest
from company.core.adr_register import (
    ADRStatus, ADRCategory, ArchitecturalDecisionRecord, ADRRegister,
)


DATE = dt.date(2024, 1, 15)


def make_adr(reg, title="Test ADR", cat=ADRCategory.EPISTEMIC_AIR_GAP,
             status=ADRStatus.ACCEPTED):
    return reg.record(
        title=title,
        category=cat,
        decided_at=DATE,
        context="Test context: failure mode",
        decision="We decided to do X",
        consequences="Trade-off: Y",
        status=status,
    )


@pytest.fixture
def reg():
    return ADRRegister()


class TestArchitecturalDecisionRecord:
    def test_is_active_accepted(self):
        adr = ArchitecturalDecisionRecord(
            adr_id="ADR-001",
            title="Test",
            category=ADRCategory.EPISTEMIC_AIR_GAP,
            status=ADRStatus.ACCEPTED,
            decided_at=DATE,
            context="ctx",
            decision="dec",
            consequences="cons",
        )
        assert adr.is_active

    def test_not_active_proposed(self):
        adr = ArchitecturalDecisionRecord(
            adr_id="ADR-001",
            title="Test",
            category=ADRCategory.EPISTEMIC_AIR_GAP,
            status=ADRStatus.PROPOSED,
            decided_at=DATE,
            context="ctx",
            decision="dec",
            consequences="cons",
        )
        assert not adr.is_active

    def test_not_active_deprecated(self):
        adr = ArchitecturalDecisionRecord(
            adr_id="ADR-001",
            title="Test",
            category=ADRCategory.EPISTEMIC_AIR_GAP,
            status=ADRStatus.DEPRECATED,
            decided_at=DATE,
            context="ctx",
            decision="dec",
            consequences="cons",
        )
        assert not adr.is_active


class TestADRRegister:
    def test_auto_id(self, reg):
        a1 = make_adr(reg, "First")
        a2 = make_adr(reg, "Second")
        assert a1.adr_id == "ADR-001"
        assert a2.adr_id == "ADR-002"

    def test_explicit_id(self, reg):
        adr = reg.record(
            title="Explicit",
            category=ADRCategory.EVENT_DRIVEN,
            decided_at=DATE,
            context="ctx",
            decision="dec",
            consequences="cons",
            adr_id="ADR-999",
        )
        assert adr.adr_id == "ADR-999"

    def test_get(self, reg):
        make_adr(reg)
        assert reg.get("ADR-001") is not None

    def test_get_missing(self, reg):
        assert reg.get("ADR-999") is None

    def test_all_adrs(self, reg):
        make_adr(reg, "A")
        make_adr(reg, "B")
        assert len(reg.all_adrs()) == 2

    def test_active_adrs(self, reg):
        make_adr(reg, "Active", status=ADRStatus.ACCEPTED)
        make_adr(reg, "Proposed", status=ADRStatus.PROPOSED)
        active = reg.active_adrs()
        assert len(active) == 1
        assert active[0].title == "Active"

    def test_by_category(self, reg):
        make_adr(reg, cat=ADRCategory.EPISTEMIC_AIR_GAP)
        make_adr(reg, cat=ADRCategory.EVENT_DRIVEN)
        epistemic = reg.by_category(ADRCategory.EPISTEMIC_AIR_GAP)
        assert len(epistemic) == 1

    def test_deprecate(self, reg):
        make_adr(reg)
        make_adr(reg)
        reg.deprecate("ADR-001", superseded_by="ADR-002")
        adr = reg.get("ADR-001")
        assert adr is not None
        assert adr.status == ADRStatus.DEPRECATED
        assert adr.superseded_by == "ADR-002"

    def test_adr_summary(self, reg):
        make_adr(reg)
        s = reg.adr_summary()
        assert "ADR Register" in s
        assert "ADR required" in s


# --- Phase LQ depth tests ---

def _direct_adr(**kwargs):
    defaults = dict(
        adr_id="ADR-001", title="Test", category=ADRCategory.EPISTEMIC_AIR_GAP,
        status=ADRStatus.ACCEPTED, decided_at=DATE,
        context="ctx", decision="dec", consequences="cons"
    )
    defaults.update(kwargs)
    return ArchitecturalDecisionRecord(**defaults)


def test_adr_id_stored():
    a = _direct_adr(adr_id="ADR-042")
    assert a.adr_id == "ADR-042"


def test_title_stored():
    a = _direct_adr(title="My Decision")
    assert a.title == "My Decision"


def test_category_stored():
    a = _direct_adr(category=ADRCategory.EVENT_DRIVEN)
    assert a.category == ADRCategory.EVENT_DRIVEN


def test_status_stored():
    a = _direct_adr(status=ADRStatus.PROPOSED)
    assert a.status == ADRStatus.PROPOSED


def test_decided_at_stored():
    d = dt.date(2025, 3, 10)
    a = _direct_adr(decided_at=d)
    assert a.decided_at == d


def test_context_stored():
    a = _direct_adr(context="failure mode X")
    assert a.context == "failure mode X"


def test_decision_stored():
    a = _direct_adr(decision="Use event sourcing")
    assert a.decision == "Use event sourcing"


def test_consequences_stored():
    a = _direct_adr(consequences="Higher complexity")
    assert a.consequences == "Higher complexity"


def test_superseded_by_default_none():
    a = _direct_adr()
    assert a.superseded_by is None


def test_is_superseded_deprecated_without_ref():
    a = _direct_adr(status=ADRStatus.DEPRECATED)
    assert a.is_superseded is False
