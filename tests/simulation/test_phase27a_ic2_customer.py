"""Phase 27a: second I&C customer C_IC2 (commercial office, 1 GWh/year)."""

import pytest
from pathlib import Path


def test_c_ic2_in_customers():
    """C_IC2 is defined in saas.customers with correct profile."""
    from saas.customers import get_customer
    c = get_customer("C_IC2")
    assert c is not None
    assert c["customer_id"] == "C_IC2"
    assert c["home_type"] == "office_building"
    assert c["segment"] == "I&C"
    assert c["metering"] == "HH"
    assert c["eac_kwh"] is None
    assert c["acquisition_date"] == "2018-01-01"


def test_c_ic2_hh_data_exists():
    """sim/hh_data/C_IC2.csv exists and has correct structure."""
    p = Path("sim/hh_data/C_IC2.csv")
    assert p.exists(), "C_IC2.csv must exist for HH settlement"
    lines = p.read_text().splitlines()
    header = lines[0].split(",")
    assert header[0] == "date"
    assert len(header) == 49  # date + 48 periods
    assert len(lines) > 3000  # at least ~9 years of data


def test_c_ic2_hh_data_annual_kwh():
    """C_IC2 CSV totals approximately 1 GWh per year (9+ GWh over full window)."""
    import csv as csv_mod
    p = Path("sim/hh_data/C_IC2.csv")
    total_kwh = 0.0
    with open(p) as f:
        reader = csv_mod.DictReader(f)
        for row in reader:
            total_kwh += sum(float(row[f"p{i}"]) for i in range(1, 49))
    # 9.5 years × ~1 GWh = ~9.5 GWh total
    assert 8_000_000 <= total_kwh <= 12_000_000, f"Expected ~9.5 GWh total, got {total_kwh/1e6:.2f} GWh"


def test_c_ic2_eac_derived_in_simulation():
    """EFFECTIVE_EAC_KWH derives C_IC2's EAC from CSV (close to 1 GWh)."""
    from simulation.run_phase2b import EFFECTIVE_EAC_KWH
    eac = EFFECTIVE_EAC_KWH.get("C_IC2")
    assert eac is not None
    assert 900_000 <= eac <= 1_100_000, f"Expected ~1 GWh, got {eac:,.0f} kWh"


def test_c_ic2_in_elec_customers():
    """C_IC2 appears in ELEC_CUSTOMERS list."""
    from simulation.run_phase2b import ELEC_CUSTOMERS
    ids = [c["customer_id"] for c in ELEC_CUSTOMERS]
    assert "C_IC2" in ids


def test_c_ic1_and_c_ic2_both_present():
    """Both I&C customers are in the electricity customer roster."""
    from simulation.run_phase2b import ELEC_CUSTOMERS
    ids = {c["customer_id"] for c in ELEC_CUSTOMERS}
    assert "C_IC1" in ids
    assert "C_IC2" in ids


def test_c_ic2_weekday_higher_than_sunday():
    """Office profile: weekday consumption substantially higher than Sunday."""
    import csv
    p = Path("sim/hh_data/C_IC2.csv")
    rows = {}
    with open(p) as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows[row["date"]] = [float(row[f"p{i}"]) for i in range(1, 49)]
    # 2018-01-02 = Tuesday, 2018-01-07 = Sunday
    tuesday = sum(rows.get("2018-01-02", []))
    sunday = sum(rows.get("2018-01-07", []))
    assert tuesday > 0
    assert sunday > 0
    assert tuesday / sunday > 5.0, f"Weekday/Sunday ratio {tuesday/sunday:.1f}× should be >5×"


def test_c_ic2_summer_peak_higher_than_winter():
    """Office A/C: summer weekday peak periods higher than winter equivalents."""
    import csv
    p = Path("sim/hh_data/C_IC2.csv")
    rows = {}
    with open(p) as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows[row["date"]] = [float(row[f"p{i}"]) for i in range(1, 49)]
    # Compare a summer Tuesday vs winter Tuesday in peak hours (SP 17-36)
    # 2018-07-03 = Tuesday July, 2018-01-02 = Tuesday January
    summer_peak = sum(rows["2018-07-03"][16:36])  # SP 17-36 (0-indexed 16-35)
    winter_peak = sum(rows["2018-01-02"][16:36])
    assert summer_peak > winter_peak, f"Summer peak {summer_peak:.0f} should exceed winter {winter_peak:.0f}"


def test_total_elec_eac_includes_c_ic2():
    """TOTAL_ELEC_EAC increases by approximately 1 GWh with C_IC2 added."""
    from simulation.run_phase2b import TOTAL_ELEC_EAC
    assert TOTAL_ELEC_EAC > 3_000_000, f"Total EAC {TOTAL_ELEC_EAC:,.0f} should exceed 3 GWh with both I&C customers"
