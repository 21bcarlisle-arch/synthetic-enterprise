"""Every served Knowledge page carries its five facets, and no sim-drawn insight feeds the world.

The director, 4 Nov: knowledge and insight are different layers, every claim carries a trust
assessment, and an insight from our own simulation must never become a world parameter or a
calibration target. The facets and their values are THE_KNOWLEDGE_BASE_STRUCTURE.md §7; the
records are site/data/knowledge_facets.json, keyed by page directory.

The page set is scanned from the served directories, never listed, so a new page with no record
reds here."""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FACETS = ROOT / "site/data/knowledge_facets.json"

DOMAINS = {"market_and_regulation", "household_and_assets", "customer_needs_and_behaviour",
           "supplier_operations", "products_measures_services", "other_markets"}
LAYERS = {"knowledge", "insight", "mixed"}
SIDES = {"world", "supplier", "both", "neither"}
GRADES = {"D", "P", "S", "A"}
VERIFIED = {"yes", "partly", "no"}
STATUSES = {"hypothesis", "tested", "held", "contested", "refuted"}
USE_KINDS = {"world", "calibration", "supplier", "page"}
CIRCULAR = {"world", "calibration"}


def served_pages() -> set[str]:
    return {d.name for d in (ROOT / "site/knowledge").iterdir()
            if d.is_dir() and not d.name.startswith("_") and (d / "index.html").exists()}


def problems(record: dict) -> list[str]:
    """Every way one page's record fails §7. Empty means it passes."""
    out = []
    for field, allowed in (("domain", DOMAINS), ("layer", LAYERS), ("side", SIDES)):
        if record.get(field) not in allowed:
            out.append(f"{field}={record.get(field)!r}")
    trust = record.get("trust") or {}
    if trust.get("grade_floor") not in GRADES:
        out.append(f"trust.grade_floor={trust.get('grade_floor')!r}")
    if trust.get("verified") not in VERIFIED:
        out.append(f"trust.verified={trust.get('verified')!r}")
    if not str(trust.get("vintage") or "")[:4].isdigit():
        out.append("trust.vintage missing")
    insights = record.get("insights")
    if not isinstance(insights, list):
        out.append("insights is not a list")
        insights = []
    if record.get("layer") in {"insight", "mixed"} and not insights:
        out.append(f"a {record.get('layer')} page names no insight")
    for use in record.get("use", []) + [u for i in insights for u in i.get("use", [])]:
        if str(use).split(":", 1)[0] not in USE_KINDS or ":" not in str(use):
            out.append(f"use {use!r}")
    for i in insights:
        claim = str(i.get("claim", ""))[:50]
        if i.get("status") not in STATUSES:
            out.append(f"insight {claim!r} status={i.get('status')!r}")
        if not isinstance(i.get("from_sim"), bool):
            out.append(f"insight {claim!r} does not say whether it is from the simulation")
        for field in ("falsified_by", "checked", "review_by"):
            if not i.get(field):
                out.append(f"insight {claim!r} has no {field}")
        if i.get("from_sim"):
            for use in i.get("use", []):
                if str(use).split(":", 1)[0] in CIRCULAR:
                    out.append(f"CIRCULAR: sim-drawn insight {claim!r} feeds {use}")
    return out


def test_the_check_can_refuse_each_kind_of_defect():
    """MUTANT: a problems() that returns [] passes every page below. Each leg is a defect."""
    good = {"domain": "supplier_operations", "layer": "mixed", "side": "both", "use": [],
            "trust": {"grade_floor": "P", "verified": "partly", "vintage": "2025-04"},
            "insights": [{"claim": "c", "status": "hypothesis", "from_sim": True, "use": [],
                          "falsified_by": "x", "checked": "2026-11-04", "review_by": "2027-02-02"}]}
    assert problems(good) == []
    bad = json.loads(json.dumps(good))
    bad["insights"][0]["use"] = ["world:simulation/population.py"]
    assert any(p.startswith("CIRCULAR") for p in problems(bad))
    bad["insights"][0]["from_sim"] = False
    assert not any(p.startswith("CIRCULAR") for p in problems(bad))
    assert problems({**good, "layer": "opinion"}) and problems({**good, "insights": []})
    assert problems({**good, "trust": {"grade_floor": "B", "verified": "no", "vintage": "2025"}})
    del bad["insights"][0]["review_by"]
    assert problems(bad)


def _records() -> dict:
    return json.loads(FACETS.read_text())["pages"]


def test_every_served_page_has_a_record_and_no_record_is_orphaned():
    records = _records()
    assert not served_pages() - set(records), sorted(served_pages() - set(records))
    assert not set(records) - served_pages(), sorted(set(records) - served_pages())


@pytest.mark.parametrize("slug", sorted(served_pages()))
def test_each_page_carries_valid_facets_and_no_circular_use(slug):
    record = _records().get(slug)
    if record is None:
        pytest.fail(f"{slug} has no facet record")
    assert problems(record) == [], f"{slug}: {problems(record)}"
