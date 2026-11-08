"""Each control-stack layer on How it's built links to the practice it holds in "Building it", and
back (director's steer of 5 Nov, item 2: "Each control-stack box on How it's built links to its
practice page in 'Building it', and back").

THE JOIN IS DERIVED, NEVER TYPED. A practice and a layer belong together when the code the map's
register says ENFORCES the practice (`enforced_by` in docs/design/the_map/concepts.yaml) is code the
layer says HOLDS it: a `<code>` path in the layer's "Show the code that holds it", or a stem in
`tools.harness_page_figures.LAYER_CODE`, which is what the layer's own evidence counts. So a concept
re-homed in the register, or a layer that stops naming its code, moves the expected links and the
pages must follow. A practice no layer holds says so on its card rather than linking nowhere.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from tools.harness_page_figures import LAYER_CODE

SITE = Path(__file__).resolve().parents[1]
ROOT = SITE.parent
KNOW = (SITE / "knowledge" / "index.html").read_text(encoding="utf-8")
HARNESS = (SITE / "harness" / "index.html").read_text(encoding="utf-8")
REGISTER = yaml.safe_load((ROOT / "docs" / "design" / "the_map" / "concepts.yaml").read_text(encoding="utf-8"))
BUILD = [c for c in REGISTER["concepts"] if any(p.split("/")[0] == "build" for p in c.get("placed", []))]


def _layers(harness: str) -> dict[int, str]:
    stack = harness[harness.index('<ol class="stack">'):harness.index("</ol>", harness.index('<ol class="stack">'))]
    return {int(m.group(1)): m.group(2) for m in re.finditer(r'<li id="layer-(\d+)">(.*?)</li>', stack, re.S)}


def _held(body: str) -> list[str]:
    held = re.search(r'<details class="held">(.*?)</details>', body, re.S)
    return re.findall(r"<code>([^<]+)</code>", held.group(1)) if held else []


def expected(concepts: list[dict], harness: str) -> dict[str, set[int]]:
    out = {}
    for c in concepts:
        out[c["id"]] = set()
        for n, body in _layers(harness).items():
            for path in c.get("enforced_by", []):
                parts = set(Path(path).parts) | {Path(path).stem}
                if parts & set(LAYER_CODE.get(n, ())) or any(
                        path == h or path.startswith(h.rstrip("/") + "/") for h in _held(body)):
                    out[c["id"]].add(n)
    return out


def drift(concepts: list[dict], know: str, harness: str) -> list[str]:
    want, bad = expected(concepts, harness), []
    layers = _layers(harness)
    for cid, ns in want.items():
        wrap = re.search(rf'<div class="practice-wrap" id="practice-{re.escape(cid)}">(.*?)</div><!-- /practice -->',
                         know, re.S)
        if not wrap:
            bad.append(f"no practice-wrap anchor for {cid} on the Knowledge tab")
            continue
        back = {int(n) for n in re.findall(r'href="\.\./harness/#layer-(\d+)"', wrap.group(1))}
        if back != ns:
            bad.append(f"{cid} links back to layers {sorted(back)}, the join says {sorted(ns)}")
        if not ns and "No layer of the control stack holds it" not in wrap.group(1):
            bad.append(f"{cid} is held by no layer and its card does not say so")
        for n, body in layers.items():
            fwd = f'href="../knowledge/#practice-{cid}"' in body
            if fwd != (n in ns):
                bad.append(f"layer {n} {'links' if fwd else 'does not link'} to {cid}; the join says "
                           f"{'it should' if n in ns else 'it should not'}")
    return bad


def test_the_join_can_find_a_layer_and_can_find_none():
    want = expected(BUILD, HARNESS)
    assert any(want.values()), "no practice is held by any layer: the join cannot find anything"
    assert not all(want.values()), "every practice is held: the 'held by no layer' leg is never exercised"


def test_each_layer_and_its_practice_link_both_ways():
    assert not drift(BUILD, KNOW, HARNESS), drift(BUILD, KNOW, HARNESS)


def test_MUTATION_a_forward_link_dropped_from_a_layer_is_caught():
    cid = next(c for c, ns in expected(BUILD, HARNESS).items() if ns)
    assert drift(BUILD, KNOW, HARNESS.replace(f'href="../knowledge/#practice-{cid}"', 'href="#"'))


def test_MUTATION_a_practice_rehomed_in_the_register_moves_the_links():
    moved = [dict(c, enforced_by=["tools/world_claims.py"]) if c["id"] == "build.dead_code" else c for c in BUILD]
    assert any("build.dead_code" in b for b in drift(moved, KNOW, HARNESS))


@pytest.mark.parametrize("n", sorted(LAYER_CODE))
def test_every_layer_carries_the_anchor_a_back_link_lands_on(n):
    assert n in _layers(HARNESS), f"layer {n} has no id, so a link back to it lands at the top of the page"
