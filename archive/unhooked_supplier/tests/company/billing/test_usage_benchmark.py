"""Phase 107: Usage benchmarking tests."""

from company.billing.usage_benchmark import usage_benchmark, _peer_group, compute_percentile


_CUSTOMERS = [
    {"customer_id": "C1", "home_type": "suburban_semi", "epc_rating": "D", "eac_kwh": 3500},
    {"customer_id": "C2", "home_type": "suburban_semi", "epc_rating": "E", "eac_kwh": 4000},
    {"customer_id": "C3", "home_type": "suburban_semi", "epc_rating": "D", "eac_kwh": 2800},
    {"customer_id": "C4", "home_type": "urban_flat", "epc_rating": "D", "eac_kwh": 1500},
]


def test_peer_group_same_home_type_and_band():
    peers = _peer_group(_CUSTOMERS[0], _CUSTOMERS)
    ids = [p["customer_id"] for p in peers]
    assert "C1" not in ids  # exclude self
    assert "C3" in ids  # same home_type and D (mid band)
    assert "C2" in ids  # D and E both "mid" band
    assert "C4" not in ids  # different home_type


def test_compute_percentile_low():
    pct = compute_percentile(2000, [3000, 4000, 5000])
    assert pct == 0.0


def test_compute_percentile_high():
    pct = compute_percentile(6000, [3000, 4000, 5000])
    assert pct == 100.0


def test_compute_percentile_empty():
    assert compute_percentile(3000, []) == 50.0


def test_usage_benchmark_returns_rating():
    result = usage_benchmark(_CUSTOMERS[0], _CUSTOMERS)
    assert result["rating"] in ("efficient", "average", "heavy", None)


def test_usage_benchmark_no_peers():
    customer = {"customer_id": "C99", "home_type": "unique_type", "epc_rating": "A", "eac_kwh": 2000}
    result = usage_benchmark(customer, _CUSTOMERS)
    assert result["peer_count"] == 0
    assert result["rating"] is None


def test_usage_benchmark_peer_count():
    result = usage_benchmark(_CUSTOMERS[0], _CUSTOMERS)
    assert result["peer_count"] >= 2


def test_usage_benchmark_peer_median():
    result = usage_benchmark(_CUSTOMERS[0], _CUSTOMERS)
    assert result["peer_median"] is not None
    assert isinstance(result["peer_median"], (int, float))


def test_consumption_template_has_benchmark():
    with open("company/portal/templates/consumption.html") as f:
        html = f.read()
    assert "benchmark" in html
    assert "peer" in html


def test_consumption_route_includes_benchmark():
    from starlette.testclient import TestClient
    from company.portal.app import app
    client = TestClient(app, raise_server_exceptions=True)
    r = client.get("/account/C1/consumption")
    assert r.status_code == 200


_HIGH_BAND_CUSTOMERS = [
    {"customer_id": "C1", "home_type": "flat", "epc_rating": "A", "eac_kwh": 2000},
    {"customer_id": "C2", "home_type": "flat", "epc_rating": "B", "eac_kwh": 2200},
    {"customer_id": "C3", "home_type": "flat", "epc_rating": "C", "eac_kwh": 2400},
    {"customer_id": "C4", "home_type": "flat", "epc_rating": "D", "eac_kwh": 3000},
]

_LOW_BAND_CUSTOMERS = [
    {"customer_id": "C1", "home_type": "house", "epc_rating": "F", "eac_kwh": 5000},
    {"customer_id": "C2", "home_type": "house", "epc_rating": "G", "eac_kwh": 6000},
    {"customer_id": "C3", "home_type": "house", "epc_rating": "E", "eac_kwh": 4000},
]

_RATING_CUSTOMERS = [
    {"customer_id": "C_TEST", "home_type": "flat", "epc_rating": "D", "eac_kwh": 0},
    {"customer_id": "C1", "home_type": "flat", "epc_rating": "D", "eac_kwh": 4000},
    {"customer_id": "C2", "home_type": "flat", "epc_rating": "D", "eac_kwh": 5000},
    {"customer_id": "C3", "home_type": "flat", "epc_rating": "E", "eac_kwh": 6000},
]


def test_epc_high_band_grouping():
    # A, B, C all map to "high" band and should be peers of each other
    peers = _peer_group(_HIGH_BAND_CUSTOMERS[0], _HIGH_BAND_CUSTOMERS)
    ids = [p["customer_id"] for p in peers]
    assert "C2" in ids  # B -> high
    assert "C3" in ids  # C -> high
    assert "C4" not in ids  # D -> mid


def test_epc_low_band_grouping():
    # F and G both map to "low" band; E maps to "mid"
    peers = _peer_group(_LOW_BAND_CUSTOMERS[0], _LOW_BAND_CUSTOMERS)
    ids = [p["customer_id"] for p in peers]
    assert "C2" in ids  # G -> low
    assert "C3" not in ids  # E -> mid


def test_efficient_rating():
    customers = list(_RATING_CUSTOMERS)
    customers[0] = dict(customers[0], eac_kwh=1000)
    result = usage_benchmark(customers[0], customers)
    # pct=0 (lowest) -> efficient
    assert result["rating"] == "efficient"


def test_heavy_rating():
    customers = [
        {"customer_id": "C0", "home_type": "flat", "epc_rating": "D", "eac_kwh": 9000},
        {"customer_id": "C1", "home_type": "flat", "epc_rating": "D", "eac_kwh": 2000},
        {"customer_id": "C2", "home_type": "flat", "epc_rating": "D", "eac_kwh": 3000},
        {"customer_id": "C3", "home_type": "flat", "epc_rating": "E", "eac_kwh": 2500},
    ]
    result = usage_benchmark(customers[0], customers)
    # pct=100 (highest) -> heavy
    assert result["rating"] == "heavy"


def test_average_rating():
    # Customer at middle percentile (33 < pct <= 66)
    customers = [
        {"customer_id": "C0", "home_type": "flat", "epc_rating": "D", "eac_kwh": 3500},
        {"customer_id": "C1", "home_type": "flat", "epc_rating": "D", "eac_kwh": 2000},
        {"customer_id": "C2", "home_type": "flat", "epc_rating": "D", "eac_kwh": 5000},
        {"customer_id": "C3", "home_type": "flat", "epc_rating": "E", "eac_kwh": 4000},
    ]
    # peers for C0: C1(D,mid) and C2(D,mid) and C3(E,mid) all mid band
    # pct = below/total: 2000 < 3500 -> 1 below, total 3 -> 33.3% -> average
    result = usage_benchmark(customers[0], customers)
    assert result["rating"] == "average"


def test_efficient_label_content():
    customers = [
        {"customer_id": "C0", "home_type": "flat", "epc_rating": "D", "eac_kwh": 1000},
        {"customer_id": "C1", "home_type": "flat", "epc_rating": "D", "eac_kwh": 4000},
        {"customer_id": "C2", "home_type": "flat", "epc_rating": "D", "eac_kwh": 5000},
        {"customer_id": "C3", "home_type": "flat", "epc_rating": "E", "eac_kwh": 6000},
    ]
    result = usage_benchmark(customers[0], customers)
    assert "lower than" in result["label"]


def test_heavy_label_content():
    customers = [
        {"customer_id": "C0", "home_type": "flat", "epc_rating": "D", "eac_kwh": 9000},
        {"customer_id": "C1", "home_type": "flat", "epc_rating": "D", "eac_kwh": 2000},
        {"customer_id": "C2", "home_type": "flat", "epc_rating": "D", "eac_kwh": 3000},
        {"customer_id": "C3", "home_type": "flat", "epc_rating": "E", "eac_kwh": 2500},
    ]
    result = usage_benchmark(customers[0], customers)
    assert "efficiency" in result["label"]


def test_customer_eac_in_result():
    result = usage_benchmark(_CUSTOMERS[0], _CUSTOMERS)
    assert result["customer_eac"] == float(_CUSTOMERS[0]["eac_kwh"])


def test_percentile_in_result():
    result = usage_benchmark(_CUSTOMERS[0], _CUSTOMERS)
    assert result["percentile"] is not None
    assert 0.0 <= result["percentile"] <= 100.0


def test_no_peers_label():
    customer = {"customer_id": "C99", "home_type": "unique", "epc_rating": "A", "eac_kwh": 2000}
    result = usage_benchmark(customer, _CUSTOMERS)
    assert result["label"] == "No similar properties to compare."
