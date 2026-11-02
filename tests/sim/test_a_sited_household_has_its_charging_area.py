"""A sited household's gas charging area comes from where it is, not from its ONS region.

Lake: data/lake/xoserve_postcode_ldz/ (Xoserve's postcode list joined to the census output areas).
The defects named here: an ONS region read as an LDZ (London is NT and SE, Wales WS and WN); a join
whose output-area vintage drifts from the siting frame's, so almost nobody has an area; and a code that
is neither a charging area nor one of the five independent networks.
"""

from __future__ import annotations

import collections
import csv
import gzip

from sim import ldz_calorific_value as L
from simulation.household_siting import OUTPUT_AREA_FRAME_PATH

INDEPENDENT_NETWORKS = {"LC", "LO", "LS", "LT", "LW"}


def _frame():
    with gzip.open(OUTPUT_AREA_FRAME_PATH, "rt", newline="") as fh:
        return [(r["region"], r["output_area"], float(r["households"])) for r in csv.DictReader(fh)]


def test_an_ons_region_is_not_one_charging_area():
    seen = collections.defaultdict(set)
    for region, oa, _ in _frame():
        seen[region].add(L.ldz_for_output_area(oa))
    assert {"NT", "SE"} <= seen["London"], seen["London"]
    assert {"WS", "WN"} <= seen["Wales"], seen["Wales"]
    assert {"NE", "EM"} <= seen["Yorkshire and The Humber"], seen["Yorkshire and The Humber"]


def test_almost_every_sited_household_has_an_area_and_every_area_is_a_real_one():
    frame = _frame()
    total = sum(h for _, _, h in frame)
    placed = sum(h for _, oa, h in frame if L.ldz_for_output_area(oa))
    # Measured 2026-11-02: 92.6%. The rest are off-grid or newer postcodes; a vintage mismatch is ~0%.
    assert placed / total > 0.9, f"{placed / total:.1%} of sited households have a charging area"
    codes = {L.ldz_for_output_area(oa) for _, oa, _ in frame} - {None}
    assert codes <= set(L.CHARGING_AREAS) | INDEPENDENT_NETWORKS, codes - set(L.CHARGING_AREAS)


def test_an_output_area_the_list_does_not_name_is_none_not_a_guess():
    assert L.ldz_for_output_area(None) is None
    assert L.ldz_for_output_area("E99999999") is None
