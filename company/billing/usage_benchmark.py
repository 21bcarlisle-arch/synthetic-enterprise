"""Usage benchmarking -- compare customer EAC against similar-home peers."""

from __future__ import annotations


_EPC_BAND_GROUP = {
    "A": "high", "B": "high", "C": "high",
    "D": "mid", "E": "mid",
    "F": "low", "G": "low",
}


def _peer_group(customer, all_customers):
    ht = customer.get("home_type")
    epc = str(customer.get("epc_rating", "")).upper()
    band_grp = _EPC_BAND_GROUP.get(epc)
    peers = []
    for c in all_customers:
        if c.get("customer_id") == customer.get("customer_id"):
            continue
        if c.get("home_type") != ht:
            continue
        c_epc = str(c.get("epc_rating", "")).upper()
        if _EPC_BAND_GROUP.get(c_epc) != band_grp:
            continue
        peers.append(c)
    return peers


def compute_percentile(value, peers):
    if not peers:
        return 50.0
    below = sum(1 for p in peers if p < value)
    return round(below / len(peers) * 100, 1)


def usage_benchmark(customer, all_customers):
    customer_eac = float(customer.get("eac_kwh", 0))
    peers = _peer_group(customer, all_customers)
    peer_eacs = [float(p.get("eac_kwh", 0)) for p in peers]

    if not peer_eacs:
        return {
            "peer_count": 0, "customer_eac": customer_eac,
            "peer_median": None, "percentile": None,
            "rating": None, "label": "No similar properties to compare.",
        }

    peer_eacs_sorted = sorted(peer_eacs)
    n = len(peer_eacs_sorted)
    peer_median = peer_eacs_sorted[n // 2]
    pct = compute_percentile(customer_eac, peer_eacs)

    if pct <= 33:
        rating = "efficient"
        label = "Your usage is lower than " + str(int(100 - pct)) + "% of similar homes."
    elif pct <= 66:
        rating = "average"
        label = "Your usage is typical for similar homes (" + str(n) + " peers)."
    else:
        rating = "heavy"
        label = "Your usage is higher than " + str(int(pct)) + "% of similar homes. Consider efficiency improvements."

    return {
        "peer_count": n, "customer_eac": customer_eac,
        "peer_median": peer_median, "percentile": pct,
        "rating": rating, "label": label,
    }
