"""D36 -- the printed bill foots ON ITS FACE, in pence, with its catch-up line shown.

THE DEFECT (director ruling THE PORTAL IS A WALL EXHIBIT, Part 1, 2026-08-12)
----------------------------------------------------------------------------
Bill C1g-INV141 (gas, Sep 2021) rendered four charge lines totalling about £26 above a
total of -£2, with nothing on the page saying where the sign came from. Every existing
control passed it, and each was right to: the RECORD carries a fifth component
(``catchup_adjustment_gbp = -28.40``), ``BILL_FOOTS`` sums that component, and
``PRINTED_BILL_FOOTS_EXACTLY`` checks the ledger's own line items. The renderer kept its
OWN line-up -- usage, standing charge, network, VAT -- which was the invariant's footing
set minus the one component that decides the sign, and it printed every figure through
``gbp()``, a PORTFOLIO formatter that rounds to whole pounds. So the page showed
``£12 + £8 + £5 + £1`` above ``-£2``: five wrong figures and a total nobody could
reconstruct, from a record that was correct throughout.

The class is therefore NOT "the bill does not foot" -- it is "the bill does not foot AS
PRINTED, and the checks all read the record". Which is why every assertion here runs the
PAGE'S OWN render functions (``_bill_render_harness.mjs`` drives the second inline script
in a VM against the real per-customer JSON) and parses the figures back out of the emitted
markup and the emitted PDF column. Reading the JSON and adding it up would pass while the
page stayed unreadable; re-implementing the renderer in Python would drift from the page
and pass while the page failed -- the tautology R15 names.

WHAT IS CHECKED, AND AGAINST WHAT
---------------------------------
* the renderer's component set IS the invariant's own set (both directions, so a sixth
  component added to ``_FOOTING_COMPONENT_KEYS`` cannot go unprinted);
* the catch-up line prints, labelled with the period it corrects, on screen AND in the
  PDF, on every catch-up bill in the population -- and on no ordinary one;
* the printed figure is the ledger's ``catchup_adjustment_gbp``, carried, never re-derived;
* the printed column adds to the printed total, to the penny;
* money on the bill path prints in pounds and pence, checked against genuinely
  non-integer values.

THE POPULATION, AND A DEFECT IT EXPOSES THAT IS NOT THIS ATOM'S TO FIX
---------------------------------------------------------------------
The page renders ``site/data/customers/*.json`` (21 accounts). ``PRINTED_BILL_FOOTS_EXACTLY``
runs on ``site/state/billing_ledger.json`` (18). The three accounts in the difference are
re-acquired accounts (``C1_2``, ``C2_2``, ``C5_2``), and 30 of their invoice RECORDS do not
foot by a penny -- a data defect the printed-footing invariant cannot see because those
accounts are outside its population. It is staged as its own finding, not fixed here (D36
is render-layer only, and SELF-INTERRUPT DISCIPLINE says queue it). What this module
therefore asserts is BOTH halves, kept separate so neither can hide the other:

* ``test_the_renderer_introduces_no_residual_of_its_own`` -- WHOLE population, zero
  tolerance: the gap between the printed column and the printed total is exactly the gap
  already in the record. This is the renderer's own obligation and it holds everywhere.
* ``test_the_printed_column_adds_up_on_every_bill_whose_record_foots`` -- the customer's
  test, exact, on every record that can pass it, with a floor on the population size so
  the exemption cannot quietly grow into a hole.

ANTI-PIN
--------
No RNG-derived value, count or date is pinned. The named record C1g-INV141 is checked when
it is present, and its check is a RELATIONSHIP (rendered figures reproduce the record's own
figures and foot), not the literal -2.43 -- a literal here would fire on a legitimate
re-run, which this repo has already paid four days of wedged publishing to learn (see
tests/tools/test_billing_tab_fix.py).
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from decimal import Decimal
from pathlib import Path

import pytest

from company.compliance.domain_invariants import _FOOTING_COMPONENT_KEYS

PROJECT = Path(__file__).resolve().parents[3]
PAGE = PROJECT / "site" / "customers" / "index.html"
HARNESS = PROJECT / "site" / "customers" / "_bill_render_harness.mjs"
CUSTOMER_DATA = PROJECT / "site" / "data" / "customers"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")

#: A printed money figure, as it must appear on a bill: pounds AND pence, always two
#: decimals, thousands separated. `-£28.40`, `£1,234.56`. Never `£12`.
MONEY = re.compile(r"-?£\d{1,3}(?:,\d{3})*\.\d{2}")

CATCHUP_KEY = "catchup_adjustment_gbp"
TOTAL_KEY = "amount_gbp"


# ---------------------------------------------------------------------------
# Reading the rendered surfaces back
# ---------------------------------------------------------------------------
def _money(token: str) -> Decimal:
    return Decimal(token.replace("£", "").replace(",", ""))


def _rows(screen_html: str) -> list[tuple[str, Decimal | None]]:
    """(label, amount) for every rendered row, in printed order.

    The amount is the LAST money token in the row's value cell, which is how a usage row
    (`422.7 kWh x 2.806p/kWh (gas) = £11.86`) states its charge. A row with no money token
    at all yields None rather than being dropped -- a line that should carry a figure and
    does not must be visible to the assertions, not silently skipped.
    """
    out = []
    for m in re.finditer(
        r'<div class="row"[^>]*><span class="rl">(.*?)</span><span>(.*?)</span></div>',
        screen_html,
        re.S,
    ):
        label, cell = m.group(1), m.group(2)
        tokens = MONEY.findall(cell)
        out.append((label, _money(tokens[-1]) if tokens else None))
    return out


def _pdf_lines(calls: list[dict]) -> list[tuple[str, Decimal | None]]:
    """(label, amount) for the PDF's charge column, paired by baseline."""
    by_y: dict[float, dict] = {}
    for c in calls:
        row = by_y.setdefault(c["y"], {})
        row["amount" if c["right"] else "label"] = c["text"]
    out = []
    for y in sorted(by_y):
        row = by_y[y]
        if "amount" not in row:
            continue
        tokens = MONEY.findall(row["amount"])
        out.append((row.get("label", ""), _money(tokens[-1]) if tokens else None))
    return out


def _total_row(rows: list[tuple[str, Decimal | None]]) -> tuple[str, Decimal | None]:
    totals = [r for r in rows if r[0].startswith("= Total")]
    assert len(totals) == 1, f"expected exactly one total row, got {[r[0] for r in rows]}"
    return totals[0]


def _charge_rows(rows: list[tuple[str, Decimal | None]]) -> list[tuple[str, Decimal | None]]:
    return [r for r in rows if not r[0].startswith("= Total")]


def _dec(value) -> Decimal:
    return Decimal(str(value))


def _record_components(inv: dict) -> Decimal:
    return sum(
        (_dec(inv[k]) for k in _FOOTING_COMPONENT_KEYS if inv.get(k) is not None),
        Decimal("0"),
    )


# ---------------------------------------------------------------------------
# Fixtures -- the page's own code, driven against the real population (R11)
# ---------------------------------------------------------------------------
def _customer_files() -> list[Path]:
    files = []
    for p in sorted(CUSTOMER_DATA.glob("*.json")):
        try:
            d = json.loads(p.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if isinstance(d, dict) and isinstance(d.get("invoices"), list) and d["invoices"]:
            files.append(p)
    assert files, "no per-customer JSON with invoices on disk -- every assertion would be vacuous"
    return files


def _render(page: Path) -> dict[str, dict]:
    """{invoice_id: {"screen": html, "pdf": [...], "record": invoice_dict}}."""
    files = _customer_files()
    proc = subprocess.run(
        [NODE, str(HARNESS), str(page), *[str(f) for f in files]],
        capture_output=True, text=True, timeout=300,
    )
    assert proc.returncode == 0, f"bill render harness failed: {proc.stderr[-4000:]}"
    out = json.loads(proc.stdout)
    records = {}
    for f in files:
        for inv in json.loads(f.read_text())["invoices"]:
            records[inv["id"]] = inv
    rendered = {}
    for acct in out["accounts"]:
        for inv in acct["invoices"]:
            rendered[inv["id"]] = {"screen": inv["screen"], "pdf": inv["pdf"], "record": records[inv["id"]]}
    assert rendered, "the harness rendered no bills -- every assertion below would be vacuous"
    return rendered


@pytest.fixture(scope="module")
def rendered() -> dict[str, dict]:
    return _render(PAGE)


@pytest.fixture(scope="module")
def page_source() -> str:
    return PAGE.read_text(encoding="utf-8")


def _catch_up_bills(rendered: dict) -> dict[str, dict]:
    return {k: v for k, v in rendered.items() if _dec(v["record"].get(CATCHUP_KEY) or 0) != 0}


# ===========================================================================
# (1) The renderer's component set IS the invariant's own set
# ===========================================================================
def test_the_component_set_is_the_invariants_own_set(page_source):
    """Exit criterion 2. The renderer must not keep a second, hand-maintained line-up:
    that is precisely how the catch-up component went unprinted -- the old renderer's
    four pushes WERE the footing set minus one, and nothing said so."""
    block = re.search(r"var BILL_COMPONENTS=\[(.*?)\n\];", page_source, re.S)
    assert block, "BILL_COMPONENTS is not declared in the page -- the column is hand-kept again"
    printed = re.findall(r'\{key:"([a-z_]+)"', block.group(1))
    assert len(printed) == len(set(printed)), f"a component is declared twice: {printed}"
    assert set(printed) == set(_FOOTING_COMPONENT_KEYS), (
        "the printed component set and BILL_FOOTS's footing set have diverged.\n"
        f"  printed but not footed: {sorted(set(printed) - set(_FOOTING_COMPONENT_KEYS))}\n"
        f"  footed but not printed: {sorted(set(_FOOTING_COMPONENT_KEYS) - set(printed))}\n"
        "A component in the total that is not on the page is the D36 defect exactly."
    )


def test_the_footing_set_still_contains_the_catch_up_component():
    """Anti-vacuity for the test above: if the catch-up key ever left the invariant, the
    set-equality check would pass a renderer that stopped printing it."""
    assert CATCHUP_KEY in _FOOTING_COMPONENT_KEYS


# ===========================================================================
# (2) The catch-up line prints, labelled, on both surfaces
# ===========================================================================
def test_a_catch_up_bill_prints_its_catch_up_line_on_screen(rendered):
    """Exit criterion 1, on-screen half."""
    catch_ups = _catch_up_bills(rendered)
    assert catch_ups, "no catch-up bill in the population -- this check would be vacuous"
    missing = []
    for inv_id, r in catch_ups.items():
        labels = [label for label, _ in _rows(r["screen"])]
        if not any("Catch-up adjustment" in label for label in labels):
            missing.append(inv_id)
    assert not missing, (
        f"{len(missing)}/{len(catch_ups)} catch-up bills printed no catch-up line "
        f"(e.g. {missing[:5]}) -- the component that decides the sign of the total is invisible"
    )


def test_a_catch_up_bill_prints_its_catch_up_line_in_the_pdf(rendered):
    """Exit criterion 1, PDF half. The downloaded statement is the artefact a customer
    keeps and disputes from; a line that is on screen and not in the PDF is worse than
    absent from both, because the two disagree."""
    catch_ups = _catch_up_bills(rendered)
    missing = [
        inv_id for inv_id, r in catch_ups.items()
        if not any("Catch-up adjustment" in label for label, _ in _pdf_lines(r["pdf"]))
    ]
    assert not missing, f"{len(missing)}/{len(catch_ups)} catch-up bills printed no catch-up line in the PDF"


def test_the_catch_up_line_names_the_period_it_corrects(rendered):
    """Exit criterion 1: 'naming the correcting period from catchup_period_start/
    catchup_period_end'. An adjustment whose period is not stated cannot be checked by
    the person it is charged to."""
    unnamed = []
    for inv_id, r in _catch_up_bills(rendered).items():
        rec = r["record"]
        start, end = rec.get("catchup_period_start"), rec.get("catchup_period_end")
        if not start or not end:
            continue
        label = next(label for label, _ in _rows(r["screen"]) if "Catch-up adjustment" in label)
        if start not in label or end not in label:
            unnamed.append((inv_id, label))
    assert not unnamed, f"catch-up lines that do not name their corrected period: {unnamed[:5]}"


def test_an_ordinary_bill_prints_no_catch_up_line(rendered):
    """Over-broadness check: a control that prints a catch-up line on every bill would
    pass the test above and be a different defect."""
    ordinary = {k: v for k, v in rendered.items() if _dec(v["record"].get(CATCHUP_KEY) or 0) == 0}
    assert ordinary, "every bill is a catch-up bill -- the check above proves nothing"
    spurious = [
        inv_id for inv_id, r in ordinary.items()
        if any("Catch-up adjustment" in label for label, _ in _rows(r["screen"]))
    ]
    assert not spurious, f"a catch-up line printed on bills that have no adjustment: {spurious[:5]}"


def test_the_printed_catch_up_figure_is_the_ledgers_own(rendered):
    """Exit criterion 4: carried through from catchup_adjustment_gbp, never re-derived.
    A re-derived figure (raw delta, or total-minus-the-other-four) agrees with the record
    on most bills and disagrees exactly where a write-off or a back-billing cap applies --
    which is the 86.1%-of-usage-lines lesson from D_printed_figure_rederivation."""
    wrong = []
    for inv_id, r in _catch_up_bills(rendered).items():
        expected = _dec(r["record"][CATCHUP_KEY])
        for surface, rows in (("screen", _rows(r["screen"])), ("pdf", _pdf_lines(r["pdf"]))):
            printed = [amt for label, amt in rows if "Catch-up adjustment" in label]
            if printed != [expected]:
                wrong.append((inv_id, surface, printed, expected))
    assert not wrong, f"printed catch-up figures that are not the ledger's: {wrong[:5]}"


# ===========================================================================
# (3) The column adds up on its face
# ===========================================================================
def test_the_renderer_introduces_no_residual_of_its_own(rendered):
    """Exit criterion 2, whole population, zero tolerance.

    The renderer's own obligation, isolated from the quality of the record: the gap
    between the printed column and the printed total must be EXACTLY the gap already in
    the record's own components. Any other value means the render layer dropped, added,
    duplicated or re-rounded a figure -- which is the D36 defect (-£28.40 dropped) and
    also the old whole-pound formatter (every line re-rounded).
    """
    offenders = []
    for inv_id, r in rendered.items():
        rows = _rows(r["screen"])
        printed_sum = sum((amt for _, amt in _charge_rows(rows) if amt is not None), Decimal("0"))
        _, printed_total = _total_row(rows)
        record_residual = _record_components(r["record"]) - _dec(r["record"][TOTAL_KEY])
        if printed_total is None or (printed_sum - printed_total) != record_residual:
            offenders.append((inv_id, printed_sum, printed_total, record_residual))
    assert not offenders, (
        f"{len(offenders)} bills where the printed column's residual is not the record's own "
        f"-- the render layer changed the arithmetic: {offenders[:5]}"
    )


def test_the_printed_column_adds_up_on_every_bill_whose_record_foots(rendered):
    """Exit criterion 2, the customer's own test: does this column add to that total.

    Restricted to records that foot, because 30 invoices on three re-acquired accounts
    (C1_2/C2_2/C5_2) carry a penny of record-level residual and sit OUTSIDE
    PRINTED_BILL_FOOTS_EXACTLY's population -- a data defect staged as its own finding,
    which no render-layer change can fix. The floor below stops that exemption growing
    into a hole that hollows this test out.
    """
    footing, checked, failures = 0, 0, []
    for inv_id, r in rendered.items():
        if _record_components(r["record"]) != _dec(r["record"][TOTAL_KEY]):
            continue
        footing += 1
        rows = _rows(r["screen"])
        printed_sum = sum((amt for _, amt in _charge_rows(rows) if amt is not None), Decimal("0"))
        _, printed_total = _total_row(rows)
        checked += 1
        if printed_sum != printed_total:
            failures.append((inv_id, str(printed_sum), str(printed_total)))
    assert failures == [], f"printed columns that do not add to their printed total: {failures[:5]}"
    assert footing >= 0.9 * len(rendered), (
        f"only {footing}/{len(rendered)} records foot -- the exemption has grown from a named "
        "30-invoice data defect into a hole big enough to hide a render defect in"
    )
    assert checked > 0


def test_the_pdf_column_adds_up_to_the_pdf_total(rendered):
    """The same test on the downloaded artefact. The PDF prints one usage line where the
    screen may print one per register, so it is checked in its own right rather than
    assumed equal to the screen."""
    failures = []
    for inv_id, r in rendered.items():
        if _record_components(r["record"]) != _dec(r["record"][TOTAL_KEY]):
            continue
        lines = _pdf_lines(r["pdf"])
        totals = [amt for label, amt in lines if label.startswith("Total")]
        charges = [amt for label, amt in lines if not label.startswith("Total") and amt is not None]
        if len(totals) != 1 or sum(charges, Decimal("0")) != totals[0]:
            failures.append((inv_id, [(label, str(amt)) for label, amt in lines]))
    assert failures == [], f"PDF columns that do not add to their printed total: {failures[:2]}"


# ===========================================================================
# (4) Pounds and pence
# ===========================================================================
def test_every_printed_bill_figure_carries_its_pence(rendered):
    """Exit criterion 3. Whole-pound rendering is the second half of the defect: it makes
    the column unfootable even when every component is on the page."""
    bad = []
    for inv_id, r in rendered.items():
        cells = re.findall(r'<div class="row"[^>]*>.*?<span>(.*?)</span></div>', r["screen"], re.S)
        for cell in cells:
            for token in re.findall(r"-?£[\d,.]+", cell):
                if not MONEY.fullmatch(token):
                    bad.append((inv_id, token))
    assert not bad, f"bill figures printed without their pence: {bad[:10]}"


def test_the_pence_actually_vary(rendered):
    """Anti-vacuity for the check above: `.00` on every bill would satisfy the regex and
    prove nothing. The atom asks for a genuinely non-integer value, e.g. -£2.43."""
    non_integer = 0
    for r in rendered.values():
        for _, amt in _rows(r["screen"]):
            if amt is not None and amt != amt.to_integral_value():
                non_integer += 1
    assert non_integer > 100, (
        f"only {non_integer} rendered figures carry non-zero pence -- the pence check is vacuous"
    )


def test_a_negative_total_prints_its_sign_and_its_pence(rendered):
    """The motivating shape: a credit bill whose total is negative because of the catch-up
    line. It must print as -£2.43, not -£2 and not £2.43."""
    credits = {
        inv_id: r for inv_id, r in rendered.items()
        if _dec(r["record"][TOTAL_KEY]) < 0
    }
    assert credits, "no credit bill in the population -- this check would be vacuous"
    for inv_id, r in credits.items():
        _, printed_total = _total_row(_rows(r["screen"]))
        assert printed_total == _dec(r["record"][TOTAL_KEY]), (
            f"{inv_id}: printed total {printed_total} is not the record's {r['record'][TOTAL_KEY]}"
        )
        expected = f"-£{abs(_dec(r['record'][TOTAL_KEY])):,.2f}"
        assert expected in r["screen"], (
            f"{inv_id}: the negative total is not printed as {expected} -- sign and pence, as written"
        )


def test_a_credit_bill_says_on_its_face_that_it_is_a_credit(rendered):
    """The ruling's actual complaint was 'nothing on the page explaining the sign'. The
    catch-up line explains WHERE the sign comes from; this says WHAT it means."""
    for inv_id, r in rendered.items():
        if _dec(r["record"][TOTAL_KEY]) < 0:
            assert "CREDIT" in r["screen"], f"{inv_id}: a negative total with no credit note on the page"


# ===========================================================================
# (5) The ruling's own motivating record
# ===========================================================================
def test_the_motivating_record_renders_its_five_lines_and_foots(rendered):
    """Exit criterion 6 -- C1g-INV141: four charge lines plus the catch-up line, summing
    to the record's own total, in pence.

    Checked as a RELATIONSHIP, not as the literal -2.43: the invoice id and the amount are
    both regenerable, and a pinned literal that fires on a legitimate re-run is a defect in
    the control (R12), which this repo has already paid four days of wedged publishing for.
    If the named record is gone, any bill of the same SHAPE -- positive charges, a negative
    catch-up, a negative total -- stands in, and the class vanishing entirely is a failure.
    """
    def shape(r):
        rec = r["record"]
        return _dec(rec.get(CATCHUP_KEY) or 0) < 0 and _dec(rec[TOTAL_KEY]) < 0

    subject_id = "C1g-INV141" if "C1g-INV141" in rendered and shape(rendered["C1g-INV141"]) else None
    if subject_id is None:
        candidates = [k for k, v in rendered.items() if shape(v)]
        assert candidates, (
            "no bill anywhere in the population has a negative total driven by a catch-up "
            "credit -- the shape the ruling was written about has vanished, so this check "
            "would pass vacuously"
        )
        subject_id = sorted(candidates)[0]

    r = rendered[subject_id]
    rec, rows = r["record"], _rows(r["screen"])
    charges = _charge_rows(rows)
    _, printed_total = _total_row(rows)

    assert len(charges) == 5, (
        f"{subject_id}: {len(charges)} charge lines printed, expected five (the four charge "
        f"components plus the catch-up line): {[label for label, _ in charges]}"
    )
    assert sum((amt for _, amt in charges), Decimal("0")) == printed_total == _dec(rec[TOTAL_KEY])
    assert printed_total != printed_total.to_integral_value(), (
        f"{subject_id}: the motivating record's total has no pence to check -- pick a sharper subject"
    )
    assert printed_total < 0 < sum(
        (amt for label, amt in charges if "Catch-up" not in label), Decimal("0")
    ), f"{subject_id}: no longer the sign-flip shape the ruling names"


# ===========================================================================
# R15 -- the controls must fire on their own named defects
# ===========================================================================
@pytest.fixture(scope="module")
def scratch():
    d = tempfile.mkdtemp(prefix="d36_mutation_")
    yield Path(d)
    shutil.rmtree(d, ignore_errors=True)


def _mutated_render(scratch: Path, name: str, source: str) -> dict[str, dict]:
    page = scratch / f"{name}.html"
    page.write_text(source, encoding="utf-8")
    return _render(page)


def test_mutation_dropping_the_catch_up_line_kills_a_named_test(scratch, page_source):
    """Direction 1: the exact defect -- the fifth component falls out of the printed set.
    It must kill BOTH the catch-up check and the footing check."""
    mutated, n = re.subn(
        r',\n\s*\{key:"catchup_adjustment_gbp"[^\n]*\}', "", page_source, count=1
    )
    assert n == 1, "the catch-up component could not be located to mutate it"

    rendered = _mutated_render(scratch, "no_catchup", mutated)
    with pytest.raises(AssertionError, match="printed no catch-up line"):
        test_a_catch_up_bill_prints_its_catch_up_line_on_screen(rendered)
    with pytest.raises(AssertionError, match="residual"):
        test_the_renderer_introduces_no_residual_of_its_own(rendered)
    with pytest.raises(AssertionError, match="do not add to their printed total"):
        test_the_printed_column_adds_up_on_every_bill_whose_record_foots(rendered)
    with pytest.raises(AssertionError, match="diverged"):
        test_the_component_set_is_the_invariants_own_set(mutated)


def test_mutation_reverting_the_bill_path_to_whole_pounds_kills_a_named_test(scratch, page_source):
    """Direction 2: the formatter half of the defect -- the bill path goes back to the
    portfolio formatter's zero decimals."""
    start = page_source.index("function billGbp(n){")
    end = page_source.index("\n}", start)
    body = page_source[start:end]
    assert "minimumFractionDigits:2,maximumFractionDigits:2" in body
    mutated = page_source[:start] + body.replace(
        "minimumFractionDigits:2,maximumFractionDigits:2",
        "minimumFractionDigits:0,maximumFractionDigits:0",
    ) + page_source[end:]

    rendered = _mutated_render(scratch, "whole_pounds", mutated)
    with pytest.raises(AssertionError, match="without their pence"):
        test_every_printed_bill_figure_carries_its_pence(rendered)
    with pytest.raises(AssertionError, match="vacuous"):
        test_the_pence_actually_vary(rendered)


def test_mutation_printing_the_uncapped_delta_kills_a_named_test(scratch, page_source):
    """Direction 3: the printed figure stops being the one the ledger APPLIED and becomes
    a plausible neighbour -- `catchup_raw_delta_gbp`, the correction before the
    back-billing cap.

    This is the realistic re-derivation defect on this page, and it is nearly invisible:
    the two fields agree on 139 of the 141 catch-up bills in the population. They diverge
    exactly where the cap bites -- i.e. on the customer who was over-billed furthest back,
    who would then be shown a credit the company is not actually giving them. A control
    that only counted catch-up LINES would pass this mutation; the carried-figure check is
    what fires.

    (The other re-derivation shape -- computing the adjustment as total-minus-the-other-
    four -- is NOT provable on today's population and is not claimed as proven: on every
    record that foots, that expression equals the carried figure to the penny by
    construction. `test_the_render_layer_does_not_re_derive_the_catch_up_figure` is the
    control for that shape, and it is a source control precisely because no output
    difference exists to observe.)
    """
    mutated = page_source.replace(
        '"</span><span>"+billGbp(i[c.key])+"</span></div>";',
        '"</span><span>"+billGbp(c.key==="catchup_adjustment_gbp"&&i.catchup_raw_delta_gbp!=null'
        '?i.catchup_raw_delta_gbp:i[c.key])+"</span></div>";',
    )
    assert mutated != page_source, "the re-derivation mutation did not apply"

    rendered = _mutated_render(scratch, "uncapped_delta", mutated)
    with pytest.raises(AssertionError, match="not the ledger's"):
        test_the_printed_catch_up_figure_is_the_ledgers_own(rendered)


def test_the_render_layer_does_not_re_derive_the_catch_up_figure(page_source):
    """Exit criterion 4 as a source control, for the shape no output can distinguish.

    The component row prints `i[c.key]` -- the ledger's own field, carried. If the
    renderer ever computes the adjustment instead (total minus the other four), the
    printed result is identical on every footing record, so only the source can tell.
    """
    row_fn = re.search(r"function billComponentRowHtml\(c,i\)\{(.*?)\n\}", page_source, re.S)
    assert row_fn, "billComponentRowHtml is gone -- the carried-figure path cannot be checked"
    body = row_fn.group(1)
    assert "billGbp(i[c.key])" in body, (
        "the component row no longer prints the ledger's own field -- a figure computed in "
        "the render layer is the D_printed_figure_rederivation defect, and on a footing "
        "record it is indistinguishable in the output"
    )
    assert not re.search(r"i\.amount_gbp\s*[-+]", body), (
        "the component row derives a component from the declared total"
    )

    # R15 for this control: it must fire on the derivation it exists to refuse.
    mutated = page_source.replace(
        "billGbp(i[c.key])",
        "billGbp(c.key===\"catchup_adjustment_gbp\"?(Number(i.amount_gbp)-Number(i.commodity_amount_gbp||0)"
        "-Number(i.standing_charge_gbp||0)-Number(i.non_commodity_amount_gbp||0)-Number(i.vat_gbp||0))"
        ":i[c.key])",
    )
    assert mutated != page_source
    with pytest.raises(AssertionError, match="no longer prints the ledger's own field"):
        test_the_render_layer_does_not_re_derive_the_catch_up_figure(mutated)


def test_the_controls_do_not_fire_on_the_unmutated_page(rendered, page_source):
    """The other half of R15: a control that fires on the real page is not a control,
    it is noise. Every assertion above is re-run here against the live page."""
    test_the_component_set_is_the_invariants_own_set(page_source)
    test_a_catch_up_bill_prints_its_catch_up_line_on_screen(rendered)
    test_the_printed_catch_up_figure_is_the_ledgers_own(rendered)
    test_the_renderer_introduces_no_residual_of_its_own(rendered)
    test_every_printed_bill_figure_carries_its_pence(rendered)
    test_the_pence_actually_vary(rendered)
