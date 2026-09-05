**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# PRE-REGISTRATION: which caller suite is each `background/direction.py` contract standing on?

**Filed 2026-09-05 by the delivery seat, from an isolated worktree, BEFORE the battery was run and
before the baseline finished. Claim id `register-low-water-evidence-convergence-sweep`.**

---

## Why this subject

`38871422b` measured one converged mechanism (`background/register_low_water.py`, four callers) and
found that after convergence the shared module inherits whichever caller suite happened to be
strongest: one contract was proved by **no** suite and two by **one**. It filed the general
statement LATENT and nothing tested whether it generalises.

The drawn direction says to ask that question of every *other* converged mechanism. Asking it
properly is a mutation battery per subject, so the first thing needed is a population and a
ranking, and the second is one subject actually measured.

**The screen** (ad-hoc, run before this file was written; it is a proxy and its limits are stated
below). Over `background/ tools/ company/ saas/ simulation/ sim/`: build the first-party import
graph, call a module CONVERGED if ≥3 first-party modules import it, and call a suite DEDICATED if
the test filename names the module or the module is the only first-party import in the file.

    converged modules (>=3 first-party callers)   161
    of those, with NO dedicated suite              15
    of those 15, with no test importer at all       3
      simulation.run_phase3b_recalibration (6 callers)
      tools.generate_company_data          (4 callers)
      background.ops_repo                  (3 callers)

**The screen is a proxy and cannot answer the question.** It is blind to callers reached by
subprocess or dynamic dispatch; "has a dedicated suite" does not mean each contract is proved (the
low-water case had four caller suites and still a contract proved by nothing); and "no dedicated
suite" does not mean unproved. Only mutation, run per caller suite separately, answers it. The
screen's job is to rank, not to grade.

**Subject chosen: `background/direction.py`.** 4 first-party callers, 4 caller suites, no suite of
its own — structurally the same shape as the low-water case, at the same caller count. It steers
the draw, so a silently-unproved contract here changes what the whole machine works on. It also
states its contracts in prose unusually explicitly, and one of them
(`focus_multiplier`) carries a literal `MUTATION (must fire):` annotation — so the module asserts,
in writing, that a specific mutation is covered. Whether anything actually covers it is the
question.

Callers and their suites:

| caller | suite |
|---|---|
| `background/supervisor.py` | `tests/background/test_supervisor.py` |
| `background/delivery_lane.py` | `tests/background/test_delivery_lane.py` |
| `background/delivery_seat.py` | `tests/background/test_delivery_seat.py` |
| `tools/generate_delivery_page.py` | — (no suite imports it *and* direction) |

The fourth suite in the battery is
`tests/background/test_the_self_audit_declared_a_correction_and_nothing_carried_it.py`, which
imports `direction` directly and is the closest thing the module has to an own suite.

## Method, fixed here

Eight mutations, each applied **alone** to `background/direction.py`, each of the four suites run
**separately** so the answer is per-caller rather than one pass/fail. Every patch asserts its
target string is present **exactly once** before applying, so a survivor cannot be a patch that
never applied. `__pycache__` cleared between runs. Baseline green established first; any suite red
at baseline is excluded from scoring and said so.

## The mutations and the contract each one breaks

| # | contract, as the module states it | mutation |
|---|---|---|
| M1 | `focus_multiplier` is **ALWAYS >= 1.0** — direction may only ADD attention, never filter | non-focus atom returns `0.5` |
| M2 | `focus_weights` returns weights untouched when the two lists **disagree in length** | drop the length check |
| M3 | forbidden target-shaped keys are refused **at any depth** | `_forbidden_keys_in` stops recursing |
| M4 | an empty `not_now` is refused — *"the rejections are what makes it reviewable"* | accept empty `not_now` |
| M5 | `wrong[i].corrected` must be a **boolean**, not merely present | accept present-but-not-bool |
| M6 | `read_direction` **NEVER RAISES** — missing, unreadable and malformed are one answer | narrow `except Exception` to `except FileNotFoundError` |
| M7 | `is_live` is bounded **below** as well as above — a future-dated record must not steer | drop the `0.0 <=` bound |
| M8 | a legacy `wrong` row's correction state is `None`, **not** `False` — *"different claims"* | return `False` |

## Predictions, fixed before the run

Scored as written; not revised afterwards.

| # | prediction |
|---|---|
| M1 | **DIES**, in `test_supervisor.py` only |
| M2 | **SURVIVES all four** — a defensive branch tests rarely construct |
| M3 | **DIES**, in `test_delivery_seat.py` only |
| M4 | **DIES**, in `test_delivery_seat.py` only |
| M5 | **DIES**, in `test_the_self_audit...` only — that suite is named for this exact defect |
| M6 | **SURVIVES all four** — fail-soft breadth is the classic unproved contract |
| M7 | **SURVIVES all four** |
| M8 | **DIES**, in `test_the_self_audit...` only |

Standing prediction for the sweep: **≥1 of the 8 survives all four suites**, i.e. the low-water
result was not special to that module. If every mutation dies somewhere, the LATENT general finding
from `38871422b` is refuted at this subject and I will say so here.

## What would refute the whole framing

If the survivors are all mutations of branches that are genuinely **unreachable** (an equivalence,
not a gap), the finding is "convergence leaves dead code", not "convergence leaves unproved
contracts". Each survivor is therefore checked for reachability by naming the real-world input that
takes the branch, before it is called a gap. A survivor with no reachable input is recorded as an
equivalence and repaired by deletion, not by a test.

## What done means for this turn

The screen's population landed; one subject measured per-caller with predictions graded beside the
result; every survivor classified reachable-gap or equivalence; and the reachable gaps repaired
**on the shared module where the contract lives**, not as a routing test per caller — three of
those would be a control guarding a control.
