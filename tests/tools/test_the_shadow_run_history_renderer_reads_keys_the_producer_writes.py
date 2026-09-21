"""A renderer of the published run history may only read keys the producer actually writes.

THE DEFECT THIS CONTROLS, measured 2026-09-20 on the committed page, not inferred.
`tools/generate_shadow_html.build_project` read `r.get("git", "")`, `r.get("date", "")` and
`r.get("net_gbp", 0)` off each entry of `dashboard.json`'s `run_history`. The producer chain --
`generate_insights.append_run_history` builds the entry, `generate_dashboard_data.
extract_run_history` passes it through untouched -- has only ever written `git_hash`,
`generated_at` and `net_margin_gbp`. All three reads missed. Every row rendered
blank / blank / `&pound;0`, and `docs/shadow/project/index.html` is COMMITTED and is served by
`.github/workflows` GitHub Pages, which uploads `docs/` whole. Ten rows of "£0 net margin" had
been public since 2026-08-20.

NOTHING COULD NOTICE, and that is the shape worth a control rather than three edits. `.get` with
a default never raises; the money column's default was `0`, which is a *plausible* figure, so the
page read as a working page showing a flat run. This is `tools/structural_blank_guard.py`'s ARM 2
(`d.get(k, 0)` -- substitutes on a MISSING KEY) on a field that guard's registry does not cover,
because its registry is derived from the nullable-CLV producer and this is a different producer.

KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. `test_..._are_keys_the_producer_writes` derives the
permitted key set from `generate_insights.append_run_history`'s own `entry = {...}` literal. Add a
sixth field to the ledger tomorrow and the renderer may read it with no edit here; rename one and
this reds. A control listing today's three names would go green on a rename that broke the page.
"""

import ast
import inspect
import json
from pathlib import Path

import pytest

from tools import generate_dashboard_data as gdd
from tools import generate_insights as gi
from tools import generate_shadow_html as gsh

PROJECT = Path(__file__).resolve().parents[2]


def _producer_entry_keys():
    """The literal keys `append_run_history` writes into a ledger entry, from its own AST.

    FAIL-CLOSED ON ITS OWN SUBJECT. An empty set would make the membership leg below vacuous --
    every read key is trivially in nothing to violate -- so an empty set RAISES here rather than
    returning. If the entry stops being a dict literal, this control must go red and be rewritten,
    not silently start passing everything.
    """
    tree = ast.parse(inspect.getsource(gi.append_run_history))
    keys = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
            for k in node.value.keys:
                if isinstance(k, ast.Constant) and isinstance(k.value, str):
                    keys.add(k.value)
    if not keys:
        raise AssertionError(
            "no string-keyed dict literal found in append_run_history -- the producer's entry "
            "shape has moved and this control can no longer derive what a renderer may read")
    return keys


def _renderer_read_keys():
    """Every literal key `build_project` reads off a run-history entry.

    Scoped to the `for r in run_hist` loop so the function's other `.get`s (on `build`) are not
    swept in: a control that judged those too would red for a reason the run-history producer
    cannot fix. Raises on an empty result for the same fail-closed reason as above.
    """
    fn = ast.parse(inspect.getsource(gsh.build_project)).body[0]
    loops = [n for n in ast.walk(fn)
             if isinstance(n, ast.For) and isinstance(n.target, ast.Name)
             and isinstance(n.iter, ast.Subscript)
             and isinstance(n.iter.value, ast.Name) and n.iter.value.id == "run_hist"]
    if len(loops) != 1:
        raise AssertionError(
            "expected exactly one `for ... in run_hist[...]` loop in build_project, found "
            "{} -- the renderer's shape has moved".format(len(loops)))
    loop = loops[0]
    var = loop.target.id
    keys = set()
    for node in ast.walk(loop):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "get"
                and isinstance(node.func.value, ast.Name) and node.func.value.id == var
                and node.args and isinstance(node.args[0], ast.Constant)):
            keys.add(node.args[0].value)
    if not keys:
        raise AssertionError(
            "build_project reads no literal key off each run-history entry -- either the renderer "
            "changed shape or this control has stopped being able to see it")
    return keys


def test_the_keys_the_shadow_renderer_reads_are_keys_the_producer_writes():
    """THE CLASS. A read key the producer never writes is a blank rendered as a value."""
    written = _producer_entry_keys()
    read = _renderer_read_keys()
    unknown = sorted(read - written)
    assert not unknown, (
        "tools/generate_shadow_html.build_project reads {} off each run_history entry, and "
        "generate_insights.append_run_history writes {}. Those reads can only ever miss, and a "
        "miss renders as a blank or as the `.get` default -- which is how ten rows of "
        "'£0 net margin' reached docs/shadow/project/index.html. Read the producer's names, or "
        "change the producer.".format(unknown, sorted(written)))


def test_the_real_ledger_entry_reaches_the_rendered_page():
    """THE INSTANCE, end to end through the real producer -- the class leg above is satisfiable
    by a renderer that reads a correct key and then drops the value on the floor.

    MUTATION: revert any one of the three reads to its pre-2026-09-20 name and this reds naming
    the value that vanished."""
    entry = {
        "git_hash": "abc123def",
        "generated_at": "2026-09-20T11:22:33.444444+00:00",
        # A WHOLE number on purpose: `_gbp` formats to 0dp, so 123456.78 renders "123,457" and an
        # assertion on "123,456" would fail for the rounding rather than for the defect.
        "net_margin_gbp": 123456.00,
        "executive_summary": "",
        "headline_metrics": {},
    }
    html = gsh.build_project({"run_history": [entry], "build": {}}, "", "2026-09-20")
    assert "abc123def" in html, "the run's git hash is not on the page"
    assert "2026-09-20" in html, "the run's date is not on the page"
    assert "123,456" in html, (
        "the run's net margin is not on the page -- the money column is the one that published a "
        "manufactured zero")


def test_a_missing_money_key_renders_a_blank_and_never_a_zero():
    """THE DEFAULT IS THE DEFECT. `r.get("net_gbp", 0)` is what made three missed keys look like a
    working page instead of a broken one. An entry that carries no margin must render the em dash
    `_gbp(None)` already produces, never `£0`.

    MUTATION: restore any numeric default on the money read and this reds."""
    html = gsh.build_project(
        {"run_history": [{"git_hash": "deadbeef1", "generated_at": "2026-09-20T00:00:00+00:00"}],
         "build": {}}, "", "2026-09-20")
    row = html[html.index("deadbeef1"):]
    row = row[:row.index("</tr>")]
    assert "&#8212;" in row, "a missing net margin must render as a blank"
    assert "&pound;0" not in row, (
        "a missing net margin rendered as £0 -- a value the company does not believe, published "
        "as though it did")


def test_the_published_payload_still_carries_the_series_this_renderer_needs():
    """NON-VACUITY ON THE LIVE ARTEFACT. Both legs above pass fixtures in; if `run_history` were
    dropped from `site/data/dashboard.json` the renderer would have nothing to render and every
    assertion here would still be green. `run_history_total` WAS deleted from that payload on
    2026-09-20; this pins that the series was NOT, and names why.

    The series has two readers -- this renderer, and the non-vacuity leg of
    `tests/background/test_the_published_series_and_the_ledger_it_came_from_are_committed_
    together.py`. That is the whole reason the deletion was asymmetric."""
    path = PROJECT / "site" / "data" / "dashboard.json"
    if not path.exists():
        pytest.skip("no published dashboard in this tree")
    payload = json.loads(path.read_text())
    assert "run_history" in payload, (
        "site/data/dashboard.json no longer publishes run_history, so build_project renders an "
        "empty table and the committed-together control has nothing to check")
    assert "run_history_total" not in payload, (
        "run_history_total is back in the payload. It is `len()` of a 100-entry ring buffer "
        "published under a name that says 'total', it read exactly 100 for 81 days, and its "
        "renderer was deleted on 2026-08-20. If a run count is wanted again it needs a source "
        "that is not truncated -- and none exists; see the 2026-09-20 result document.")
    assert gdd.extract_run_history.__doc__, "the surviving reader lost its reason"
