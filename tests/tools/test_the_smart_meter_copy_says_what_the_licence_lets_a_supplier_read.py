"""The second cold read's N6 (2026-10-28): the Explore copy said, of a smart home with no
half-hourly reads, that "read frequency is the customer's consent to give". It is not, under the
licence's smart data access rules as docs/market_research/smart_meter_hh_data_consent_2026.md and
smart_meters_and_half_hourly_settlement_2026-10-25.md summarise them. A supplier needs no consent for
the monthly read. It may take daily reads unless the customer opts out. Only half-hourly reads are
the customer's to opt in to. The commons does not yet hold the licence text (the GAP is on
INV_SMART_METER_BILLED_ON_ITS_OWN_READS). Both places the sentence is written are graded."""
import re
from pathlib import Path

from tools.generate_explore_hh_day import _coverage_statement

PAGE = Path(__file__).resolve().parents[2] / "site" / "explore" / "index.html"


def _smart_panel_copy() -> str:
    text = PAGE.read_text()
    start = text.index("HH_META.smartUnread && HH_META.smartUnread[group]")
    # The page writes the sentence as concatenated string literals; read it as one string.
    return re.sub(r'"\s*\+\s*"', "", text[start:text.index("could be fixed by asking", start)])


def test_the_coverage_sentence_names_each_read_frequency_at_its_own_rule():
    s = _coverage_statement(with_reads=3, smart_without=119, households=707)
    assert "consent to give" not in s, s
    assert "monthly reads need no consent" in s and "opts out" in s and "opt in" in s, s


def test_the_smart_household_panel_says_the_same_and_the_clause_still_drops_at_zero():
    body = _smart_panel_copy()
    assert "consent to give" not in body, body
    assert "monthly reads need no consent" in body, body
    assert "SMART" not in _coverage_statement(with_reads=3, smart_without=0, households=707)
