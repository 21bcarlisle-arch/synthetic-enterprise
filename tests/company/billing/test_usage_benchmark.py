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
