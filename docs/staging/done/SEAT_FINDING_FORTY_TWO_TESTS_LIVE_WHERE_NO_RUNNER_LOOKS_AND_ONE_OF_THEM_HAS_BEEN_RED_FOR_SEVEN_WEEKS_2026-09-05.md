**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# FINDING: forty-two tests live where no runner looks, and one of them has been red for seven weeks

**Measured 2026-09-05, delivery seat, from an isolated worktree at `1a03c893d`. Claim id
`register-low-water-evidence-convergence-sweep`. Found by pointing
`tools/converged_contract_screen.py` (landed `1a03c893d`) at its own population — this is the
sweep's first result, not a separate investigation.**

---

## How the screen surfaced it

The screen ranked `tools/generate_company_data.py` as the sharpest instance of the class it was
built to find: **4 first-party callers, 194 test files reaching it transitively, 0 naming it.**
That is the `ops_repo` shape — a converged module whose contracts stand on nothing.

The expected answer was "no suite was ever written". It is the opposite. The screen's own caller
list gave it away:

    callers:
      background.process_run_complete
      tools.generate_dashboard_data
      tools.generate_world_data
      tools.test_generate_company_data        <-- a TEST file, counted as a CALLER

A dedicated suite exists. It lives in `tools/`, not `tests/`, so no runner collects it and the
screen correctly classified it as production code — because **that is what it is to the gate.**

## What is actually there

Five `test_*.py` files under `tools/`. **Four of them are real suites carrying 42 tests; the
fifth is not a test file at all:**

| file | tests collected |
|---|---|
| `tools/test_generate_company_data.py` | 16 |
| `tools/test_generate_regulatory_data.py` | 11 |
| `tools/test_generate_decisions_data.py` | 8 |
| `tools/test_generate_market_data.py` | 7 |
| `tools/test_execution_metric.py` | **0** — a tool that measures test execution, named `test_*` |

That last row is worth its line: it is a production module whose filename matches pytest's default
`test_*.py` collection pattern. It collects clean today, but it is the reason a
"just point a runner at `tools/`" repair is not free — the directory is not a test directory and
one of its files only looks like one.

They are not stubs. `tools/test_generate_company_data.py` carries R15 in its own docstring
("a control must be able to FAIL") and names its defect per test —
`test_arrears_mutation_of_one_balance_moves_distribution_r15`,
`test_arrears_fail_closed_on_empty_ledger_r15`, `test_no_goal_seek_reads_only_cost_to_serve_r12`.
This is careful work by the standards of this tree. Nothing has ever run it.

## Why nothing runs them, stated exactly

There is **no pytest configuration in this repository, and no file that could hold one**: at the
repo root there is no `pyproject.toml`, no `pytest.ini`, no `setup.cfg`, no `tox.ini` and no
`conftest.py`, and `testpaths` appears in no `.toml`, `.ini` or `.cfg` anywhere in the tree.
Collection is therefore determined **entirely** by the path each runner passes — there is no
default that could rescue a misplaced file. There are three test locations and two runners:

| location | runner |
|---|---|
| `tests/**` | `tools/head_green_census.py` → `pytest tests/`, and the pre-commit test gate |
| `site/test_*.py` | `tools/site_lane_gate.py` → `pytest <ROOT>/site` |
| **`tools/test_*.py`** | **nothing** |

Grepping the whole tree for `tools/test_` or `tools.test_` returns **no runner, no systemd unit,
no timer, no git hook** — every hit is prose referring to `tests/tools/test_*`, the correct
directory. The convention is real and these five files are simply on the wrong side of it. There
are **no name collisions** in `tests/tools/`, so nothing forced them there.

## The consequence, measured

Run by hand: **41 pass, 1 fails.**

    FAILED tools/test_generate_regulatory_data.py::test_live_cache_matches_regeneration
    AssertionError: module_count drifted: cache=63 fresh=67

The test's own section header is `# the live emitted cache is self-consistent (defends against a
stale commit)`. **It is a control written for precisely this failure, and it has never been in a
position to report it.**

`site/data/regulatory.json` is stamped `2026-07-18T19:30:45Z` — seven weeks. Its generator
`tools/generate_regulatory_data.py` has **no caller**: nothing in `background/` or `tools/`
invokes it, so the feed has not been regenerated since, and `company/regulatory/` has gained
modules meanwhile.

## What this does NOT establish, and the overclaim I am not making

**No reader sees the stale figure.** No HTML or JavaScript under `site/` reads
`regulatory.json`; the only references anywhere are the generator, its uncollected test, a
comment in `site/test_evidence_links_resolve.py`, and prose in three documents. So this is a dead
artefact with a stale number, **not a wrong figure on the director's surface**, and it must not be
written up as one. Severity is BLOCKING for the collection gap, which is live and general, not for
the drifted count, whose blast radius today is zero.

Nor does this establish anything about the other 41. They pass **today, run by hand, in this
worktree**. Whether they were passing last week is unknown and unknowable: there is no record,
because there was no runner.

## The shape, stated generally — a third species

The sweep has now found three distinct ways convergence and evidence come apart, and they need
different repairs:

1. **`register_low_water` (`38871422b`) — the evidence did not move with the code.** Four caller
   suites; the shared module inherited whichever happened to be strongest; one contract proved by
   none.
2. **`ops_repo` (`befe26b7e`) — the REPAIR stayed at the call sites.** Two callers hand-rolled the
   same guard, the third had none, and the shared function had no test at all.
3. **`generate_company_data` (here) — the evidence exists and the runner cannot see it.** This one
   is invisible to every instrument the previous two would have used, because a test-count, a
   coverage figure and a "does a suite exist?" grep all answer *yes*.

Species 3 is the worst of the three to detect and the cheapest to fix, which is a bad combination:
nothing was ever going to notice, and nothing had to.

## The repair, and why it is NOT applied here

**`git mv` alone is NOT the repair, and I checked before writing that it was.** There are no name
collisions in `tests/tools/`, but three of the four suites are **location-dependent**:

    PROJECT = Path(__file__).resolve().parent.parent    # the repo root -- only from tools/
    sys.path.insert(0, str(PROJECT))
    sys.path.insert(0, str(PROJECT / "tools"))
    import generate_market_data as G

`tools/` has no `__init__.py`, so `tools.generate_company_data` resolves only as a namespace
package from the repo root — which is why one suite imports that way and the other three reach for
`sys.path` instead. Moved to `tests/tools/`, `parent.parent` becomes `<root>/tests` and the bare
import fails. The move therefore also needs `parent.parent` → `parent.parent.parent` in three
files. Small, but a `git mv` that looked free and is not, and worth the line because **the obvious
repair would have failed at collection and read as "these tests were broken all along."**

It is deliberately not done in this commit, per SELF_INTERRUPT_DISCIPLINE and because **the move
would red the tree on its first collection** — which is the correct outcome and exactly why it must
be a decision rather than a drive-by. Landing it requires deciding the drifted feed at the same time,
and there are three honest routes, which is one too many for a turn that found this by accident:

* **regenerate** `site/data/regulatory.json` — but nothing calls the generator, so the feed goes
  stale again the same day, and this buys a green test rather than a working mechanism;
* **give the generator a caller** — the real repair for a dead feed, and a larger change than this
  finding's subject;
* **delete the feed and its generator** — defensible: nothing reads it. That is a deletion of a
  published-shaped artefact and belongs to whoever owns Door 3, not to this sweep.

The collection gap should be closed regardless of which is chosen; the two decisions are
separable and only the second is contested.

## The instrument's own limit, restated because it nearly hid this

`tools/converged_contract_screen.py` treats `tests/**` as the test population and everything else
as production. That is why it found this — and it is also why it will **not** find the next one by
itself: a sixth test file appearing under `tools/` tomorrow is a new production module to the
screen, and its 0-direct-importer row looks exactly like a module that never had a suite. The
screen ranks; it cannot tell those two apart. Only opening the caller list does, which is what
happened here.
