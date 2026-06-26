"""Phase 268 tests: /sim/ section -- wholesale price explorer."""
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
SITE = PROJECT / "site"
DATA = SITE / "data"


def test_sim_index_exists():
    assert (SITE / "sim" / "index.html").exists()


def test_sim_index_has_nav():
    text = (SITE / "sim" / "index.html").read_text()
    assert "site-nav" in text or "nav-link" in text


def test_sim_index_active_not_dim():
    text = (SITE / "sim" / "index.html").read_text()
    assert "active" in text
    assert "dim" not in text


def test_main_index_sim_link_not_dim():
    text = (SITE / "index.html").read_text()
    assert "site-nav-link dim" not in text


def test_sim_data_json_exists():
    assert (DATA / "sim_data.json").exists()


def test_sim_data_has_monthly():
    d = json.loads((DATA / "sim_data.json").read_text())
    assert len(d["monthly"]) >= 100


def test_sim_data_has_crisis_years():
    d = json.loads((DATA / "sim_data.json").read_text())
    months = d["monthly"]
    crisis = [m for m in months if m["is_crisis"]]
    years = {m["month"][:4] for m in crisis}
    assert "2021" in years
    assert "2022" in years


def test_sim_data_peak_over_500():
    d = json.loads((DATA / "sim_data.json").read_text())
    peaks = d["peak_records"]
    assert len(peaks) > 0
    assert peaks[0]["ssp"] > 500


def test_sim_data_annual_2022_highest_mean():
    d = json.loads((DATA / "sim_data.json").read_text())
    annual = d["annual"]
    y22 = next((a for a in annual if a["year"] == "2022"), None)
    assert y22 is not None
    other_means = [a["mean"] for a in annual if a["year"] != "2022"]
    assert y22["mean"] > max(other_means)


def test_generate_sim_data_module():
    import sys
    sys.path.insert(0, str(PROJECT))
    from tools.generate_sim_data import generate
    assert callable(generate)
