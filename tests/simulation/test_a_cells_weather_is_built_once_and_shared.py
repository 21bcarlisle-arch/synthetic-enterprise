"""Control for `simulation.weather_inputs._cell_series`: one weather series per cell and field.

Measured on a 160-founder book to 2017 (2026-10-08): with the memo off and on, the settled records,
events, treasury path, eligibility verdicts and demand providers digest identically, and the peak
falls 1,705 -> 1,683 MB. Those runs are minutes long, so they are evidence for the commit.
"""
from simulation import weather_inputs as wi


class _World:
    """Two premises in cell A, one in cell B: the smallest store that can tell sharing from copying."""

    def cell_id_for(self, lat, lon):
        return "A" if lat < 55 else "B"

    def for_cell(self, cell):
        return [{"date": "2020-01-01", "temperature_mean_c": 3.0 if cell == "A" else 1.0}]


def _premise(cid, lat):
    return {"customer_id": cid, "location": {"lat": lat, "lon": -1.0}}


def test_premises_in_one_cell_share_ONE_series_and_another_cell_or_world_does_not():
    """Defect: every premise gets its own copy of its cell's sky, so weather memory grows with
    accounts instead of cells. BOTH SIDES: a memo keyed too coarsely (shared across cells or across
    worlds) would hand a premise somebody else's weather, which is worse than the copy.
    """
    world, other_world = _World(), _World()
    a1 = wi.weather_means_for_customer(_premise("P1", 51.5), world)
    a2 = wi.weather_means_for_customer(_premise("P2", 52.0), world)
    b = wi.weather_means_for_customer(_premise("P3", 57.0), world)
    assert a1 is a2, "two premises in one cell built two series"
    assert a1 == {"2020-01-01": 3.0} and b == {"2020-01-01": 1.0}
    assert wi.weather_means_for_customer(_premise("P4", 51.5), other_world) is not a1
