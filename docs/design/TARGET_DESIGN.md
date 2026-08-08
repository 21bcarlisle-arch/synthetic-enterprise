# TARGET_DESIGN — the architecture we would build today

**Atom:** `AO7_target_design_doc` (lane `H_harness`, programme `ARCHITECTED_OUT` §2).
**Status:** L2 — mechanically real. The targets below are machine-measured by
`tools/target_design_delta.py`; run it for the live delta.

```
python3 tools/target_design_delta.py            # the delta table
python3 tools/target_design_delta.py --json     # for AO6 / the consolidation rhythm
python3 tools/target_design_delta.py --check    # structural integrity only
```

---

## 0. What this document is, and the failure mode it is designed against

The director's framing: *"drawing the map of A to B is easier once you got there."* This is the
map — the architecture we would build **today**, knowing what we now know, after building the
thing once.

**It is a DIRECTION, NOT A REWRITE MANDATE.** The codebase encodes hundreds of fixed defects,
each protected by a test. A rewrite discards exactly that value; the tests are the accumulated
memory of every way this thing has been wrong. Every KNIFE pass and every RHYTHM pass either moves
the code one step toward a target below, **or amends the target with reasons**. Amending is a
first-class outcome, not a failure — a target that survives contact unchanged for a year is more
likely to be unexamined than right.

**The named failure mode** (the atom's own `origin_note`) is a target document that becomes an
aspirational wish-list nobody measures against. Prose describing an architecture we do not have,
read by nobody, drifting from a tree that moved underneath it. Every architecture-vision document
ever written wants to become this.

So the load-bearing half of this atom is **not the prose below — it is the reported delta**, and
the guard is structural rather than exhortative:

> **No target may exist here without a probe that measures it.**
> `tools/target_design_delta.py --check` returns rc 2 if any target block names a probe that is
> not implemented, or if any implemented probe has no target block. **A wish cannot be written
> into this document.** To state a target, you must first say how it is measured — and if it
> cannot be measured, it belongs in §4 (Not mechanisable), stated as such, not dropped.

**The delta is a DIAGNOSTIC, never a target (R12).** A non-zero delta does **not** fail the check
and must never gate a commit. This is deliberate and it is the whole design: if a large delta
turned the build red, the cheapest fix would be to weaken the target or delete it from this
document, and the map would start optimising itself toward the territory. What *does* fail is a
target that stopped being measured. **We gate on measurability, never on the number.**

**Delta is reported, not hidden.** Where the actual is far from the target, that is the honest
state of the codebase and it is printed in full.

---

## 1. The shape we are aiming at

Four layers, and the direction of knowledge between them is the whole design.

```
   WORLD  (sim/, simulation/)          the ground truth: prices, weather, meters, people
     │                                  it may be as complex as reality allows
     │   drives  ──►  typed, versioned messages
     ▼
   THE WALL  (interface/, company/interfaces/)     the go-live seam
     │                                  swap sim adapters for real endpoints, unchanged above
     ▼
   COMPANY  (company/)                 discovers the world through observables, and is
     │                                  ALLOWED TO BE WRONG about it
     ▼
   SURFACES  (saas/, site/)            what a human reads: bills, reports, the website
```

**The asymmetry is the point, and only one direction is an epistemic law.** The company must not
be able to read simulation internals — that is a WALL, enforced, and it currently holds
(see T3's note). The world driving the company is legitimate and expected; the target there is
*typed adapters* rather than direct imports, which is an architectural preference and a go-live
requirement, **not** an epistemic breach. Conflating the two would manufacture a false alarm, and
this document does not.

**The harness (`background/`, `tools/`, `tests/`) sits outside all four.** It measures and it
schedules; it is never in the business's data path. It is allowed to read everything, because it
is the only thing that legitimately sees both sides of the wall.

---

## 2. The targets

Each block below is parsed by the tool. `direction` is how the actual is compared to `target`;
the delta is `actual - target` for `at_most`, and `target - actual` for `at_least`.

### T1 — No module is a monolith

A module past a few hundred lines has stopped being one capability. The concrete case is the
annual-report builder, named by the July dependency analysis as a KNIFE target: it is the single
largest module in the repository by a wide margin, and it is where reporting, orchestration and
formatting have fused. The target is not a line budget for its own sake — it is that **the reason
a file is long is always that it does more than one thing**, and the split is along those things.

`tools/size_ratchet.py` (SP3) already holds the *monotonic* version of this — "did this commit
make it worse?" — and the ratchet is the mechanism that keeps the number falling. This target is
the *destination* that ratchet is walking toward, measured with SP3's own census so the two can
never disagree about what a line is.

```target
id: T1_no_module_is_a_monolith
probe: modules_over_line_cap
direction: at_most
target: 0
unit: modules over 2000 lines
```

### T2 — No import cycles

A cycle means two modules are one module wearing two names, and it is the reliable structural
signature of a seam that was never drawn. It also makes the KNIFE dangerous: you cannot move
either half independently. The named instance is the reporting module's mutual import with the
main run.

```target
id: T2_no_import_cycles
probe: import_cycles
direction: at_most
target: 0
unit: cycles (strongly-connected components > 1)
```

### T3 — The world reaches the company through the wall

Today the world imports company modules directly, in both senses that matter: it binds the world
to the company's internal module layout, and it means the go-live swap (sim adapters out, real
endpoints in) has more than one place to happen. The target is that every world→company crossing
is a typed, versioned message through the seam, per the standing typed-flow seam preference.

**Stated precisely, because the reverse claim would be an alarm and would be wrong:** this is the
*drive* direction, not the epistemic one. The company→world direction is the epistemic wall and it
is measured separately by T3b. A world module importing a company module is architectural debt.
A company module importing a world internal would be a law broken.

```target
id: T3_world_reaches_company_through_the_wall
probe: world_files_importing_company_directly
direction: at_most
target: 0
unit: files under sim/ or simulation/ importing company.* directly
```

### T3b — The company cannot see inside the world

The epistemic law itself, measured rather than asserted. This one is a WALL: its target is zero
and, unlike every other line in this document, a regression here is not debt to be scheduled — it
is a defect to be fixed on sight. It is listed here so that the day it stops being zero, the delta
table says so.

```target
id: T3b_company_cannot_see_world_internals
probe: company_files_importing_world_internals
direction: at_most
target: 0
unit: files under company/ importing sim/simulation internals outside the seam
```

### T4 — Every capability is reachable

A module nothing imports and no command runs is either an unfinished thought or a capability the
next builder will write again — the write-time blindness this whole programme exists to end.
Measured by AO1's index, whose `orphan` status is derived from real import edges.

The target is zero, and **the resolution is "wired or retired", where retired means archived,
never deleted** (director, standing). An orphan that is deliberately dormant is not an exception
to be waved through here: it is either wired to something, or moved out of the production tree.

```target
id: T4_every_capability_is_reachable
probe: orphan_capabilities
direction: at_most
target: 0
unit: orphan modules
```

### T5 — Money state has exactly one source

State that exists twice drifts, and drift in the billing ledger is drift in the money. The shape
we want is one source with derived copies **regenerated, never edited** — so a derived copy does
not belong in version control beside its source, where nothing distinguishes it from a fork.

The 2026-08-04 structural audit reported these copies as byte-identical and asked "which copy is
the truth?". Measured on 2026-08-08, they are **not** identical: the two `billing_ledger.json`
copies differ in their `meta.source_json` stamp — they are snapshots of two different runs, ~5
minutes apart — while the `customers` payload matched exactly. So the honest reading is
**publish-lag, not a fork of the money**, today. What makes it a target anyway is that nothing
enforces the distinction: the same lag with an edit in it would look identical.

```target
id: T5_money_state_has_one_source
probe: duplicated_state_files
direction: at_most
target: 0
unit: state files tracked at more than one path
```

### T6 — Every company module is exercised by a test

The 2026-08-04 audit's cleanest finding: the machinery that runs the company is better covered
than the company. That is where attention went, and it is backwards — the harness failing is a
bad day, the billing engine failing silently is the business.

**The target is named for exactly what the probe measures, and no more:** a module that no test
file imports *at all* is not merely under-tested, it is unexecuted outside production. That is a
floor, not a coverage claim.

**Measured 2026-08-08, and it corrects the audit's FINDING 4 rather than restating it** (the
advisor invited refutation with evidence). Of 444 production modules under `company/`: **3 are
imported by no test whatsoever**, and **59 have no dedicated `test_<name>.py` file**. The audit's
"226 of 874 non-test files have no matching test" is the second kind of measure, taken repo-wide.
Both numbers are real and they answer different questions; neither is the depth question, which
§4 records as not mechanisable here. The finding's *direction* stands — depth in `company/` is
thinner than in the harness — but "226 untested files" overstates it, because filename matching
is not a coverage measure and this repo has been bitten before by treating a per-file test mapping
as a blast radius.

```target
id: T6_company_modules_are_exercised
probe: company_modules_without_tests
direction: at_most
target: 0
unit: company modules no test imports
```

---

## 3. What this document deliberately does NOT target

Stated so their absence reads as a decision rather than an oversight.

- **A line-count budget for the repository.** Size is a tripwire, never a score (SP3's own
  anti-Goodhart rule, binding). There is no lower bound and there should not be one.
- **A uniform refactor.** KNIFE is "never uniform" by the programme's own wording: named
  hotspots, one per pass, behaviour-preserving.
- **Test count.** Explicitly not a value answer anywhere in this project.
- **Deleting anything.** Archive-never-delete is standing. T4's "retire" means archive.

## 4. Not mechanisable (stated, not dropped)

Targets that belong to the architecture but that no probe here can honestly measure. Listing them
is the alternative to quietly pretending the measured set is the whole set.

- **"Simple to describe, demo and test."** The programme's actual goal. Legibility is judged by
  the Expert Hour / cold-eyes walk, not by a probe — a metric for it would be gamed within a week.
- **Forced-reuse damage.** The mirror error of duplication: two purposes coupled into one
  mechanism because the index said something similar existed. Cheap to cause while chasing T4,
  and there is no counter for it. It is what the AO2 gate's "know, then choose" wording is for.
- **Whether a seam is drawn in the right place.** T2 finds cycles; nothing finds a seam that is
  acyclic and simply wrong.
- **Test DEPTH.** T6 measures whether a module is exercised at all, which is a floor. Whether the
  tests that touch it assert anything worth asserting is the R15 question, and R15 answers it per
  control by mutation, not by a repo-wide number. A coverage percentage here would be the most
  gameable line in the document — the one target where hitting the number and doing the work come
  apart most cheaply.

---

## 5. Amendment log

Every KNIFE and RHYTHM pass moves the code toward a target or amends a target with reasons.
Amendments are recorded here, newest first.

| Date | Target | Change | Reason |
|---|---|---|---|
| 2026-08-08 | — | Document created at L2 with six measured targets. | `AO7`, programme §2. Actuals at creation are in the commit message; the live delta is the tool's, not this table's — a hand-copied number here would be the drift this document is designed against. |
