"""Phase CV: DA/DC Contract Register tests."""
import pytest
from datetime import date
from company.market.dadc_contract_register import (
    DADCContractRegister, MeteringAgentType, MeterType
)

_D = date(2020, 1, 1)
_MPAN = "1012345678901"


def _reg_with_dc():
    r = DADCContractRegister()
    a = r.appoint(_MPAN, MeteringAgentType.DC, "Stark Energy", _D)
    return r, a


# 1. appoint creates active appointment
def test_appoint():
    r, a = _reg_with_dc()
    assert a.is_active
    assert a.agent_type == MeteringAgentType.DC


# 2. active_appointments includes new appointment
def test_active():
    r, a = _reg_with_dc()
    assert a in r.active_appointments


# 3. terminate deactivates appointment
def test_terminate():
    r, a = _reg_with_dc()
    r.terminate(_MPAN, MeteringAgentType.DC, date(2021, 1, 1))
    assert r.agent_for_mpan(_MPAN, MeteringAgentType.DC) is None


# 4. agent_for_mpan returns active agent
def test_agent_for_mpan():
    r, a = _reg_with_dc()
    result = r.agent_for_mpan(_MPAN, MeteringAgentType.DC)
    assert result is not None
    assert result.agent_name == "Stark Energy"


# 5. agent_for_mpan returns None when no matching agent
def test_agent_for_mpan_missing():
    r = DADCContractRegister()
    assert r.agent_for_mpan(_MPAN, MeteringAgentType.DA) is None


# 6. mpans_without_dc detects missing DC
def test_mpans_without_dc():
    r = DADCContractRegister()
    r.appoint(_MPAN, MeteringAgentType.DA, "AgentCo", _D)  # DA only, no DC
    assert _MPAN in r.mpans_without_dc()


# 7. mpans_without_dc empty when DA_DC covers it
def test_da_dc_covers():
    r = DADCContractRegister()
    r.appoint(_MPAN, MeteringAgentType.DA_DC, "CombinedAgent", _D)
    assert _MPAN not in r.mpans_without_dc()


# 8. mpans_without_da detects missing DA
def test_mpans_without_da():
    r, a = _reg_with_dc()  # DC only
    assert _MPAN in r.mpans_without_da()


# 9. agents_by_name count
def test_agents_by_name():
    r = DADCContractRegister()
    r.appoint("M1", MeteringAgentType.DC, "AgentA", _D)
    r.appoint("M2", MeteringAgentType.DA, "AgentA", _D)
    r.appoint("M3", MeteringAgentType.DC, "AgentB", _D)
    names = r.agents_by_name()
    assert names["AgentA"] == 2
    assert names["AgentB"] == 1


# 10. multiple MPANs independently tracked
def test_multiple_mpans():
    r = DADCContractRegister()
    r.appoint("M1", MeteringAgentType.DA_DC, "Agent1", _D)
    r.appoint("M2", MeteringAgentType.DA_DC, "Agent1", _D)
    assert len({a.mpan for a in r.active_appointments}) == 2


# 11. terminate only affects matching MPAN and type
def test_terminate_specific():
    r = DADCContractRegister()
    r.appoint("M1", MeteringAgentType.DC, "Agent1", _D)
    r.appoint("M2", MeteringAgentType.DC, "Agent1", _D)
    r.terminate("M1", MeteringAgentType.DC, date(2021, 1, 1))
    assert r.agent_for_mpan("M2", MeteringAgentType.DC) is not None


# 12. da_dc_summary contains BSC
def test_summary():
    r, a = _reg_with_dc()
    summary = r.da_dc_summary()
    assert "BSC" in summary
    assert "DA/DC" in summary
