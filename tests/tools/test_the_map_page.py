"""The map's page shows what the map generated, and each link on it opens a concept that is there.

The defect this names: a page in the mock-up's shape that reads complete while a measure a knowledge
page states is silently dropped, a link opens nothing, or an empty layer with no reason recorded
renders as if it were filled. Each test says which way it would go red.
"""
from __future__ import annotations

import re

from tools import the_map_page


def _concept(cid, **over):
    c = {"id": cid, "prefLabel": cid.title(), "definition": "d", "match": ["Bacs"],
         "placed": ["supplier/Collect"], "page": {"id": "debt", "published": True, "notes": ["n1"]},
         "world": [{"module": "simulation.rails", "status": "wired"}],
         "supplier": [{"module": "company.billing.desk", "status": "orphan"}],
         "gap": {"wall": "not observable"}, "missing": ["wall"], "links": [], "also_named": []}
    c.update(over)
    return c


def _map(concepts):
    return {"spines": {"supplier": {"prefLabel": "The supplier", "steps": ["Collect", "Bill"]},
                       "build": {"prefLabel": "How it's built", "steps": ["Testing and controls"]}},
            "concepts": concepts, "findings": [], "notes": {"notes": 2, "on_a_page": 1, "on_no_page": ["n2"]}}


def test_a_claim_on_a_mapped_page_is_a_measure_and_one_on_no_mapped_page_is_a_finding(monkeypatch):
    """MUTATION: drop the `if not pages` branch and the unplaced claim vanishes, so this fires;
    attach every claim to every page and the n2 claim lands on `debt`, so this fires too."""
    from tools import world_claims
    monkeypatch.setattr(world_claims, "claims", lambda root=None: [
        {"id": "dd_share", "measure": "direct_debit_share_of_accounts", "band": [0.6, 0.7],
         "source": "s", "page": "docs/market_research/n1.md"},
        {"id": "fuel_split", "measure": "nobody_wrote_this", "band": [0.1, 0.2],
         "source": "s", "page": "docs/market_research/n2.md"}])
    on_page, unplaced = the_map_page.claim_measures(_map([_concept("collect.a")]))
    assert [k["id"] for k in on_page["debt"]] == ["dd_share"]
    assert on_page["debt"][0]["computed_by"] == "tools.world_claims._direct_debit_share_of_accounts"
    assert [(k["id"], k["computed_by"]) for k in unplaced] == [("fuel_split", None)]
    html = the_map_page.render(_map([_concept("collect.a")]), on_page, unplaced)
    assert "measure on no mapped page: 1" in html
    assert "_direct_debit_share_of_accounts" in html


def test_every_link_on_the_page_opens_a_panel_that_exists():
    """MUTATION: render the panel id as anything but `c-<id>` and the hrefs point nowhere, so this
    fires. It also asserts a link IS rendered, so a page that drops every link cannot pass."""
    a = _concept("collect.a", links=[{"rel": "causes", "to": "build.b"}])
    b = _concept("build.b", placed=["build/Testing and controls"], rule="R15", rule_mechanisms=[],
                 enforced_by=[{"path": "x.py", "exists": False}], evidence=None,
                 links=[{"rel": "causes (from)", "to": "collect.a"}])
    html = the_map_page.render(_map([a, b]), {}, [])
    targets = set(re.findall(r'href="#(c-[^"]+)"', html))
    assert targets == {"c-collect.a", "c-build.b"}
    assert targets <= set(re.findall(r'id="(c-[^"]+)"', html))
    assert 'causes <a href="#c-build.b">' in html and "How it&#x27;s built</p>" in html


def test_an_empty_layer_says_its_reason_or_says_it_has_none():
    """MUTATION: render an empty layer as a blank cell and neither string appears, so this fires."""
    reasoned = _concept("collect.a")
    bare = _concept("collect.b", gap={}, missing=["wall"])
    html = the_map_page.render(_map([reasoned, bare]), {}, [])
    assert "Gap: not observable" in html
    assert "Gap, and no reason recorded" in html
    assert "nothing calls it" in html
