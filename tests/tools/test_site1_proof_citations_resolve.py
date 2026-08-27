"""MAJOR-7, the half the styling fix does not reach: a PUBLISHED citation must
point at an artefact that ACTUALLY EXISTS.

Expert-Hour finding (docs/design/maturity_map.yaml :: SITE1_expert_doors
expert_hour.findings):

  MAJOR-7 "evidence citations that are inert by construction ... The cited paths
          are not published: /docs/review_gates/done/HEDGE_VOLATILITY_LOOKBACK_
          FORESIGHT_BUG.md -> 404 ... On a page whose proposition is 'walk any
          figure to its evidence', styling a dead citation as a link trains a
          reader to distrust the real ones."

Two RIVAL rescue branches each closed the STYLING half of that finding (a dead
<a href="#"> now renders as an inert provenance tag). Neither closed this half.
Audited on 2026-08-03, six of the fifteen repo-internal paths the door published
did not exist at the path shown:

    docs/staging/CLOCK_TRUTH_AND_THE_BRIDGE.md
    docs/staging/DOMAIN_SENSE_AND_COMPLIANCE.md
    docs/staging/END_TO_END_VERIFICATION.md
    docs/staging/MARGIN_REALISM.md
    docs/staging/DIRECTOR_AXIS1_SITE_VERDICT_ROWSCORED_2026-07-23.md
    docs/design/PURPOSE_PITCH_V4.md (§12)

Not one was invented -- every one had been ARCHIVED by the staging protocol
(docs/staging/X.md -> docs/staging/done/X.md, or in_progress/) after the citation
was authored. Telling a reader the evidence is at a path where nothing sits is the
same lie as a dead anchor, wearing different clothes, and it is a ROT class: it
recurs at every archive sweep. Hence a resolver in the generator (fix the class,
R10) and this gate.

INDEPENDENCE (R15 anti-TAUTOLOGY). This test never asks the resolver whether a
path resolves. It reads the PUBLISHED site/data/proof.json and stats each path
itself, so the oracle (the filesystem) is a different thing from the mechanism
under test (generate_proof_data._resolve_citation). The resolver's documented
fallback is to leave an unfindable citation UNCHANGED, precisely so this gate
fires rather than the publish pipeline wedging.

ANTI-PIN. Nothing here pins a count, a date or a specific path -- the assertion is
the RELATIONSHIP "every published citation resolves", so regenerating the data can
never wedge it.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

import tools.generate_proof_data as gpd

PROJECT = Path(__file__).resolve().parents[2]
PROOF_JSON = PROJECT / "site" / "data" / "proof.json"


# ---------------------------------------------------------------------------
# The independent oracle: walk a payload, stat every citation with the stdlib.
# ---------------------------------------------------------------------------
def _unresolved(payload) -> list[str]:
    """Every citation string in `payload` whose path does not exist on disk."""
    bad: list[str] = []

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key in gpd.CITATION_KEYS and isinstance(value, str):
                    path, _ = gpd.citation_path(value)
                    if path is not None and not (PROJECT / path).exists():
                        bad.append(value)
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(payload)
    return bad


def _citations(payload) -> list[str]:
    found: list[str] = []

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key in gpd.CITATION_KEYS and isinstance(value, str):
                    found.append(value)
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(payload)
    return found


@pytest.fixture(scope="module")
def published() -> dict:
    # FAIL-SILENT guard: an unreadable published artefact is a FAILED check, never
    # a skipped one -- an absence assertion over {} would pass vacuously.
    assert PROOF_JSON.is_file(), f"{PROOF_JSON} missing -- the gate has nothing to check"
    data = json.loads(PROOF_JSON.read_text())
    assert isinstance(data, dict) and data, "published proof.json is empty"
    return data


# ===========================================================================
# The gate itself
# ===========================================================================
def test_every_published_citation_resolves_to_a_real_artefact(published):
    # FAIL-OPEN floor: prove there ARE citations before asserting none are broken.
    cites = _citations(published)
    assert len(cites) >= 10, f"only {len(cites)} citations found -- the gate is checking nothing"
    paths = [c for c in cites if gpd.citation_path(c)[0] is not None]
    assert len(paths) >= 10, f"only {len(paths)} of {len(cites)} citations parsed as paths"

    bad = _unresolved(published)
    assert bad == [], (
        "the Proof door publishes %d citation(s) pointing at nothing: %s -- a reader "
        "told to walk the figure to its evidence finds an empty path" % (len(bad), bad))


def test_the_gate_fires_on_a_phantom_citation(published):
    """R15: prove this control can FAIL, on its own named defect."""
    mutated = copy.deepcopy(published)
    mutated["corrections"][0]["source"] = "docs/staging/THIS_FILE_DOES_NOT_EXIST.md"
    bad = _unresolved(mutated)
    assert "docs/staging/THIS_FILE_DOES_NOT_EXIST.md" in bad, (
        "the citation gate did NOT fire on a phantom path")


def test_the_gate_fires_on_the_exact_historical_defect(published):
    """The real 2026-08-03 defect: a staging directive cited at its pre-archive
    path after the staging protocol moved it into done/."""
    stale = "docs/staging/MARGIN_REALISM.md"
    assert not (PROJECT / stale).exists(), (
        "premise changed: %s exists again, so it is no longer the historical defect" % stale)
    assert (PROJECT / "docs/staging/done/MARGIN_REALISM.md").exists(), (
        "the artefact is not in done/ either -- update this test's premise")
    mutated = copy.deepcopy(published)
    mutated["timeline"][0]["source"] = stale
    assert stale in _unresolved(mutated), "the gate missed the real historical defect"


def test_the_gate_does_not_false_positive_on_a_live_path(published):
    """R15 the other way: the control must clear on good input."""
    mutated = copy.deepcopy(published)
    mutated["corrections"][0]["source"] = "docs/design/maturity_map.yaml"
    assert (PROJECT / "docs/design/maturity_map.yaml").is_file()
    assert _unresolved(mutated) == [], "the gate false-positives on a genuinely live path"


def test_a_url_citation_is_never_stat_ed_as_a_path(published):
    mutated = copy.deepcopy(published)
    mutated["corrections"][0]["source"] = "https://www.ofgem.gov.uk/some/page"
    assert _unresolved(mutated) == [], "a URL citation was wrongly treated as a repo path"


# ===========================================================================
# citation_path: the path/prose/URL split, both directions
# ===========================================================================
@pytest.mark.parametrize("value", [
    "https://example.com/x.md",
    "http://example.com/x.md",
    "",
    "   ",
    None,
    123,
    "docs/retrospectives/",                      # a directory, not a file
    "no hedge-outcome source is built",          # honest prose: there IS no source
    "not instrumented yet",
])
def test_citation_path_returns_none_for_non_paths(value):
    assert gpd.citation_path(value) == (None, None), value


def test_citation_path_strips_a_section_annotation_but_keeps_it_as_a_label():
    path, annotation = gpd.citation_path("docs/design/PURPOSE_PITCH_V4.md (§12)")
    assert path == "docs/design/PURPOSE_PITCH_V4.md", path
    assert "12" in annotation, annotation


def test_a_missing_path_is_never_waved_through_as_prose():
    """FAIL-OPEN guard on the prose heuristic: the only thing that makes a string
    prose is whitespace, so a broken path can never hide behind it."""
    path, _ = gpd.citation_path("docs/staging/GONE.md")
    assert path == "docs/staging/GONE.md", "a broken path was excused as prose"
    assert not (PROJECT / path).exists()


# ===========================================================================
# _resolve_citation / resolve_citations: the fix mechanism
# ===========================================================================
def test_resolver_repoints_an_archived_staging_directive():
    out = gpd._resolve_citation("docs/staging/MARGIN_REALISM.md")
    assert out == "docs/staging/done/MARGIN_REALISM.md", out
    assert (PROJECT / out).is_file()


def test_resolver_repoints_a_parked_in_progress_directive():
    name = "DIRECTOR_AXIS1_SITE_VERDICT_ROWSCORED_2026-07-23.md"
    out = gpd._resolve_citation("docs/staging/" + name)
    assert out == "docs/staging/in_progress/" + name, out
    assert (PROJECT / out).is_file()


def test_resolver_preserves_a_section_annotation_when_it_repoints(tmp_path, monkeypatch):
    monkeypatch.setattr(gpd, "PROJECT", tmp_path)
    (tmp_path / "docs" / "staging" / "done").mkdir(parents=True)
    (tmp_path / "docs" / "staging" / "done" / "X.md").write_text("x")
    out = gpd._resolve_citation("docs/staging/X.md (§4)")
    assert out == "docs/staging/done/X.md (§4)", out


def test_resolver_leaves_a_live_path_untouched():
    live = "docs/design/maturity_map.yaml"
    assert gpd._resolve_citation(live) == live


def test_resolver_leaves_an_unfindable_path_untouched_rather_than_inventing_one():
    """The publish path must never wedge, and must never fabricate a location --
    an unfindable citation passes through and this file's gate catches it."""
    ghost = "docs/staging/NO_SUCH_ARTEFACT_ANYWHERE.md"
    assert gpd._resolve_citation(ghost) == ghost


def test_resolver_walks_nested_lists_and_dicts():
    payload = {"a": [{"source": "docs/staging/MARGIN_REALISM.md"},
                     {"b": {"doctrine": "docs/staging/CONTROLS_THAT_CANNOT_FAIL.md"}}]}
    gpd.resolve_citations(payload)
    assert payload["a"][0]["source"] == "docs/staging/done/MARGIN_REALISM.md"
    assert payload["a"][1]["b"]["doctrine"] == "docs/staging/done/CONTROLS_THAT_CANNOT_FAIL.md"


def test_resolver_ignores_a_non_citation_key_that_happens_to_hold_a_path():
    """Only declared CITATION_KEYS are rewritten -- a file_scope or evidence entry
    must not be silently re-pointed by this mechanism."""
    payload = {"file_scope": "docs/staging/MARGIN_REALISM.md"}
    gpd.resolve_citations(payload)
    assert payload["file_scope"] == "docs/staging/MARGIN_REALISM.md"


def _resolver_call_lines() -> list[str]:
    """Lines of generate() that CALL resolve_citations -- comments excluded.

    A substring search alone is fail-open: "# resolve_citations(data)" contains
    "resolve_citations(" and would satisfy it while the mechanism is dead code.
    Caught by mutation M8 on 2026-08-03; this is the closed version.
    """
    import inspect
    return [ln.strip() for ln in inspect.getsource(gpd.generate).splitlines()
            if ln.strip().startswith("resolve_citations(")]


def test_the_generator_actually_calls_the_resolver():
    """No orphan mechanism (R11): the resolver must be WIRED into generate(),
    not merely defined -- a mechanism nobody invokes is the fix that isn't."""
    assert _resolver_call_lines(), "resolve_citations is never called by generate()"


def test_the_wiring_check_is_not_satisfied_by_a_commented_out_call():
    """R15 on the control above: prove it rejects the exact shape that fooled it."""
    commented = ["# resolve_citations(data)", "  # resolve_citations(data)"]
    assert not [ln for ln in commented if ln.strip().startswith("resolve_citations(")], (
        "the wiring check would accept a commented-out call")


# ---------------------------------------------------------------------------
# THE PROVENANCE-LABEL CARVE-OUT (2026-08-27)
# ---------------------------------------------------------------------------
# Implements the recommendation in
# docs/staging/done/WORKER_FINDING_A_PROVENANCE_LABEL_IS_STAT_ED_AS_A_REPO_PATH_2026-08-18.md,
# diagnosed nine days before it was built. `source` is an overloaded key: a repo-relative
# artefact to the Proof door's citations, a derivation METHOD in `couple_w2_11_d5`'s
# `_measured_on` blocks. The gate was stat-ing the method label and reporting a dead citation on
# a figure whose provenance is honestly recorded.
#
# A control that fires on correct data trains its reader to skip it -- and while it cried wolf,
# the REAL rot class (an archived citation) would have landed inside the same red and been
# indistinguishable from the noise. So the narrowing needs its partner more than most.

from tools.generate_proof_data import citation_path  # noqa: E402


def test_a_bare_provenance_label_is_not_read_as_a_path():
    assert citation_path("predicted_from_this_book") == (None, None)


@pytest.mark.parametrize("still_a_path", [
    "docs/staging/GONE.md",   # the rot class: separator AND extension
    "GONE.md",                # no separator, but an extension -- still nameable
    "site/data/proof.json",
    "tools/generate_proof_data.py",
])
def test_the_carve_out_does_NOT_swallow_a_real_citation(still_a_path):
    """THE PARTNER, and the one that matters. The FAIL-OPEN direction is the expensive one: an
    archived citation waved through as prose is exactly the lie this gate exists to catch."""
    assert citation_path(still_a_path) == (still_a_path, "")


def test_a_dotted_token_with_no_separator_is_still_checked():
    """A file in the repo root is a real citation and carries no separator at all -- the
    narrowing keys on "no separator AND no extension", never on the separator alone."""
    assert citation_path("CLAUDE.md") == ("CLAUDE.md", "")


def test_the_other_two_carve_outs_are_untouched():
    assert citation_path("https://example.com/x") == (None, None)
    assert citation_path("no hedge-outcome source is built") == (None, None)
    assert citation_path("docs/retrospectives/") == (None, None)
