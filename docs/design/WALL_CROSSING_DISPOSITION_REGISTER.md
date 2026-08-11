# The wall-crossing disposition register

**Atom:** `KNIFE3_wall_crossing_paydown` (lane `H_harness`, L0→L2), pass 3 of 4 of AO5
**Plan:** `docs/design/KNIFE_HOTSPOT_PASSES.md` § Pass 3
**Mechanism:** `python3 tools/wall_crossing_dispositions.py` — rc 2 if any live crossing has no ruling
**Close-time check:** `python3 tools/wall_crossing_dispositions.py --at-head` — rc 2 if a `cut` row is not cut IN THE COMMITTED TREE (§0a)
**Measured from:** `tools/epistemic_wall.live_crossings()` — the one shared walker, extracted by this pass's first step
**Opened:** 2026-08-09

---

## 0. What this is, and the clause it serves

Pass 3 stated its exit as **conditions, not a number**, and the first condition is the one that
cannot be satisfied by moving a measurement:

> Every one of the 88 surviving crossings carries a disposition. Cut, or explicitly grandfathered
> with a named reason. **No edge survives *unexamined*.**

This document is that examination, one row per edge, and `tools/wall_crossing_dispositions.py` is
what stops it being a promise. The tool reads the rulings from here and the crossings from the
walker, and fails if the two disagree in **either** direction — an unruled live edge is the
unexamined edge the clause is about; a ruling for an edge that no longer exists is a stale register
pretending to cover a tree it has not looked at.

**It does not gate on the count.** Eighty-eight edges each carrying an honest ruling is a pass. One
edge with no row is a failure. R12 governs: the count is a diagnostic, and pass 4 has already
withdrawn "the count falls" once in this programme when its own measurement contradicted it.

---

## 0a. The close-time check: a `cut` is a claim about the REPO, not about your desk

Added 2026-08-10, immediately after the correction in §3a, because that correction was the THIRD
instance of one class in two days and R10 forbids closing an absurdity-class defect with an instance
fix. The other two: KNIFE pass 1 recorded LANDED in a committed doc with four files unstaged, and
the capability index reporting the working tree as the repo's state.

Every instrument in this programme read the working tree. That is correct for a GATE — it must red
before you commit a new crossing — and useless for a CLAIM, because the tree under your feet is not
the tree anyone else gets. `tools/epistemic_wall.crossings_at_head()` runs the *same walker, same
classifiers, same perimeter* against a `git archive HEAD` export; the only difference is one
argument, so a second definition of "a crossing" cannot creep in through the back door.

**The check is deliberately ASYMMETRIC, and this is the part worth reading before changing it.**
The REGISTER is read from the working tree (the claim, as just written); the CODE is read from HEAD
(what a clone gets). The obvious symmetric design — HEAD's register against HEAD's code — is
**blind to the exact case that motivated it**: the B7 tick committed neither its register nor its
code, so HEAD was self-consistently in the old state and a symmetric check passed. The asymmetry is
what turns "I have written down that this is cut" into a testable claim.

Proven against real history, not a mock: the working-tree register replayed against the tree at
`d06df9514` (the commit before the landing) yields **exactly four findings**, naming exactly the four
B7 edges as `ruled cut but the import IS STILL IN HEAD`. R15 mutation coverage —
`tests/tools/test_wall_crossing_at_head.py`, 12 tests — pins the anti-tautology property (the two
modes must be able to DISAGREE, with a vacuity guard proving the disagreement comes from the commit),
three fail-open paths (empty export, truncated export caught by an independent `git ls-tree` oracle,
non-repo), and fail-silent (git absent is an ERROR, never a skip).

---

## 1. The three dispositions

| | Meaning | What the tool checks |
|---|---|---|
| **`cut`** | The edge is **gone from the tree**. | The import is genuinely absent — verified against the walker, never against the claim. A `cut` row whose import is still there is rc 2. |
| **`grandfathered`** | The edge **stays, permanently**, for a named standing reason. A wall-design ruling. | The edge is live, and the reason is substantive (not `TBD`/`later`/`see above`). |
| **`owed`** | The edge is a real violation, it has been **ruled on**, and the cut that kills it is **named**. | The edge is live, and `design=` names a design block that actually exists in §3. |

The exit clause names only the first two. Applied literally to a pass this size, that forces every
edge to be either fixed today or declared permanently acceptable today — and the second is how an
XL pass quietly becomes a green one. Eighty-eight "acceptable"s is not an examination; it is a
surrender with a rubber stamp.

So `owed` carries the weight, and it is deliberately **not** "pending". It is the same device pass 4
used for the 258 orphans, where each row had to name a *consumer* and absent, decorative and refuted
nominations were refused: **a deferral that must name its own mechanism is examined; a deferral that
need only say "later" is not.** A row here names a design, and a design that no row references is
itself rc 2 — a plan for nothing.

---

## 2. What the examination found: the plan's own A/B split was slightly wrong

The pass plan split the 88 into **shape A (67 composition roots) and shape B (21 wall violations)**
by source file. Ruling per *edge* rather than per *file* moves two of them:
`simulation.run_phase2b → company.core.reputation_index` and `→ company.core.resentment_ledger` sit
inside a shape-A file, but the cut that kills them is **B1**, not the composition lift. Disposing an
edge by the cut that actually removes it is the only assignment that keeps `design=` meaningful.

**The real split is 65 / 23.** Recorded rather than quietly fixed, in the same spirit as the three
overlap-table corrections in the plan: this is the fourth time in the programme that measuring
something has corrected the document that scheduled it.

### 2a. The load-bearing finding — three "company" modules are world physics

`company/core/reputation_index.py`, `company/core/resentment_ledger.py` and
`company/core/activation_energy.py` have **zero company-side importers**. Every module that imports
them is SIM-side. And they describe themselves, in their own opening lines, as physics:

> *"the GRI as a first-class **behavioral physics** entity"* — `reputation_index.py`
> *"the Resentment Ledger as a first-class Horizon 2 **behavioral physics** entity"* — `resentment_ledger.py`
> *"**Assign each agent** an Activation_Energy variable representing Status Quo Bias"* — `activation_energy.py`

A customer's accumulated resentment, their status-quo bias, and the market's real regard for the
supplier are facts **about the world**, not the supplier's beliefs about it. They are filed on the
company side, and six crossings exist solely because the world has to reach back across the wall to
read its own physics.

**This matters because it defeats the objection that killed the analogous move in pass 2.** Pass 2
considered moving `saas/customers.py` to the SIM side and rejected it, correctly, because doing so
would re-open class (a) — the strictly forbidden direction that pass 1 had just driven to zero.
Here that objection is refuted by measurement rather than argued away: with **no company-side
importer**, moving these three modules to the SIM side creates **no** class-(a) edge. It is the same
shape of fix, and the reason pass 2 could not do it is absent.

This is also not a relocation past the walker. `tools/` is unwalked, which is why pass 1 refused to
route a dependency through it; `sim/` and `simulation/` are walked byte for byte the same as
`company/` and `saas/`. The edge dies because the dependency stops crossing the wall, not because
the instrument stops looking.

### 2b. Shape A is a composition problem, and the obvious cut is the wrong one

Ten files, 65 edges, all `simulation/run_phase*.py` plus `run_segments`. Measured: **nine of the ten
are leaves inside the wall** — no module in `company/`, `saas/`, `sim/` or `simulation/` imports
them. Only `run_phase2b` has in-edges, and they come from three other shape-A files plus
`simulation.run_scenario`. Every one has a `main()`. They are not the simulated world; they are
scenario harnesses that compose a world and a company and run them together — the same finding pass 1
made about the reporting cycle ("the coupling was never a reporting need, it was a composition"), at
ten times the scale.

**The tempting cut is to move all ten to `tools/` and watch 65 edges vanish. That would be
laundering, and the register says so before anyone tries it.** Pass 1's move was legitimate because
it extracted a *thin* composition — a `main()` that called both layers — and left the substantive
modules in place, clean, still walked, naming the other side nowhere. Here the composition **is** the
substance: `run_phase2b.py` is 2,954 lines of which `main()` is roughly 2,100, and its module-level
definitions are all private helpers of that `main()`. Relocating the file changes no code, removes no
dependency, and moves only the walker's reach. It fails pass 3's own second exit clause — *nothing is
routed through a package the walker does not walk* — and it is precisely the move pass 1 refused.

> **SCOPED 2026-08-10, when this design was drawn for execution — see §3c. Not a correction: the
> paragraph above is right, and step 7 had already measured where its reach ends.**
> The refusal's evidence is `run_phase2b` — 2,961 lines, `main()` ~2,100, walled in-edges. Written
> as "all ten", it reads wider than that evidence, and step 7's own record already drew the line
> before any file moved: *"seven of them are 75-153 line files that are `main()` plus its private
> helpers. That is the criterion that separates a lift from a laundering, and it DERIVES section
> 2b's own refusal for `run_phase2b` rather than contradicting it."* Those seven define nothing any
> module imports and describe themselves in their own opening lines as scripts ("*the orchestration
> glue wiring the five Phase 0b deliverables together — not itself a delegated deliverable, just
> the script that drives them and prints the result*"). For them, "the composition **is** the
> substance" holds in the opposite sense from the one intended: there is nothing else in the file,
> so "extract the thin composition and leave the substantive module walked and clean" has no
> residue to leave behind. They were **misfiled** — the mirror of B1's three behavioural-physics
> modules filed company-side — and the mirror-image cut applies. The refusal stands as written for
> the three files whose measurement supports it: `run_phase2b`, `run_phase4c_on_phase2b`,
> `run_segments`. Recorded because the ban and the exception now live in one place; a reader who
> finds only the ban would put back what §3c cut.

The honest cut is in **B7's** shape, applied ten times: the harness keeps the composition, but the
world-side work it inlines is separated from the company-side decisions it inlines, and only genuine
entry-point composition sits above both layers. That is XL on its own and it is the bulk of what
remains of this pass. Two further constraints the measurement forces, recorded so the next draw does
not rediscover them: `simulation.run_scenario` imports `run_phase2b` and would become a SIM module
depending on a composition root above it, so it moves or it is re-pointed; and `run_phase2b` has 135
referrers outside `simulation/` (mostly tests), so any rename is a large mechanical churn that must
land in its own commit, separately from any behaviour question.

### 2c. There are zero `grandfathered` rows, deliberately

Not one of the 88 is an edge worth defending as permanently legitimate outside the seam. Every one
is either composition-root mislocation (A, B7) or a genuine inversion (B1–B6, B8). The class exists
and is exercised — its guards are mutation-proven against synthetic registers in
`tests/tools/test_wall_crossing_dispositions.py` — but nothing in the live tree claims it. An empty
class is stated here so that a future row appearing in it is a visible event rather than a default.

---

## 3. The cut designs

Each block is referenced by the rows in §4. A design no row references is rc 2.

<!-- WALL-CROSSING-DESIGN A_composition_lift
Was 65 direct edges over 10 files (+3 indirect, §3b). PART 1 EXECUTED 2026-08-10 — the SEVEN
MISFILED harnesses, 16 edges, see §3c. THREE FILES REMAIN and they are the substantive ones:
`run_phase2b` (32 direct + the 3 indirect), `run_phase4c_on_phase2b` (13) and `run_segments`
(4) — 49 direct + 3 indirect.

For these three the §2b refusal stands UNAMENDED and it is now load-bearing rather than
blanket: all three have walled in-edges, and `run_phase2b` is 2,961 lines of which `main()` is
~2,100, so the composition genuinely IS the substance and moving the file would remove the
measurement rather than the dependency. The part-1 cut does NOT generalise to them and §3c
records the four conditions that separate the two cases, each measured per file.

The cut for the remaining three is per-harness separation: the world-side setup the harness
inlines is pushed down into `simulation/`, the company-side decisions it inlines are pushed into
the company layer behind `company.interfaces`, and what remains above both layers is genuine
entry-point composition. Constraints measured, not assumed: `simulation.run_scenario` imports
`run_phase2b` and must be re-pointed or moved with it; `run_phase2b` carries 135 referrers
outside `simulation/`, so the mechanical rename lands in its own commit, separate from any
behaviour question. Two other designs wait on this half specifically and not on part 1 — the B5
residual and the B4 remainder both need a company-side EMITTER, and the bills they need it for
are assembled by `run_phase4c_on_phase2b`, which is one of the three still standing.

STATUS 2026-08-10, and read this before re-deriving the numbers above. `run_segments` was cut at
STEP 10 (§3e), so TWO files remain, not three. STEP 11 (§3f) then executed the company-side half of
the separation described in this block for `run_phase4c_on_phase2b`: bill assembly moved behind
`company.interfaces.bill_assembly`, 3 of its 13 edges cut, leaving 10 on `main()`. The EMITTER that
the last paragraph above says B5's residual and B4's remainder are waiting for NOW EXISTS —
`company/billing/monthly_bill_assembly.py`. Neither push is built; both are unblocked. What remains
of this design is `run_phase2b` (32 direct + 2 indirect) and `run_phase4c_on_phase2b`'s remaining 10.

STEP 14, 2026-08-11 (§3i) took three of those ten: the supplier's month-end CLOSE — issuance gate,
account-6100 shaping, double-entry posting, P&L, billed-clock reconciliation — moved to
`company/finance/accounting_close.py` behind `company.interfaces.accounting_close`. SEVEN remain on
that module and they are TWO GROUPS, not seven items: the customer-value builders (`churn_model`,
`cost_to_serve`, `enterprise_value`, `home_move_win_rate`) and the billing-experience builders
(`contact_model`, `payment_behaviour`); the eighth, `dd_review_runner`, is §3h's routing residual.
Take them as groups — each is one company process the world is currently orchestrating, and cutting
a group is what makes the seam a door rather than a re-export. `run_phase2b`'s 32 + 2 are untouched
and remain the bulk of this design.

STEPS 15 and 16, 2026-08-11 (§3j/§3k) took six of those seven as the two groups named above, leaving
`dd_review_runner` — §3h's routing residual, and §3k records that no further composition lift removes
it. `run_phase4c_on_phase2b` is therefore DONE as far as this design goes.

STEP 17, 2026-08-11 (§3l) opened `run_phase2b` — the file every step so far deferred — with the
supplier's annual statutory return: RO, FiT levelisation and CCL, one group behind
`company.interfaces.statutory_obligations`, 3 of its 34. **31 direct + 2 indirect remain, and they are
FOUR groups, not thirty-one items:** the trading desk (`forward_book`, `hedge_decision`,
`wholesale_credit_exposure`, `hedge_policy`, `collateral_death_test`, `margin_call_book`), the CRM
builders (`churn_model`, `complaints`, `customer_profitability`, `enriched_churn_estimate`,
`nps_tracker`, `payment_behaviour_analytics`, `satisfaction_accumulator`, `tpi_book`,
`churn_accuracy_report`), the pricing/regulatory group (`tariff_engine`, `margin_feedback`,
`ofgem_price_cap`, `decision_policy`) and the `saas.*` set (`cost_to_serve`, `customer_reaction`,
`demand_response`, `growth_mandate`, `ledger`, `property_model`, `smart_meter_rollout`,
`tariff_pricing`), plus the two indirect edges on `account_ledger` /
`payment_observation_consumer`. Take them as groups, one step each, per the same rule §3j set.
WALL-CROSSING-DESIGN -->

<!-- WALL-CROSSING-DESIGN B2_company_brain_decides_the_world
4 edges, and the most serious inversion in the register. It was 5 until step 12 took the CEILING
half away (§3g): `simulation.satisfaction_churn` took the company's MAX_CHURN_PROBABILITY as the
world's ceiling, and that turned out to be B3's shape rather than this one — a CONSTANT the world
could simply own, cuttable in an afternoon without touching who decides anything. What is left is
this design's actual subject and none of it got easier: `simulation.customer_events` imports the
company's own churn model, its customer-reaction model and its home-move win rates in order
to decide WHO ACTUALLY CHURNS. This makes the company's belief self-fulfilling:
the model cannot be wrong about churn, because the model IS churn. That destroys the quantity
the COUPLED TRIAD is built to measure — the gap between what the company believes and what the
world does — and it silently flatters every churn-accuracy figure derived from it. Cut: the
world gets its own churn physics, derived from customer state (resentment stock, activation
energy, price position, tenure) with no import of any company model; the company keeps its
estimate; the harness measures the gap between them. This is a coupled-triad build, not a
mechanical move, and it must not be attempted as one.
WALL-CROSSING-DESIGN -->


---

## 3b. The walker could not see three of them — added 2026-08-10 (step 7)

**This section is not a cut. It is the count going UP, and the reason that is progress.**

`tools/epistemic_wall.py` has carried this sentence since the step-1 extraction:

> *routing a dependency through a package the walker does not walk (`tools/`) moves the
> measurement rather than the dependency, and ... KNIFE pass 1 refused that move.*

True, correct, and **never measured**. Nothing asked whether the tree ALREADY contained such a
route. It did — three, all class (b), all out of `simulation/run_phase2b.py:95`:

```
simulation.run_phase2b -> company.billing.account_ledger
simulation.run_phase2b -> company.billing.arrears_engine
simulation.run_phase2b -> company.billing.payment_observation_consumer
```

Each is carried by **two independent bridges** — `background.live_payment_triad` and
`tools.couple_w2_11_d5` — so cutting either one alone removes nothing. That is why
`IndirectEdge` reports every entry point and not just the shortest chain it happened to walk
first: a checker that printed one route would have told a reader to make a cut that does not cut.

**CORRECTED 2026-08-10, by an event rather than by a re-read.** "Each is carried by two
independent bridges" was an over-claim: it held for two of the three. When `15125f388` removed
`tools/couple_w2_11_d5`'s `from company.billing.arrears_engine import age_bucket` for an unrelated
R15 reason, the `-> company.billing.arrears_engine` route DIED — so that one was carried by that
bridge ALONE, and `background.live_payment_triad` never imported `arrears_engine` at all. The
per-edge entry-point list the checker prints was right; the sentence summarising it across all
three was not. Three indirect edges became two, and the allowlist shrank accordingly. Worth
keeping because the correction cost nothing only because the ratchet reds on a stale entry: an
allowlist that merely *permitted* these would have carried the dead one silently.

**A hazard named in prose and left unmeasured is the fail-open shape R15 names third** — the
check that passes because nobody ran it. Three instruments were affected and all three now share
the wider perimeter, because a report measuring a narrower one than its gate is the third-register
drift the step-1 extraction exists to prevent, wearing a friendlier face:

| Instrument | Before | Now |
|---|---|---|
| ratchet (the GATE) | 72 direct, shrink-only | + `test_epistemic_wall_indirect_ratchet.py`, 20 tests, its own dated shrink-only allowlist |
| this register (the EXAMINATION) | 88 rows / 72 live | 91 rows / 75 live — the three are ruled below |
| KNIFE ledger (the REPORT) | `wall_crossings 72 edges` | `75 edges`, `72 direct + 3 indirect` |

**Why it landed BEFORE the composition lift, and in a commit that cuts nothing.**
`A_composition_lift` moves thin scenario harnesses out of `simulation/` and above both layers,
which in this repo means into `tools/`. That move is a CUT only if nothing walked still reaches
the company through the moved file; otherwise it is exactly the laundering §2b refuses in writing.
Pass 3 could not honestly make it while `tools/` was an unmeasured channel. Instrument first, in
its own commit, with the direct allowlists byte-unchanged — the same rule this pass applied to the
step-1 extraction, applied to its own consequence.

**Proven able to fail, on the real tree, not a fixture.** A laundered route injected into
`simulation/settlement.py` via a throwaway `tools/` module reds three tests in the new module
(`test_no_new_indirect_crossings`, the frozen census, and the per-bridge verdict for `tools`) —
while `test_epistemic_wall_ratchet.py` passes **12/12 on the same injected route**. That green
direct ratchet is the clearest statement of what was missing, and it is a measurement rather than
an argument.

**Class (a) via a bridge is at ZERO** — measured here for the first time, not inherited. KNIFE
pass 1 drove the direct forbidden direction to zero; nothing had asked the indirect question.
`interface/` and `background/` are named in the census and reported on by name, so a clean bridge
is an explicit verdict rather than a silence.

---

## 3c. `A_composition_lift` PART 1 — the seven harnesses were MISFILED, not relocated

**EXECUTED 2026-08-10. 16 edges, 7 files, 75 → 59 live crossings (72 → 56 direct; the 3 indirect
are untouched and that is the proof, see below).**

This is the cut §2b banned, executed on the subset §2b's evidence never covered, against the
criterion **step 7 recorded before any file moved** — so the burden here is not "did the number
fall" but **"is this the laundering the pass banned in writing?"** Four conditions separate the two
cases. Each was measured per file BEFORE the move, and all four must
hold; any one failing puts the file back with `run_phase2b`.

| Condition | Why it is the dividing line | Measured |
|---|---|---|
| **1. Zero importers anywhere inside the wall** | If a walled module imports the harness, moving it hides that module's dependency behind a bridge. That is laundering, exactly. With no walled importer, **no walled module's dependency set changes at all**. | 0 for all seven (`company/`, `saas/`, `sim/`, `simulation/`). The only importers in the tree are three `_resolve_book` imports in one test. |
| **2. The file defines nothing the codebase uses** | "Extract the thin composition, leave the substantive module walked and clean" needs a residue to leave behind. If every symbol is a private helper of `main()`, the whole file IS the composition and there is no second thing to strand. | 75–153 lines each; every module-level symbol unimported outside tests. |
| **3. It is an entry point by its own account** | A misfiling claim has to rest on something other than convenience. | All seven have `main()` + `if __name__ == "__main__"`, and say so in their docstrings — `run_phase0b`: *"the orchestration glue wiring the five Phase 0b deliverables together — not itself a delegated deliverable, just the script that drives them and prints the result"*. |
| **4. What it hands the company is an OBSERVABLE** | The wall's actual claim. A harness that passed sim internals into a company function would be a real violation wearing composition's clothes, and moving it would bury the violation instead of the edge. | Published SSP history, published PC1 shapes, forward prices off the published curve, the supplier's own settled records, the supplier's own supply book. **No sim internal crosses in any of the seven.** Per-edge in §4. |

`run_phase0b`, `run_phase0c`, `run_phase1c`, `run_phase1c_full_window`, `run_phase1c_renewals`,
`run_phase3a`, `run_phase4b_on_phase2b` → `tools/`, which is where `run_annual_report.py`,
`run_segment_report.py` and `run_phase4c_pipeline.py` already live. `git mv`, so the history
follows. The 16 tuples are DELETED from `LEGACY_SIM_READS_COMPANY`: the ratchet floor moved down
with the code and none of the sixteen can return silently.

**The count fell by 16 and the dependency graph did not change. Both halves of that sentence are
true and the register states it rather than letting the number speak.** The same functions call the
same functions in the same order. What changed is that seven files filed as *the simulated world*
are now filed as *entry points*, which is what they always were — the mirror image of B1, where
three files filed as *the company* were behavioural physics. A count that moves because a
misfiling was corrected is the ratchet working; the identical count movement obtained by pushing a
live dependency behind an unwalked hop is the laundering, and condition 1 is what tells them apart.

### The proof that this is condition 1 and not a promise — injected into the real tree

The lift is a cut only while nothing walked reaches the company back through a moved file. That is
not an argument, it is the thing the step-7 indirect ratchet was landed to measure, one commit
before this one, for exactly this reason. Tested by injection rather than assertion:

`simulation/_knife3_reentry_probe.py`, one line — `from tools.run_phase1c import
build_priced_customers` — the precise re-entry that would retroactively turn this cut into a
laundering.

* `live_indirect_crossings()` went 3 → **6**, naming all three:
  `simulation._knife3_reentry_probe -> saas.{clv_seed, customer_reaction, tariff_pricing}`,
  each `via ('tools.run_phase1c',)`.
* `tests/architecture/test_epistemic_wall_indirect_ratchet.py`: **4 failed, 16 passed** — the
  frozen census, the redundancy pin, `test_no_new_indirect_crossings` and the per-bridge verdict
  for `tools`.
* `tests/architecture/test_epistemic_wall_ratchet.py`: **12 passed.** The direct ratchet is blind
  to it, which is the clearest available statement of why part 1 could not honestly have landed
  before step 7 did.
* Probe deleted; indirect ratchet back to **20 passed**, `live_indirect_crossings()` back to 3.

No new control was added for this, deliberately. A `test_no_walled_module_imports_a_lifted_root`
would red on exactly the trees `test_no_new_indirect_crossings` already reds on — a second name for
one measurement, which is the accretion this project forbids and the redundancy the union metric in
§3b was already caught hiding. The existing guard covers the case; the injection above is the
evidence that it covers *this* case.

### What this does NOT unblock, stated because the adjacent designs name it

B5's residual and B4's remainder are both blocked on a company-side EMITTER, and both name
`A_composition_lift` as the blocker. Part 1 does **not** move either: the bills they need stamped
are assembled by `simulation/run_phase4c_on_phase2b.py::build_monthly_bills`, which is one of the
three files still standing. Their blocker is part 2, and it was part 2 all along.

---

## 3d. The three standing files, measured ONE AT A TIME — added 2026-08-10 (step 10)

Part 1 lifted seven files as a group and left three, and both §2b's scoped refusal and the atom's
own step-9 record describe those three with a single sentence: *"all three with walled in-edges."*
**That sentence is FALSE for two of the three, and it was never measured.** An AST census over
`company/`, `saas/`, `sim/` and `simulation/` — the same instrument §3c used, pointed at the files
it did *not* move — finds walled importers only for `run_phase2b`:

| File | 1. zero walled importers | 2. defines nothing the codebase uses | 3. entry point by its own account | 4. hands the company only observables |
|---|---|---|---|---|
| `run_phase2b` (2,961) | **NO** — `simulation/run_scenario.py` | **NO** — 18 module-level symbols imported elsewhere, incl. `tools/fabric_settlement_gap.py` and `run_scenario` | yes | not reached |
| `run_phase4c_on_phase2b` (822) | yes | **NO** — `build_monthly_bills`, 225 lines, assembles the company's bills | **NO — by its own docstring**: *"this module is a pure LIBRARY — it has no CLI and no `__main__` block"* | not reached |
| `run_segments` (631) | yes | yes — `main` is the only symbol anything imports, and only from `tools/` | yes — `main()` + `__main__` + a docstring calling itself a run | **NO, and repairable** — see §3e |

Why the correction matters rather than being pedantry: a group refusal resting on a property two
of its three members do not have is a refusal that cannot be checked. Anyone re-deriving it would
find the claim false and be entitled to conclude the ban was wrong — when in fact the ban is right
for all three and rests on a *different* condition in each case. `run_phase4c_on_phase2b`'s blocker
was never a walled importer: it is that the file is a LIBRARY holding the bill-assembly routine
B5's residual and B4's remainder need a company-side emitter for. Naming its real blocker is what
makes the sentence in §3c above — *"their blocker is part 2"* — mean something specific.

**And naming it is what made it actionable — STEP 11 (§3f) acted on this exact row.** The blocker
this table identified was not "the file cannot move", it was "the bill-assembly routine is on the
wrong side of the wall". Those are different problems with different fixes, and only the second one
has a cut. Step 11 moved the routine and left the file where it is; the row's condition-2 and
condition-3 verdicts BOTH still stand, because `main()` still holds ten crossings and the module is
still a library with no CLI. That is the payoff of measuring per file rather than per group: the
refusal survived intact while the thing it was really about got cut.

The conditions are also now stated as what they are: **per-file, not per-group.** Seven were lifted
together in part 1 because all seven passed all four, not because they were a batch.

## 3e. `A_composition_lift` PART 2 — `run_segments`, and the leak that had to be repaired first

**EXECUTED 2026-08-10. 4 edges, 1 file, 59 → 55 live crossings (56 → 52 direct; the 3 indirect
untouched again, and again that is the proof).**

Conditions 1–3 hold by the §3d measurement. **Condition 4 failed, and it failed on something
real** — not a filing question:

```
price_fixed_tariff(fwd, current_eac, term_start, naked_fraction=1 - MIN_HEDGE_FLOOR)
                                                                  ^ sim.hedging_strategy
```

The world's own minimum-hedge mandate was deciding what fraction of volume the COMPANY prices
capital cost on. That is precisely the leak B7 cut out of `simulation/renewals.py` five steps
earlier, and finding a second live instance of it makes the class real rather than anecdotal (R10:
an absurdity-class defect is not closed by an instance fix). Had this file been lifted with the
leak in it, the leak would have moved to `tools/`, where no instrument counts it — condition 4's
own words, *"moving it would bury the violation instead of the edge."*

**So the repair and the lift land in ONE commit, repair first.** `naked_fraction` now comes from
`company.risk.hedge_policy.COMPANY_MIN_HEDGE_FLOOR`, exactly as `renewal_desk.py::NAKED_FRACTION`
does and as `simulation/run_phase2b.py` already did. **No price moves, and that is measured, not
asserted:** both floors are `0.85`, so both readings produce the identical float
`0.15000000000000002` — the same bits reach `price_fixed_tariff`, so the argument is unchanged and
there is nothing to re-run. Deliberately NOT pinned by a test that the two floors are equal: such
a test would restore in the suite exactly the coupling the cut removes from the code — the trap
B3's design block recorded and B7 refused for this same constant.

The world's copy of the floor is still read in the file, for `RESET_HEDGE_FRACTION` and
`evolve_hedge_fraction` — the world's OWN hedge book and its OWN evolution. Only the argument
crossing into company pricing changed hands. (`run_phase2b` goes further and uses
`company_evolve_hedge_fraction` too; whether the segment run should follow is a behaviour question
that would move numbers, so it is NOT bundled into a wall pass — B7's rule that a pass must never
move a price in the same commit as an import.)

**THE HONEST RESIDUAL, and it is B7's.** On a segment's first gas term the forward comes from
`_bootstrap_gas_price`, built out of `sim.forward_curve`'s private `_ewma`/`_seasonal_shape`, and
that number is handed to the company's pricing function. It is the same cold-start leak B7 named
and preserved in `simulation/renewals.py` (`fallback_forward_price_gbp_per_mwh`) — a supplier's
cold-start rule should be its own. B7 kept it VISIBLE by naming it in a seam signature; here the
edge stops being counted the moment the file is lifted, so it is recorded HERE instead, **owed**,
against the same open company-side question: *what does a supplier quote when it has no price
history?* One answer closes both.

**The count fell by 4, and the dependency graph changed in exactly one place** — the naked-fraction
constant now comes from the company instead of the world. Everything else is the same functions
calling the same functions in the same order.

---

## 3f. Bill assembly is the supplier's own — added 2026-08-10 (step 11)

**3 edges cut, 53 → 50 live. This is the emitter two other designs named as their blocker.**

`simulation/run_phase4c_on_phase2b.py::build_monthly_bills` reached into
`company/billing/back_billing.py`, `company/billing/account_adjustment_register.py` and
`saas/bill_generator.py` — three of that module's thirteen crossings. Assembling a customer's
monthly bill from that customer's settled records is not world physics. It decides the billing
period, whether the bill goes out on a real read or an ESTIMATE, and — when a real read arrives —
how a run of estimated bills reconciles under the Ofgem SLC 31A back-billing cap, including the
SLC 21BA write-off. Every line of that is the supplier's own routine, which a real supplier is free
to change without telling the world. It sat SIM-side for composition reasons only.

Moved to `company/billing/monthly_bill_assembly.py`, behind `company/interfaces/bill_assembly.py`.

### Why this is a cut and not a file move — the read direction is INVERTED

The refusal in §2b/§3d is about moving a file past the walker. This is the other half of the
`A_composition_lift` design as written — *"the company-side decisions it inlines are pushed into the
company layer behind `company.interfaces`"* — and the test that separates the two is what happened
to the dependency, not to the path.

`build_monthly_bills` also called `simulation.meter_reads`: `simulate_read`,
`meter_type_for_customer`, and `MeterReadEvent` for the forced final read. **Carrying those imports
across would have traded three class-(b) edges for three class-(a) ones** — company reading SIM
internals, the STRICTLY FORBIDDEN direction, which is at zero. The count would have fallen by three
and the wall would have been in worse shape. That is the laundering, and it is the reason this cut
took a design rather than a `git mv`.

So the dependency is inverted instead. Whether a read ARRIVES is world physics; a supplier
*observes* reads. The company therefore imports nothing from the world and receives a
`ReadArrivalFeed` (a `runtime_checkable` Protocol) from its caller. The world's implementation is
`simulation/meter_reads.py::SimulatedReadFeed`. At go-live it is a real D0010/DTC adapter behind the
same unchanged Protocol — the swap `tools/meter_read_port.py::MeterReadPort` was built for, and the
typed-flow seam preference applied rather than quoted.

### Behaviour is unchanged BY CONSTRUCTION, which is a stronger claim than measured

`SimulatedReadFeed` is a pass-through: the same `meter_type_for_customer` / `simulate_read` /
`MeterReadEvent` called with the same arguments in the same order the inline code used, so the
identical objects come back. There is no seed to re-derive and no second code path to keep in step.

This was deliberately NOT done the other way. The obvious alternative — have `main()` pass in the
`generate_meter_read_log()` events it already builds — would also have cut the edges AND closed the
read DUPLICATION the function's own docstring records as a follow-up. It was refused because the
two paths agreeing rests on an *asserted* identical seed, so that version would move numbers if the
assertion were ever wrong, and a wall pass is not where a behaviour change gets discovered. The
duplication stays recorded as owed.

### The blocker two designs recorded is now gone, and neither push was built

`company/interfaces/collections_communication.py` (B5) and `company/interfaces/dd_review_outcome.py`
(B4) each stated the same structural blocker in their own docstrings: they could deliver a PULL and
not the PUSH their design asks for, because *there was no company-side bill emitter to stamp an
attribute onto*. There is one now. Both docstrings are corrected in the same commit.

**Neither push is built here, on purpose.** B5's own words are that a push with the substance of a
pull is *"a strictly worse artefact than an honest pull through a named door"*; shipping the emitter
and claiming the pushes in one commit would be the same error one layer up. The emitter is the
enabling condition, not the work. Both remain owed, now against a live seam rather than a missing one.

### What did NOT move

`main()` keeps its other ten crossings — `dd_review_runner`, `pre_bill_validation`,
`domain_invariants`, and the seven `saas/` builders. Those are `run_phase4c_on_phase2b`'s remaining
composition problem and §3d's per-file conditions still refuse the file itself. `build_monthly_bills`
survives at its old path as a thin world-side wrapper supplying the feed: it is the world's own call
site, it is what `saas/ledger.py` and `simulation/meter_reads.py` document by name, and keeping it
meant no test and no caller had to learn about the feed.

### The two ways this cut could rot silently, and the control that fires on each

Added 2026-08-10 with the cut: `tests/company/interfaces/test_bill_assembly_seam.py`, the same
shape passes 1 and 2 gave their seams. The wall ratchet already polices the STATIC half of the
inversion — a module-scope `company.billing.monthly_bill_assembly -> simulation.*` import is a new
class-(a) edge with no grandfathering left to hide behind. Two exposures it cannot see, per R15:

1. **A lazy import.** The ratchet's own docstring states the limit: static imports only, and an
   in-function or `importlib` import escapes it. The natural convenience change here is exactly
   that — make `read_feed` optional and construct the world's feed inside the function so callers
   "don't have to bother" — and it would re-cross the wall in the forbidden direction with every
   static instrument in the tree still green. The control is therefore BEHAVIOURAL: it runs the
   real billing run in a CLEAN interpreter (in-process, `simulation.*` is already in `sys.modules`
   from the rest of the suite, so a lazy import would be served from cache and leave no trace) and
   reports which modules loaded. Observed: 2 bills built, zero `sim`/`simulation` modules loaded.
   Its mutation copies the module's real source with `import simulation.meter_reads` inserted into
   `build_monthly_bills` and asserts the probe reds — it does, naming `simulation.meter_reads`.
2. **A reordered feed.** `ReadArrivalFeed` is `runtime_checkable`, and that checks method PRESENCE
   only, never signatures — a documented stdlib fail-open, and it bites here because every feed
   call site passes POSITIONALLY. So the second control compares parameter names AND order between
   `SimulatedReadFeed` and the Protocol, and its mutation exhibits a feed with two parameters
   swapped that `isinstance()` still accepts. The `isinstance` check alone was not evidence.

---

## 3g. `B3_world_needs_its_own_cap_physics`, applied a SECOND time — added 2026-08-10 (step 12)

**`simulation.satisfaction_churn -> saas.churn_model` is cut. 50 → 49 live (48 → 47 direct).**

B3's executed block (§3a) ends by naming the shape it had just cut: *"a belief constituting the
fact it is a belief about ... that is B2's shape at one edge instead of five."* It was describing
the price cap. The same sentence was true, unread, of a second edge in the register — and it was
filed under B2, the design that says of itself *"this is a coupled-triad build, not a mechanical
move, and it must not be attempted as one."*

**The finding is the FILING, not the fix.** `simulation/satisfaction_churn.py` clamped the world's
GROUND-TRUTH churn probability at the company's `MAX_CHURN_PROBABILITY`. B2's four other edges hand
the company's *reasoning* the job of deciding who churns; this one handed it a *number* — a ceiling
the world can perfectly well own. Being filed alongside the hard four is what kept it looking like a
coupled-triad build for a day longer than it was. **A design block is a ruling about a class, and an
edge can sit in the wrong class while every count above it stays correct.** Worth recording because
the register's whole method is ruling by class: the classes are load-bearing, so a misfiled member
is a defect of the same kind as a miscounted edge, and nothing in the tooling looks for one.

**The world's ceiling had three copies and one of them was the company's.** Before the cut:
`satisfaction_churn` borrowed the company's constant, `switching_propensity` carried a private
`_MAX_CHURN_PROBABILITY = 0.95`, and `customer_events` had a bare `0.95` literal inside a `min()`.
One world fact, three expressions, and the register already names what that becomes (`one name, two
numbers`). The cut gives it one home on the world's side — `simulation/churn_ceiling.py` — and folds
the other two in. **Only the first is an edge**; the other two are housekeeping that arrived with it
and are recorded as such, not counted.

**No number moves, and that is measured rather than asserted.** Both ceilings are 0.95, so every
clamp returns the identical float; the world's arithmetic is bit-for-bit what it was. What changed
is who depends on whom.

**The control, and what it deliberately does NOT assert.** No test pins the two constants equal —
that would restore in the suite exactly the coupling the cut removes from the code, which is the
refusal B3 recorded for the cap schedule and B7 for the hedge floor, for the third time here.
`tests/simulation/test_churn_ceiling.py` asserts INDEPENDENCE by mutation instead, and both
mutations were RUN on the real tree, not named:

  1. **The company's ceiling mutated to 0.10** → the world's clamp does not move.
     Re-injecting the deleted import (`from saas.churn_model import MAX_CHURN_PROBABILITY as
     WORLD_MAX_CHURN_PROBABILITY`, a same-name alias so nothing else has to change) reds
     `test_mutating_the_companys_ceiling_does_not_move_the_worlds` AND
     `test_no_sim_module_names_the_companys_churn_constant`, and independently reds four tests in
     `test_epistemic_wall_ratchet.py` including the frozen census. 6 failed / 12 passed; reverted.
  2. **THE VACUITY GUARD, which is the one with teeth.** Mutation 1 proves nothing on its own — it
     would pass identically against a company constant that nothing reads (`donated residual is not
     a control`). So `test_the_same_mutation_does_move_the_companys_own_answer` asserts the same
     mutation DOES move the company's own capped estimate. Replacing `MAX_CHURN_PROBABILITY` with a
     literal `1.0` inside `saas.churn_model.churn_probability` reds exactly that test and nothing
     else. 1 failed / 5 passed; reverted.

  A third guard, `test_the_world_clamp_actually_binds`, covers the vacuity in the other direction:
  a ceiling no input can reach makes every independence claim about it vacuously true.

**The named-edge control asks the WALKER, never a substring.** A substring scan fails on its own
subject here — the docstrings recording *why* the import went away contain both `saas.churn_model`
and `MAX_CHURN_PROBABILITY`. That is the `REVIEW_GATE must match idleness, not prose mentioning the
string` class, which bit this programme once already at §3a, so the control calls
`tools.epistemic_wall.live_crossings()` — the one definition of "a crossing" this pass extracted as
its first step, and the reason that extraction was the first step.

### The wall was enforced only AFTER the commit, and that is now fixed

Found while placing the control: `tests/architecture/test_epistemic_wall_ratchet.py` was not in
`tools/pre_commit_test_gate.py`'s always-run `CONTROL_TESTS`. Per-file selection ran it when the
RATCHET was edited — the case that needs it least — and stayed silent when a sim module landed a
fresh `saas.*` import, which is the only case it exists for. So a crossing could LAND on committed
HEAD and wait for the post-commit publish gate to find it, which is precisely what
`WORKER_FINDING_THE_EPISTEMIC_WALL_IS_BREACHED_AT_HEAD_2026-08-09` cost.

It is the same R10 class the three neighbouring `CONTROL_TESTS` entries were each added for (a
whole-tree scanner reachable only from the scanner's own file), applied to the one control CLAUDE.md
classes as a **WALL** rather than a dial. Added, with its cost stated rather than glossed: ~4.8s on
every code commit, by far the most expensive entry in that list, because it is an AST walk of four
packages.

**What this does NOT close.** B2 keeps all four `customer_events` edges and loses none of its
difficulty — the world still asks the company's brain who churns. This cut removes a guaranteed zero
from the coupled-triad gap score; it does not narrow the gap, because there was never a gap here to
narrow.

---

## 3h. The world was OPERATING the supplier's collection register — added 2026-08-10 (step 13)

**`simulation.dd_collection_book -> company.billing.direct_debit` is cut. 49 → 48 live (47 → 46
direct). `B4_billing_mechanics_reached_directly` is DONE — 4 of 4 edges, the first design in this
register to close completely.**

### The edge B4 called the hard one, and why it was harder than the other three

B4's other three edges were the world *consulting* the company: a private helper, a compliance
book, a constant. This one was different in kind and the block said so —

> `dd_collection_book` does not merely CONSULT the company's billing module — it BUILDS the
> company's artefact ... so the world is operating the supplier's collection register.

Concretely, inside the world's own loop: `DirectDebitBook()` opened, `create_mandate(...)` called
with the masked bank details the supplier files, a rolling-median re-estimate deciding when the
standing amount had drifted far enough to write to the customer's bank, `next_collection_on_day`
snapping the collection onto the customer's anniversary, and `DDPaymentAttempt(...)` appended with
the register's own `"collected"`/`"failed"` vocabulary. A household does not run its supplier's
collections desk. It is told an amount and a date, the money moves or it does not, and the
supplier writes that down.

### This one is a PUSH, and that is the difference from B4's other two doors

`credit_refund_requests.py` and `dd_review_outcome.py` both landed as PULLS through named doors,
and both docstrings record the same honest limit: B4 asks the company to EMIT and the world to
APPLY, and there was no company-side emitter to emit from. Step 11 removed that blocker
(`company/billing/monthly_bill_assembly.py`) and both pushes stayed owed against it.

**This edge did not need to borrow that emitter, and noticing that is the finding.** The blocker
those two doors recorded is specific — a *bill* attribute needs a *bill* emitter. What this edge
needs is a **collection instruction**, and the desk that decides collections is its own emitter.
Reading "A_composition_lift's work" off the sibling rows would have parked this edge behind
`run_phase2b`'s 32-edge composition problem indefinitely. **A blocker inherited from a sibling row
is a claim to re-measure, not a fact to adopt** — the same shape as step 12's finding one section
up, where an edge sat in the wrong design class while every count above it stayed correct.

So: `company/billing/dd_collections_desk.py` owns the register and issues three instructions —
`MandateSetupInstruction`, `AmendmentInstruction`, `CollectionInstruction`. The world puts each on
the Bacs rails, and reports back what the rails did: the AUDDIS confirmation date, the ADDACS
confirmation date, the date a collection resolved, whether the money arrived, and the ARUDD reason
text when it did not. Rails timing is industry physics — the supplier observes it, it does not
choose it. What no longer crosses: `DirectDebitBook`, `DirectDebitMandate`, `DDPaymentAttempt`,
`next_collection_on_day`, the materiality floor and the re-estimation window.

### What stayed world-side, deliberately

**Whether the money arrives.** `simulation/arrears_engine.py::payment_outcome` keeps it, drawn
from its own per-bill substream. A desk that decided its own collection outcomes would be the B2
inversion in miniature — the company's belief constituting the fact it is a belief about — and it
would silently flatter every collection-success figure the register feeds. `record_collection_outcome`
takes `collected` as an argument and has no other route to it.

**The customer's collection day.** `staggered_payment_day` moved to the world at step 9 for
exactly this reason; the world hands it over at mandate setup, as a customer tells their supplier
which day suits them.

### No number moves, and it is measured rather than asserted

Every routine was lifted with its arithmetic, its ordering and its reference strings unchanged. A
140-customer, 30-month population (seasonal swing, a sustained step change in a fifth of the book,
mixed segments and commodities) built through `build_dd_collection_book` before and after:
**74 mandates, 2,220 attempts, sha256
`fb084d0d52a9136576d71652d7a6430e7d39e21366f84609cde2d42f79bc2fb0` on both sides.** The rails RNG
substream matters here and was preserved by construction: `rails_rng` is drawn only by the
collection's own `resolve_submission`, and this cut changes which module *issues* a submission,
never how many are issued or in what order.

That hash is deliberately **not** pinned in a test. It is an equivalence claim about a moment in
history, and a control asserting it would fail on the next legitimate change to the re-estimation
routine while proving nothing about that routine's correctness — `never pin generated values in
controls`.

### The way this cut could rot silently, and the control that fires on it

`tests/company/interfaces/test_dd_collection_instructions_seam.py` (9 tests) and
`tests/company/billing/test_dd_collections_desk.py` (17 tests).

**The exposure is the door widening, and no existing instrument can see it.** Adding
`DirectDebitBook` to the seam's imports — the obvious convenience, since
`build_dd_collection_book`'s return is now deliberately unannotated for want of a name — would
hand the world the register's construction back **with the epistemic ratchet still green**,
because the SIM's import still terminates on the exempt seam package. R15 evidence, both
mutations performed on the real tree rather than named:

  1. **The widening reds the control.** `DirectDebitBook` re-exported at the seam →
     `test_the_door_exposes_only_the_desk_and_its_instructions` and its paired mutation test fail
     (2 failed / 7 passed). Two further widenings are parametrised: `DDPaymentAttempt` (the
     register's construction) and `AMENDMENT_WINDOW_BILLS` (the supplier's re-estimation routine
     handed over as a constant).
  2. **THE VACUITY GUARD, which is the one with teeth.** Mutation 1 proves nothing on its own if
     something else already catches it — that would make this suite a `donated residual`. Under
     the *same live widening*, `tests/architecture/test_epistemic_wall_ratchet.py` is **12 passed
     / 0 failed**. The ratchet is blind to it by construction, measured rather than argued. The
     in-suite version compares `live_crossings()` before and after and asserts the sets are
     identical.
  3. **Re-injecting the deleted import is caught** by a control that asks the WALKER, never a
     substring — the docstrings recording why the import went away contain both
     `company.billing.direct_debit` and `DirectDebitBook`, so a text scan fails on its own
     subject. That is the `REVIEW_GATE must match idleness, not prose mentioning the string`
     class, which bit this programme at §3a and again at §3g.

**The limit, stated rather than glossed:** neither control can see a COPY. A re-implementation of
`next_collection_on_day`'s arithmetic inside `simulation/` under a different name would create no
edge and expose no forbidden name — the `one name, two numbers` defect this register names
elsewhere. Nothing here detects that.

### The honest residual

`collection_register()` returns the desk's own `DirectDebitBook` so the run's report serialiser
can read it, and the world holds that object for one hop on the way. It cannot name the type,
construct one, or write to it through any exported name, so the property B4 asked for holds. What
remains is one layer up and belongs to `A_composition_lift`:
`simulation/run_phase4c_on_phase2b.py::main` is what threads the register into the report. That is
a routing residual, not a decision the world takes.

---

## 3i. The month-end close is the supplier's own — added 2026-08-11 (step 14)

**3 edges cut, 48 → 45 live (46 → 43 direct; the 2 indirect untouched, and again that is the
proof). `A_composition_lift`, the company-side half of `run_phase4c_on_phase2b`, continued from
§3f.** Ten crossings remained on that module after bill assembly; three of them were one process.

`main()` ran the supplier's month-end itself: it partitioned the bill list through
`company/billing/pre_bill_validation.py`'s Tier-1 issuance gate, shaped the customer-value layer's
cost-to-serve schedule into account-6100 events with `saas.ledger.make_cost_to_serve_event`, merged
those with the run's acquisition-spend and fixed-cost events, posted the double-entry ledger,
derived the P&L, summarised it, and then checked
`company.compliance.domain_invariants.check_billed_clock_reconciles` against the result — the last
of those through a function-scope import buried 350 lines into the file.

Not one of the five steps is world physics. A real supplier changes its issuance gate, its chart of
accounts, its revenue-recognition policy and its month-end reconciliation without telling anyone.
The world's contribution is the SETTLED RECORDS — what physically flowed — plus two spend schedules
it already emitted as data. All of it now goes through `company/interfaces/accounting_close.py` into
`company/finance/accounting_close.py`, which returns an `AccountingClose`.

### The read direction, again, because it is what separates a cut from a file move

`company/finance/accounting_close.py` imports nothing from `simulation/` or `sim/`. The settled
records arrive as plain dicts through the signature. Moving the close with a world import intact
would have traded three class-(b) crossings for class-(a) ones — the strictly forbidden direction,
at zero and staying there. Same test §3f applied to bill assembly, and it is enforced the same way:
`tests/company/interfaces/test_accounting_close_seam.py` runs a real close in a clean interpreter
and asks `sys.modules` which world modules loaded, because a LAZY in-function import is invisible to
the static ratchet by that file's own documented limit. The mutation performs exactly that import
and the control fires.

### Behaviour is unchanged BY CONSTRUCTION, and then measured anyway

Nothing is reimplemented: the same five functions are called with the same arguments in the same
order, including the `extra_events or None` collapse, which is preserved verbatim so there is not
even an empty-list-versus-None question to argue. That is the §3f-class claim.

It is nevertheless MEASURED, because "by construction" is exactly what a dropped step also looks
like from the outside. The seam test transcribes the PRE-CUT inlined sequence from the source it
was lifted out of — not from the module under test, which would be a mirror — and asserts the
door's `events`, `pnl` and `meta` are identical over a fixture carrying two customers, three
settlement records, two issuable bills, one HELD bill and both spend schedules. Two mutations prove
it can fail: dropping the issuance gate, and reordering the merged extra events.

The reorder mutation is worth recording because the OBVIOUS version of it cannot fail.
`build_ledger` sorts by `(timestamp, settlement_period, event_type)` with a stable sort, so swapping
the acquisition and fixed-cost schedules changes nothing — those two differ in `event_type` and the
sort is total over them. Order is observable only where the key TIES, so the control uses two
acquisition events in the same month. A reorder control built on the obvious swap would have been a
control that cannot fail, which R15 rates worse than none.

### THE TAUTOLOGY THIS CUT CREATES, stated because moving code created it

The billed-clock invariant asks whether the ledger's recognised revenue reconciles with the bills
that fed it. Before this step, `validate_bills(...)` and `check_billed_clock_reconciles(...)` sat in
different paragraphs of a 419-line run module. They are now four lines apart in one function, and
that adjacency is a live hazard: feed the UNFILTERED bill list to `build_ledger` *and* to
`check_billed_clock_reconciles` and the invariant returns True while the held bill's revenue is
recognised — a real accounting error, green suite. It is the R15 TAUTOLOGY pattern exactly: the
checked value derived from the same source it checks. The invariant is a control only while its two
sides come from different populations.

This is NOT a defect introduced by the cut — the same tautology was available before, at greater
typing distance — and it is not repaired by argument. The seam test carries an INDEPENDENT control
that does not consult the flag at all: it asks the EVENTS whether the held bill's £9,999 was posted,
and asserts the held half comes back so a caller cannot fail to notice a bill was withheld. Its
mutation performs the tautology and asserts, in the test body, that the invariant stayed green —
so if a future change makes the tautology impossible, the control announces that rather than
quietly passing.

### What did NOT move, and the count that did not fall as far as it looks like it should

`saas.payment_behaviour` remains a live crossing of the run module. The close no longer receives the
payment model from the world — it imports the supplier's own credit-risk and bad-debt model
directly, which is the correct ownership — but `build_payment_behaviour(bills)` is still called
world-side for the billing-experience output, so the module-level edge survives until that group is
cut. Stated here rather than left to be discovered from a count of 3 where a reader might have
expected 4. The model stays injectable for one measured reason, not for symmetry: `build_ledger`
writes a real `CREDIT_COLLECTIONS_POLICY` decision-log entry per provisioned bill, and a test that
could not substitute the model would either append to the company's audit trail or never reach the
provisioning path at all. The seam test asserts the default IS `saas.payment_behaviour` — a `None`
default would silently drop every payment and bad-debt event from the ledger, which is the
fail-open shape, not a convenience.

**Seven crossings remain on `run_phase4c_on_phase2b`**, and they are two coherent groups rather than
a list: the customer-value builders (`saas.churn_model`, `saas.cost_to_serve`,
`saas.enterprise_value`, `saas.home_move_win_rate`) and the billing-experience builders
(`saas.contact_model`, `saas.payment_behaviour`), plus `company.billing.dd_review_runner`, whose
residual §3h already recorded as a routing question rather than a decision.

---

## 3j. The customer-value layer is the supplier's belief, not the world's arithmetic — added 2026-08-11 (step 15)

**4 edges cut, 45 → 41 live (43 → 39 direct; the 2 indirect untouched, and again that is the
proof that a bridge route was not silently taken instead). `A_composition_lift`, continuing §3i's
company-side paydown of `run_phase4c_on_phase2b`.** Seven crossings remained on that module after
the month-end close; four of them were one process.

`main()` composed the supplier's customer-value layer itself: it costed every customer
(`saas.cost_to_serve`), formed a churn belief over the book (`saas.churn_model`), priced home-move
retention off that belief (`saas.home_move_win_rate`), valued the book on both
(`saas.enterprise_value`), and separately shaped the cost-to-serve schedule into the account-6100
posting series the close consumes.

None of it is world physics. How a supplier apportions cost to a customer, what it believes about
who will leave, and what it thinks its book is worth are its own models — a real supplier changes
all four without telling anyone, and gets them wrong without the world noticing. What the world owns
is the SETTLED RECORDS and the customer book, as data. All of it now goes through
`company/interfaces/customer_value.py` into `company/analytics/customer_value_view.py`, which
returns a `CustomerValueView`.

### Why this is a GROUP and not four items

§3i's own instruction. The four builders are one process with a dependency chain inside it:
`build_home_move_win_rates` needs `churn_risk`, and `build_enterprise_value` needs both
`churn_risk` and `cost_to_serve`. Cutting them one at a time would have left the world holding the
intermediate beliefs and threading them back in — a seam that publishes a PULL is half a cut, and
the count would have fallen while the coupling stayed. Taking the group means the chain is internal
and the door carries only what the world actually owns.

### `price_differential_pct` is PASSED, not read

Both the home-move and enterprise-value models need the run's market-position parameter. It is a
signature argument rather than a module read, so no world constant crosses the wall to set it —
the same shape §3e used for the hedge floor and §3g for the churn ceiling. A parameter threaded
through a seam and then ignored is the donated-residual shape, so it is not left to inspection:
`test_mutation_price_differential_is_actually_read` moves it and asserts both the win rates and the
enterprise value move with it.

### The read direction, and the one thing that genuinely moved

`company/analytics/customer_value_view.py` imports nothing from `simulation/` or `sim/` — records
and customers arrive as plain dicts — so no class-(a) edge is traded for the four class-(b) ones.

Behaviour is unchanged by construction for the four builders: same functions, same arguments, same
order. **One thing did move, and it is recorded rather than glossed:** the account-6100 schedule
(`build_cost_to_serve_ledger_events`) used to be computed ~50 lines LATER in `main()`, just before
the close; it is now computed inside the view, earlier. The identity claim for that move is that
its inputs — `all_records` and `all_customers` — are the same at both points. That claim is not left
as a reading of the file. Control 3 parses `main()`, takes the region between the view call and the
`close_the_books` call, and asserts nothing in it mutates or rebinds `all_records`; its mutation
injects exactly the defect the move would expose (a record appended between the two points, which
pre-cut would have reached the 6100 schedule and post-cut would not), and no other test in the suite
notices it. It carries a VACUITY GUARD, because a region-shaped control passes for free once the
region empties: the guard asserts the region is still more than five statements, so a future
refactor that empties it fails loudly and control 3 gets retired rather than left as decoration.

### What did NOT fall, stated rather than left to be inferred from a count that stops at 4

Three crossings remain on the module: the billing-experience builders (`saas.contact_model`,
`saas.payment_behaviour`) — a different process on a different input (`bills`, not settled records)
— and `company.billing.dd_review_runner`, which §3h already ruled a ROUTING residual. They are the
next group, not this one.

## 3k. The billing-experience layer is the supplier's belief about its own book — added 2026-08-11 (step 16)

**2 edges cut, 41 → 39 live (39 → 37 direct; the 2 indirect untouched, and again that is the proof
that a bridge route was not silently taken instead). `A_composition_lift`, finishing §3j's paydown
of `run_phase4c_on_phase2b`.** Three crossings remained on that module after the customer-value
layer; two of them were the group §3j named as next.

`main()` composed the supplier's billing-experience layer itself: it segmented every customer by
credit risk, booked a bad-debt provision at that segment's rate, derived the payment date it expects
from each (`saas.payment_behaviour`), and estimated how likely each bill was to generate a contact,
how many of those escalate, and the service-quality score that falls out (`saas.contact_model`).

None of it is world physics. Which of its own customers a supplier calls a credit risk, what it
provisions against them, when it expects to be paid, and how it models a confusing bill becoming a
complaint are its own beliefs — a real supplier changes all of them without telling anyone and is
wrong about them routinely. What the world owns is the BILLS, as data. Both now go through
`company/interfaces/billing_experience.py` into `company/analytics/billing_experience_view.py`,
which returns a `BillingExperienceView`.

### The group argument here is WEAKER than §3j's, and that is stated rather than borrowed

§3j's four were a group because of a dependency CHAIN: cutting one at a time would have stranded an
intermediate belief world-side, so the group was forced. These two are INDEPENDENT of each other —
neither reads what the other writes, and either could have been cut alone with no PULL created.
They travel together for a weaker and more ordinary reason: one input (`bills`, and nothing else)
and one question. Two doors onto the same argument list, differing only in which belief comes back,
would be two doors for no gain. Recorded this way because copying §3j's chain argument onto a pair
that has no chain would make the register say something false about its own reasoning.

### The bill list crosses UNFILTERED, and that is a decision with a control on it

~120 lines below the moved call, `close_the_books` partitions these same bills through the Tier-1
issuance gate and recognises revenue only against the ISSUED half (§3i, `BILL_TO_LEDGER_LINKAGE.md`).
The obvious tidy-up when recomposing is to apply the same filter here for consistency. It would be
wrong in both directions: a HELD bill has not been sent, so it can generate no contact — but the
provision a supplier books against a customer's credit risk does not vanish because a bill sat in
the exception queue, and the pre-cut code provisioned against every bill. The filter would move the
bad-debt figure silently: no exception, no static signal, just a smaller number in the run output.
So it is not left to a paragraph — `test_mutation_filtering_to_the_issued_half_moves_the_view` runs
the real `validate_bills` over the fixture book and asserts the provision moves, and its VACUITY
GUARD (`test_the_fixture_actually_contains_a_held_bill`) fails loudly if the gate ever stops holding
the bill built for it, rather than letting the control compare a book against itself.

### The read direction, and behaviour unchanged by construction

`company/analytics/billing_experience_view.py` imports nothing from `simulation/` or `sim/` — the
bills arrive as plain dicts — so no class-(a) edge is traded for the two class-(b) ones. Same two
functions, same argument, same relative order, same point in `main()`; nothing is reimplemented and
neither builder reads what the other writes, so the order is not load-bearing and nothing here
claims it is. The lazy-import escape the static ratchet cannot see is covered behaviourally: the
seam test builds a real view in a clean interpreter, asks `sys.modules` which world modules loaded,
and its mutation performs exactly that import.

### THE LEAK THIS CUT DOES NOT REPAIR, named because the new door would otherwise imply it was clean

`simulation/contact_centre.py::generate_contact_centre_log(bills, contact_model)` draws the world's
ACTUAL contact events off `contact_probability` — the number this view computes as the supplier's
ESTIMATE. The company's belief about how often it will be contacted therefore CONSTITUTES how often
it is contacted. That is the B2/B3 inversion, the same shape as `simulation/satisfaction_churn.py`
clamping the world's churn at the company's `MAX_CHURN_PROBABILITY` before §3g cut it, and the same
shape as §3e's `naked_fraction`.

It pre-dates this cut and is untouched by it: the crossing paid down here is the run module's
IMPORT, not the world's use of the returned dict. It is FILED rather than fixed on sight
(`SELF_INTERRUPT_DISCIPLINE` — the repair is a world-side contact-physics module with its own
independence proof, a B3-shaped atom, not a line in this one):
`docs/staging/WORKER_FINDING_THE_WORLDS_CONTACT_RATE_IS_THE_COMPANYS_ESTIMATE_2026-08-11.md`.
Recorded here because after the cut the flow reads as a sanctioned seam hand-back, and a reader
could take the door as evidence the direction was examined and found clean. It was examined and
found DIRTY, in a dimension this pass does not own. The seam test deliberately carries no control
for it: a control here would either pin the leak in place or fail on day one.

### What is left on this module — ONE, and it is a residual by ruling

`company.billing.dd_review_runner` is the last crossing of `run_phase4c_on_phase2b`, and §3h already
ruled it a ROUTING residual (the world threads the desk's own register into the report) rather than
a decision the world takes. No further composition lift removes it, because there is no company
PROCESS left here to lift — only a value carried from a company organ into the run's output dict.
Stated so a future pass does not draw this module again expecting a cut that its own ruling says is
not there.

## 3l. The statutory return is the supplier's own accounting — added 2026-08-11 (step 17)

**3 edges cut, 39 → 36 live (37 → 34 direct; the 2 indirect untouched, and again that is the
proof). This is the FIRST cut on `run_phase2b`, the file every previous step deferred.**

`simulation/run_phase2b.py::main()` computed the supplier's whole annual statutory return itself —
Phase OG (Renewables Obligation), Phase OH (FiT levelisation levy), Phase OI (Climate Change Levy),
three contiguous blocks reaching `company.regulatory.roc_ledger`, `company.regulatory.fit_book` and
`company.regulatory.ccl_ledger`. Working out what you owe under the RO, the FiT levelisation
mechanism and the CCL off your own supply volumes is not physics: it is a licensed supplier doing
its own statutory accounting, and getting it wrong is what Ofgem and HMRC fine suppliers for. Now
`company/regulatory/statutory_obligations.py` does it behind
`company.interfaces.statutory_obligations`, and the world hands over the settled records and its own
two I&C rosters as DATA.

### It reached through the wall for three PRIVATE tables, which is worse than the edge count says

Worth naming because the count alone does not show it. The world was not merely calling three
company ledgers — it imported `_ROC_OBLIGATION_LEVEL`, `_ROC_BUY_OUT_PRICE_GBP` and
`_FIT_LEVELISATION_RATE_PER_MWH`, three underscore-prefixed rate tables, to build the per-year
figures itself. The obligation level and the buy-out price are the two numbers that DEFINE the
supplier's RO liability; the world reading them directly is the same shape of inversion as B2's,
scaled down to constants. They are now read inside the layer that owns them.

### Why this is a GROUP and not three items

RO and FiT are computed off ONE shared accumulator — annual electricity volume supplied
(`_elec_mwh_by_year` in the code this replaced). Cutting them separately would have left the world
holding that intermediate and threading it into both doors: a seam that publishes a PULL is half a
cut, which is §3j's rule and the reason the customer-value four went together. CCL joins them
because it is the same process on the same input at the same point in the report — one annual
statutory return — and it is the only one of the three needing the segmentation.

### Behaviour is unchanged BY CONSTRUCTION, and the identity is measured anyway

The three blocks are transcribed statement-for-statement in their original order, off the same
inputs, with the rounding at the same places and the same summary keys; the three summaries flow
into the same three slots of the output dict. `tests/company/interfaces/test_statutory_obligations_seam.py`
control 2 does not take that on trust — it replays the PRE-CUT inlined sequence, transcribed from
`run_phase2b.py` as it stood at `57cb9d872`, and asserts all three summaries are equal. Its mutation
drops the RO commodity filter and proves the comparison can fail.

### THE DEFECT THIS CUT INTRODUCES, stated because moving code created it

Before the cut, CCL read `ELEC_CUSTOMERS` and `GAS_CUSTOMERS` at the point of use, so the elec
roster could not arrive where the gas roster belonged. Now both are built at the call site and
passed into one signature — and a swap, or a dropped `segment == "I&C"` filter, would change every
CCL figure while every test exercising the impl module directly stayed green, because the impl would
be given exactly what the caller chose to give it. Control 3 is an AST check over the real call site
with a vacuity guard on the number of calls examined (zero calls → every finding list is empty for
free), and two mutations that perform the swap and the dropped filter. Control 1 is the standard
behavioural lazy-import detector, mutated on a COPY of the real source so no repo file is edited
mid-run. **9 tests, 3 of them mutations.**

### The residual this cut declines to fix, and why

`FITBook.levelisation_charge_gbp(year, total_mwh_supplied)` is called with `_mwh_fit * 1000.0` and
divides by 1000 internally, so the parameter named MWh is handed kWh and the two errors cancel: the
arithmetic is right and the naming is wrong. Found while transcribing, NOT repaired here — B7's rule
is that a wall pass never moves a number in the same commit as an import, and this one is one
careless edit away from moving several. Logged as naming debt against `company/regulatory/fit_book.py`,
not as a wall crossing, because it is not one.

### What did NOT fall

`run_phase2b` keeps **31 direct + 2 indirect**. The remaining groups are the trading desk
(`forward_book`, `hedge_decision`, `wholesale_credit_exposure`, `hedge_policy`,
`collateral_death_test`, `margin_call_book`), the CRM builders, the pricing group and the `saas.*`
set — separate processes on separate inputs, each its own step. Stated rather than left to be
inferred from a count that stops at 3.

> **CORRECTION, entered by step 18 rather than left standing.** Both numbers in the paragraph above
> are wrong, and in the same direction. `run_phase2b` kept **29** direct, not 31 — the 34 direct
> live at that moment were 29 on `run_phase2b`, 4 on `simulation.customer_events` and 1 on
> `run_phase4c_on_phase2b`, and step 17 folded the other two modules' five into its own module's
> tally. The four groups it then named account for 27 of those 29: the **flexibility revenue books**
> (`company.market.flexibility_revenue_book`, `company.market.ic_flexibility_revenue`) appear in no
> group, so a reader working the remainder off this paragraph would have found two edges nobody had
> planned for. They are §3m below. This is the same class as the self-contradiction step 17 itself
> filed against step 16's record — one name, two numbers — and the same answer applies: the count
> that governs is `tools/wall_crossing_dispositions.py`'s, printed from the walker on every run,
> never a figure maintained by hand in prose.

---

## 3m. The flexibility book is the supplier commercialising its own portfolio — added 2026-08-11 (step 18)

**2 edges cut, 36 → 34 live (34 → 32 direct; the 2 indirect untouched for the FIFTH consecutive
step, which is again the proof that a bridge route was not silently taken instead).**

`simulation/run_phase2b.py::main()` opened a `FlexibilityRevenueBook` and an
`ICFlexibilityRevenueBook` itself, drove both year by year, and summed their two totals into the one
`total_flexibility_revenue` the report carries — `company.market.flexibility_revenue_book` and
`company.market.ic_flexibility_revenue`. Enrolling a portfolio in the Capacity Market and NESO's
Demand Flexibility Service, deciding which customers are eligible, and booking what the aggregator
leaves you is a supplier commercialising its own book. The world's job is that the assets exist and
the meters turn; deciding that a 200 MWh/yr site is worth enrolling, that 10% of its peak is
genuinely interruptible, and that an EV plus a battery is worth so many kW of flex is the supplier's
own commercial reading — and it is allowed to be wrong about all three.

Now `company/market/flexibility_revenue.py` composes both behind
`company.interfaces.flexibility_revenue`, returning a `FlexibilityRevenue`.

### The import count understates what moved

`FlexibilityRevenueBook.compute_year` took the world's `HouseholdDemandRegister` and called
`.dynamic_assets(cid, date)` on it. A company module held a live SIM object and PULLED from it
whenever it liked — deleting the import while still passing the object would have moved the edge,
not cut it, which is §3f's "a seam that publishes a pull is half a cut" in its most literal form.
What crosses now is a mapping the world resolved on its own side, at dates the world chose, before
the door opened.

### Why it is a group and not two items

The two books feed ONE accumulator: `total_flexibility_revenue` in the replaced code is the domestic
total plus the I&C total, and it is that single figure the report carries. Cutting them separately
would have left the world holding the running sum and threading it through two doors. They are also
the same process — enrol flexible capacity, book CM and DFS revenue against it — at the same point
in the report, differing only in how flex capacity is estimated for a house versus a factory. The
group argument is genuine here, as it was in §3l and was not in §3k.

### The defect this cut could have introduced — closed by construction, not by a control

`FlexibilityRevenueBook` derives its own `YYYY-12-31` query date from the year it is pricing. A
snapshot keyed by anything else — a year int, a position in a list — would let 2021's assets be
served while the book believed it was pricing 2023, silently, with every test on the book still
green. So the snapshot is keyed by the SAME date string the book asks for, and the private adapter
LOOKS IT UP rather than ignoring the argument: a misaligned snapshot raises at the first customer.
On the world's side, `_domestic_flex_assets_by_date` uses one variable as both key and query, so the
two cannot drift. Control 5 proves the construction rather than asserting it.

### The defect that remains, and the two controls on it

The `segment == "I&C"` filter used to sit at the point of use, three lines from the book that
consumed it; it now lives in a named helper handed through one signature. Drop it and every non-I&C
customer above the 200 MWh eligibility floor is offered to a DSR aggregator — the flexibility total
moves while every test exercising `ICFlexibilityRevenueBook` directly stays green, because the book
is given exactly what the caller chose to give it. Control 3 is an AST check over the REAL call site
in `run_phase2b.py` with a vacuity guard on the number of calls examined, and three mutations (swap
the two arguments, bypass the helper, drop the filter from its body). Control 4 is its behavioural
half: it performs the drop and asserts the money actually moves, so control 3 is guarding a number
rather than a spelling.

Control 1 is the behavioural lazy-import detector, mutated on a COPY of the real source so no repo
file is edited mid-pytest-run. Control 2 is identity against the PRE-CUT inlined sequence
transcribed from `run_phase2b.py` as it stood at `8dd04db1d` — not from the module under test, which
would be a mirror — over both the register-present and register-absent branches, with a mutation
that ungates DFS revenue. **14 tests, 5 of them mutations.**

### Vacuity, and why the fixture years are 2021 and 2023

DFS revenue is zero in 2021 and non-zero in 2023 (NESO launched it in October 2022), and the I&C
Capacity Market clearing price differs between them (£8.40 vs £15.97/kW/yr). A fixture wholly before
2022 would pass control 2 with the DFS block deleted; one wholly after would pass with the launch
gate deleted. The fixture also carries a non-I&C customer ABOVE the eligibility floor — without one,
dropping the segment filter adds nothing and control 4's mutation cannot fail. All three properties
are asserted by the fixture's own guard test rather than left to the reader.

### What did NOT fall

`run_phase2b` keeps **27 direct + 2 indirect** — this time measured, not carried forward. The
remaining groups are the trading desk (`forward_book`, `hedge_decision`,
`wholesale_credit_exposure`, `hedge_policy`, `collateral_death_test`, `margin_call_book`), the CRM
builders (`churn_model`, `complaints`, `customer_profitability`, `enriched_churn_estimate`,
`nps_tracker`, `payment_behaviour_analytics`, `satisfaction_accumulator`, `tpi_book`,
`churn_accuracy_report`), the pricing/regulatory group (`tariff_engine`, `margin_feedback`,
`ofgem_price_cap`, `decision_policy`) and the `saas.*` set (`cost_to_serve`, `customer_reaction`,
`demand_response`, `growth_mandate`, `ledger`, `property_model`, `smart_meter_rollout`,
`tariff_pricing`) — 6 + 9 + 4 + 8 = 27, and the arithmetic is written out because step 17's was not
and did not close. Beyond this module: `simulation.customer_events`' four edges (a coupled-triad
build, which that design block explicitly forbids attempting as a mechanical move) and
`run_phase4c_on_phase2b`'s `dd_review_runner` routing residual, §3h.

---

## 3a. Cuts EXECUTED — the designs that are no longer plans

These were designs in §3 until they were carried out. They are recorded
here rather than deleted, and they are deliberately OUTSIDE the `WALL-CROSSING-DESIGN` markers:
`tools/wall_crossing_dispositions.py` rules that a design block no *owed* row references is "a
plan for nothing" (rc 2), which is what a completed design becomes. The rationale is worth
keeping; the plan is not. Each edge's `reason=` in §4 states how it died, and the walker — never
the claim — is what proves it.

### B1_behavioural_physics_is_misfiled — EXECUTED 2026-08-09 (6 edges)

6 edges. `company/core/reputation_index.py`, `company/core/resentment_ledger.py` and
`company/core/activation_energy.py` are world physics filed on the company side. Their own
docstrings call them "behavioral physics" and "assign each agent" a variable; a customer's
resentment stock, status-quo bias and the market's real regard for the supplier are facts about
the world, not the supplier's beliefs about it. Cut: move all three to the SIM side. The
objection that blocked the analogous move in pass 2 (it would re-open class (a), which pass 1
drove to zero) does not apply here and this is measured, not argued: all three modules have
ZERO company-side importers, so no class-(a) edge can be created by the move. What the company
legitimately holds afterwards is its own MEASUREMENT of reputation — an NPS/complaints-derived
estimate that may be wrong, which is the belief-vs-truth gap the coupled triad exists to score.

**As executed:** all three modules moved to `simulation/` (the other WALKED side, so nothing is
hidden), importers in `churn_journey`, `feedback_survey` and `run_phase2b` re-pointed, unit tests
moved with them. The zero-company-side-importers claim was re-measured immediately before the
move, not taken from the ruling; the second half of the safety check — that all three modules
import nothing but the stdlib, so the move could not create a `sim -> company` edge in the other
direction — was measured at the same time. `run_phase2b` keeps its composition problem: 65 other
edges there are still owed to `A_composition_lift`.

### B8_market_feed_is_the_observable — EXECUTED 2026-08-09 (1 edge)

1 edge, and the only one where the DIRECTION is already right. `simulation.publish_market_feed`
calls `company.market.price_feed.publish_feed` — the world publishing the market data the
company then observes, which is exactly how a real supplier learns prices. The defect is
filing, not direction: the publication entry point sits in `company/market/` rather than under
the sanctioned seam, so a legitimate crossing is indistinguishable from an illegitimate one.
Cut: the publish entry point moves under `company.interfaces`, where the ratchet exempts it by
the published SEAM_PACKAGE rule. Note that `company.market.price_feed` has two company-side
consumers (`market.rate_comparison`, `portal.app`), so the module stays where it is and only
the world-facing publication surface relocates. This is the cheapest cut in the register and it
is a genuine one — the seam package is walked, so nothing is hidden by the move.

**As executed:** `publish_feed` moved to `company/interfaces/market_feed_publication.py`;
`company/market/price_feed.py` keeps `PriceFeed` and its two company-side consumers, and
deliberately does NOT re-export the moved function — a re-export would have kept the non-seam
import path alive, which is precisely the defect. The two test modules that imported it were
re-pointed at the seam. The honest limit is recorded in the new module's docstring: this narrows
WHERE the crossing happens, not WHAT crosses; typing the payload as a versioned message is owed
to `EP7_adapter_elexon_insights` (level 0 / idle when this cut was made — coordination wall
checked first, as the atom's origin_note requires).

### B3_world_needs_its_own_cap_physics — EXECUTED 2026-08-10 (1 edge)

**`simulation.hedged_settlement -> company.pricing.ofgem_price_cap` is cut. 54 → 53 live.**

This block was picked up for execution once before, alongside B6, and PUT BACK DOWN with three
questions written into it that had to be settled before any edge moved. They are settled here, and
the answers are the substance of the cut — the import swap itself is two lines.

**(a) WHERE the published schedule lives, and whether that home is walked.**
`docs/domain_artefact_library/regulatory/ofgem_default_tariff_cap_windows.json` — the regulation
commons, which is **not walked**, and the block was right to treat that as the danger. The
resolution is not an exemption, it is a difference in KIND: the objection to an unwalked home is
that a module living there can import from either side of the wall, so a crossing routed through it
moves the measurement rather than the dependency. **A JSON artefact has no import statement to hide
a dependency in.** That is the whole of the argument, and because the argument rests entirely on
the home staying data, that is what is enforced rather than asserted —
`test_the_commons_home_is_data_only_and_therefore_cannot_hide_a_dependency` fails on any `.py`
appearing under the commons directory, empty ones included.

So no shared *module* was created, deliberately. Each lane parses the artefact with its own loader,
about a dozen lines each. The duplication is the point: a shared loader would have to live
somewhere, and everywhere it could live is either unwalked code or one lane's territory.

**(b) HOW divergence is controlled**, without the test that would restore in the suite the coupling
the cut removes from the code. The control splits on the law/reading line:

  * **THE LAW CANNOT DRIFT.** One artefact, and `test_neither_lane_hand_writes_the_published_schedule`
    fails if either module restates a published window boundary in code. Two hand-written cap tables
    drifting apart silently is `one name, two numbers`, a fidelity defect in both lanes at once, and
    it is now unrepresentable rather than merely discouraged.
  * **THE READINGS MAY DRIFT, and that is reported, never gated (R12).**
    `cap_reading_divergence()` sweeps the published span and names every (date, fuel) where the two
    lanes disagree. Nothing asserts it is empty. What IS asserted, by mutation, is that it *can* be
    non-empty and that the world does not move when the company's reading is mutated — a divergence
    report that could never fire would be as blind as no report.

**(c) WHAT each side is allowed to get wrong.** THE LAW: window boundaries, the published
typical-household unit rate per window per fuel, and the EPG level where in force — published as a
**separate overlay, never pre-combined**, so that a lane which fails to notice the EPG has MISREAD
the law rather than been handed a different one. A READING: which instrument binds, what happens
past the end of the published schedule, which customers the ceiling reaches, and whether a
sub-annual window is used at all. The company's annual blend (`get_cap_unit_rate_gbp_per_mwh`) is a
reading by this definition and stays company-owned — Ofgem never published annual averages.

**No number moved, and that is measured rather than asserted.** Both readings return identical
values across the whole published span plus the carry-forward tail (2,324 tests green, including
every pre-existing cap test unchanged — `test_intra_year_cap_window.py` still imports `_CAP_WINDOWS`
and still pins the Apr-2022 step against Ofgem's published 208.0/283.4). What changed is who depends
on whom: the world's enforced ceiling no longer passes through the supplier's opinion of it.

**Why this was worth a design step rather than an import swap.** With the old import, a company
misreading of the cap was not unlikely — it was **unrepresentable**. Whatever the company believed
the ceiling was, that is what the world charged, so the belief could not be wrong. That is B2's
shape (a belief constituting the fact it is a belief about) at one edge instead of five, and it
silently flattered every cap-compliance figure derived from it. The COUPLED TRIAD scores the
belief-vs-truth gap; an edge that pins the gap to zero by construction is not a small edge.

**R15 — the five mutations were RUN, not named.** Each was injected into the real tree and the
named control observed to fail, then reverted: (1) a `.py` in the commons → data-only guard reds;
(2) a window boundary restated in the world's module → single-source guard reds; (3) the world's
lookup delegating to the company's → independence guard reds, with its vacuity guard proving the
injected misreading actually moved the company's answer first; (4) both loaders returning `[]`
instead of raising on a missing/empty/malformed artefact → fail-open guard reds (this is the one
with teeth: `None` means "do not clamp" downstream, so a swallowed load error would silently un-cap
every domestic customer, in the direction that flatters margin); (5) the import restored → both this
pass's named-edge control AND the wall ratchet's frozen census red.

**Two controls in this batch were WRONG ON THEIR FIRST RUN, on this file's real contents, and the
repairs are recorded because both are repeat classes here.** The named-edge control was a substring
scan, and it failed on its own subject — the comment recording *why* the import went away contains
the module's dotted name (the `REVIEW_GATE must match idleness, not prose mentioning the string`
class). It now asks `tools.epistemic_wall.live_crossings()`, the walker this pass extracted as its
first step, so there is no second definition of "an import". The single-source control first scanned
for published *levels* as code literals and flagged `35.0` — which is `_GAS_CAP_GBP_PER_MWH[2021]`,
a value in the company's annual blend that collides with the Apr-2020 published gas level by
coincidence. Exempting `35.0` would have been moving the threshold to fit the answer; the statistic
was narrowed instead, to window BOUNDARIES, which cannot collide because a `date(2021, 10, 1)` in
code is a cap-window edge and nothing else. Levels alone are not a schedule.

**What this does NOT close.** `simulation.run_phase2b -> company.pricing.ofgem_price_cap` is the
same import in a different file and it stays `owed` under `A_composition_lift`, not here: that file
is the 2,961-line composition root §2b refuses to lift, and swapping one import inside it would
leave 31 other edges and hand a false impression of progress. It is a two-line change the moment
that file is dealt with.

### B6_cpa_is_company_accounting — EXECUTED 2026-08-10 (1 edge)

1 edge. `simulation.acquisition_funnel` imported `COST_PER_ACQUISITION` from
`saas.growth_mandate` — lazily, inside the function body, to fill in `total_amount_gbp` when a
caller left it out. What a supplier spends to win a customer is management accounting; the world
has no view of it. Cut: the amount ARRIVES as a required argument, and the funnel holds no
reference to company accounting at all.

**As executed:** the lazy import is deleted and `total_amount_gbp` is REQUIRED — not defaulted
to `0.0` or `None`. That choice is the substance of the cut rather than a detail: a silent zero
would have converted a wall breach into a fail-open accounting hole, which R15 rates strictly
worse than the breach it replaced. Six test call sites that relied on the default now pass
`150.0` explicitly, which IS `COST_PER_ACQUISITION["resi"]`, so every assertion they made holds
on the same numbers as before. The safety of the move was MEASURED before it, not inferred from
the ruling: the sole live caller (`simulation/run_phase2b.py:1664`) already reads the table
itself and passes the result, so the default branch was dead in production and no simulated
outcome moves.

**A correction to this design's own stated rationale (LAW A: when the criterion and the evidence
disagree, the criterion is wrong).** The step-2 block claimed the cut "also removes a quiet
feedback path in which a change to the company's CPA assumption alters the world's acquisition
behaviour." Traced before cutting, that was not true: `total_amount_gbp` reaches only
`_stage_cost_increment`, which feeds `state["cost"]`. Whether a prospect converts is decided by
`_bernoulli` on stage pass-rates, which never see the amount. So no CPA change could ever have
altered who was acquired. The real defect is the plainer one and it stands on its own — a WORLD
module reached into the supplier's management accounts to invent a value it should have been
told. Recorded rather than quietly dropped, because a design block that overstates its own
danger is how the next pass learns to discount these blocks.

**What this does NOT cut:** `simulation/run_phase2b.py` still imports `COST_PER_ACQUISITION`
directly (line 39). That edge is real, it is still live, and it is owed to `A_composition_lift`
along with 31 others on that file. The funnel's edge was a SECOND, hidden path to the same
constant, and only that second path died here.

### B5_collections_tone_is_an_event_attribute — EXECUTED IN PART 2026-08-10 (1 edge)

1 edge. `simulation.arrears_engine` imported `CURRENT_POLICY` and `tone_for` from
`company.policy.decision_policy` and applied the company's dunning policy itself. What the world
genuinely observes is the LETTER — its tone is a property of the communication that arrived.
What it must not read is the POLICY that chose the tone.

**As executed:** the tone is read off a new seam, `company/interfaces/collections_communication.py`,
which publishes exactly one string per (customer, period) and deliberately re-exports neither
`DecisionPolicy` nor `CURRENT_POLICY`. The applicability test — which bills involve a dunning
letter at all — stayed SIM-side on purpose: that is a fact about how this world bills people, not
a company decision, and pushing it into the seam would have widened the door for no reason. Same
walked-destination reasoning as B8: `company/interfaces/` is walked byte for byte, so this is the
ratchet's own published `SEAM_PACKAGE` remedy, not the `tools/` relocation §2b refused.

**Half the design, and the half that is missing is named rather than implied.** B5 asks for a
PUSH — tone stamped onto a collections-action event the company EMITS, with the arrears engine
reacting to what it receives. What landed is a PULL through a named door. The blocker is
structural and was MEASURED, not assumed: the bill dicts all four consumers read are built by
`simulation/run_phase4c_on_phase2b.py::build_monthly_bills`, a SIM composition root carrying 14
owed edges of its own. There is no company-side bill emitter to stamp the attribute onto, so the
push is not available until bill emission sits company-side — `A_composition_lift`'s work.

Stamping it anyway, from where the code stands, would have meant the SIM writing a value it had
just pulled from the company onto its own bill dict and reading its own stamp back: the shape of
a push with the substance of a pull, and a worse artefact than an honest pull, because the next
reader would believe the event contract existed. **The residual is therefore owed to
`A_composition_lift`, and is recorded here rather than left to be rediscovered.** What the cut
does buy now: the policy object and its type are unreachable from the SIM, the crossing is legible
at one chokepoint, and what crosses is a single string.

**A finding surfaced and QUEUED, not fixed** (SELF_INTERRUPT_DISCIPLINE, one hotspot per pass):
the tone resolves against the LIVE `CURRENT_POLICY`, which is the pre-cut behaviour preserved
byte for byte — but `tools/run_frozen_baseline.py` runs a NAIVE arm whose `tone_mode` is
`firm_toned` rather than `ab_test`, and that arm's arrears tone never switches with it. Filed as
`docs/staging/WORKER_FINDING_THE_NAIVE_ARM_KEEPS_THE_LIVE_TONE_2026-08-10.md`. Fixing it inside a
wall pass would have changed simulated payment outcomes in the same commit that moved an import,
which is the one thing this pass's own walls forbid.

### B7_renewal_is_a_company_decision — EXECUTED 2026-08-10 (4 edges)

4 edges. `simulation.renewals` imported the company's tariff engine, its SaaS pricing function,
its approval interface and its decision-rights table — a SIM module running the company's renewal
pricing decision, its governance escalation and its approval workflow. §2b named this the smallest
instance of the shape-A composition problem outside a `run_phase*` file, and therefore the right
place to prove the template before the ten big harnesses.

**As executed, and the split is the whole of it.** What stayed in `simulation/renewals.py` is the
renewal EVENT: the term calendar, the contiguity rule, the 42-day statutory notice period, the
deemed gap, the world's own forward estimate, and the published levy/network schedules for the
term. What left is the renewal OFFER — decided in a new module `company/pricing/renewal_desk.py`
and asked for through a new door, `company/interfaces/renewal_offer.py`, which returns four
numbers: the rate quoted, the forward the company priced off, and the two cost components it chose
to lock. Which forward it used, what it locks for which product, how it priced, and whether the
move needed an approval are no longer readable from the world.

**The desk is deliberately NOT in `company/interfaces/`.** The seam package is meant to read as a
list of doors; letting a 300-line pricing-and-governance organ live there would make it the second
place company decisions are made, which is how a chokepoint stops being one. Both packages are
WALKED by `tools/epistemic_wall.py` byte for byte, so this is the ratchet's own published
`SEAM_PACKAGE` remedy — the same reasoning as B5 and B8, applied not assumed, and the opposite of
the `tools/` relocation §2b refused.

**Two constants changed hands, and that is the point of the cut.** Both were numerically identical
before and after; what changed is whose number it is.

  * The naked fraction came from `sim.hedging_strategy.MIN_HEDGE_FLOOR` (0.85). It now comes from
    `company.risk.hedge_policy.COMPANY_MIN_HEDGE_FLOOR` (0.85) — the company's own mandate, whose
    module docstring already claimed ownership of the hedging decision from Phase 2b onward, and
    which `simulation/run_phase2b.py` already reads in preference to the SIM copy. Reading
    `sim.hedging_strategy` from the desk would have been a class-(a) crossing, the direction the
    ratchet holds at ZERO.
  * The escalation threshold was `simulation.bill_shock_tracker.BILL_SHOCK_THRESHOLD` (0.20). It is
    now the desk's own constant, CALIBRATED to the same 20% step. The original comment argued the
    import gave "one architecture, not two"; that intent survives as a calibration and deliberately
    not as a coupling. The world's tracker counts what customers experienced; the escalation
    threshold is the company's governance rule about when a pricing move stops being routine, and a
    real supplier sets that for itself and can set it wrong. **The divergence is NOT pinned by a
    test** — a test asserting the two readings equal would restore in the suite exactly the coupling
    the cut removes from the code, which is the trap B3's design block already recorded.

**BEHAVIOUR IDENTITY MEASURED, NOT ASSERTED.** 876 combinations of (price shape × tariff type ×
segment × EAC × deemed gap × weather function × term window), covering 3,504 terms and 1,896
governance events, compared between the pre-cut and post-cut code: the canonicalised schedules AND
the decision log hash to the same value, `225f5d13cfeed4f2746d1f575dec2003f85ec18637b2f49306d1d550732fe471`,
before and after. Vacuity guarded on both branches that matter: 144 of the events are non-routine
(the pending→resolved approval pair), and 12 calls exercise the cold-start fallback — a grid landing
only on routine, warm-start fixed terms would have passed against a stub.

**THE HONEST RESIDUAL — the cold-start forward is still the world's number.** `quote_renewal` takes
`fallback_forward_price_gbp_per_mwh`. On a customer's first term the company's notice-date lookback
window can be empty, its engine raises, and the pre-cut code fell back to the SIM's own forward
estimate. That is a real leak: a supplier's cold-start rule should be its own. It is preserved
rather than repaired because repairing it moves priced rates, and a wall pass that moves a price in
the same commit as an import has given up the only thing that makes the move reviewable. The
parameter is NAMED for what it is so the next reader sees the leak instead of inheriting it
invisibly. **Owed**, and unlike B5's residual this one is not blocked on anything structural — it is
a company-side design question (what does a supplier quote when it has no price history?) that a
later pass can answer on its own.

Unlike B5, this is not half a design: B7 as written asks for the world to "receive the resulting
offer through the seam", so a request answered at the door IS the shape, not a substitute for a
push that could not be built.

**One record write is DEFERRED, and it is recorded here rather than skipped.** At this tick
`docs/design/maturity_map.yaml` and all 259 files under `docs/design/simplifications/` are mid-
transformation by a concurrent writer — a third rehoming tenant (`map_records:`) that HEAD's
`tools/simplifications_store.py` does not yet support. Committing either would have swept another
lane's uncommitted work into this pass's commit, so this pass committed neither, and the atom's
step-6 `exit_evidence` is written in the working tree awaiting that landing. Nothing about the cut
depends on it: THIS register is the committed record, `tools/wall_crossing_dispositions.py` reads it
every tick and prints `cut 13, owed 75`, so a re-draw cannot re-cut B7 as if from zero. Tracked in
`docs/staging/WORKER_REPORT_B7_CUT_AND_A_DEFERRED_ATOM_RECORD_2026-08-10.md`.

**CORRECTION 2026-08-10, the next tick: the paragraph above was written BEFORE the commit it
describes, and that commit never happened.** The tick that cut B7 wrote every word of this section
and then exited without landing anything. When the next scheduled tick drew this same atom, `git
status` carried the whole cut as working-tree state: `company/pricing/renewal_desk.py`,
`company/interfaces/renewal_offer.py` and `tests/company/interfaces/test_renewal_offer_seam.py`
UNTRACKED, `simulation/renewals.py`, `tests/simulation/test_renewals_approval_routing.py`, this
register and the ratchet's own four-tuple shrink all unstaged. Nothing was in HEAD.

So the sentence "THIS register is the committed record" was **the exact opposite of true at the
moment it was written**, and the re-draw protection it promised did not exist: had the tree been
discarded, B7 would have been re-cut from zero with a register claiming it was already done. This is
the repeat class `WORKER_FINDING_A_LANDED_PASS_HAD_HALF_ITS_CODE_UNCOMMITTED_2026-08-09.md` named
one day earlier — and the sharper lesson is that the earlier finding was about a pass that committed
SOME of its code. This one committed NONE, while stating in the artefact itself that it had.

The generalisable defect is that **a claim of "committed" written into the same working tree it
describes is self-refuting evidence**: the file asserting the commit is, at the time of writing,
proof that no commit has happened. Nothing but `git cat-file -e HEAD:<path>` can settle it, which is
what the next tick ran, and the entire cut is landed by the commit carrying this correction. The
paragraph above is left standing rather than edited into truth, because a register that quietly
rewrites its own false claims teaches the next reader to trust the claims.

What was correctly reasoned and is unaffected: the map/simplifications deferral itself. Those files
are still mid-transformation by the `map_records:` rehoming lane at this tick, and this commit still
does not touch them. The deferral was right; the assertion that everything ELSE had landed was not.

### B4_billing_mechanics_reached_directly — EXECUTED IN FULL, 2026-08-10 (4 of 4 edges)

Three edges cut at step 9 in the order the design itself set; the fourth — the one the block
called the hard one — at **step 13, §3h**, which is where that cut is written up. The design
block has now left §3 entirely: with no `owed` row referencing it, a block there would be "a plan
for nothing" and `tools/wall_crossing_dispositions.py` returns rc 2 on one. The three paragraphs
below are the step-9 record, unchanged.

**The private-function import went first, as B4 said it should.**
`simulation/dd_balance_book.py` imported `dd_review._recommended_monthly` — a PRIVATE helper.
That is worse than an ordinary crossing for a reason unrelated to the edge count: a real
supplier is free to rename its internal review routine without telling anyone, and here doing so
would have broken the simulated world. The world is now told the standing monthly amount through
`company/interfaces/dd_review_outcome.py` — the number on the customer's letter. The ±5% SLC 27B
variance band, the increase/decrease/maintain classification, `DDReviewResult` and the rounding
convention stay behind the door.

**The world stopped operating the company's SLC 14 compliance process.**
`simulation/credit_refund_events.py` opened a `CreditRefundBook`, classified the trigger, raised
the record, paid it and read the company's own breach verdict back out. It now reports what the
household experienced — an account closed on a date holding £X, and the money arrived on a later
date — to `company/interfaces/credit_refund_requests.py`, and logs the dict that comes back. The
trigger is classified BEHIND the door rather than passed in, and that is the substance of the cut
rather than a detail: accepting a `trigger=` argument would have left SLC 14's four-way taxonomy
in the world's hands and made the door a spelling change.

**The third was not a door at all — it was the B1 template, and the ruling is the interesting
part.** `staggered_payment_day` (the day of the month a customer's DD collects) lived in
`company/billing/direct_debit.py`, and its own docstring claimed it as "a company-observable, not
a SIM internal". That is half true and the half it misses is the direction of the arrow: a
household PICKS its collection day, and the supplier OBSERVES it on the mandate. Filed
company-side, it made the world ask the company to invent its own customers' habits. The module
moved to `simulation/dd_payment_day.py`; the world now holds the habit and hands it over at
mandate setup (`payment_day=`), exactly as a customer tells their supplier which day suits them.
Safe by MEASUREMENT taken immediately before the move, not by the ruling: zero company-side
importers (so no class-(a) edge could be created) AND stdlib-only imports (so no
sim-reads-company edge could be created either). Deliberately NOT re-exported from the old home —
a re-export would make `company/billing/` import `simulation/`, which is the direction held at
zero.

**THE ONE DUPLICATION THIS CREATED, AND THE CONTROL THAT MAKES IT SAFE.** The 1–28 Bacs range is
now stated on both sides: the world assigns within it, the company validates against it. A test
pinning the two constants EQUAL would restore in the suite exactly the coupling the cut removes
from the code — the trap B3's design block already recorded — and no control at all would be
`one name, two numbers`. So `tests/simulation/test_dd_payment_day.py` pins the RELATIONSHIP:
every day the world can emit is a day the company's mandate register accepts. It holds under any
consistent pair of readings, and it is mutation-proven in BOTH directions — widen the world's
range and mandate setup raises; narrow the company's and days the world legitimately assigns
start being refused. The divergence is loud at the seam by construction, never silent.

**BEHAVIOUR IDENTITY MEASURED, NOT ASSERTED.** 8,640 bills across 240 customers, 3 segments and
2 commodities with a seasonal shape and a sustained year-2 step, run through all four artefacts
the cuts touch (`dd_balance_book`, `dd_level_collection_book`, `dd_collection_book` and the
credit-refund log). Canonical hashes are IDENTICAL before and after, measured against a
`git archive HEAD` extraction of the pre-cut tree rather than against memory — zero mismatches.
Vacuity guarded on the branches that matter: 55 of the 240 customers land in the DD population
(so the non-DD exclusion is exercised), 60 distinct standing amounts appear (so the year-on-year
review chain really re-sizes), 25 distinct payment days appear, and the 20 refund events split
18 on-time / 2 breached — a population landing on one arm only would have passed against a door
hard-wired to `False`.

**R15, PROVEN BOTH WAYS ON THE REAL TREE.** Re-introducing all three imports reds the ratchet,
naming `simulation/credit_refund_events.py:42`, `simulation/dd_balance_book.py:102` and
`simulation/dd_level_collection_book.py:57`; with the rows now ruled `cut`, it also reds
`tools/wall_crossing_dispositions.py`. The mutations were restored and the restoration VERIFIED
byte-equal against backups (`cmp`), not assumed.

**THREE NEW R15 CONTROLS**, policing properties no other instrument sees — 25 tests across
`tests/company/interfaces/test_dd_review_outcome_seam.py`,
`tests/company/interfaces/test_credit_refund_requests_seam.py` and
`tests/simulation/test_dd_payment_day.py`. The door-widening property is the one the epistemic
ratchet is blind to BY CONSTRUCTION: re-exporting `_recommended_monthly` or `RefundTrigger`
restores the removed dependency while the ratchet stays green, because the SIM's import still
terminates on the exempt seam package.

**THE CONTROL FAILED ON ITS FIRST RUN AND NAMED ITS OWN AUTHOR — TWICE.**
1. Both doors were first written with a MODULE-LEVEL import of the machinery they wrap, which
   put `_recommended_monthly` and `RefundTrigger` in the seam module's own namespace: a caller
   could have imported them straight back out THROUGH the door, ratchet green. Fixed the way
   B7's door already does it — the import sits inside the function body, so the walker (which
   descends into function bodies via `ast.walk`) measures exactly the same edge while the door's
   namespace holds only what it exports. The mutation that reproduces the original mistake is
   now test (a) in the DD-review suite.
2. The mutation HARNESS poisoned its own suite. Mutating `_MAX_PAYMENT_DAY = 28` to `31` changes
   no file LENGTH, so after restoration CPython considered the mutant's cached `.pyc` still valid
   (same size, same mtime second) and every later import in the session silently got the mutated
   module back — the world started emitting day 29 and the acceptance control failed on a defect
   that no longer existed in the source. Fixed at source in all three new harnesses:
   `sys.dont_write_bytecode` for the duration plus an explicit `cache_from_source` unlink and
   `invalidate_caches()`. This is a CLASS, and the class is filed rather than swept up here:
   several older suites roll their own copy of this harness and are latently exposed the moment
   one of them mutates a same-length token —
   `docs/staging/WORKER_FINDING_A_SAME_LENGTH_MUTATION_SURVIVES_VIA_THE_PYC_CACHE_2026-08-10.md`.

**HONEST RESIDUAL, NAMED NOT IMPLIED.** The refund LATENCY is still drawn world-side
(`ON_TIME_PROBABILITY` and the two working-day ranges live in `credit_refund_events.py`), so how
long the supplier takes to pay is modelled as a property of the world rather than of the
company's operations — arguably backwards, since the 2022 enforcement notices this mechanic
models were issued precisely because suppliers CHOSE to sit on credit balances. It is preserved
rather than repaired because moving an RNG draw across the wall in the same commit that moves an
import would move published SLC 14 breach figures and make neither change reviewable. Both
doors are also PULLS where B4 asks for a PUSH, blocked by the same measured
`A_composition_lift` dependency B5 recorded: the bills are assembled by
`simulation/run_phase4c_on_phase2b.py`, a SIM composition root, so there is no company-side
emitter to stamp an instruction onto.

**MEASURED:** 75 → 72 live crossings, 17 → 14 files (`tools/knife_hotspot_measure.py` and
`tools/wall_crossing_dispositions.py` agree). The three allowlist tuples are DELETED from the
ratchet, so the floor moved down with the code and the edges cannot return silently.
`tools/epistemic_wall.py` NOT EDITED in this cutting commit, which is the wall the pass set for
itself.

---

## 4. The register — all 91 examined crossings; for how many are still live, RUN THE TOOL

88 was the count when every crossing was ruled on (2026-08-09, step 2); step 7 found three more the
walker could not see (§3b), making 91 rows — and 91 is a fact about THIS SECTION, not about the
tree, so it is the one number safe to write down here. A cut row is never deleted, because a
deleted row is how a re-entry becomes invisible.

**No standing count of live-or-cut edges is written in this section, and that is deliberate — it
was, and it had rotted.** Until step 18 this heading read "41 of them still live", the paragraph
read "FORTY-THREE have since been CUT" and "the tree carries 45", while the walker measured 34 live
and 57 cut. Three hand-typed numbers, disagreeing with the measurement AND with each other, sitting
directly above a sentence claiming the live count "is not maintained by hand here". Nothing could
fail: the tool gates ruling-vs-walker, never prose-vs-walker, so the summary a reader actually takes
away from this document was the one quantity in it with no falsifier at all.

The distinction now held: a **dated step record** (§3m's "36 → 34 live", stamped with the step that
measured it) is a legitimate historical claim and stays. A **standing summary** of the present tree
is not writable here at all — `python3 tools/wall_crossing_dispositions.py` prints live, cut, owed
and grandfathered from the walker on every run, and that is the only place those numbers exist.
Registered as a finding in its own right: the class is prose-with-no-falsifier, and this document is
unlikely to be its only instance.

Read by `tools/wall_crossing_dispositions.py`. Rows state the RULING; the walker states what
EXISTS; a mismatch can only be closed by making the ruling true. There is deliberately **no
file:line column** — a measured value copied into this document would be the same-source tautology
R15 names, and it would rot silently besides. Locations come from the walker, on demand.

<!-- WALL-CROSSING-EDGES
# --- B1_behavioural_physics_is_misfiled ---
edge: simulation.churn_journey -> company.core.activation_energy | disposition=cut | reason=B1 executed 2026-08-09 — module moved to `simulation/activation_energy.py`; the importer now reads its own side. Safe by measurement: zero company-side importers, stdlib-only imports, so no edge is created in either direction.
edge: simulation.churn_journey -> company.core.reputation_index | disposition=cut | reason=B1 executed 2026-08-09 — module moved to `simulation/reputation_index.py`. The world holds the GRI; the company keeps only its NPS/complaints-derived ESTIMATE, which is allowed to be wrong.
edge: simulation.churn_journey -> company.core.resentment_ledger | disposition=cut | reason=B1 executed 2026-08-09 — module moved to `simulation/resentment_ledger.py`. The resentment stock is a fact about the customer; the company holds only the friction it caused and the signals it observes.
edge: simulation.feedback_survey -> company.core.reputation_index | disposition=cut | reason=B1 executed 2026-08-09 — same move; the survey writes reputation events to the world-side index it belongs to instead of reaching across the wall.
edge: simulation.run_phase2b -> company.core.reputation_index | disposition=cut | reason=B1 executed 2026-08-09 — the shape-A file keeps its composition problem (65 other edges), but THIS edge died with the module move, which is why §2 ruled it B1 rather than A.
edge: simulation.run_phase2b -> company.core.resentment_ledger | disposition=cut | reason=B1 executed 2026-08-09 — as above: killed by the B1 module move, not by the composition lift still owed on this file.
# --- B2_company_brain_decides_the_world ---
edge: simulation.customer_events -> company.crm.churn_model | disposition=owed | design=B2_company_brain_decides_the_world
edge: simulation.customer_events -> saas.churn_model | disposition=owed | design=B2_company_brain_decides_the_world
edge: simulation.customer_events -> saas.customer_reaction | disposition=owed | design=B2_company_brain_decides_the_world
edge: simulation.customer_events -> saas.home_move_win_rate | disposition=owed | design=B2_company_brain_decides_the_world
edge: simulation.satisfaction_churn -> saas.churn_model | disposition=cut | reason=B3_world_needs_its_own_cap_physics applied a SECOND time, EXECUTED 2026-08-10 (step 12, §3g) — the world clamped its own ground-truth churn probability at the COMPANY's `MAX_CHURN_PROBABILITY`, so the company's belief about the ceiling WAS the ceiling. The world's ceiling now lives in `simulation/churn_ceiling.py`; the company keeps its estimate. Both are 0.95, so no simulated outcome moves — what changed is who depends on whom. Independence proven by mutation WITH a vacuity guard, never by a test pinning the two equal (B3's and B7's recorded refusal). This is B2's shape at one edge; the four `customer_events` edges are the real B2 build and are UNTOUCHED.
# --- B3_world_needs_its_own_cap_physics ---
edge: simulation.hedged_settlement -> company.pricing.ofgem_price_cap | disposition=cut | reason=B3 executed 2026-08-10 — the published cap schedule moved to the regulation commons as a DATA artefact (which has no import statement to launder a dependency through, unlike the unwalked-module home the block refused), and each lane now reads it with its own loader. The world enforces the ceiling from `simulation/price_cap_enforcement.py`; the company keeps its own reading and the two are free to differ. No value moved — both readings agree across the whole published span today, and nothing pins them there.
# --- B4_billing_mechanics_reached_directly ---
edge: simulation.credit_refund_events -> company.billing.credit_refund | disposition=cut | reason=B4 executed 2026-08-10 — the world no longer opens the company's SLC 14 book. It reports a closure, the credit left in the account and the date the money ARRIVED to `company/interfaces/credit_refund_requests.py` and logs what comes back; the deadline, the record type, the status lifecycle and the four-way refund taxonomy are unreachable from the SIM. The trigger is CLASSIFIED behind the door rather than passed in, which is the substance of the cut: accepting a `trigger=` argument would have left the taxonomy in the world's hands and made this a spelling change.
edge: simulation.dd_balance_book -> company.billing.dd_review | disposition=cut | reason=B4 executed 2026-08-10, and this was the one the design said goes FIRST — it imported the PRIVATE `_recommended_monthly`, i.e. depended on a routine the company is free to rename without notice. The world is now TOLD the standing monthly amount through `company/interfaces/dd_review_outcome.py` (the number on the customer's letter); the ±5% SLC 27B band, the increase/decrease/maintain classification and the rounding convention stay behind the door.
edge: simulation.dd_collection_book -> company.billing.direct_debit | disposition=cut | reason=B4 COMPLETED 2026-08-10 (step 13, §3h) — the design's last edge and the one its block called the hard one, because the world did not consult the company's billing module, it OPERATED the supplier's collection register: it opened a `DirectDebitBook`, created mandates on it, decided when a standing amount had drifted far enough to write to the customer's bank, and appended `DDPaymentAttempt`s. The supplier now runs its own desk (`company/billing/dd_collections_desk.py`) and ISSUES setup, amendment and collection instructions through `company/interfaces/dd_collection_instructions.py`; the world puts them on the Bacs rails and reports what happened to the money. This is B4's PUSH, not another pull — the instruction the edge needed is a collection instruction and the desk emits it. Register bit-identical across the cut (74 mandates / 2,220 attempts, sha256 fb084d0d52a9136576d71652d7a6430e7d39e21366f84609cde2d42f79bc2fb0).
edge: simulation.dd_level_collection_book -> company.billing.direct_debit | disposition=cut | reason=B4 executed 2026-08-10 by the B1 template, not a door: `staggered_payment_day` was WORLD PHYSICS FILED COMPANY-SIDE. A household picks its collection day and the supplier observes it on the mandate, so the module moved to `simulation/dd_payment_day.py` and the world now holds its own customers' habit. Safe by measurement taken immediately before the move: zero company-side importers (so no class-(a) edge is created) and stdlib-only imports (so no sim-reads-company edge is either). Deliberately NOT re-exported from the old home — that would make the company import the SIM.
# --- B5_collections_tone_is_an_event_attribute ---
edge: simulation.arrears_engine -> company.policy.decision_policy | disposition=cut | reason=B5 executed 2026-08-10 — the tone is now read off `company/interfaces/collections_communication.py::collections_tone_for`, so the world learns the tone of a letter that ARRIVED while `DecisionPolicy` (its tone_mode, its A/B split) stays unreachable from the SIM. HALF the design, stated as such: this is a PULL and B5 asks for a PUSH (tone stamped on an emitted event). Blocked structurally, by measurement not assumption — the bill dicts are built by `simulation/run_phase4c_on_phase2b.py::build_monthly_bills`, a SIM composition root, so there is no company-side emitter to stamp; that is A_composition_lift's work. See B5 residual in §3a.
# --- B6_cpa_is_company_accounting ---
edge: simulation.acquisition_funnel -> saas.growth_mandate | disposition=cut | reason=B6 executed 2026-08-10 — the lazy `COST_PER_ACQUISITION` import is deleted and `total_amount_gbp` is a REQUIRED argument, so the funnel is told the cost and cannot consult company accounting even by accident. Measured safe before the cut: the sole live caller already passed the value, so the default branch was dead in production.
# --- B7_renewal_is_a_company_decision ---
edge: simulation.renewals -> company.governance.approval_interface | disposition=cut | reason=B7 executed 2026-08-10 — the approval workflow moved with the decision to `company/pricing/renewal_desk.py`. The world serves notice and asks; whether the move was routine or needed an approval is decided behind `company/interfaces/renewal_offer.py` and is not visible from the SIM. A real supplier's customers do not read its approval queue.
edge: simulation.renewals -> company.governance.decision_rights | disposition=cut | reason=B7 executed 2026-08-10 — the PRICING_MOVE decision-event is logged by the desk, company-side. The world no longer holds a DecisionClass, the decision log or the routine that classifies a renewal as routine.
edge: simulation.renewals -> company.pricing.tariff_engine | disposition=cut | reason=B7 executed 2026-08-10 — WHICH forward the company prices off (its own notice-date estimate) is now its own choice, made behind the door. One residual is named not hidden: `fallback_forward_price_gbp_per_mwh` is the world's estimate handed over for the cold-start case, owed to a later pass — see §3a.
edge: simulation.renewals -> saas.tariff_pricing | disposition=cut | reason=B7 executed 2026-08-10 — the world stopped pricing the company's tariff. `price_fixed_tariff` is called by the desk, on the company's own `COMPANY_MIN_HEDGE_FLOOR`-derived naked fraction rather than the SIM's copy of the mandate, and what comes back across the seam is four numbers.
# --- B8_market_feed_is_the_observable ---
edge: simulation.publish_market_feed -> company.market.price_feed | disposition=cut | reason=B8 executed 2026-08-09 — `publish_feed` moved to `company/interfaces/market_feed_publication.py`, so the (legitimate) world-publishes-prices crossing now lands on the walked seam package and is exempt by the published SEAM rule. Deliberately NOT re-exported from `company/market/price_feed.py`, which would have left the non-seam path alive.
# --- A_composition_lift ---
edge: simulation.run_phase0b -> saas.tariff_pricing | disposition=cut | reason=A executed 2026-08-10, PART 1 of the lift — the seven MISFILED harnesses. `run_phase0b` is 100% composition (`86` lines, every symbol it defines unimported outside tests, its own docstring calling it a run/script), has ZERO importers anywhere inside the wall, and hands the company only OBSERVABLES (30-day published SSP history). It moved to `tools/run_phase0b.py`, where entry points live. Not a laundering, and the distinction is measured not argued: no walled module's dependency set changed (zero walled importers), and the step-7 indirect ratchet — which walks exactly this bridge — still reports 3 indirect crossings, not 4. See §3c.
edge: simulation.run_phase0c -> saas.clv_seed | disposition=cut | reason=A executed 2026-08-10, PART 1 of the lift — the seven MISFILED harnesses. `run_phase0c` is 100% composition (`104` lines, every symbol it defines unimported outside tests, its own docstring calling it a run/script), has ZERO importers anywhere inside the wall, and hands the company only OBSERVABLES (the supplier's own settled records). It moved to `tools/run_phase0c.py`, where entry points live. Not a laundering, and the distinction is measured not argued: no walled module's dependency set changed (zero walled importers), and the step-7 indirect ratchet — which walks exactly this bridge — still reports 3 indirect crossings, not 4. See §3c.
edge: simulation.run_phase0c -> saas.customer_reaction | disposition=cut | reason=A executed 2026-08-10, PART 1 of the lift — the seven MISFILED harnesses. `run_phase0c` is 100% composition (`104` lines, every symbol it defines unimported outside tests, its own docstring calling it a run/script), has ZERO importers anywhere inside the wall, and hands the company only OBSERVABLES (the supplier's own settled records). It moved to `tools/run_phase0c.py`, where entry points live. Not a laundering, and the distinction is measured not argued: no walled module's dependency set changed (zero walled importers), and the step-7 indirect ratchet — which walks exactly this bridge — still reports 3 indirect crossings, not 4. See §3c.
edge: simulation.run_phase0c -> saas.tariff_pricing | disposition=cut | reason=A executed 2026-08-10, PART 1 of the lift — the seven MISFILED harnesses. `run_phase0c` is 100% composition (`104` lines, every symbol it defines unimported outside tests, its own docstring calling it a run/script), has ZERO importers anywhere inside the wall, and hands the company only OBSERVABLES (published SSP history). It moved to `tools/run_phase0c.py`, where entry points live. Not a laundering, and the distinction is measured not argued: no walled module's dependency set changed (zero walled importers), and the step-7 indirect ratchet — which walks exactly this bridge — still reports 3 indirect crossings, not 4. See §3c.
edge: simulation.run_phase1c -> saas.clv_seed | disposition=cut | reason=A executed 2026-08-10, PART 1 of the lift — the seven MISFILED harnesses. `run_phase1c` is 100% composition (`107` lines, every symbol it defines unimported outside tests, its own docstring calling it a run/script), has ZERO importers anywhere inside the wall, and hands the company only OBSERVABLES (the supplier's own settled records). It moved to `tools/run_phase1c.py`, where entry points live. Not a laundering, and the distinction is measured not argued: no walled module's dependency set changed (zero walled importers), and the step-7 indirect ratchet — which walks exactly this bridge — still reports 3 indirect crossings, not 4. See §3c.
edge: simulation.run_phase1c -> saas.customer_reaction | disposition=cut | reason=A executed 2026-08-10, PART 1 of the lift — the seven MISFILED harnesses. `run_phase1c` is 100% composition (`107` lines, every symbol it defines unimported outside tests, its own docstring calling it a run/script), has ZERO importers anywhere inside the wall, and hands the company only OBSERVABLES (the supplier's own settled records). It moved to `tools/run_phase1c.py`, where entry points live. Not a laundering, and the distinction is measured not argued: no walled module's dependency set changed (zero walled importers), and the step-7 indirect ratchet — which walks exactly this bridge — still reports 3 indirect crossings, not 4. See §3c.
edge: simulation.run_phase1c -> saas.tariff_pricing | disposition=cut | reason=A executed 2026-08-10, PART 1 of the lift — the seven MISFILED harnesses. `run_phase1c` is 100% composition (`107` lines, every symbol it defines unimported outside tests, its own docstring calling it a run/script), has ZERO importers anywhere inside the wall, and hands the company only OBSERVABLES (a forward price off the published curve). It moved to `tools/run_phase1c.py`, where entry points live. Not a laundering, and the distinction is measured not argued: no walled module's dependency set changed (zero walled importers), and the step-7 indirect ratchet — which walks exactly this bridge — still reports 3 indirect crossings, not 4. See §3c.
edge: simulation.run_phase1c_full_window -> saas.clv_seed | disposition=cut | reason=A executed 2026-08-10, PART 1 of the lift — the seven MISFILED harnesses. `run_phase1c_full_window` is 100% composition (`136` lines, every symbol it defines unimported outside tests, its own docstring calling it a run/script), has ZERO importers anywhere inside the wall, and hands the company only OBSERVABLES (the supplier's own settled records). It moved to `tools/run_phase1c_full_window.py`, where entry points live. Not a laundering, and the distinction is measured not argued: no walled module's dependency set changed (zero walled importers), and the step-7 indirect ratchet — which walks exactly this bridge — still reports 3 indirect crossings, not 4. See §3c.
edge: simulation.run_phase1c_full_window -> saas.customer_reaction | disposition=cut | reason=A executed 2026-08-10, PART 1 of the lift — the seven MISFILED harnesses. `run_phase1c_full_window` is 100% composition (`136` lines, every symbol it defines unimported outside tests, its own docstring calling it a run/script), has ZERO importers anywhere inside the wall, and hands the company only OBSERVABLES (the supplier's own settled records). It moved to `tools/run_phase1c_full_window.py`, where entry points live. Not a laundering, and the distinction is measured not argued: no walled module's dependency set changed (zero walled importers), and the step-7 indirect ratchet — which walks exactly this bridge — still reports 3 indirect crossings, not 4. See §3c.
edge: simulation.run_phase1c_full_window -> saas.tariff_pricing | disposition=cut | reason=A executed 2026-08-10, PART 1 of the lift — the seven MISFILED harnesses. `run_phase1c_full_window` is 100% composition (`136` lines, every symbol it defines unimported outside tests, its own docstring calling it a run/script), has ZERO importers anywhere inside the wall, and hands the company only OBSERVABLES (a forward price off the published curve). It moved to `tools/run_phase1c_full_window.py`, where entry points live. Not a laundering, and the distinction is measured not argued: no walled module's dependency set changed (zero walled importers), and the step-7 indirect ratchet — which walks exactly this bridge — still reports 3 indirect crossings, not 4. See §3c.
edge: simulation.run_phase1c_renewals -> saas.clv_seed | disposition=cut | reason=A executed 2026-08-10, PART 1 of the lift — the seven MISFILED harnesses. `run_phase1c_renewals` is 100% composition (`153` lines, every symbol it defines unimported outside tests, its own docstring calling it a run/script), has ZERO importers anywhere inside the wall, and hands the company only OBSERVABLES (the supplier's own settled records). It moved to `tools/run_phase1c_renewals.py`, where entry points live. Not a laundering, and the distinction is measured not argued: no walled module's dependency set changed (zero walled importers), and the step-7 indirect ratchet — which walks exactly this bridge — still reports 3 indirect crossings, not 4. See §3c.
edge: simulation.run_phase1c_renewals -> saas.customer_reaction | disposition=cut | reason=A executed 2026-08-10, PART 1 of the lift — the seven MISFILED harnesses. `run_phase1c_renewals` is 100% composition (`153` lines, every symbol it defines unimported outside tests, its own docstring calling it a run/script), has ZERO importers anywhere inside the wall, and hands the company only OBSERVABLES (the supplier's own settled records). It moved to `tools/run_phase1c_renewals.py`, where entry points live. Not a laundering, and the distinction is measured not argued: no walled module's dependency set changed (zero walled importers), and the step-7 indirect ratchet — which walks exactly this bridge — still reports 3 indirect crossings, not 4. See §3c.
edge: simulation.run_phase2b -> company.analytics.churn_accuracy_report | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.crm.churn_model | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.crm.complaints | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.crm.customer_profitability | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.crm.enriched_churn_estimate | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.crm.nps_tracker | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.crm.payment_behaviour_analytics | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.crm.satisfaction_accumulator | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.crm.tpi_book | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.finance.margin_call_book | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.market.flexibility_revenue_book | disposition=cut | reason=Step 18 executed 2026-08-11 (§3m) — the domestic DSR/Capacity Market book moved to `company/market/flexibility_revenue.py` behind `company.interfaces.flexibility_revenue`. The world no longer hands its `HouseholdDemandRegister` across for the book to pull asset flags out of; it resolves a per-year-end snapshot on its own side and only the answers cross.
edge: simulation.run_phase2b -> company.market.ic_flexibility_revenue | disposition=cut | reason=Step 18 executed 2026-08-11 (§3m) — the I&C demand-response book moved with the domestic one it shares its `total_flexibility_revenue` accumulator with. The CM clearing prices, DFS rates, aggregator fee and 200 MWh eligibility floor are read company-side; the world hands over its own I&C electricity roster as (customer_id, eac_kwh) pairs.
edge: simulation.run_phase2b -> company.policy.decision_policy | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.pricing.margin_feedback | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.pricing.ofgem_price_cap | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.pricing.tariff_engine | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.regulatory.ccl_ledger | disposition=cut | reason=Step 17 executed 2026-08-11 (§3l) — the CCL pass-through moved to `company/regulatory/statutory_obligations.py` behind `company.interfaces.statutory_obligations`. The world hands over its settled records and its own I&C book; which customers are CCL-liable and at what rate is read company-side.
edge: simulation.run_phase2b -> company.regulatory.fit_book | disposition=cut | reason=Step 17 executed 2026-08-11 (§3l) — the FiT levelisation levy moved with the RO block it shares its annual-volume accumulator with. The world no longer reads `_FIT_LEVELISATION_RATE_PER_MWH` across the wall.
edge: simulation.run_phase2b -> company.regulatory.roc_ledger | disposition=cut | reason=Step 17 executed 2026-08-11 (§3l) — the Renewables Obligation moved behind the same door. The world no longer reads `_ROC_OBLIGATION_LEVEL` / `_ROC_BUY_OUT_PRICE_GBP`, two of a sibling layer's PRIVATE tables.
edge: simulation.run_phase2b -> company.risk.collateral_death_test | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.risk.hedge_policy | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.trading.forward_book | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.trading.hedge_decision | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.trading.wholesale_credit_exposure | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> saas.cost_to_serve | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> saas.customer_reaction | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> saas.demand_response | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> saas.growth_mandate | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> saas.ledger | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> saas.property_model | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> saas.smart_meter_rollout | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> saas.tariff_pricing | disposition=owed | design=A_composition_lift
edge: simulation.run_phase3a -> saas.customer_reaction | disposition=cut | reason=A executed 2026-08-10, PART 1 of the lift — the seven MISFILED harnesses. `run_phase3a` is 100% composition (`94` lines, every symbol it defines unimported outside tests, its own docstring calling it a run/script), has ZERO importers anywhere inside the wall, and hands the company only OBSERVABLES (the supplier's own settled records). It moved to `tools/run_phase3a.py`, where entry points live. Not a laundering, and the distinction is measured not argued: no walled module's dependency set changed (zero walled importers), and the step-7 indirect ratchet — which walks exactly this bridge — still reports 3 indirect crossings, not 4. See §3c.
edge: simulation.run_phase4b_on_phase2b -> saas.churn_model | disposition=cut | reason=A executed 2026-08-10, PART 1 of the lift — the seven MISFILED harnesses. `run_phase4b_on_phase2b` is 100% composition (`75` lines, every symbol it defines unimported outside tests, its own docstring calling it a run/script), has ZERO importers anywhere inside the wall, and hands the company only OBSERVABLES (the supplier's own settled records + its own supply book). It moved to `tools/run_phase4b_on_phase2b.py`, where entry points live. Not a laundering, and the distinction is measured not argued: no walled module's dependency set changed (zero walled importers), and the step-7 indirect ratchet — which walks exactly this bridge — still reports 3 indirect crossings, not 4. See §3c.
edge: simulation.run_phase4b_on_phase2b -> saas.cost_to_serve | disposition=cut | reason=A executed 2026-08-10, PART 1 of the lift — the seven MISFILED harnesses. `run_phase4b_on_phase2b` is 100% composition (`75` lines, every symbol it defines unimported outside tests, its own docstring calling it a run/script), has ZERO importers anywhere inside the wall, and hands the company only OBSERVABLES (the supplier's own settled records + its own supply book). It moved to `tools/run_phase4b_on_phase2b.py`, where entry points live. Not a laundering, and the distinction is measured not argued: no walled module's dependency set changed (zero walled importers), and the step-7 indirect ratchet — which walks exactly this bridge — still reports 3 indirect crossings, not 4. See §3c.
edge: simulation.run_phase4b_on_phase2b -> saas.enterprise_value | disposition=cut | reason=A executed 2026-08-10, PART 1 of the lift — the seven MISFILED harnesses. `run_phase4b_on_phase2b` is 100% composition (`75` lines, every symbol it defines unimported outside tests, its own docstring calling it a run/script), has ZERO importers anywhere inside the wall, and hands the company only OBSERVABLES (the supplier's own settled records + its own supply book). It moved to `tools/run_phase4b_on_phase2b.py`, where entry points live. Not a laundering, and the distinction is measured not argued: no walled module's dependency set changed (zero walled importers), and the step-7 indirect ratchet — which walks exactly this bridge — still reports 3 indirect crossings, not 4. See §3c.
edge: simulation.run_phase4c_on_phase2b -> company.billing.account_adjustment_register | disposition=cut | reason=B_bill_assembly_is_the_suppliers_own (A_composition_lift step 11) EXECUTED 2026-08-10 — monthly bill assembly moved to `company/billing/monthly_bill_assembly.py` behind `company/interfaces/bill_assembly.py`. The world hands over settled records and a `ReadArrivalFeed` and takes back bills; the back-billing cap, the write-off register and the bill generator are unreachable from the SIM. The read direction is INVERTED rather than carried across — see §3f.
edge: simulation.run_phase4c_on_phase2b -> company.billing.back_billing | disposition=cut | reason=B_bill_assembly_is_the_suppliers_own (A_composition_lift step 11) EXECUTED 2026-08-10 — monthly bill assembly moved to `company/billing/monthly_bill_assembly.py` behind `company/interfaces/bill_assembly.py`. The world hands over settled records and a `ReadArrivalFeed` and takes back bills; the back-billing cap, the write-off register and the bill generator are unreachable from the SIM. The read direction is INVERTED rather than carried across — see §3f.
edge: simulation.run_phase4c_on_phase2b -> company.billing.dd_review_runner | disposition=owed | design=A_composition_lift
edge: simulation.run_phase4c_on_phase2b -> company.billing.pre_bill_validation | disposition=cut | reason=`A_composition_lift` step 14, 2026-08-11 (§3i) — the Tier-1 issuance gate moved into `company/finance/accounting_close.py` behind `company.interfaces.accounting_close`. Deciding whether a bill is fit to issue is the supplier's own routine; the world never sees the gate, only the closed books.
edge: simulation.run_phase4c_on_phase2b -> company.compliance.domain_invariants | disposition=cut | reason=`A_composition_lift` step 14, 2026-08-11 (§3i) — the billed-clock reconciliation moved with the posting it checks. It was a function-scope import inside `main()`, which the walker sees but a reader easily does not; it is now adjacent to the ledger it reconciles, and §3i records the TAUTOLOGY that adjacency creates and the independent control built for it.
edge: simulation.run_phase4c_on_phase2b -> saas.bill_generator | disposition=cut | reason=B_bill_assembly_is_the_suppliers_own (A_composition_lift step 11) EXECUTED 2026-08-10 — monthly bill assembly moved to `company/billing/monthly_bill_assembly.py` behind `company/interfaces/bill_assembly.py`. The world hands over settled records and a `ReadArrivalFeed` and takes back bills; the back-billing cap, the write-off register and the bill generator are unreachable from the SIM. The read direction is INVERTED rather than carried across — see §3f.
edge: simulation.run_phase4c_on_phase2b -> saas.churn_model | disposition=cut | reason=`A_composition_lift` step 15, 2026-08-11 (§3j) — the supplier's BELIEF about who will leave — a belief it is allowed to get wrong, which is the point of the wall. Moved with its group; `home_move_win_rate` and `enterprise_value` both consume it, so cutting it alone would have left the world holding the intermediate and threading it back.
edge: simulation.run_phase4c_on_phase2b -> saas.contact_model | disposition=cut | reason=`A_composition_lift` step 16, 2026-08-11 (§3k) — the supplier's estimate of how likely its own bill is to generate a contact, how many escalate to a complaint, and the service-quality score off them. Moved into `company/analytics/billing_experience_view.py` behind `company.interfaces.billing_experience` with `saas.payment_behaviour`; the world hands over the bills as DATA and takes back a `BillingExperienceView`. §3k NAMES the leak this does NOT repair: `simulation/contact_centre.py` still draws the world's actual contact events off this estimate, the B2/B3 inversion, filed as a finding rather than fixed on sight.
edge: simulation.run_phase4c_on_phase2b -> saas.cost_to_serve | disposition=cut | reason=`A_composition_lift` step 15, 2026-08-11 (§3j) — the supplier's own apportionment of cost to a customer. Moved into `company/analytics/customer_value_view.py` behind `company.interfaces.customer_value` with the other three of its group; it also produces the account-6100 posting schedule the close consumes, which is why that computation moved earlier and why §3j carries a control over the region it moved across.
edge: simulation.run_phase4c_on_phase2b -> saas.enterprise_value | disposition=cut | reason=`A_composition_lift` step 15, 2026-08-11 (§3j) — what the supplier thinks its book is worth, off its own churn and cost-to-serve beliefs. Moved with its group; it is the end of the dependency chain that makes these four one process rather than four items.
edge: simulation.run_phase4c_on_phase2b -> saas.home_move_win_rate | disposition=cut | reason=`A_composition_lift` step 15, 2026-08-11 (§3j) — what this supplier will pay to keep a moving customer, priced off its own churn belief and its own market position. Moved with its group.
edge: simulation.run_phase4c_on_phase2b -> saas.ledger | disposition=cut | reason=`A_composition_lift` step 14, 2026-08-11 (§3i) — double-entry posting, the P&L derivation, the ledger summary and the account-6100 shaping of the cost-to-serve schedule all moved company-side. The world still owns the settled records and the spend schedules; it hands them over as DATA and takes back an `AccountingClose`.
edge: simulation.run_phase4c_on_phase2b -> saas.payment_behaviour | disposition=cut | reason=`A_composition_lift` step 16, 2026-08-11 (§3k) — the supplier's credit-risk segmentation of its own customers, the bad-debt provision rate it books against each, and the payment date it expects. This is the edge §3i explicitly recorded as NOT falling with `saas.ledger`, because `build_payment_behaviour(bills)` was still called world-side for the billing-experience output; step 16 is the group named there, so the debt is paid rather than restated. The bills cross UNFILTERED — §3k records why the close's issuance filter must not be applied here and the mutation that pins it.
edge: simulation.run_segments -> saas.growth_mandate | disposition=cut | reason=A executed 2026-08-10, PART 2 of the lift — `run_segments` was the ONE of the three standing shape-A files that passes conditions 1, 2 and 3 by measurement (zero walled importers by AST census; `main` is the only symbol anything imports, and only from `tools/`; `main()` + `__main__` + a docstring calling itself a run). Its population physics is delegated to `simulation/segments.py`, so the file is composition with no residue to strand. Moved to `tools/run_segments.py`. See §3d/§3e. Condition 4: the mandate string and the £50/month overhead are the company's own constants, read back out — no sim internal crosses.
edge: simulation.run_segments -> saas.ledger | disposition=cut | reason=A executed 2026-08-10, PART 2 of the lift — `run_segments` was the ONE of the three standing shape-A files that passes conditions 1, 2 and 3 by measurement (zero walled importers by AST census; `main` is the only symbol anything imports, and only from `tools/`; `main()` + `__main__` + a docstring calling itself a run). Its population physics is delegated to `simulation/segments.py`, so the file is composition with no residue to strand. Moved to `tools/run_segments.py`. See §3d/§3e. Condition 4: `make_fixed_cost_event(month, FIXED_COST_MONTHLY)` is handed a month and the company's own constant — no sim internal crosses.
edge: simulation.run_segments -> saas.property_model | disposition=cut | reason=A executed 2026-08-10, PART 2 of the lift — `run_segments` was the ONE of the three standing shape-A files that passes conditions 1, 2 and 3 by measurement (zero walled importers by AST census; `main` is the only symbol anything imports, and only from `tools/`; `main()` + `__main__` + a docstring calling itself a run). Its population physics is delegated to `simulation/segments.py`, so the file is composition with no residue to strand. Moved to `tools/run_segments.py`. See §3d/§3e. Condition 4: nothing is handed to the company here at all — the dwelling defaults flow the other way, INTO `simulation.demand_model`. Whether those dwelling facts are world physics filed company-side (the B1 shape) is a real open question, and lifting this file does NOT bury it: `simulation.run_phase2b -> saas.property_model` is still live and still ruled.
edge: simulation.run_segments -> saas.tariff_pricing | disposition=cut | reason=A executed 2026-08-10, PART 2 of the lift — `run_segments` was the ONE of the three standing shape-A files that passes conditions 1, 2 and 3 by measurement (zero walled importers by AST census; `main` is the only symbol anything imports, and only from `tools/`; `main()` + `__main__` + a docstring calling itself a run). Its population physics is delegated to `simulation/segments.py`, so the file is composition with no residue to strand. Moved to `tools/run_segments.py`. See §3d/§3e. Condition 4 FAILED here and was REPAIRED, not relocated: `naked_fraction` was `1 - sim.hedging_strategy.MIN_HEDGE_FLOOR` — the world's hedge mandate deciding what the company prices capital cost on, the same leak B7 cut out of `simulation/renewals.py`. It now reads `company.risk.hedge_policy.COMPANY_MIN_HEDGE_FLOOR`. Both floors are 0.85, so the argument is the identical float and no price moves. The cold-start forward remains the world's number — B7's named residual, restated in §3e.
# --- A_composition_lift (INDIRECT — added 2026-08-10, step 7) ---
# These three do not appear as import statements in `run_phase2b.py` naming a company
# module. They reach `company/billing/` through `background.live_payment_triad` and
# `tools.couple_w2_11_d5`, and were invisible to every instrument in this programme until
# the walker learned to look through the bridge packages (§3b). They are ruled to the same
# design as the 32 direct edges out of the same file, because the same cut kills them: once
# run_phase2b's composition sits above both layers, its source endpoint stops being a walled
# module and the route stops crossing the wall. Cutting only the printed bridge is NOT the
# cut — each is carried by BOTH bridges, which is why the checker prints every entry point.
edge: simulation.run_phase2b -> company.billing.account_ledger | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.billing.arrears_engine | disposition=cut | reason=CUT 2026-08-10 as a SIDE EFFECT, not by this design: `15125f388` (atom D21, H27 Expert Hour #5) removed `tools/couple_w2_11_d5`'s module-scope `from company.billing.arrears_engine import age_bucket` when that dimension's truth side stopped being the company organ's own rule, and that import was the second bridge hop carrying this route. Recorded as cut rather than owed because a debt against a corpse hides that the register is stale. Verified as a real cut and not a blind walker: the sibling edges out of the same file and line are still reported live by the same walk. The remaining TWO stay owed to A_composition_lift.
edge: simulation.run_phase2b -> company.billing.payment_observation_consumer | disposition=owed | design=A_composition_lift
WALL-CROSSING-EDGES -->

---

## 5. What this register does not decide

- **Whether the crossing count should be zero.** It is a diagnostic. The ratchet enforces monotone
  shrink; nothing here sets a target, and nothing may be promoted or shortened to hit one.
- **The order the eight designs are executed in.** B8 is cheapest and B1 is the highest
  value-per-edge with its blocking objection already measured away; B2 is the most serious and the
  least mechanical. That is a ranking input, not a schedule.
- **Anything about the Epoch-3 adapter programme.** It is the BOUNDARY half of this knife and owns
  its own scope. Its eight atoms were confirmed idle before pass 3's first edit; **re-check before
  executing any design here** — two lanes cutting one seam is the failure the plan's §3 is about.
