#!/usr/bin/env python3
"""R15 proof for the company-side network refusal (director ruling, 2026-08-18).

The control asserts a property that is FALSE TODAY, deliberately: four company-side modules
can reach a real endpoint, and the control is red until the seam is repaired. That makes the
mutations the only evidence it works at all — a red control proves nothing about its own
correctness, and "it is red because the defect is real" is exactly what a broken control
would also say.

So every test here drives a SYNTHETIC tree with a known answer:

  * a company module reaching an HTTP client through a sim module  -> MUST fire
  * the same shape but shelling `git`                              -> MUST NOT fire
  * the same shape but shelling `curl`                             -> MUST fire
  * a company module with no route at all                          -> MUST NOT fire
  * an empty or unreadable scan                                    -> MUST RAISE
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tools import company_network_isolation as iso


def _tree(root: Path, files: dict[str, str]) -> None:
    for rel, body in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")


DIRS = ("company", "sim")


def test_MUTATION_a_transitive_http_route_fires(tmp_path):
    """The real breach's shape: company -> sim module -> requests. A control that only
    looked for `import requests` under company/ would be green here, over a live route."""
    _tree(tmp_path, {
        "company/__init__.py": "",
        "company/interfaces/__init__.py": "",
        "company/interfaces/seam.py": "from sim.prices import fetch\n",
        "sim/__init__.py": "",
        "sim/prices.py": "import requests\ndef fetch(): return requests.get('https://x')\n",
    })
    found = iso.violations(str(tmp_path), DIRS)
    assert [v["module"] for v in found] == ["company.interfaces.seam"], found
    assert found[0]["how"] == "http client"
    assert found[0]["path"][-1] == "sim.prices"


def test_MUTATION_a_shell_to_a_network_binary_fires(tmp_path):
    """`company.compliance.internal_audit` shells curl at a URL held in a module constant.
    Leaving subprocess out of the capability set would have missed it entirely."""
    _tree(tmp_path, {
        "company/__init__.py": "",
        "company/audit.py": 'import subprocess\nURL="http://x"\nsubprocess.run(["curl", URL])\n',
        "sim/__init__.py": "",
    })
    found = iso.violations(str(tmp_path), DIRS)
    assert [v["module"] for v in found] == ["company.audit"], found
    assert "curl" in found[0]["how"]


def test_MUTATION_a_shell_to_git_does_NOT_fire(tmp_path):
    """The precision call. `saas.reporting.annual_report` shells `git`, which is not a route
    to any endpoint. Counting every subprocess import would fail it forever, and a control
    that cries wolf is one people learn to route around."""
    _tree(tmp_path, {
        "company/__init__.py": "",
        "company/report.py": 'import subprocess\nsubprocess.run(["git", "log"])\n',
        "sim/__init__.py": "",
        "sim/x.py": "import requests\n",
    })
    assert iso.violations(str(tmp_path), DIRS) == []


def test_a_company_module_with_no_route_does_not_fire(tmp_path):
    """The target state, so the control is known to be able to pass. Without this the suite
    could not distinguish 'correctly red' from 'always red'."""
    _tree(tmp_path, {
        "company/__init__.py": "",
        "company/billing.py": "from company.model import price\n",
        "company/model.py": "def price(): return 1\n",
        "sim/__init__.py": "",
        "sim/world.py": "import requests\n",
    })
    assert iso.violations(str(tmp_path), DIRS) == []


def test_the_route_survives_an_extra_hop(tmp_path):
    """Transitivity is the whole point: the live breach runs company -> seam -> sim -> net,
    and a two-hop-only walk would miss the next one."""
    _tree(tmp_path, {
        "company/__init__.py": "",
        "company/a.py": "from company.b import go\n",
        "company/b.py": "from sim.c import go\n",
        "sim/__init__.py": "",
        "sim/c.py": "from sim.d import go\n",
        "sim/d.py": "import httpx\ndef go(): pass\n",
    })
    found = {v["module"] for v in iso.violations(str(tmp_path), DIRS)}
    assert found == {"company.a", "company.b"}, found


def test_MUTATION_FAIL_OPEN_a_scan_that_finds_no_network_raises(tmp_path):
    """An empty answer here means the scan is looking in the wrong place, not that the
    repository is offline. Reporting 'no violations' from a scan that found no network at
    all is the fail-open this control cannot afford."""
    _tree(tmp_path, {"company/__init__.py": "", "company/x.py": "x = 1\n",
                     "sim/__init__.py": ""})
    with pytest.raises(iso.IsolationUnavailable):
        iso.violations(str(tmp_path), DIRS)


def test_the_live_repository_is_red_with_named_routes():
    """The state of the real tree, asserted so a silent repair is noticed too. If this ever
    turns green, the seam was fixed and this test should be replaced by one asserting the
    property holds -- not deleted."""
    found = iso.violations()
    assert found, "the company layer now has no route out -- replace this with the green assertion"
    modules = {v["module"] for v in found}
    assert "company.interfaces.sim_interface" in modules, (
        "the seam's price fallback is the known route; if it is gone, say so here"
    )
    for v in found:
        assert v["how"], f"{v['module']} is reported with no explanation of how"
        assert v["path"][-1] != v["module"] or v["hops"] == 0


# ---------------------------------------------------------------------------
# The ratchet: known routes frozen, growth refused
# ---------------------------------------------------------------------------
def test_the_gate_is_green_on_the_known_routes():
    """The tree is not held hostage to four routes while the seam repair is designed."""
    assert iso.gate_violations() == []


def test_the_baseline_is_exactly_the_routes_that_exist():
    """Shrink-only in both directions: an unfrozen route is new debt, a frozen one that is
    gone is stale credit. Either makes the count meaningless."""
    live = {v["module"] for v in iso.violations()}
    assert live == set(iso.KNOWN_ROUTES), (
        f"live={sorted(live)} frozen={sorted(iso.KNOWN_ROUTES)}"
    )


def test_every_frozen_route_says_what_it_is():
    for module, why in iso.KNOWN_ROUTES.items():
        assert len(why) > 30, f"{module} is frozen with no explanation of the route"


def test_MUTATION_a_new_route_fails_the_gate(monkeypatch):
    """The property the gate exists for. Drop one entry from the baseline and the route it
    covered must read as new."""
    trimmed = dict(iso.KNOWN_ROUTES)
    victim = trimmed.pop("company.portal.app")
    assert victim
    monkeypatch.setattr(iso, "KNOWN_ROUTES", trimmed)
    problems = iso.gate_violations()
    assert any("NEW ROUTE" in p and "company.portal.app" in p for p in problems), problems


def test_MUTATION_a_stale_baseline_entry_fails_the_gate(monkeypatch):
    """The half a debt register usually lacks: an entry that has been discharged and still
    sits there claiming the credit."""
    padded = dict(iso.KNOWN_ROUTES)
    padded["company.imaginary"] = "a route that does not exist, frozen anyway"
    monkeypatch.setattr(iso, "KNOWN_ROUTES", padded)
    problems = iso.gate_violations()
    assert any("STALE BASELINE" in p and "company.imaginary" in p for p in problems), problems
