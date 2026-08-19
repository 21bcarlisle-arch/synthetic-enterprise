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

import ast
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

# ---------------------------------------------------------------------------
# THE SOLE LOCATOR for "the page as it SHIPPED before a named repair".
#
# Sections 18, 19, 21 and 22 each need the committed revision that predates their own
# repair -- R15's only arm whose subject is the REAL defect rather than a synthetic
# reversal of the fix. Until 2026-08-19 each section had privately written its own, and
# every one of the four was broken:
#
#   * 18, 19 and 21 walked a FIXED ANCESTOR WINDOW (HEAD then HEAD~1..3 / ..8) looking
#     for the absence of their own symbol. A window is wall-clock in disguise. This repo
#     commits many times a day, so all three had scrolled past their window and decayed
#     into SKIPS -- the mutation arms still reported green while the arm that proves the
#     defect was ever real had silently stopped executing. That is R15's FAIL-SILENT
#     pattern applied to the proofs themselves.
#   * 22 was window-free and STILL never ran: it handed `git -C <site/customers>` a
#     REPO-ROOT-relative pathspec, and git resolves a pathspec relative to -C, so
#     `git log -S` matched nothing and the locator returned None on every call. It was
#     green for exactly one tick -- on the uncommitted-case branch below, before its own
#     symbol was committed -- and turned RED the moment its repair landed.
#
# Four private answers to one question is the same root cause this module has now paid
# for four times (four sentence sites deciding privately what to claim about one
# household's money; two governors deciding privately what a subject is). So the repair
# is a SOLE WRITER, not three edits: ask git WHICH COMMIT introduced the symbol and take
# that commit's parent. No window, no pinned SHA, nothing to decay.
# ---------------------------------------------------------------------------
INDEX_PATH = "site/customers/index.html"
MODULE_PATH = "site/customers/test_wall_exhibit.py"


def _repo_root() -> str:
    """Asked of git rather than assumed from HERE. The pathspec bug above is exactly what
    happens when a git invocation and its path argument disagree about their origin."""
    p = subprocess.run(["git", "-C", str(HERE), "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True, timeout=60)
    assert p.returncode == 0, f"not a git checkout: {p.stderr.strip()}"
    return p.stdout.strip()


def _pre_repair_source(symbol: str, path: str = INDEX_PATH) -> str | None:
    """`path` as it SHIPPED before `symbol` was introduced, or None if unfindable.

    Returning None is not a licence to skip: every caller ASSERTS on it, because "the
    proof did not run" and "the proof passed" must not look the same to a reader of the
    suite. None is reserved for the genuinely unanswerable case (the introducing commit
    is a root commit, or the path has no history at all).
    """
    root = _repo_root()

    def show(rev: str) -> str | None:
        p = subprocess.run(["git", "-C", root, "show", f"{rev}:{path}"],
                           capture_output=True, text=True, timeout=60)
        return p.stdout if p.returncode == 0 else None

    head = show("HEAD")
    if head is not None and symbol not in head:
        return head  # not yet committed: HEAD *is* the pre-repair revision

    p = subprocess.run(
        ["git", "-C", root, "log", "--format=%H", "-S", symbol, "--", path],
        capture_output=True, text=True, timeout=120,
    )
    shas = [s for s in p.stdout.split() if s]
    if not shas:
        return None
    src = show(f"{shas[-1]}^")  # oldest = the commit that INTRODUCED it; take its parent
    if src is None or symbol in src:
        return None  # post-condition: never hand back a page that still carries the repair
    return src

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

# The "(at closure)" qualifier section 13 puts on a closed household's forward-looking
# labels. Optional everywhere it appears below, so a pattern matches the same figure on a
# live household and on a closed one.
_Q = r"(?: \(at closure\))?"

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
    # Section 13 stamps a closed household's forward-looking labels "(at closure)". The
    # '<'-anchored patterns went blind the moment that shipped -- the SAME narrowed-parser
    # class the comment above records, caught a second time by the anti-vacuity test rather
    # than by review. `_Q` is the qualifier, optional, so the leak checker keeps seeing
    # these figures on a closed household AND on a live one.
    # The op-state exhibit now carries TWO churn tiles -- the renewal-risk model's score
    # and the belief the company acted on (coldwalk:site2_churn_belief_published_as_23_
    # and_5_for_one_decision). Both are company-only figures, and a '<'-anchored "Churn
    # risk<" saw NEITHER once each grew a producer qualifier -- the third instance of the
    # narrowed-parser class this dict's own comments record. Unanchored on purpose.
    "churn probability": (rf'class="kpi-label">Churn Probability{_Q}<',
                          r'class="kpi-label">Churn risk'),
    "customer lifetime value": (rf'class="rl">Customer Lifetime Value{_Q}<', r'>Combined CLV<'),
    "pricing action": (r'class="kpi-label">Pricing Action',),
    "forecast profit": (rf'class="rl">Forecast Annual Profit{_Q}<', r'>Projected Net Margin<',
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


def _op_state_render(index: Path = INDEX, legs: tuple[Path, ...] | None = None,
                     company: str | None = None) -> dict[str, str]:
    """Run the op-state script over company.json plus a chosen set of household fuel legs.

    `legs` defaults to EVERY leg the household has, because that is what the live page's
    own boot path fetches. Passing a SUBSET is how the leg-scoped fallback gets driven --
    see the dual-fuel section below; that path is the half of the scope control that can
    actually fail, so it needs to be reachable from a test.

    `company` overrides the published company.json blob. The page carries TWO producers of
    the household's collections record (that block, and the legs' own reaction chains), so
    a test that can only ever feed them matching inputs cannot drive the disagreement --
    see section 18.
    """
    if legs is None:
        legs = _dual_fuel_pair()
    proc = subprocess.run(
        [NODE, str(RENDER_HARNESS), str(index), *[str(p) for p in legs]],
        input=COMPANY_DATA.read_text(encoding="utf-8") if company is None else company,
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
    marker = '<div data-wall-chrome="1" style="text-align:center;margin:6px 0 8px"><a href="./?acc=C1"'
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
    marker = ('"company estimate, not a fact · bill-shock model scored at the last '
              'renewal period"')
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


# --- two churn estimators, published as two ---------------------------------
# coldwalk:site2_churn_belief_published_as_23_and_5_for_one_decision.
#
# The page published company.json's `latest_churn_probability` under the caption "belief
# at last renewal decision" while rendering a DIFFERENT number -- the reaction chain's
# `company_belief` -- for that same decision further down the same page. Measured over
# docs/reports/run_output_latest.json on 2026-08-18, the two estimators disagree on 54 of
# 58 renewal decisions (93%), so this is a class and not a C1 curiosity.
#
# The figures were never the defect; the caption was. These tests pin that each tile names
# the producer its number came from, and that the "acted on" tile really carries the
# chain's belief rather than a second copy of the model's score.
_CHURN_MODEL_LABEL = "Churn risk (renewal-risk model)"
_CHURN_ACTED_LABEL = "Churn risk the company acted on"


def _op_state_tiles(html: str) -> dict[str, tuple[str, str]]:
    return {m.group("label"): (m.group("value"), m.group("sub") or "")
            for m in _TILE.finditer(html)}


def _chain_last_belief(leg: Path) -> tuple[str, float] | None:
    """The operative belief, read STRAIGHT from the published leg record.

    Independence (R15 tautology guard): this walks the on-disk reaction_chain itself, so
    the expected value never passes through the render path it is used to check."""
    best = None
    for event in json.loads(leg.read_text(encoding="utf-8")).get("reaction_chain", []):
        if not str(event.get("event_type") or "").startswith("outcome_"):
            continue
        if event.get("company_belief") is None or not event.get("date"):
            continue
        if best is None or event["date"] > best[0]:
            best = (event["date"], float(event["company_belief"]))
    return best


def _assert_producer_named(index: Path) -> None:
    """The provenance assertions, over an ARBITRARY index, so a mutation can drive exactly
    the same checks the named test below makes rather than a re-typed approximation."""
    tiles = _op_state_tiles(_op_state_render(index=index).get("cust-value", ""))
    assert _CHURN_MODEL_LABEL in tiles and _CHURN_ACTED_LABEL in tiles, (
        "the op-state exhibit does not render both churn estimates under their own "
        "labels. Before this repair it rendered a single 'Churn risk' tile carrying the "
        "renewal-risk model's score under a caption claiming it was the belief the "
        f"company acted on. Saw: {sorted(tiles)}"
    )
    model_sub = tiles[_CHURN_MODEL_LABEL][1]
    assert "bill-shock model" in model_sub, (
        f"the renewal-risk model tile does not name its producer: {model_sub!r}"
    )
    assert "belief at last renewal decision" not in model_sub, (
        "the renewal-risk model's score is captioned as the belief the company held at "
        "the last renewal decision -- that is the OTHER estimator, and the page renders "
        "it a few hundred pixels further down with a different value"
    )


def test_the_two_churn_estimates_each_name_their_own_producer():
    """Neither churn tile may claim the other's provenance."""
    tiles = _op_state_tiles(_op_state_render().get("cust-value", ""))
    assert _CHURN_MODEL_LABEL in tiles and _CHURN_ACTED_LABEL in tiles, (
        "the op-state exhibit no longer renders both churn estimates -- it published one "
        f"of them as the other before, which is the defect this pins. Saw: {sorted(tiles)}"
    )
    _assert_producer_named(INDEX)
    assert "renewal decision" in tiles[_CHURN_ACTED_LABEL][1], (
        "the acted-on tile does not say which decision its belief was formed at"
    )


def test_the_acted_on_churn_tile_carries_the_chains_belief_not_the_models_score():
    """The independence half: the rendered value must be the CHAIN's number."""
    elec, _gas = _dual_fuel_pair()
    expected = _chain_last_belief(elec)
    assert expected is not None, (
        "the fixture household publishes no renewal outcome carrying a belief -- this "
        "assertion would be vacuous"
    )
    date, belief = expected
    tiles = _op_state_tiles(_op_state_render().get("cust-value", ""))
    value, sub = tiles[_CHURN_ACTED_LABEL]
    assert value.strip() == f"{belief * 100:.0f}%", (
        f"the acted-on tile renders {value!r}, but the household's own reaction chain "
        f"records {belief:.3f} at its last decision ({date}). Publishing the model's "
        f"score here is exactly the substitution this finding named"
    )
    assert date in sub, f"the acted-on tile does not date its decision ({sub!r})"
    model_value = tiles[_CHURN_MODEL_LABEL][0].strip()
    assert model_value != value.strip(), (
        "both churn tiles render the same number, so this fixture cannot tell a real "
        "reconciliation from one tile copied into the other"
    )


def test_a_household_with_no_recorded_belief_renders_absence_not_a_number(tmp_path):
    """FAIL-CLOSED (R15): 1 of the 19 published legs carries no outcome event with a
    belief. Absence must render as absence -- never as agreement with the model's score,
    which is the fail-open shape the page's own NO_BELIEF rule exists to refuse."""
    elec, _gas = _dual_fuel_pair()
    stripped = json.loads(elec.read_text(encoding="utf-8"))
    stripped["reaction_chain"] = [
        e for e in stripped.get("reaction_chain", [])
        if not str(e.get("event_type") or "").startswith("outcome_")
    ]
    leg = tmp_path / "C1.json"
    leg.write_text(json.dumps(stripped), encoding="utf-8")
    tiles = _op_state_tiles(_op_state_render(legs=(leg,)).get("cust-value", ""))
    value, sub = tiles[_CHURN_ACTED_LABEL]
    assert value.strip() == "--", (
        f"a household with no recorded decision belief renders {value!r} as though the "
        "company had held one"
    )
    assert "no renewal decision" in sub, f"absence is not explained to the reader: {sub!r}"


def test_mutation_restoring_the_false_caption_kills_a_named_test(tmp_path):
    """R15 direction 1: put the original false provenance back."""
    src = INDEX.read_text(encoding="utf-8")
    marker = "company estimate, not a fact · bill-shock model scored at the last renewal period"
    assert marker in src, "the model tile's caption no longer has the shape this reverts"
    mutant = tmp_path / "index.html"
    mutant.write_text(
        src.replace(marker, "company estimate, not a fact · belief at last renewal decision"),
        encoding="utf-8",
    )
    tiles = _op_state_tiles(_op_state_render(index=mutant).get("cust-value", ""))
    sub = tiles[_CHURN_MODEL_LABEL][1]
    assert "belief at last renewal decision" in sub and "bill-shock model" not in sub, (
        "MUTATION DID NOT APPLY: the caption was not reverted, so the assertion below "
        "would prove nothing"
    )
    with pytest.raises(AssertionError):
        _assert_producer_named(mutant)


def test_mutation_publishing_the_models_score_as_the_acted_on_belief_kills_a_named_test(tmp_path):
    """R15 direction 2: the substitution the finding actually caught -- render the model's
    score in the tile that claims to be the belief the company acted on."""
    src = INDEX.read_text(encoding="utf-8")
    marker = "? tile(\"Churn risk the company acted on\", pct(op.belief),"
    assert marker in src, "the acted-on tile no longer has the shape this mutation targets"
    mutant = tmp_path / "index.html"
    mutant.write_text(
        src.replace(marker,
                    "? tile(\"Churn risk the company acted on\", pct(h.latest_churn_probability),"),
        encoding="utf-8",
    )
    elec, _gas = _dual_fuel_pair()
    expected = _chain_last_belief(elec)
    assert expected is not None
    tiles = _op_state_tiles(_op_state_render(index=mutant).get("cust-value", ""))
    rendered_value = tiles[_CHURN_ACTED_LABEL][0].strip()
    assert rendered_value != f"{expected[1] * 100:.0f}%", (
        "MUTATION SURVIVED: the acted-on tile rendered the chain's belief even after the "
        "page was changed to publish the model's score there -- the named test above "
        "cannot tell the two estimators apart"
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


# ---------------------------------------------------------------------------
# 13. A closed account has no future, so it has no live forecast
#     (coldwalk:site2_churned_account_presented_in_the_present_tense, render half)
#
# Five of the nine domestic households published to this page carry a real `churned`
# timeline event. The page rendered their churn probability, expected lifetime, pricing
# action, CLV and forecast annual profit as LIVE forward-looking estimates -- under a
# present-day data stamp, directly beside its own notice reading "Account closed
# 2021-12-30 -- final bill C1-INV72. Account settled to zero." A supplier holds no live
# churn forecast for a household that has left; it holds the last belief it formed before
# they left.
#
# The rule pinned here is a TENSE rule, not a value rule: a forward-looking figure on a
# closed household must present as a belief frozen at the closure date, and a forward-
# looking figure on a LIVE household must not. Both directions are asserted, because a
# one-directional control is passed by "never stamp" (the original defect) or by "always
# stamp" (a page that tells every reader their live account has closed). Each direction
# is mutation-killed below.
#
# NOT fixed here, and deliberately: the #op-state exhibit's own churn tile reads
# company.json's `household` block, which carries no closure field at all -- it cannot
# know without either new plumbing (forbidden by this atom's constraint) or an inference
# from annual_pnl's last year, which would be an inference printed as a fact. And the
# published records themselves disagree: C1's electricity leg carries churn_probability
# 0.23 / clv 2840.5 while its gas leg, same household and same closure date, carries
# zeros. That is the finding's DATA half and belongs to tools/generate_customer_data.py,
# not to this page.
# ---------------------------------------------------------------------------
FORWARD_LOOKING_LABELS = (
    "Churn Probability",
    "Expected Lifetime",
    "Pricing Action (Electricity)",
    "Pricing Action (Gas)",
    "Customer Lifetime Value",
    "Forecast Annual Profit",
)
FROZEN_SUFFIX = " (at closure)"

# Only LABEL sites. The projection's prose says "discounted at the same rate used for
# Customer Lifetime Value", which is a reference, not a figure wearing a label -- reading
# raw text would make that sentence look like an unstamped figure and the control would
# cry wolf on a page that was right.
_LABEL_SITE = re.compile(
    r'<span class="rl">(?P<rl>[^<]*)</span>|<div class="kpi-label">(?P<kpi>[^<]*)</div>'
)


def _closed_household() -> tuple[Path, Path]:
    return CUSTOMER_DATA / "C1.json", CUSTOMER_DATA / "C1g.json"


def _live_household() -> tuple[Path, Path]:
    return CUSTOMER_DATA / "C2.json", CUSTOMER_DATA / "C2g.json"


def _closure_dates(legs: tuple[Path, ...]) -> list[str]:
    dates = []
    for leg in legs:
        rec = json.loads(leg.read_text(encoding="utf-8"))
        dates += [e["date"] for e in rec.get("timeline", []) if e.get("type") == "churned"]
    return sorted(dates)


def _drive_pair(index: Path, tmp: Path, legs: tuple[Path, Path]) -> tuple[list[str], str]:
    """(rendered forward-looking labels, all rendered html) for one household.

    Runs the page's own code over the published records for THAT household, across every
    tab and both injection points that carry a forward-looking figure -- the same route
    the real fixture takes, so a mutation cannot pass by being rendered differently here.
    """
    proc = _run(index, legs[0], legs[1], tmp)
    assert proc.returncode == 0, f"harness failed on {legs[0].name}: {proc.stderr}"
    out = json.loads(proc.stdout)
    html = "".join(out["views"]["both"].values()) + "".join(out["injected"].values())
    labels = []
    for m in _LABEL_SITE.finditer(html):
        text = (m.group("rl") or m.group("kpi") or "").strip()
        base = text[: -len(FROZEN_SUFFIX)] if text.endswith(FROZEN_SUFFIX) else text
        if base in FORWARD_LOOKING_LABELS:
            labels.append(text)
    assert labels, (
        "no forward-looking figure rendered at all -- every assertion below would be vacuous"
    )
    return labels, html


# The predicates, extracted so the R15 mutations kill the CHECKER a named test runs
# rather than a private re-derivation of the same rule.
def _check_frozen(labels: list[str]) -> None:
    live = sorted({lab for lab in labels if not lab.endswith(FROZEN_SUFFIX)})
    assert not live, (
        "this household has closed its account, and these forward-looking figures still "
        f"render as live estimates: {live} -- the supplier holds a last belief, not a forecast"
    )


def _check_not_frozen(labels: list[str]) -> None:
    stamped = sorted({lab for lab in labels if lab.endswith(FROZEN_SUFFIX)})
    assert not stamped, (
        "this household has NOT closed its account, yet these figures are presented as "
        f"beliefs frozen at closure: {stamped} -- an always-stamp render would satisfy the "
        "closed-account control while telling every live customer they had left"
    )


def test_the_closed_fixture_household_actually_carries_live_forward_looking_figures():
    """Vacuity guard, first. If the closed household's published record carried zeros for
    every forward-looking field, there would be nothing to mis-tense and the control below
    would pass over a page that had never been fixed.

    ANY, not ALL -- the docstring's own condition. This asserted `all(...)` until
    W2_17_dual_fuel_leg_clv_attribution landed the DATA half named at the top of this
    section, and the two upstream fixes together make ALL unmeetable BY DESIGN for a
    closed household: build_clv now excludes accounts that are no longer supplied
    (WORKER_FINDING_THE_BOOK_VALUE_COUNTS_CUSTOMERS_WHO_HAVE_ALREADY_LEFT), so a departed
    C1 gets no CLV, no expected lifetime and no forecast margin -- and the generator now
    publishes those as null instead of the fabricated zeros this section was written
    against. A household that has left SHOULD carry fewer live figures; demanding four of
    them made this guard red for the correct behaviour.

    It still guards what it was built to guard: a record blank in every field fails, and
    the control itself carries a second, independent vacuity assert at the RENDER level
    (`assert labels` in _drive_pair). Five of the six forward-looking labels still render
    for this household, so the control below is nowhere near vacuous.
    """
    elec, gas = _closed_household()
    assert _closure_dates((elec, gas)), "the 'closed' fixture has no churned event at all"
    rec = json.loads(elec.read_text(encoding="utf-8"))
    forward = {k: rec.get(k) for k in
               ("churn_probability", "clv_gbp", "expected_lifetime_periods", "forecast_annual_profit_gbp")}
    assert any(v for v in forward.values()), (
        f"the closed household publishes no live forward-looking figures at all ({forward}) "
        "-- the tense control would have nothing to catch"
    )


def test_the_live_fixture_household_has_not_closed():
    """Vacuity guard for the inverse direction: the negative fixture must really be open,
    or 'not stamped' would be proven on a second closed household."""
    assert not _closure_dates(_live_household()), (
        "the 'live' fixture household carries a churned event -- the inverse direction "
        "would be asserting that a CLOSED account is not stamped, which is the defect"
    )


def test_every_forward_looking_figure_on_a_closed_account_is_frozen(tmp_path):
    """THE control. Every forward-looking figure the page renders for a household that has
    closed its account presents as a belief frozen at closure, not a live forecast."""
    labels, _ = _drive_pair(INDEX, tmp_path, _closed_household())
    _check_frozen(labels)


def test_the_closed_account_panels_say_when_the_belief_was_frozen(tmp_path):
    """A stamp with no date is still the present tense -- the reader cannot tell WHEN the
    belief stopped being updated. The date rendered is the household's own churn event,
    read here from the published records rather than typed in, so a regenerated run cannot
    make this cry wolf."""
    legs = _closed_household()
    _labels, html = _drive_pair(INDEX, tmp_path, legs)
    want = _closure_dates(legs)[-1]
    assert f"closed its account on {want}" in html, (
        f"the closed-account panels never state the closure date {want} -- "
        "'(at closure)' alone does not tell the reader when the forecast stopped"
    )


def test_a_live_households_forward_looking_figures_are_not_stamped_frozen(tmp_path):
    """The other direction. A household that has not closed must render its forecasts as
    forecasts -- this is what stops the control being satisfied by stamping everything."""
    labels, _ = _drive_pair(INDEX, tmp_path, _live_household())
    _check_not_frozen(labels)


def test_mutation_dropping_the_frozen_stamp_kills_a_named_test(tmp_path):
    """R15, direction 1: the ORIGINAL defect restored. fwdLabel() is the sole writer of the
    qualifier, so returning the label unchanged is exactly the page as cold-eyes found it --
    a closed household's churn probability, expected lifetime, pricing action, CLV and
    forecast profit printed in the present tense. The frozen HINT survives this mutation
    deliberately: the subject of the killed test is the labels, and a page that explains in
    prose what its own labels contradict is the prose-control failure this atom exists to
    remove."""
    src = INDEX.read_text(encoding="utf-8")
    marker = "function fwdLabel(label){return householdClosureDate()?label+FROZEN_SUFFIX:label;}"
    assert marker in src, "the frozen-stamp writer no longer has the shape this mutation reverts"
    mutant = tmp_path / "index.html"
    mutant.write_text(src.replace(marker, "function fwdLabel(label){return label;}"), encoding="utf-8")
    labels, _ = _drive_pair(mutant, tmp_path, _closed_household())
    with pytest.raises(AssertionError, match="still render as live estimates"):
        _check_frozen(labels)


def test_mutation_stamping_every_household_frozen_kills_a_named_test(tmp_path):
    """R15, direction 2: the tautology. A closure detector that always answers 'closed'
    makes the control above pass on any page at all -- and tells a live account holder's
    supplier that its own customer has left. The inverse test is required to kill it."""
    src = INDEX.read_text(encoding="utf-8")
    marker = "  var legs=[HH.elec,HH.gas],best=null;"
    assert marker in src, "the closure detector no longer has the shape this mutation reverts"
    mutant = tmp_path / "index.html"
    mutant.write_text(src.replace(marker, '  var legs=[HH.elec,HH.gas],best="2021-12-30";'),
                      encoding="utf-8")
    labels, _ = _drive_pair(mutant, tmp_path, _live_household())
    with pytest.raises(AssertionError, match="has NOT closed its account"):
        _check_not_frozen(labels)


# ===========================================================================
# (14) THE PAGE IS DRIVEN OVER THE WHOLE PUBLISHED BOOK, NOT OVER TWO FIXTURES
#      -- a structural blank must not become either a refusal or a zero
# ===========================================================================
#
# Both defects this section closes were LIVE on https://poesys.net/customers/ and were
# invisible to a 82/82 green suite for the same reason: every control above drives one
# dual-fuel pair (C1/C1g) plus one live pair (C2/C2g). Two households of thirteen.
#
# DEFECT A -- THE REFUSAL FIRED ON REAL DATA. `chainSide()` fails closed, correctly: an
# event type nobody has sided cannot be placed, because placing it by default would be a
# silent claim about which side of the wall it belongs on. But `_CHAIN_SIDE` was written
# on 2026-08-13 against the RESIDENTIAL arrears ladder only, and simulation/arrears_engine
# .py also publishes the I&C dispute ladder (INVOICE_DISPUTED -> DISPUTE_NOTICE ->
# PAYMENT_PLAN_AGREED). Those three types are published live -- 22 events across C5, C6,
# C_IC2, C_IC3, C_IC3g and C_IC4 -- and none was sided. So `timelinePanels()` THREW on
# four of thirteen households, and because `renderTab()` has no catch, the Timeline tab
# rendered as an empty body with no message: the causal reaction chain, one of the three
# layers the atom's own exit criterion (3) names, was unreachable for those households on
# the public page. C_IC4 escaped only because its `timeline` array is empty, which is a
# latent version of the same bomb (queued, not fixed here: it is a generator question).
#
# DEFECT B -- THE BLANK BECAME A CONFIDENT ZERO. The records deliberately carry null for
# a forward-looking figure the company holds no belief about. `gbp()` honoured that; two
# other render sites did not. `(d.expected_lifetime_periods||0).toFixed(1)` printed
# "0.0 yrs" and `d.churn_probability||0` printed "0%" under a green "Low risk" caption,
# on the COMPANY-attributed Retention & Risk panel, for every household whose record says
# the figure is not modelled. `combinedTotals().clv` summed two nulls to the number 0 and
# published it as "Combined CLV £0" (null+null===0 in JS). This is the render instance of
# WORKER_FINDING_A_NULL_CLV_ENTERS_THE_PUBLISHED_MEDIAN_AS_THE_NUMBER_ZERO_2026-08-17,
# on the one surface where fabricating a company belief is the exhibit's own subject.
#
# THE CONTROL IS THE POPULATION, NOT THE THREE KEYS. Adding three entries to _CHAIN_SIDE
# and three null-guards is the instance fix; R10 requires the class to fail by itself. So
# every check below runs over EVERY published household, and the event-type census reads
# the page's map on one side and the published book on the other -- two independent
# sources, so the next stage the generator invents fails here before it reaches a reader.
# ---------------------------------------------------------------------------
_NUMERIC = re.compile(r"^-?[£$]?-?[\d,]+(?:\.\d+)?\s*(?:%|yrs|kWh)?$")

# published field -> the label it renders under
_BELIEF_SITES = {
    "clv_gbp": "Customer Lifetime Value",
    "expected_lifetime_periods": "Expected Lifetime",
    "churn_probability": "Churn Probability",
    "forecast_annual_profit_gbp": "Forecast Annual Profit",
}


def _published_households() -> list[tuple[str, Path, Path]]:
    """Every household published to this page, as (base id, elec leg, gas leg).

    The gas leg falls back to the electricity leg because the harness takes two paths and
    the page's own loader passes the same record twice for a single-fuel household.
    """
    legs: dict[str, dict[str, Path]] = {}
    for path in sorted(CUSTOMER_DATA.glob("*.json")):
        if path.name.startswith("_"):
            continue
        rec = json.loads(path.read_text(encoding="utf-8"))
        acct = rec.get("account_id") or path.stem
        base = acct[:-1] if acct.endswith("g") else acct
        legs.setdefault(base, {})["gas" if rec.get("commodity") == "gas" else "elec"] = path
    out = []
    for base, pair in sorted(legs.items()):
        elec = pair.get("elec") or pair.get("gas")
        out.append((base, elec, pair.get("gas") or elec))
    return out


def _chain_side_keys(index: Path) -> set[str]:
    """The page's OWN map, read out of the page rather than restated here -- restating it
    would make this a comparison of the test against itself."""
    m = re.search(r"var _CHAIN_SIDE=\{(.*?)\n\};", index.read_text(encoding="utf-8"), re.S)
    assert m, "the page no longer declares _CHAIN_SIDE in the shape this control reads"
    body = re.sub(r"/\*.*?\*/", " ", m.group(1), flags=re.S)
    return set(re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*:", body))


def _published_chain_types() -> dict[str, set[str]]:
    """event_type -> the record files that publish it. The independent side of the census."""
    seen: dict[str, set[str]] = {}
    for path in sorted(CUSTOMER_DATA.glob("*.json")):
        if path.name.startswith("_"):
            continue
        rec = json.loads(path.read_text(encoding="utf-8"))
        for ev in rec.get("reaction_chain") or []:
            seen.setdefault(str(ev.get("event_type")), set()).add(path.name)
    return seen


def _rendered_value(html: str, label: str) -> str | None:
    """The value rendered immediately after a label site, or None if the label is absent."""
    m = re.search(
        r'(?:<div class="kpi-label">|<span class="rl">)'
        + re.escape(label)
        + r'(?:\s*\(at closure\))?(?:</div>|</span>)\s*<[^>]*>([^<]*)<',
        html,
    )
    return m.group(1).strip() if m else None


def _render_household(index: Path, tmp: Path, legs: tuple[Path, Path]) -> str:
    proc = _run(index, legs[0], legs[1], tmp)
    assert proc.returncode == 0, (
        f"the page REFUSED to render {legs[0].name}: {proc.stderr.strip()[-400:]}"
    )
    out = json.loads(proc.stdout)
    return "".join(out["views"]["both"].values()) + "".join(out["injected"].values())


def test_the_page_renders_every_published_household(tmp_path):
    """THE population control, and the one that would have caught defect A live.

    Not "the fixture renders" -- every household this page is published to serve. A
    refusal is a blank tab on a public surface with no message, so the whole book is the
    subject or the control is measuring the two accounts someone happened to pick.
    """
    households = _published_households()
    assert len(households) > 5, (
        f"only {len(households)} households enumerated -- this control's whole point is "
        "the population, so a shrunken book makes it vacuous"
    )
    failed = []
    for base, elec, gas in households:
        proc = _run(INDEX, elec, gas, tmp_path)
        if proc.returncode != 0:
            reason = next((ln for ln in proc.stderr.splitlines() if "Error:" in ln), "")
            failed.append(f"{base}: {reason.strip()[:160]}")
    assert not failed, (
        f"{len(failed)} of {len(households)} published households do not render at all "
        "-- their tab body is empty on the live page:\n  " + "\n  ".join(failed)
    )


def test_every_reaction_chain_event_type_in_the_published_book_declares_a_side(tmp_path):
    """THE class control (R10). Independent, not tautological: one side is the page's own
    `_CHAIN_SIDE` map, the other is every `event_type` the generator actually publishes.
    The next stage simulation/arrears_engine.py invents fails HERE, before a reader meets
    an empty tab."""
    known = _chain_side_keys(INDEX)
    published = _published_chain_types()
    assert len(published) > 5, (
        f"only {len(published)} event types found in the published book -- census vacuous"
    )
    unsided = {
        t: sorted(files) for t, files in published.items()
        if t not in known and not t.startswith("outcome_")
    }
    assert not unsided, (
        "the published book carries reaction-chain event types the page cannot side, so "
        "chainSide() refuses and the Timeline tab renders empty for every household "
        f"below: {json.dumps({k: v for k, v in sorted(unsided.items())}, indent=2)}"
    )


def test_no_reaction_chain_row_renders_a_raw_event_type_as_its_own_label(tmp_path):
    """A sided-but-unlabelled type renders, so the census above passes -- and prints
    `arrears_payment_plan_agreed` at the reader. Siding and naming are separate omissions
    and need separate checks."""
    published = _published_chain_types()
    src = INDEX.read_text(encoding="utf-8")
    m = re.search(r"var _CHAIN_LABEL=\{(.*?)\n\};", src, re.S)
    assert m, "the page no longer declares _CHAIN_LABEL in the shape this control reads"
    labelled = set(re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*:", re.sub(r"/\*.*?\*/", " ", m.group(1), flags=re.S)))
    unlabelled = sorted(
        t for t in published
        if t not in labelled and not t.startswith("outcome_")
    )
    assert not unlabelled, (
        "these published event types have no human label, so chainLabel() falls back to "
        f"the raw snake_case identifier on a public page: {unlabelled}"
    )


def test_a_forward_looking_field_published_as_null_never_renders_as_a_number(tmp_path):
    """DEFECT B, over the whole book. A record that says "no belief" must not be rendered
    as a belief of zero. Asserted against the RENDERED value, not the source, so a second
    render site added later is covered by the same check."""
    offences = []
    for base, elec, gas in _published_households():
        rec = json.loads(elec.read_text(encoding="utf-8"))
        html = _render_household(INDEX, tmp_path, (elec, gas))
        for field, label in _BELIEF_SITES.items():
            if rec.get(field) is not None:
                continue
            value = _rendered_value(html, label)
            if value is not None and _NUMERIC.match(value.replace("&nbsp;", "")):
                offences.append(f"{base}: {field} is null, but '{label}' renders '{value}'")
    assert not offences, (
        "a field the published record deliberately carries as null is rendered as a "
        "number under a company-attributed label -- the page states a belief the company "
        "declined to hold:\n  " + "\n  ".join(offences)
    )


def test_a_household_that_does_publish_forward_looking_figures_still_renders_them(tmp_path):
    """The inverse, and the reason the check above cannot be satisfied by blanking
    everything. A record that HAS a belief must show it."""
    populated = []
    for base, elec, gas in _published_households():
        rec = json.loads(elec.read_text(encoding="utf-8"))
        have = {f: rec.get(f) for f in _BELIEF_SITES if rec.get(f) is not None}
        if not have:
            continue
        populated.append(base)
        html = _render_household(INDEX, tmp_path, (elec, gas))
        for field in have:
            value = _rendered_value(html, _BELIEF_SITES[field])
            assert value is not None and _NUMERIC.match(value.replace("&nbsp;", "")), (
                f"{base} publishes {field}={have[field]!r} and the page renders "
                f"'{_BELIEF_SITES[field]}' as {value!r} -- a real belief has been blanked"
            )
    assert len(populated) >= 3, (
        f"only {populated} publish any forward-looking figure at all -- this inverse "
        "would be proven on too small a population to stop the blank-everything fix"
    )


def test_the_published_book_carries_both_blank_and_populated_forward_looking_records():
    """Anti-vacuity on the DATA, pinning the population both controls above need. If the
    generator ever published a belief for every account, the null control would pass over
    a page that had never been fixed; if it published none, the inverse would."""
    blank, filled = [], []
    for base, elec, _gas in _published_households():
        rec = json.loads(elec.read_text(encoding="utf-8"))
        vals = [rec.get(f) for f in _BELIEF_SITES]
        (blank if all(v is None for v in vals) else filled).append(base)
    assert blank and filled, (
        f"the book no longer contains both cases (blank={blank}, populated={filled}) -- "
        "one of the two controls above has gone vacuous"
    )


# --- R15, both defects, both directions -----------------------------------


def test_mutation_unsiding_the_ic_dispute_ladder_kills_a_named_test(tmp_path):
    """R15 on defect A: the page exactly as it was live. Removing the three I&C dispute
    types puts the refusal back on four real households."""
    src = INDEX.read_text(encoding="utf-8")
    marker = '  arrears_invoice_disputed:"customer",arrears_dispute_notice:"customer",\n  arrears_payment_plan_agreed:"customer",\n'
    assert marker in src, "the I&C dispute siding no longer has the shape this mutation reverts"
    mutant = tmp_path / "index.html"
    mutant.write_text(src.replace(marker, ""), encoding="utf-8")
    failed = []
    for base, elec, gas in _published_households():
        if _run(mutant, elec, gas, tmp_path).returncode != 0:
            failed.append(base)
    assert failed, (
        "MUTATION SURVIVED: the page rendered every household with the I&C dispute ladder "
        "unsided, so test_the_page_renders_every_published_household cannot catch defect A"
    )
    _saved, globals()["INDEX"] = INDEX, mutant
    try:
        with pytest.raises(AssertionError, match="do not render at all"):
            test_the_page_renders_every_published_household(tmp_path)
        with pytest.raises(AssertionError, match="cannot side"):
            test_every_reaction_chain_event_type_in_the_published_book_declares_a_side(tmp_path)
    finally:
        globals()["INDEX"] = _saved


def test_mutation_restoring_the_fabricated_zero_kills_a_named_test(tmp_path):
    """R15 on defect B, direction 1: `||0` back on the expected-lifetime render site is
    the page as it was live, printing '0.0 yrs' for a record that says 'not modelled'."""
    src = INDEX.read_text(encoding="utf-8")
    marker = 'yrs(d.expected_lifetime_periods)'
    assert marker in src, "the expected-lifetime render site no longer has this shape"
    mutant = tmp_path / "index.html"
    mutant.write_text(
        src.replace(marker, '(d.expected_lifetime_periods||0).toFixed(1)+" yrs"'), encoding="utf-8"
    )
    _saved, globals()["INDEX"] = INDEX, mutant
    try:
        with pytest.raises(AssertionError, match="renders '0.0 yrs'"):
            test_a_forward_looking_field_published_as_null_never_renders_as_a_number(tmp_path)
    finally:
        globals()["INDEX"] = _saved


def test_mutation_blanking_every_forward_looking_figure_kills_a_named_test(tmp_path):
    """R15 on defect B, direction 2 -- the fail-open the null control INVITES. A page that
    renders every forward-looking figure as a dash satisfies the null check on any book at
    all, while telling the supplier it has no beliefs about any of its customers. Only the
    inverse kills it."""
    src = INDEX.read_text(encoding="utf-8")
    marker = 'function yrs(v){return v==null?NO_BELIEF:Number(v).toFixed(1)+" yrs";}'
    assert marker in src, "the yrs() formatter no longer has the shape this mutation targets"
    mutant = tmp_path / "index.html"
    mutant.write_text(src.replace(marker, "function yrs(v){return NO_BELIEF;}"), encoding="utf-8")
    _saved, globals()["INDEX"] = INDEX, mutant
    try:
        with pytest.raises(AssertionError, match="a real belief has been blanked"):
            test_a_household_that_does_publish_forward_looking_figures_still_renders_them(tmp_path)
    finally:
        globals()["INDEX"] = _saved


# ---------------------------------------------------------------------------
# 16. A lifetime-net figure names WHICH SIDE OF COST-TO-SERVE it is on
#     (coldwalk:site2_lifetime_net_captioned_after_cost_to_serve_is_before_it --
#      the CLASS, completed 2026-08-17)
#
# The 2026-08-12 walk found ONE tile printing lifetime_net_gbp (before cost to serve)
# under an "after cost-to-serve" caption, beside a cost-to-serve tile a reader could
# subtract -- which is what made the exhibit read at ~26% household net margin instead of
# ~12%. That instance was repaired the same day at TWO of the page's FIVE lifetime-net
# render sites, and the repair shipped with NO test at all: the caption could be flipped
# straight back to the defect and nothing went red.
#
# So this section is R10-shaped -- the class, not the instance. The page renders a
# lifetime-net figure in five places (op-state tile, drill-down Overview, drill-down
# Accounts, drill-down Billing, household roll-up); three of the five stated no side, and
# the roll-up -- the HOUSEHOLD figure the finding's own arithmetic was about -- published a
# before-cost-to-serve net under "what these accounts are worth to the supplier" while
# combinedTotals().net_after_cts sat computed and rendered nowhere.
#
# ANTI-PIN: nothing here pins a number. The expected values are read from the SAME
# published per-customer records the page reads, so regenerating the book cannot make this
# cry wolf -- only a figure appearing under the wrong side of cost-to-serve can.
# ---------------------------------------------------------------------------
_BEFORE_CTS = "before cost to serve"
_AFTER_CTS = "after cost to serve"
_NET_BLOCK_CLASSES = {"kpi", "row", "df-cell"}
_BEFORE_LABELS = ("lifetime net margin", "lifetime net (commodity)", "combined net margin")
_AFTER_LABELS = ("net after cost to serve", "combined net after cost to serve")
_MONEY_RE = re.compile(r"-?£\s?([\d,]+(?:\.\d+)?)")


class _BlockText(HTMLParser):
    """Visible text of every leaf money block the page renders (.kpi / .row / .df-cell).

    Reads the RENDERED markup rather than the source, so a qualifier that is written in
    the file but never reaches the page cannot satisfy this control.
    """

    VOID = {"br", "hr", "img", "input", "meta", "link", "source", "col"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.open: list[list] = []
        self.blocks: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in self.VOID:
            return
        self.depth += 1
        if _NET_BLOCK_CLASSES.intersection((dict(attrs).get("class") or "").split()):
            self.open.append([self.depth, []])

    def handle_startendtag(self, tag, attrs):
        return

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        while self.open and self.open[-1][0] >= self.depth:
            _d, buf = self.open.pop()
            self.blocks.append(" ".join("".join(buf).split()))
        self.depth -= 1

    def handle_data(self, data):
        for entry in self.open:
            entry[1].append(data)


def _money_blocks(html: str) -> list[str]:
    p = _BlockText()
    p.feed(html)
    p.close()
    return [b for b in p.blocks if b]


def _lifetime_net_blocks(html: str) -> list[tuple[str, str]]:
    """(declared_side, block_text) for every block rendering a lifetime-net figure.

    `declared_side` is None when the block names no side at all -- which is the state
    three of the five render sites were in, and is a failure, not an absence of one.
    """
    out: list[tuple[str, str]] = []
    for text in _money_blocks(html):
        low = text.lower()
        is_after = any(low.startswith(x) for x in _AFTER_LABELS)
        is_before = (not is_after) and any(low.startswith(x) for x in _BEFORE_LABELS)
        if not (is_after or is_before):
            continue
        if _AFTER_CTS in low:
            side = "after"
        elif _BEFORE_CTS in low:
            side = "before"
        else:
            side = None
        out.append((side, text))
    return out


def _net_expectations() -> tuple[set[float], set[float]]:
    """The values that legitimately belong on each side, from the published records."""
    e, g = _leg_records()
    before = {e["lifetime_net_gbp"], g["lifetime_net_gbp"],
              e["lifetime_net_gbp"] + g["lifetime_net_gbp"]}
    after = {e["lifetime_net_after_cts_gbp"], g["lifetime_net_after_cts_gbp"],
             e["lifetime_net_after_cts_gbp"] + g["lifetime_net_after_cts_gbp"]}
    return before, after


def _check_lifetime_net_sides(blocks: list[tuple[str, str]]) -> None:
    """The predicate, extracted so the R15 mutations below kill the check a NAMED test
    runs rather than re-deriving an equivalent rule inside the mutation."""
    assert blocks, "the page rendered no lifetime-net figure at all -- this control is vacuous"
    unsided = [t for side, t in blocks if side is None]
    assert not unsided, (
        "these lifetime-net figures render without saying which side of cost-to-serve they "
        f"are on, so a reader cannot know what the number is: {unsided}"
    )
    before, after = _net_expectations()
    # The page's two gbp() formatters differ in precision (2dp in the op-state exhibit,
    # 0dp in the drill-down), so a figure is matched to the nearest legitimate value and
    # the SIDE of that match is what is asserted.
    for side, text in blocks:
        m = _MONEY_RE.search(text)
        assert m, f"a lifetime-net block rendered no money value at all: {text}"
        got = float(m.group(1).replace(",", "")) * (-1 if text[m.start()] == "-" else 1)
        want = before if side == "before" else after
        wrong = after if side == "before" else before
        near_right = min(abs(got - c) for c in want)
        near_wrong = min(abs(got - c) for c in wrong)
        assert near_right <= 1.0 and near_right < near_wrong, (
            f"'{text}' is captioned {side} cost to serve but renders {got}, which is the "
            f"{'AFTER' if side == 'before' else 'BEFORE'}-cost-to-serve figure -- this is "
            "the 2026-08-12 cold-eyes finding, restored"
        )


def test_the_two_sides_of_cost_to_serve_are_far_apart_on_this_household():
    """Vacuity guard, first. If cost-to-serve were ~zero the before and after figures would
    coincide and every assertion below would pass on a page that had swapped them."""
    before, after = _net_expectations()
    e, g = _leg_records()
    assert e["cost_to_serve_gbp"] > 1 and g["cost_to_serve_gbp"] > 1, (
        "a leg carries no cost to serve -- before and after are the same number and this "
        "whole section proves nothing"
    )
    for b in before:
        assert min(abs(b - a) for a in after) > 2.0, (
            "a before-cost-to-serve value sits within the match tolerance of an after one; "
            "the side assertion below could not tell them apart"
        )


def test_every_lifetime_net_figure_names_its_cost_to_serve_side(rendered):
    """THE control. Subject is the WHOLE page in the both-sides view -- op-state exhibit
    plus every drill-down tab -- because three of the five render sites live in the region
    an earlier control's subject excluded (section 9's lesson, applied)."""
    _check_lifetime_net_sides(_lifetime_net_blocks(whole_document(rendered, "both")))


def test_the_control_sees_every_lifetime_net_render_site(rendered):
    """Anti-vacuity, and the reason the 2026-08-12 repair was incomplete: it fixed the two
    sites someone happened to be looking at. A scanner that finds fewer sites than the page
    has is how the other three stayed unqualified for five days."""
    blocks = _lifetime_net_blocks(whole_document(rendered, "both"))
    labels = {t.lower().split("£")[0].strip().rstrip("-").strip() for _s, t in blocks}
    for expected in ("lifetime net margin", "lifetime net (commodity)",
                     "combined net margin", "net after cost to serve",
                     "combined net after cost to serve"):
        assert any(x.startswith(expected) for x in labels), (
            f"the scanner no longer sees the '{expected}' render site -- either the page "
            f"stopped rendering it or this control went blind to it. Saw: {sorted(labels)}"
        )


def test_the_household_rollup_publishes_its_net_after_cost_to_serve(rendered):
    """The finding's own arithmetic was about the HOUSEHOLD, not one leg: shown
    1241.48/4815.98 = 25.8% against an actual after-cost-to-serve 12.1%. The roll-up is
    where a reader gets the household figure, and combinedTotals() already computed
    net_after_cts -- it was simply rendered nowhere."""
    e, g = _leg_records()
    want = e["lifetime_net_after_cts_gbp"] + g["lifetime_net_after_cts_gbp"]
    blocks = [t for _s, t in _lifetime_net_blocks(whole_document(rendered, "both"))
              if t.lower().startswith("combined net after cost to serve")]
    assert blocks, "the household roll-up publishes no after-cost-to-serve total"
    m = _MONEY_RE.search(blocks[0])
    got = float(m.group(1).replace(",", "")) * (-1 if blocks[0][m.start()] == "-" else 1)
    assert abs(got - want) <= 1.0, (
        f"the roll-up's after-cost-to-serve total renders {got}; this household's two legs "
        f"publish {round(want, 2)}"
    )


# --- R15, both ways --------------------------------------------------------
def test_mutation_the_original_defect_restored_kills_a_named_test(tmp_path):
    """R15 direction 1: THE 2026-08-12 finding itself, put back. A before-cost-to-serve
    value under an after-cost-to-serve caption -- the exact edit, at the exact site the
    walk found it -- must kill a named test. Before this section shipped, it did not."""
    src = INDEX.read_text(encoding="utf-8")
    marker = 'return "<span class=\\"muted\\">"+(which==="after"?"after cost to serve":"before cost to serve")+"</span>";'
    assert marker in src, "ctsSide() no longer has the shape this mutation reverts"
    mutant = tmp_path / "index.html"
    mutant.write_text(
        src.replace(marker, 'return "<span class=\\"muted\\">after cost to serve</span>";'),
        encoding="utf-8",
    )
    blocks = _lifetime_net_blocks(whole_document(_drive(mutant, tmp_path), "both"))
    with pytest.raises(AssertionError, match="restored"):
        _check_lifetime_net_sides(blocks)


def test_mutation_dropping_the_qualifier_kills_a_named_test(tmp_path):
    """R15 direction 2: the state three of the five sites were actually in -- no caption at
    all. Silence is not a safe default here; a bare 'Lifetime Net Margin £493' beside a
    'Cost to Serve £330' is exactly what a reader mis-reads."""
    src = INDEX.read_text(encoding="utf-8")
    marker = 'return "<span class=\\"muted\\">"+(which==="after"?"after cost to serve":"before cost to serve")+"</span>";'
    assert marker in src, "ctsSide() no longer has the shape this mutation reverts"
    mutant = tmp_path / "index.html"
    mutant.write_text(src.replace(marker, 'return "";'), encoding="utf-8")
    blocks = _lifetime_net_blocks(whole_document(_drive(mutant, tmp_path), "both"))
    with pytest.raises(AssertionError, match="which side of cost-to-serve"):
        _check_lifetime_net_sides(blocks)


# ===========================================================================
# 17. THE LANDING DOCUMENT (cold-eyes 2026-08-17, the re-run walk)
# ===========================================================================
# The walk that was the named L3 gate returned NO, and both structural findings were in
# the one region every control above structurally excluded: the page AS IT BOOTS.
#
#   coldwalk:site2_case_study_cards_render_sim_truth_in_the_customer_view
#     "The customer's side" rendered "sim 3.2% vs company 95.0%", "True satisfaction fell
#     12.2 percentage points" and "Real downstream drift" -- under the view's own sentence
#     "No company estimate and no simulation ground truth is in this view; if one appears,
#     the page is broken". All three blindfolded personas led with it independently.
#   coldwalk:site2_wall_view_selector_throws_in_its_own_landing_state
#     every click of the three view buttons on the landing page raised
#     "Cannot read properties of null (reading 'segment')".
#
# WHY 97 TESTS WERE GREEN AGAINST THAT PAGE, which is the reusable half. Every fixture in
# sections 1-16 assigns a fully populated household before it drives anything:
# `_wall_harness.mjs` sets `sandbox.HH` and only then calls setWallView. So no subject in
# this module could contain either defect -- one lives in the branch taken when HH is
# empty, the other in a component appended to #app by a path neither layoutPanels() nor
# applyWallViewToOpState() can see. This is the SAME class as 2026-08-12 ("a new layer
# above a control must inherit its subject"), caught a second time, in the same module.
#
# So this section's SUBJECT is the rendered #app document in the boot state, via
# `_landing_harness.mjs`, driven through the page's own showLogin()/setWallView().
#
# ANTI-PIN: the leak strings are read from site/data/case_studies.json, not typed here, so
# regenerating the book changes what is checked rather than making these cry wolf.
LANDING_HARNESS = HERE / "_landing_harness.mjs"
CASE_STUDIES_PATH = HERE.parent / "data" / "case_studies.json"


def _landing(index: Path = INDEX) -> dict:
    proc = subprocess.run(
        [NODE, str(LANDING_HARNESS), str(index), str(CASE_STUDIES_PATH)],
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, f"landing harness failed: {proc.stderr}"
    return json.loads(proc.stdout)


def _cases() -> list[dict]:
    cases = json.loads(CASE_STUDIES_PATH.read_text(encoding="utf-8"))["cases"]
    assert cases, "no curated cases on disk -- every assertion below would be vacuous"
    return cases


def _check_no_behind_the_wall_case_in_the_customer_view(landing: dict) -> None:
    """The named check. Kept as a function so a mutant page can be pushed through the
    SAME assertion, which is what makes the mutation tests below name a real test."""
    customer = landing["views"]["customer"]
    leaked = [c for c in _cases()
              if c.get("wall_side") != "customer" and c["headline"] in customer]
    assert not leaked, (
        "the customer's view of the landing document publishes curated headlines that are "
        "not customer-observable -- the page's own sentence says that means it is broken: "
        + "; ".join(f"[{c.get('wall_side')}] {c['category']}" for c in leaked)
    )


def test_the_view_selector_does_not_throw_in_the_pages_own_landing_state():
    """coldwalk:site2_wall_view_selector_throws_in_its_own_landing_state. The landing page
    IS the page's home state; every visitor who touches a view button is in it."""
    landing = _landing()
    threw = {v: m for v, m in landing["threw"].items() if m}
    assert not threw, f"setWallView threw on the landing page: {threw}"


def test_the_customer_view_of_the_landing_document_carries_no_behind_the_wall_case():
    """coldwalk:site2_case_study_cards_render_sim_truth_in_the_customer_view."""
    _check_no_behind_the_wall_case_in_the_customer_view(_landing())


def test_every_curated_card_declares_a_side_the_page_knows():
    """Structural, per the ruling's non-negotiable: a curated card whose side nobody chose
    cannot be filtered, so it must not be publishable at all."""
    undeclared = [c["category"] for c in _cases() if c.get("wall_side") not in SIDES]
    assert not undeclared, (
        f"curated cards declare no side the wall knows: {undeclared} -- "
        "tools/generate_case_study_recommender.py must choose one"
    )


def test_the_behind_the_wall_view_still_publishes_every_curated_card():
    """ANTI-VACUITY for the two tests above: if the grid simply stopped rendering, the
    leak check would pass for the wrong reason and the exhibit would have lost a feature.
    Every card must survive somewhere."""
    landing = _landing()
    missing = [c["category"] for c in _cases() if c["headline"] not in landing["views"]["behind"]]
    assert not missing, f"curated cards vanished from the behind-the-wall view: {missing}"
    assert landing["views"]["customer"] != landing["views"]["both"], (
        "the customer view and the both-sides view render identically -- the selector is "
        "not governing this region at all"
    )


def test_an_undeclared_block_bolted_onto_the_document_is_withheld_and_recorded():
    """The class fix, not the instance. The case-study grid leaked because it was appended
    to #app by a third path; the guard's subject is now the document, so ANY top-level
    block that declares neither a side nor chrome is removed and recorded."""
    probes = _landing()["probes"]
    assert probes["undeclared_block_withheld"], (
        "a block bolted onto #app with no declared side survived into the customer's view"
    )
    assert probes["undeclared_block_recorded"], (
        "the undeclared block was withheld silently -- a fail-closed control that says "
        "nothing is how the 2026-08-12 repair shipped at 2 of 5 sites"
    )
    assert probes["unknown_side_block"] and "marketing" in probes["unknown_side_block"], (
        "a block declaring a side the wall does not know must be refused, not filtered"
    )


def test_a_case_with_no_declared_side_is_withheld_rather_than_published():
    probes = _landing()["probes"]
    assert "cs-card" not in probes["undeclared_case_html"], (
        "cards with no declared side were published anyway"
    )
    assert len(probes["undeclared_case_drops"]) == len(_cases()), (
        "the page did not record every withheld card"
    )


# --- R15, both defects, both directions ------------------------------------
def _mutate(tmp_path: Path, marker: str, replacement: str) -> Path:
    src = INDEX.read_text(encoding="utf-8")
    assert marker in src, f"the page no longer has the shape this mutation reverts: {marker!r}"
    mutant = tmp_path / "index.html"
    mutant.write_text(src.replace(marker, replacement), encoding="utf-8")
    return mutant


def test_mutation_the_landing_leak_restored_kills_a_named_test(tmp_path):
    """R15 direction 1: the 2026-08-17 finding itself, put back -- the curated grid stops
    obeying the view. Proven to fire: run against the pre-fix page this raises with all
    six cards named."""
    mutant = _mutate(tmp_path, '    if(!wallViewShows(side))return "";',
                     '    if(false)return "";')
    with pytest.raises(AssertionError, match="not customer-observable"):
        _check_no_behind_the_wall_case_in_the_customer_view(_landing(mutant))


def test_mutation_treating_an_undeclared_case_as_customer_observable_kills_a_named_test(tmp_path):
    """R15 direction 2: the fail-OPEN version of the same control -- a card with no
    declared side defaults to the customer's side instead of being withheld. This is the
    state the page was actually in (no card declared anything), so the mutation is the
    defect, not a hypothetical."""
    mutant = _mutate(
        tmp_path,
        '    if(!side||!WALL_SIDES[side]){dropped.push(String((c&&c.category)||"?"));return "";}',
        '    if(!side||!WALL_SIDES[side]){side="customer";}',
    )
    probes = _landing(mutant)["probes"]
    assert "cs-card" in probes["undeclared_case_html"], (
        "the mutation did not reach the page -- this test would be vacuous"
    )
    with pytest.raises(AssertionError, match="published anyway"):
        assert "cs-card" not in probes["undeclared_case_html"], (
            "cards with no declared side were published anyway"
        )


def test_mutation_restoring_the_unconditional_household_render_kills_a_named_test(tmp_path):
    """R15 for the second finding: setWallView calling renderHousehold() with no household
    open -- the exact line, reverted -- must kill a named test. Before this section
    shipped it did not, because no fixture had ever occupied the boot state."""
    mutant = _mutate(
        tmp_path,
        "  if(hasHousehold())renderHousehold();else renderCaseStudies();",
        "  renderHousehold();",
    )
    threw = {v: m for v, m in _landing(mutant)["threw"].items() if m}
    assert threw, "the mutation did not reach the page -- this test would be vacuous"
    assert all("segment" in m for m in threw.values()), threw


def test_mutation_letting_an_undeclared_block_through_kills_a_named_test(tmp_path):
    """R15 for the class guard itself: drop the fail-closed branch and the bolted-on block
    -- the shape the case-study grid had -- survives into the customer's view."""
    mutant = _mutate(tmp_path, "    if(!side&&!chromeFlag){", "    if(false){")
    probes = _landing(mutant)["probes"]
    assert not probes["undeclared_block_withheld"], (
        "the mutation did not reach the page -- this test would be vacuous"
    )


# ===========================================================================
# 18. THE COLLECTIONS RECORD HAS ONE PRODUCER, NOT TWO
#     (coldwalk:site2_arrears_counters_contradict_the_accounts_own_timeline)
#
# The money panel published "FAILED PAYMENTS 0 - direct-debit returns", "PAYS BY direct
# debit" and "No arrears cases on this account's electricity record" directly above the
# same household's own two complete four-step arrears cascades, whose rows read "Standard
# credit payment not received". All three claims came from company.json's `household`
# block -- ONE LEG, commodity='electricity' -- while the cascades come from the per-leg
# reaction chains the Timeline tab renders. Two producers of one fact, published side by
# side, never reconciled. MAJOR, all three blind personas, and the 2026-08-13 repair that
# moved arrears onto the customer's side of the wall is what left the clean claim stranded
# in the panel whose own footnote boasts about having fixed it.
#
# The rule these tests pin is a PRODUCER rule, not a value rule: every collections claim
# on this panel is derived by __householdCollections() from the legs the page itself
# fetched, so no claim can contradict the record rendered below it. The company.json block
# is not thrown away -- it is reconciled leg-to-leg and a disagreement is PUBLISHED.
#
# Each predicate is extracted so an R15 mutation kills the CHECKER a named test runs,
# rather than re-deriving an equivalent check inside the mutation.
# ===========================================================================
_ARREARS_OPENERS = {
    "arrears_dd_failed",
    "arrears_payment_missed",
    "arrears_invoice_disputed",
}
# Every claim on the panel that asserts something about how this household pays.
_COLLECTIONS_PANELS = ("cust-money", "cust-arrears", "cust-who")
# The phrases that assert a clean record. A page may say any of these ONLY when every leg
# it holds is actually clean.
#
# CHOSEN FROM THE DEFECT'S VOCABULARY, NOT THE FIX'S. The first draft of this list held the
# repaired page's own wordings and PASSED against `git show HEAD:site/customers/index.html`
# -- the shipped defect said "No arrears cases on this account's electricity record", which
# matched none of them. A leak list written by reading the fix is a control whose subject
# was chosen by convenience. These are deliberately the widest form of each claim, and the
# page's per-leg breakdown says "<fuel> leg -- none" precisely so a scoped line cannot
# collide with the household-wide claim this list forbids.
_CLEAN_CLAIMS = ("clean payment history", "no missed payment", "no arrears case")


def _household_legs() -> list[tuple[str, tuple[Path, ...]]]:
    """Every published household as (base id, its OWN legs) -- one path for a single-fuel
    account, two for a dual-fuel one.

    Deliberately NOT `_published_households()`: that helper duplicates the electricity leg
    to fill a fixed two-slot harness signature, which would double-count this section's
    subject (an account's arrears events would be read twice) and would make every
    single-fuel household render as an incomplete two-leg load.
    """
    legs: dict[str, dict[str, Path]] = {}
    for path in sorted(CUSTOMER_DATA.glob("*.json")):
        if path.name.startswith("_"):
            continue
        rec = json.loads(path.read_text(encoding="utf-8"))
        acct = rec.get("account_id") or path.stem
        base = acct[:-1] if acct.endswith("g") else acct
        legs.setdefault(base, {})["gas" if rec.get("commodity") == "gas" else "elec"] = path
    out: list[tuple[str, tuple[Path, ...]]] = []
    for base, pair in sorted(legs.items()):
        ordered = tuple(p for k in ("elec", "gas") if (p := pair.get(k)) is not None)
        out.append((base, ordered))
    assert out, "no published households at all -- every assertion in this section is vacuous"
    return out


def _openers_in(path: Path) -> list[dict]:
    """The arrears cases a leg publishes, counted INDEPENDENTLY of the page.

    A case is counted by its OPENER: C4 and C7 publish interleaved cascades (a second miss
    opens before the first resolves), so pairing a ladder start to a ladder end would
    silently merge or split real cases. This is derived here from the published record,
    never read back out of the page's own helper -- a test that called
    __householdCollections() to decide what __householdCollections() should say would be
    grading its own copy.
    """
    rec = json.loads(path.read_text(encoding="utf-8"))
    return [e for e in rec.get("reaction_chain") or []
            if str(e.get("event_type")) in _ARREARS_OPENERS]


def _channels_in(path: Path) -> list[str]:
    rec = json.loads(path.read_text(encoding="utf-8"))
    out: list[str] = []
    for e in (rec.get("ledger") or {}).get("entries") or []:
        if e.get("type") == "payment_received" and e.get("method") and e["method"] not in out:
            out.append(str(e["method"]))
    return out


def _collections_text(index: Path = INDEX, legs: tuple[Path, ...] | None = None,
                      company: str | None = None) -> str:
    """Everything the panel says about how this household pays, as ONE subject.

    The union matters: the defect was a clean claim in the money panel beside real cases
    in the arrears block. A check whose subject is either block alone cannot see it -- the
    wrong-subject class this module has now paid for three times.
    """
    rendered = _op_state_render(index, legs, company)
    text = " ".join(rendered.get(p, "") for p in _COLLECTIONS_PANELS)
    assert text.strip(), "the collections panels rendered nothing -- every check below is vacuous"
    return text


def _check_no_clean_claim_over_a_leg_with_arrears(text: str, cases: int, who: str) -> None:
    if not cases:
        return
    said = [c for c in _CLEAN_CLAIMS if c in text.lower()]
    assert not said, (
        f"{who}: the exhibit publishes {said} while this household's own legs carry {cases} "
        "arrears case(s) -- the same record the Timeline tab renders directly below it"
    )


def _check_missed_count_is_every_leg(tiles: dict[str, tuple[str, str]], cases: int, who: str) -> None:
    assert "Payments missed" in tiles, (
        f"{who}: the exhibit no longer renders a 'Payments missed' tile at all"
    )
    got = tiles["Payments missed"][0].strip()
    assert got == str(cases), (
        f"{who}: the tile publishes '{got}' missed payments, but this household's legs "
        f"carry {cases} arrears case(s) -- a leg-scoped counter is wearing a household caption"
    )


# --- the population, before anything is asserted over it --------------------
def test_the_published_book_carries_both_a_household_with_arrears_and_one_without():
    """VACUITY GUARD, first. If no published household had arrears on a leg the company
    block does not cover, the clean-claim control would pass over a page that never
    suppresses a clean claim; if none were clean on every leg, the anti-vacuity leg below
    would pass over a page that never MAKES one. Both halves must exist in the real book."""
    dirty, clean = [], []
    for base, legs in _household_legs():
        (dirty if sum(len(_openers_in(p)) for p in legs) else clean).append(base)
    assert dirty, "no published household carries an arrears case -- this whole section is vacuous"
    assert clean, "every published household carries arrears -- the clean-claim leg is vacuous"


def test_the_fixture_households_arrears_are_on_a_leg_the_company_block_does_not_cover():
    """The finding's own shape, pinned against the data rather than restated. company.json
    publishes ONE leg of C1; the cases are on the OTHER one. That asymmetry is what made a
    correctly-derived single-leg counter into a false household claim, so if the book ever
    stops having it, this section is testing a defect that can no longer occur."""
    block = json.loads(COMPANY_DATA.read_text(encoding="utf-8"))["household"]
    elec, gas = _dual_fuel_pair()
    assert block["commodity"] == "electricity", "the household block is no longer the electricity leg"
    assert not _openers_in(elec), "the electricity leg now carries arrears -- the asymmetry is gone"
    assert _openers_in(gas), "the gas leg carries no arrears -- the contradiction cannot arise"
    assert block.get("failed_payment_count") == 0, (
        "the block no longer publishes a zero failed-payment count -- the finding's own instance is gone"
    )


# --- THE control ------------------------------------------------------------
@pytest.mark.parametrize("base,legs", _household_legs(), ids=[b for b, _ in _household_legs()])
def test_no_clean_payment_claim_survives_a_leg_that_carries_arrears(base, legs):
    """THE control, driven over EVERY published household rather than the one the walk
    named. A clean claim on this panel must be unreachable while any leg the page holds
    publishes an arrears case."""
    cases = sum(len(_openers_in(p)) for p in legs)
    _check_no_clean_claim_over_a_leg_with_arrears(_collections_text(legs=legs), cases, base)


@pytest.mark.parametrize("base,legs", _household_legs(), ids=[b for b, _ in _household_legs()])
def test_the_missed_payment_count_covers_every_leg_the_household_has(base, legs):
    """The value half: the counter equals the household's own arrears openers, computed
    here from the published records rather than from company.json's single-leg block --
    which is the thing being corrected."""
    cases = sum(len(_openers_in(p)) for p in legs)
    _check_missed_count_is_every_leg(_money_tiles(legs=legs), cases, base)


def test_a_household_clean_on_every_leg_still_gets_its_clean_claim():
    """ANTI-VACUITY for the control above. A page that simply deleted the words 'clean
    payment history' would pass every leak check for the wrong reason. Some household must
    still be told, in plain words, that its record is clean."""
    for base, legs in _household_legs():
        if sum(len(_openers_in(p)) for p in legs):
            continue
        text = _collections_text(legs=legs).lower()
        assert any(c in text for c in _CLEAN_CLAIMS), (
            f"{base} has no arrears on any leg and the panel says so nowhere -- the "
            f"suppression is unconditional, not conditional: {text[:400]}"
        )
        return
    pytest.fail("no clean household to drive -- guarded by the population test above")


def _check_payment_channels_named(value: str | None, want: list[str]) -> None:
    assert value is not None, "the exhibit no longer renders a 'Pays by' tile"
    missing = [c for c in want if c.replace("_", " ") not in value]
    assert not missing, (
        f"'Pays by' renders '{value}' but this household actually pays by {want} across its "
        f"legs -- a single-leg fact is wearing a household caption (missing: {missing})"
    )


def test_the_payment_channel_names_every_channel_the_household_actually_uses():
    """The compounding half the walk named: 'PAYS BY direct debit' sat above arrears rows
    reading 'Standard credit payment not received'. Both are true of ONE LEG each, and the
    block published the first as the household's."""
    elec, gas = _dual_fuel_pair()
    want = _channels_in(elec) + [c for c in _channels_in(gas) if c not in _channels_in(elec)]
    assert len(want) > 1, (
        "this household's legs now pay the same way -- the finding's own instance is gone "
        "and this test can no longer fail"
    )
    who = _op_state_render(legs=(elec, gas))["cust-who"]
    _check_payment_channels_named(_rendered_value(who, "Pays by"), want)


def _check_no_household_wide_claim_on_partial_load(text: str) -> None:
    assert "not a household-wide claim" in text, (
        "one leg loaded and the panel still made a household-scoped collections claim: "
        f"{text[:500]}"
    )
    assert "clean payment history" not in text.lower(), (
        "a partial load rendered 'clean payment history' -- the claim covers legs it never read"
    )


def test_an_incomplete_leg_load_publishes_no_household_wide_collections_claim():
    """The fail-open direction. If a leg does not load, the panel must not answer the
    household question at all -- a clean claim assembled from the legs that happened to
    arrive is the original defect with a different cause."""
    elec, _gas = _dual_fuel_pair()
    _check_no_household_wide_claim_on_partial_load(_collections_text(legs=(elec,)))


# --- the two producers, reconciled in public --------------------------------
def _swapped_company(commodity: str = "electricity") -> str:
    """The real company.json, whose household block keeps its own published counters. It
    is then driven against ANOTHER household's legs -- the 'swap the belief between two
    units' shape -- so the two producers genuinely disagree without either being faked."""
    blob = json.loads(COMPANY_DATA.read_text(encoding="utf-8"))
    blob["household"]["commodity"] = commodity
    return json.dumps(blob)


def _disagreeing_legs() -> tuple[str, tuple[Path, ...]]:
    block = json.loads(COMPANY_DATA.read_text(encoding="utf-8"))["household"]
    want = int(block["arrears_case_count"])
    for base, legs in _household_legs():
        elec = legs[0]
        if len(_openers_in(elec)) != want:
            return base, legs
    pytest.fail("no published household's electricity leg disagrees with the block's count")


def test_the_two_producers_are_reconciled_in_public_when_they_disagree():
    """The class mechanism. The page carries two records of one fact. Where they disagree
    it must SAY they disagree and name both -- never silently prefer either, which is what
    publishing the block's counter alone had been doing."""
    base, legs = _disagreeing_legs()
    text = _collections_text(legs=legs, company=_swapped_company())
    assert "Two company records of one fact, and they disagree" in text, (
        f"driven against {base}'s legs, the block's counter and the legs' own chains "
        f"disagree and the page publishes no reconciliation at all: {text[:600]}"
    )


def _check_no_reconciliation_when_they_agree(text: str) -> None:
    assert "Two company records of one fact" not in text, (
        "the reconciliation note fires on a household whose two producers agree -- it is "
        f"unconditional, so its firing carries no information: {text[:600]}"
    )


def test_the_reconciliation_note_is_silent_when_the_two_producers_agree():
    """The inverse, and the one that stops the note being decoration. On the real published
    pairing the block and the electricity leg AGREE (0 and 0), so a page that printed the
    disagreement unconditionally would be crying wolf on its own front door."""
    _check_no_reconciliation_when_they_agree(_collections_text(legs=_dual_fuel_pair()))


def test_an_unclassified_arrears_event_refuses_the_count_rather_than_undercounting(tmp_path):
    """FAIL-CLOSED, and the reason this direction matters more than usual: an arrears event
    the page cannot classify does not render as an undercount, it renders as a CLEAN
    PAYMENT HISTORY. Refusing is the only honest failure mode here."""
    elec, gas = _dual_fuel_pair()
    rec = json.loads(gas.read_text(encoding="utf-8"))
    rec["reaction_chain"].append({
        "customer_id": "C1", "date": "2020-05-05", "event_type": "arrears_meter_disconnected",
        "description": "unclassified", "amount_gbp": 10.0, "outcome": "X",
    })
    mutant = tmp_path / "C1g.json"
    mutant.write_text(json.dumps(rec), encoding="utf-8")
    text = _collections_text(legs=(elec, mutant))
    assert "arrears_meter_disconnected" in text, (
        "an arrears event type the page does not classify was silently dropped from the "
        f"count instead of refusing it by name: {text[:600]}"
    )
    assert "clean payment history" not in text.lower(), (
        "the refusal path still published a clean claim -- the worst direction to fail in"
    )


# --- R15, every direction the class can fail in ----------------------------
def _mutant_index(tmp_path: Path, old: str, new: str) -> Path:
    src = INDEX.read_text(encoding="utf-8")
    assert old in src, f"the page no longer has the shape this mutation reverts: {old[:80]}"
    out = tmp_path / "index.html"
    out.write_text(src.replace(old, new, 1), encoding="utf-8")
    return out


def test_mutation_reading_the_counter_off_the_single_leg_block_kills_a_named_test(tmp_path):
    """R15 direction 1: THE ORIGINAL DEFECT, restored -- the tile reads company.json's
    single-leg failed_payment_count again. The value check must kill it by name."""
    mutant = _mutant_index(
        tmp_path,
        '    return tile("Payments missed",String(col.total),sub,(col.total>0?"amber":""));',
        '    return tile("Payments missed",String(h.failed_payment_count),sub,"");',
    )
    elec, gas = _dual_fuel_pair()
    with pytest.raises(AssertionError, match="a leg-scoped counter is wearing a household caption"):
        _check_missed_count_is_every_leg(
            _money_tiles(mutant, legs=(elec, gas)), len(_openers_in(gas)), "C1")


def test_mutation_restoring_the_unconditional_clean_claim_kills_a_named_test(tmp_path):
    """R15 direction 2: the CLAIM half, which no value check can see. Make the clean branch
    reachable whatever the legs carry -- the exact state the page shipped in -- and the
    counter can stay right while the sentence beside it stays wrong."""
    mutant = _mutant_index(tmp_path, "} else if(col&&col.total){", "} else if(false){")
    elec, gas = _dual_fuel_pair()
    text = _collections_text(mutant, legs=(elec, gas))
    assert "clean payment history" in text.lower(), (
        "this mutation was meant to restore the clean claim and did not reach the page"
    )
    with pytest.raises(AssertionError, match="the exhibit publishes"):
        _check_no_clean_claim_over_a_leg_with_arrears(text, len(_openers_in(gas)), "C1")


def test_mutation_counting_only_the_first_leg_kills_a_named_test(tmp_path):
    """R15 direction 3: the SCOPE half. Derive from the legs, as the fix does, but stop at
    the first one -- which for this household is the clean electricity leg, so the page
    lands straight back on 'no missed payment' beside two live cascades."""
    mutant = _mutant_index(
        tmp_path,
        "    var acc=((legs&&legs.accounts)||[]).filter(Boolean);\n    if(!acc.length)return null;\n    var out={complete:acc.length===((legs&&legs.expected)||0),count:acc.length,",
        "    var acc=((legs&&legs.accounts)||[]).filter(Boolean).slice(0,1);\n    if(!acc.length)return null;\n    var out={complete:acc.length===((legs&&legs.expected)||0),count:acc.length,",
    )
    elec, gas = _dual_fuel_pair()
    with pytest.raises(AssertionError, match="a leg-scoped counter is wearing a household caption"):
        _check_missed_count_is_every_leg(
            _money_tiles(mutant, legs=(elec, gas)), len(_openers_in(gas)), "C1")


def test_mutation_failing_open_on_an_unclassified_event_kills_a_named_test(tmp_path):
    """R15 direction 4: the refusal itself. Drop the fail-closed flag and an arrears event
    the page cannot classify is dropped from the count in silence -- which for a household
    whose only cases were unclassified would render as a clean payment history."""
    mutant = _mutant_index(tmp_path, "    out.refused=out.unknown.length>0;", "    out.refused=false;")
    elec, gas = _dual_fuel_pair()
    rec = json.loads(gas.read_text(encoding="utf-8"))
    rec["reaction_chain"] = [e for e in rec["reaction_chain"]
                             if not str(e.get("event_type", "")).startswith("arrears")]
    rec["reaction_chain"].append({
        "customer_id": "C1", "date": "2020-05-05", "event_type": "arrears_meter_disconnected",
        "description": "unclassified", "amount_gbp": 10.0, "outcome": "X",
    })
    stripped = tmp_path / "C1g.json"
    stripped.write_text(json.dumps(rec), encoding="utf-8")
    text = _collections_text(mutant, legs=(elec, stripped))
    assert "clean payment history" in text.lower(), (
        "the fail-open mutation did not reach the page -- this test would be vacuous"
    )
    assert "arrears_meter_disconnected" not in text, (
        "the mutation was meant to silence the refusal and the page still named the event"
    )


def test_mutation_an_unconditional_reconciliation_note_kills_a_named_test(tmp_path):
    """R15 direction 5: the reconciliation. A note that always fires reports nothing, and
    would let a real disagreement hide inside permanent noise."""
    mutant = _mutant_index(
        tmp_path,
        "    if(Number(h.arrears_case_count)===leg.cases)return \"\";",
        "    if(false)return \"\";",
    )
    text = _collections_text(mutant, legs=_dual_fuel_pair())
    with pytest.raises(AssertionError, match="unconditional, so its firing carries no information"):
        _check_no_reconciliation_when_they_agree(text)


def test_every_check_in_this_section_fires_on_the_page_as_it_shipped(tmp_path):
    """R15's own subject: the SHIPPED DEFECT, not a synthetic mutation of the repair.

    Each mutation above reverts one mechanism. This drives all four checkers against the
    page exactly as it was published -- `git show HEAD~:site/customers/index.html`, or the
    committed parent once this lands -- and requires every one of them to fire. It is the
    test that caught the first draft of _CLEAN_CLAIMS: those phrases were read off the
    REPAIR, so the leak check passed against a page that published "No arrears cases on
    this account's electricity record" above two live cascades.

    FAILS rather than skips when the pre-repair revision cannot be found (2026-08-19): it
    used to walk a fixed ancestor window, scrolled past it, and skipped for an unknown
    number of ticks while its mutation siblings reported green. A control that silently
    passes when its subject is unavailable is a FAILED control (R15), and a skip reads as
    a pass to everything that looks at this suite.
    """
    src = _pre_repair_source("__householdCollections")
    assert src is not None, (
        "cannot locate the committed index.html that predates __householdCollections -- "
        "the shipped-defect proof did NOT run, which is not the same as passing"
    )
    shipped = tmp_path / "index.html"
    shipped.write_text(src, encoding="utf-8")

    elec, gas = _dual_fuel_pair()
    cases = len(_openers_in(gas))
    assert cases, "the fixture household has no arrears -- this proof would be vacuous"
    text = _collections_text(shipped, legs=(elec, gas))

    with pytest.raises(AssertionError, match="the exhibit publishes"):
        _check_no_clean_claim_over_a_leg_with_arrears(text, cases, "C1")
    with pytest.raises(AssertionError, match="Payments missed"):
        _check_missed_count_is_every_leg(_money_tiles(shipped, legs=(elec, gas)), cases, "C1")
    want = _channels_in(elec) + [c for c in _channels_in(gas) if c not in _channels_in(elec)]
    with pytest.raises(AssertionError, match="wearing a household caption"):
        _check_payment_channels_named(
            _rendered_value(_op_state_render(shipped, legs=(elec, gas))["cust-who"], "Pays by"), want)
    with pytest.raises(AssertionError, match="household-scoped collections claim"):
        _check_no_household_wide_claim_on_partial_load(_collections_text(shipped, legs=(elec,)))


# ===========================================================================
# 19. ONE ACCOUNT, ONE STANDING CLAIM
#     (coldwalk:site2_closed_account_settled_to_zero_and_in_credit)
# ===========================================================================
#
# THE FINDING, all three blind personas, and it survived the 2026-08-15 present-tense
# repair. One household -- C1, closed 2021-12-30 -- and the page published, at once:
#
#   Billing tab   "Account closed 2021-12-30 -- final bill C1-INV72. Account settled to zero."
#   Overview      "You are currently £24.37 in credit -- that is your money, held by us"
#   Risk tab      "the household combined (both fuels) LIVE ledger position", under a
#                 header stamped "data 2026-08-17"
#
# The arithmetic was never wrong: 6,560.17 - 6,584.54 = -24.37, the credit sitting entirely
# on the gas leg. It is a STATEMENT contradiction, and the reading a blind COO reached for
# first is a supplier holding a departed customer's credit balance for four and a half
# years. Either the closed account settled to zero or it did not; the page published both.
#
# TWO DEFECTS, ONE CLASS -- four sentence sites each deciding privately what to claim
# about the same money:
#   1. TENSE. Three sites were hard-wired present tense on a household the page's own
#      timeline knows has gone. fwdLabel() had frozen every forward-looking LABEL since
#      2026-08-12; the MONEY sentences were never brought under it.
#   2. A MISSING BRANCH, and this one is a literal falsehood rather than a tense problem.
#      closedAccountNotice() tested `current_balance_gbp > 0.005` and otherwise printed
#      "Account settled to zero" -- so a CREDIT balance, being negative, fell through to
#      the zero branch. On C1's GAS tab that claim sat over a ledger reading -£24.37.
#      No fixture in this module could see it: every one drove the electricity leg.
#
# THE FIX IS A SOLE WRITER, not four repaired sentences (R10). window.__accountStanding
# decides state, tense and words from one input, and all four sites ask it -- including
# across the two inline scripts, which is why both harnesses now run both scripts.
#
# WHAT THE PAGE STILL CANNOT KNOW. Nothing published here records whether that closing
# credit was refunded. The finding's own note says its resolution needs a fact the page
# does not carry, and inventing it -- either way -- is exactly the inference-printed-as-
# fact this exhibit exists to make visible. So the page states the closing position and
# states that the refund is not in the record, and the control below REQUIRES that
# statement rather than allowing silence.
#
# R15 five ways: the credit branch removed, the writer made closure-blind, the writer made
# always-closed (the tautology that would satisfy the closed-account direction by telling
# every live customer they had left), the writer silenced entirely (fail-open), and the
# page exactly as it shipped.
# ---------------------------------------------------------------------------

# Present-tense standing claims. Each is a live-account assertion about where money stands.
_LIVE_STANDING_PHRASES = (
    "You are currently",
    "Your account is currently",
    "live ledger position",
)
_SETTLED_CLAIM = "settled to zero"
_NO_REFUND_RECORD = "records whether that credit was refunded"


def _leg_balance(leg: Path) -> float:
    return float((json.loads(leg.read_text(encoding="utf-8")).get("ledger") or {})
                 .get("current_balance_gbp") or 0.0)


def _bills_by_fuel(index: Path, tmp: Path, legs: tuple[Path, Path]) -> dict[str, str]:
    """The Billing tab as rendered for EACH fuel leg -- the region the settlement claim
    lives in, and the one every fixture in this module was blind to before this section."""
    proc = _run(index, legs[0], legs[1], tmp)
    assert proc.returncode == 0, f"harness failed on {legs[0].name}: {proc.stderr}"
    out = json.loads(proc.stdout)
    bills = {k: v for k, v in (out.get("billsByFuel") or {}).items() if v}
    assert bills, "the harness rendered no billing tab at all -- these checks would be vacuous"
    return bills


def _standing_document(index: Path, tmp: Path, legs: tuple[Path, Path]) -> str:
    """Every region that makes a claim about where this household's money stands: the
    drill-down's own tabs, the per-fuel billing tabs, and the static op-state exhibit's
    money and Direct-Debit panels. A subject smaller than this is how the contradiction
    survived -- the two halves of it were rendered by two different scripts."""
    proc = _run(index, legs[0], legs[1], tmp)
    assert proc.returncode == 0, f"harness failed on {legs[0].name}: {proc.stderr}"
    out = json.loads(proc.stdout)
    doc = "".join(out["views"]["both"].values())
    doc += "".join(v or "" for v in (out.get("billsByFuel") or {}).values())
    op = _op_state_render(index, legs=legs)
    doc += "".join(op.get(k, "") for k in ("cust-money", "cust-dd-cycle"))
    assert doc.strip(), "nothing rendered -- every assertion below would be vacuous"
    return doc


# The predicates, extracted so each R15 mutation kills the checker a NAMED test runs.
def _check_no_settlement_claim_over_a_non_zero_ledger(bills: dict[str, str],
                                                      balances: dict[str, float]) -> None:
    bad = {f: balances[f] for f, html in bills.items()
           if _SETTLED_CLAIM in html and abs(balances.get(f, 0.0)) > 0.005}
    assert not bad, (
        "the page claims the account 'settled to zero' on a leg whose own published ledger "
        f"is not zero: {bad} -- either the closed account settled or it did not, and this "
        "publishes both"
    )


def _check_no_live_standing_claim_on_a_closed_household(doc: str) -> None:
    found = sorted({p for p in _LIVE_STANDING_PHRASES if p in doc})
    assert not found, (
        "this household has closed its account, and the page still states where its money "
        f"stands in the present tense: {found} -- a departed customer's closing balance is "
        "not a live position, and reading it as one is a supplier holding their money today"
    )


def _check_the_live_standing_claim_is_made_on_a_live_household(doc: str) -> None:
    assert any(p in doc for p in _LIVE_STANDING_PHRASES), (
        "this household has NOT closed its account, yet the page makes no present-tense "
        "statement about where its money stands -- a writer that says 'at closure' about "
        "everything would satisfy the closed-account control while telling every live "
        "account holder they had left"
    )
    assert "closed on" not in doc and "at closure" not in doc, (
        "this household has NOT closed its account, yet the page describes its balance as "
        "a position at closure"
    )


def _check_a_closing_credit_says_the_refund_is_unrecorded(doc: str) -> None:
    assert _NO_REFUND_RECORD in doc, (
        "this household closed while in credit and the page does not say whether that "
        "money was refunded -- the record does not carry the answer, so staying silent "
        "lets the reader supply it (both readings are damaging, and one is a four-year "
        "held credit balance)"
    )


def test_the_closed_fixture_household_really_closed_holding_a_credit():
    """VACUITY FLOOR, and it is the whole finding in two numbers. If the fixture household
    had not closed, or had closed square, every check in this section would pass over a
    page that had never been repaired."""
    elec, gas = _closed_household()
    assert _closure_dates((elec, gas)), "the 'closed' fixture carries no churned event"
    be, bg = _leg_balance(elec), _leg_balance(gas)
    assert abs(be) <= 0.005, (
        f"the electricity leg no longer settles to zero ({be}) -- the contradiction this "
        "section pins is 'one leg square, the other in credit, one claim covering both'"
    )
    assert bg < -0.005, (
        f"the gas leg no longer closes in credit ({bg}) -- there would be no non-zero "
        "ledger for a 'settled to zero' claim to contradict"
    )


def test_no_settlement_claim_is_published_over_a_non_zero_ledger(tmp_path):
    """THE control for defect 2. Driven PER FUEL LEG, because the claim is rendered from
    the leg's own ledger and C1's credit sits entirely on the gas leg."""
    elec, gas = _closed_household()
    bills = _bills_by_fuel(INDEX, tmp_path, (elec, gas))
    _check_no_settlement_claim_over_a_non_zero_ledger(
        bills, {"elec": _leg_balance(elec), "gas": _leg_balance(gas)})


def test_a_leg_scoped_settlement_claim_names_its_leg(tmp_path):
    """The true half of the contradiction. 'Account settled to zero' was CORRECT about
    C1's electricity ledger and was still read as the household's, because nothing on the
    notice said which of the two accounts it was about."""
    elec, gas = _closed_household()
    bills = _bills_by_fuel(INDEX, tmp_path, (elec, gas))
    for fuel, want in (("elec", "electricity"), ("gas", "gas")):
        html = bills.get(fuel) or ""
        notice = re.search(r'<div class="closed-notice">(.*?)</div>', html, re.S)
        assert notice, f"no closed-account notice rendered on the {fuel} leg"
        assert want in notice.group(1), (
            f"the {fuel} leg's closed-account notice never names the leg it is about: "
            f"{notice.group(1)!r} -- on a dual-fuel household that reads as the account's"
        )


def test_a_closed_household_makes_no_present_tense_claim_about_its_money(tmp_path):
    """THE control for defect 1, over every region that makes a standing claim."""
    _check_no_live_standing_claim_on_a_closed_household(
        _standing_document(INDEX, tmp_path, _closed_household()))


def test_a_closed_household_in_credit_says_the_refund_is_not_in_the_record(tmp_path):
    """The honest half. The page cannot know whether the credit was refunded, so it says
    so -- rather than implying either answer by choice of tense."""
    _check_a_closing_credit_says_the_refund_is_unrecorded(
        _standing_document(INDEX, tmp_path, _closed_household()))


def test_a_live_household_still_states_its_position_in_the_present_tense(tmp_path):
    """The other direction. This is what stops the control above being satisfied by a
    writer that stamps every household 'at closure'."""
    _check_the_live_standing_claim_is_made_on_a_live_household(
        _standing_document(INDEX, tmp_path, _live_household()))


def test_the_drill_down_has_no_second_copy_of_the_standing_writer():
    """The class, not the instances. Four sites each deciding privately what to claim IS
    the defect; a local fallback in the second script would let them drift apart again, so
    the drill-down's doorway refuses rather than re-derives."""
    src = INDEX.read_text(encoding="utf-8")
    assert src.count("window.__accountStanding=function") == 1, (
        "the account-standing writer is defined more than once -- there is no sole writer"
    )
    m = re.search(r"function standing\(bal,opts\)\{(.*?)\n\}", src, re.S)
    assert m, "the drill-down no longer has a standing() doorway to the sole writer"
    assert "throw new Error" in m.group(1), (
        "standing() no longer refuses when the writer is missing -- an unavailable control "
        "is a FAILED control (R15), and a silent fallback here is the second implementation "
        "this repair exists to remove"
    )


def test_mutation_removing_the_credit_branch_kills_a_named_test(tmp_path):
    """R15 direction 1: THE ORIGINAL DEFECT. Send a credit balance back down the zero
    branch and the gas leg publishes 'Account settled to zero' over its own -£24.37."""
    mutant = _mutate(tmp_path, ':(st.state==="credit")?(" Closing balance: "',
                     ':(false)?(" Closing balance: "')
    elec, gas = _closed_household()
    bills = _bills_by_fuel(mutant, tmp_path, (elec, gas))
    with pytest.raises(AssertionError, match="is not zero"):
        _check_no_settlement_claim_over_a_non_zero_ledger(
            bills, {"elec": _leg_balance(elec), "gas": _leg_balance(gas)})


def test_mutation_a_closure_blind_writer_kills_a_named_test(tmp_path):
    """R15 direction 2: the tense half restored. A writer that cannot see the closure date
    returns every sentence in the present tense -- the page as cold-eyes found it."""
    mutant = _mutate(
        tmp_path,
        'var closed=(o.closedOn==null||o.closedOn==="")?null:String(o.closedOn);',
        "var closed=null;")
    with pytest.raises(AssertionError, match="in the present tense"):
        _check_no_live_standing_claim_on_a_closed_household(
            _standing_document(mutant, tmp_path, _closed_household()))


def test_mutation_an_always_closed_writer_kills_a_named_test(tmp_path):
    """R15 direction 3: the TAUTOLOGY. A writer that answers 'closed' for everything passes
    the closed-account control on any page at all -- and tells a live account holder that
    their own account has closed. The inverse direction is required to kill it."""
    mutant = _mutate(
        tmp_path,
        'var closed=(o.closedOn==null||o.closedOn==="")?null:String(o.closedOn);',
        'var closed="2021-12-30";')
    with pytest.raises(AssertionError, match="has NOT closed"):
        _check_the_live_standing_claim_is_made_on_a_live_household(
            _standing_document(mutant, tmp_path, _live_household()))


def test_mutation_a_silent_writer_kills_a_named_test(tmp_path):
    """R15 direction 4: FAIL-OPEN. Silence passes both tense checks trivially -- no
    present-tense phrase is present if no sentence is written at all. The refund statement
    and the live-household check are what make silence fail."""
    mutant = _mutate(
        tmp_path, "    return st;\n  };",
        '    return {balance:st.balance,closedOn:null,isClosed:false,state:st.state,'
        'caption:"",sentence:"",settlement:"",positionLabel:""};\n  };')
    with pytest.raises(AssertionError, match="does not say whether that"):
        _check_a_closing_credit_says_the_refund_is_unrecorded(
            _standing_document(mutant, tmp_path, _closed_household()))
    with pytest.raises(AssertionError, match="makes no present-tense"):
        _check_the_live_standing_claim_is_made_on_a_live_household(
            _standing_document(mutant, tmp_path, _live_household()))


def test_every_standing_check_fires_on_the_page_as_it_shipped(tmp_path):
    """R15 direction 5, and the only one whose subject is the REAL defect rather than a
    synthetic reversal of the repair: the page exactly as cold-eyes read it.

    NAMED for this section on purpose. The first draft reused section 18's test name and
    Python silently SHADOWED it -- one module, one namespace, so the earlier proof stopped
    being collected at all and the suite went from 1 skipped to 0 with no failure to show
    for it. A duplicate-definition census is now part of this module's own checks below.

    FAILS rather than skips when no pre-repair revision is reachable (2026-08-19) -- a
    control that silently passes when its subject is unavailable is a FAILED control, and
    this one had been skipping.
    """
    src = _pre_repair_source("__accountStanding")
    assert src is not None, (
        "cannot locate the committed index.html that predates __accountStanding -- the "
        "shipped-defect proof did NOT run, which is not the same as passing"
    )
    shipped = tmp_path / "shipped.html"
    shipped.write_text(src, encoding="utf-8")
    elec, gas = _closed_household()

    bills = _bills_by_fuel(shipped, tmp_path, (elec, gas))
    with pytest.raises(AssertionError, match="is not zero"):
        _check_no_settlement_claim_over_a_non_zero_ledger(
            bills, {"elec": _leg_balance(elec), "gas": _leg_balance(gas)})

    doc = _standing_document(shipped, tmp_path, (elec, gas))
    with pytest.raises(AssertionError, match="in the present tense"):
        _check_no_live_standing_claim_on_a_closed_household(doc)
    with pytest.raises(AssertionError, match="does not say whether that"):
        _check_a_closing_credit_says_the_refund_is_unrecorded(doc)


# ===========================================================================
# 20. WHICH ACCOUNT AM I LOOKING AT?
#     (coldwalk:site2_c1_pinned_exhibit_reads_as_the_open_households)
#
# MAJOR, and the evidence IS the misread rate: 3 of 3 blindfolded personas attributed the
# pinned exhibit's GBP6,560.17 and "two person / urban flat" to C6 (an SME with no gas) and
# to C_IC1 (I&C, GBP257k of term margin at risk). The static #op-state exhibit is pinned to
# ONE account -- company.json's household.id -- and re-renders ~2,000px above EVERY
# household's drill-down on all six tabs, with nothing separating the two.
#
# WHY EVERY EXISTING CONTROL IN THIS MODULE WAS BLIND TO IT. Nineteen sections of guards all
# answer one question: which SIDE of the wall is this figure on. Not one of them can answer
# which ACCOUNT it is about, and the misread was entirely the second question. The heading
# does say "as of account C1" -- a phrase inside a heading, which is the prose form the
# ruling's own non-negotiable rejects ("if a new panel can be added without declaring which
# side, nothing has been built -- only written down"). The same is true of subject.
#
# THE MECHANISM. Subject is declared the way side is: `data-account-subject` on the region,
# written by renderCustomerState() the moment company.json names the account, and by
# renderHousehold() from HH.base. One writer -- applyWallViewToOpState, which already owned
# op-state membership -- decides what the document does, and it REMOVES the second subject
# rather than hiding it, because "the reader cannot confuse these two households" is a claim
# about the DOM. It fails CLOSED on an unknown exhibit subject: unprovable sameness is the
# state the misread came out of.
#
# INDEPENDENCE (R15's TAUTOLOGY pattern). `window.__subjectViolations()` does not ask
# opStateSuppressedReason() whether the suppression worked. It reads the rendered document.
# Its missing-subject arm is about the DECLARATION, not the rendering, precisely so that
# stripping the attribute fires it even though the suppression would ALSO then hide the
# exhibit -- otherwise the fix would mask its own control's evidence.
#
# ANTI-PIN: nothing here pins a figure or a count from the run. The account ids come off
# company.json and the per-customer JSON, and the child count comes off the page's own
# markup, so regenerating the book changes what is compared rather than making these cry
# wolf. Only genuinely rendering two households at once can fail them.
SUBJECT_HARNESS = HERE / "_subject_harness.mjs"
COMPANY_JSON = HERE.parent / "data" / "company.json"


def _subject_fixture() -> tuple[Path, Path, Path]:
    """The exhibit's own household, its gas leg, and a DIFFERENT household -- all read off
    disk. Chosen by identity (company.json says whose the exhibit is), never hard-coded:
    re-point the exhibit at another account and this fixture follows it."""
    exhibit_id = (json.loads(COMPANY_JSON.read_text(encoding="utf-8")).get("household") or {}).get("id")
    assert exhibit_id, "company.json publishes no household -- the exhibit has no subject"
    elec = CUSTOMER_DATA / f"{exhibit_id}.json"
    assert elec.exists(), f"the exhibit's account {exhibit_id} has no per-customer record"
    gas_id = (json.loads(elec.read_text(encoding="utf-8")).get("dual_fuel_combined") or {}).get("gas_account_id")
    gas = CUSTOMER_DATA / f"{gas_id}.json" if gas_id else None
    others = sorted(
        p for p in CUSTOMER_DATA.glob("*.json")
        if p.stem not in {"_index", exhibit_id} and not p.stem.endswith("g")
        and json.loads(p.read_text(encoding="utf-8")).get("commodity") != "gas"
    )
    assert others, "no second household on disk -- this section would be vacuous"
    return elec, (gas if gas and gas.exists() else elec), others[0]


def _subject(index: Path = INDEX) -> dict:
    elec, gas, other = _subject_fixture()
    proc = subprocess.run(
        [NODE, str(SUBJECT_HARNESS), str(index), str(COMPANY_JSON), str(elec), str(other), str(gas)],
        capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, f"subject harness failed: {proc.stderr}"
    return json.loads(proc.stdout)


def _check_one_subject_in_the_document(doc: dict) -> None:
    """The law, stated once so the mutations below can all be judged by the same sentence."""
    state = doc["states"]["other_household_open"]
    assert state["threw"] is None, state["threw"]
    assert doc["exhibitAccount"] != doc["otherAccount"], (
        "the fixture opened the exhibit's own household -- this check would be vacuous"
    )
    assert state["op_state_children"] == 0, (
        f"the exhibit pinned to {doc['exhibitAccount']} is still in the rendered document "
        f"with household {doc['otherAccount']} open below it -- "
        f"{state['op_state_children']} of {state['op_state_children_expected']} blocks "
        "survive, which is the state 3 of 3 blind readers misattributed"
    )
    assert not state["violations"], state["violations"]


@pytest.mark.skipif(not NODE, reason="node not available")
def test_the_pinned_exhibit_leaves_the_document_when_another_household_is_open():
    """THE FINDING. Two accounts must not render at once."""
    _check_one_subject_in_the_document(_subject())


@pytest.mark.skipif(not NODE, reason="node not available")
def test_the_exhibit_stays_gone_on_every_tab():
    """The walk measured the exhibit above SIX tabs, so one tab is not the population.
    switchTab() re-enters renderHousehold(), which is exactly why it persisted before."""
    per_tab = _subject()["states"]["other_household_open_per_tab"]
    assert len(per_tab) >= 6, f"only {len(per_tab)} tabs driven -- the page has six"
    still_there = {t: s["op_state_children"] for t, s in per_tab.items() if s["op_state_children"]}
    assert not still_there, f"the pinned exhibit survives on these tabs: {still_there}"
    threw = {t: s["threw"] for t, s in per_tab.items() if s["threw"]}
    assert not threw, threw


@pytest.mark.skipif(not NODE, reason="node not available")
def test_the_removal_is_stated_and_not_silent():
    """A block that vanishes without explanation is a different defect from the one being
    fixed. The boundary names BOTH accounts, so a reader who saw the exhibit at the door
    knows which household it belonged to and which one they are now reading."""
    doc = _subject()
    boundary = doc["states"]["other_household_open"]["boundary_html"]
    assert doc["exhibitAccount"] in boundary and doc["otherAccount"] in boundary, (
        f"the boundary names neither account: {boundary!r}"
    )
    assert doc["states"]["landing"]["boundary_html"] == "", (
        "the boundary renders at the door, where there is no second subject to separate"
    )


@pytest.mark.skipif(not NODE, reason="node not available")
def test_closing_the_household_brings_the_exhibit_back():
    """R11 forbids an ORPHAN TRANSITION: a hold whose release does nothing, or is untested,
    is half a mechanism. This is the release."""
    doc = _subject()
    closed = doc["states"]["closed_again"]
    assert closed["threw"] is None, closed["threw"]
    assert closed["op_state_children"] == closed["op_state_children_expected"], (
        f"the exhibit did not come back after doLogout(): {closed['op_state_children']} of "
        f"{closed['op_state_children_expected']} blocks"
    )
    assert closed["boundary_html"] == "", "the boundary outlived the separation it explained"


@pytest.mark.skipif(not NODE, reason="node not available")
def test_null_control_the_exhibits_own_household_does_not_remove_it():
    """THE NULL CONTROL, and this section is worth little without it. Opening the exhibit's
    OWN account moves the SAMPLE (which household is open) without moving the LAW (two
    subjects must not co-render). If the exhibit vanished here too, the mechanism would be
    "hide it whenever anything is open" wearing a subject rule's clothes -- and every test
    above would pass on it."""
    doc = _subject()
    same = doc["states"]["exhibit_household_open"]
    assert same["threw"] is None, same["threw"]
    assert same["op_state_children"] == same["op_state_children_expected"], (
        f"the exhibit for {doc['exhibitAccount']} was removed with its OWN household open "
        "-- the rule being enforced is not about subject at all"
    )
    assert same["boundary_html"] == "", (
        "a separation was announced between an account and itself"
    )
    assert not same["violations"], same["violations"]


@pytest.mark.skipif(not NODE, reason="node not available")
def test_the_view_selector_still_governs_the_exhibit():
    """This change adds a SECOND reason to withhold an op-state block to the writer that
    already owned the first. The first must still work -- a customer-side view may not
    carry a company-only or SIM-only block."""
    per_view = _subject()["states"]["landing_per_view"]
    assert per_view["customer"]["op_state_children"] < per_view["both"]["op_state_children"], (
        "the customer view no longer filters the exhibit -- the subject gate ate the side gate"
    )
    leaked = [s for s in per_view["customer"]["sides"] if s not in (None, "customer")]
    assert not leaked, f"behind-the-wall blocks in the customer view: {leaked}"
    assert "customer" not in per_view["behind"]["sides"], per_view["behind"]["sides"]


@pytest.mark.skipif(not NODE, reason="node not available")
def test_mutation_leaving_the_exhibit_pinned_kills_a_named_test(tmp_path):
    """R15 direction 1: the defect itself, restored. Neuter the suppression and the exhibit
    goes back above the other household -- which is the page cold-eyes actually read."""
    mutant = _mutate(
        tmp_path,
        "function opStateSuppressedReason(){\n  var open=openSubject();\n  if(!open)return null;",
        "function opStateSuppressedReason(){\n  var open=openSubject();\n  if(open)return null;",
    )
    doc = _subject(mutant)
    assert doc["states"]["other_household_open"]["op_state_children"] > 0, (
        "the mutation did not reach the page -- this test would be vacuous"
    )
    with pytest.raises(AssertionError, match="still in the rendered document"):
        _check_one_subject_in_the_document(doc)
    assert doc["states"]["other_household_open"]["violations"], (
        "the exhibit renders above another household and the CONTROL stayed silent -- it "
        "is reporting the fix's opinion of itself, not the document"
    )


@pytest.mark.skipif(not NODE, reason="node not available")
def test_mutation_never_declaring_the_exhibits_subject_kills_a_named_test(tmp_path):
    """R15 direction 2, the FAIL-OPEN shape: the region stops declaring whose account it is.
    Two things must happen, and the second is the one that makes the control independent --
    the page must withhold the exhibit (it cannot prove sameness), AND the control must
    still report the missing declaration even though nothing visibly leaked. A control that
    only speaks when the fix has already failed is the fix grading itself."""
    mutant = _mutate(
        tmp_path,
        'if(opHost&&opHost.setAttribute)opHost.setAttribute("data-account-subject",String(h.id||""));',
        "if(false){}",
    )
    doc = _subject(mutant)
    landing = doc["states"]["landing"]
    assert not landing["op_state_subject"], (
        "the mutation did not reach the page -- this test would be vacuous"
    )
    same = doc["states"]["exhibit_household_open"]
    assert same["op_state_children"] == 0, (
        "an exhibit that cannot name its account was rendered above a household anyway -- "
        "the suppression fails OPEN on an unknown subject"
    )
    assert any("declares no account subject" in v for v in same["violations"]), same["violations"]


@pytest.mark.skipif(not NODE, reason="node not available")
def test_mutation_the_drill_down_stops_declaring_its_subject_kills_a_named_test(tmp_path):
    """R15 direction 3: the OTHER side of the same declaration. If the drill-down stops
    saying whose account it is, the page reads as though nothing is open -- and the exhibit
    is pinned back over it. Both regions have to declare, or neither declaration matters."""
    mutant = _mutate(
        tmp_path,
        '"<div class=\\"account-wrap\\" data-wall-chrome=\\"1\\" data-account-subject=\\""+esc(HH.base)+"\\">"+',
        '"<div class=\\"account-wrap\\" data-wall-chrome=\\"1\\">"+',
    )
    doc = _subject(mutant)
    assert doc["states"]["other_household_open"]["op_state_children"] > 0, (
        "the mutation did not reach the page -- this test would be vacuous"
    )
    with pytest.raises(AssertionError, match="still in the rendered document"):
        _check_one_subject_in_the_document(doc)


@pytest.mark.skipif(not NODE, reason="node not available")
def test_mutation_hiding_instead_of_removing_kills_a_named_test(tmp_path):
    """R15 direction 4: the CSS answer. Leave the blocks in the document and merely stop
    re-appending them. This is the plausible cheap fix, it looks right in a screenshot, and
    the whole page's doctrine is that removal must be true of the DOM -- because the claim
    being made is about what a reader can read, not about what is painted."""
    mutant = _mutate(
        tmp_path,
        "    else if(el.parentNode===host)host.removeChild(el);\n  });\n  renderSubjectBoundary(suppressed);",
        "    else if(el.parentNode===host&&!suppressed)host.removeChild(el);\n  });\n  renderSubjectBoundary(suppressed);",
    )
    doc = _subject(mutant)
    assert doc["states"]["other_household_open"]["op_state_children"] > 0, (
        "the mutation did not reach the page -- this test would be vacuous"
    )
    with pytest.raises(AssertionError, match="still in the rendered document"):
        _check_one_subject_in_the_document(doc)


@pytest.mark.skipif(not NODE, reason="node not available")
def test_the_membership_writer_is_still_the_only_one():
    """The page has paid twice for a second writer of one fact (four sentences about one
    balance; a case-study grid appended by a third path). This adds a REASON to the existing
    op-state membership writer rather than a sibling writer, and that is a property worth
    holding: only applyWallViewToOpState may append to or remove from #op-state."""
    src = INDEX.read_text(encoding="utf-8")
    body = src[src.index("function applyWallViewToOpState(){"):]
    body = body[: body.index("\n}\n") + 3]
    # The property is SOLE WRITER, not single call site: section 21 added a second removal
    # BRANCH (the undeclared block, withheld) inside this same function. What must stay
    # true is that every #op-state membership call in the page lives inside it -- so the
    # two counts must be EQUAL, and non-zero so a page that stopped governing the region
    # at all cannot pass by making both sides zero.
    for call in ("host.appendChild(", "host.removeChild("):
        assert src.count(call) == body.count(call) >= 1, (
            f"{call} appears {src.count(call)} times in the page and {body.count(call)} "
            "times inside applyWallViewToOpState -- #op-state membership has a second writer"
        )
    for entry in ("  renderTab();\n  // The subject of the page has just changed.",
                  "  applyWallViewToOpState();\n  loadCaseStudies();"):
        assert entry in src, (
            f"an entry point no longer re-runs the membership writer: {entry!r} -- the "
            "exhibit will outlive, or fail to survive, a change of subject"
        )


def test_no_definition_in_this_module_shadows_another():
    """A CONTROL ON THE CONTROLS, and it is here because this section's own first draft
    tripped it.

    This module is one namespace and 3,200 lines across nineteen sections, each written in
    its own tick. Reusing a test name does not collide -- Python rebinds, the earlier
    function is never collected, and the suite reports one FEWER test with no failure to
    show for it. That is a silently deleted R15 proof: exactly the FAIL-SILENT pattern R15
    names, applied to the proofs themselves. Section 19's draft shadowed section 18's
    shipped-defect test and the only visible symptom was a skip count dropping from 1 to 0.

    Helpers count too: a redefined `_mutate` retroactively changes what four earlier
    mutation tests actually run.
    """
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    seen: dict[str, int] = {}
    dupes: dict[str, list[int]] = {}
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if node.name in seen:
            dupes.setdefault(node.name, [seen[node.name]]).append(node.lineno)
        seen[node.name] = node.lineno
    assert not dupes, (
        "these top-level names are defined more than once in this module, so the earlier "
        f"definition is shadowed and never runs: {dupes} -- rename the later one"
    )


# ===========================================================================
# 21. THE OTHER GOVERNOR'S FAIL-OPEN HALF
#     (the second half of coldwalk:site2_case_study_cards_render_sim_truth_in_the_
#      customer_view -- named by the 2026-08-17 re-run walk, fixed then on #app only)
# ===========================================================================
#
# The page has TWO membership governors, one per region, and until this section only one of
# them was fail-closed:
#
#   #app        applyWallViewToApp()      every top-level child must carry data-wall-side
#                                         or data-wall-chrome; an undeclared one is REMOVED
#                                         and recorded.  (built 2026-08-17)
#   #op-state   applyWallViewToOpState()  `if(!suppressed&&(!side||wallViewShows(side)))
#                                         host.appendChild(el)` -- an undeclared block was
#                                         APPENDED, in every view, including the customer's.
#
# The walk's own words for the second one were "a second, quieter defect in the same
# function: `if(!side||wallViewShows(side))` showed any UNDECLARED block in every view --
# the fail-open half". The tick that found it fixed the #app half and left this one. Two
# blocks were living on that branch when this section was written -- the region heading and
# the drill-down link -- both genuinely chrome, which is why nothing had leaked YET and why
# the module stayed green: R15's FAIL-OPEN pattern exactly, a control that passes because
# its subject happens to be innocent.
#
# AND IT WAS TWO DEFECTS, NOT ONE. Driving a block that DECLARED data-wall-side="company"
# into the live region on the shipped page put it in the CUSTOMER's view as well --
# because opStateBlocks() cached #op-state's children on its first call, so a block
# appended after boot was never in any governor's subject at all, whatever it declared.
# That is the third time this page has paid for the same class: "a new layer above a
# control does not inherit its subject" (2026-08-12 the op-state exhibit, 2026-08-17 the
# case-study grid, here the region's own child list). The cache is now a UNION -- it still
# holds document order for the restore, and any live child not in it joins on the next pass.
#
# WHY THE EXISTING STATIC CONTROL COULD NOT SEE EITHER. `test_the_op_state_region_declares_
# a_side_for_every_block` scans the SOURCE FILE and its subject is CONTENT_CLASSES, a
# hand-kept set of six class names. A block using none of them is invisible to it, and a
# block that never appears in the file at all -- appended at runtime -- cannot be in its
# subject by construction. The governor's subject is every child of the region, with no
# vocabulary to keep, which is why the fix belongs at the governor and not in the list.
#
# PROVEN ON THE PAGE AS IT SHIPPED (`git show HEAD:site/customers/index.html`, run through
# this section's own probes): an undeclared block carrying "True satisfaction fell 12.2
# percentage points" -- the exact SIM-only string the customer view's own note forbids --
# rendered in the customer view, and nothing was recorded.
#
# ANTI-VACUITY, both null controls in the harness rather than in prose. (b) the same block
# DECLARED chrome must SURVIVE, or the "fix" is "hide anything appended late" wearing a
# declaration rule's clothes. (c) the same block DECLARED company must be governed by the
# VIEW -- behind the wall yes, customer's side no -- or the fix is "withhold everything
# appended late", which would pass (a) for the wrong reason.
#
# ANTI-PIN: no figure, count or stamp from the run appears here. The sentinel strings are
# written by the harness, and the leak string is the one the page's own WALL_VIEW_NOTE
# declares broken. Regenerating the book cannot make any of these cry wolf.

_OP_STATE_LEAK = "True satisfaction fell"


def _op_state_probes(index: Path = INDEX) -> dict:
    return _subject(index)["states"]["op_state_declaration_probes"]


@pytest.mark.skipif(not NODE, reason="node not available")
def test_an_undeclared_block_in_the_exhibit_is_withheld_in_every_view():
    """THE FINDING. A block appended to #op-state declaring neither a side nor chrome must
    not reach a reader -- in ANY view. Checking only the customer's would pass a mutant
    that defaults a missing side to `customer`, which is the fail-open shape itself."""
    p = _op_state_probes()
    assert p["undeclared_op_state_threw"] is None, p["undeclared_op_state_threw"]
    assert _OP_STATE_LEAK not in p["undeclared_op_state_html"], (
        "an undeclared block carrying SIM-only ground truth rendered in the pinned exhibit "
        "-- the customer view's own note says that means the page is broken"
    )


@pytest.mark.skipif(not NODE, reason="node not available")
def test_the_withholding_is_recorded_and_not_silent():
    """A fail-closed control that hides the evidence of its own firing is how the #app half
    of this defect went unnoticed for a week. The block is withheld AND named."""
    recorded = _op_state_probes()["undeclared_op_state_recorded"]
    assert recorded, (
        "the undeclared block was withheld silently -- nothing tells an author why their "
        "new panel vanished, so the next one is added the same way"
    )
    assert any("op-state" in str(v) for v in recorded), recorded


@pytest.mark.skipif(not NODE, reason="node not available")
def test_null_control_a_block_declared_chrome_survives():
    """NULL CONTROL (b). Moves the DECLARATION, not the law. If a chrome-declared block
    were withheld too, the mechanism would be "hide anything appended after boot" and every
    test above would pass on it."""
    p = _op_state_probes()
    assert "CHROME-SENTINEL" in p["chrome_op_state_html"], (
        "a block that declared itself chrome was withheld -- the rule being enforced is "
        "not about declaration at all"
    )
    assert not p["chrome_op_state_recorded"], p["chrome_op_state_recorded"]


@pytest.mark.skipif(not NODE, reason="node not available")
def test_null_control_a_block_declared_company_is_governed_by_the_view():
    """NULL CONTROL (c), and it is the one that catches the OTHER cheap fix. A block that
    DOES declare a side must be filtered by the view selector like every static panel --
    present behind the wall, absent from the customer's side. "Withhold everything appended
    late" would satisfy the finding test and destroy the region."""
    per_view = _op_state_probes()["sided_op_state_per_view"]
    assert per_view["behind"] and per_view["both"], (
        "a correctly-declared company block never reached the behind-the-wall view -- the "
        "governor is refusing declarations rather than reading them"
    )
    assert not per_view["customer"], (
        "a block declaring data-wall-side=company rendered in the customer's view"
    )


@pytest.mark.skipif(not NODE, reason="node not available")
def test_every_static_block_in_the_exhibit_declares_a_side_or_chrome():
    """The region as it SHIPS, not as a probe drives it. Every child either carries a wall
    side or says it is chrome -- so no block is relying on a fail-open branch that no
    longer exists."""
    per_view = _subject()["states"]["landing_per_view"]["both"]
    sides, chrome = per_view["sides"], per_view["chrome"]
    assert len(sides) == len(chrome) >= 2, (sides, chrome)
    undeclared = [i for i, s in enumerate(sides) if not s and not chrome[i]]
    assert not undeclared, (
        f"#op-state children at these positions declare neither a side nor chrome: "
        f"{undeclared} -- they render in every view by default"
    )
    assert any(sides), "the exhibit declares no wall side at all -- this check is vacuous"
    assert any(chrome), "no block declares chrome -- the chrome arm is untested here"


@pytest.mark.skipif(not NODE, reason="node not available")
def test_mutation_the_fail_open_branch_restored_kills_a_named_test(tmp_path):
    """R15 direction 1: the defect itself, exactly as it shipped. Remove the fail-closed
    branch and an undeclared block is appended in every view again."""
    mutant = _mutate(tmp_path, "    if(!side&&!chromeFlag){", "    if(false){")
    p = _op_state_probes(mutant)
    assert _OP_STATE_LEAK in p["undeclared_op_state_html"], (
        "MUTATION SURVIVED: the fail-open branch is back and the undeclared block was "
        "still withheld -- this test is not measuring the branch it names"
    )
    assert not p["undeclared_op_state_recorded"], p["undeclared_op_state_recorded"]


@pytest.mark.skipif(not NODE, reason="node not available")
def test_mutation_the_cached_subject_restored_kills_a_named_test(tmp_path):
    """R15 direction 2, the SECOND defect and the more interesting one. Put the once-only
    snapshot back: a block appended after boot is then in no governor's subject at all, so
    it renders in every view EVEN THOUGH it correctly declares a company side."""
    mutant = _mutate(
        tmp_path,
        "  if(OP_STATE_BLOCKS===null)OP_STATE_BLOCKS=[];\n  var host=document.getElementById(\"op-state\");",
        "  if(OP_STATE_BLOCKS!==null)return OP_STATE_BLOCKS;\n  OP_STATE_BLOCKS=[];\n"
        "  var host=document.getElementById(\"op-state\");",
    )
    per_view = _op_state_probes(mutant)["sided_op_state_per_view"]
    assert per_view["customer"], (
        "MUTATION SURVIVED: with the subject snapshotted once, a block appended later is "
        "still being filtered -- this test is not measuring the cache it names"
    )


@pytest.mark.skipif(not NODE, reason="node not available")
def test_mutation_hiding_the_record_kills_a_named_test(tmp_path):
    """R15 direction 3, FAIL-SILENT: withhold the block but stop recording it. The page
    looks identical to a reader and the author of the next undeclared panel learns nothing.
    The leak test above stays green on this mutant, which is why it needs its own."""
    mutant = _mutate(tmp_path, "  WALL_VIOLATIONS.push(what);", "  if(false)WALL_VIOLATIONS.push(what);")
    p = _op_state_probes(mutant)
    assert _OP_STATE_LEAK not in p["undeclared_op_state_html"], (
        "the mutation changed the withholding too -- it is not isolating the record"
    )
    assert not p["undeclared_op_state_recorded"], (
        "MUTATION SURVIVED: the record was silenced and something still reported it"
    )


@pytest.mark.skipif(not NODE, reason="node not available")
def test_mutation_treating_chrome_as_a_side_kills_a_named_test(tmp_path):
    """R15 direction 4, the OVER-BROAD failure. Accept `data-wall-chrome` as though it were
    a declared side and a chrome block stops being shown in every view -- the region's
    heading and its drill-down link would disappear from the customer's side. This is the
    mutation that proves the two arms are genuinely different arms."""
    mutant = _mutate(
        tmp_path,
        "    if(!suppressed&&(!side||wallViewShows(side)))host.appendChild(el);",
        "    if(!suppressed&&side&&wallViewShows(side))host.appendChild(el);",
    )
    per_view = _subject(mutant)["states"]["landing_per_view"]["customer"]
    assert not any(per_view["chrome"]), (
        "MUTATION SURVIVED: chrome blocks are still in the customer view after the arm "
        "that shows them was removed"
    )


@pytest.mark.skipif(not NODE, reason="node not available")
def test_both_checks_in_this_section_fire_on_the_page_as_it_SHIPPED(tmp_path):
    """R15's real subject: the page as PUBLISHED, not a synthetic mutation of the repair.
    Both defects must fire on it, or this section is describing a problem the page never
    had. A synthetic mutation can be wrong about what shipped; this cannot.

    FAILS rather than skips when its subject cannot be found (2026-08-19)."""
    src = _pre_repair_source("recordOpStateViolation")
    assert src is not None, (
        "cannot locate the committed index.html that predates recordOpStateViolation -- "
        "the shipped-defect proof did NOT run, which is not the same as passing"
    )
    shipped = tmp_path / "index.html"
    shipped.write_text(src, encoding="utf-8")
    p = _op_state_probes(shipped)
    assert _OP_STATE_LEAK in p["undeclared_op_state_html"], (
        "the shipped page did NOT leak an undeclared block into the exhibit -- this "
        "section is fixing something that was not broken"
    )
    assert not p["undeclared_op_state_recorded"], (
        "the shipped page already recorded the undeclared block -- the record is not new"
    )
    assert p["sided_op_state_per_view"]["customer"], (
        "the shipped page already filtered a late-appended company block out of the "
        "customer view -- the cached-subject half of this section is not real"
    )


# ===========================================================================
# (22) THE REGION LIST IS THE SUBJECT NOBODY HAD
#
# THE FINDING, and it is this atom's own recurring class for the FOURTH time. Three earlier
# ticks each closed "a new layer above a control does not inherit its subject" one layer at a
# time: the op-state exhibit (2026-08-12), the case-study grid appended to #app by a third
# path (2026-08-17), and #op-state's own cached child list (2026-08-18). Each fix widened a
# governor's subject to the children of one region. Nobody ever widened it to the REGIONS.
#
# applyWallViewToApp's own comment says "the subject is now the DOCUMENT". It is not; it is
# #app. applyWallViewToOpState's is #op-state. The set of governed regions was two
# getElementById literals -- the same hand-kept-subject shape as CONTENT_CLASSES, which the
# 2026-08-18 tick had already found structurally blind. The page has SEVEN top-level regions.
#
# MEASURED FIRST, on the served page in a real chromium, before a line of the repair existed:
# a block carrying "True satisfaction fell 12.2 percentage points" -- the exact string this
# page's own WALL_VIEW_NOTE declares means the page is broken -- appended to document.body and
# then setWallView("customer") called through the page's own entry point SURVIVED in the
# customer's view, with WALL_VIOLATIONS empty, __subjectViolations() empty and 0 console
# errors. It was green because every region that existed happened to be innocent, which is
# R15's FAIL-OPEN pattern exactly and says nothing about the next region.
#
# THE MECHANISM. Every rendering top-level child of <body> declares data-wall-chrome (carries
# no figure) or data-wall-governed="<fn>" (its contents are governed, by a function that must
# exist on window); anything else is recorded and REMOVED. Named governor rather than a
# boolean on purpose: an unfalsifiable claim of governance is decoration, so a region naming a
# function that is not there is treated exactly as one that declared nothing.
#
# WHY NOT data-wall-side ON THE CONTAINERS: #op-state and #app carry no figure of their own,
# and filtering the container by view would take its customer-observable children with it.
#
# NO CACHE, deliberately. opStateBlocks() caches because that governor removes AND restores;
# taking the snapshot once is what let a post-boot block escape it (2026-08-18). This governor
# never restores, so a live read costs nothing and closes that hole by construction.
#
# ANTI-PIN: no figure, count or stamp from the run appears in this section. The region list
# comes off the page's own markup and the sentinels are the harness's own strings.
# ===========================================================================
_BODY_LEAK = "True satisfaction fell 12.2 percentage points"
# Written HERE, not read off the page. The governor has an exemption set (DOC_NONRENDERING);
# if the test took its subject from that set, the page could exempt a region from its own
# control and stay green -- R15's TAUTOLOGY pattern. These are the tags that render nothing,
# and test_the_pages_exemption_set_cannot_be_widened pins the page's set inside this one.
_NON_RENDERING = {"SCRIPT", "STYLE", "LINK", "META", "TEMPLATE", "NOSCRIPT", "TITLE", "BASE"}


def _content_regions(probes: dict) -> list[dict]:
    return [r for r in probes["declared_regions"] if r["tag"] not in _NON_RENDERING]


def _doc_probes(index: Path = INDEX) -> dict:
    return _subject(index)["states"]["document_region_probes"]


def _check_no_undeclared_region_survives(probes: dict) -> None:
    """The law, stated once so every mutation below is judged by the same sentence."""
    leaked = {v: ids for v, ids in probes["undeclared_region_ids"].items()
              if "bolted-at-body" in ids}
    assert not leaked, (
        "a top-level region declaring neither a side's governor nor chrome, carrying "
        f"{_BODY_LEAK!r}, survived in these views: {sorted(leaked)} -- the page's own "
        "customer-view note says that means the page is broken"
    )


@pytest.mark.skipif(not NODE, reason="node not available")
def test_every_top_level_region_declares_chrome_or_names_its_governor():
    """THE STRUCTURAL GUARD, and the one exit criterion (1) actually turns on: a region added
    without declaring anything must not be publishable. Subject is the page's own body."""
    probes = _doc_probes()
    undeclared = [r for r in _content_regions(probes)
                  if r["chrome"] is None and not r["governed"]]
    assert not undeclared, (
        "top-level regions of the page declare neither data-wall-chrome nor "
        f"data-wall-governed: {undeclared}"
    )
    assert len(_content_regions(probes)) >= 5, (
        f"only {len(_content_regions(probes))} content regions were read off the page -- "
        "this check would be near-vacuous"
    )


@pytest.mark.skipif(not NODE, reason="node not available")
def test_the_pages_exemption_set_cannot_be_widened():
    """The guard skips tags that render nothing. If the page were free to choose that set,
    it could exempt a leaking region from its own control and stay green -- so the page's
    set must sit INSIDE the one written in this module, which the page cannot edit."""
    page_set = _doc_probes()["page_nonrendering"]
    assert page_set, "the governor's DOC_NONRENDERING set could not be read off the page"
    extra = sorted(set(page_set) - _NON_RENDERING)
    assert not extra, (
        f"the page exempts tags this control does not accept as non-rendering: {extra}"
    )


@pytest.mark.skipif(not NODE, reason="node not available")
def test_every_declared_governor_is_a_function_that_exists():
    """The half that stops the attribute becoming decoration. A region asserting governance
    by a name nothing defines is ungoverned, and the page must say so rather than believe it.
    Checked here against the page's SOURCE so the assertion is independent of the governor's
    own runtime lookup -- a checker that asks the fix whether the fix worked is a tautology."""
    src = INDEX.read_text(encoding="utf-8")
    governed = [r["governed"] for r in _doc_probes()["declared_regions"] if r["governed"]]
    assert governed, "no region declares a governor -- this check would be vacuous"
    missing = [g for g in governed if f"function {g}(" not in src]
    assert not missing, f"regions name governors this page does not define: {missing}"


@pytest.mark.skipif(not NODE, reason="node not available")
def test_an_undeclared_region_bolted_onto_the_body_is_withheld_in_every_view():
    """THE FINDING ITSELF, driven through the page's own setWallView in all three views --
    checking only 'behind' would pass a mutant that defaults the missing declaration to the
    customer's side, which is the fail-open shape being guarded."""
    _check_no_undeclared_region_survives(_doc_probes())


@pytest.mark.skipif(not NODE, reason="node not available")
def test_the_withheld_region_is_recorded_and_not_removed_in_silence():
    """FAIL-SILENT is its own arm: the leak check above stays green on a governor that
    removes the block and says nothing, and a control that hides the evidence of its own
    firing is how a defect stays invisible for days."""
    recorded = _doc_probes()["undeclared_region_recorded"]
    assert any("bolted-at-body" in r for r in recorded), (
        f"the undeclared region was withheld silently -- WALL_VIOLATIONS held {recorded}"
    )


@pytest.mark.skipif(not NODE, reason="node not available")
def test_null_control_a_region_declared_chrome_survives_in_every_view():
    """WITHOUT THIS the mechanism could be 'remove anything appended after boot' wearing a
    declaration rule's clothes, and the leak test would pass for the wrong reason. Moves the
    DECLARATION, not the law."""
    probes = _doc_probes()
    dropped = {v: ids for v, ids in probes["chrome_region_ids"].items()
               if "bolted-at-body" not in ids}
    assert not dropped, (
        f"a region that DID declare itself chrome was removed anyway in {sorted(dropped)} -- "
        "the governor is not reading the declaration"
    )
    assert not probes["chrome_region_recorded"], (
        f"a correctly-declared region was recorded as a violation: {probes['chrome_region_recorded']}"
    )


@pytest.mark.skipif(not NODE, reason="node not available")
def test_a_region_naming_a_governor_that_does_not_exist_is_treated_as_undeclared():
    """The OVER-BROAD direction's opposite: proof the two arms are different arms. A region
    may not buy its way past the guard with a string."""
    probes = _doc_probes()
    _assert_fake_governor_withheld(probes)
    assert any("bolted-at-body" in r for r in probes["fake_governor_recorded"]), (
        "the imaginary-governor region was withheld silently"
    )


def _assert_fake_governor_withheld(probes: dict) -> None:
    """The law for the governor-is-real arm, shared by the check and its mutation so a
    mutant cannot reach the page by a different route than the test it must kill."""
    survived = {v: ids for v, ids in probes["fake_governor_ids"].items()
                if "bolted-at-body" in ids}
    assert not survived, (
        f"a region claiming an imaginary governor survived in {sorted(survived)}"
    )


@pytest.mark.skipif(not NODE, reason="node not available")
def test_the_pages_own_regions_all_survive_after_the_guard_has_run():
    """R11's no-orphan-transition rule applied to a REMOVAL: a guard whose release is
    untested is half a mechanism. Every region the page ships with must still be in the
    document, in every view, once the guard has removed three probes."""
    probes = _doc_probes()
    expected = [r["key"] for r in _content_regions(probes)]
    assert len(expected) >= 5, f"the harness read too few regions to be meaningful: {expected}"
    for view, ids in probes["surviving_regions"].items():
        missing = [e for e in expected if e not in ids]
        assert not missing, f"the guard removed the page's own regions in {view!r}: {missing}"
    assert not probes["surviving_recorded"], probes["surviving_recorded"]
    assert probes["undeclared_region_threw"] is None, probes["undeclared_region_threw"]


# --- R15, four mutations, each killing a NAMED test -------------------------
def test_mutation_the_body_level_fail_open_kills_a_named_test(tmp_path):
    """(1) The defect itself, restored: an undeclared region is left in the document."""
    mutant = _mutate(
        tmp_path,
        '      recordRegionViolation(idx,el,"declares neither data-wall-chrome nor data-wall-governed");',
        "      return;",
    )
    with pytest.raises(AssertionError, match="survived in these views"):
        _check_no_undeclared_region_survives(_doc_probes(mutant))


def test_mutation_silencing_the_region_record_kills_a_named_test(tmp_path):
    """(2) FAIL-SILENT. The block is still removed, so the leak test stays GREEN -- which is
    exactly why the record needs a test of its own."""
    mutant = _mutate(tmp_path, "  WALL_VIOLATIONS.push(what);\n  if(typeof console!==\"undefined\"&&console.error)console.error(\n    \"wall exhibit: an \"+what+\" was withheld -- every top-level region must carry \"+",
                     "  if(false)WALL_VIOLATIONS.push(what);\n  if(typeof console!==\"undefined\"&&console.error)console.error(\n    \"wall exhibit: an \"+what+\" was withheld -- every top-level region must carry \"+")
    probes = _doc_probes(mutant)
    _check_no_undeclared_region_survives(probes)  # still green -- the point of this mutation
    assert not any("bolted-at-body" in r for r in probes["undeclared_region_recorded"]), (
        "the mutation did not actually silence the record, so this proves nothing"
    )


def test_mutation_accepting_any_governor_string_kills_a_named_test(tmp_path):
    """(3) The OVER-BROAD arm: the declaration is trusted without checking the governor is
    real, which turns data-wall-governed into decoration."""
    mutant = _mutate(tmp_path, '      if(typeof window[governed]==="function")return;',
                     "      return;")
    with pytest.raises(AssertionError, match="imaginary governor"):
        _assert_fake_governor_withheld(_doc_probes(mutant))
    # and it must NOT also kill the plain leak check -- if it did, this mutation would be
    # proving the fail-open arm again rather than the governor-is-real arm.
    _check_no_undeclared_region_survives(_doc_probes(mutant))


def test_mutation_removing_the_guard_from_setwallview_kills_a_named_test(tmp_path):
    """(4) The mechanism disconnected rather than broken -- the shape in which a control is
    present in the file, passes its own unit reading, and never runs on the page."""
    mutant = _mutate(tmp_path, "  enforceDocumentRegions();\n}", "\n}")
    with pytest.raises(AssertionError, match="survived in these views"):
        _check_no_undeclared_region_survives(_doc_probes(mutant))


@pytest.mark.skipif(not NODE, reason="node not available")
def test_this_section_fires_on_the_page_as_it_SHIPPED(tmp_path):
    """R15's real subject: the page as PUBLISHED, not a synthetic reversal of the repair. A
    mutation can be wrong about what shipped; this cannot. If this ever cannot find the
    pre-repair revision it FAILS -- it does not skip -- because 'the proof did not run' and
    'the proof passed' must not look the same.

    This section wrote the first window-free locator and got its PATHSPEC wrong (a
    repo-root-relative path handed to `git -C <site/customers>`), so it returned None on
    every call once its own repair was committed. Section 23 moved the locator to the
    module's sole writer and fixed the origin; this call site is unchanged in intent."""
    src = _pre_repair_source("enforceDocumentRegions")
    assert src is not None, (
        "cannot locate the committed index.html that predates enforceDocumentRegions -- "
        "the shipped-defect proof did NOT run, which is not the same as passing"
    )
    shipped = tmp_path / "index.html"
    shipped.write_text(src, encoding="utf-8")
    probes = _doc_probes(shipped)
    assert any("bolted-at-body" in ids for ids in probes["undeclared_region_ids"].values()), (
        "the shipped page did NOT leak an undeclared body-level region -- this section is "
        "fixing something that was never broken"
    )
    assert not probes["undeclared_region_recorded"], (
        f"the shipped page already recorded it: {probes['undeclared_region_recorded']}"
    )
    undeclared = [r for r in _content_regions(probes)
                  if r["chrome"] is None and not r["governed"]]
    assert len(undeclared) >= 5, (
        "the shipped page already declared its regions -- the structural half of this "
        f"section is not real (undeclared: {undeclared})"
    )


# ===========================================================================
# 23. THE PROOFS THEMSELVES ARE A POPULATION
#     (WORKER_FINDING_THREE_SHIPPED_DEFECT_PROOFS_HAVE_QUIETLY_STOPPED_RUNNING_2026-08-19)
# ===========================================================================
#
# THE FINDING. `pytest site/customers/ -q -rs` reported three skips:
#
#   test_wall_exhibit.py:2945  no revision of index.html without __householdCollections
#                              is reachable -- the shipped-defect proof did NOT run
#   test_wall_exhibit.py:3268  no committed revision without __accountStanding is reachable
#   test_wall_exhibit.py:3809  no committed index.html without this repair within the window
#
# Those are sections 18, 19 and 21's R15 direction-5 arms -- the ONLY arm in each section
# whose subject is the defect the page actually shipped, rather than a synthetic reversal
# of the repair. All three had stopped executing. Their mutation siblings stayed green, the
# suite stayed green, and the only visible symptom was a skip count nobody reads.
#
# AND THE FOURTH, which is why this is a class and not three instances. Section 22 was
# written to fix exactly this and was ITSELF broken, in a different way: it handed
# `git -C <site/customers>` the repo-root-relative pathspec `site/customers/index.html`.
# git resolves a pathspec relative to -C, so `git log -S` matched nothing, the locator
# returned None, and the test FAILED at HEAD -- red, not skipped, because that section had
# already adopted assert-don't-skip. It had been green for exactly one tick, on the
# uncommitted-case branch, and turned red the moment its own repair was committed. Four
# private answers to one question; four different ways of being wrong.
#
# THE REPAIR IS A SOLE WRITER (R10: the class, not the instances). `_pre_repair_source` is
# now the module's only route to a pre-repair revision and its only caller of git. This
# section is the control that keeps it that way: a fifth section that reinvents a locator,
# reintroduces a window, or converts a proof back into a skip fails HERE, by construction,
# whatever it is named.
#
# WHAT IS DELIBERATELY NOT THE SUBJECT: a bare `HEAD~` (the parent, no window). Section
# 18's comment at the top of this module cites `git show HEAD~:...` as diff evidence and is
# honest. The decaying shape is a NUMBERED or INTERPOLATED ancestor reference.

_SHIPPED_PROOF = "as_it_ship"          # the naming convention for R15's direction-5 arm
_SOLE_LOCATOR = "_pre_repair_source"
_GIT_WRITERS = {"_repo_root", "_pre_repair_source"}
_MIN_SHIPPED_PROOFS = 4

# The subject is a REV STRING HANDED TO GIT, read off the AST -- not the file's text.
# Keying on the text would make this module's own header, which has to name the defect it
# repaired, the first thing to fail; a control that forbids describing its own subject is
# not a control, it is a gag. Both decayed shapes are string constants beginning "HEAD~":
# the tuple form ("HEAD~1", "HEAD~2", ...) directly, and the interpolated form f"HEAD~{n}"
# via the constant half of its JoinedStr.
#
# STATED LIMIT: a window assembled at runtime ("HEAD" + "~" + str(n)) would slip this arm.
# Arm 4 is the backstop -- it fires on any NEW function that shells git at all, whatever it
# names its revisions -- which is why the two arms are proven separately below.
_WINDOW_RE = re.compile("^HEAD" + "~")

# Tests whose subject IS the locator, and which therefore call it without being
# shipped-defect proofs. Written out rather than pattern-matched, and CHECKED: a member
# that looks like a proof would be an exemption used to dodge arm 3, so
# test_the_locator_probe_exemption_cannot_hide_a_proof refuses one.
_LOCATOR_PROBES = {"test_the_sole_locator_resolves_a_pre_repair_page_for_every_symbol_it_is_asked"}


def _top_level_functions(tree: ast.Module) -> dict[str, ast.FunctionDef]:
    """Top-level defs only. `ast.walk` over each still reaches nested helpers, so a git call
    hidden in a closure is attributed to the function that owns it rather than escaping as
    an anonymous inner name."""
    return {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}


def _calls_in(fn: ast.FunctionDef) -> set[str]:
    out: set[str] = set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name):
                out.add(f.id)
            elif isinstance(f, ast.Attribute):
                out.add(f.attr)
    return out


def _shipped_proofs(tree: ast.Module, label: str) -> set[str]:
    """The population, with its own anti-vacuity floor. A census that finds nothing must
    REFUSE -- every arm below is trivially green on an empty subject, which is the
    fail-open direction R15 names."""
    found = {n for n in _top_level_functions(tree) if _SHIPPED_PROOF in n.lower()}
    assert len(found) >= _MIN_SHIPPED_PROOFS, (
        f"{label}: found {len(found)} shipped-defect proofs, expected at least "
        f"{_MIN_SHIPPED_PROOFS} -- this control's own population has gone missing, and "
        f"every check in this section passes vacuously on an empty one ({sorted(found)})"
    )
    return found


def _git_invokers(tree: ast.Module) -> set[str]:
    out: set[str] = set()
    for name, fn in _top_level_functions(tree).items():
        for n in ast.walk(fn):
            if not (isinstance(n, ast.Call) and n.args):
                continue
            a = n.args[0]
            if (isinstance(a, ast.List) and a.elts and isinstance(a.elts[0], ast.Constant)
                    and a.elts[0].value == "git"):
                out.add(name)
    return out


def _check_no_shipped_proof_uses_a_window(src: str, label: str) -> None:
    hits = sorted({n.value for n in ast.walk(ast.parse(src))
                   if isinstance(n, ast.Constant) and isinstance(n.value, str)
                   and _WINDOW_RE.match(n.value)})
    assert not hits, (
        f"{label}: a pre-repair revision is located by a fixed ancestor window. A window is "
        f"wall-clock in disguise -- it decays into a skip and the proof stops running with "
        f"no red to show for it: {hits[:4]}"
    )


def _check_shipped_proofs_fail_rather_than_skip(src: str, label: str) -> None:
    tree = ast.parse(src)
    fns = _top_level_functions(tree)
    skipping = sorted(n for n in _shipped_proofs(tree, label) if "skip" in _calls_in(fns[n]))
    assert not skipping, (
        f"{label}: these shipped-defect proofs can skip: {skipping}. 'The proof did not run' "
        f"and 'the proof passed' must not look the same to a reader of this suite."
    )


def _check_the_locator_is_the_sole_writer(src: str, label: str) -> None:
    tree = ast.parse(src)
    proofs = _shipped_proofs(tree, label)
    callers = {n for n, f in _top_level_functions(tree).items()
               if _SOLE_LOCATOR in _calls_in(f)}
    assert proofs == callers - _LOCATOR_PROBES, (
        f"{label}: the shipped-defect proofs and the callers of {_SOLE_LOCATOR} are not the "
        f"same set. Proofs locating their subject privately: "
        f"{sorted(proofs - callers)}; non-proofs calling the locator: "
        f"{sorted(callers - proofs - _LOCATOR_PROBES)}."
    )


def _check_git_has_one_writer(src: str, label: str) -> None:
    stray = sorted(_git_invokers(ast.parse(src)) - _GIT_WRITERS)
    assert not stray, (
        f"{label}: these functions shell git directly instead of going through "
        f"{_SOLE_LOCATOR}: {stray}. Four private locators is how three of them decayed "
        f"into skips and the fourth went red without anyone noticing."
    )


_ARMS = (
    _check_no_shipped_proof_uses_a_window,
    _check_shipped_proofs_fail_rather_than_skip,
    _check_the_locator_is_the_sole_writer,
    _check_git_has_one_writer,
)


def _this_module() -> str:
    return Path(__file__).resolve().read_text(encoding="utf-8")


def _decoy(*, proofs: int = _MIN_SHIPPED_PROOFS, body: str = "    src = _pre_repair_source('x')\n",
           extra: str = "") -> str:
    """A synthetic module written HERE rather than borrowed from the real one.

    A decoy lifted from the module under test can pass a mutation while proving nothing --
    it carries every other property of the real file, so the arm that fires may not be the
    arm being exercised. These are the smallest modules that reach each arm.
    """
    out = ["import pytest", ""]
    for i in range(proofs):
        out.append(f"def test_section_{i}_fires_on_the_page_as_it_shipped():")
        out.append(body.rstrip("\n") or "    pass")
        out.append("")
    out.append(extra)
    return "\n".join(out)


# --- the four arms, against this module as it stands -----------------------------------

def test_no_shipped_defect_proof_locates_its_subject_by_a_window():
    """ARM 1. The shape that decayed -- an ancestor rev built from a fixed offset. Gone, and
    the constant that reintroduces it fires here."""
    _check_no_shipped_proof_uses_a_window(_this_module(), "this module")


def test_the_locator_probe_exemption_cannot_hide_a_proof():
    """Arm 3 carries an exemption, so the exemption needs its own arm -- otherwise the way
    to defeat the sole-writer rule is to add your section to the exemption set.

    Two conditions, both checkable: an exempt name may not look like a shipped-defect proof
    (which is what arm 3 would then stop counting), and every exempt name must actually
    exist in this module, so a rename cannot leave a stale entry silently widening the hole.
    """
    fns = _top_level_functions(ast.parse(_this_module()))
    for name in sorted(_LOCATOR_PROBES):
        assert name in fns, (
            f"{name} is exempted from the sole-writer rule but does not exist in this "
            f"module -- a stale exemption is a hole nothing is watching"
        )
        assert _SHIPPED_PROOF not in name.lower(), (
            f"{name} is exempted from the sole-writer rule while naming itself a "
            f"shipped-defect proof -- that is the rule being used to dodge itself"
        )


def test_every_shipped_defect_proof_fails_rather_than_skips():
    """ARM 2. The FAIL-SILENT half. Three of these were skipping when this section was
    written, and the suite was green throughout."""
    _check_shipped_proofs_fail_rather_than_skip(_this_module(), "this module")


def test_the_pre_repair_locator_is_this_modules_sole_writer():
    """ARM 3. Set EQUALITY, both directions: a proof may not locate its subject privately,
    and nothing that is not a proof may call the locator. Keyed on the mechanism, so the
    naming convention and the actual population cannot drift apart."""
    _check_the_locator_is_the_sole_writer(_this_module(), "this module")


def test_nothing_in_this_module_shells_git_except_the_locator():
    """ARM 4, and it is the one that does not depend on a naming convention at all. A fifth
    section could satisfy arms 1-3 and still shell git for a revision under some other
    name; this fires on the subprocess call itself."""
    _check_git_has_one_writer(_this_module(), "this module")


@pytest.mark.parametrize("symbol", [
    "__householdCollections",   # section 18
    "__accountStanding",        # section 19
    "recordOpStateViolation",   # section 21
    "enforceDocumentRegions",   # section 22
])
def test_the_sole_locator_resolves_a_pre_repair_page_for_every_symbol_it_is_asked(symbol):
    """The locator answers, for real, for every symbol this module actually asks about --
    the direct evidence that the three skips and the one red are gone.

    ANTI-VACUITY, and it is not decorative: a MISSPELLED symbol predates every revision, so
    the locator would cheerfully return HEAD and the check would pass while proving nothing.
    The symbol must be present in the live page first.
    """
    assert symbol in INDEX.read_text(encoding="utf-8"), (
        f"{symbol} is not in the live index.html -- this parametrisation is asking the "
        f"locator about a symbol the page does not have, and would pass trivially"
    )
    src = _pre_repair_source(symbol)
    assert src is not None, (
        f"the sole locator cannot find the revision that predates {symbol} -- the "
        f"shipped-defect proof that depends on it did NOT run"
    )
    assert symbol not in src, (
        f"the locator returned a page that still carries {symbol} -- its post-condition "
        f"failed, and the proof would be running against the repaired page"
    )


# --- R15: four mutations, each killing a NAMED test, plus a null control ----------------

def test_mutation_a_windowed_locator_kills_a_named_test():
    """(1) The original defect: the ancestor window restored."""
    mutant = _decoy(body='    for rev in ("HEAD", "HEAD' + '~1"):\n        src = _pre_repair_source(rev)\n')
    with pytest.raises(AssertionError, match="fixed ancestor window"):
        _check_no_shipped_proof_uses_a_window(mutant, "decoy")


def test_mutation_a_proof_that_skips_kills_a_named_test():
    """(2) FAIL-SILENT: the proof still exists, still reads correctly, and reports nothing
    when its subject is unavailable. Note arm 1 stays GREEN on this decoy -- the two arms
    are different arms, which is the point of proving them separately."""
    mutant = _decoy(body="    src = _pre_repair_source('x')\n    if src is None:\n        pytest.skip('no subject')\n")
    _check_no_shipped_proof_uses_a_window(mutant, "decoy")  # not this arm's defect
    with pytest.raises(AssertionError, match="can skip"):
        _check_shipped_proofs_fail_rather_than_skip(mutant, "decoy")


def test_mutation_a_proof_locating_its_subject_privately_kills_a_named_test():
    """(3) The sole-writer arm: a section that goes back to answering the question itself."""
    mutant = _decoy(proofs=_MIN_SHIPPED_PROOFS - 1) + (
        "\ndef test_section_9_fires_on_the_page_as_it_shipped():\n"
        "    src = _my_own_locator()\n"
    )
    with pytest.raises(AssertionError, match="locating their subject privately"):
        _check_the_locator_is_the_sole_writer(mutant, "decoy")


def test_mutation_a_stray_git_call_kills_a_named_test():
    """(4) OVER-BROAD direction, and the arm that survives a rename: a helper that shells
    git for a revision under a name no convention covers. Arms 1-3 are green on it."""
    mutant = _decoy(extra=(
        "def _quietly_locate():\n"
        "    return subprocess.run(['git', 'show', 'x:y'], capture_output=True)\n"
    ))
    for arm in _ARMS[:3]:
        arm(mutant, "decoy")  # none of the other three can see it
    with pytest.raises(AssertionError, match="shell git directly"):
        _check_git_has_one_writer(mutant, "decoy")


def test_mutation_an_empty_population_refuses_rather_than_passing():
    """(5) FAIL-OPEN, the direction that makes every other arm meaningless: delete the
    proofs and the census has nothing to object to. It must REFUSE, not pass."""
    empty = _decoy(proofs=0)
    for arm in (_check_shipped_proofs_fail_rather_than_skip,
                _check_the_locator_is_the_sole_writer):
        with pytest.raises(AssertionError, match="population has gone missing"):
            arm(empty, "decoy")


def test_null_control_a_clean_module_passes_every_arm():
    """The null control. Without it these checkers could be `assert False` wearing four
    different messages: a module that does the right thing must come back clean."""
    for arm in _ARMS:
        arm(_decoy(), "clean decoy")


def test_this_section_fires_on_the_module_as_it_SHIPPED():
    """R15 direction 5 for THIS section, and its subject is this module's own source.

    Every arm above must fire on the module as it was published -- the version with three
    windowed locators, three skipping proofs and a fourth locator whose pathspec never
    matched. Located by the same sole locator, pointed at this file instead of the page, so
    this section is not exempt from the mechanism it exists to enforce.
    """
    src = _pre_repair_source(_SOLE_LOCATOR, MODULE_PATH)
    assert src is not None, (
        "cannot locate the committed test module that predates the sole locator -- the "
        "shipped-defect proof did NOT run, which is not the same as passing"
    )
    fired = []
    for arm in _ARMS:
        try:
            arm(src, "the module as it shipped")
        except AssertionError:
            fired.append(arm.__name__)
    assert sorted(fired) == sorted(a.__name__ for a in _ARMS), (
        "the module as it shipped did NOT trip every arm of this section -- an arm that "
        f"cannot fire on the real defect is not evidence. Fired: {fired}"
    )


# ===========================================================================
# 24. THE PAGE DOES NOT WRITE DOWN WHICH ACCOUNTS EXIST
#     (worker tick, SITE2 draw 2026-08-19)
# ===========================================================================
#
# THE FINDING, measured on the LIVE surface before any repair existed. The landing card
# answers "which accounts can I open?" with a list typed into the page on 2026-06-30:
#
#     Electricity: C1-C9, C_IC1-C_IC4 / Gas: C1g-C4g, C_IC3g          -- 18 accounts
#
# The roster the same page fetches for its own prev/next arrows, and which the site serves
# at /data/customers.json, carried NINETEEN: SYN-2021-001 entered it on 2026-08-13 and the
# typed list did not move. So for six days https://poesys.net/customers/ told every visitor
# that an account it will happily open -- and will CYCLE THEM INTO, one press of the arrow
# from C_IC4 -- does not exist. Nothing could fail on it: the claim had no subject outside
# itself, so there was nothing for a control to compare it against.
#
# THE CLASS, which is this module's own recurring shape for the fifth time: a private
# answer to a question an artefact already answers. Four sentence sites deciding what to
# claim about one household's money (08-18); two governors deciding what a subject is
# (08-18); seven regions in nobody's subject (08-19); four proofs privately locating a
# revision (08-19); and now the page's own population.
#
# THE REPAIR IS A SOLE SOURCE, not an edited literal. `fetchCustomerGroups()` already
# fetched the roster for cycling; the landing card's list is now rendered from that SAME
# fetch by `rosterHintHtml()`, so the two consumers cannot disagree by construction. There
# is no literal to update, and updating one would not be a repair -- it would reset the
# clock on the next drift.
#
# FAIL-CLOSED, and that is the arm that matters most here: an unreadable or empty roster
# produces a REFUSAL ("this page will not list the accounts -- it would only be guessing"),
# never a written-down fallback. A fallback literal is the same defect wearing a
# contingency label, and it would sit in the one state nobody looks at.
ROSTER_PATH = HERE.parent / "data" / "customers.json"
ACCOUNT_FILES_INDEX = HERE.parent / "data" / "customers" / "_index.json"
_MIN_ROSTER = 10          # anti-vacuity floor: every arm below is green on an empty roster
_ROSTER_LINES = ("Electricity", "Gas")


def _published_accounts(roster: dict) -> set[str]:
    """The account ids the roster publishes, as the page's own reader assembles them."""
    out = set()
    for c in roster.get("customers", []):
        for leg in (c.get("legs") or {}).values():
            if leg and leg.get("cid"):
                out.add(leg["cid"])
    return out


def _rendered_accounts(hint: str | None) -> set[str]:
    """The ids the rendered card actually NAMES, parsed off the two labelled lines.

    Deliberately not a regex over id-shaped tokens: a shape pattern would have to be
    taught what an account id looks like, and SYN-2021-001 -- the account this section
    exists because of -- does not look like the others.
    """
    out: set[str] = set()
    for chunk in (hint or "").split("<br>"):
        label, _, rest = chunk.partition(": ")
        if label.strip() in _ROSTER_LINES and rest.strip():
            out |= {t.strip() for t in rest.split(",") if t.strip()}
    return out


def _landing_with_roster(index: Path, roster: Path | str) -> dict:
    """The landing harness driven with a roster its ../data/customers.json fetch RESOLVES
    with (a path) or REJECTS (the literal 'REJECT')."""
    proc = subprocess.run(
        [NODE, str(LANDING_HARNESS), str(index), str(CASE_STUDIES_PATH), str(roster)],
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, f"landing harness failed: {proc.stderr}"
    return json.loads(proc.stdout)


def _roster_on_disk() -> dict:
    return json.loads(ROSTER_PATH.read_text(encoding="utf-8"))


# --- the arms, as functions, so a mutant page goes through the SAME checker -------------
def _check_the_card_names_exactly_the_published_roster(landing: dict, roster: dict,
                                                       label: str) -> None:
    published = _published_accounts(roster)
    assert len(published) >= _MIN_ROSTER, (
        f"{label}: the roster publishes {len(published)} accounts -- below the floor of "
        f"{_MIN_ROSTER}, so every check in this section would pass vacuously"
    )
    assert landing["rosterSlotInDocument"], (
        f"{label}: the landing document has no roster slot at all, so the account list is "
        f"either written down somewhere this control cannot see, or missing"
    )
    rendered = _rendered_accounts(landing["rosterHint"])
    missing = sorted(published - rendered)
    invented = sorted(rendered - published)
    assert not missing, (
        f"{label}: the landing card does not name these published accounts, and the page's "
        f"own arrows will cycle a reader into them: {missing}"
    )
    assert not invented, (
        f"{label}: the landing card names accounts the published roster does not carry: "
        f"{invented}"
    )


def _check_the_card_moves_with_the_roster(index: Path, tmp: Path, label: str) -> None:
    """INDEPENDENCE. A list pinned into the page would satisfy the equality arm above for
    exactly as long as the roster stands still -- which is what the shipped defect did for
    six days. Move the roster; the card must move with it."""
    roster = _roster_on_disk()
    extra = "C_ROSTER_PROBE_1"
    assert extra not in _published_accounts(roster), "probe id collides with a real account"
    roster["customers"] = roster["customers"] + [
        {"customer_group": extra, "legs": {"electricity": {"cid": extra}}}
    ]
    moved = tmp / "roster_moved.json"
    moved.write_text(json.dumps(roster), encoding="utf-8")
    rendered = _rendered_accounts(_landing_with_roster(index, moved)["rosterHint"])
    assert extra in rendered, (
        f"{label}: an account added to the roster did not appear on the landing card -- the "
        f"card is not reading the roster, it is repeating a list that happens to match it"
    )


def _check_an_unreadable_roster_is_refused_not_guessed(index: Path, roster: dict,
                                                       label: str) -> None:
    """FAIL-CLOSED. With the artefact unreadable the card must name NOTHING and say so."""
    landing = _landing_with_roster(index, "REJECT")
    hint = landing["rosterHint"] or ""
    named = sorted(a for a in _published_accounts(roster) if a in hint)
    assert not named, (
        f"{label}: with the roster unreadable the landing card still named accounts "
        f"{named} -- a fallback literal is the shipped defect wearing a contingency label"
    )
    assert not _rendered_accounts(hint), f"{label}: an account list survived an unreadable roster"
    assert "will not list the accounts" in hint, (
        f"{label}: an unreadable roster produced neither a list nor a refusal, so a reader "
        f"cannot tell a short roster from a broken one: {hint[:200]!r}"
    )


def _check_the_two_published_populations_agree(roster: dict, label: str) -> None:
    """The card can only be as honest as the artefact it reads. If the roster the page
    fetches and the per-account files the site serves ever disagree, the card under-reports
    again -- truthfully, from a partial source."""
    files = set(json.loads(ACCOUNT_FILES_INDEX.read_text(encoding="utf-8")))
    published = _published_accounts(roster)
    assert files == published, (
        f"{label}: /data/customers.json and /data/customers/_index.json publish different "
        f"populations. Served as files but not in the roster the card reads: "
        f"{sorted(files - published)}; in the roster with no file to open: "
        f"{sorted(published - files)}"
    )


# --- the arms, live ---------------------------------------------------------------------
def test_the_landing_card_names_exactly_the_published_roster():
    roster = _roster_on_disk()
    _check_the_card_names_exactly_the_published_roster(
        _landing_with_roster(INDEX, ROSTER_PATH), roster, "the live page")


def test_the_landing_card_moves_when_the_roster_moves(tmp_path):
    _check_the_card_moves_with_the_roster(INDEX, tmp_path, "the live page")


def test_an_unreadable_roster_is_refused_rather_than_guessed():
    _check_an_unreadable_roster_is_refused_not_guessed(INDEX, _roster_on_disk(), "the live page")


def test_the_roster_and_the_served_account_files_publish_one_population():
    _check_the_two_published_populations_agree(_roster_on_disk(), "the published artefacts")


# --- R15: each mutation kills a NAMED arm, and the others are asserted GREEN on it -------
def _mutant(tmp: Path, old: str, new: str, name: str = "index.html") -> Path:
    src = INDEX.read_text(encoding="utf-8")
    assert src.count(old) == 1, f"mutation precondition: {old!r} appears {src.count(old)} times"
    out = tmp / name
    out.write_text(src.replace(old, new, 1), encoding="utf-8")
    return out


def test_mutation_a_card_that_drops_an_account_kills_the_equality_arm(tmp_path):
    """Direction 1: the shipped defect itself -- an account the roster carries and the card
    does not name."""
    mutant = _mutant(tmp_path, "(groups||[]).forEach(function(g){",
                     "(groups||[]).slice(0,-1).forEach(function(g){")
    roster = _roster_on_disk()
    with pytest.raises(AssertionError, match="does not name these published accounts"):
        _check_the_card_names_exactly_the_published_roster(
            _landing_with_roster(mutant, ROSTER_PATH), roster, "dropped-account mutant")
    # the fail-closed arm is GREEN on it: proving one arm twice is not proving two arms
    _check_an_unreadable_roster_is_refused_not_guessed(mutant, roster, "dropped-account mutant")


def test_mutation_a_card_that_invents_an_account_kills_the_equality_arm(tmp_path):
    """The opposite direction. A card may not name an account that cannot be opened."""
    mutant = _mutant(tmp_path, "var elec=[],gas=[];", 'var elec=["C_NOT_A_REAL_ACCOUNT"],gas=[];')
    with pytest.raises(AssertionError, match="does not carry"):
        _check_the_card_names_exactly_the_published_roster(
            _landing_with_roster(mutant, ROSTER_PATH), _roster_on_disk(), "invented-account mutant")


def test_mutation_a_literal_fallback_on_an_unreadable_roster_kills_the_failclosed_arm(tmp_path):
    """FAIL-OPEN, the direction that would quietly restore the whole defect: the roster is
    unreachable and the page answers from a list typed into it anyway."""
    mutant = _mutant(
        tmp_path,
        'if(!elec.length&&!gas.length)return "<span class=\\"red\\">"+esc(ROSTER_HINT_UNAVAILABLE)+"</span>";',
        'if(!elec.length&&!gas.length)return "Electricity: C1, C2<br>Gas: C1g";',
    )
    roster = _roster_on_disk()
    with pytest.raises(AssertionError, match="still named accounts"):
        _check_an_unreadable_roster_is_refused_not_guessed(mutant, roster, "literal-fallback mutant")
    # and the equality arm is GREEN on it -- with the roster READABLE this page is correct,
    # which is exactly why a fail-closed arm has to exist separately.
    _check_the_card_names_exactly_the_published_roster(
        _landing_with_roster(mutant, ROSTER_PATH), roster, "literal-fallback mutant")


def test_mutation_a_pinned_list_that_happens_to_match_kills_the_independence_arm(tmp_path):
    """TAUTOLOGY, R15's first killer pattern: a card that returns today's roster as a
    string. It satisfies the equality arm perfectly -- asserted below -- and is blind to
    every future change, which is precisely the state the page shipped in."""
    pinned = _landing_with_roster(INDEX, ROSTER_PATH)["rosterHint"]
    assert pinned and "SYN-2021-001" in pinned, "precondition: the live card renders the roster"
    mutant = _mutant(
        tmp_path, "function rosterHintHtml(groups){",
        "function rosterHintHtml(groups){return " + json.dumps(pinned) + ";",
    )
    with pytest.raises(AssertionError, match="repeating a list that happens to match"):
        _check_the_card_moves_with_the_roster(mutant, tmp_path, "pinned-list mutant")
    _check_the_card_names_exactly_the_published_roster(
        _landing_with_roster(mutant, ROSTER_PATH), _roster_on_disk(), "pinned-list mutant")


def test_mutation_an_emptied_roster_refuses_rather_than_passing(tmp_path):
    """FAIL-OPEN on the SUBJECT rather than the page: an empty roster makes every arm above
    trivially satisfiable, so the anti-vacuity floor must REFUSE it."""
    with pytest.raises(AssertionError, match="below the floor"):
        _check_the_card_names_exactly_the_published_roster(
            _landing_with_roster(INDEX, ROSTER_PATH), {"customers": []}, "emptied roster")


def test_null_control_the_live_page_and_roster_pass_every_arm(tmp_path):
    """Without this these five checkers could be `assert False` in five costumes."""
    roster = _roster_on_disk()
    _check_the_card_names_exactly_the_published_roster(
        _landing_with_roster(INDEX, ROSTER_PATH), roster, "null control")
    _check_the_card_moves_with_the_roster(INDEX, tmp_path, "null control")
    _check_an_unreadable_roster_is_refused_not_guessed(INDEX, roster, "null control")
    _check_the_two_published_populations_agree(roster, "null control")


def test_the_landing_card_as_it_shipped_denied_a_published_account(tmp_path):
    """R15 direction 5: the page AS IT SHIPPED, located by the module's sole locator.

    The typed list covered C1-C9 as a range, so a substring census over it would report
    most accounts 'missing' and prove nothing. SYN-2021-001 is the one account no range in
    that list reaches -- it is the account that entered the roster after the list was
    written -- so the proof is that the shipped document does not contain it ANYWHERE while
    the roster it serves alongside does.
    """
    src = _pre_repair_source("rosterHintHtml")
    assert src is not None, (
        "cannot locate the committed page that predates the roster-driven card -- the "
        "shipped-defect proof did NOT run, which is not the same as passing"
    )
    shipped = tmp_path / "shipped.html"
    shipped.write_text(src, encoding="utf-8")
    landing = _landing_with_roster(shipped, ROSTER_PATH)
    assert not landing["rosterSlotInDocument"], (
        "the located revision already carries the roster slot -- it is not the pre-repair page"
    )
    published = _published_accounts(_roster_on_disk())
    assert "SYN-2021-001" in published, "precondition: the roster publishes SYN-2021-001"
    document = "".join(landing["views"].values())
    assert "SYN-2021-001" not in document, (
        "the page as it shipped DID name SYN-2021-001 -- this proof no longer describes a "
        "real defect and must be rewritten rather than left passing"
    )
    assert "Electricity: C1" in document, (
        "the page as it shipped did not render the typed list this section replaced, so "
        "the located revision is the wrong subject"
    )
