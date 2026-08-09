# KNIFE — the four hotspot passes

**Atom:** `AO5_hotspot_consolidation` (lane `H_harness`, epoch 3, L0→L2)
**Serves:** `DIRECTOR_PROGRAMME_ARCHITECTED_OUT_2026-08-05.md` §1, step KNIFE
**Ledger:** `tools/knife_hotspot_measure.py` — run it before and after every pass
**Written:** 2026-08-09, from a measured walk of the tree on `main`

---

## 0. What this document is, and what it is not

It is the **sequencing and disjointness plan** for the four named hotspots. Each pass listed here
mints its own atom with its own real `file_scope` and is its own sized draw. This document is
never the place a cut happens.

It is **not** a re-derivation of the targets. The director ruled the four already-named and
explicitly not to be re-derived; §1 of the programme names them and the atom repeats them. What
*is* derived here is their **current size** and their **mutual overlap**, because those are facts
about today's tree that July's analysis could not know — and, as it turns out, three of the four
figures it carried are now wrong. That matters for sizing, not for scope.

The four walls the director pre-ruled are restated once so no pass has to go looking:

1. **Sequence position** — nothing cuts before NET. `AO3_join_test_tier` and
   `AO4_scale_constraints_executable` are both L2, so this condition is met, and it is carried by
   `depends_on` in the map rather than by anyone remembering it.
2. **One hotspot per pass.** Never two.
3. **Behaviour-preserving moves only.**
4. **Byte-identical output checks where they exist.**

And the fifth, from this atom's own `origin_note`: a shared `file_scope` across four high-risk
refactors is the concurrency hazard the three-lanes rule exists to prevent. Section 3 is that
hazard, measured.

---

## 1. The tree as it actually is (2026-08-09)

| # | Hotspot | July's figure | Measured today | The gap matters because |
|---|---|---|---|---|
| 1 | Reporting module | ~9k lines, mutual-import cycle with the main run | **10 files, 11,094 lines**; `saas/reporting/annual_report.py` alone is **9,378**. The cycle is real and mutual: **3 edges** | July's "~9k module" is one FILE, not the package. The package has grown ~23% since. A pass scoped to "the module" would be sized for the wrong thing — and would miss the far end of its own cycle. |
| 2 | Customer module straddling the wall | named, unsized | `saas/customers.py` (496 lines) reached directly by **16 SIM modules** | The straddle is the 16 reachers, not the file. The file is small; the pass is not. |
| 3 | SIM↔company crossings bypassing the seam | "100+ … bypassing the empty seam" | **107 live edges** across **33 files** (2 company→SIM, 105 SIM→company) | The count holds. **"Empty seam" does not** — `company/interfaces/sim_interface.py` is 399 lines with 8 company-side consumers. The seam exists; the crossings route around it. |
| 4 | Zero-import company modules | ~320, candidates for wiring or retirement | **258** company-side orphans (`company/` 258 of them; `market` 59, `crm` 52, `regulatory` 42, `billing` 33) | **All 258 carry test evidence.** Not one is untested dead code. |

**The finding that changes how pass 4 must be run:** every single orphan has a test. "Nothing
imports it" and "nobody wanted it" are different facts, and this repo has already paid for
confusing them — the no-caller class census (2026-08-09) found 13 instances in 13 days, 8 of them
discovered by accident. So retirement may **never** be inferred from orphan status alone; pass 4
needs a positive reason per module, and `ARCHIVE, NEVER DELETE` (director, standing) governs the
disposition either way.

Freshness of these numbers is not a matter of trust: `python3 tools/knife_hotspot_measure.py`
recomputes all of them from the tree in one command, and the ledger fails rather than reports if
any probe cannot measure.

---

## 2. What "behaviour-preserving" means here, concretely

Wall 3 is the one most easily satisfied in words and missed in fact. For these passes it means all
four of:

- **The full suite is green before and after**, run once per integration, never fanned out.
- **`tests/architecture/test_epistemic_wall_ratchet.py` is the arbiter for passes 1–3.** Its frozen
  edge lists may only SHRINK. A pass that removes a crossing deletes its tuple; a pass that adds
  one is not behaviour-preserving by definition. Crucially: **the pass must not edit the walker.**
  A refactor that changes the instrument and the measured thing in the same commit has measured
  nothing.
- **Byte-identical outputs where they exist** (wall 4). For pass 1 the artefact is the annual
  report: regenerate before and after, `diff` must be empty. Where no byte-comparable artefact
  exists, the pass says so in its own atom rather than substituting a weaker check silently.
- **`tools/knife_hotspot_measure.py` run before and after**, with the delta quoted in the pass's
  close. A pass whose hotspot did not move did not happen.

---

## 3. Disjointness — the measured overlap, and the order it forces

File-set overlaps between the four hotspots, measured (not assumed):

|              | reporting | customer | crossings | orphans |
|--------------|-----------|----------|-----------|---------|
| **reporting**  | —       | **1**    | **3**     | 0       |
| **customer**   | 1       | —        | **16**    | 0       |
| **crossings**  | 3       | 16       | —         | 0       |
| **orphans**    | 0       | 0        | 0         | —       |

> **This table was corrected by its own ledger, on the ledger's first real run.** The hand analysis
> that drafted this document had reporting↔customer at 0 and reporting↔crossings at 2, because it
> counted only the edges *leaving* `saas.reporting`. The probe counts both directions — a cycle is
> not owned by one side of it — and found the third edge,
> `simulation.run_phase4c_on_phase2b → saas.reporting.annual_report`, whose source file is *also*
> one of the customer straddle's 16 reachers. That single file is the whole difference between
> conclusion (a) as drafted and conclusion (a) as it stands. It is recorded here rather than
> quietly fixed because a plan that claims two high-risk refactors are disjoint when they are not
> is precisely the failure this atom exists to prevent, and the guard catching its own author is
> the strongest evidence available that it can fail.

Three conclusions follow, and none of them were visible from the prose:

**(a) No two of hotspots 1, 2 and 3 are disjoint.** Passes 1 and 2 share
`simulation/run_phase4c_on_phase2b.py` — the reporting cycle's far end is one of the customer
module's reachers. **All three wall passes are therefore strictly serial**, and no future widening
of the three-lanes width may run any pair of them concurrently.

**(b) Hotspot 3 CONTAINS 1 and 2.** Its 33 files include all three of hotspot 1's cycle files and
all 16 of hotspot 2's reachers. So pass 3 cannot run before or beside passes 1 and 2 — it would
re-cut the same edges, and two passes cutting one seam is exactly the hazard the `origin_note`
names. **Pass 3 goes last among the wall passes.** This is not a preference; it is what the
overlap table permits.

**(c) Hotspot 4 is disjoint from all three.** Zero shared files with any of them — and note *why*
that is a real finding rather than a definitional one: an orphan could in principle also sit on a
crossing edge (nothing stops a module with no company-side caller being imported from `simulation/`),
and the measurement says none does. Pass 4 is therefore free to run at any position, including
alongside a wall pass, if width is ever available.

The ledger re-checks this table on every run and **fails if a declared overlap is not the real
one** — in either direction. An overlap declared that isn't there is a plan describing a tangle it
invented; a real overlap left undeclared is the concurrency hazard itself, silently.

### 3a. Amendment after pass 1 (2026-08-09) — conclusions (a) and (b) no longer hold

Pass 1 landed, and the ledger immediately failed on this document: it had declared
reporting↔customer=1 and reporting↔crossings=3, and the tree now has **0 and 0**. That is the
guard working, not a defect — but it means the sequencing conclusions above are stale, and a later
pass reading them would be reading a map of a tangle that no longer exists.

Measured overlap after pass 1:

|              | reporting | customer | crossings | orphans |
|--------------|-----------|----------|-----------|---------|
| **reporting**  | —       | 0        | 0         | 0       |
| **customer**   | 0       | —        | **16**    | 0       |
| **crossings**  | 0       | 16       | —         | 0       |
| **orphans**    | 0       | 0        | 0         | —       |

**(a) is now false, and it was pass 1 that falsified it.** The three shared files were
`annual_report.py`, `segment_report.py` and `run_phase4c_on_phase2b.py`; the first two no longer
carry any crossing and the third no longer participates in a `saas.reporting` edge, so hotspot 1
fell out of both other hotspots' file sets by being *fixed*. Hotspot 1 is now disjoint from
everything. The serial constraint it imposed is discharged.

**(b) shrinks: hotspot 3 now contains only hotspot 2**, not 1 and 2. Pass 3 still goes after
pass 2 — the 16 customer edges are still inside the 104 crossings, and that is the whole of the
remaining containment.

**What does NOT change:** passes 2 and 3 remain strictly serial with each other (16 shared files),
and pass 4 remains free. The rule that produced these numbers is unchanged — re-run
`python3 tools/knife_hotspot_measure.py` before drawing any later pass rather than trusting this
table, which is now on its second correction in one day.

**Baselines are deliberately NOT re-frozen.** They are the 2026-08-09 pre-KNIFE figures, and the
delta against them (`-1 file` on reporting, `-2 files / 107→104 edges` on crossings) is the
evidence a pass happened. Re-freezing after each pass would erase exactly the thing §2 requires
be quoted at close.

### 3b. Amendment after pass 2 (2026-08-09) — the overlap table is now empty, and so is (b)

Pass 2 landed and the ledger failed on this document a second time, in the same way and for the
same good reason: it declared customer↔crossings=16 and the tree now has **0**.

|              | reporting | customer | crossings | orphans |
|--------------|-----------|----------|-----------|---------|
| **reporting**  | —       | 0        | 0         | 0       |
| **customer**   | 0       | —        | 0         | 0       |
| **crossings**  | 0       | 0        | —         | 0       |
| **orphans**    | 0       | 0        | 0         | —       |

**(b) is now discharged as well.** Hotspot 3 contained hotspot 2 through exactly the sixteen
reachers; those are gone, so it contains nothing. The `customer_straddle` population has collapsed
to the single file `saas/customers.py` with no reachers, which is the goal state for that hotspot,
not a measurement failure — the probe still measures it, and a new SIM reacher would re-inflate it
immediately.

**Every hotspot is now disjoint from every other.** The serial constraint that governed passes 1–3
is fully discharged. Pass 3 no longer *has* to run last; it runs next because it is the only wall
work left, and its coordination wall with the Epoch-3 adapter programme (§4) is unchanged and
still binding. **Do not read a table of zeros as "no constraints exist"** — re-run
`python3 tools/knife_hotspot_measure.py` before drawing pass 3 rather than trusting this table,
which is now on its third correction in one day. The correction rate is the point: three
sequencing plans, three falsifications, all by the same probe.

---

## 4. The passes

Each is its own atom, its own `file_scope`, its own sized draw. Sizes are forecasts and are
diagnostics, never targets (LAW A): if a size and an exit test disagree, the size is wrong.

### Pass 1 — `KNIFE1_reporting_cycle` (size M)
**Cut:** break the mutual import between `saas/reporting/` and the main run. Three edges:
`saas.reporting.annual_report → simulation.run_phase4c_on_phase2b` and
`saas.reporting.segment_report → simulation.run_segments` (class (a) — company-side code reading
SIM internals, the strictly forbidden direction and the ratchet's own named highest-priority
shrink target), plus the return edge
`simulation.run_phase4c_on_phase2b → saas.reporting.annual_report` (class (b)) that closes the
cycle. Cutting either direction alone leaves an import, not a cycle — and the return edge is the
file pass 2 also touches, which is why these two passes are serial.
**Exit:** both class-(a) tuples deleted from `LEGACY_COMPANY_READS_SIM`, so class (a) reaches
**zero**; the return tuple deleted from `LEGACY_SIM_READS_COMPANY` (105 → 104); annual report
byte-identical.
**Explicitly NOT in this pass:** splitting the 9,378-line `annual_report.py`. That is a size
problem, this is a cycle problem, and one hotspot per pass forbids doing both. The split is owed
to the RHYTHM duty (`AO6`) or its own later atom, and is named here so it is deferred rather than
forgotten.

**LANDED 2026-08-09.** Ledger delta: `reporting_monolith` 3 edges → **0**; `wall_crossings`
107 → **104** edges, 33 → 31 files. `LEGACY_COMPANY_READS_SIM` is now **empty** — class (a) is at
zero. Full ratchet suite (12 tests) green, including both mutation proofs.

*How it was cut, because the shape is the reusable part:* the coupling was never a reporting need
— it was a COMPOSITION ("run the world, then describe it"), and a composition root belongs above
both layers. It moved to `tools/run_annual_report.py`, `tools/run_segment_report.py` and
`tools/run_phase4c_pipeline.py` (`tools/` is outside `WALL_DIRS`, and `tools/run_frozen_baseline.py`
already imported the run entry point directly). Both reporting modules are now render-only CLIs
and name `simulation` nowhere; `run_phase4c_on_phase2b.py` is a pure library naming no company-side
package. **The cut is not a lazy import or an indirection.** The walker sees function-local imports
exactly as it sees module-level ones — that is why `segment_report`'s lazy import was on the
allowlist in the first place — and routing the same dependency through a package the walker does
not walk would have moved the measurement rather than the dependency.

*Two honest caveats, recorded rather than smoothed:*
1. **"Byte-identical" needed one qualification.** Rendered from the same `run_output_latest.json`
   before and after, the 377,008-character report differs on **exactly one line**: `Generated:`,
   its own UTC clock stamp. Identity holds over every other line. Later passes asserting wall 4 on
   this artefact should diff modulo that line rather than claim raw byte-equality and be surprised.
2. **An empty class-(a) allowlist makes its stale-entry test vacuous.** It has nothing left to find
   stale. The live class-(a) controls are `test_no_new_company_reads_sim`, its mutation proof, and
   the on-disk walker mutation — all still firing, and now with no grandfathering left to hide
   behind. Noted in the allowlist itself.

*Behaviour change worth knowing:* `python3 -m saas.reporting.annual_report` with no cached data
used to silently start a multi-hour simulation. It now exits with a message naming
`python3 -m tools.run_annual_report`. The `--from-json` path — the one `process_run_complete.py`
uses — is untouched.

### Pass 2 — `KNIFE2_customer_straddle` (size L)
**Cut:** the 16 SIM modules reaching directly into `saas/customers.py`. Route through the seam.
**Exit:** those 16 edges gone from `LEGACY_SIM_READS_COMPANY`; class (b) drops to 88 (from 104,
after pass 1 has taken the return edge).
**Watch:** `simulation.run_phase2b` owns 35 of the 105 class-(b) edges overall — the single densest
source in the codebase. Pass 2 touches only its customer edges. Its remaining edges belong to
pass 3, and pass 2 must not opportunistically take them.

**LANDED 2026-08-09.** Ledger delta: `customer_straddle` 17 files / 16 edges → **1 file / 0 edges**;
`wall_crossings` 104 → **88** edges, 31 → 23 files. All sixteen tuples deleted from
`LEGACY_SIM_READS_COMPANY`. Full ratchet suite (12 tests) green, both mutation proofs included.
The watch held: `run_phase2b`'s non-customer edges were left alone — it is still in the class-(b)
allowlist with the rest of its edges, and the 88 that survive are pass 3's.

*How it was cut.* The seam is `company/interfaces/supply_book.py` — **the supply book**: which
meter points this supplier has registered. That framing is the whole of the design, and it is not
a euphemism for a re-export. In GB a supplier registers against an MPAN in the central systems and
the industry *learns* the point is on its book; the world knowing the registered population is
real, and the sixteen `from saas.customers import CUSTOMERS` statements were the world reaching
into the CRM to find out instead. Six names crossed (`CUSTOMERS`, `SUCCESSOR_CUSTOMERS`,
`ACQUIRED_CUSTOMERS`, `get_customer`, `customer_to_settlement_input`, `make_acquired_customer`);
they are now `registered_supply_points()`, `successor_supply_points()`, `acquired_supply_points()`,
`registered_point()`, `settlement_input()`, `register_acquired_point()`.

*Why routing through `company.interfaces` is not pass 1's refused move.* Pass 1 declined to route a
dependency through `tools/`, because `tools/` is outside `WALL_DIRS` — the walker never looks
there, so the edge would have vanished from the measurement rather than from the code. The
opposite is true here: `company/interfaces/**` **is** walked, byte for byte as before, and its
exemption is a published rule at the top of the ratchet (`SEAM_PACKAGE`) whose own doctrine string
names this exact remedy — *"if this crossing is intentional and unavoidable, route it through the
seam"*. The test of the difference is falsifiability, and it survives it: put
`from saas.customers import CUSTOMERS` back into any SIM module today and
`test_no_new_sim_reads_company` reds instantly, with no grandfathered tuple left for it to hide
behind. That was not true yesterday.

*Three honest caveats, recorded rather than smoothed:*
1. **This routes the crossing; it does not remove the dependency.** The same records cross, at one
   reviewable chokepoint instead of sixteen unreviewable ones. Anyone reading "16 → 0" as
   decoupling is reading it wrong, which is why the seam's own docstring says so first.
2. **The seam does not yet narrow the record to what industry can see.** A real registration
   publishes identity, supply start, address, profile class, metering and EAC — not
   `contract_type`, not the supplier's internal `segment` label. Narrowing is a behaviour change
   and wall 3 forbids it in this pass; it is owed to pass 3 / the Epoch-3 adapter programme.
3. **The dwelling truth is still filed on the wrong side.** `home_type`, `bedrooms` and
   `epc_rating` are facts about a physical property living in company-side code. The clean fix —
   move `saas/customers.py` to the SIM side — would re-open class (a), which pass 1 drove to zero,
   so it is strictly worse and was rejected rather than overlooked.

*Behaviour preservation, and the one place it was nearly lost.* The three rosters are **mutable
module-level lists**: `run_phase2b` appends a registration to `ACQUIRED_CUSTOMERS` as each
acquisition lands, and `_clear_acquired_customers()` clears it in place in test teardown. A seam
returning a defensive copy would have severed both silently — green suite, wrong world. The
accessors therefore return the live objects, callers bind once at import exactly as
`from ... import` did, and the property is asserted directly (`is`-identity for all three rosters
across all importable modules, plus an append and an in-place clear observed through
`run_phase2b`) rather than inferred from the tests passing.

*Wall 4 (byte-identical output): no comparable artefact, stated rather than substituted.* Pass 1
had the annual report. This pass changes no rendering path, and the run that would produce a
comparable artefact is the ~100-minute Phase 2b simulation. The evidence offered instead is the
identity assertion above, which is the *stronger* check for this particular change — a copy is the
only way this refactor could alter behaviour, and identity refutes it directly.

*A third definition of "the seam" now has teeth, which strengthens pass 3's first step.* Pass 1
queued a finding that `tools/epistemic_verifier.py`'s `APPROVED_ORCHESTRATION` still exempts the two
edges it had just deleted. This pass makes the divergence structural rather than merely redundant:
the verifier's `APPROVED_SEAM` is a **single file** (`company/interfaces/sim_interface`) while the
ratchet's `SEAM_PACKAGE` is the **package** (`company.interfaces`). `supply_book.py` is the first
seam module the two definitions disagree about. Nothing is broken today — the verifier passes,
because `company/interfaces/` is separately in its `EXEMPT_PATHS`, so the file is exempt by a
different clause than the one named "the approved seam". That is a control passing for a reason
other than the one it states, and it is exactly what pass 3's shared-definition extraction is for.
Recorded here so the extraction has a second concrete referent, not just the stale orchestration
list.

*Two pre-existing defects surfaced, QUEUED not fixed (SELF_INTERRUPT_DISCIPLINE):*
`simulation/run_phase2a.py` and `simulation/run_phase2a_repriced.py` **do not import** — module
scope does `sum(c["eac_kwh"] for c in CUSTOMERS)` and 12 of the 18 roster entries carry
`eac_kwh: None`. Confirmed pre-existing by evaluating the same expression over the same object
(the roster is one shared list, so HEAD's binding fails identically), and nothing in the tree
imports either module. Filed as `WORKER_FINDING_TWO_UNIMPORTABLE_PHASE2A_MODULES_2026-08-09.md`.

### Pass 3 — `KNIFE3_wall_crossing_paydown` (size XL, must run last of the three)
**Cut:** the remaining crossings, after 1 and 2 have taken theirs.
**First step, before any cut:** lift `build_edges` / `company_reads_sim` / `sim_reads_company` out
of `tests/architecture/test_epistemic_wall_ratchet.py` into a shared module, so the ratchet, the
KNIFE ledger, and this pass all read one definition of "a crossing". This extraction is deliberately
deferred to here rather than done while planning: moving the net while planning the cuts is the
error the MAP→NET→KNIFE sequence exists to prevent.
**Coordination wall:** the Epoch-3 adapter programme is the BOUNDARY half of this knife and is not
duplicated here. **Check it before starting pass 3** — two lanes cutting one seam is the failure
this whole section is about.

#### Drawn 2026-08-09. Coordination wall checked, first step LANDED, EXIT stated.

**Coordination wall: clear.** All eight Epoch-3 adapter atoms (`EP7`–`EP14`) are `level_current: 0`,
`loop_stage: idle`, `file_scope: []`. No lane is cutting this seam. Checked before the first edit,
which is the order the wall specifies.

**The count this pass is measured against: 88 edges across 23 files** (`python3
tools/knife_hotspot_measure.py`, 2026-08-09 — class (a) is at zero and stays there). Not 107.

##### First step — LANDED: one definition of "a crossing"

`build_edges` / `company_reads_sim` / `sim_reads_company`, the perimeter and the seam now live in
**`tools/epistemic_wall.py`**. Three consumers import it and keep only their own job: the ratchet
GATES, the KNIFE ledger REPORTS, `tools/epistemic_verifier.py` SCANS at phase close over a wider
(dynamic-import) reach. The dated allowlists stay in the ratchet — the definition is shared, the
POLICY baseline is not, which is what lets a pass say "the walker was not edited" and mean it.
Control: `tests/architecture/test_epistemic_wall_single_source.py` (15 tests), which asserts
**object identity** rather than equal answers, because two identical copies of the walker compare
equal on today's tree and are precisely the defect.

Four things it turned up, none of which were visible from the prose:

1. **The control failed on its first run and named its own author.** `tools/epistemic_wall.py`
   ALREADY EXISTED — untracked, in no commit, imported by nothing: an earlier attempt at this same
   extraction that died before it was wired up. The pass had written its own replacement.
   Disposition per the standing rule for work a guard flags as unmerged: **adopt, do not rebuild**
   — the found file is the survivor, the pass's copy was deleted, and the pass's additions (the
   two shared predicates, the wiring, the control) went on top. The provenance is recorded in the
   module's own docstring, because "a landed pass had half its code uncommitted" is a repeat class
   here and the record is the only place the next reader sees the duplicate was resolved on purpose.
2. **The stale orchestration carve-out is deleted** (`WORKER_FINDING_STALE_ORCHESTRATION_CARVE_OUT`,
   queued by pass 1). `APPROVED_ORCHESTRATION` exempted exactly the two class-(a) edges pass 1 had
   cut. A dead exemption is a **pre-authorised re-entry**; both imports now fire. And it was
   PINNED GREEN — two assertions in `tests/controls/test_control_mutation.py` asserted the
   exemption held, so the test suite was defending it. Those assertions are inverted, with the
   reason in place.
3. **A second, undocumented escape hatch went with it.** `APPROVED_SEAM` was consulted as a
   SUBSTRING of the offending import LINE in the regex fallback — so `from simulation.household
   import Household  # company/interfaces/sim_interface` cleared a real crossing by comment. Not a
   seam exemption; a comment-shaped bypass. Deleted; the genuine source-side exemption is
   `EXEMPT_PATHS`, now DERIVED from the shared `SEAM_PACKAGE` so it cannot drift from it again —
   which was this extraction's second declared referent (§ pass 2, "a third definition of the seam
   now has teeth").
4. **Two of the ledger's own mutation proofs were RED at HEAD, and pass 2 is why.** They pinned
   whichever real overlap the tree happened to carry; pass 2 cut the last sixteen, the overlap
   table went to all zeros, and the guards died with "mutation source line is no longer in the live
   plan". That is the anti-vacuity assert working *and* a design defect it exposed: **a control
   whose fixture needs a LIVE instance of the defect dies exactly when the codebase reaches its
   goal state** — and total disjointness IS the goal state here. Repaired at the statistic, not the
   fixture: the overlap is now manufactured on the MEASURED side, so both guards keep proving the
   same thing on a tree with no tangle left, plus a vacuity twin showing they are silent without
   the injected defect.

##### EXIT — stated now, as conditions, not as a number

Pass 4 withdrew "the count falls" as an exit clause when its own measurement contradicted it. The
same discipline applies here from the start (R12: the count is a diagnostic; LAW A: when a
criterion and the evidence disagree, the criterion is wrong):

- **Every one of the 88 surviving crossings carries a disposition.** Cut (the edge is gone, and its
  tuple deleted from `LEGACY_SIM_READS_COMPANY`), or explicitly grandfathered with a named reason.
  No edge survives *unexamined*. That is the clause that cannot be satisfied by moving a
  measurement.
- **Nothing is routed through a package the walker does not walk.** Pass 1's refused move stands.
- **The walker is not edited in a cutting commit** — instrument and measured thing never move
  together. The extraction above is deliberately its own commit, before any cut, with the ratchet's
  frozen allowlists byte-unchanged, so the baseline is provably unmoved across it.
- **Wall 4:** no byte-comparable artefact exists for the crossings (the comparable run is the
  ~100-minute Phase 2b). Stated, not substituted with a weaker check — as pass 2 did.

##### The decomposition the measurement forces — and it is NOT one shape

The 88 survivors are two different problems wearing one name, and the split is the finding:

| Shape | Edges | Files | What it actually is | The cut, by precedent |
|---|---|---|---|---|
| **A — composition roots inside `simulation/`** | **67** | 10 (`simulation/run_phase*.py`) | Not the simulated world. Scenario harnesses that compose a world AND a company and run them together. `run_phase2b.py` alone is 2,954 lines and 34 edges — the densest source in the codebase. | **Pass 1's cut.** A composition root belongs ABOVE both layers. This is the same "the coupling was never a reporting need, it was a composition" finding at ten times the scale. |
| **B — world physics reading the company's brain** | **21** | 13 (`arrears_engine`, `churn_journey`, `customer_events`, `dd_*_book`, `hedged_settlement`, `feedback_survey`, …) | Genuine wall violations: the world reaching into company policy, the company's churn ceiling, its price-cap reading, its CPA. | **Pass 2's cut.** A designed seam per population, in the direction the world legitimately learns things. |

Shape B is the smaller count and the harder work: each of the 21 is a wall-DESIGN question ("may
the world know the supplier's cap reading?"), not a mechanical move, and cutting one badly is worse
than leaving it measured. Shape A is bulk but has a proven template.

##### Second step — LANDED: every one of the 88 carries a disposition

The first EXIT clause is now a mechanism rather than a promise:
`docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md` rules on all 88 edges, and
`python3 tools/wall_crossing_dispositions.py` exits 2 if any live crossing has no ruling — or if a
ruling names an edge the tree no longer has. R15 proof:
`tests/tools/test_wall_crossing_dispositions.py` (46 tests), every guard mutated against a
SYNTHETIC register rather than the live tree, for the reason finding (4) above had to repair in the
ledger's own proofs — the goal state of this register (everything cut, nothing owed) is exactly the
state a live-fixture proof would go vacuous in.

Three things the examination turned up, and one it refused:

1. **The A/B split in the table above is 65/23, not 67/21.** Two `run_phase2b` edges
   (`→ company.core.reputation_index`, `→ company.core.resentment_ledger`) sit in a shape-A file but
   are killed by a shape-B cut. Ruling per EDGE rather than per FILE is the only assignment that
   keeps a named cut design meaningful. **Fourth time in this programme that measuring something has
   corrected the document that scheduled it.**
2. **Three `company/core/` modules are world physics, and the objection that blocked the analogous
   move in pass 2 is measurably absent here.** `reputation_index`, `resentment_ledger` and
   `activation_energy` call themselves "behavioral physics" in their own docstrings and have **zero
   company-side importers** — every importer is SIM-side. Pass 2 rejected moving `saas/customers.py`
   to the SIM side because it would re-open class (a); with no company-side importer, moving these
   three creates no class-(a) edge at all. Six edges, one cut, blocking objection refuted by
   measurement rather than argued away.
3. **The most serious inversion is not in shape A.** `simulation.customer_events` imports the
   company's churn model *to decide who actually churns*. The company's belief is therefore
   self-fulfilling, which destroys the exact quantity the COUPLED TRIAD exists to score and
   silently flatters every churn-accuracy figure downstream of it.

**And the refusal, recorded before anyone tries it:** the tempting shape-A cut is to move all ten
`run_phase*` harnesses to `tools/` and watch 65 edges vanish. That is laundering. Pass 1's move was
legitimate because it extracted a *thin* composition and left the substantive modules in place,
walked and clean; here the composition IS the substance (`run_phase2b.py` is 2,954 lines of which
`main()` is ~2,100). Relocating it changes no code, removes no dependency, and moves only the
walker's reach — failing this pass's own second exit clause. The register says so in writing so the
next draw inherits the ruling instead of rediscovering the temptation.

**Status: first and second steps landed; the cut has not started.** Recorded loudly rather than left
implicit, because the orphaned duplicate found in finding (1) is what a silent partial pass looks
like from the next draw. The remaining work is the eight named designs in the register, and B8
(one edge, relocate a publication surface under the seam) is the cheapest genuine cut available.

### Pass 4 — `KNIFE4_orphan_disposition` (size L, position free)
**Cut:** dispose of the 258 company-side orphans — wire or retire, **archive, never delete**.
**Method, forced by §1's finding:** every one has a test, so the orphan list is a list of
*questions*, not a list of corpses. Each module gets a positive disposition with a reason: wired
(a caller exists and was missing), retired-to-archive (the capability was superseded — name the
superseder), or kept-and-explained (it is a library/entry point the index cannot see, which is a
defect in the index's caller detection and gets logged as one).
**Exit:** every orphan carries a disposition; the count falls; nothing is deleted.

**LANDED 2026-08-09 — and it falsified two of its own three premises.** Register:
`docs/design/ORPHAN_DISPOSITION_REGISTER.md`; mechanism: `capability_index.py --dispositions`,
17 mutation proofs in `tests/tools/test_capability_index.py`. Ledger delta: `company_orphans`
258 → **258**.

1. **"The index cannot see its caller" is empty, by measurement.** Four blindness hypotheses were
   tested before any module was ruled on — dotted-name strings in production `.py`, dynamic
   loading (`walk_packages`/`import_module`/`__import__`), references from all 6,226 tracked
   non-`.py` files, and unguarded `main()` entry points. Total real callers found: **zero**. The
   only two hits are a docstring example in `tools/internal_seam_verifier.py` and 258 pure
   *documentation* mentions. `kept-and-explained` is not a bucket here, and there is no index
   defect to log — the accusation was worth measuring before acting on.
2. **`retired-to-archive` is empty too.** A symbol-overlap scan of all 258 against every wired
   module found one pair above 50% (`imbalance_analytics` vs the wired `imbalance_ledger`), and
   the orphan carries bias detection the wired one lacks — a consolidation candidate, not a
   superseded copy. Owed to `AO6`.
3. **The real class is a fourth one: `unhooked`** — tested capability whose consumer was never
   built. 258 of 258. It is made falsifiable per row by requiring a *nominated consumer* derived
   from the package's wired modules, and the check refuses absent, decorative and refuted
   nominations.

**"The count falls" is therefore withdrawn as an exit clause, not deferred.** With no justified
retirement and no missing caller, the only ways to move 258 today are deletion (a director wall),
archiving on orphan status alone (this pass's own method forbids it), or manufacturing an import —
moving the measurement rather than the code, which is exactly what pass 1 refused when it declined
to route a dependency past the walker. R12: the count is a diagnostic, never a target. LAW A: when
a criterion and the evidence disagree, the criterion is wrong. This is the **second** time in one
day that a pass's measurement has corrected the plan that scheduled it (§3a was the first).
The fall is owed to the consumers being built, and the register's referent column is that work
list, sorted by door.

---

## 5. The declared ledger

These blocks are read by `tools/knife_hotspot_measure.py`. They state INTENT; the tool measures
the TREE; a mismatch can only be closed by making the declaration true. Baselines are diagnostics
(R12) — missing one is rc 0 and reported. Overlaps are the gate.

<!-- KNIFE-HOTSPOT
hotspot: reporting_monolith
probe: reporting_monolith
baseline_files: 10
baseline_edges: 3
baseline_lines: 11094
overlaps: customer_straddle=0, wall_crossings=0, company_orphans=0
KNIFE-HOTSPOT -->

<!-- KNIFE-HOTSPOT
hotspot: customer_straddle
probe: customer_straddle
baseline_files: 17
baseline_edges: 16
baseline_lines: 496
overlaps: reporting_monolith=0, wall_crossings=0, company_orphans=0
KNIFE-HOTSPOT -->

<!-- KNIFE-HOTSPOT
hotspot: wall_crossings
probe: wall_crossings
baseline_files: 33
baseline_edges: 107
overlaps: reporting_monolith=0, customer_straddle=0, company_orphans=0
KNIFE-HOTSPOT -->

<!-- KNIFE-HOTSPOT
hotspot: company_orphans
probe: company_orphans
baseline_files: 258
overlaps: reporting_monolith=0, customer_straddle=0, wall_crossings=0
KNIFE-HOTSPOT -->

---

## 6. What this document does not decide

- **Whether `annual_report.py` should be split.** Named in pass 1 as deferred; owed to RHYTHM.
- **The shape of the Epoch-3 adapter programme.** It is the boundary half; it owns its own scope.
- **Any exit criterion for pass 3.** Deliberately left to the draw, because today's number is not
  the number that pass will face.
- **Whether the crossing count *should* be zero.** It is a diagnostic. The ratchet enforces
  monotone shrink; nothing here sets a target, and nothing may be promoted or shortened to hit one.
