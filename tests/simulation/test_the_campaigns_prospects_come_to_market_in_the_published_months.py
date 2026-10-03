"""The campaign's prospects come to market in each year's published months, like the founders.

b35e8cfa4 shaped founders and the trickle by DESNZ QEP Table 2.7.1 and left `iter_prospects` --
the campaign, most of the book -- uniform. The control is 2021's crisis months: suppliers failed
and November-December carried about 5% of that year's transfers, against the 17% a uniform year
gives them, a gap no sampling noise at 400 prospects closes. The uniform draw must still be
consumed, so the prospects themselves (ids, segments, homes) are the same ones as before.
"""
from __future__ import annotations

import datetime as dt

from simulation.net_new_acquisition import PROSPECTS_PER_YEAR, iter_prospects


def _months(year):
    return [dt.date.fromisoformat(str(p.acquisition_date)[:10]).month
            for p in iter_prospects(year, base_seed=11, n=PROSPECTS_PER_YEAR)]


def test_2021s_prospects_thin_out_in_the_crisis_months():
    months = _months(2021)
    assert sum(m >= 11 for m in months) / len(months) < (61 / 365) / 2


def test_only_the_date_moves(monkeypatch):
    """Same draw with the year's shape removed (the uniform path): every attribute but the date
    must be identical, which holds only while the uniform draw is still consumed."""
    import simulation.net_new_acquisition as nna

    def attrs(ps):
        return [(p.customer_id, p.segment, p.commodity, p.consumption_band,
                 getattr(p, "payment_method", None)) for p in ps]

    shaped = list(iter_prospects(2019, base_seed=11, n=PROSPECTS_PER_YEAR))
    table = {k: v for k, v in nna.GB_DOMESTIC_TRANSFERS_BY_MONTH_THOUSANDS.items() if k != 2019}
    monkeypatch.setattr(nna, "GB_DOMESTIC_TRANSFERS_BY_MONTH_THOUSANDS", table)
    uniform = list(iter_prospects(2019, base_seed=11, n=PROSPECTS_PER_YEAR))
    assert attrs(shaped) == attrs(uniform)
    assert [p.acquisition_date for p in shaped] != [p.acquisition_date for p in uniform]
