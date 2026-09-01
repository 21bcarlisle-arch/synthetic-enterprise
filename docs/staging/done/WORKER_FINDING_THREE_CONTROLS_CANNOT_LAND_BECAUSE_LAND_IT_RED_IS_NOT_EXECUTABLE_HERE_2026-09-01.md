**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

**Class:** `uncommitted_and_orphaned_work` (existing class, so this instance is born archived).

# Three of the five controls are red at HEAD, and "land it red" is not a move this repo has

Lane 0 for 2026-09-01 said, of five controls sitting in the working tree and in no commit:
*"If a control is red at that commit, land it red with the blocking-set decision recorded — a
control held back until it is green is a control that does not exist."*

**That instruction is not executable here, and the refusal says so in as many words.**
`tools/pre_commit_test_gate.py` ends with `A red commit is structurally impossible (director P0,
2026-07-17)`. There is no known-red channel on the commit path — `tools/head_green_census.py` has a
`known_red` baseline, but it is a *reporting* baseline for the nightly HEAD census and nothing on the
pre-commit path reads it. So a control whose subject is another lane's uncommitted work cannot be
landed at all, red or otherwise, until that lane lands. **That is the mechanism which kept all five
of these in no commit**, and it is the thing to decide about — not the five files.

## The verdicts, by name, measured at a `git archive HEAD` checkout with the control copied in

| control | verdict | why |
|---|---|---|
| `tests/background/test_a_behind_origin_publish_refuses_instead_of_deepening_the_fork.py` | **GREEN** | landed `ea5e66c60` with its subject |
| `tests/tools/test_a_published_surface_is_reproducible_from_its_committed_input.py` | **GREEN** | landed `522f8b540`, after its input landed at `0247f3061`; RED at `6d80d4441` before that |
| `tests/saas/reporting/test_a_departure_route_carries_its_denominator.py` | **RED at HEAD**, 2 failures | subject is `saas/reporting/annual_report.py`, uncommitted (SVT reducer lane) |
| `tests/simulation/test_svt_assignment.py` | **RED at HEAD**, 1 failure (`test_the_year_level_anchor_does_not_scale_the_published_inertia_rate`) | subject is `simulation/renewals.py`, uncommitted since 2026-08-31 09:37 (C1b SVT-roll lane) |
| `tests/tools/test_settlement_ceiling_probe.py` | **RED at HEAD**, 11 failures, `AttributeError: module 'tools.settlement_ceiling_probe' has no attribute 'menu'` | subject is `tools/settlement_ceiling_probe.py`, uncommitted |

All three reds are the SAME shape and none is a defect in the control: each names a subject that is
on disk and in no commit. Landing them means landing three different lanes' in-flight work under
this seat's message — a world-behaviour change (`simulation/renewals.py` decides who rolls to SVT),
a report reducer, and a probe. That is a bigger call than this direction authorises and it is not
one to take unattended, so it was not taken.

## What the ruff ratchet cost, because it is the same class one level up

`tests/architecture/test_static_quality_ratchet.py` is a SAFETY-CONTROL in
`tools/pre_commit_test_gate.py` — run on every commit staging a `CODE_PREFIX` path — and
`real_ruff_counts()` lints `REPO_ROOT`, the shared **working tree**, while
`test_ruff_no_stale_baseline_entries` demands exact equality with the frozen floor. So the moment any
lane holds an uncommitted lint improvement, every code commit in the tree is refused. On this morning
that lane was `simulation/renewals.py` (I001 1336 at HEAD, 1335 in the tree), and the previous seat's
own entry recorded the 1335 reading and deliberately pinned the floor to HEAD's 1336 — leaving the
tree red, which is why that seat's commit, the divergence guard it was written for, and four other
controls were all still uncommitted six hours later. Banked at 1335 in `ea5e66c60` with the trade
stated in the shrink log: HEAD reads 1336 against it until the renewals lane lands, and HEAD was
already red on two tests in that file before, so the red count at HEAD does not move.

The docs-only publish commits that kept landing all through are exactly the ones that stage no
`CODE_PREFIX` and never ran it. **A gate that only the blocked lanes trigger looks green from the
outside for as long as nobody needs it.**

## What is owed, and it is a decision rather than a build

Either (a) the three subject lanes land their own work, at which point their controls land with them
and this closes itself; or (b) the pre-commit path grows a way to record a control as landed-red with
its blocking set — which is a real change to a director P0 and belongs to him, not to a worker tick.
Recommending (a) and doing nothing about (b): the three lanes are live, not abandoned, and (b) buys a
mechanism for a problem that goes away when they land.

Separately and smaller: `docs/design/wall_channel_census_baseline.json` is still uncommitted, blocked
on the SVT lane's two unruled channel-F crossings (`svt_decisions`, `svt_departures` into
`saas/reporting/annual_report.py`). Ruling another lane's crossings to clear my own gate would be the
amnesty that list forbids.
