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

### Pass 2 — `KNIFE2_customer_straddle` (size L)
**Cut:** the 16 SIM modules reaching directly into `saas/customers.py`. Route through the seam.
**Exit:** those 16 edges gone from `LEGACY_SIM_READS_COMPANY`; class (b) drops to 88 (from 104,
after pass 1 has taken the return edge).
**Watch:** `simulation.run_phase2b` owns 35 of the 105 class-(b) edges overall — the single densest
source in the codebase. Pass 2 touches only its customer edges. Its remaining edges belong to
pass 3, and pass 2 must not opportunistically take them.

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
**Exit:** stated when the pass is drawn, against the count that survives passes 1 and 2 — not
against today's 107, which will be stale by then.

### Pass 4 — `KNIFE4_orphan_disposition` (size L, position free)
**Cut:** dispose of the 258 company-side orphans — wire or retire, **archive, never delete**.
**Method, forced by §1's finding:** every one has a test, so the orphan list is a list of
*questions*, not a list of corpses. Each module gets a positive disposition with a reason: wired
(a caller exists and was missing), retired-to-archive (the capability was superseded — name the
superseder), or kept-and-explained (it is a library/entry point the index cannot see, which is a
defect in the index's caller detection and gets logged as one).
**Exit:** every orphan carries a disposition; the count falls; nothing is deleted.

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
overlaps: customer_straddle=1, wall_crossings=3, company_orphans=0
KNIFE-HOTSPOT -->

<!-- KNIFE-HOTSPOT
hotspot: customer_straddle
probe: customer_straddle
baseline_files: 17
baseline_edges: 16
baseline_lines: 496
overlaps: reporting_monolith=1, wall_crossings=16, company_orphans=0
KNIFE-HOTSPOT -->

<!-- KNIFE-HOTSPOT
hotspot: wall_crossings
probe: wall_crossings
baseline_files: 33
baseline_edges: 107
overlaps: reporting_monolith=3, customer_straddle=16, company_orphans=0
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
