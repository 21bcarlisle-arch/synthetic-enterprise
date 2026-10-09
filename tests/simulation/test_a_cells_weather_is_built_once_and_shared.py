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


class _CountingWorld(_World):
    def __init__(self):
        self.reads: list[str] = []

    def for_cell(self, cell):
        self.reads.append(cell)
        return super().for_cell(cell) if cell != "B" else [{"date": "2020-01-01"}]


def test_a_cells_rows_are_read_once_per_field_not_once_per_premise():
    """Defect: the memo saves the series but `for_cell` -- 3,653 row dicts -- is still built for
    every premise before the memo is asked, so the run pays per account for weather it already
    holds. BOTH SIDES: a second FIELD of the same cell is a real miss and must read again, and an
    empty series must still name its day count (which needs the rows)."""
    world = _CountingWorld()
    for i, lat in enumerate((51.0, 51.5, 52.0, 53.0)):
        wi.weather_means_for_customer(_premise(f"P{i}", lat), world)
    assert world.reads == ["A"]
    wi.cloud_cover_for_customer(_premise("P9", 51.0), world)
    assert world.reads == ["A", "A"]
    first = wi.cell_weather_for_customer(_premise("Q1", 57.0), world=world)
    again = wi.cell_weather_for_customer(_premise("Q2", 57.0), world=world)
    assert first.refusal == again.refusal and "on any of its 1 days" in again.refusal
