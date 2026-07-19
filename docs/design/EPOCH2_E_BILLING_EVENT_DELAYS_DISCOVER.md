# EPOCH-2 ATOM E — BILLING PHYSICS WITH REAL EVENT DELAYS (DISCOVER, doc-only)

**Status:** DISCOVER, doc-only. Provenance: **proposal**. **No level claimed.** Writes **no** `sim/`/`company/`/`saas/`/`harness/`
code, edits neither `maturity_map.yaml` nor any engine, touches only `docs/design/`. **W1 BUILD stays CLOSED** — this
campaign proceeds through DISCOVER/FRAME until the director opens it (`EPOCH_GATING_AND_ATOM_AUTHORSHIP` Rule 1). Isolated
worktree; no push; one commit.

**Source of task:** `docs/staging/in_progress/DIRECTOR_CAMPAIGN_EPOCH2_COUPLED_WORLD_2026-07-19.md` Ordering section —
"billing physics (including real event delays — estimated and late reads, settlement true-ups, the meter→cash lag)
sitting **downstream of usage**" — decomposed as atom **E** in `docs/design/EPOCH2_COUPLED_WORLD_CAMPAIGN_DECOMPOSITION.md`.

**No network this session.** Every external market/regulatory fact is flagged **`[recall — verify at BUILD]`**. Historical
Ground Truth forbids fabricating a specific date/figure in a DISCOVER doc; structural claims are stated as structure, and
anywhere a number would be load-bearing it is flagged, not invented. Repo figures below are quoted from code/committed docs
read this session (file + line/constant cited).

**Relationship to prior work — this atom CONSOLIDATES and COUPLES, it does not re-derive.** Three of the four delay stages
already exist as separate, landed mechanisms. Atom E's distinct deliverable is (a) the **single explicit delay chain**
meter→bill→cash that no doc currently owns end-to-end, and (b) the **coupled interaction** with atoms B/C/D — how a
weather-surge regime turns a physical event into a *delayed, uncertain financial* one, and the belief-vs-truth gap that
lag opens. It builds directly on:
- `simulation/meter_reads.py` (Phase 3) — read arrival/estimation/failure: smart-not-communicating rate, traditional
  actual-read cadence, estimate-from-trailing-actuals, SLC 31A forced catch-up. **Stage (a) of the chain already exists.**
- `simulation/settlement_timetable.py` (**W3_2_settlement_timetable**, SIM side) + `company/regulatory/settlement_reconciliation.py`
  (company side) — the R1/R2/R3/RF revision sequence on the bitemporal spine. **Stage (b) already exists, both sides of the wall.**
- The **payment triad** `D5_account_hierarchy_payments` (company belief) / `W4_4_payment_observable_seam` (the wall) /
  `W2_11_payment_behaviour_source` (SIM generator) / `H27_payment_belief_gap` (harness) — DD timing, failures, arrears
  ageing, the no-remittance blind spot. **Stage (c), the meter→cash tail, already exists as a live coupled triad.**
- `company/billing/back_billing.py` — Ofgem SLC 31A 12-month cap (from 2018-05-01), the legal ceiling on how far a late
  true-up can reach back.
- `EPOCH2_BC_PRICE_FORMATION_AND_SUPPLIER_COST_DISCOVER.md` — the supplier-cost = hedge-weighted-average finding and the
  volume-coupling hypothesis; §2 below is the *billing-lag* reading of that same imbalance/volume exposure.
- `EPOCH2_A_SCOPE_OF_NEED_SCORING_FRAME_DISCOVER.md` — the archetype×regime grid; §4/§6 tie the gap here to specific cells.

The `MATURITY_MAP.md` flow taxonomy already names three flows — `price_to_bill | meter_to_cash | close_to_learn`. **This
atom lives on `meter_to_cash`**: it is that flow's physics made explicit and coupled.

---

## 0. The one-paragraph idea

A real supplier delivers energy in an instant (the cold∧still half-hour) but **learns what it delivered, bills it, and
banks the cash over the following weeks-to-months**, and every step of that lag is both *delayed* and *uncertain*. The
volume is first **estimated** (from stale trailing history that cannot know a weather surge just happened), then **trued
up** across Elexon's R1→R2→R3→RF runs over ~28 months, and the cash then lags the bill again through DD timing, failure and
arrears. The company's books therefore carry a **provisional** position that firms up over time; the SIM knows the **true
settled** position immediately. **That difference, and its delay, is a measurable belief-vs-truth gap** — and it is exactly
in a weather-surge regime (the coupled world's dangerous cell) that the gap is largest and most adverse, because estimation
systematically *understates* a surge until the true-up lands. The delay is not an accounting nicety; it is a distinct
**exposure** — cash and hedge are carried against a number that is wrong in a known direction — and atom F must price it.

---

## 1. THE DELAY CHAIN, EXPLICIT — meter → bill → cash

The chain has three stages, each a real lag with its own cause, sign, and magnitude. The SIM already implements the
mechanism of each; this section states them as **one chain** and fixes the vocabulary the coupling (§2) and the gap (§4)
use. Read top-to-bottom; each `⏱` is a real lag, each `≈?` is a place BUILD must ground a number.

```
  ENERGY DELIVERED                                         (t0 — the physical half-hour; instantaneous, known ONLY to the SIM)
        │
        │  ⏱ (a) READ LAG + ESTIMATION            the company does not yet know the volume
        ▼
  READ / VOLUME OBSERVED           smart: near-real-time IF communicating; else ESTIMATED from trailing actuals
        │                          traditional: ~6-monthly actual; otherwise ESTIMATED
        │
        │  ⏱ (b) SETTLEMENT TRUE-UP               the volume the company DID observe is itself provisional
        ▼
  SETTLED VOLUME FIRMS UP          Elexon R1(~1mo) → R2(~3mo) → R3(~5mo) → RF(~28mo); each resolves a further share
        │
        │  ⏱ (c) BILL → CASH LAG                  the (still-provisional) figure becomes an invoice, then cash
        ▼
  CASH BANKED                      bill issue → payment terms → DD timing → failure/arrears/dunning → write-off
```

### 1.1 Stage (a) — READ delays: estimated vs actual, late, missing, the cadence
*(mechanism landed: `simulation/meter_reads.py`)*

| What | Value in repo | Anchor | Sign / effect |
|---|---|---|---|
| Smart meter "not communicating" this period | `SMART_METER_NOT_COMMUNICATING_RATE = 0.10` | DESNZ Q4 2024 Smart Meters Stats `[recall — verify at BUILD]` | falls back to estimation |
| Smart transmission delay (when communicating) | `SMART_METER_DELAY_MEAN_DAYS = 1.5` (expovariate) | near-real-time WAN+DCC | small |
| Traditional actual-read probability / month | `TRADITIONAL_ACTUAL_READ_PROBABILITY = 1/6` | ~6-monthly cadence, Citizens Advice `[recall — SLC 21A precise cadence UNVERIFIED, flagged in-module]` | else estimated |
| Traditional/self-read delay | `TRADITIONAL_DELAY_MEAN_DAYS = 9.0` | manual channel | late-read |
| On-time cutoff | `READ_CUTOFF_DAYS_AFTER_PERIOD_END = 5` | bill-gen cutoff | later ⇒ estimated then corrected |
| Estimate source | mean of `ESTIMATE_TRAILING_WINDOW = 3` own confirmed actuals | "based on your previous usage" | **backward-looking — cannot see a surge** |
| Forced catch-up cap | `MAX_CONSECUTIVE_ESTIMATED_PERIODS = 12` | SLC 31A back-billing | bounds the estimation run |

**The load-bearing property for the coupling:** an estimate is built **only** from the customer's own *prior* confirmed
actuals (the epistemic wall applied to billing — never from this period's true settlement figure). So the estimate is a
**lagged, smoothed** version of consumption. When consumption jumps (weather surge), the estimate lags **below** truth
until an actual read arrives — a **systematic, signed** under-statement, not zero-mean noise. This is the seed of §2.

### 1.2 Stage (b) — SETTLEMENT true-ups: Elexon Initial → R1 → R2 → R3 → RF
*(mechanism landed both sides: `simulation/settlement_timetable.py` (SIM) + `company/regulatory/settlement_reconciliation.py` (company))*

The **volume the company observed is itself provisional** — even a "confirmed actual" read feeds an industry settlement
figure that Elexon revises over a fixed run sequence, resolving a further share of the total adjustment at each run:

| Run | Months post-delivery (repo const) | Share of total gap resolved (repo const) | Cumulative |
|---|---|---|---|
| Initial | 0 (recognised at delivery) | — | provisional |
| R1 | `R1_MONTHS = 1` | `R1_SHARE = 0.60` | 0.60 |
| R2 | `R2_MONTHS = 3` | `R2_SHARE = 0.25` | 0.85 |
| R3 | `R3_MONTHS = 5` | `R3_SHARE = 0.12` | 0.97 |
| RF (Final Reconciliation) | `RF_MONTHS = 28` | `RF_SHARE = 0.03` | **1.00 (RF resolves the gap exactly; asserted at import)** |

Variance band (fraction of billed units potentially adjusted): **HH ±0.5%** (`HH_VARIANCE = 0.005`), **non-HH ±4.0%**
(`NON_HH_VARIANCE = 0.040`) — profile-class (resi/SME) firms up an order of magnitude looser than HH-metered I&C. Anchor:
Elexon Settlement Performance Reports `[recall — verify shares/months/bands at BUILD; the two constant sets are duplicated
across the wall by design and a test asserts they never drift]`. The figure is carried on the **bitemporal spine**
(`company/interfaces/bitemporal_event_log.py`): `valid_time` = the settlement day the figure is ABOUT; `transaction_time`
= each run's publication date. **What is estimated, when it trues up, the sign of the correction:** in a demand-*destruction*
regime (price spike → rationing) actual < estimated → **net credit** in late reconciliation (`settlement_reconciliation.py`
docstring, "crisis-year bias"); in a demand-*surge* regime the sign flips to **net charge** — see §2.

### 1.3 Stage (c) — the meter→cash lag: bill issue → DD timing → arrears/dunning
*(mechanism landed as a live coupled triad: D5 / W4_4 / W2_11 / H27; `simulation/arrears_engine.py`, `simulation/payment_seam_adapter.py`)*

The (still-provisional) figure becomes an invoice, and cash lags *again*:
- **Bill issue → payment terms → DD collection** — cash `value_date` is the **real clearing date**, which may be late,
  never the due date (`payment_seam_adapter.py`: a `RemittanceAdvice`'s `value_date` = `PaymentEvent.payment_date`).
- **Failure** — residential DD failure rises with income stress (`arrears_engine.py`: LOW 3% / MODERATE 12% / HIGH 35%
  DD-failure `[recall — verify calibration at BUILD]`); a failed **non-DD** payment produces **no remittance at all** (the
  C-S3 no-remittance blind spot the seam models — the supplier observes only the *absence* of expected cash).
- **Arrears / dunning delays** — `DD_FAILED → FIRST_NOTICE(+7d) → SECOND_NOTICE(+21d) → RESOLVED(+45d) | WRITTEN_OFF(+90d)`;
  I&C dispute path `INVOICE_DISPUTED → DISPUTE_NOTICE(+14d) → PAYMENT_PLAN(+30d) | WRITTEN_OFF(+60d)`; write-off then
  runs a further DCA placement/recovery tail. These are **weeks-to-months of additional cash lag** on the already-lagged
  billed figure, and they are **stress-conditioned** — the same regime that surges volume also raises failure.

**Net:** cash for energy delivered at `t0` in a surge half-hour is (i) first *understated* by estimation, (ii) *trued up*
over 1–28 months, and (iii) *collected* over a further stress-conditioned tail — three lags stacking, the first two firming
the *volume*, the third firming the *cash against that volume*.

---

## 2. WHY THE DELAYS MATTER TO THE COUPLED WORLD — the interaction with atoms B / C / D

This is the atom's reason to exist beyond bookkeeping. The delay chain does not sit beside the weather cascade; it is the
**financial back-end of it**, and it is *most wrong exactly where the cascade is most dangerous*.

**The mechanism, stage by stage, in a cold∧still surge regime** (the joint-tail cell of `W1_3_NATIONAL_WEATHER_JOINT_REGIME`
and the compounding tail of `W1_COUPLED_WEATHER_CASCADE`):
1. **Physics (atoms B/C/D):** cold∧still → residual-demand spike → wholesale price spike → the supplier's *incremental*
   volume (consumption above hedged quantity) is transacted **at the moment it is most expensive** (the B/C volume-coupling
   hypothesis, SUPPORTED for a hedged book). The cost is incurred **now**.
2. **Read lag (stage a):** the surged volume is billed on an **estimate built from pre-surge trailing actuals** →
   billed revenue **understates** the delivered (and paid-for) energy. The revenue that would offset the expensive
   incremental purchase **has not been recognised yet**, and is biased *low*.
3. **Settlement true-up (stage b):** the industry settlement firms up over R1→RF; because actual > estimated in a surge,
   the reconciliation direction is a **net charge/upward true-up landing months later** (sign flip of the
   `settlement_reconciliation.py` crisis-year *credit* bias — that doc models demand-*destruction*; a surge is the
   opposite). The supplier's true position was worse than its books showed *at the moment it most needed to know*.
4. **Cash lag (stage c):** the same surge regime is when affordability stress is highest (bill shock → arrears), so the
   understated bill is *also* collected slowest / partially / not at all — the cash tail lengthens precisely when the cost
   was front-loaded.

**The exposure this creates (distinct from price exposure, distinct from volume exposure):** the delay **converts a physical
event into a delayed, uncertain financial one**. Between `t0` and RF the company carries:
- a **hedge/collateral position sized against a volume it has under-observed** (it hedged/valued to an estimate that a
  surge just invalidated) — a *timing* mismatch on top of the *price/volume* mismatch B/C already price;
- a **provisional P&L that will be revised adversely** with a lag of up to 28 months (the true-up is a known-direction
  future charge in a surge);
- **working-capital drag** — cash out (expensive incremental energy, now) leads cash in (understated bill, collected late)
  by the full chain length.

**Why atom F (value ranking) must price it:** this is a **fourth, orthogonal** axis of belief-vs-truth error alongside
price-formation (B), cost-geography (C), and cascade-correlation (D). Two suppliers with *identical* price and volume
models can differ materially in exposure purely by **how lagged and how biased their billed-vs-settled position is** — and
the lag's cost is **regime-sensitive and one-directional in a surge**, which is exactly the joint-tail behaviour the
director's requirement 4 says dominates. A value model blind to the delay under-prices its worst cell (A1
affordability + surge, per the scoring frame). **Being wrong here is *not* cheap** — so it should rank high in F's
exposure-weighting, which is the point of measuring the gap (§4).

---

## 3. CANDIDATE INVARIANTS (R10 — NO code; class-level, R15-failable)

Per R10 an absurdity-class defect closes only by extending the invariant library so the *whole class* fails; per R15 each
invariant is stated with the **mutation** that must make it fire. These are **candidates for BUILD**, not asserted here.

**INV-E1 — Provisional-then-trued (ties to R14 clock-truth).** Any billed/settled position for a delivery period carries a
**settlement basis** (`provisional | initial | R1 | R2 | R3 | RF`) and its value may only *converge* toward the true
settled value across the run sequence — cumulative share resolved is monotone non-decreasing and reaches exactly 1.0 at RF.
*Ties to:* R14 (no financial figure without its clock) and the existing `settlement_timetable` share-sum assertion; the
`AmountDue.v1` seam already mandates a `basis` field (`GO_LIVE_SEAM_AND_INTERNAL_SEAMS_DESIGN.md`).
*R15 mutation:* emit a settled figure with **no basis** → gate RED; emit a later run whose cumulative share **< an earlier
run's** (non-monotone / un-firms) → RED; make RF resolve to ≠ true value (shares not summing to 1) → RED. Fail-open guard:
a **missing** basis must FAIL (an absent clock is a defect), not pass.

**INV-E2 — Cash lags delivery by a defined, regime-sensitive lag.** For every delivered period, `cash_banked_date ≥
bill_issue_date ≥ read_observed_date ≥ delivery_date`, and the *distribution* of the meter→cash lag **widens** (mean and
tail) as income-stress / surge regime rises — cash may **never** be recognised at or before delivery.
*R15 mutation:* inject a payment whose `value_date` = due date rather than real clearing date → RED (the
`payment_seam_adapter` already forbids this in prose; the invariant makes it fail); inject a regime where the stressed-cohort
lag distribution is **not** wider than the calm cohort → RED (guards the coupling being silently dropped).

**INV-E3 — Estimated reads systematically mis-state a weather surge until true-up (signed, not zero-mean).** Across a
population in a surge regime, the mean signed error `(billed_estimated_volume − true_delivered_volume)` is **negative**
(understatement) and closes only when an actual read / settlement run lands; it is **not** a zero-mean noise term.
*R15 mutation:* replace the trailing-actuals estimator with a truth-peeking one (estimate = true volume) → the invariant's
"gap exists pre-true-up" clause goes RED (proves it was measuring a real lag); flip the estimator to a *forward*-looking
one that anticipates the surge → RED (proves the wall — an estimate that sees the future is the defect). Fail-open guard:
zero customers in the surge cell must **fail the frame as UNMEASURED** (per scoring-frame §3.4), not pass as "no error".

*(All three are **class** invariants — they fail for any period/customer/regime violating them, not an instance patch.)*

---

## 4. THE COUPLED-TRIAD GAP — belief (billed/estimated) vs truth (settled) over the delay

Per the COUPLED TRIAD doctrine: **SIM** knows the true settled position at `t0`; the **COMPANY** believes a
billed/estimated position that firms up over the chain; the **HARNESS** measures the belief-vs-truth GAP. The delay makes
this a **time-indexed** gap, which is its distinctive feature.

**Candidate headline metric — `settled_position_belief_gap`** (proposed name; a *ratio*, so per scoring-frame §3.5 it
carries **no** settled/billed/banked clock — it is *about* those clocks, not a financial figure):

> At a given as-of date `d`, for a cohort/cell, the gap is the **normalised absolute divergence between the company's
> believed position** (its books' billed/estimated figure as-of `d`) **and the true settled position** the SIM holds for the
> same delivery periods — normalised by the true settled magnitude. Reported as a **curve over `d`** (t0 → RF), whose
> **area** is the *lag-integrated* exposure and whose **t0 value** is the raw belief error before any true-up.

Companion per-dimension gaps (matching how `H27_payment_belief_gap` reports a headline + companions in
`coupled_gap_ledger.json`):
- **volume-estimation gap** — signed `(estimated − true)` volume pre-true-up (tests INV-E3; expected *negative* in a surge);
- **timing/convergence gap** — how long (and how much value) remains provisional at each as-of horizon (area under the curve);
- **cash-recognition gap** — reuse/extend `H27`'s detection + ageing gaps for the stage-(c) tail (do **not** re-measure;
  cite it), so E's *new* contribution is stages (a)+(b), and the triad's cash tail stays owned by the payment triad.

**Ledger shape (proposed, matches existing entries):** a `coupled_gap_ledger.json` key (e.g. `E_billing_event_delays`)
with `metric: "settled_position_belief"`, `gap` (normalised 0–1 or curve-area), `g0` (baseline = believe-the-estimate-forever,
never true up → gap = full divergence), `raw_gap`, `components` (per-run residual shares, per-regime signed error,
per-cell), `note`, `twin_atom_id`, `measured_at`, `run_git_commit`. **Baseline (g0) so the control can FAIL:** "company
never trues up / believes its t0 estimate permanently" → maximal gap; a company that firms up correctly across R1→RF drives
the gap down — a *mutation that stops the true-up* must move the measured gap up, or the metric is theatre (R15).

**The gap is the score** (COUPLED TRIAD): no world/SIM billing-delay depth reaches L3 until the company has been tested
against it and this gap measured; the company's billing-delay handling is complete only once it has faced a surge regime
that defeats its estimator. Report per digest + Proof door.

---

## 5. WALL / CURRICULUM + C-S CONSTRAINTS (requirement 5)

**The wall (requirement 5 — randomness behind the curtain).** The **true** reads, the **true** settled volume, and the
**generating** processes (which meters fail to communicate, which reads arrive late, the true reconciliation adjustment)
live in the **SIM**. The company sees only **estimated-then-actual observables in time** — a bill it issued, a remittance
that did or didn't arrive, a settlement run publication — and must **infer** its true position, imperfectly, exactly as a
real supplier does. The estimate is built **only from the company's own prior confirmed actuals** (`meter_reads.py`), never
from the true settlement figure — the wall applied to billing. The measured belief-vs-truth gap (§4) **is** the deliverable.

**C-S3 (asynchronous wall contracts) — this atom is a *native* C-S3 case, already modelled.** Request and response are
**separate events in time**: a read *request* (bill-gen) and the *actual read* are different timestamps; a settlement
*delivery* and each *run revision* are different `transaction_time`s on the bitemporal spine; a DD *collection* and its
*remittance/return* are separate events (the seam already does this — `W4_4`/`payment_seam_adapter`). **Build ONE mechanism,
not three:** the settlement timetable, the read arrival, and the payment seam are the **same async-in-time contract**
(the addendum's "C-S3 and A3_approval_interface are the SAME law"); atom E should express the delay chain on the **existing
bitemporal spine**, not a new latency mechanism. Also relevant: **C-S1** (event-arrival tolerance — a late/estimated read
is the canonical out-of-order event; company logic must age correctly when it arrives, as `payment_observation_consumer.py`
already does) and **C-S2** (idempotent replay — a re-published settlement run for the same `valid_time` must not double-count;
the bitemporal `transaction_time` supersession already provides this). **SIMPLICITY GUARD:** the spine + seam already
exist — this adds *discipline and coupling*, not architecture.

**Baseline vs director curriculum (R13).** The **baseline** delay physics — the R1/R2/R3/RF timeline, the ±0.5%/±4% bands,
the read cadence, DD-failure base rates — are **fidelity-to-reality** parameters, calibrated blind to company P&L, changed
only for realism (and only after the BUILD-time verification of the `[recall]` anchors below). **Curriculum** — *which*
delay/stress regimes the company lives through (a "settlement-shock scenario", a "mass-estimation winter", a widened
reconciliation band) — is the **director's** instrument: named, versioned, director-authored, never agent-tuned from
company outcomes. The **sign flip** of the reconciliation bias (credit in destruction, charge in surge) is a *baseline*
fidelity fact; *how often the surge regime occurs* is *curriculum*.

**Portability lens.** Keep the chain **basis-and-regime keyed**, not Ofgem/Elexon-hardcoded: the *shape* (estimate → true-up
→ collect) is universal to metered utilities; a second market swaps the run timetable and cadence behind the same
`meter_to_cash` flow. Log any Elexon-specific constant as a regime-keyed value, not an implicit global (portability debt if
not — remediation-on-touch, not speculative retrofit).

---

## 6. OPEN QUESTIONS / WHAT BUILD NEEDS (unresolvable here — network / data / director)

1. **Verify the settlement anchors `[recall — verify at BUILD]`:** R1/R2/R3/RF months (1/3/5/28) and shares
   (0.60/0.25/0.12/0.03), and the ±0.5% HH / ±4% non-HH variance bands, against **live Elexon Settlement Performance
   Reports**. The repo duplicates these across the wall with a drift test, but neither side has been re-fetched this
   session — they are inherited, not re-verified. *(No network in autonomous runs — needs a discovery-agent pass.)*
2. **The SLC 21A actual-read cadence** is flagged **UNVERIFIED** in `meter_reads.py` (the 1/6 monthly probability is a
   ~6-monthly-practice proxy from Citizens Advice, not the Ofgem SLC text). BUILD must ground the real cadence or keep it a
   registered simplification.
3. **The reconciliation-direction sign under a *surge*** — `settlement_reconciliation.py` models the crisis-year *credit*
   (demand destruction) bias; the surge *charge* bias (§2 step 3) is asserted here by symmetry and **must be evidenced**
   (is late reconciliation genuinely a net upward true-up in a cold-snap over-consumption event, or does demand response /
   estimation-catch-up damp it?). This is a load-bearing coupling claim, not yet data-backed.
4. **DD-failure and arrears-timing calibration** (LOW/MODERATE/HIGH 3/12/35%; the +7/+21/+45/+90d dunning cadence) is
   flagged illustrative in `arrears_engine.py` — BUILD needs real forbearance/collections timing anchors.
5. **Metric normalisation (director / A6 harness call):** is the headline `settled_position_belief_gap` the **curve area**
   (lag-integrated) or the **t0 value** (raw belief error), and is the population score the **worst-cell MAX** (per scoring
   frame §3.3) or a cohort aggregate? Same **harm-weighted-vs-equal-cell** values-call flagged for atom A applies —
   **director's**, not the agent's.
6. **Sequencing / where E's own gap harness homes:** the cash-tail gap is already `H27`'s; E's new gap (stages a+b) needs a
   harness twin atom — propose `couples_with` a new `H_settled_position_gap` (or extend `H27`'s companion set). Homing is a
   FRAME decision; **W1/BUILD stays closed** until the director opens it. This DISCOVER pass proposes the atom, no more.
7. **Upstream dependency (inherited from B/C):** the price engine's **~10× SSP miscalibration** (`W1_6`) is a hard
   dependency for any *magnitude* claim about the surge-regime exposure — the delay-chain *shape* is independent of it, but
   the *£ size* of the coupled exposure (§2) cannot be trusted until that is fixed.

---

*Epistemic wall intact (no company code reads SIM internals; the estimate is built only from the company's own prior
actuals). No figure fabricated — every external number carries a `[recall — verify at BUILD]` flag; every repo figure
cites its file/constant. Provenance: proposal. No level claimed. DISCOVER/FRAME only; W1 BUILD closed.*
