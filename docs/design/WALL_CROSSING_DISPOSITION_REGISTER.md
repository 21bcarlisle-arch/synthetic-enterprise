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
WALL-CROSSING-DESIGN -->

<!-- WALL-CROSSING-DESIGN B2_company_brain_decides_the_world
5 edges, and the most serious inversion in the register. `simulation.customer_events` imports
the company's own churn model, its customer-reaction model and its home-move win rates in order
to decide WHO ACTUALLY CHURNS; `simulation.satisfaction_churn` takes the company's
MAX_CHURN_PROBABILITY as the world's ceiling. This makes the company's belief self-fulfilling:
the model cannot be wrong about churn, because the model IS churn. That destroys the quantity
the COUPLED TRIAD is built to measure — the gap between what the company believes and what the
world does — and it silently flatters every churn-accuracy figure derived from it. Cut: the
world gets its own churn physics, derived from customer state (resentment stock, activation
energy, price position, tenure) with no import of any company model; the company keeps its
estimate; the harness measures the gap between them. This is a coupled-triad build, not a
mechanical move, and it must not be attempted as one.
WALL-CROSSING-DESIGN -->

<!-- WALL-CROSSING-DESIGN B4_billing_mechanics_reached_directly
4 edges, of which THREE WERE CUT 2026-08-10 (§3a) and ONE remains — this block stays a plan
only for `simulation.dd_collection_book -> company.billing.direct_debit`.

The design, unchanged: `credit_refund_events`, `dd_balance_book`, `dd_collection_book` and
`dd_level_collection_book` reach into `company/billing/` for refund construction, direct-debit
scheduling and — in the worst case — a PRIVATE function, `dd_review._recommended_monthly`. What
the world legitimately knows here is what a customer would experience: money left the account
on a day, a refund arrived, the monthly amount changed. It does not know the routine that chose
the amount. Cut: the company EMITS these as instructions/outcomes over the existing async wall
contract (C-S3), and the world's books apply what they receive rather than recomputing it from
the company's internals. The private-function import goes first: it is a dependency on a
routine the company is free to change without notice, which is the one property a real supplier
does not grant the world.

WHAT IS LEFT, AND WHY IT IS THE HARD ONE. `dd_collection_book` does not merely CONSULT the
company's billing module — it BUILDS the company's artefact: it opens a `DirectDebitBook`,
creates mandates on it and records `DDPaymentAttempt`s, so the world is operating the supplier's
collection register. Two of the four names it imports have already been dealt with elsewhere
(`staggered_payment_day` moved to the world with the B1-shaped cut; `next_collection_on_day` has
REAL company-side callers inside `direct_debit.py`, so it can neither move nor be duplicated
without becoming `one name, two numbers`). What is left is the book itself, and handing it over
is the push B4 actually asks for: the company emits a collection instruction, the world reports
what happened to the money. That needs a company-side emitter, which is `A_composition_lift`'s
work — the same structural blocker measured for B5 and re-measured here, not inherited.
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

### B4_billing_mechanics_reached_directly — EXECUTED IN PART 2026-08-10 (3 of 4 edges)

Three edges cut, in the order the design itself set. The design block stays in §3 because its
fourth edge is still `owed`, and what remains is named there rather than implied.

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

## 4. The register — all 91 examined crossings, 59 of them still live

88 was the count when every crossing was ruled on (2026-08-09, step 2); step 7 found three more the
walker could not see (§3b), making 91 rows. THIRTY-EIGHT have since been CUT — seventeen by B1/B3–B8
(§3a), sixteen by `A_composition_lift` part 1 (§3c) and four by part 2 (§3e) — so the tree carries 53
and this section carries 91 rows: a cut row is not deleted, because a deleted row is how a re-entry
becomes invisible. The live count is not maintained by
hand here — `tools/wall_crossing_dispositions.py` prints it from the walker on every run, and
the two numbers disagreeing is itself the failure the tool exists to raise.

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
edge: simulation.satisfaction_churn -> saas.churn_model | disposition=owed | design=B2_company_brain_decides_the_world
# --- B3_world_needs_its_own_cap_physics ---
edge: simulation.hedged_settlement -> company.pricing.ofgem_price_cap | disposition=cut | reason=B3 executed 2026-08-10 — the published cap schedule moved to the regulation commons as a DATA artefact (which has no import statement to launder a dependency through, unlike the unwalked-module home the block refused), and each lane now reads it with its own loader. The world enforces the ceiling from `simulation/price_cap_enforcement.py`; the company keeps its own reading and the two are free to differ. No value moved — both readings agree across the whole published span today, and nothing pins them there.
# --- B4_billing_mechanics_reached_directly ---
edge: simulation.credit_refund_events -> company.billing.credit_refund | disposition=cut | reason=B4 executed 2026-08-10 — the world no longer opens the company's SLC 14 book. It reports a closure, the credit left in the account and the date the money ARRIVED to `company/interfaces/credit_refund_requests.py` and logs what comes back; the deadline, the record type, the status lifecycle and the four-way refund taxonomy are unreachable from the SIM. The trigger is CLASSIFIED behind the door rather than passed in, which is the substance of the cut: accepting a `trigger=` argument would have left the taxonomy in the world's hands and made this a spelling change.
edge: simulation.dd_balance_book -> company.billing.dd_review | disposition=cut | reason=B4 executed 2026-08-10, and this was the one the design said goes FIRST — it imported the PRIVATE `_recommended_monthly`, i.e. depended on a routine the company is free to rename without notice. The world is now TOLD the standing monthly amount through `company/interfaces/dd_review_outcome.py` (the number on the customer's letter); the ±5% SLC 27B band, the increase/decrease/maintain classification and the rounding convention stay behind the door.
edge: simulation.dd_collection_book -> company.billing.direct_debit | disposition=owed | design=B4_billing_mechanics_reached_directly
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
edge: simulation.run_phase2b -> company.market.flexibility_revenue_book | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.market.ic_flexibility_revenue | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.policy.decision_policy | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.pricing.margin_feedback | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.pricing.ofgem_price_cap | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.pricing.tariff_engine | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.regulatory.ccl_ledger | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.regulatory.fit_book | disposition=owed | design=A_composition_lift
edge: simulation.run_phase2b -> company.regulatory.roc_ledger | disposition=owed | design=A_composition_lift
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
edge: simulation.run_phase4c_on_phase2b -> company.billing.account_adjustment_register | disposition=owed | design=A_composition_lift
edge: simulation.run_phase4c_on_phase2b -> company.billing.back_billing | disposition=owed | design=A_composition_lift
edge: simulation.run_phase4c_on_phase2b -> company.billing.dd_review_runner | disposition=owed | design=A_composition_lift
edge: simulation.run_phase4c_on_phase2b -> company.billing.pre_bill_validation | disposition=owed | design=A_composition_lift
edge: simulation.run_phase4c_on_phase2b -> company.compliance.domain_invariants | disposition=owed | design=A_composition_lift
edge: simulation.run_phase4c_on_phase2b -> saas.bill_generator | disposition=owed | design=A_composition_lift
edge: simulation.run_phase4c_on_phase2b -> saas.churn_model | disposition=owed | design=A_composition_lift
edge: simulation.run_phase4c_on_phase2b -> saas.contact_model | disposition=owed | design=A_composition_lift
edge: simulation.run_phase4c_on_phase2b -> saas.cost_to_serve | disposition=owed | design=A_composition_lift
edge: simulation.run_phase4c_on_phase2b -> saas.enterprise_value | disposition=owed | design=A_composition_lift
edge: simulation.run_phase4c_on_phase2b -> saas.home_move_win_rate | disposition=owed | design=A_composition_lift
edge: simulation.run_phase4c_on_phase2b -> saas.ledger | disposition=owed | design=A_composition_lift
edge: simulation.run_phase4c_on_phase2b -> saas.payment_behaviour | disposition=owed | design=A_composition_lift
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
