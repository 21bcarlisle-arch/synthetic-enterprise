"""Controls for the evidence pages behind the diagram nodes (SITE_evidence_pages_behind_nodes).

The feature under test: every node on the front-door model-on-a-page diagram drills to the
PRIMARY STATE substantiating its stage claim -- the atoms it rests on, their real levels, the
artefacts the map cites, the tests, and the ledger record of each level move.

WHAT THESE CONTROLS ARE FOR (R15). This feature has exactly two characteristic ways to be
worthless, and both are silent:

  1. FAIL-OPEN AT THE SOURCE -- a source artefact is missing and the page renders
     empty-but-plausible. A reader then cannot tell "there is no evidence" from "the generator
     could not read the map", which is strictly worse than no page. Closed by the
     source-unavailable block below: every source, missing AND empty, must raise, and must
     leave the previous page untouched.
  2. FAIL-OPEN AT THE CITATION -- the page cites artefacts that are not there. This site has
     already shipped that defect twice (SITE1/MAJOR-7: dead anchors styled as live ones; and
     its 2026-08-03 follow-up: six of fifteen cited paths archived out from under the
     citation). Closed by an INDEPENDENT oracle: this module stats every path itself with the
     stdlib rather than asking the generator whether it thinks the path resolves. A generator
     bug that labels an absent file RESOLVED is caught by something that never consulted the
     generator, so the pair cannot be tautological (R15 TAUTOLOGY).

Each test names the defect it fires on in its docstring, and each was mutation-proven RED
against that defect before being committed.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent.parent
SITE = PROJECT / "site"
EVIDENCE_JSON = SITE / "data" / "evidence.json"
EVIDENCE_HTML = SITE / "evidence" / "index.html"
FRONT_DOOR = SITE / "index.html"
MAPPING = SITE / "data" / "moap_node_atoms.json"

# The MISSING citations that exist in docs/design/maturity_map.yaml TODAY. This is a RATCHET,
# not a suppression: a NEW unresolvable citation fails this suite loudly, and fixing one of
# these also fails it (telling you to unpin), so the set can only be changed deliberately.
# The map is owned by the orchestrator, not by this atom's file_scope, so these two cannot be
# fixed here -- they are reported instead, and the page renders both of them in red.
#   site/supplier/index.html -- a door that was REMOVED from the site; still cited by
#   B2_opex_cost_to_serve and E2_revenue_reconciliation as evidence of their level.
KNOWN_UNRESOLVED_CITATIONS = {"site/supplier/index.html"}


@pytest.fixture(scope="module")
def payload() -> dict:
    assert EVIDENCE_JSON.is_file(), (
        f"{EVIDENCE_JSON} missing -- run tools/generate_evidence_data.py"
    )
    return json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def page_html() -> str:
    assert EVIDENCE_HTML.is_file(), (
        f"{EVIDENCE_HTML} missing -- run tools/generate_evidence_data.py"
    )
    return EVIDENCE_HTML.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def mapping() -> dict:
    return json.loads(MAPPING.read_text(encoding="utf-8"))


# --- fail-open floors --------------------------------------------------------
# Asserted FIRST so nothing below can pass vacuously on a thin or empty artefact.


def test_payload_is_substantial(payload):
    """FAIL-OPEN FLOOR: a truncated or near-empty payload must not let the real assertions
    below pass over an empty iterable."""
    assert len(payload["nodes"]) >= 6, "expected the six model-on-a-page nodes"
    assert payload["totals"]["atoms"] >= 40, payload["totals"]
    assert payload["totals"]["citations"] >= 150, payload["totals"]
    assert payload["suite"]["test_count"] > 1000, payload["suite"]


def test_page_is_substantial(page_html):
    """FAIL-OPEN FLOOR: the rendered page must actually carry content, not a stub."""
    assert len(page_html) > 20000, f"evidence page is only {len(page_html)} bytes"
    assert "generate_evidence_data.py" in page_html, "generated-by marker absent"
    assert "Loading" not in page_html, (
        "the page must be server-side rendered, not a JS stub: a crawler or a JS-off reader "
        "must see the evidence, not the word 'Loading'"
    )


# --- the drill exists, both ends ---------------------------------------------


def test_every_node_drills_to_its_own_evidence_section(payload, page_html, mapping):
    """DEFECT: a diagram node whose evidence section is absent from the page -- the link
    lands nowhere and the claim is undrillable."""
    for node in mapping["nodes"]:
        nid = node["id"]
        assert f'id="{nid}"' in page_html, (
            f"node {nid!r} has no evidence section on {EVIDENCE_HTML}"
        )
    assert {n["id"] for n in payload["nodes"]} == {n["id"] for n in mapping["nodes"]}


def test_front_door_links_every_node_to_its_evidence_and_nothing_else(mapping, page_html):
    """DEFECT: the front door and the mapping disagree about the node set -- a node silently
    loses its evidence link, or a link points at a section that does not exist.

    Checked in BOTH directions so neither a dropped link nor an orphan link passes."""
    front = FRONT_DOOR.read_text(encoding="utf-8")
    hrefs = re.findall(
        r'<a[^>]*class="node-evidence"[^>]*href="([^"]+)"', front
    )
    assert hrefs, "no node-evidence links on the front door at all"
    frags = [h.split("#", 1)[1] for h in hrefs if "#" in h]
    assert len(frags) == len(hrefs), f"a node-evidence link has no fragment: {hrefs}"
    expected = [n["id"] for n in mapping["nodes"]]
    assert sorted(frags) == sorted(expected), (
        f"front-door evidence links {sorted(frags)} != mapping nodes {sorted(expected)}"
    )
    for frag in frags:
        assert f'id="{frag}"' in page_html, (
            f"front door links to #{frag} but the evidence page has no such anchor"
        )


# --- citations must resolve (INDEPENDENT ORACLE) -----------------------------


def _all_citations(payload):
    for node in payload["nodes"]:
        for atom in node["atoms"]:
            for c in atom["citations"]:
                yield atom["id"], c


def test_every_citation_claimed_resolvable_actually_exists_on_disk(payload):
    """DEFECT (the fail-open core): the page tells a reader an artefact is on disk when it is
    not -- the SITE1/MAJOR-7 class.

    INDEPENDENCE: this stats each path with pathlib directly. It never asks the generator
    whether the path resolves, so a generator that mislabels a missing file as RESOLVED is
    caught by an oracle that shares none of its logic."""
    checked = 0
    for atom_id, c in _all_citations(payload):
        if c["status"] not in ("RESOLVED", "RELOCATED"):
            continue
        resolved = c["resolved_path"]
        assert resolved, f"{atom_id}: status {c['status']} with no resolved_path"
        assert (PROJECT / resolved).exists(), (
            f"{atom_id}: citation {c['path']!r} is published as {c['status']} at "
            f"{resolved!r} but nothing exists there"
        )
        checked += 1
    assert checked >= 150, f"only {checked} citations checked -- floor not met"


def test_unresolved_citations_are_the_known_set_and_no_more(payload):
    """DEFECT: a NEW unresolvable citation enters the map and the page quietly publishes it.

    A ratchet in both directions -- a new one fails, and fixing a pinned one fails too, so the
    pin cannot rot into a permanent suppression."""
    missing = {c["path"] for _, c in _all_citations(payload) if c["status"] == "MISSING"}
    new = missing - KNOWN_UNRESOLVED_CITATIONS
    assert not new, (
        f"new unresolvable evidence citation(s) in the maturity map: {sorted(new)}. "
        "Either fix the citation or add it to KNOWN_UNRESOLVED_CITATIONS with a reason."
    )
    fixed = KNOWN_UNRESOLVED_CITATIONS - missing
    assert not fixed, (
        f"citation(s) {sorted(fixed)} now resolve -- remove them from "
        "KNOWN_UNRESOLVED_CITATIONS so the ratchet keeps its grip."
    )


def test_relocated_citations_report_both_paths(payload):
    """DEFECT: an archived artefact is silently rewritten to its new home, hiding the ROT
    class (docs/staging/X.md -> docs/staging/done/X.md) that keeps recurring."""
    for atom_id, c in _all_citations(payload):
        if c["status"] != "RELOCATED":
            continue
        assert c["path"] != c["resolved_path"], atom_id
        assert not (PROJECT / c["path"]).exists(), (
            f"{atom_id}: {c['path']} is marked RELOCATED but still exists"
        )


# --- missing evidence must be VISIBLY missing --------------------------------


def test_absent_evidence_renders_visibly_missing(payload, page_html):
    """DEFECT (the whole point of the atom): an atom with no evidence renders an
    empty-but-plausible panel, so a reader reads absence as adequacy.

    Every MISSING reason the payload records must appear on the rendered page."""
    reasons = {r for n in payload["nodes"] for a in n["atoms"] for r in a["missing"]}
    assert reasons, "no atom has any missing evidence -- floor implausible, check the payload"
    for reason in reasons:
        assert reason in page_html, (
            f"payload records {reason} but the page never renders it -- absence is being "
            "hidden from the reader"
        )


def test_atoms_without_a_ledger_record_say_so_in_words(payload, page_html):
    """DEFECT: an atom whose level move has no R16 ledger record renders as if it did.

    This is the single most common honest gap on the page today, so it must be stated in
    plain words, not merely absent."""
    no_ledger = [
        a["id"]
        for n in payload["nodes"]
        for a in n["atoms"]
        if "NO_LEDGER_RECORD" in a["missing"]
    ]
    assert no_ledger, "expected some atoms to predate the self-certification ledger"
    assert "No entry in <code>gate_authorizations.jsonl</code>" in page_html
    # Every atom with an EMPTY ledger says so -- which is a superset of the NO_LEDGER_RECORD
    # flag, because an atom still at level 0 has no level move to record and so is not
    # flagged, yet must still show the reader that no record exists.
    empty_ledger = [
        a["id"] for n in payload["nodes"] for a in n["atoms"] if not a["ledger"]
    ]
    assert set(no_ledger) <= set(empty_ledger)
    assert page_html.count("No entry in <code>gate_authorizations.jsonl</code>") == len(
        empty_ledger
    ), "every atom with no ledger entry must render the statement exactly once"


def test_no_citation_is_rendered_as_a_clickable_link(payload, page_html):
    """DEFECT: SITE1/MAJOR-7 -- a repo-internal citation styled as a live link. These paths
    are not web-servable; a dead citation wearing a live link's clothes trains a reader to
    distrust the real ones.

    Every cited path must appear inside an inert `evsrc` span and never inside an anchor."""
    anchors = re.findall(r"<a\b[^>]*>(.*?)</a>", page_html, re.S)
    paths = {c["resolved_path"] or c["path"] for _, c in _all_citations(payload)}
    for path in paths:
        for text in anchors:
            assert path not in text, (
                f"citation {path!r} is rendered inside an anchor -- repo paths are not "
                "web-servable and must render as inert provenance tags"
            )
    assert 'href="#"' not in page_html, "a dead-anchor citation pattern is present"
    sample = sorted(paths)[:20]
    for path in sample:
        assert f'<span class="evsrc' in page_html and path in page_html, path


# --- the page is DERIVED, never hand-typed -----------------------------------


def test_page_is_reproducible_from_the_sources(payload):
    """DEFECT: a hand-typed figure creeps onto the page and goes stale the moment an atom
    moves -- the stale-cell class this project keeps catching.

    Regenerating from the same sources must reproduce the payload exactly, apart from the
    stamps that are meant to change."""
    from tools.generate_evidence_data import build_payload

    fresh = build_payload()
    # `suite` is legitimately volatile: EVERY pytest invocation appends to
    # test_execution_log.jsonl, so this very test run can move it. The evidence content --
    # nodes, atoms, citations, ledger, totals -- must be byte-identical.
    volatile = ("generated_at", "git_hash", "suite")
    assert {k: v for k, v in fresh.items() if k not in volatile} == {
        k: v for k, v in payload.items() if k not in volatile
    }, "the published evidence.json is not reproducible from its sources"
    assert fresh["suite"]["test_count"] > 1000, (
        "the published suite figure must be the largest recorded collection, so a partial "
        "run can never shrink it"
    )


def test_rendered_totals_come_from_the_payload(payload, page_html):
    """DEFECT: the page's headline counts drift from the data they claim to summarise."""
    t = payload["totals"]
    for key in ("citations", "citations_resolved", "citations_missing", "atoms"):
        assert f"<strong>{t[key]}</strong>" in page_html, (
            f"total {key}={t[key]} is not rendered on the page"
        )


# --- source unavailable must be LOUD (fail-silent killer) --------------------

_SOURCES = ("map_path", "mapping_path", "ledger_path", "suite_log_path")


@pytest.fixture
def sources(tmp_path):
    """Real copies of all four sources under tmp_path, so a test can break exactly one."""
    from tools import generate_evidence_data as G

    out = {}
    for kw, src in (
        ("map_path", G.MAP_PATH),
        ("mapping_path", G.MAPPING_PATH),
        ("ledger_path", G.LEDGER_PATH),
        ("suite_log_path", G.SUITE_LOG_PATH),
    ):
        dest = tmp_path / src.name
        shutil.copy2(src, dest)
        out[kw] = dest
    return out


def test_all_four_sources_together_still_build(sources):
    """FAIL-OPEN FLOOR for the block below: with every source present the build SUCCEEDS, so
    the raises below are attributable to the break and not to the fixture."""
    from tools.generate_evidence_data import build_payload

    payload = build_payload(**sources)
    assert len(payload["nodes"]) >= 6


@pytest.mark.parametrize("broken", _SOURCES)
def test_a_missing_source_raises_rather_than_rendering_a_blank_page(sources, broken):
    """DEFECT (fail-silent): a source artefact disappears and the page renders empty, so a
    reader sees a tidy blank where the evidence used to be. An unavailable check is a FAILED
    check, never a passing one."""
    from tools.generate_evidence_data import EvidenceSourceUnavailable, build_payload

    sources[broken].unlink()
    with pytest.raises(EvidenceSourceUnavailable):
        build_payload(**sources)


@pytest.mark.parametrize("broken", _SOURCES)
def test_an_empty_source_raises_rather_than_rendering_a_blank_page(sources, broken):
    """DEFECT (fail-open on empty): the classic pass-on-empty. A zero-byte source must be as
    loud as an absent one."""
    from tools.generate_evidence_data import EvidenceSourceUnavailable, build_payload

    sources[broken].write_text("", encoding="utf-8")
    with pytest.raises(EvidenceSourceUnavailable):
        build_payload(**sources)


@pytest.mark.parametrize("broken", ("ledger_path", "suite_log_path"))
def test_an_unparseable_source_raises(sources, broken):
    """DEFECT: a JSONL source full of garbage parses to zero records and the page renders as
    though nothing had ever been recorded."""
    from tools.generate_evidence_data import EvidenceSourceUnavailable, build_payload

    sources[broken].write_text("not json\n{oops\n", encoding="utf-8")
    with pytest.raises(EvidenceSourceUnavailable):
        build_payload(**sources)


def test_generate_writes_nothing_when_a_source_is_unavailable(tmp_path, monkeypatch):
    """DEFECT: the generator half-writes -- it raises, but only AFTER replacing the live page
    with a blank one. The previous page must survive an unavailable source intact."""
    from tools import generate_evidence_data as G

    out_json = tmp_path / "evidence.json"
    out_html = tmp_path / "index.html"
    out_json.write_text('{"sentinel": true}', encoding="utf-8")
    out_html.write_text("<html>previous page</html>", encoding="utf-8")
    monkeypatch.setattr(G, "OUT_JSON", out_json)
    monkeypatch.setattr(G, "OUT_HTML", out_html)
    monkeypatch.setattr(G, "MAP_PATH", tmp_path / "does_not_exist.yaml")

    with pytest.raises(G.EvidenceSourceUnavailable):
        G.generate()

    assert json.loads(out_json.read_text()) == {"sentinel": True}
    assert out_html.read_text() == "<html>previous page</html>"


def test_a_node_with_no_atoms_cannot_render_as_evidenced(tmp_path, sources):
    """DEFECT: an empty node vacuously reads as fully evidenced (`all([])` is True), the
    exact false-green the Phase-B derivation guards against."""
    from tools.generate_evidence_data import build_payload

    mapping = json.loads(sources["mapping_path"].read_text(encoding="utf-8"))
    mapping["nodes"][0]["atoms"] = []
    sources["mapping_path"].write_text(json.dumps(mapping), encoding="utf-8")

    payload = build_payload(**sources)
    node = payload["nodes"][0]
    assert node["computed_stage"] == "Planned", (
        "an atom-less node must never compute Live"
    )
    assert node["atoms_at_target"] == 0
