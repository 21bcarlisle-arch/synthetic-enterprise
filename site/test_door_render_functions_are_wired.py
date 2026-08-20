"""R10 CLASS CONTROL: a door's render function must be WIRED, not merely defined.

WHY THIS EXISTS (2026-08-11, cold-eyes Expert Hour on the live site).
`site/company/index.html` defined `renderBookMix` at line 327 and never called it.
The live door served `<p id="mix-intro">Loading...</p>` for 8 days (since 93fbc41a7,
2026-08-03) under the heading "Whose book this is -- the revenue mix, before any
claim", while the FRONT door delegated to it by name. The block's own source comment
states its purpose: a reader who meets "Net margin / customer" before learning that
~99% of the revenue is earned by five I&C accounts "has been misled by ORDERING".
That is exactly what every live reader got.

THREE CONTROLS ALL PASSED OVER IT, which is why the fix is a class and not a call:
  1. `site/company/_render_harness.mjs` hand-typed `sandbox.renderBookMix(d)` ITSELF,
     so the three door tests in test_company_door.py asserted rendered pixels for a
     panel the page never rendered -- the control was a PRODUCER of its own evidence
     (R15 tautology). Fixed at the cause: the harness now derives its call set from
     the page's boot path and exits non-zero on an orphan.
  2. `site/live_pixel_verify.py` grades only elements the page's script WROTE, so an
     element left at its shipped `Loading...` placeholder is outside the checked
     population -- fail-open for PARTIAL render, a commoner shape than the total
     render failure it was built for.
  3. The precedent rule already existed in-repo and was never generalised:
     tests/tools/test_site1_proof_citations_resolve.py::test_the_generator_actually_
     calls_the_resolver ("a mechanism nobody invokes is the fix that isn't", mutation
     M8) landed 2026-08-03 -- the SAME DAY this shipped dead.

R10 says an absurdity-class defect may not be closed with an instance fix. So this
grades EVERY door, not the one that failed.

BLAST RADIUS, MEASURED BEFORE THE PREDICATE WAS CHOSEN: 110 render functions across
12 doors, exactly 1 orphan (`renderBookMix`). This control therefore lands with no
cleanup backlog behind it -- it is a standing guard, not a ratchet over known dirt.

R15 (a control must be able to FAIL): the mechanism tests below prove the predicate
fires on an orphan, stays quiet on both legitimate wiring shapes (direct call and
by-reference `.then(fn)`), and -- per mutation M8's lesson -- is not satisfied by a
COMMENTED-OUT call. The vacuity guard proves it cannot fail-open by globbing nothing.
"""

import re
from pathlib import Path

_SITE_ROOT = Path(__file__).resolve().parent


def _strip_comments(code: str) -> str:
    """Remove JS comments so a commented-out call cannot count as wiring.

    Mutation M8's lesson, applied here before it could bite: a bare substring search
    accepts `// renderBookMix(d)` while the mechanism is dead. `://` is preserved so
    a URL in a string is not mistaken for a line comment.
    """
    code = re.sub(r"/\*[\s\S]*?\*/", "", code)
    return "\n".join(re.sub(r"(?<!:)//.*$", "", line) for line in code.splitlines())


def orphan_render_functions(code: str) -> list[str]:
    """Render functions DEFINED in this script but invoked nowhere in it.

    Two legitimate wiring shapes, both counted:
      * a direct call      -- `renderState(d);`
      * a reference handed to something that will call it -- `.then(renderCoverage)`
    """
    live = _strip_comments(code)
    defined = re.findall(r"^\s*function\s+(render[A-Za-z0-9_]*)\s*\(", live, re.M)
    orphans = []
    for fn in defined:
        direct = any(
            not live[: m.start()].rstrip().endswith("function")
            for m in re.finditer(rf"\b{fn}\s*\(", live)
        )
        by_ref = re.search(rf"[=,(\[]\s*{fn}\s*[,)\]]", live) is not None
        if not direct and not by_ref:
            orphans.append(fn)
    return orphans


def _door_scripts() -> dict[Path, str]:
    doors = {}
    for path in sorted(_SITE_ROOT.glob("*/index.html")):
        code = "\n".join(re.findall(r"<script>([\s\S]*?)</script>", path.read_text()))
        if re.search(r"^\s*function\s+render", code, re.M):
            doors[path] = code
    return doors


# --------------------------------------------------------------------------
# LIVE GATE -- the real doors, every one of them
# --------------------------------------------------------------------------


def test_no_door_defines_a_render_function_it_never_invokes():
    """The class fix for `renderBookMix`: a panel whose renderer is never called
    serves its shipped "Loading..." placeholder to every live reader, and no
    pixel-level control catches it because the element was never written."""
    offenders = {
        path.relative_to(_SITE_ROOT).as_posix(): orphans
        for path, code in _door_scripts().items()
        if (orphans := orphan_render_functions(code))
    }
    assert not offenders, f"door render functions defined but never invoked: {offenders}"


def test_the_gate_actually_has_a_population_to_grade():
    """Vacuity guard: a glob that matches nothing passes the gate above silently.
    Measured 2026-08-11: 12 doors, 110 render functions."""
    doors = _door_scripts()
    total = sum(len(re.findall(r"^\s*function\s+render", code, re.M)) for code in doors.values())
    assert len(doors) >= 2, f"only {len(doors)} doors found -- the glob is broken, not the site"
    # The floor was 50, sized to a site with eleven JavaScript doors. Two remain, and the
    # number is not the property -- "the extractor still finds functions" is. A floor that
    # tracks the site's size would need re-pinning on every fold, which is how it goes stale.
    assert total >= 5, f"only {total} render functions found -- the extractor is broken"


# --------------------------------------------------------------------------
# R15 MECHANISM SELF-TESTS -- prove the predicate can fail, and can pass
# --------------------------------------------------------------------------

_ORPHAN = """
function renderThing(d){ el("x").innerHTML="hi"; }
jget("../data/a.json").then(function(d){ renderOther(d); });
"""

_DIRECT = """
function renderThing(d){ el("x").innerHTML="hi"; }
Promise.all([a]).then(function(res){ renderThing(res[0]); });
"""

_BY_REF = """
function renderThing(d){ el("x").innerHTML="hi"; }
jget("../data/a.json").then(renderThing).catch(noop);
"""

_COMMENTED = """
function renderThing(d){ el("x").innerHTML="hi"; }
// renderThing(d);
"""


def test_the_predicate_fires_on_the_defect_it_was_built_for():
    assert orphan_render_functions(_ORPHAN) == ["renderThing"]


def test_a_direct_call_counts_as_wiring():
    """Independence: the predicate is not always-positive."""
    assert orphan_render_functions(_DIRECT) == []


def test_a_by_reference_handoff_counts_as_wiring():
    """`.then(renderCoverage)` is how 3 of the company door's 11 functions are wired;
    a predicate blind to it would red 12 doors and be turned off within a day."""
    assert orphan_render_functions(_BY_REF) == []


def test_a_commented_out_call_is_not_wiring():
    """Mutation M8's exact shape, pre-empted: the fail-open that would let this
    control pass over a mechanism someone commented out during a debug session."""
    assert orphan_render_functions(_COMMENTED) == ["renderThing"]


def test_a_url_in_a_string_is_not_mistaken_for_a_comment():
    """The comment-stripper must not eat live code following an https:// literal."""
    code = 'var u="https://poesys.net/x"; function renderThing(d){}\nrenderThing(1);'
    assert orphan_render_functions(code) == []
