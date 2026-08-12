"""The wall exhibit's side-declaration control (atom SITE2).

WHAT THIS PAGE IS NOW
---------------------
`DIRECTOR_RULING_THE_PORTAL_IS_A_WALL_EXHIBIT_2026-08-12` Part 2 ruled that this page
stops calling itself a customer portal and becomes a deliberate side-by-side comparison
of the two sides of the epistemic wall for one household: what the account holder can
see, what the company knows, and what only the simulation knows.

THE CONTROL, AND WHY IT IS STRUCTURAL AND NOT PROSE
---------------------------------------------------
The ruling's non-negotiable:

    "The side-declaration must be structural, not prose. A control that cannot fail is
     not a control. If a new panel can be added to this page without declaring which
     side of the wall it sits on, nothing has been built -- only written down."

The page already had honesty labelling (the DD note, the carbon placeholder, the
SIM-internal settlement-clock notes). All of it is prose: a new panel bypasses it just by
not mentioning it. So the mechanism is:

  1. `layoutPanels()` in the page is the SOLE writer of `.wall-panel` markup. Tab
     renderers return LISTS of `panel(side, title, body)` objects; `panel()` throws on a
     missing or unknown side, and `layoutPanels()` throws again on anything reaching it
     that is neither a declared panel nor explicitly-marked chrome.
  2. This module asserts on the RENDERED markup (R11, via `_wall_harness.mjs` driving the
     page's own code against real per-customer JSON) that NO content block sits outside a
     declared panel -- which is what catches a panel bolted on AROUND the helper rather
     than through it, the failure mode the ruling names.

Half 1 alone would be a control that a lazy edit walks past. Half 2 alone would be a
control with no enforcement point. Both are needed and both are mutation-proven below.

WHAT IT REFUSES (the named instances from the atom's exit criteria)
------------------------------------------------------------------
company-only  lifetime revenue, lifetime net, cost-to-serve, churn probability, CLV,
              pricing action, forecast profit -- may never render in the customer-eye view
sim-only      satisfaction score, causal reaction chain, wholesale trading margin --
              may never render under a company-attributed panel either

ANTI-PIN (R15's other half)
---------------------------
Nothing here pins a figure, a count or a stamp. Every assertion is a relationship between
a rendered block and the side it declared, so regenerating the run cannot make it cry
wolf -- only genuinely mixing the two sides of the wall can.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
HARNESS = HERE / "_wall_harness.mjs"
CUSTOMER_DATA = HERE.parent / "data" / "customers"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")

SIDES = ("customer", "company", "sim")

# Blocks that CARRY CONTENT. Nav chrome (tab-nav, fuel-select-row, year-btns) carries
# none of these classes, which is why chrome needs no side and content cannot avoid one.
CONTENT_CLASSES = {"card", "kpi-grid", "accounts-grid", "chart-wrap", "bill-sum", "timeline-list"}

# Elements the page fills in AFTER layout. Each must land inside a declared panel, or the
# guard above would be trivially bypassable by injecting content into a bare placeholder.
INJECTION_POINTS = {
    "bills-section": "customer",
    "usage-section": "customer",
    "cashflow-kpis": "customer",
    "cashflow-kpis-company": "company",
    "forecast-cashflow-body": "company",
}

# The named instances the atom's exit criterion (3) requires be tested specifically,
# keyed to the markup the page actually renders for each label (not to prose, which
# legitimately discusses these figures in the exhibit's explanatory header).
COMPANY_ONLY_FIGURES = {
    "lifetime revenue": (r'class="rl">Lifetime Revenue<', r'>Combined Revenue<'),
    "lifetime net": (r'class="rl">Lifetime Net Margin<', r'class="kpi-label">Lifetime net<',
                     r'>Combined Net Margin<'),
    "cost-to-serve": (r'class="rl">Cost to Serve<', r'class="kpi-label">Cost to serve<',
                      r'>Cost to Serve \(lifetime\)<'),
    "churn probability": (r'class="kpi-label">Churn Probability<', r'class="kpi-label">Churn risk<'),
    "customer lifetime value": (r'class="rl">Customer Lifetime Value<', r'>Combined CLV<'),
    "pricing action": (r'class="kpi-label">Pricing Action',),
    "forecast profit": (r'class="rl">Forecast Annual Profit<', r'>Projected Net Margin<',
                        r'>Net Cash Contribution'),
}
SIM_ONLY_FIGURES = {
    "satisfaction score": (r'class="kpi-label">Satisfaction<',),
    "causal reaction chain": (r'Reaction Chain &mdash; Bill Shock to Outcome',
                              r'class="timeline-effect"'),
    "wholesale trading margin": (r"commodity trading margin",),
}


# ---------------------------------------------------------------------------
# The scanner -- the enforcement point
# ---------------------------------------------------------------------------
class WallScan(HTMLParser):
    """Walks rendered markup and records, for every element, the wall side it inherits.

    Fail-closed by construction: an element inherits a side only from an ancestor that
    actually carries `data-wall-side` with a value in SIDES. Anything else inherits None,
    which is what `undeclared` collects.
    """

    VOID = {"br", "hr", "img", "input", "meta", "link", "source", "col"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.stack: list[tuple[str, str | None]] = []
        self.undeclared: list[tuple[str, str]] = []   # (tag, class) content blocks with no side
        self.bad_side: list[str] = []                 # data-wall-side values outside SIDES
        self.id_side: dict[str, str | None] = {}
        self.panels: list[dict] = []                  # {side, html}
        self._open_panels: list[tuple[int, str, list[str]]] = []
        self.saw_panel = False

    def _side(self) -> str | None:
        for _, side in reversed(self.stack):
            if side:
                return side
        return None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        declared = a.get("data-wall-side")
        if declared is not None:
            self.saw_panel = True
            if declared not in SIDES:
                self.bad_side.append(declared)
                declared = None
        inherited = declared or self._side()
        classes = (a.get("class") or "").split()
        if a.get("id"):
            self.id_side[a["id"]] = inherited
        if CONTENT_CLASSES.intersection(classes) and inherited is None:
            self.undeclared.append((tag, a.get("class") or ""))
        if tag not in self.VOID:
            self.stack.append((tag, declared))
            if declared:
                self._open_panels.append((len(self.stack), declared, []))
        self._collect(self.get_starttag_text() or "")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID and self.stack:
            self.handle_endtag(tag)

    def _collect(self, text: str) -> None:
        for _, _, buf in self._open_panels:
            buf.append(text)

    def handle_data(self, data):
        self._collect(data)

    def handle_entityref(self, name):
        self._collect(f"&{name};")

    def handle_charref(self, name):
        self._collect(f"&#{name};")

    def handle_endtag(self, tag):
        self._collect(f"</{tag}>")
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                while self._open_panels and self._open_panels[-1][0] > i + 1:
                    self._open_panels.pop()
                if self._open_panels and self._open_panels[-1][0] == i + 1:
                    depth, side, buf = self._open_panels.pop()
                    self.panels.append({"side": side, "html": "".join(buf)})
                del self.stack[i:]
                return


def scan(html: str) -> WallScan:
    s = WallScan()
    s.feed(html)
    s.close()
    return s


def figure_violations(html: str, figures: dict[str, tuple[str, ...]]) -> list[str]:
    """Named figures that appear in `html`. Shared by the real checks AND the mutation
    proofs below, so a mutation that fools the checker fails a named test."""
    return [name for name, pats in figures.items()
            if any(re.search(p, html) for p in pats)]


# ---------------------------------------------------------------------------
# Fixtures -- the page's own code, driven against real per-customer JSON (R11)
# ---------------------------------------------------------------------------
def _dual_fuel_pair() -> tuple[Path, Path]:
    elec = CUSTOMER_DATA / "C1.json"
    gas = CUSTOMER_DATA / "C1g.json"
    assert elec.is_file() and gas.is_file(), (
        "no dual-fuel household on disk -- the exhibit cannot be rendered and every "
        "assertion below would be vacuous"
    )
    return elec, gas


@pytest.fixture(scope="module")
def rendered() -> dict:
    elec, gas = _dual_fuel_pair()
    proc = subprocess.run(
        [NODE, str(HARNESS), str(INDEX), str(elec), str(gas)],
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, f"wall harness failed: {proc.stderr}"
    out = json.loads(proc.stdout)
    assert out["views"]["both"], "harness rendered no tabs -- guard would be vacuous"
    return out


@pytest.fixture(scope="module")
def op_state_html() -> str:
    """The server-rendered top-of-page region, extracted from the file itself."""
    html = INDEX.read_text(encoding="utf-8")
    start = html.index('<div id="op-state"')
    end = html.index("<script>", start)
    frag = html[start:end]
    assert "wall-panel" in frag, "op-state region declares no panels at all"
    return frag


# ===========================================================================
# (1) Every panel declares a side, structurally
# ===========================================================================
def test_no_content_block_renders_outside_a_declared_panel(rendered):
    """The guard. A new panel added without declaring a side lands here."""
    offenders = {}
    for view, tabs in rendered["views"].items():
        for tab, html in tabs.items():
            s = scan(html)
            if s.undeclared or s.bad_side:
                offenders[f"{view}/{tab}"] = {"undeclared": s.undeclared, "bad_side": s.bad_side}
    assert not offenders, (
        "these content blocks render outside any declared wall side (add them via "
        f"panel(side, title, body)): {offenders}"
    )


def test_the_op_state_region_declares_a_side_for_every_block(op_state_html):
    s = scan(op_state_html)
    assert s.saw_panel, "op-state declares no wall panels"
    assert not s.undeclared, f"undeclared blocks in the op-state region: {s.undeclared}"
    assert not s.bad_side, f"unknown wall sides in the op-state region: {s.bad_side}"


def test_every_injection_point_sits_inside_a_declared_panel(rendered):
    """A placeholder outside a panel would let content in without declaring a side."""
    seen: dict[str, str | None] = {}
    for tabs in rendered["views"].values():
        for html in tabs.values():
            for eid, side in scan(html).id_side.items():
                if eid in INJECTION_POINTS and side is not None:
                    seen[eid] = side
    missing = sorted(set(INJECTION_POINTS) - set(seen))
    assert not missing, f"these placeholders never rendered inside a declared panel: {missing}"
    wrong = {k: (seen[k], v) for k, v in INJECTION_POINTS.items() if seen.get(k) != v}
    assert not wrong, f"placeholders landed on the wrong side of the wall (got, want): {wrong}"


def test_injected_content_is_non_empty(rendered):
    """FAIL-OPEN floor: the attribution checks below are only meaningful if the page
    actually put something in these placeholders."""
    empty = [k for k, v in rendered["injected"].items() if not v]
    assert not empty, f"placeholders rendered empty -- attribution checks are vacuous: {empty}"


# ===========================================================================
# (2) The customer-eye view is its own coherent subset
# ===========================================================================
def test_the_customer_view_renders_only_customer_panels(rendered):
    for tab, html in rendered["views"]["customer"].items():
        sides = {p["side"] for p in scan(html).panels}
        assert sides <= {"customer"}, f"{tab}: customer-eye view rendered {sides}"


def test_the_customer_view_is_a_real_view_not_an_empty_one(rendered):
    """It must be COHERENT: a real account holder's bills, usage, payments and meter
    details all present, as their own thing rather than assembled by reading labels."""
    joined = " ".join(rendered["views"]["customer"].values())
    assert scan(joined).panels, "customer-eye view rendered no panels at all"
    for staple in ("Billing History", "Usage", "Statement", "MPAN", "Tariff", "Your balance"):
        assert staple in joined, f"customer-eye view is missing {staple!r}"


def test_the_behind_the_wall_view_excludes_the_customer_side(rendered):
    for tab, html in rendered["views"]["behind"].items():
        sides = {p["side"] for p in scan(html).panels}
        assert "customer" not in sides, f"{tab}: behind-the-wall view leaked a customer panel"


def test_both_sides_view_shows_both_columns(rendered):
    joined = " ".join(rendered["views"]["both"].values())
    assert "The customer&#x27;s side" in joined or "The customer's side" in joined, joined[:400]
    assert "Behind the wall" in joined, joined[:400]


# ===========================================================================
# (3) No figure crosses the wall
# ===========================================================================
def _side_html(rendered, view: str, side: str) -> str:
    out = []
    for html in rendered["views"][view].values():
        out += [p["html"] for p in scan(html).panels if p["side"] == side]
    return "".join(out)


def test_no_company_only_figure_renders_in_the_customer_eye_view(rendered):
    html = _side_html(rendered, "customer", "customer") + "".join(
        v for k, v in rendered["injected"].items() if INJECTION_POINTS[k] == "customer"
    )
    leaked = figure_violations(html, COMPANY_ONLY_FIGURES)
    assert not leaked, f"company-only figures rendered in the customer-eye view: {leaked}"


def test_no_sim_only_figure_renders_in_the_customer_eye_view(rendered):
    html = _side_html(rendered, "customer", "customer")
    leaked = figure_violations(html, SIM_ONLY_FIGURES)
    assert not leaked, f"SIM-only figures rendered in the customer-eye view: {leaked}"


def test_no_sim_only_figure_renders_under_a_company_panel(rendered):
    html = _side_html(rendered, "both", "company") + "".join(
        v for k, v in rendered["injected"].items() if INJECTION_POINTS[k] == "company"
    )
    leaked = figure_violations(html, SIM_ONLY_FIGURES)
    assert not leaked, (
        "SIM-only figures rendered under a company-attributed panel -- the company "
        f"cannot know these: {leaked}"
    )


def test_the_op_state_money_panels_split_on_the_wall(op_state_html):
    """The top-of-page money grid used to mix all three layers in ONE tile row."""
    sides = {eid: side for eid, side in scan(op_state_html).id_side.items()
             if eid.startswith("cust-")}
    assert sides.get("cust-money") == "customer", sides
    assert sides.get("cust-value") == "company", sides
    assert sides.get("cust-sim") == "sim", sides
    assert sides.get("cust-classify") == "company", sides


def test_the_named_figures_are_actually_present_somewhere(rendered):
    """ANTI-VACUITY: the refusals above prove nothing if the page stopped rendering
    these figures altogether. Each named instance must still be on the page, on the
    side it belongs to."""
    company_side = _side_html(rendered, "both", "company") + "".join(
        v for k, v in rendered["injected"].items() if INJECTION_POINTS[k] == "company"
    )
    sim_side = _side_html(rendered, "both", "sim")
    found_company = set(figure_violations(company_side, COMPANY_ONLY_FIGURES))
    missing = sorted(set(COMPANY_ONLY_FIGURES) - found_company)
    assert not missing, f"company-only figures vanished from the page entirely: {missing}"
    found_sim = set(figure_violations(sim_side, SIM_ONLY_FIGURES))
    assert "causal reaction chain" in found_sim, "the reaction chain vanished from the SIM side"
    assert "wholesale trading margin" in found_sim, "the trading margin vanished from the SIM side"


# ===========================================================================
# (4)/(5) The page stops claiming to be a customer portal, and says what it is
# ===========================================================================
def test_the_page_no_longer_calls_itself_a_customer_portal():
    html = INDEX.read_text(encoding="utf-8")
    assert "<title>Poesys - Two Sides of the Wall</title>" in html
    assert "Customer Portal" not in html, "the 'Customer Portal' claim is still on the page"
    assert "Log in with your Poesys account number" not in html, "the login claim survives"
    assert ">Sign in<" not in html, "the sign-in button still frames this as an account login"


def test_the_relationship_to_the_real_portal_is_stated_on_the_page():
    html = INDEX.read_text(encoding="utf-8")
    assert html.count("company/portal/") >= 2, (
        "the real customer portal at company/portal/ must be named on the page, not "
        "left to be inferred"
    )
    assert "not a customer portal" in html.lower()


def test_the_exhibit_states_why_the_sides_differ():
    html = INDEX.read_text(encoding="utf-8")
    for claim in ("Two sides of the wall", "Why the sides differ"):
        assert claim in html, f"exhibit framing missing: {claim!r}"


# ===========================================================================
# (6) The honesty notes that were already on the page survive
# ===========================================================================
# Captured by diffing the pre-change page (git show HEAD~:site/customers/index.html at the
# time of the SITE2 build). The ruling: "Do not weaken or remove the honesty notes already
# on the page; absorb them."
PRE_EXISTING_HONESTY_NOTES = (
    "Settlement clock (SIM-internal wholesale-cost accounting)",
    "Gross/Net here are the SIM's internal commodity trading margin per year",
    "DESIGNED, NOT INSTRUMENTED",
    "this account is on the current <strong>Variable DD</strong> engine",
    "That staggering is instrumented (DD1).",
    "The carbon ledger (atom E5) is designed but not instrumented",
    "We will not fabricate one.",
    "no effect shown means the sim has no wired mechanism for that event type yet",
    "Lifetime Revenue shown on the Accounts tab is a different, ex-VAT commodity-only accounting figure",
    "synthetic simulation, not a real bill.",
)


def test_every_pre_existing_honesty_note_survives_the_redesign():
    html = INDEX.read_text(encoding="utf-8")
    lost = [n for n in PRE_EXISTING_HONESTY_NOTES if n not in html]
    assert not lost, f"the redesign dropped honesty notes that were already on the page: {lost}"


# ===========================================================================
# (7) Part 1's bill-render path is untouched by Part 2's redesign
# ===========================================================================
def test_the_bill_render_path_is_intact():
    """The ruling's own 'Part 1 lands intact through this work'. D36 owns these
    functions; SITE2 must not have moved, renamed or restructured them."""
    html = INDEX.read_text(encoding="utf-8")
    for fn in ("function billEquationHtml(i){", "function billUsageLinesHtml(i){",
               "function billMeterDetailsHtml(i){", "function downloadBillPdf(i){",
               "function billExpandHtml(i,allInvoices){"):
        assert fn in html, f"the bill render path lost {fn!r}"


# ===========================================================================
# R15 -- the control must fire on its own named defects, both directions
# ===========================================================================
def test_mutation_a_panel_that_declares_no_side_is_refused_at_source(rendered):
    """Direction 1a: the page's own helper refuses an undeclared panel."""
    probes = rendered["probes"]
    for probe in ("panel_with_no_side", "panel_with_unknown_side",
                  "raw_block_reaches_layout", "undeclared_object_reaches_layout"):
        assert probes[probe], f"MUTATION SURVIVED: {probe} did not raise"
        assert "wall" in probes[probe].lower() or "declare" in probes[probe].lower(), probes[probe]
    assert probes["declared_panel_is_accepted"] is None, (
        "the control is over-broad: it rejects a correctly-declared panel too"
    )


def test_mutation_removing_a_panels_side_attribute_kills_the_guard(rendered):
    """Direction 1b: strip `data-wall-side` off a rendered panel -- the STRUCTURAL guard
    (not the helper) must flag the content it was carrying."""
    html = rendered["views"]["both"]["risk"]
    assert 'data-wall-side="company"' in html, "fixture precondition: the risk tab has a company panel"
    mutated = html.replace('data-wall-side="company"', "", 1)
    assert scan(mutated).undeclared, (
        "MUTATION SURVIVED: a panel stripped of its side declaration still passed the guard"
    )
    assert not scan(html).undeclared, "the guard flags the unmutated page -- it is over-broad"


def test_mutation_an_undeclared_panel_in_the_file_kills_the_guard(tmp_path):
    """Direction 1c: the same mutation applied to the FILE, not to a rendered string --
    a new card appended to the op-state region without declaring a side."""
    src = INDEX.read_text(encoding="utf-8")
    marker = '<div style="text-align:center;margin:6px 0 8px"><a href="./?acc=C1"'
    assert marker in src, "fixture precondition: the op-state drill-down link is where expected"
    mutated_file = tmp_path / "index.html"
    mutated_file.write_text(
        src.replace(marker, '<div class="card">A new panel nobody declared</div>' + marker, 1),
        encoding="utf-8",
    )
    text = mutated_file.read_text(encoding="utf-8")
    frag = text[text.index('<div id="op-state"'):text.index("<script>", text.index('<div id="op-state"'))]
    assert scan(frag).undeclared, (
        "MUTATION SURVIVED: a bare card added to the page declared no side and the guard passed"
    )


def test_mutation_a_company_only_figure_moved_into_the_customer_view_kills_a_named_test(rendered):
    """Direction 2: the exact defect the ruling is about -- a company-only figure
    presented as something the customer sees. This feeds the mutated markup to the SAME
    checker `test_no_company_only_figure_renders_in_the_customer_eye_view` uses."""
    clean = _side_html(rendered, "customer", "customer")
    assert not figure_violations(clean, COMPANY_ONLY_FIGURES), (
        "precondition: the real customer view is clean"
    )
    mutated = clean.replace(
        "<div class=\"card\">",
        "<div class=\"card\"><div class=\"row\"><span class=\"rl\">Churn Probability</span>"
        "<span>41%</span></div>",
        1,
    )
    # the churn label the page actually uses for a KPI tile
    mutated += '<div class="kpi"><div class="kpi-label">Churn Probability</div></div>'
    leaked = figure_violations(mutated, COMPANY_ONLY_FIGURES)
    assert "churn probability" in leaked, (
        "MUTATION SURVIVED: a churn probability moved into the customer-eye view was not caught"
    )


def test_mutation_a_sim_only_figure_moved_under_a_company_panel_is_caught(rendered):
    clean = _side_html(rendered, "both", "company")
    assert not figure_violations(clean, SIM_ONLY_FIGURES), "precondition: company panels are clean"
    mutated = clean + '<div class="kpi"><div class="kpi-label">Satisfaction</div></div>'
    assert "satisfaction score" in figure_violations(mutated, SIM_ONLY_FIGURES), (
        "MUTATION SURVIVED: a satisfaction score under a company panel was not caught"
    )


def test_the_scanner_itself_fails_closed_on_empty_input():
    """FAIL-OPEN proof: an empty document must not read as 'every panel declared'."""
    s = scan("")
    assert not s.saw_panel, "an empty document claimed to contain declared panels"
    # and the door test that uses saw_panel must therefore fail on it
    with pytest.raises(AssertionError):
        assert s.saw_panel, "op-state declares no wall panels"
