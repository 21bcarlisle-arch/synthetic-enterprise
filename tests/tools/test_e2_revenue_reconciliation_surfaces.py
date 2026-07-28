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

R15 compliance: this control can FAIL —
  * test_control_fires_on_stripped_disclosure mutates a real surface (strips its
    disclosure tokens) and proves the check flags it;
  * test_control_does_not_fail_open_on_new_undisclosed_surface proves a NEW live
    net-margin surface with no disclosure is caught by auto-discovery;
  * test_control_does_not_fail_open_on_missing_expected_surface proves the exact
    fail-silent hole R15 pattern 3 names — an EXPECTED net-margin surface that
    goes missing/empty/loses its net-margin figure (a truncated or broken deploy)
    is treated as a VIOLATION, not silently passed. Auto-discovery alone cannot
    catch this: a surface that renders nothing is invisible to a content glob, so
    the core control now carries an explicit expected-surface registry
    (EXPECTED_NET_MARGIN_SURFACES) whose absence fails the check. An unavailable
    check is a FAILED check.

Red-team note (2026-07-27, HARDEN self-refill draw): before this pass the module
docstring CLAIMED a `test_control_does_not_fail_open` proved missing/empty = a
violation, but no such test existed and net_margin_surfaces_missing_disclosure
did the opposite — it `continue`d past an empty file (skip = pass). An emptied
company/index.html produced zero violations while a headline reporting surface
was blank. That advertised-but-unimplemented guarantee (R15 theatre) is now real
code + a mutation test, not prose.
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

# Live surfaces that MUST render a net-margin figure. Auto-discovery (a content
# glob) cannot notice a surface that has gone blank — an emptied/truncated deploy
# renders no net-margin token and simply drops out of the discovered set, passing
# the disclosure scan silently. So the core control also asserts these surfaces
# are PRESENT, non-empty and still rendering their figure; an unavailable expected
# surface is a VIOLATION (R15 fail-silent doctrine — an unavailable check has
# FAILED, not succeeded). Kept in lockstep with the must_include set below.
EXPECTED_NET_MARGIN_SURFACES = (
    "project/index.html",
    "customers/index.html",
    "company/index.html",   # the nav-linked surface the four-item hand-registry missed
    # (2026-07-28 HARDEN red-team) two further LIVE nav-linked doors were found
    # rendering the net_margin_gbp figure yet sitting OUTSIDE this fail-silent
    # registry -- an emptied deploy of either would have passed the control green.
    # site/index.html links "./proof/" as a top-level door and "./now/" as "the
    # business right now". They are load-bearing public reporting surfaces, so an
    # emptied/vanished deploy of either is a fail-silent VIOLATION, not a pass.
    # test_no_live_net_margin_surface_escapes_expected_registry now forbids this
    # registry from ever going stale again (discovered subset of EXPECTED).
    "now/index.html",
    "proof/index.html",
)


def _is_excluded(path: Path) -> bool:
    p = "/" + path.as_posix()
    return any(sub in p for sub in EXCLUDED_SUBPATHS)


def net_margin_surfaces_missing_disclosure(site_root: Path, expected=()):
    """Return a list of (path, reason) for every LIVE reporting surface that
    renders a net-margin figure without a clock/basis disclosure.

    ``expected`` is a tuple of site-relative paths that MUST render a net-margin
    figure. Each is checked for presence / non-emptiness / a net-margin token; an
    expected surface that cannot be inspected (missing, empty, or no longer a
    net-margin surface) is a VIOLATION, not a pass — a control that cannot inspect
    its subject has FAILED, it has not succeeded (R15 fail-silent doctrine). A
    content glob alone cannot catch this: a blank surface renders no token and
    silently drops out of discovery, which is exactly the hole this closes.
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
            # An empty file carries no net-margin token, so the disclosure scan
            # cannot judge it. Emptiness of an EXPECTED surface is caught below
            # (fail-closed); a non-expected empty page is legitimately skipped.
            continue
        if NET_MARGIN_KEY.search(text) and not DISCLOSURE.search(text):
            violations.append((path, "renders a net-margin figure with no clock/basis disclosure"))

    # Fail-silent guard: every expected surface must be present, non-empty and
    # still rendering its net-margin figure. This is the check auto-discovery
    # cannot perform (a blank surface is invisible to a content glob).
    for rel in expected:
        p = site_root / rel
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            violations.append((p, "expected net-margin surface missing/unreadable — fail-silent guard"))
            continue
        if not text.strip():
            violations.append((p, "expected net-margin surface is empty — fail-silent guard"))
        elif not NET_MARGIN_KEY.search(text):
            violations.append((p, "expected net-margin surface no longer renders its net-margin figure — fail-silent guard"))
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
    violations = net_margin_surfaces_missing_disclosure(SITE, expected=EXPECTED_NET_MARGIN_SURFACES)
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
        # (2026-07-19 v4 retirement) supplier/index.html retired -- the old Supplier
        # split re-homes into The Company; its net-margin+disclosure coverage lives
        # on company/index.html below, so discovery is unchanged, not going blind.
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
    real = SITE / "company" / "index.html"   # (v4) supplier retired; company is the live twin
    text = real.read_text(encoding="utf-8", errors="replace")
    assert NET_MARGIN_KEY.search(text) and DISCLOSURE.search(text), (
        "precondition: company page must currently be a compliant net-margin surface"
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


def test_control_does_not_fail_open_on_missing_expected_surface(tmp_path):
    """R15 fail-silent (pattern 3): an EXPECTED net-margin surface that goes
    missing / empty / loses its net-margin figure — a truncated or broken deploy
    that renders a blank page — is invisible to a content glob, so it must be
    caught by the expected-surface registry, not silently passed.

    Both directions proven: a present, compliant surface yields NO violation; the
    same surface emptied yields a violation naming it.
    """
    fake_site = tmp_path / "site"
    (fake_site / "company").mkdir(parents=True)
    good = fake_site / "company" / "index.html"
    good.write_text(
        "<html><body>net_margin_gbp <span class='basisNote'>settled clock</span></body></html>",
        encoding="utf-8",
    )
    expected = ("company/index.html",)
    assert net_margin_surfaces_missing_disclosure(fake_site, expected=expected) == [], (
        "precondition: a present compliant expected surface must not be flagged"
    )

    # MUTATION: emptied deploy — the net-margin figure is gone, the file is blank.
    good.write_text("", encoding="utf-8")
    violations = net_margin_surfaces_missing_disclosure(fake_site, expected=expected)
    assert any("company/index.html" in p.as_posix() and "fail-silent" in why
               for p, why in violations), (
        "R15 fail-silent: an emptied expected net-margin surface slipped the control"
    )

    # MUTATION: removed entirely — missing file is also a failed check.
    good.unlink()
    violations = net_margin_surfaces_missing_disclosure(fake_site, expected=expected)
    assert any("company/index.html" in p.as_posix() for p, _ in violations), (
        "R15 fail-silent: a missing expected net-margin surface slipped the control"
    )


def test_control_fires_on_expected_surface_that_kept_content_but_lost_its_figure(tmp_path):
    """R15 independent-coverage (2026-07-28 HARDEN rest-with-proof draw): isolate
    the no-figure branch of the expected-surface fail-silent guard.

    The two sub-checks in the expected loop — the empty-guard (``not text.strip()``)
    and the no-figure-guard (``not NET_MARGIN_KEY.search(text)``) — were only ever
    exercised JOINTLY by test_control_does_not_fail_open_on_missing_expected_surface,
    which empties the file. An empty file trips BOTH guards, and that test only
    asserts ``"fail-silent" in why`` (a string BOTH messages carry), so neutering
    EITHER guard alone still leaves all prior tests green — neither half was
    independently mutation-detectable (same subset-coverage class as the A3
    links-not-prose fail-open, [[feedback_audit_sibling_half_for_hardened_class]]).

    The no-figure-guard has a domain the empty-guard cannot reach: a PRESENT,
    non-empty expected surface whose net-margin figure was silently dropped (a
    redesign that keeps the page but removes the headline figure — exactly what the
    root index.html did). That is a real fail-silent deploy and must be a VIOLATION.
    This test feeds that exact input; it reds precisely when the no-figure-guard is
    neutered and nothing else. No source guard is added — the control is unchanged;
    this only makes the EXISTING guard fireable (not Nth-guard accretion)."""
    fake_site = tmp_path / "site"
    (fake_site / "company").mkdir(parents=True)
    good = fake_site / "company" / "index.html"
    # Present, non-empty, but the net-margin figure is gone (a real page redesign
    # could do this while keeping plenty of other content, so the empty-guard does
    # NOT fire — only the no-figure-guard can catch it).
    good.write_text(
        "<html><body><h1>The Company</h1><p>Lots of prose, KPIs, charts — but the "
        "headline net-margin figure was removed in a redesign.</p></body></html>",
        encoding="utf-8",
    )
    assert good.read_text(encoding="utf-8").strip(), "precondition: surface is non-empty"
    expected = ("company/index.html",)
    violations = net_margin_surfaces_missing_disclosure(fake_site, expected=expected)
    assert any("company/index.html" in p.as_posix() and "fail-silent" in why
               and "no longer renders" in why for p, why in violations), (
        "R15 fail-silent: a present-but-figure-gone expected surface slipped the "
        "no-figure-guard — the guard was not independently mutation-detectable"
    )


def test_expected_surfaces_track_the_discovery_registry():
    """The fail-silent registry (EXPECTED_NET_MARGIN_SURFACES) and the discovery
    must_include set are the SAME real live surfaces; keep them in lockstep so a
    surface can never be dropped from one without the other noticing."""
    discovered = {p.relative_to(SITE).as_posix() for p in _discovered_live_surfaces(SITE)}
    for rel in EXPECTED_NET_MARGIN_SURFACES:
        assert (SITE / rel).is_file(), f"expected net-margin surface absent from live site: {rel}"
        assert rel in discovered, f"expected surface not discovered as a net-margin surface: {rel}"


def test_no_live_net_margin_surface_escapes_expected_registry():
    """R15 fail-silent, CLASS closure (2026-07-28 HARDEN red-team): the OTHER
    direction of the lockstep. The hand-maintained EXPECTED registry stays hand-
    maintained (never derived from discovery -- that would be a tautology, R15
    pattern 1), but EVERY live surface that renders a net-margin figure MUST appear
    in it. Without this, a newly-added live net-margin door (this is exactly how
    now/ and proof/ slipped out) escapes the fail-silent guard: discovery checks
    its disclosure while present, but an emptied deploy renders no token, drops out
    of discovery, and passes green. This test forbids the registry from ever going
    stale again -- discovered subset of EXPECTED, enforced, not conventional."""
    discovered = {p.relative_to(SITE).as_posix() for p in _discovered_live_surfaces(SITE)}
    escaped = discovered - set(EXPECTED_NET_MARGIN_SURFACES)
    assert not escaped, (
        "fail-silent hole: live net-margin surface(s) render a net_margin figure but "
        "are NOT in the EXPECTED_NET_MARGIN_SURFACES fail-silent registry, so an "
        f"emptied deploy of them would pass green: {sorted(escaped)}. Add them to "
        "EXPECTED_NET_MARGIN_SURFACES (or, if a deliberate design change removed the "
        "figure, drop the surface and note why -- as the root index.html note shows)."
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
