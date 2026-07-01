"""Phase CI: Annual Board Pack Synthesiser tests."""
import pytest
from company.risk.annual_board_pack import (
    AnnualBoardPack, BoardSignal, BoardSignalRAG, BoardSignalCategory
)


def _green_pack() -> AnnualBoardPack:
    pack = AnnualBoardPack(2024)
    pack.add_financial("Net Margin", "£1.2M", BoardSignalRAG.GREEN, "Above breakeven")
    pack.add_risk("Resilience Scorecard", "3.0/3.0", BoardSignalRAG.GREEN, "All pillars GREEN")
    pack.add_compliance("SLC Tracker", "COMPLIANT", BoardSignalRAG.GREEN, "No breaches")
    return pack


def _mixed_pack() -> AnnualBoardPack:
    pack = AnnualBoardPack(2022)
    pack.add_financial("Net Margin", "£0.2M", BoardSignalRAG.AMBER, "Near breakeven")
    pack.add_risk("Resilience Scorecard", "1.6/3.0", BoardSignalRAG.RED, "Hedge and concentration RED")
    pack.add_compliance("SLC Tracker", "BREACH_RISK", BoardSignalRAG.AMBER, "SLC31A near limit")
    pack.add_portfolio("Hedge Coverage", "35%", BoardSignalRAG.RED, "Below 40% policy minimum")
    return pack


# 1. Pack initialises with correct year
def test_pack_year():
    pack = AnnualBoardPack(2023)
    assert pack.year == 2023


# 2. add_signal returns BoardSignal with correct fields
def test_add_signal_fields():
    pack = AnnualBoardPack(2023)
    sig = pack.add_financial("P&L", "£500k", BoardSignalRAG.GREEN, "Above target")
    assert sig.name == "P&L"
    assert sig.rag == BoardSignalRAG.GREEN
    assert sig.category == BoardSignalCategory.FINANCIAL


# 3. all_signals length correct
def test_all_signals_count():
    pack = _green_pack()
    assert len(pack.all_signals) == 3


# 4. red_signals empty when all GREEN
def test_red_signals_empty_all_green():
    pack = _green_pack()
    assert len(pack.red_signals) == 0


# 5. green_signals captures all-green pack
def test_green_signals_all_green():
    pack = _green_pack()
    assert len(pack.green_signals) == 3


# 6. overall_rag GREEN when all green
def test_overall_rag_all_green():
    pack = _green_pack()
    assert pack.overall_rag == BoardSignalRAG.GREEN


# 7. overall_rag RED when any RED
def test_overall_rag_any_red():
    pack = _mixed_pack()
    assert pack.overall_rag == BoardSignalRAG.RED


# 8. overall_rag AMBER when mix of AMBER and GREEN
def test_overall_rag_amber():
    pack = AnnualBoardPack(2020)
    pack.add_financial("P&L", "£600k", BoardSignalRAG.GREEN)
    pack.add_risk("VaR", "1.8x", BoardSignalRAG.AMBER)
    assert pack.overall_rag == BoardSignalRAG.AMBER


# 9. red_signals correctly filtered
def test_red_signals_filtered():
    pack = _mixed_pack()
    assert len(pack.red_signals) == 2  # Resilience + Hedge Coverage


# 10. signals_by_category filters correctly
def test_signals_by_category():
    pack = _mixed_pack()
    risk_signals = pack.signals_by_category(BoardSignalCategory.RISK)
    assert len(risk_signals) == 1
    assert risk_signals[0].name == "Resilience Scorecard"


# 11. highest_risk_signals returns RED first
def test_highest_risk_signals():
    pack = _mixed_pack()
    top = pack.highest_risk_signals(n=2)
    assert all(s.is_red for s in top)


# 12. pack_summary contains key sections
def test_pack_summary():
    pack = _mixed_pack()
    summary = pack.pack_summary()
    assert "2022" in summary
    assert "RED" in summary
    assert "Financial" in summary
    assert "Risk" in summary


# --- Phase MD depth tests ---

def test_signal_category_stored():
    signal = BoardSignal(BoardSignalCategory.FINANCIAL, 'Net Margin', '£1M', BoardSignalRAG.GREEN)
    assert signal.category == BoardSignalCategory.FINANCIAL


def test_signal_name_stored():
    signal = BoardSignal(BoardSignalCategory.RISK, 'Score', '2.5', BoardSignalRAG.AMBER)
    assert signal.name == 'Score'


def test_signal_value_stored():
    signal = BoardSignal(BoardSignalCategory.COMPLIANCE, 'SLC', 'GREEN', BoardSignalRAG.GREEN)
    assert signal.value == 'GREEN'


def test_signal_rag_stored():
    signal = BoardSignal(BoardSignalCategory.STRATEGIC, 'Growth', '+5%', BoardSignalRAG.AMBER)
    assert signal.rag == BoardSignalRAG.AMBER


def test_signal_commentary_default_empty():
    signal = BoardSignal(BoardSignalCategory.FINANCIAL, 'Rev', '£1M', BoardSignalRAG.GREEN)
    assert signal.commentary == ''


def test_is_red_true():
    signal = BoardSignal(BoardSignalCategory.RISK, 'Score', '1.0', BoardSignalRAG.RED)
    assert signal.is_red is True


def test_is_green_false_for_amber():
    signal = BoardSignal(BoardSignalCategory.RISK, 'Score', '1.5', BoardSignalRAG.AMBER)
    assert signal.is_green is False


def test_add_signal_returns_board_signal():
    pack = AnnualBoardPack(2023)
    result = pack.add_signal(BoardSignalCategory.FINANCIAL, 'Rev', '£1M', BoardSignalRAG.GREEN)
    assert isinstance(result, BoardSignal)


def test_board_signal_category_has_5_members():
    assert len(list(BoardSignalCategory)) == 5


def test_board_signal_rag_has_3_members():
    assert len(list(BoardSignalRAG)) == 3
