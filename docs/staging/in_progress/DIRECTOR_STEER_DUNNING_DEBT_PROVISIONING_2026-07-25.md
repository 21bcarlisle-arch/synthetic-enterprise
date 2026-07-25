<!-- SUPERVISOR_DRAW: blocked -->
<!-- PARKED 2026-07-25 (moved root -> in_progress to stop the empty-root re-grant pathology, per
     CLAUDE.md multi-part-instruction rule; the B2_OPEX pattern). This steer is a design-session
     output: large ledger-spine workstream, sequenced and partly director-reserved. Its ONE
     dependency-forced, non-walled, buildable-now next step (§5 step-1: the bad-debt RECONCILIATION
     BRIDGE, report-first) is now MINTED as RUNG-1 work ->
     docs/staging/PLANNER_MINTED_bad_debt_reconciliation_bridge_2026-07-25.md. Draw THAT, not this doc.
     BLOCKING SUB-ITEMS holding the rest of this steer:
       (1) §5 steps 2-4 (wire outcome->estimate; the ladder w/ ability-to-pay; CoT attribution) are
           two-way-door DOWNSTREAM of step-1 landing + being read (don't build on an unreconciled base).
       (2) DIRECTOR-RESERVED walls R-1..R-5 (method fixed-vs-curriculum-dial; dunning harm ratio;
           write-off-timing-as-policy; disengaged-majority curriculum/fidelity; holdout discipline) —
           escalate, do not decide. D5 stands: detection stays SENSING-ONLY, no collections action.
     UNBLOCK: the reconciliation report lands+read -> re-rank step-2; OR a director ruling on any R-*.
     Decisions D1-D7 are transmit-and-absorb (R12 diagnostic-not-target; D2 variance = first-class
     measured, register as a fidelity-ledger row; D3 three-clock bridge on the revenue-bridge standing). -->

# [DIRECTOR-STEER] — Dunning, debt discovery and provisioning: the design session output (2026-07-25)

**Type:** [DIRECTOR-STEER] via advisor bridge. This is the session RESERVED by
`DIRECTOR_RULING_PAYMENT_DETECTION_CARVE_OUT_2026-07-25.md` §3. That reservation is now
**RELEASED** for the scope below and only that scope.

**Method note (R9):** every finding below was verified against origin this session — module source
read directly via the Contents API, caller counts by code search. Where a map summary or an earlier
design doc says something different, the code wins and the divergence is named.

---

## 0. The headline, before anything else

**The provisioning method that is actually live is not expected-credit-loss and not incurred-loss.
It is a flat revenue haircut, and it is structurally incapable of ever being wrong.**

Two better mechanisms are already built, tested, and wired to nothing. A third estimate — the real
one — lands on a different clock and never meets either. The design task is therefore mostly
**reconciliation and wiring, not new construction**. Treat that as good news about scope and bad
news about what the published P&L currently means.

---

## 1. Findings (verified, evidence named)

### F1 — The live provisioning method is a contra-revenue rate

- `saas/payment_behaviour.py::bad_debt_provision_gbp()` = `revenue × flat rate by credit-risk band`
  (low 0.005 / medium 0.02 / high 0.05 / vulnerable 0.08).
- The band comes from `CREDIT_RISK_BY_CUSTOMER` — a **hardcoded four-entry dict** (C1 low, C2
  medium, C3 vulnerable, C4 low). Every other customer in the book falls through to a default.
- `saas/ledger.py::make_payment_received_event` books cash as `total_amount_gbp − provision_gbp`:
  **cash received is reduced by the provision, not by non-payment.** A customer who pays in full
  still contributes less than they paid.
- `make_bad_debt_event` posts the write-off **30 days after expected payment date,
  unconditionally** — it is not gated on the payment having failed.

**Why this matters more than the rate being wrong:** no outcome ever feeds back into the estimate,
so estimate-vs-actual variance does not exist. A provisioning method whose error cannot be measured
is not a provisioning method. It also cannot express aging, cure, or roll-rate — the three things a
provision is for.

### F2 — Two better mechanisms are built and unwired

| Module | What it is | Live callers |
|---|---|---|
| `company/finance/bad_debt_provision.py` | Aging matrix — current/31-60/61-90/91-180/180+ at 0.5/5/20/50/90% | **Zero.** `AgingBucket` appears only in the module itself, its own test, and one coverage-expansion test. |
| `company/finance/debt_collection.py` | A real dunning ladder — 7-day reminder → 14-day warning → 28-day pre-legal → DCA → legal → write-off, with per-stage recovery probabilities and 6-year statute-barring | **Zero.** `DebtStage` appears only in the module, its own test, and one archived staging doc. |

This is the same class as `back_billing.py` and `dd_mandate_register.py` — both previously found
fully built with no callers. R10 applies: it is a class defect, not two instances.

The aging matrix's docstring claims "forward-looking provision." It is not forward-looking; the
rates are hardcoded constants. The shape is right (a provision matrix is the correct IFRS 9
simplified-approach form for trade receivables); the substance is asserted, not estimated.

### F3 — There are four expected-loss numbers and no bridge between them

1. Flat haircut (live, at bill issue) — **billed clock**.
2. Aging matrix (unwired).
3. Stage recovery probabilities (unwired).
4. `simulation/arrears_engine.py::compute_emergent_bad_debt()` — the **actual outcome**, which
   `apply_emergent_bad_debt()` writes onto settlement records, replacing the flat rate and carrying
   the net-margin delta through treasury — **settled clock**.

So the estimate sits on the billed clock, the outcome sits on the settled clock, cash sits on the
banked clock, and nothing reconciles them.

**This answers the question "how does the provisioning choice move the P&L across the three
clocks": today it doesn't move it, it hides it.** The variance between provision and realised loss
is the entire P&L signal of a provisioning method, and it is currently unobservable by construction.

This is structurally identical to the two-revenue-pipelines defect (`MARGIN_REALISM_E2_TWO_PIPELINES_FINDING.md`),
which disagreed 26–52% every year and was closed by building a reconciliation bridge. **Revenue has
a bridge. Bad debt has none.**

### F4 — The dunning ladder's hard half is absent

The built ladder is a **timing** ladder (7/14/28 days). That is the easy half and it is the half
that is built.

**`ability_to_pay` returns zero hits across the entire repository.** SLC 27.5–27.8 requires a
domestic supplier to take the customer's ability to pay into account when setting a debt repayment
rate. That is the central legal constraint on UK domestic collections and it governs the
**instalment amount**, not the stage timing. `company/billing/payment_deferral.py` and an
arrears-engine `repayment_plan` exist, so the plan object is there; the affordability test that
sizes it is not.

This is a **coupling gap, not a build-from-scratch gap**: `C6_affordability_inference` (L2) already
produces an affordability band from observables only, with a measured belief gap of 0.607. That is
precisely the input an ability-to-pay assessment consumes. Same shape as W2_12.

Present and usable: winter moratorium and PPM warrant restrictions (`ppm_warrant_register.py`,
`winter_moratorium.py`), the domestic late-charge exclusion and business statutory interest (W2_9 at
L3), disconnection warning machinery.

### F5 — The post-write-off tail already exists and is better than expected

`arrears_engine.py` carries DCA placement (30d), DCA outcome (180d), debt sale (90d), recovery rates
by debt archetype (OVERWHELMED 0.30 / NEUTRAL 0.20 / AVOIDANT 0.20), 15% DCA commission and a 12%
debt-sale haircut — all explicitly flagged **illustrative and unbenchmarked** in their own comments.
The pipeline is there; the anchors are not. That is the honest state and it should stay labelled
that way until anchored.

---

## 2. Two corrections to the session's framing

**C1 — "The cannot-pay / will-not-pay gap in Board Spec 006" is not a gap.**
The spec grades it **MET** twice: §1 S1-collections ("the best-realised claim in the spec") and
battery item 6-5 ("the flagship coupled triad"). `willingness_classification.py` holds the hidden
ABILITY×WILLINGNESS 2×2; `arrears_classifier.py` runs a Bayes gate with an 8:1 signed harm cost,
PURSUE iff p > 8/9.

The real adjacent gap is **battery item 8 / S3-measured: ABSENT — no holdout or uplift machinery
anywhere in the codebase.** The company distinguishes cannot-pay from will-not-pay and treats them
differently, and has **never measured whether the differentiated treatment works**. The coupled-triad
gap measures belief-versus-truth; it does not measure treatment uplift. The discriminator is proven;
the treatment is a hypothesis wearing a name.

Design attention belongs on the treatment arm, not the split.

**C2 — Change of tenancy is the crystallisation moment, not the discovery moment.**
W2_12 DISCOVER (2026-07-23) names the missing piece precisely: `account_closure.py` carries the
`DEBT_REFERRED` **status** but no modelled **probability** that a move-out final bill goes unpaid.
CoT is where an already-known arrears balance becomes **unrecoverable because the person has gone** —
that is loss crystallisation. Discovery happens earlier, at due-date plus grace, which is exactly
what the detection organ authorised yesterday senses. Putting the discovery sensor at CoT would site
it in the wrong place and double-count against that organ.

What *is* distinctive about CoT, and is the genuinely hard problem, is **attribution**: debt follows
the person, not the property (SLC 27 / SLC 12.2, already typed in `change_of_tenancy_register.py`).
At the moment of a move the supplier frequently cannot tell whether an unpaid balance belongs to a
departed occupant, an incoming occupant on deemed terms, or a void period. **Misattributed debt —
pursuing a new tenant for a previous occupant's balance — is a real and recurring UK enforcement
theme, and it is a customer-harm event, not just a revenue error.** That is the physics worth
modelling at CoT.

---

## 3. DECIDED — follows from already-ratified canon, transmit as decisions

**D1 — Provisioning is a diagnostic, never a target (R12).** The provision figure may not be
calibrated toward a benchmark, a plausibility band, or a better-looking P&L. The company must be
permitted to provision badly.

**D2 — The provision-to-realised-loss variance is a first-class measured quantity.** Same status as
the coupled-triad gaps: measured, published, never tuned away. A smaller *measured* variance is the
honesty target; a company that believes it provisions perfectly is a wider hidden gap wearing a
better number (R15 both ways — the control must be failable).

**D3 — Bad debt requires a reconciliation bridge across the three clocks, on the same standing as
the revenue bridge.** No bad-debt figure is published without its clock (R14 already binds this).
Estimate on billed, outcome on settled, cash on banked, with every reconciling item named and
quantified.

**D4 — The unwired mechanisms are reconciled or retired, not left standing.** Two fully-built
zero-caller modules holding competing answers to the same question is the exact hazard R10 was
written for. Either becomes the live method or is honestly retired; both staying is not an option.

**D5 — Detection remains sensing-only.** Yesterday's carve-out is unchanged. Nothing in this steer
authorises a collections *action* — dunning execution, service change, or pricing consequence.

**D6 — Ability-to-pay is a hard regulatory constraint on the ladder, not a policy preference.** Any
repayment-rate mechanism that does not consume an affordability assessment is non-compliant by
construction, and the invariant must be failable (R15).

**D7 — Illustrative DCA/debt-sale constants stay labelled illustrative** until externally anchored.
No silent promotion to fact.

---

## 4. RESERVED TO THE DIRECTOR — do not decide these without him

**R-1 — Provisioning method: fixed baseline, or curriculum dial?**
My recommendation is the **IFRS 9 simplified approach** (lifetime ECL from day one, provision matrix,
no three-stage transfer machinery) because that is what real UK suppliers actually do — but with the
matrix **estimated from the company's own realised roll rates plus a forward-looking overlay**, not
asserted. The overlay is not decoration here: 2022 wholesale prices → higher bills → higher default,
and a static matrix would have under-provided in 2021 and over-provided in 2024.

The genuinely interesting alternative is to make method itself an **R13 curriculum dial**. Incurred
loss is the *wrong* model and precisely for that reason the *valuable* one: it systematically
under-provides right up to the point of failure, which is close to how several real 2021–22 UK
suppliers looked shortly before they went. A tournament that cannot run a company that provisions
badly and dies of it is missing a mortality mechanism. **Director's call — R13 curriculum is
reserved.**

**R-2 — The harm-cost ratio for dunning misclassification.** Collections has an 8:1 signed harm cost
for pursue/forbear. A dunning ladder needs its own, and it is not the same number — the harm of
escalating a cannot-pay household to a warrant is categorically different from the harm of failing
to pursue a will-not-pay. Harm weights are curriculum.

**R-3 — Write-off timing as a policy object.** This is the single largest P&L lever in the whole
design: when a balance leaves the book determines the year the loss lands. Is write-off timing a
fixed rule, or a company policy choice the company may get wrong and be scored on? Values-adjacent.

**R-4 — The disengaged-majority question (F3, still open from Board Spec 006).** ACTIVE 0.48 vs
DISENGAGED 0.29 leans toward the "book of rational actors" the board warns against. Debt physics is
unusually sensitive to this — a disengaged book fails differently. Curriculum choice or fidelity
defect: still your call, and it now has a second lane depending on it.

**R-5 — Holdout discipline.** Battery item 8 fails today. Introducing holdouts means deliberately
under-treating a control group of real (simulated) customers in arrears. That has a consumer-duty
shape to it even in simulation, and it is a values call, not a build decision.

---

## 5. Sequencing (the requirement, not the implementation)

The order is forced by dependency, not preference:

1. **Reconcile before building.** The four expected-loss numbers must be brought into one place and
   their disagreement quantified — as the revenue bridge did — *before* any new provisioning
   mechanism is chosen. Choosing a method on top of an unreconciled base repeats the MARGIN_REALISM
   error of computing percentages on an untrustworthy denominator.
2. **Wire the outcome back to the estimate.** Until realised loss feeds the provision, no method can
   be evaluated, and R-1 cannot be answered on evidence.
3. **Then the ladder**, with ability-to-pay as a gating constraint from the first commit rather than
   a later compliance retrofit.
4. **CoT attribution physics last** — it depends on the ladder's arrears state existing.

W2_12 stays a coupling layer per its own DISCOVER. No new register, no new closure engine, no new
deemed-rate engine.

---

## 6. Risk

**What this touches:** `saas/ledger.py` (the double-entry spine — every published financial figure),
`saas/payment_behaviour.py`, `simulation/run_phase4c_on_phase2b.py`, the two unwired finance modules,
and every surface rendering net margin, treasury or enterprise value.

**Blast radius: high, and higher than it looks.** Bad debt reaches `net_margin_gbp` through
`apply_emergent_bad_debt()`'s treasury carry-forward, so any change to the bad-debt line moves the
headline P&L, enterprise value, and the margin bridge's own remainder. The bridge currently records
bad debt as a non-reconciling item; that classification was made when the figures were smaller and
must be re-derived, not inherited.

**Probable failure mode:** a stale-test wedge in the publish gate. Prior integration work has
repeatedly broken dependents that were never themselves changed, and the ledger has more dependents
than anything else in the codebase. Expect the four publish-gate wedges pattern.

**Inline mitigation:** treat the reconciliation as report-first — quantify the disagreement and
publish it *before* changing any figure that feeds a surface. A bridge that explains the gap is
safe; a corrected number that moves the front door is not, until the gate is green.

**Second-order risk specific to this domain:** improving detection and provisioning together will
make bad debt look worse. That is the correct direction and it must not be softened. If the number
degrades on a truer method, the number was wrong before (R12).

**Proportionality tag:** reconciliation and measurement = **just do it**. Any change to a published
financial figure = **contract-touching, implement with named mitigations**. Provisioning method
selection and harm weights = **[ACT] first — reserved above.**

---

*Advisor bridge, 2026-07-25. Findings verified against origin this session; caller counts by code
search; no claim in §1 is carried from memory or from a map summary.*
