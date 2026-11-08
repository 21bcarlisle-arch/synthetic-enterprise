# Increment 3: the legs of tests/company/test_phase_ic_coverage_expansion.py that test archived modules. Its live legs stay there.
"""Phase IC: coverage expansion for supplier_fitness_register, annual_board_pack, environmental_impact."""
import datetime as dt

import pytest

# ===== supplier_fitness_register =====
from company.regulatory.supplier_fitness_register import (
    FitnessConcernCategory,
    FitnessOutcome,
    FitnessRole,
    SupplierFitnessRegister,
)


def _sfr():
    reg = SupplierFitnessRegister()
    reg.assess("P001","Alice Smith",FitnessRole.EXECUTIVE_DIRECTOR,dt.date(2023,1,1),
               FitnessOutcome.FIT)
    reg.assess("P002","Bob Jones",FitnessRole.NON_EXECUTIVE_DIRECTOR,dt.date(2022,6,1),
               FitnessOutcome.FIT_WITH_CONDITIONS,conditions=("Must recuse on energy investments",))
    reg.assess("P003","Carol Brown",FitnessRole.SENIOR_MANAGER,dt.date(2022,1,1),
               FitnessOutcome.NOT_FIT,concerns=(FitnessConcernCategory.PRIOR_SUPPLIER_FAILURE,))
    return reg

class TestSupplierFitnessRegister:
    def test_get_assessment(self):
        reg = _sfr()
        a = reg.get("P001")
        assert a is not None and a.name == "Alice Smith"

    def test_is_fit_for_fit_outcome(self):
        reg = _sfr()
        assert reg.get("P001").is_fit

    def test_is_fit_with_conditions(self):
        reg = _sfr()
        assert reg.get("P002").is_fit

    def test_not_fit_persons(self):
        reg = _sfr()
        nf = reg.not_fit_persons()
        assert len(nf) == 1 and nf[0].person_id == "P003"

    def test_all_fit_is_false_when_not_fit(self):
        reg = _sfr()
        assert not reg.all_fit

    def test_all_fit_when_everyone_fit(self):
        reg = SupplierFitnessRegister()
        reg.assess("X","Name",FitnessRole.EXECUTIVE_DIRECTOR,dt.date(2023,1,1),FitnessOutcome.FIT)
        assert reg.all_fit

    def test_overdue_review(self):
        reg = _sfr()
        # P003 assessed 2022-01-01; overdue after 2023-01-01
        overdue = reg.overdue_reviews(dt.date(2024,1,1))
        ids = [a.person_id for a in overdue]
        assert "P003" in ids

    def test_not_overdue_within_365_days(self):
        reg = _sfr()
        overdue = reg.overdue_reviews(dt.date(2023,1,1))
        assert "P001" not in [a.person_id for a in overdue]

    def test_prior_supplier_failure_risk(self):
        reg = _sfr()
        risk = reg.prior_supplier_failure_risk()
        assert len(risk) == 1 and risk[0].person_id == "P003"

    def test_fitness_summary_contains_key_fields(self):
        reg = _sfr()
        s = reg.fitness_summary(dt.date(2024,1,1))
        assert "Senior persons" in s and "Not fit" in s


# ===== annual_board_pack =====
from company.risk.annual_board_pack import AnnualBoardPack, BoardSignalCategory, BoardSignalRAG


def _pack():
    pack = AnnualBoardPack(2022)
    pack.add_financial("Net Margin","£1.2M",BoardSignalRAG.GREEN,"Above budget")
    pack.add_risk("VaR Utilisation","85%",BoardSignalRAG.AMBER,"Approaching limit")
    pack.add_compliance("SLC Breaches","3 open",BoardSignalRAG.RED,"2x SLC14")
    pack.add_portfolio("Churn Rate","6.2%",BoardSignalRAG.AMBER,"Rising trend")
    pack.add_strategic("Market Share","1.1%",BoardSignalRAG.GREEN,"On target")
    return pack

class TestAnnualBoardPack:
    def test_signal_count(self):
        pack = _pack()
        assert len(pack.all_signals) == 5

    def test_red_signals_filter(self):
        pack = _pack()
        assert len(pack.red_signals) == 1
        assert pack.red_signals[0].category == BoardSignalCategory.COMPLIANCE

    def test_green_signals_filter(self):
        pack = _pack()
        assert len(pack.green_signals) == 2

    def test_overall_rag_red_when_any_red(self):
        pack = _pack()
        assert pack.overall_rag == BoardSignalRAG.RED

    def test_overall_rag_amber_when_no_red(self):
        pack = AnnualBoardPack(2022)
        pack.add_financial("Net Margin","OK",BoardSignalRAG.GREEN)
        pack.add_risk("VaR","85%",BoardSignalRAG.AMBER)
        assert pack.overall_rag == BoardSignalRAG.AMBER

    def test_overall_rag_green_when_all_green(self):
        pack = AnnualBoardPack(2022)
        pack.add_financial("Profit","£1M",BoardSignalRAG.GREEN)
        assert pack.overall_rag == BoardSignalRAG.GREEN

    def test_signals_by_category(self):
        pack = _pack()
        financial = pack.signals_by_category(BoardSignalCategory.FINANCIAL)
        assert len(financial) == 1

    def test_highest_risk_signals_order(self):
        pack = _pack()
        top = pack.highest_risk_signals(3)
        assert top[0].rag == BoardSignalRAG.RED

    def test_is_red_property(self):
        pack = _pack()
        reds = [s for s in pack.all_signals if s.is_red]
        assert len(reds) == 1

    def test_pack_summary_contains_year(self):
        pack = _pack()
        s = pack.pack_summary()
        assert "2022" in s and "RED" in s
