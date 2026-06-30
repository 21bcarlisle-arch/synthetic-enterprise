"""Phase BN: Segment Margin Attribution section tests."""
import pytest
from saas.reporting.annual_report import _section_segment_margin_attribution


def _data(yr, seg_data: dict) -> dict:
    return {"years": {str(yr): {"segment_split": seg_data}}}


def _multi(years_dict: dict) -> dict:
    return {"years": {str(yr): {"segment_split": ss} for yr, ss in years_dict.items()}}


def _ss(resi_e=0.0, resi_g=0.0, sme_e=0.0, ic_e=0.0, ic_g=0.0):
    return {
        "resi electricity": {"gross_gbp": resi_e},
        "resi gas": {"gross_gbp": resi_g},
        "SME electricity": {"gross_gbp": sme_e},
        "I&C electricity": {"gross_gbp": ic_e},
        "I&C gas": {"gross_gbp": ic_g},
    }


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_segment_margin_attribution({}) == ""
    assert _section_segment_margin_attribution({"years": {}}) == ""
    assert _section_segment_margin_attribution({"years": {"2022": {}}}) == ""


# 2. Header present
def test_header_present():
    d = _data(2022, _ss(resi_e=1000, ic_e=50000))
    assert "Segment Gross Margin Attribution" in _section_segment_margin_attribution(d)


# 3. I&C electricity dominance visible
def test_ic_dominance():
    d = _data(2022, _ss(resi_e=3739, ic_e=964199))
    result = _section_segment_margin_attribution(d)
    assert "£964,199" in result


# 4. Negative segment shown with minus
def test_negative_segment():
    d = _data(2022, _ss(resi_g=-742, ic_e=964199))
    result = _section_segment_margin_attribution(d)
    assert "-£742" in result or "£-742" in result


# 5. Total column computed
def test_total_column():
    d = _data(2022, _ss(resi_e=1000, sme_e=2000, ic_e=10000))
    result = _section_segment_margin_attribution(d)
    assert "£13,000" in result  # 1000 + 2000 + 10000 = 13000


# 6. Best GM year identified
def test_best_gm_year():
    d = _multi({
        2021: _ss(ic_e=500000),
        2022: _ss(ic_e=1000000),
        2023: _ss(ic_e=800000),
    })
    result = _section_segment_margin_attribution(d)
    assert "Best gross margin year: 2022" in result


# 7. Worst GM year identified
def test_worst_gm_year():
    d = _multi({
        2021: _ss(ic_e=500000),
        2022: _ss(ic_e=1000000),
        2023: _ss(ic_e=800000),
    })
    result = _section_segment_margin_attribution(d)
    assert "Worst: 2021" in result


# 8. Loss-making segment flagged
def test_loss_making_flagged():
    d = _data(2022, _ss(resi_g=-742, ic_e=964199))
    result = _section_segment_margin_attribution(d)
    assert "Loss-making" in result
    assert "resi gas" in result


# 9. Year rows sorted chronologically
def test_years_sorted():
    d = _multi({
        2023: _ss(ic_e=800000),
        2021: _ss(ic_e=500000),
        2022: _ss(ic_e=1000000),
    })
    result = _section_segment_margin_attribution(d)
    pos_2021 = result.find("| 2021 |")
    pos_2022 = result.find("| 2022 |")
    pos_2023 = result.find("| 2023 |")
    assert pos_2021 < pos_2022 < pos_2023


# 10. All 5 segment columns present
def test_five_columns():
    d = _data(2022, _ss(resi_e=1, resi_g=2, sme_e=3, ic_e=4, ic_g=5))
    result = _section_segment_margin_attribution(d)
    assert "resi electricity" in result
    assert "I&C electricity" in result
    assert "I&C gas" in result


# 11. Missing segment handled gracefully
def test_missing_segment():
    # Only electricity segments, no gas
    d = _data(2022, {"resi electricity": {"gross_gbp": 5000}, "I&C electricity": {"gross_gbp": 100000}})
    result = _section_segment_margin_attribution(d)
    assert "Segment Gross Margin" in result


# 12. No loss-making note when all positive
def test_no_loss_note_when_all_positive():
    d = _data(2022, _ss(resi_e=1000, resi_g=500, sme_e=2000, ic_e=50000, ic_g=5000))
    result = _section_segment_margin_attribution(d)
    assert "Loss-making" not in result
