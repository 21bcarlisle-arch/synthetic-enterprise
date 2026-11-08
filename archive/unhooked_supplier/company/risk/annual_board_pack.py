"""Annual Board Pack synthesiser — aggregates company-level risk signals.

A UK energy supplier's board reviews quarterly risk signals from multiple
operational and financial modules. This synthesiser collates the signals
and produces a structured board pack.

Epistemic constraint: all inputs come from company-observable data —
management accounts, trading records, compliance logs. No SIM internals.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class BoardSignalRAG(str, Enum):
    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"


class BoardSignalCategory(str, Enum):
    FINANCIAL = "Financial"
    RISK = "Risk"
    COMPLIANCE = "Compliance"
    PORTFOLIO = "Portfolio"
    STRATEGIC = "Strategic"


@dataclass
class BoardSignal:
    category: BoardSignalCategory
    name: str
    value: str
    rag: BoardSignalRAG
    commentary: str = ""

    @property
    def is_red(self) -> bool:
        return self.rag == BoardSignalRAG.RED

    @property
    def is_green(self) -> bool:
        return self.rag == BoardSignalRAG.GREEN


class AnnualBoardPack:
    """Collects board signals and produces a structured pack summary."""

    def __init__(self, year: int) -> None:
        self.year = year
        self._signals: list[BoardSignal] = []

    def add_signal(
        self,
        category: BoardSignalCategory,
        name: str,
        value: str,
        rag: BoardSignalRAG,
        commentary: str = "",
    ) -> BoardSignal:
        signal = BoardSignal(category, name, value, rag, commentary)
        self._signals.append(signal)
        return signal

    def add_financial(self, name, value, rag, commentary="") -> BoardSignal:
        return self.add_signal(BoardSignalCategory.FINANCIAL, name, value, rag, commentary)

    def add_risk(self, name, value, rag, commentary="") -> BoardSignal:
        return self.add_signal(BoardSignalCategory.RISK, name, value, rag, commentary)

    def add_compliance(self, name, value, rag, commentary="") -> BoardSignal:
        return self.add_signal(BoardSignalCategory.COMPLIANCE, name, value, rag, commentary)

    def add_portfolio(self, name, value, rag, commentary="") -> BoardSignal:
        return self.add_signal(BoardSignalCategory.PORTFOLIO, name, value, rag, commentary)

    def add_strategic(self, name, value, rag, commentary="") -> BoardSignal:
        return self.add_signal(BoardSignalCategory.STRATEGIC, name, value, rag, commentary)

    @property
    def all_signals(self) -> list[BoardSignal]:
        return list(self._signals)

    @property
    def red_signals(self) -> list[BoardSignal]:
        return [s for s in self._signals if s.is_red]

    @property
    def green_signals(self) -> list[BoardSignal]:
        return [s for s in self._signals if s.is_green]

    @property
    def overall_rag(self) -> BoardSignalRAG:
        if any(s.is_red for s in self._signals):
            return BoardSignalRAG.RED
        if any(s.rag == BoardSignalRAG.AMBER for s in self._signals):
            return BoardSignalRAG.AMBER
        return BoardSignalRAG.GREEN

    def signals_by_category(self, category: BoardSignalCategory) -> list[BoardSignal]:
        return [s for s in self._signals if s.category == category]

    def highest_risk_signals(self, n: int = 3) -> list[BoardSignal]:
        order = {BoardSignalRAG.RED: 2, BoardSignalRAG.AMBER: 1, BoardSignalRAG.GREEN: 0}
        return sorted(self._signals, key=lambda s: order[s.rag], reverse=True)[:n]

    def pack_summary(self) -> str:
        n = len(self._signals)
        n_red = len(self.red_signals)
        n_green = len(self.green_signals)
        lines = [
            "Annual Board Pack — {}".format(self.year),
            "Overall RAG: {} | Signals: {} | RED: {} | GREEN: {}".format(
                self.overall_rag.value, n, n_red, n_green
            ),
        ]
        for cat in BoardSignalCategory:
            cat_signals = self.signals_by_category(cat)
            if cat_signals:
                lines.append("{}:".format(cat.value))
                for s in cat_signals:
                    lines.append("  {} [{}]: {} — {}".format(
                        s.name, s.rag.value, s.value, s.commentary or "—"
                    ))
        return chr(10).join(lines)
