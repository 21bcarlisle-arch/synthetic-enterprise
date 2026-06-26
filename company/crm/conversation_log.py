from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ConversationOutcome(str, Enum):
    RESOLVED = 'resolved'
    ESCALATED = 'escalated'
    PENDING_CALLBACK = 'pending_callback'
    ABANDONED = 'abandoned'
    TRANSFERRED = 'transferred'


@dataclass(frozen=True)
class ConversationTurn:
    speaker: str
    text: str
    timestamp: dt.datetime


@dataclass
class CustomerConversation:
    conversation_id: str
    customer_id: str
    contact_reason: str
    channel: str
    started_at: dt.datetime
    agent_id: Optional[str] = None
    ended_at: Optional[dt.datetime] = None
    outcome: Optional[ConversationOutcome] = None
    csat_score: Optional[int] = None
    nps_score: Optional[int] = None
    turns: List[ConversationTurn] = field(default_factory=list)

    def add_turn(self, speaker: str, text: str, timestamp: dt.datetime) -> ConversationTurn:
        turn = ConversationTurn(speaker=speaker, text=text, timestamp=timestamp)
        self.turns.append(turn)
        return turn

    def close(self, ended_at: dt.datetime, outcome: ConversationOutcome,
              csat_score: Optional[int] = None, nps_score: Optional[int] = None) -> None:
        self.ended_at = ended_at
        self.outcome = outcome
        if csat_score is not None:
            if not (1 <= csat_score <= 5):
                raise ValueError(f'CSAT must be 1-5, got {csat_score}')
            self.csat_score = csat_score
        if nps_score is not None:
            if not (0 <= nps_score <= 10):
                raise ValueError(f'NPS must be 0-10, got {nps_score}')
            self.nps_score = nps_score

    @property
    def duration_seconds(self) -> Optional[float]:
        if self.ended_at is None:
            return None
        return (self.ended_at - self.started_at).total_seconds()

    @property
    def is_open(self) -> bool:
        return self.ended_at is None


class ConversationLog:
    def __init__(self) -> None:
        self._conversations: Dict[str, CustomerConversation] = {}
        self._next_id = 1

    def start(self, customer_id: str, contact_reason: str, channel: str,
              started_at: dt.datetime, agent_id: Optional[str] = None
              ) -> CustomerConversation:
        conv_id = f'CONV-{self._next_id:05d}'
        self._next_id += 1
        conv = CustomerConversation(
            conversation_id=conv_id,
            customer_id=customer_id,
            contact_reason=contact_reason,
            channel=channel,
            started_at=started_at,
            agent_id=agent_id,
        )
        self._conversations[conv_id] = conv
        return conv

    def get(self, conversation_id: str) -> Optional[CustomerConversation]:
        return self._conversations.get(conversation_id)

    def conversations_for_customer(self, customer_id: str) -> List[CustomerConversation]:
        return [c for c in self._conversations.values() if c.customer_id == customer_id]

    def open_conversations(self) -> List[CustomerConversation]:
        return [c for c in self._conversations.values() if c.is_open]

    def avg_csat(self) -> Optional[float]:
        scores = [c.csat_score for c in self._conversations.values() if c.csat_score is not None]
        return round(sum(scores) / len(scores), 2) if scores else None

    def avg_nps(self) -> Optional[float]:
        scores = [c.nps_score for c in self._conversations.values() if c.nps_score is not None]
        return round(sum(scores) / len(scores), 2) if scores else None

    def resolution_rate(self) -> Optional[float]:
        closed = [c for c in self._conversations.values() if not c.is_open]
        if not closed:
            return None
        resolved = [c for c in closed if c.outcome == ConversationOutcome.RESOLVED]
        return round(len(resolved) / len(closed), 4)

    def annual_summary(self) -> dict:
        all_c = list(self._conversations.values())
        closed = [c for c in all_c if not c.is_open]
        by_outcome: dict = {}
        for c in closed:
            key = c.outcome.value if c.outcome else 'unknown'
            by_outcome[key] = by_outcome.get(key, 0) + 1
        return {
            'total_conversations': len(all_c),
            'open': len(self.open_conversations()),
            'closed': len(closed),
            'avg_csat': self.avg_csat(),
            'avg_nps': self.avg_nps(),
            'resolution_rate': self.resolution_rate(),
            'by_outcome': by_outcome,
        }
