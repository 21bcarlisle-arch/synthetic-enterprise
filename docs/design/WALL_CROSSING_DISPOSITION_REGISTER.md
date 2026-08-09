# The wall-crossing disposition register

**Atom:** `KNIFE3_wall_crossing_paydown` (lane `H_harness`, L0→L2), pass 3 of 4 of AO5
**Plan:** `docs/design/KNIFE_HOTSPOT_PASSES.md` § Pass 3
**Mechanism:** `python3 tools/wall_crossing_dispositions.py` — rc 2 if any live crossing has no ruling
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
65 edges, 10 files, all `simulation/run_phase*.py` + `run_segments`. These are scenario
harnesses, not the simulated world: nine of the ten are leaves inside the wall and every one
has a `main()`. The cut is NOT a bulk move of the files to `tools/` — see section 2b. The
composition is the substance of these files, so relocating them would remove the measurement
rather than the dependency, and pass 3's second exit clause forbids exactly that. The cut is
per-harness separation: the world-side setup the harness inlines is pushed down into
`simulation/`, the company-side decisions it inlines are pushed into the company layer behind
`company.interfaces`, and what remains above both layers is genuine entry-point composition.
Constraints measured, not assumed: `simulation.run_scenario` imports `run_phase2b` and must be
re-pointed or moved with it; `run_phase2b` carries 135 referrers outside `simulation/`, so the
mechanical rename lands in its own commit, separate from any behaviour question.
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

<!-- WALL-CROSSING-DESIGN B3_world_needs_its_own_cap_physics
1 edge. `simulation.hedged_settlement` imports `company.pricing.ofgem_price_cap` to get the cap
unit rate. The regulation-commons doctrine is what makes this subtle and what settles it: the
regulatory TEXT is a shared commons readable by every lane, because law is published in reality
— but each lane's IMPLEMENTATION of that law stays independently owned, precisely so that a
company misreading the cap stays structurally possible, matching real suppliers who get fined
for exactly that. Importing the company's READING of the cap collapses the two and makes a
misread impossible. Cut: the world enforces the cap from the published figures in the domain
artefact library, the company keeps its own reading, and the two are allowed to differ.

REFINED 2026-08-10, when this was picked up for execution alongside B6 and put back down. As
written above, the cut is UNDERSPECIFIED in exactly the place it can go wrong, and the tempting
execution is one this pass has already refused once in writing. "The world reads the published
figures" does not say WHERE the published schedule lives, and the cheapest home for it — a
lane-neutral module under `tools/` — is not walked by `tools/epistemic_wall.py`. Routing the
crossing through an unwalked module would drop the edge count by one while changing nothing
about who depends on whom: the same laundering the step-2 ruling refused for the shape-A
harnesses, and the same class as `moving a file past the walker is not a cut`. The
regulation-commons doctrine sanctions a shared home for regulatory TEXT, so a commons is not
forbidden — but "doctrine permits a commons" is not the same claim as "this particular
relocation is a cut," and the two must not be allowed to stand in for each other.

Three things this block must settle BEFORE any edge moves, none of which are mechanical:
  (a) WHERE the published window schedule lives, and whether that home is walked. If it is not
      walked, the design must say what makes it a commons rather than a blind spot.
  (b) HOW divergence is controlled. The world getting its own reading is the entire point — a
      test pinning the two readings equal would restore the coupling in the test suite that the
      cut removes from the code. But with no control at all this becomes `one name, two numbers`:
      two cap tables drifting apart silently, which is a fidelity defect in both lanes.
  (c) WHAT each side is allowed to get wrong. `get_cap_unit_rate_for_date` carries real policy
      beyond the published levels — carry-forward past the last window, `min(Ofgem, EPG)`, the
      VAT/standing-charge basis (R14). Those are READINGS of the law. The published windows are
      the law. The split between them is the cut, and it has not been drawn yet.

Sized honestly, that is a design step plus a build, not the one-line import swap the edge count
suggests. It stays `owed` until (a)–(c) are answered.
WALL-CROSSING-DESIGN -->

<!-- WALL-CROSSING-DESIGN B4_billing_mechanics_reached_directly
4 edges. `credit_refund_events`, `dd_balance_book`, `dd_collection_book` and
`dd_level_collection_book` reach into `company/billing/` for refund construction, direct-debit
scheduling and — in the worst case — a PRIVATE function, `dd_review._recommended_monthly`. What
the world legitimately knows here is what a customer would experience: money left the account
on a day, a refund arrived, the monthly amount changed. It does not know the routine that chose
the amount. Cut: the company EMITS these as instructions/outcomes over the existing async wall
contract (C-S3), and the world's books apply what they receive rather than recomputing it from
the company's internals. The private-function import goes first: it is a dependency on a
routine the company is free to change without notice, which is the one property a real supplier
does not grant the world.
WALL-CROSSING-DESIGN -->

<!-- WALL-CROSSING-DESIGN B7_renewal_is_a_company_decision
4 edges. `simulation.renewals` imports the company's tariff engine, its SaaS pricing function,
its approval interface and its decision-rights table — that is, a SIM module runs the company's
renewal pricing decision, including its internal governance. This is the shape-A composition
problem outside a `run_phase*` file, and it is the smallest instance of it, which makes it the
right place to prove the template before the ten big harnesses are touched. Cut: the renewal
DECISION moves to the company layer; the world keeps the renewal EVENT (a contract reached its
term end) and receives the resulting offer through the seam.
WALL-CROSSING-DESIGN -->

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

---

## 4. The register — all 88 examined crossings, 79 of them still live

88 was the count when every crossing was ruled on (2026-08-09, step 2). NINE have since been
CUT (§3a), so the tree carries 79 and this section carries 88 rows: a cut row is not deleted,
because a deleted row is how a re-entry becomes invisible. The live count is not maintained by
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
edge: simulation.hedged_settlement -> company.pricing.ofgem_price_cap | disposition=owed | design=B3_world_needs_its_own_cap_physics
# --- B4_billing_mechanics_reached_directly ---
edge: simulation.credit_refund_events -> company.billing.credit_refund | disposition=owed | design=B4_billing_mechanics_reached_directly
edge: simulation.dd_balance_book -> company.billing.dd_review | disposition=owed | design=B4_billing_mechanics_reached_directly
edge: simulation.dd_collection_book -> company.billing.direct_debit | disposition=owed | design=B4_billing_mechanics_reached_directly
edge: simulation.dd_level_collection_book -> company.billing.direct_debit | disposition=owed | design=B4_billing_mechanics_reached_directly
# --- B5_collections_tone_is_an_event_attribute ---
edge: simulation.arrears_engine -> company.policy.decision_policy | disposition=cut | reason=B5 executed 2026-08-10 — the tone is now read off `company/interfaces/collections_communication.py::collections_tone_for`, so the world learns the tone of a letter that ARRIVED while `DecisionPolicy` (its tone_mode, its A/B split) stays unreachable from the SIM. HALF the design, stated as such: this is a PULL and B5 asks for a PUSH (tone stamped on an emitted event). Blocked structurally, by measurement not assumption — the bill dicts are built by `simulation/run_phase4c_on_phase2b.py::build_monthly_bills`, a SIM composition root, so there is no company-side emitter to stamp; that is A_composition_lift's work. See B5 residual in §3a.
# --- B6_cpa_is_company_accounting ---
edge: simulation.acquisition_funnel -> saas.growth_mandate | disposition=cut | reason=B6 executed 2026-08-10 — the lazy `COST_PER_ACQUISITION` import is deleted and `total_amount_gbp` is a REQUIRED argument, so the funnel is told the cost and cannot consult company accounting even by accident. Measured safe before the cut: the sole live caller already passed the value, so the default branch was dead in production.
# --- B7_renewal_is_a_company_decision ---
edge: simulation.renewals -> company.governance.approval_interface | disposition=owed | design=B7_renewal_is_a_company_decision
edge: simulation.renewals -> company.governance.decision_rights | disposition=owed | design=B7_renewal_is_a_company_decision
edge: simulation.renewals -> company.pricing.tariff_engine | disposition=owed | design=B7_renewal_is_a_company_decision
edge: simulation.renewals -> saas.tariff_pricing | disposition=owed | design=B7_renewal_is_a_company_decision
# --- B8_market_feed_is_the_observable ---
edge: simulation.publish_market_feed -> company.market.price_feed | disposition=cut | reason=B8 executed 2026-08-09 — `publish_feed` moved to `company/interfaces/market_feed_publication.py`, so the (legitimate) world-publishes-prices crossing now lands on the walked seam package and is exempt by the published SEAM rule. Deliberately NOT re-exported from `company/market/price_feed.py`, which would have left the non-seam path alive.
# --- A_composition_lift ---
edge: simulation.run_phase0b -> saas.tariff_pricing | disposition=owed | design=A_composition_lift
edge: simulation.run_phase0c -> saas.clv_seed | disposition=owed | design=A_composition_lift
edge: simulation.run_phase0c -> saas.customer_reaction | disposition=owed | design=A_composition_lift
edge: simulation.run_phase0c -> saas.tariff_pricing | disposition=owed | design=A_composition_lift
edge: simulation.run_phase1c -> saas.clv_seed | disposition=owed | design=A_composition_lift
edge: simulation.run_phase1c -> saas.customer_reaction | disposition=owed | design=A_composition_lift
edge: simulation.run_phase1c -> saas.tariff_pricing | disposition=owed | design=A_composition_lift
edge: simulation.run_phase1c_full_window -> saas.clv_seed | disposition=owed | design=A_composition_lift
edge: simulation.run_phase1c_full_window -> saas.customer_reaction | disposition=owed | design=A_composition_lift
edge: simulation.run_phase1c_full_window -> saas.tariff_pricing | disposition=owed | design=A_composition_lift
edge: simulation.run_phase1c_renewals -> saas.clv_seed | disposition=owed | design=A_composition_lift
edge: simulation.run_phase1c_renewals -> saas.customer_reaction | disposition=owed | design=A_composition_lift
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
edge: simulation.run_phase3a -> saas.customer_reaction | disposition=owed | design=A_composition_lift
edge: simulation.run_phase4b_on_phase2b -> saas.churn_model | disposition=owed | design=A_composition_lift
edge: simulation.run_phase4b_on_phase2b -> saas.cost_to_serve | disposition=owed | design=A_composition_lift
edge: simulation.run_phase4b_on_phase2b -> saas.enterprise_value | disposition=owed | design=A_composition_lift
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
edge: simulation.run_segments -> saas.growth_mandate | disposition=owed | design=A_composition_lift
edge: simulation.run_segments -> saas.ledger | disposition=owed | design=A_composition_lift
edge: simulation.run_segments -> saas.property_model | disposition=owed | design=A_composition_lift
edge: simulation.run_segments -> saas.tariff_pricing | disposition=owed | design=A_composition_lift
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
