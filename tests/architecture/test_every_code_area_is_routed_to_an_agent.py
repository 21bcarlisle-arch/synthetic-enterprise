"""The defect: for four months the supplier's own code had no specialist agent.

The sub-agent descriptions in `.claude/agents/` were written on 2026-06-07 for a repo of `sim/`,
`saas/` and `interface/`. The tree grew `company/` (the supplier, the largest area) and
`simulation/` (the world's run loop and draws), and nothing checked the descriptions against it,
so routing sent neither anywhere. Found by the 2026-09-29 prompt audit.

KEYED TO THE TREE, NOT TO A LIST. "Holds a real share of the code" is measured from the files git
tracks at the moment the test runs, so a directory that grows past the threshold must be routed the
day it does, and nobody maintains an expected-directories list that could itself go stale.
"""
from __future__ import annotations

import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGENTS = ROOT / ".claude" / "agents"
#: A top-level directory holding at least this share of the product code (tracked Python outside
#: tooling and tests, which are routed by their subject) is a code area some agent must be routed to.
SHARE = 0.05
NOT_A_CODE_AREA = {"tests", "tools", "background", "site", "docs", ".claude", "functions"}


def _descriptions() -> dict[str, str]:
    out = {}
    for f in sorted(AGENTS.glob("*.md")):
        m = re.search(r"^description:\s*(.+)$", f.read_text(), re.M)
        if m:
            out[f.stem] = m.group(1)
    return out


def _python_share() -> dict[str, float]:
    files = subprocess.run(["git", "ls-files", "*.py"], cwd=ROOT, capture_output=True, text=True,
                           check=True).stdout.split()
    # The share is of PRODUCT code -- the directories agents are routed to -- not of the whole repo,
    # where the test suite dwarfs everything and a 104-file world package reads as 3%.
    counts = Counter(f.split("/")[0] for f in files if "/" in f and f.split("/")[0] not in NOT_A_CODE_AREA)
    total = sum(counts.values())
    return {d: n / total for d, n in counts.items()}


def _named_paths(text: str) -> set[str]:
    return {m.rstrip("/") for m in re.findall(r"`([A-Za-z0-9_./-]+)`", text) if "/" in m or m.endswith(".py")}


def _routes(text: str) -> set[str]:
    """The areas a description ROUTES work to: the paths named in its `Use for work inside ...` sentence."""
    m = re.search(r"Use for (?:any )?work inside ([^.]*)\.", text)
    return {p.split("/")[0] for p in _named_paths(m.group(1))} if m else set()


def test_every_code_area_holding_a_real_share_of_the_code_is_routed_to_an_agent():
    desc = _descriptions()
    share = _python_share()
    areas = {d for d, s in share.items() if s >= SHARE and d not in NOT_A_CODE_AREA}
    # Not vacuous: the areas this was written for are measured as areas at all.
    assert {"company", "simulation"} <= areas, (areas, share)
    # ROUTING IS THE SENTENCE THAT SENDS WORK, not any mention. A description may name an area to
    # say it never touches it ("never reads or writes `company/`") or to guard its seam; counting
    # those as routing let a description with no route to `company/` pass, which is the defect.
    routed = {d for d in areas for text in desc.values() if d in _routes(text)}
    unrouted = sorted(areas - routed)
    assert not unrouted, (
        f"code areas no agent description names: {unrouted} "
        f"(shares: { {d: round(share[d], 3) for d in unrouted} }). Route them in .claude/agents/.")


def test_every_path_a_description_names_exists():
    missing = {name: sorted(p for p in _named_paths(text) if not (ROOT / p).exists())
               for name, text in _descriptions().items()}
    missing = {k: v for k, v in missing.items() if v}
    assert not missing, f"agent descriptions name paths that do not exist: {missing}"
