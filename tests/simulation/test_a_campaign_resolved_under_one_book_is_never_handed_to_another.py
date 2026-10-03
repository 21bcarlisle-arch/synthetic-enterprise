"""A campaign resolved under one book setting is never handed back under another.

`_CAMPAIGN_MEMO` was keyed on the seed alone, but the pre-growth book also turns on settings read at
call time. The population draw alone moves the campaign from 228 winners (off) to 52 (on). With
`test_live_population_seam` and a whole run selected together, the run reused the other setting's
campaign and held a winner it drew no dwelling for: 19 tests errored on origin (2026-10-03).
"""
from __future__ import annotations

from simulation import live_population as lp


def _winners(seed):
    return [p.customer_id for p, _w in lp._campaign(lp._pre_growth_book(seed), seed)["winners"]]


def test_each_draw_setting_gets_its_own_campaign_whichever_resolved_first(monkeypatch, tmp_path):
    monkeypatch.setenv("SE_GROW_BOOK", "1")
    monkeypatch.setattr(lp, "_SUBSET_VERDICT_RECORD", tmp_path / "verdict.json")
    seed = lp._DEFAULT_BASE_SEED
    saved = dict(lp._CAMPAIGN_MEMO)
    try:
        lp._CAMPAIGN_MEMO.clear()
        monkeypatch.setenv("SE_DRAW_POPULATION", "1")
        drawn = _winners(seed)
        lp._CAMPAIGN_MEMO.clear()
        monkeypatch.setenv("SE_DRAW_POPULATION", "0")
        undrawn = _winners(seed)
        assert undrawn != drawn, "vacuous: the draw flag changed nothing, so keys cannot be told apart"
        # the undrawn campaign is now memoised; the drawn setting must still get its own
        monkeypatch.setenv("SE_DRAW_POPULATION", "1")
        assert _winners(seed) == drawn
    finally:
        lp._CAMPAIGN_MEMO.clear()
        lp._CAMPAIGN_MEMO.update(saved)
