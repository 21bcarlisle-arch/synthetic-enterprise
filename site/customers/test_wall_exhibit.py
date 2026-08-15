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
    # Anchored on the label PREFIX, not the closing '<'. This atom's own 2026-08-12
    # caption fix renamed the tile to "Lifetime net (commodity)" and added "Net after
    # cost to serve"; a '<'-anchored pattern went silently blind to both, which is the
    # narrowed-parser class. test_the_named_figures_are_visible_to_the_checker below
    # now fails if any of these ever stops matching the page.
    "lifetime net": (r'class="rl">Lifetime Net Margin<', r'class="kpi-label">Lifetime net',
                     r'class="kpi-label">Net after cost to serve', r'>Combined Net Margin<'),
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


class _TopLevelSplit(HTMLParser):
    """Splits a fragment into its TOP-LEVEL element children, keeping each child's raw
    html and its declared wall side. Used to hand the #op-state region to the node
    harness as real DOM children, so the page's own view filter can act on them."""

    VOID = {"br", "hr", "img", "input", "meta", "link", "source", "col"}

    def __init__(self, raw: str) -> None:
        super().__init__(convert_charrefs=False)
        self.raw = raw
        self.lines = raw.splitlines(keepends=True)
        self.depth = 0
        self.start: int | None = None
        self.side: str | None = None
        self.children: list[dict] = []

    def _off(self) -> int:
        line, col = self.getpos()
        return sum(len(x) for x in self.lines[: line - 1]) + col

    def handle_starttag(self, tag, attrs):
        if tag in self.VOID:
            return
        if self.depth == 0:
            self.start = self._off()
            self.side = dict(attrs).get("data-wall-side")
        self.depth += 1

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        self.depth -= 1
        if self.depth == 0 and self.start is not None:
            end = self.raw.index(">", self._off()) + 1
            self.children.append({"side": self.side, "html": self.raw[self.start:end]})
            self.start = None


RENDER_HARNESS = HERE / "_render_harness.mjs"
COMPANY_DATA = HERE.parent / "data" / "company.json"


def _op_state_render(index: Path = INDEX, legs: tuple[Path, ...] | None = None) -> dict[str, str]:
    """Run the op-state script over company.json plus a chosen set of household fuel legs.

    `legs` defaults to EVERY leg the household has, because that is what the live page's
    own boot path fetches. Passing a SUBSET is how the leg-scoped fallback gets driven --
    see the dual-fuel section below; that path is the half of the scope control that can
    actually fail, so it needs to be reachable from a test.
    """
    if legs is None:
        legs = _dual_fuel_pair()
    proc = subprocess.run(
        [NODE, str(RENDER_HARNESS), str(index), *[str(p) for p in legs]],
        input=COMPANY_DATA.read_text(encoding="utf-8"),
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, f"op-state render harness failed: {proc.stderr}"
    out = json.loads(proc.stdout)
    return {k: v["innerHTML"] for k, v in out.items() if v and v["innerHTML"]}


def _op_state_injected(index: Path = INDEX) -> dict[str, str]:
    """The op-state region's FIGURES, as its own script renders them.

    The exhibit panels ship as empty placeholders (`<div id="cust-value">`); the first
    inline script fills them from company.json at runtime. A union subject built from the
    static shell alone would contain no `Lifetime net`, `Cost to serve`, `Churn risk` or
    `Satisfaction` label at all -- i.e. it would be blind to the exact figures cold-eyes
    found on screen in the customer view. So the shell is filled here first, from the same
    published data the live page reads -- INCLUDING the household's fuel legs, which the
    live boot path fetches after company.json. Filling it from company.json alone would
    build the union subject out of the leg-scoped FALLBACK render, i.e. out of markup no
    live reader is served.
    """
    filled = _op_state_render(index)
    assert filled, "the op-state script rendered nothing -- the union subject would be a shell"
    return filled


def _op_state_children(frag: str, index: Path = INDEX) -> list[dict]:
    # Drop the wrapper <div id="op-state" ...> so we split its CHILDREN, not itself.
    inner = frag[frag.index(">", frag.index('<div id="op-state"')) + 1:]
    inner = inner[: inner.rindex("</div>")]
    for el_id, html in _op_state_injected(index).items():
        inner = re.sub(rf'(id="{re.escape(el_id)}"[^>]*>)', lambda m: m.group(1) + html, inner, count=1)
    p = _TopLevelSplit(inner)
    p.feed(inner)
    p.close()
    assert p.children, "op-state region split into no children -- the view test would be vacuous"
    return p.children


def _run(index: Path, elec: Path, gas: Path, tmp: Path) -> subprocess.CompletedProcess:
    """Drive the page's own code, returning the raw process so a caller can assert on a
    REFUSAL as well as on output. Shared by the real fixture and every mutation below, so
    a mutation cannot pass by taking a different route to the markup than the real check."""
    # The op-state region is built from the SAME file the harness drives. Building it from
    # the real INDEX while driving a mutant would make every op-state mutation invisible --
    # the wrong-subject class this module already paid for once (section 9).
    spec = tmp / "children.json"
    spec.write_text(json.dumps(_op_state_children(_op_state_fragment(index), index)), encoding="utf-8")
    return subprocess.run(
        [NODE, str(HARNESS), str(index), str(elec), str(gas), str(spec)],
        capture_output=True, text=True, timeout=60,
    )


def _drive(index: Path, tmp: Path) -> dict:
    elec, gas = _dual_fuel_pair()
    proc = _run(index, elec, gas, tmp)
    assert proc.returncode == 0, f"harness failed on {index.name}: {proc.stderr}"
    return json.loads(proc.stdout)


@pytest.fixture(scope="module")
def rendered(tmp_path_factory) -> dict:
    elec, gas = _dual_fuel_pair()
    spec = tmp_path_factory.mktemp("opstate") / "children.json"
    spec.write_text(json.dumps(_op_state_children(_op_state_fragment())), encoding="utf-8")
    proc = subprocess.run(
        [NODE, str(HARNESS), str(INDEX), str(elec), str(gas), str(spec)],
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, f"wall harness failed: {proc.stderr}"
    out = json.loads(proc.stdout)
    assert out["views"]["both"], "harness rendered no tabs -- guard would be vacuous"
    assert out["opState"]["both"], "harness rendered no op-state -- union guard would be vacuous"
    return out


def _op_state_fragment(index: Path = INDEX) -> str:
    html = index.read_text(encoding="utf-8")
    start = html.index('<div id="op-state"')
    end = html.index("<script>", start)
    frag = html[start:end]
    assert "wall-panel" in frag, "op-state region declares no panels at all"
    return frag


@pytest.fixture(scope="module")
def op_state_html() -> str:
    """The server-rendered top-of-page region, extracted from the file itself."""
    return _op_state_fragment()


def whole_document(rendered: dict, view: str) -> str:
    """THE SUBJECT THAT WAS MISSING.

    Every view-filtering assertion in this module used to run against `rendered["views"]`
    alone -- the drill-down. The static exhibit above it was a separate fixture that only
    ever checked side DECLARATION. So "the customer view shows only customer panels" was
    green while the live page rendered churn risk, cost-to-serve, lifetime net and a SIM
    satisfaction score in that very view (cold-eyes, 2026-08-12). This function returns
    what a reader of the page in `view` actually has in front of them: the surviving
    op-state region PLUS every drill-down tab. Any check whose subject is this cannot be
    passed by a region the view switch does not reach.
    """
    return rendered["opState"][view] + "".join(rendered["views"][view].values())


def sides_in(html: str) -> set[str]:
    """The distinct wall sides a rendered fragment actually declares."""
    return {p["side"] for p in scan(html).panels}


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


# ===========================================================================
# (9) THE VIEW SELECTOR GOVERNS THE WHOLE PAGE
#
# Added 2026-08-12 after the Expert-Hour cold-eyes walk. Everything above this
# point had one of two subjects -- the drill-down panels, or the op-state region's
# side DECLARATIONS -- and neither is the document a reader sees. The live page
# was rendering `Lifetime net`, `Cost to serve`, `Churn risk` and `Satisfaction`
# inside "The customer's side" while all 24 tests were green. These tests take
# the union as their subject, so no region can sit outside the control again.
# ===========================================================================
def test_the_customer_view_of_the_whole_page_contains_no_company_or_sim_panel(rendered):
    doc = whole_document(rendered, "customer")
    assert scan(doc).saw_panel, "no panels at all in the customer view -- check would be vacuous"
    leaked = sorted(x for x in sides_in(doc) if x != "customer")
    assert not leaked, (
        f"the customer view of the WHOLE page renders {leaked} panels. The page's own note "
        f"in this view says 'if one appears, the page is broken'."
    )


def test_the_behind_view_of_the_whole_page_contains_no_customer_panel(rendered):
    doc = whole_document(rendered, "behind")
    assert scan(doc).saw_panel, "no panels at all in the behind view -- check would be vacuous"
    assert "customer" not in sides_in(doc), (
        "the behind-the-wall view of the WHOLE page renders customer-observable panels, "
        "under a note claiming everything on this side is invisible to the account holder"
    )


def test_no_named_company_only_figure_survives_anywhere_in_the_customer_view(rendered):
    leaked = figure_violations(whole_document(rendered, "customer"), COMPANY_ONLY_FIGURES)
    assert not leaked, (
        f"company-only figures {leaked} render in the customer-eye view of the whole page"
    )


def test_no_named_sim_only_figure_survives_anywhere_in_the_customer_view(rendered):
    leaked = figure_violations(whole_document(rendered, "customer"), SIM_ONLY_FIGURES)
    assert not leaked, (
        f"SIM-only figures {leaked} render in the customer-eye view of the whole page"
    )


def test_the_op_state_region_is_actually_filtered_not_merely_reordered(rendered):
    """ANTI-VACUITY, both directions. The union tests above would also pass if the
    harness simply returned an empty op-state for the filtered views, or if every view
    returned the same html (which is exactly the defect)."""
    both, cust, behind = (rendered["opState"][v] for v in ("both", "customer", "behind"))
    assert cust and behind, "a filtered view rendered an EMPTY op-state -- that is not a view"
    assert cust != both and behind != both, (
        "the op-state region is identical across views -- the view switch does not reach it"
    )
    # and the two filtered views must partition it, not overlap
    assert "customer" in sides_in(cust)
    assert sides_in(behind) and "customer" not in sides_in(behind)


def test_the_customer_view_still_carries_the_customers_own_exhibit_panels(rendered):
    """The cheapest way to pass the tests above is to delete the exhibit from the
    customer view entirely. It must still render the household's own money."""
    cust = rendered["opState"]["customer"]
    assert 'id="cust-money"' in cust and 'id="cust-who"' in cust, (
        "the customer view dropped the household's own account and money panels"
    )
    assert 'id="cust-value"' not in cust and 'id="cust-sim"' not in cust, (
        "the customer view kept the company-value or SIM panel placeholders"
    )


def test_mutation_a_view_switch_that_skips_the_op_state_region_kills_a_named_test(tmp_path):
    """R15, the defect this section exists for: restore the pre-fix setWallView (drill-down
    only) and the union guard must fail. Proven on the FILE, driven through the real harness."""
    src = INDEX.read_text(encoding="utf-8")
    # The mutation is "setWallView stops reaching the op-state region", so it is expressed as
    # the REMOVAL OF THAT CALL, not as a pin on the whole function body. The original pinned
    # the exact one-line body and went red the moment a second statement was added to the
    # function -- a fixture that rots on any unrelated edit ("a fixture's neutralise list rots
    # when the callee gains a check"). Anchored on the call, it survives that and still
    # reverts exactly the pre-fix behaviour: drill-down filtered, exhibit not.
    m = re.search(r"function setWallView\(v\)\{([^}]*)\}", src)
    assert m, "setWallView no longer has a flat body this mutation can operate on"
    body = m.group(1)
    assert "applyWallViewToOpState();" in body, (
        "setWallView no longer calls applyWallViewToOpState -- either the fix was reverted "
        f"(a real defect, not a fixture problem) or it was renamed. Body: {body!r}"
    )
    mutant = tmp_path / "index.html"
    mutant.write_text(
        src.replace(m.group(0), m.group(0).replace("applyWallViewToOpState();", "")),
        encoding="utf-8",
    )
    elec, gas = _dual_fuel_pair()
    spec = tmp_path / "children.json"
    spec.write_text(json.dumps(_op_state_children(_op_state_fragment())), encoding="utf-8")
    proc = subprocess.run(
        [NODE, str(HARNESS), str(mutant), str(elec), str(gas), str(spec)],
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, f"mutant harness failed: {proc.stderr}"
    out = json.loads(proc.stdout)
    leaked = figure_violations(whole_document(out, "customer"), COMPANY_ONLY_FIGURES)
    assert leaked, (
        "MUTATION SURVIVED: setWallView stopped filtering the exhibit and no company-only "
        "figure was reported in the customer view -- the union guard is not doing the work"
    )
    assert "customer" in sides_in(out["opState"]["behind"]), (
        "MUTATION SURVIVED: the unfiltered behind view showed no customer panels"
    )


def test_mutation_an_op_state_block_with_an_unknown_side_is_refused(rendered):
    """R15, fail-closed: a block declaring a side the wall does not know cannot be
    filtered, so the page must REFUSE it rather than render it in every view."""
    msg = rendered["opStateProbes"]["unknown_side_block"]
    assert msg and "unknown wall-side" in msg, (
        "an op-state block declaring side='marketing' was accepted -- it would then render "
        f"in the customer view unfiltered (got {msg!r})"
    )


def test_the_named_figures_are_visible_to_the_checker_in_the_op_state_exhibit(rendered):
    """ANTI-BLINDNESS. The union checks above are only worth anything if the checker can
    actually SEE the figures cold-eyes found on screen. This atom's own caption fix proved
    the risk: renaming a tile to "Lifetime net (commodity)" made a '<'-anchored pattern stop
    matching, and every leak test went quietly green. If a rename blinds the checker again,
    this fails first."""
    both = rendered["opState"]["both"]
    found_co = set(figure_violations(both, COMPANY_ONLY_FIGURES))
    found_sim = set(figure_violations(both, SIM_ONLY_FIGURES))
    for name in ("lifetime net", "cost-to-serve", "churn probability"):
        assert name in found_co, (
            f"the checker can no longer see {name!r} in the op-state exhibit -- either the "
            f"page stopped rendering it or its pattern was blinded by a rename"
        )
    assert "satisfaction score" in found_sim, (
        "the checker can no longer see the SIM satisfaction score in the op-state exhibit"
    )


def test_a_view_filtered_panel_is_still_fillable_when_its_data_lands():
    """The op-state script fills its placeholders from an async fetch. Once the view
    selector REMOVES a panel from the document, document.getElementById can no longer
    reach it, so a view switch racing that fetch would throw inside renderCustomerState
    and blank the whole exhibit. This pins the fallback path that prevents it.

    LIMIT, stated: this is a source-level wiring pin, not a rendered assertion -- the
    harness's document stub resolves every id, so it cannot reproduce a detached node.
    The rendered proof is the live-surface check recorded against this atom.
    """
    src = INDEX.read_text(encoding="utf-8")
    assert "window.opStateFind=function(id){" in src, (
        "the detached-block lookup is gone -- a filtered panel can no longer be filled"
    )
    assert "document.getElementById(id)||(window.opStateFind&&window.opStateFind(id))" in src, (
        "the op-state script's el() no longer falls back to the detached blocks"
    )
    # and the lookup must search the SAME cache the filter detaches into
    lookup = src[src.index("window.opStateFind=function(id){"):]
    assert "OP_STATE_BLOCKS" in lookup[:400], (
        "opStateFind does not search OP_STATE_BLOCKS -- it cannot find a detached panel"
    )


# ===========================================================================
# (10) The 2026-08-12 cold-eyes walk's remaining render findings
#
# Four findings from the same walk that produced section (9). Each is a defect in
# what this page RENDERS -- not in the sim or the company's beliefs -- so each is
# this atom's own scope, and each gets a control that can fail on its own defect.
# ===========================================================================

# The arrears cascade this household actually lived through. Cold-eyes found these
# rendering ONLY inside the SIM reaction chain -- a customer's own overdue notices
# and payment plan filed behind the wall, while the money panel above called the
# account clean. Every one of them is a letter the account holder received.
CUSTOMER_OBSERVABLE_ARREARS = (
    "Payment missed", "First overdue notice", "Second notice", "Arrears cleared",
)


def _timeline(rendered: dict, view: str) -> str:
    return rendered["views"][view]["timeline"]


def _arrears_events_on_disk() -> list[dict]:
    """ANTI-VACUITY SOURCE. Every assertion below is worthless if the household has no
    arrears events at all, so the checks read them from the JSON the page is driven with."""
    events: list[dict] = []
    for path in _dual_fuel_pair():
        data = json.loads(path.read_text(encoding="utf-8"))
        events += [e for e in data.get("reaction_chain", [])
                   if str(e.get("event_type", "")).startswith("arrears")]
    return events


def test_the_household_actually_has_an_arrears_history_to_side():
    """The anti-vacuity gate for this whole section. If the fixture household stops
    carrying arrears events, the siding checks below silently prove nothing -- so they
    fail HERE, loudly, rather than passing empty."""
    events = _arrears_events_on_disk()
    assert events, (
        "the fixture household carries no arrears events, so every arrears-siding "
        "assertion below would be vacuously true -- pick a household that has some"
    )
    kinds = {e["event_type"] for e in events}
    assert kinds & {"arrears_payment_missed", "arrears_first_notice", "arrears_dd_failed"}, (
        f"no customer-observable arrears event in the fixture (got {sorted(kinds)})"
    )


def test_a_customers_own_arrears_notices_render_on_the_customer_side(rendered):
    """coldwalk:site2_arrears_history_visible_only_behind_the_wall.

    An overdue notice and an offered payment plan were SENT TO THIS HOUSEHOLD. On an
    exhibit whose whole subject is the wall, filing them behind it is the exhibit
    making the exact error it exists to expose."""
    customer = _timeline(rendered, "customer")
    missing = [lbl for lbl in CUSTOMER_OBSERVABLE_ARREARS if lbl not in customer]
    assert not missing, (
        f"customer-observable arrears events missing from the customer's own view: {missing} "
        "-- the household cannot see its own overdue notices on a page that shows them"
    )


def test_the_customers_arrears_notices_are_not_filed_behind_the_wall(rendered):
    """The other half: they must be OUT of the behind-the-wall view, not merely also in
    the customer one. Sided means sided."""
    behind = _timeline(rendered, "behind")
    leaked = [lbl for lbl in CUSTOMER_OBSERVABLE_ARREARS if lbl in behind]
    assert not leaked, (
        f"customer-observable arrears events still render behind the wall: {leaked}"
    )


def test_the_reaction_chain_stays_sim_only_after_the_split(rendered):
    """ANTI-OVERCORRECTION. The split must not drag the causal chain -- the hidden
    churn-journey state and the sim's realized probabilities -- onto the customer side.
    Exit criterion (3) names the causal reaction chain as SIM-only."""
    assert "Reaction Chain" in _timeline(rendered, "behind"), (
        "the SIM reaction chain vanished from the behind-the-wall view -- the split "
        "removed it instead of re-siding the arrears half"
    )
    assert "Reaction Chain" not in _timeline(rendered, "customer"), (
        "the SIM reaction chain leaked into the customer's view"
    )


def test_no_raw_event_type_enum_reaches_the_page(rendered):
    """The walk read 'arrears_payment_missed' off the live surface: an unlabelled event
    type falls through chainLabel() and prints its own enum on a public page."""
    both = _timeline(rendered, "both")
    raw = sorted({m for m in re.findall(r"arrears_[a-z_]+|outcome_[a-z_]+|journey_state", both)})
    assert not raw, f"raw event-type enums rendered on the page: {raw}"


def test_mutation_arrears_events_filed_behind_the_wall_kill_a_named_test(tmp_path):
    """R15 for the siding. Re-file the arrears cascade on the SIM side in the FILE, drive
    the real harness, and the named check above must report it."""
    src = INDEX.read_text(encoding="utf-8")
    marker = 'arrears_first_notice:"customer",arrears_second_notice:"customer",'
    assert marker in src, "_CHAIN_SIDE no longer has the shape this mutation reverts"
    mutant = tmp_path / "index.html"
    mutant.write_text(
        src.replace(marker, 'arrears_first_notice:"sim",arrears_second_notice:"sim",'),
        encoding="utf-8",
    )
    out = _drive(mutant, tmp_path)
    behind = out["views"]["behind"]["timeline"]
    assert "First overdue notice" in behind, (
        "MUTATION SURVIVED: arrears re-sided to sim and the behind-the-wall view still "
        "did not carry them -- the siding is not driving the render"
    )
    assert "First overdue notice" not in out["views"]["customer"]["timeline"], (
        "MUTATION SURVIVED: the customer view still showed the notice"
    )


def test_mutation_an_unclassified_chain_event_is_refused_not_silently_placed(tmp_path):
    """R15 fail-closed, proven on real DATA rather than on the file. An event type nobody
    has sided cannot be placed, and placing it by default would be a silent claim about
    which side of the wall it belongs on -- the claim this page exists to make explicit."""
    elec, gas = _dual_fuel_pair()
    data = json.loads(gas.read_text(encoding="utf-8"))
    chain = data.get("reaction_chain") or []
    assert chain, "fixture has no reaction chain -- this proof would be vacuous"
    chain.append({**chain[0], "event_type": "arrears_third_notice_2029"})
    mutant_gas = tmp_path / "gas.json"
    mutant_gas.write_text(json.dumps(data), encoding="utf-8")
    proc = _run(INDEX, elec, mutant_gas, tmp_path)
    assert proc.returncode != 0, (
        "MUTATION SURVIVED: an event type with no declared wall side rendered anyway -- "
        f"the page placed it silently. stdout head: {proc.stdout[:300]!r}"
    )
    assert "declares no wall side" in proc.stderr, (
        f"refused, but not for the stated reason: {proc.stderr[-400:]!r}"
    )


# --- the retail tariff unit -------------------------------------------------
def test_the_retail_tariff_range_is_labelled_in_the_unit_it_is_actually_in(rendered):
    """coldwalk:site2_tariff_range_pounds_per_mwh_labelled_pence_per_mwh -- a 100x unit
    mislabel on a public surface.

    INDEPENDENCE (R15 anti-tautology): the check does not compare the label to itself. It
    compares the number the page renders in this column against the SAME quantity rendered
    by a DIFFERENT code path elsewhere on the page -- the timeline's "Tariff renewed at
    128.0 GBP/MWh" -- and requires them to be the same order of magnitude. A column in
    pence and a line in pounds cannot both be right."""
    accounts = rendered["views"]["behind"]["accounts"]
    cells = re.findall(r'<td style="color:var\(--muted\);font-size:11px">([^<]*)</td>', accounts)
    ranged = [c for c in cells if "–" in c]
    assert ranged, "no tariff-range cell rendered -- this check would be vacuous"
    assert not [c for c in ranged if "p/MWh" in c], (
        f"the retail tariff range is labelled in pence per MWh: {ranged[:3]} -- the fields "
        "behind it are tariff_min_gbp_per_mwh / tariff_max_gbp_per_mwh"
    )
    assert all("&pound;/MWh" in c for c in ranged), (
        f"tariff-range cells carry no unit at all: {ranged[:3]}"
    )

    renewals = re.findall(r"Tariff renewed at ([\d.]+) £/MWh", _timeline(rendered, "customer"))
    assert renewals, "no renewal line to cross-check the unit against"
    rendered_range = [float(n) for c in ranged
                      for n in re.findall(r"\d+", c.replace("&pound;", ""))]
    assert rendered_range, f"no numbers parsed out of {ranged[:3]}"
    lo, hi = min(rendered_range), max(rendered_range)
    ref = float(renewals[0])
    assert lo <= ref * 4 and hi >= ref / 4, (
        f"the tariff-range column ({lo}-{hi}) and the renewal line ({ref} GBP/MWh) render "
        "the same quantity two orders of magnitude apart -- one of them has the wrong unit"
    )


def test_mutation_relabelling_the_tariff_range_as_pence_kills_a_named_test(tmp_path):
    """R15 for the unit. Put the pence label back and the named check must fire."""
    src = INDEX.read_text(encoding="utf-8")
    marker = '+" &pound;/MWh"'
    assert marker in src, "the tariff-range unit no longer has the shape this mutation reverts"
    mutant = tmp_path / "index.html"
    mutant.write_text(src.replace(marker, '+" p/MWh"'), encoding="utf-8")
    out = _drive(mutant, tmp_path)
    cells = re.findall(r'<td style="color:var\(--muted\);font-size:11px">([^<]*)</td>',
                       out["views"]["behind"]["accounts"])
    assert [c for c in cells if "p/MWh" in c], (
        "MUTATION SURVIVED: the pence label was restored and the checker's own subject "
        "did not carry it -- the check is looking at the wrong markup"
    )


# --- R14 clocks belong to money, and only to money --------------------------
_TILE = re.compile(
    r'<div class="kpi-label">(?P<label>[^<]*)</div>'
    r'<div class="kpi-value[^"]*">(?P<value>.*?)</div>'
    r'(?:<div class="kpi-sub">(?P<sub>[^<]*)</div>)?',
    re.S,
)


def _clocked_tiles(html: str) -> list[tuple[str, str, str]]:
    return [(m.group("label"), m.group("value"), m.group("sub") or "")
            for m in _TILE.finditer(html) if "clock" in (m.group("sub") or "")]


def test_no_non_monetary_tile_carries_a_settlement_clock(op_state_html, rendered):
    """coldwalk:site2_churn_probability_carries_a_settlement_clock, closed as a CLASS
    (R10), not as an instance.

    R14's clock discipline exists so a financial figure states which basis it is on --
    settled, billed or banked. A probability, a count or a score has no such basis, so
    stamping one on it is slot-filling, and slot-filled labelling is exactly what makes
    a labelling discipline stop meaning anything. The rule is therefore: a tile may
    carry a clock only if its VALUE is money."""
    html = op_state_html + rendered["opState"]["both"]
    clocked = _clocked_tiles(html)
    assert clocked, (
        "no tile on the page carries a clock at all -- either R14 labelling is gone or "
        "this checker's pattern no longer matches the page's tile markup"
    )
    offenders = [(label, value, sub) for label, value, sub in clocked
                 if not re.match(r"^-?&pound;|^-?£", value.strip())]
    assert not offenders, (
        "non-monetary figures carrying an R14 settlement clock (a probability, count or "
        f"score has no settled/billed/banked basis): {offenders}"
    )


def test_mutation_a_clock_put_back_on_the_churn_probability_kills_a_named_test(tmp_path):
    """R15 for the class control above, proven through the page's own render."""
    src = INDEX.read_text(encoding="utf-8")
    marker = '"company estimate, not a fact · belief at last renewal decision"'
    assert marker in src, "the churn caption no longer has the shape this mutation reverts"
    mutant = tmp_path / "index.html"
    mutant.write_text(src.replace(marker, '"settled clock · company estimate"'), encoding="utf-8")
    out = _drive(mutant, tmp_path)
    offenders = [t for t in _clocked_tiles(_op_state_fragment(mutant) + out["opState"]["both"])
                 if not re.match(r"^-?&pound;|^-?£", t[1].strip())]
    assert offenders, (
        "MUTATION SURVIVED: a settlement clock was restored on the churn PROBABILITY and "
        "the class control did not flag it"
    )


# --- the door's own view selector -------------------------------------------
def test_the_door_carries_the_view_switch_its_own_copy_promises(rendered):
    """coldwalk:site2_landing_promises_a_view_switch_that_is_not_on_the_landing_page.

    The header says: choosing "The customer's side" BELOW renders that view on its own.
    The control used to be emitted only by renderHousehold(), so a reader arriving at the
    canonical door was told to use something that was not there. Subject is the RENDERED
    control coming out of the page's own setWallView(), not a grep of the file."""
    promise = INDEX.read_text(encoding="utf-8")
    assert "renders that view on its own" in promise, (
        "the header no longer makes this promise -- delete this test or restore the copy"
    )
    door = rendered["doorWallView"]
    assert door.get("both"), (
        "the canonical door renders no view selector, while the page's own header tells "
        "a reader to use one below"
    )
    for view, _label in [("both", None), ("customer", None), ("behind", None)]:
        assert f"setWallView('{view}')" in door[view], (
            f"the door's selector offers no way back to the {view!r} view"
        )
    assert 'class="wall-view-btn vactive"' in door["customer"], (
        "the door's selector does not show which view is active, so a reader cannot tell "
        "the page is filtered"
    )


def test_mutation_a_door_selector_that_never_refreshes_kills_a_named_test(tmp_path):
    """R15: drop the door selector's refresh out of setWallView and the active-state
    assertion above must fail -- a selector that never repaints tells the reader the
    wrong view is on."""
    src = INDEX.read_text(encoding="utf-8")
    assert "renderDoorWallView();applyWallViewToOpState()" in src, (
        "setWallView no longer refreshes the door selector before filtering"
    )
    mutant = tmp_path / "index.html"
    mutant.write_text(
        src.replace("renderDoorWallView();applyWallViewToOpState()", "applyWallViewToOpState()"),
        encoding="utf-8",
    )
    out = _drive(mutant, tmp_path)
    door = out["doorWallView"]
    # The distinction that matters: the selector is still THERE (rendered once at boot),
    # it is just frozen on the wrong view. A missing selector would prove nothing about
    # the refresh, so assert the mutant is the stale case and not the absent one.
    assert door["customer"] and "wall-view-btn" in door["customer"], (
        "the mutant rendered no selector at all -- this proves nothing about the refresh"
    )
    assert 'class="wall-view-btn vactive" onclick="setWallView(\'customer\')"' not in door["customer"], (
        "MUTATION SURVIVED: the refresh was removed and the selector still reported the "
        "customer view as active -- the assertion is not reading the repaint"
    )


# ===========================================================================
# (11) NEITHER SIDE OF THE WALL IS BLANK ON ANY TAB
#      coldwalk:site2_behind_the_wall_view_is_empty_on_two_of_six_tabs
# ===========================================================================
# The walk found Consumption and Billing rendering customer-side panels ONLY: selecting
# "Behind the wall" on either gave nav chrome and nothing else, and "Both sides" printed
# the empty-column placeholder. Driving the harness while fixing it found a THIRD blank
# sub-view the walk had not enumerated (billing:statement), which is why the control below
# is a sweep over every rendered sub-view rather than a check of the two tabs that were
# named. An exhibit whose whole thesis is the gap between two sides cannot show one side.
#
# WHY THIS IS NOT THE SAME CHECK AS SECTION (1). Section (1) asks whether a rendered block
# DECLARED a side; it is satisfied by a tab that renders one lonely customer panel, which is
# exactly the state the walk found. This asks whether both sides actually have content --
# a completeness property section (1) is structurally blind to.
_EMPTY_COLUMN = "Nothing on this side of the wall for this view."


def _tab_sides(rendered: dict, view: str) -> dict[str, set[str]]:
    return {tab: sides_in(html) for tab, html in rendered["views"][view].items()}


def test_the_control_sees_every_sub_view_the_page_renders(rendered):
    """ANTI-VACUITY, first. Every assertion below is a sweep over the rendered sub-views,
    so it passes trivially if the harness stops producing them. Pin the population by NAME
    -- including the two the walk named and the one it missed."""
    tabs = set(rendered["views"]["both"])
    for required in ("consumption", "billing:bills", "billing:statement"):
        assert required in tabs, (
            f"{required!r} is not in the driven population -- the blank-side control would "
            f"be blind to the very sub-view the finding was about. Got: {sorted(tabs)}"
        )
    assert len(tabs) >= 8, f"only {len(tabs)} sub-views driven -- population shrank: {sorted(tabs)}"


def test_no_tab_is_blank_behind_the_wall(rendered):
    """THE CONTROL. Selecting 'Behind the wall' must leave content on every tab."""
    blank = sorted(tab for tab, sides in _tab_sides(rendered, "behind").items() if not sides)
    assert not blank, (
        "these tabs render NOTHING behind the wall -- a reader who selects that view gets "
        f"nav chrome and a standing note: {blank}"
    )


def test_no_tab_is_blank_on_the_customers_own_side(rendered):
    """The same property in the other direction: the customer-eye view is a coherent
    subset only if it is actually populated on every tab."""
    blank = sorted(tab for tab, sides in _tab_sides(rendered, "customer").items() if not sides)
    assert not blank, f"these tabs render nothing in the customer-eye view: {blank}"


def test_the_both_sides_view_never_prints_an_empty_column(rendered):
    """The reader-visible symptom the walk actually saw. layoutPanels() prints a
    placeholder when a column has no panels; on this page that placeholder is a defect
    report, so it must never reach a reader."""
    offenders = sorted(tab for tab, html in rendered["views"]["both"].items()
                       if _EMPTY_COLUMN in html)
    assert not offenders, (
        f"the empty-column placeholder ({_EMPTY_COLUMN!r}) rendered on: {offenders}"
    )


def test_the_two_tabs_the_walk_named_carry_real_content_not_empty_shells(rendered):
    """A panel that declares a side and renders nothing would satisfy every check above.
    Assert the repaired tabs carry the figures that make them load-bearing."""
    behind = rendered["views"]["behind"]
    cons = behind["consumption"]
    assert "Estimated reads" in cons and "Written off under back-billing rules" in cons, (
        "the consumption company panel lost the read-exposure figures that are its reason "
        "to exist"
    )
    assert "Net &pound;/MWh" in cons or "Net £/MWh" in cons, (
        "the consumption SIM panel lost its unit-margin column"
    )
    for tab in ("billing:bills", "billing:statement"):
        assert "settled clock" in behind[tab] and "billed clock" in behind[tab], (
            f"{tab} behind the wall no longer puts the two clocks beside each other -- "
            "which is the whole content the finding said was missing"
        )


def test_the_repaired_panels_did_not_smuggle_a_figure_across_the_wall(rendered):
    """The repair adds panels on the far side; the wall checks must still hold over them.
    Named-instance form so this fails for a STATED reason rather than via section (3)."""
    customer = "".join(
        p["html"] for tab in ("consumption", "billing:bills", "billing:statement")
        for p in scan(rendered["views"]["customer"][tab]).panels
    )
    leaked = figure_violations(customer, COMPANY_ONLY_FIGURES) + figure_violations(
        customer, SIM_ONLY_FIGURES)
    assert not leaked, f"the repaired tabs leaked into the customer-eye view: {leaked}"
    company = "".join(
        p["html"] for tab in ("consumption", "billing:bills", "billing:statement")
        for p in scan(rendered["views"]["both"][tab]).panels if p["side"] == "company"
    )
    assert not figure_violations(company, SIM_ONLY_FIGURES), (
        "the repaired tabs put a SIM-only figure under a company panel -- the per-year "
        "wholesale result belongs on the SIM panel, which is why it renders there"
    )


# --- R15, both ways ---------------------------------------------------------
def test_mutation_dropping_the_consumption_far_side_kills_a_named_test(tmp_path):
    """R15 direction 1: revert Consumption to customer-only -- the state the walk found --
    and the blank-side control must fire."""
    src = INDEX.read_text(encoding="utf-8")
    marker = "  out.push(consumptionCompanyPanel(d));\n  out.push(consumptionSimPanel(d));\n"
    assert marker in src, "consumptionPanels no longer has the shape this mutation reverts"
    mutant = tmp_path / "index.html"
    mutant.write_text(src.replace(marker, ""), encoding="utf-8")
    out = _drive(mutant, tmp_path)
    assert not sides_in(out["views"]["behind"]["consumption"]), (
        "the mutant still rendered something behind the wall on Consumption -- this proves "
        "nothing about the control"
    )
    with pytest.raises(AssertionError, match="render NOTHING behind the wall"):
        test_no_tab_is_blank_behind_the_wall(out)
    with pytest.raises(AssertionError, match="empty-column placeholder"):
        test_the_both_sides_view_never_prints_an_empty_column(out)


def test_mutation_dropping_the_billing_far_side_kills_a_named_test(tmp_path):
    """R15 direction 2: the same defect on the other repaired tab, mutated independently
    so one panel cannot carry the other's proof."""
    src = INDEX.read_text(encoding="utf-8")
    marker = '    out.push(billingCompanyPanel(BILL_FUEL==="elec"?HH.elec:HH.gas));\n'
    assert marker in src, "billingPanels no longer has the shape this mutation reverts"
    mutant = tmp_path / "index.html"
    mutant.write_text(src.replace(marker, ""), encoding="utf-8")
    out = _drive(mutant, tmp_path)
    assert not sides_in(out["views"]["behind"]["billing:bills"]), (
        "the mutant still rendered something behind the wall on Billing -- proves nothing"
    )
    with pytest.raises(AssertionError, match="render NOTHING behind the wall"):
        test_no_tab_is_blank_behind_the_wall(out)


def test_mutation_a_side_declared_but_empty_panel_does_not_satisfy_the_control(tmp_path):
    """R15 fail-open probe, the subtle one. A panel that declares a side and renders an
    empty body would pass every side-DECLARATION check in section (1) and would pass the
    blank-side sweep too, because a side is present. The content check is what catches it,
    so prove the content check is what is doing the work."""
    src = INDEX.read_text(encoding="utf-8")
    marker = '"<div class=\\"row\\"><span class=\\"rl\\">Estimated reads</span>'
    assert marker in src, "the consumption company panel no longer has the row this drops"
    mutant = tmp_path / "index.html"
    mutant.write_text(src.replace("Estimated reads", "Something else entirely"), encoding="utf-8")
    out = _drive(mutant, tmp_path)
    # Still non-blank -- the sweep is satisfied, which is precisely the blind spot.
    assert sides_in(out["views"]["behind"]["consumption"]), "mutant went blank; wrong probe"
    test_no_tab_is_blank_behind_the_wall(out)
    with pytest.raises(AssertionError, match="read-exposure figures"):
        test_the_two_tabs_the_walk_named_carry_real_content_not_empty_shells(out)


# ---------------------------------------------------------------------------
# The household's money is the HOUSEHOLD's, not one fuel leg's
# (coldwalk:site2_dual_fuel_household_shows_electricity_only_money)
#
# The exhibit is headed "One household -- end to end" and its own first tile declares
# "Products: dual fuel / electricity + gas". Every money figure under it came from
# company.json's `household` block, which is commodity='electricity' ONLY. So the page
# understated its own declared subject by ~60% on lifetime net, told the account holder --
# on the CUSTOMER-OBSERVABLE side of the wall -- that they had received 72 invoices when
# they had received 144, and printed "Balance £0.00 / paid up to date" while the same
# page's Risk tab showed the household in credit.
#
# The rule these tests pin is a scope rule, not a value rule: a money figure is either
# summed over EVERY leg the household has and scoped "household", or it names the single
# leg it came from. The second half is the one that can fail, so it is driven explicitly.
# ---------------------------------------------------------------------------
_MONEY_PANELS = ("cust-money", "cust-value")


def _money_tiles(index: Path = INDEX, legs: tuple[Path, ...] | None = None) -> dict[str, tuple[str, str]]:
    """label -> (value, sub) across both op-state money panels, as the page renders them."""
    rendered = _op_state_render(index, legs)
    tiles: dict[str, tuple[str, str]] = {}
    for panel in _MONEY_PANELS:
        for m in _TILE.finditer(rendered.get(panel, "")):
            tiles[m.group("label").strip()] = (m.group("value").strip(), (m.group("sub") or "").strip())
    assert tiles, "no money tiles rendered at all -- every assertion below would be vacuous"
    return tiles


def _leg_records() -> tuple[dict, dict]:
    elec, gas = _dual_fuel_pair()
    return json.loads(elec.read_text(encoding="utf-8")), json.loads(gas.read_text(encoding="utf-8"))


def _money(value: str) -> float:
    return float(value.replace("&pound;", "").replace("£", "").replace(",", "").replace("−", "-"))


def test_the_dual_fuel_fixture_has_two_legs_that_actually_differ():
    """Vacuity guard, first: if the gas leg carried no money -- or the same money as the
    electricity leg -- then summing it and not summing it would render identically, and
    every assertion below would pass over a broken page."""
    e, g = _leg_records()
    assert g["ledger"]["total_billed_gbp"] > 0, "gas leg bills nothing -- the sum test is vacuous"
    assert g["ledger"]["total_billed_gbp"] != e["ledger"]["total_billed_gbp"], (
        "both legs bill the identical amount -- a one-leg render would be indistinguishable "
        "from a household render and this section would prove nothing"
    )
    assert g["lifetime_net_gbp"] != 0, "gas leg has no net -- the company-side sum test is vacuous"


# The two predicates, extracted so the R15 mutations below can kill the CHECKER a named
# test runs, rather than re-deriving an equivalent check inside the mutation (which would
# prove only that the mutation's own copy of the rule works).
def _check_household_sums(tiles: dict[str, tuple[str, str]], e: dict, g: dict) -> None:
    expected = {
        "Billed (lifetime)": e["ledger"]["total_billed_gbp"] + g["ledger"]["total_billed_gbp"],
        "Collected": e["ledger"]["total_collected_gbp"] + g["ledger"]["total_collected_gbp"],
        "Balance": e["ledger"]["current_balance_gbp"] + g["ledger"]["current_balance_gbp"],
        "Lifetime net (commodity)": e["lifetime_net_gbp"] + g["lifetime_net_gbp"],
        "Cost to serve": e["cost_to_serve_gbp"] + g["cost_to_serve_gbp"],
    }
    for label, want in expected.items():
        assert label in tiles, f"the exhibit no longer renders a '{label}' tile"
        got = _money(tiles[label][0])
        assert abs(got - want) < 0.02, (
            f"'{label}' renders {got} but this household's two legs sum to {round(want, 2)} -- "
            "a single-leg figure is being shown under a household heading"
        )


def _check_no_household_claim_without_every_leg(tiles: dict[str, tuple[str, str]]) -> None:
    offenders = {label: sub for label, (_v, sub) in tiles.items()
                 if "household" in sub.lower() and "clock" in sub}
    assert not offenders, (
        "money tiles captioned 'household' while the household's gas leg was not loaded -- "
        f"these figures cover the electricity leg only: {offenders}"
    )
    scoped = [label for label, (_v, sub) in tiles.items() if "leg only" in sub]
    assert scoped, (
        "the incomplete render named no leg at all -- a reader cannot tell these are one "
        "fuel account's figures rather than the household's"
    )


def test_the_household_money_panels_sum_every_fuel_leg():
    """Each money figure equals the sum over the household's legs, computed here from the
    SAME published per-customer records the page reads -- not from a number typed into this
    test, and not from company.json's single-leg block, which is the thing being corrected."""
    e, g = _leg_records()
    _check_household_sums(_money_tiles(), e, g)


def test_the_invoice_count_is_every_invoice_the_account_holder_received():
    """The customer-observable half of the same defect: the count sits next to 'Billed
    (lifetime)' on the side of the wall the account holder can see, so it must be the
    invoices they actually got, across both fuels."""
    e, g = _leg_records()
    want = len(e["invoices"]) + len(g["invoices"])
    sub = _money_tiles()["Billed (lifetime)"][1]
    assert f"{want} invoices" in sub, (
        f"the billed tile says '{sub}' -- this household received {want} invoices across its "
        f"two fuel accounts ({len(e['invoices'])} electricity + {len(g['invoices'])} gas)"
    )


def test_the_household_balance_agrees_with_the_drill_downs_combined_position():
    """The finding's cross-tab half: the exhibit showed 'Balance GBP0.00 -- paid up to date'
    while the Risk tab showed the household combined position in credit. Two balances on one
    page with no stated scope. They are now the same quantity."""
    e, g = _leg_records()
    want = e["ledger"]["current_balance_gbp"] + g["ledger"]["current_balance_gbp"]
    got = _money(_money_tiles()["Balance"][0])
    assert abs(got - want) < 0.02, (
        f"the exhibit's balance is {got} but the household's combined ledger position is "
        f"{round(want, 2)} -- the page still carries two different balances for one household"
    )


@pytest.mark.parametrize("one_leg", [False, True], ids=["no-legs", "one-leg"])
def test_no_money_figure_claims_household_scope_while_derived_from_fewer_legs(one_leg):
    """THE control. A figure summed over fewer legs than the household has must name the leg
    it came from and must NOT be captioned 'household' -- the defect being fixed is precisely
    a single-leg figure wearing a household caption, so an incomplete render that still said
    'household' would reintroduce it while every value test above stayed green."""
    fixture = (_dual_fuel_pair()[0],) if one_leg else ()
    _check_no_household_claim_without_every_leg(_money_tiles(legs=fixture))


def test_mutation_summing_only_the_first_leg_kills_a_named_test(tmp_path):
    """R15, direction 1: the ORIGINAL defect, restored -- electricity-leg values under a
    household caption. The scope word stays correct, so only the value check can catch it,
    and the mutation is required to kill that check by name."""
    src = INDEX.read_text(encoding="utf-8")
    marker = "var sum=function(f){return acc.reduce(function(a,x){return a+(Number(f(x))||0);},0);};"
    assert marker in src, "the household sum no longer has the shape this mutation reverts"
    mutant = tmp_path / "index.html"
    mutant.write_text(src.replace(marker, "var sum=function(f){return Number(f(acc[0]))||0;};"),
                      encoding="utf-8")
    tiles = _money_tiles(mutant)
    assert "household" in tiles["Billed (lifetime)"][1], (
        "this mutation is meant to keep the household CAPTION and corrupt only the "
        "arithmetic; it changed the caption instead, so it proves the wrong control"
    )
    with pytest.raises(AssertionError, match="single-leg figure is being shown"):
        _check_household_sums(tiles, *_leg_records())


def test_mutation_a_single_leg_figure_wearing_a_household_caption_kills_a_named_test(tmp_path):
    """R15, direction 2: the scope guard itself. A fallback that says 'household' when a leg
    is missing is the defect with the label filed off, and no value check can see it -- the
    values are correct FOR ONE LEG."""
    src = INDEX.read_text(encoding="utf-8")
    marker = ': (dual?(String(h.commodity||"electricity")+" leg only"):"household \u00b7 "+String(h.commodity||""));'
    assert marker in src, "the scope fallback no longer has the shape this mutation reverts"
    mutant = tmp_path / "index.html"
    mutant.write_text(src.replace(marker, ': "household";'), encoding="utf-8")
    with pytest.raises(AssertionError, match="captioned 'household'"):
        _check_no_household_claim_without_every_leg(_money_tiles(mutant, legs=(_dual_fuel_pair()[0],)))
