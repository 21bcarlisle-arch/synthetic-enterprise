# CORE_FIDELITY_BEFORE_LOOPS — director reorientation (P1)

**Staged:** 2026-07-08 ~12:15 BST by advisor; this is an explicit director
decision, not a proposal. **Tier:** 2 — proceed. **Phase RY is DEFERRED, not
cancelled** — do not start it. It re-enters the queue after the block below.

## The director's observation (verbatim intent)
The customer portal bill is still really poor. The sim has no unhappy-path
errors and delays. Customers have no household segments and no psychology. The
project has been going deeper into refinement loops (reputation, feedback,
gap analyses) while core aspects of the SIM and the software remain undeveloped.

## Why this outranks RY (advisor rationale, director-endorsed)
Two of the missing items are *already-decided Epoch Three mission clauses that
have not been built*: "time as a random variable — latency distributions and
unhappy paths are first-class, not edge cases," and "brand as behavioural
physics," which presupposes customers with psychology. RY's reputation→
acquisition loops would act on a homogeneous population with no psyches to move
— the loop would be mechanically real but behaviourally hollow. Build the
substrate first; RY will be worth strictly more afterwards. This is what
depth-before-scale means: depth of the core, not depth of the periphery.

## The block (three objectives — you design the phase decomposition)

### A. Household segments & customer psychology
A heterogeneous population of household archetypes replacing (or parameterising)
the current homogeneous customers. Dimensions to consider: dwelling type and
tenure, occupancy, income band / fuel-poverty status, payment method (DD /
prepay / on-receipt), tech adoption (smart meter, EV, heat pump, solar),
engagement level. Each archetype carries a psychology that the existing
mechanisms consume: price sensitivity / elasticity, switching inertia, channel
preference, complaint propensity, forgiveness buffer, bill-shock response.
**Anchored-noise law applies:** calibrate segment shares and behavioural
parameters to real published UK statistics (e.g. English Housing Survey, ONS,
Ofgem consumer-archetype research) via the discovery agent; register every
anchor in ASSUMPTIONS.md with provenance. Existing behavioural machinery (churn
journey, retention offers, NUDGE Layer 1, satisfaction) should become
segment-conditioned rather than population-uniform.

### B. Unhappy paths & time as a random variable (enforce the existing clause)
First audit, then build: sweep the estate for processes that currently execute
instantly and perfectly, and produce the violation list (candidates: bill
generation and delivery, meter-read arrival/failure/estimation, switching
timelines, payment failures and retries, refunds, contact-centre response
times, complaint acknowledgement). Then give the sim latency and error physics:
distributions on process times, failure/retry rates calibrated to real
data-quality statistics where anchors exist (registered in ASSUMPTIONS.md),
and — critically — the *company experiencing the consequences*: late bills,
estimated reads, missed SLAs feeding complaints, compensation where SLCs
require it. Epistemic wall unchanged: the company sees delays and errors only
as a real supplier would.

### C. The bill itself
A UK-domestic-compliant bill artefact, rendered properly on the customer
portal. It should withstand inspection by someone who has seen a real UK bill:
standing charge and unit rate split, VAT at 5%, actual-vs-estimated read basis
with meter serial/MPAN, billing period and consumption, payment method and
balance carried, back-billing limits where relevant, TDCV/annual-comparison
context. BILL_STRUCTURE_AND_DISCOVERY.md is prior art — reconcile with it
rather than restarting. Portal rendering follows the existing website design
laws (canonical CRM-style layouts, full UK lens). Bills produced under B's
physics (late, estimated, corrected) should look like what they are.

## Sequencing & economy
- You propose the phase decomposition (likely 2-3 phases; A and B may interleave;
  C can ride on either) — file it as the next phase(s) and proceed; no opt-out
  window needed, this instruction IS the direction. Order within the block is
  yours to argue.
- Token economy remains a P1 constraint (~50% weekly consumed, Wednesday). Sim
  runs for calibration should use SIM_FAST_MODE where possible; prefer the
  audit (B) and design/anchor-gathering work early since it is cheap.
- RY re-enters after the block, followed by the existing P-5 rank (NUDGE
  remainder, device-level price-response from the gap analysis, hedge grading
  when entries suffice, NBP gas pending Tier 1, per-event recosting, DCC at
  market-flows stage). Update PRIORITIES.md accordingly — it remains sole
  arbiter.

## Definition of done (per phase, R1 as ever)
Evidence on business surfaces per rule 0b: a named household on the Customers
tab whose segment and psychology visibly shaped a real event; a late/estimated/
corrected bill a reader can open on the portal; the sim tab showing a latency
distribution doing real work. Consumer-verified on deployed surfaces.

<!-- PHASE 1 ACTIONED 2026-07-08: phase decomposition filed at
     docs/design/CORE_FIDELITY_PHASES.md (4 phases: audits done this phase, then
     A/B/C implementation phases). PRIORITIES.md updated -- RY deferred (not
     cancelled), this block is now P1. Phase 1 (audits) completed and evidenced
     in the design doc: 5 confirmed unhappy-path gaps (meter-reads highest
     priority, refund processing found built-but-dead-code, bill-issue-lag,
     contact-centre response time, switching-funnel calendar spacing), household
     segment archetype design (dimensions + psychology parameters mapped to the
     existing mechanisms each would feed), bill-artefact gap audit against a real
     UK-bill checklist. Phases 2-4 (the actual implementations) are substantial
     multi-session work, not started this turn -- filed and queued, not claimed
     done. Doc archived here per the Staging Directory Protocol; the design doc
     is the live reference going forward, not this file. -->
