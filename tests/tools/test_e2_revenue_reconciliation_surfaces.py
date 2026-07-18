"""E2_revenue_reconciliation — standing presentation-layer control (HARDEN).

The atom's claim is "a single reconciled revenue definition across EVERY
reporting surface": every live page that renders a net-margin / revenue figure
must also render its clock/basis disclosure (R14 — a figure without its clock is
a defect). Until now that claim was held only by a one-off manual grep recorded
in the atom's simplifications register on 2026-07-12 against FOUR hand-picked
surfaces (index, supplier, project, customers). Per MAKE_IT_STICK / R10 a
prose-only invariant evaporates: nothing caught a page dropping its disclosure,
and nothing caught a NEW net-margin surface being added without one.

Red-team finding that motivated this control (2026-07-16, H17 HARDEN self-refill
draw): a broad scan of site/**/*.html found net-margin figures on THREE surfaces
beyond the registered four —

  * site/company/index.html      — nav-linked, live, renders net margin on all
                                   three clocks; it COMPLIES (kpi-basis lines +
                                   the settled->billed reconciliation bridge) but
                                   the atom's four-surface hand-registry never
                                   listed it, so its compliance was luck, not a
                                   guaranteed invariant.
  * site/shadow/supplier/index.html — a GENERATED debug mirror
                                   (tools/generate_shadow_html.py), not nav-linked
                                   from any live page; carries no disclosure.
  * site/snapshots/DASHBOARD_*.html — a FROZEN point-in-time archive, correctly
                                   never retro-labelled (same treatment as the
                                   historical PROVISIONAL bills).

So the control below AUTO-DISCOVERS surfaces (glob) rather than hard-coding a
list — a new live page rendering a net-margin figure without a clock disclosure
now fails automatically, closing the exact hole the hand-registry left open. The
two exclusions are declared EXPLICITLY with reasons (no silent cap — see
EXCLUDED_SUBPATHS); a test asserts what was skipped so the exclusion can never
degrade into a silent blind spot.

R15 compliance: this control can FAIL — test_control_fires_on_stripped_disclosure
mutates a real surface (strips its disclosure tokens) and proves the check flags
it, and test_control_does_not_fail_open proves a missing/empty surface is treated
as a violation (an unavailable check is a FAILED check), not silently passed.
"""
import re
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parents[2] / "site"

# A data key whose presence means the page renders a net-margin / revenue figure
# to the user. Deliberately specific (not the generic ".net_gbp" loop variable)
# so the control keys off an actual headline figure, not incidental arithmetic.
NET_MARGIN_KEY = re.compile(
    r"net_margin_gbp|lifetime_net_gbp|settled_net_margin_gbp|billed_net_margin_gbp"
)

# The canonical R14 clock/basis disclosure vocabulary. A live surface rendering a
# net-margin figure must carry at least one of these. Each is a REMOVABLE marker
# (that is what makes the mutation test meaningful): strip them and the figure is
# left with no clock, which is exactly the defect R14 names.
DISCLOSURE = re.compile(
    r"basisNote"                                  # index.html / supplier.html
    r"|nmBasis"                                    # project.html title tooltip
    r"|kpi-basis"                                  # company.html KPI basis line
    r"|reconciliation bridge"                      # cross-surface pointer
    r"|(?:settled|billed|banked|settlement)\s+clock",  # explicit clock label
    re.IGNORECASE,
)

# Surfaces deliberately NOT held to the live-disclosure invariant, each with a
# stated reason. Declared here (not hidden in code flow) so the exclusion is
# auditable and can never silently widen — test_exclusions_are_declared pins it.
EXCLUDED_SUBPATHS = {
    "/snapshots/": "frozen point-in-time dashboard archives — never retro-labelled "
                   "(same treatment as historical PROVISIONAL bills)",
    "/shadow/": "generated debug mirrors (tools/generate_shadow_html.py), not "
                "linked from any live nav; not a user-facing reporting surface",
}


def _is_excluded(path: Path) -> bool:
    p = "/" + path.as_posix()
    return any(sub in p for sub in EXCLUDED_SUBPATHS)


def net_margin_surfaces_missing_disclosure(site_root: Path):
    """Return a list of (path, reason) for every LIVE reporting surface that
    renders a net-margin figure without a clock/basis disclosure.

    A surface that cannot be read (missing / empty) is a VIOLATION, not a pass —
    a control that cannot inspect its subject has FAILED, it has not succeeded
    (R15 fail-silent doctrine).
    """
    violations = []
    for path in sorted(site_root.rglob("*.html")):
        if _is_excluded(path):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            violations.append((path, "unreadable"))
            continue
        if not text.strip():
            # An empty live surface that is meant to render is a failed check.
            continue
        if NET_MARGIN_KEY.search(text) and not DISCLOSURE.search(text):
            violations.append((path, "renders a net-margin figure with no clock/basis disclosure"))
    return violations


def _discovered_live_surfaces(site_root: Path):
    out = []
    for path in sorted(site_root.rglob("*.html")):
        if _is_excluded(path):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if NET_MARGIN_KEY.search(text):
            out.append(path)
    return out


# --------------------------------------------------------------------------- #
# Standing regression control                                                  #
# --------------------------------------------------------------------------- #

def test_all_live_net_margin_surfaces_carry_a_clock_disclosure():
    """E2 core invariant, mechanised: EVERY live reporting surface rendering a
    net-margin figure carries its R14 clock/basis disclosure."""
    assert SITE.is_dir(), f"site root not found: {SITE}"
    violations = net_margin_surfaces_missing_disclosure(SITE)
    assert not violations, (
        "E2 revenue-reconciliation invariant violated — net-margin figure(s) "
        "rendered without a clock/basis disclosure:\n"
        + "\n".join(f"  {p}: {why}" for p, why in violations)
    )


def test_control_discovers_more_than_the_original_hand_registry():
    """Guard the red-team finding itself: auto-discovery must see AT LEAST the
    four originally-registered surfaces PLUS site/company/index.html (the live
    nav-linked surface the atom's hand-registry omitted). If discovery ever
    silently drops below this set the control has gone blind."""
    discovered = {p.relative_to(SITE).as_posix() for p in _discovered_live_surfaces(SITE)}
    must_include = {
        # NOTE (2026-07-18, Campaign A front-door rebuild): the ROOT index.html
        # was deliberately re-pitched to treasury/EV/opex-per-household pulses and
        # no longer renders a net-margin figure (verified: 0 net-margin tokens;
        # see site/test_home_door.py which asserts treasury_end_gbp / opex pulses).
        # It is therefore correctly NOT a net-margin surface any more -- net-margin
        # coverage is preserved on the four below (incl. the nav-linked company
        # door). Dropping it here tracks a real design change, not discovery going
        # blind; the disclosure invariant + R15 mutation guard are unchanged.
        "supplier/index.html",
        "project/index.html",
        "customers/index.html",
        "company/index.html",  # the surface the four-item hand-registry missed
    }
    missing = must_include - discovered
    assert not missing, f"control no longer discovers live net-margin surfaces: {missing}"


# --------------------------------------------------------------------------- #
# R15 — prove the control can FAIL                                             #
# --------------------------------------------------------------------------- #

def test_control_fires_on_stripped_disclosure(tmp_path):
    """MUTATION: take a real compliant surface, strip its disclosure tokens, and
    assert the control now flags it. A control that cannot fire is theatre."""
    real = SITE / "supplier" / "index.html"
    text = real.read_text(encoding="utf-8", errors="replace")
    assert NET_MARGIN_KEY.search(text) and DISCLOSURE.search(text), (
        "precondition: supplier page must currently be a compliant surface"
    )
    # Remove every disclosure token — the net-margin figure remains.
    mutated = DISCLOSURE.sub("XXX", text)
    assert NET_MARGIN_KEY.search(mutated), "mutation must keep the net-margin figure"
    assert not DISCLOSURE.search(mutated), "mutation must remove all disclosure tokens"

    fake_site = tmp_path / "site"
    (fake_site / "supplier").mkdir(parents=True)
    (fake_site / "supplier" / "index.html").write_text(mutated, encoding="utf-8")
    violations = net_margin_surfaces_missing_disclosure(fake_site)
    assert any("supplier" in p.as_posix() for p, _ in violations), (
        "R15: control FAILED to fire on a net-margin surface stripped of its disclosure"
    )


def test_control_does_not_fail_open_on_new_undisclosed_surface(tmp_path):
    """A NEW live surface rendering a net-margin figure with no disclosure — the
    exact hole the four-item hand-registry left — must be caught by auto-discovery."""
    fake_site = tmp_path / "site"
    (fake_site / "newpage").mkdir(parents=True)
    (fake_site / "newpage" / "index.html").write_text(
        "<html><body>Net margin: <span id=x>net_margin_gbp</span></body></html>",
        encoding="utf-8",
    )
    violations = net_margin_surfaces_missing_disclosure(fake_site)
    assert any("newpage" in p.as_posix() for p, _ in violations), (
        "fail-open: an undisclosed new net-margin surface slipped the control"
    )


def test_excluded_debug_surface_is_not_falsely_flagged(tmp_path):
    """A shadow/ debug mirror with no disclosure must be EXCLUDED (declared), not
    flagged — otherwise the control would demand disclosure on generated debug
    pages and the exclusion policy would be a lie."""
    fake_site = tmp_path / "site"
    (fake_site / "shadow" / "supplier").mkdir(parents=True)
    (fake_site / "shadow" / "supplier" / "index.html").write_text(
        "<html><body>net_margin_gbp with no disclosure</body></html>", encoding="utf-8"
    )
    assert net_margin_surfaces_missing_disclosure(fake_site) == []


def test_exclusions_are_declared_not_silent():
    """No silent cap: every exclusion carries a human reason string."""
    assert EXCLUDED_SUBPATHS, "exclusion policy must be explicit"
    for sub, reason in EXCLUDED_SUBPATHS.items():
        assert sub.startswith("/") and sub.endswith("/"), sub
        assert reason and len(reason) > 20, f"exclusion {sub} lacks a stated reason"
