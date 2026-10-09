# [ADVISOR] Import-graph census — four observations for the seat's consideration

Date: 2026-10-09. Measured at commit 91a7981 (2026-10-09 04:52 +0100) by an AST
import parse of every non-test Python module (1,275 modules, 2,321 internal
import edges). These are observations with evidence, offered as hypotheses for
the seat to weigh and dispose of — not directives, and no priority over drawn
work is claimed. The seat owns the plan.

**Method and limits.** Static `import`/`from` statements only, resolved against
the repo's own module set. Dynamic dispatch, subprocess calls and data-file
coupling are invisible to this instrument, so "no import edges" never means
dead. Same method as the 2026-07-16 advisor census, so the deltas below are
like-for-like.

## 1. The boundary's door sits inside a mutual-import knot

A 36-module strongly-connected cluster spans both sides of the SIM/company
boundary and runs through the door itself — members include
`company.interfaces.sim_interface`, `company.interfaces.recorded_sim_interface`,
`simulation.payment_seam_adapter`, `simulation.registration_loss_feed`. Every
module in a strongly-connected cluster can reach every other through imports,
so while the door participates, neither side can be built, tested or replaced
without the other. The problem this poses: the ambition of re-running or
swapping the company against a fixed world needs the two sides separable at
exactly this boundary. Whether and when to untangle it is the seat's call.

## 2. The boundary residue is now a small, countable set

On 2026-07-16: 101 sim-side → company-side imports bypassing any interface, 2
direct company → SIM imports, 3 sanctioned seam crossings, and an `interface/`
directory containing only a `.gitkeep`. Today: 49 bypassing imports, 0 direct
company → SIM imports, 9 sanctioned seam crossings, and a real `interface/`
layer (7 modules, 2,285 lines) imported 33 times. The direction of travel is
clearly right, and what remains is an enumerable list of 49 edges rather than a
diffuse property. Offered as a measurement the seat may find worth owning;
offered as a diagnostic, not a target — the number is useful precisely while
nothing is rewarded for moving it.

## 3. Change-risk is concentrating in three files

`background.process_run_complete` is 10,985 lines with 97 imports (was 1,324 /
50 in July); `saas.reporting.annual_report` is 11,130 lines with 49 imports;
`background.supervisor` is 7,223 lines. These are the widest funnels in the
codebase: most work lands through them, so a defect in any one has the largest
possible blast radius, and their growth rate exceeds the codebase's. The
problem is stated, not the remedy.

## 4. The recovery tooling is entangled with itself

A second 24-module mutual-import cluster is the machine's own self-management
stack — `background.tree_lock`, `tools.pre_commit_test_gate`,
`tools.surgical_land`, `background.fork_salvage` among its members. This is the
machinery currently handling the live holder fork (origin 74 commits ahead,
landings blocked). The problem it poses: tooling whose job is recovering from
entanglement cannot easily be exercised, tested or trusted in isolation while
it is itself one inseparable cluster. Worth weighing against the cost of
leaving it as it is.

**One neutral ratio, recorded without a grade:** background + tools now carry
307k of 533k non-test lines (58%) — more than the world, company and SaaS
layers combined. Not asserted as wrong; named so the periodic end-to-end
consistency review can look at it deliberately rather than discover it.

---

## Risk

- **Touches:** this file only (`docs/staging/`). No executable path, no
  published figure, no gate.
- **Blast radius:** seat attention. The failure mode is these observations
  being read as directives and spawning rules or gates; the mitigation is
  inline — they are hypotheses, the seat owns disposition, and nothing here
  claims priority over drawn work.
- **Consume-path note:** landings/publishing are currently blocked by the
  holder fork; this document is dated, self-contained and remains valid
  whenever it is read.
- **Proportionality:** reversible / narrow.
