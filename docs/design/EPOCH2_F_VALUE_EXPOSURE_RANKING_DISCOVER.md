# Epoch-2 atom F — the VALUE / EXPOSURE RANKING (DISCOVER→FRAME, doc-only)

**Status:** DISCOVER/FRAME, doc-only. Provenance: **proposal**. **No level claimed.** Writes only
under `docs/design/`; edits neither `maturity_map.yaml`, `supervisor.py`, `coupled_triad.py`,
`generate_proof_data.py`, `CLAUDE.md` nor any engine — those are the orchestrator's/BUILD's landing
acts. This is **requirement 2** of the Epoch-2 coupled-world campaign
(`docs/staging/in_progress/DIRECTOR_CAMPAIGN_EPOCH2_COUPLED_WORLD_2026-07-19.md`): *"VALUE is the
arbiter of which gaps to close — not gap size … it may choose to be wrong in one area more than
another and only value can help it decide … the value cycle IS Epoch 2 itself, not something that
comes after."* Homed as atom **F** in `docs/design/EPOCH2_COUPLED_WORLD_CAMPAIGN_DECOMPOSITION.md`.
**W1 BUILD stays CLOSED.** Isolated worktree; no push; one commit.

**No network this session.** No £ figure or market number is fabricated (Historical Ground Truth).
The only empirical numbers cited are **already-committed live gaps** read this session from
`docs/observability/coupled_gap_ledger.json`, quoted as the measured inputs the ranking consumes;
every **exposure** weight is symbolic/provisional and flagged `[provisional — calibrate at BUILD]`
(the £-at-stake model, P(regime), and severity are BUILD outputs, not invented here, §6). Asserted-
not-estimated choices are registered as simplifications (R10).

**What this atom owns (and what it does NOT).** Atom A owns **scoring** (how wrong we are, worst
cell). Atom D owns the **estimated dependence strength** `L` that severity is built from. B/C own
the **£ cost physics** (`E[Δvol·spot]`). **F owns the one thing none of them own: the function that
turns a measured belief-vs-truth GAP into a RANKED fidelity-investment queue by weighting it by
EXPOSURE (value-at-risk) — so the company spends where being wrong is expensive and correctly
tolerates being wrong where it is cheap — and the bootstrap that lets that value model exist while
it is still being built.** Atom A §1.4 explicitly *reserved the population weight π for requirement
2*; atom D §5 explicitly *hands F the `L`-based severity*. This doc collects those handoffs into one
ranking.

---

## 0. The one-paragraph idea

A fidelity harness that ranks its own to-do list by **gap size** spends its next unit of work on
whichever cell is *most wrong* — which is not the same as whichever cell it is *most expensive to be
wrong in*. A 0.9 gap on a rare, cheap corner (being wrong about the DD business case for the
comfortable middle in a calm market) outranks a 0.3 gap on the affordability-stressed household in a
crisis (bill-shock → arrears → self-disconnect → bad debt + a compliance breach) — and that ordering
is **backwards**. The fix is to rank not by `gap` but by `gap × exposure`, where **exposure = the
value-at-risk if the company is this wrong, here** (£, or a defensible proxy). Then a **big gap in a
cheap corner ranks BELOW a small gap in an expensive one — which is the whole point** (requirement
2). The circularity the director names — *the company needs a value model to rank its own fidelity
investments, but the value model is itself being built* — is resolved not by deadlock but by a
**converging loop**: a crude, honestly-provisional exposure proxy is computable **today**, good
enough to get the *ordering* roughly right, and it **sharpens as the cascade fidelity it ranks
improves** (better P(regime) from atom D's `L`, better severity from B/C's covariance, better π from
the population-draw atom). The value model and the fidelity it prioritises get less wrong
*together*. **That loop is why value is Epoch 2 itself** — it is not a phase after the physics; it is
the mechanism that decides *which physics to deepen next*, and it runs concurrently with the
deepening.

---

## 1. THE RANKING FUNCTION — `priority = gap × exposure`

### 1.1 The function

For every measured belief-vs-truth gap — indexed **per coupled pair** `(w, c)` and, once atom A's
cells are populated, **per scoring-frame cell `(a, g)`** (archetype × regime) — the fidelity-
investment priority is:

```
priority(gap)  =  gap  ×  exposure
```

- **`gap`** — the **normalised** belief-vs-truth gap already in the codebase (`gap = raw_gap / g0`,
  COUPLED_TRIAD §1.2), read live from `coupled_gap_ledger.json`. Dimensionless; `1` = no better than
  blind; `>1` = worse than blind (so it *amplifies* priority — an actively harmful model in an
  expensive corner is correctly the top of the queue); `0` = perfect (a wall leak, §5, not a
  triumph). **F consumes the gap; it never recomputes or re-defines it** (independence, §4).
- **`exposure`** — the **value-at-risk if wrong here**, in £ (or a defensible proxy). Its
  decomposition is the heart of this atom (§1.2).

The queue is ordered by **descending `priority`**. Units: `priority` is `gap` (dimensionless) ×
`exposure` (£) = **£ of value-at-risk mis-served** — the queue is literally ranked by the £ the
company is putting at risk by being this wrong. That £-denomination is what makes heterogeneous gaps
(a classification gap, a detection gap, a cost-covariance gap) **comparable on one axis** — the same
role the `g0` normaliser plays for scoring, lifted to the spend decision.

### 1.2 EXPOSURE — value-at-risk, factorised (the four terms the campaign reserved for F)

Exposure answers *"how much money moves if the company's belief is wrong in this corner?"* It
factorises into the four terms the upstream atoms explicitly handed to F:

```
exposure(a, g)  =  π(a)·N        # HOW MANY are exposed   — population weight × book size (atom A §1.4, reserved for F)
                 × s(a)          # HOW MUCH each has at stake — £-at-stake per account (bill / bad-debt / feed-in / cost-to-serve)
                 × P(regime g)   # HOW LIKELY the dangerous state — regime probability, incl. atom D's joint-tail lift L
                 × κ(a, g)       # HOW BAD when wrong      — loss-given-wrong severity in this corner (atom D's E[Δvol·spot] / harm)
```

Term by term, with its source and its honesty tag:

| Term | Meaning | Source / who supplies it | Tag |
|---|---|---|---|
| **`π(a)`** | population weight of archetype `a` — how often the SIM draws this case | **Atom A §1.4, reserved for F.** Frequency. A5≈large, A3≈small. `π·N` = accounts of this type. | `[provisional — fixed ~31 cast until the population-draw atom W2_2 lands, §6]` |
| **`s(a)`** | £-at-stake **per account** if the belief is wrong: annual bill × at-risk fraction (A1 bad-debt), feed-in liability (A3), cost-to-serve mis-attribution (A2/A4) | Billing data + archetype populations (BUILD) | `[provisional — real bill/bad-debt/feed-in £ needed, §6; no figure fabricated]` |
| **`P(regime g)`** | probability the regime occurs — **and here atom D's `L` is load-bearing:** the joint-tail lift raises the corner mass above the naive independent product, `P(g) ≈ L · P_A · P_B` (atom D §4). G3 cold∧still is `2.34×` more probable than a marginal model believes (W1_3 anchor). | **Atom D §5.** A model that ignores `L` under-rates exactly the correlated tail that kills suppliers. | `[L directional; magnitude blocked on the capacity-weighted GB series + price-engine recalibration, §6]` |
| **`κ(a, g)`** | loss-given-wrong **severity** in this corner. For financial cells = the **£ covariance** `E[Δvol·spot]` in the joint tail (B/C §3, atom D's D3) — the money lost only where short-volume and spike coincide. For collections cells = the **harm** (customer-harm × compliance breach). | **Atom D §5 (severity) + B/C §3 (covariance) + COUPLED_TRIAD §1.4 (harm).** | `[covariance magnitude blocked on price-engine, §6; harm weights are DIRECTOR curriculum, §5]` |

**Atom D is load-bearing twice** (its own §5 says so): `L` scales both the *probability* of the
dangerous regime (`P(regime)`) and, via the D3 covariance, its *severity* (`κ`). So a link with a
high, well-estimated `L` and a large book concentration ranks **above** a link with a bigger raw gap
but a rare, cheap regime — which is exactly requirement 2's mandate.

### 1.3 The whole point — a big gap in a cheap corner ranks BELOW a small gap in an expensive one

This is not a side-effect; it is the design objective, and it must be stated so BUILD cannot lose it.
Worked illustration using the **real live gaps** (from `coupled_gap_ledger.json`, this session) with
**exposure shown symbolically** (magnitudes are BUILD outputs, not invented — the *ordering flip* is
what the illustration demonstrates, and it is robust to the exact £):

- **`W2_10 ⇄ C12` DD-attribution gap = 0.516** (a **large** gap: over half the DD business case is
  selection artefact). But evaluate it in the cell it most naturally lives in — the **comfortable
  DD-paying middle (A5) in a calm/soft market (G1)**: `π` large but `s` low (calm market, being wrong
  about the DD channel's causal credit is cheap — no one is failing), `P(regime)` for G1 is the
  common baseline, `κ` small. → **exposure LOW → priority LOW.**
- **`W2_11 ⇄ D5` payment-failure detection gap = 0.297** (a **smaller** gap: the no-remittance blind
  spot misses ~30% of true failures). But evaluate it on the **affordability-stressed household (A1)
  in a crisis (G2)**: `s` high (a missed failure → arrears → bad debt + a self-disconnect harm +
  a possible compliance breach), `P(regime)` in a director-authored crisis is elevated, `κ` high
  (the harm term). → **exposure HIGH → priority HIGH.**

**Result: `priority(W2_11 @ A1×G2) > priority(W2_10 @ A5×G1)` even though `0.297 < 0.516`.** The
smaller gap wins the next unit of fidelity work, because being wrong there is expensive. That
inversion — gap-size ordering overturned by exposure — **is the deliverable.** (Note this is *also*
why atom A's cell frame is F's necessary input: the *same* pair evaluated in a different cell gets a
different exposure — `W2_11` on A5@G1 would rank low — so the ranking is cell-resolved, not pair-
flat. F cannot rank without A's grid.)

### 1.4 Refinement — rank the CLOSEABLE gap, not the raw gap (and why it's only a refinement)

Some gaps are **structurally irreducible**: the observable channel is strictly coarser than the
hidden truth, so the gap **cannot reach 0** without a wall leak. The ledger already records this —
`W2_4 ⇄ C6`: *"Non-zero and NOT recoverable to zero … managing vs comfortable are indistinguishable
from payments."* Spending fidelity budget trying to close a gap below its wall-imposed floor is burnt
budget: you invest and the number does not move. The sharper ranking weights the **reducible**
portion:

```
priority(gap)  =  exposure  ×  (gap − gap_floor)          # gap_floor = the irreducible, wall-imposed gap
```

where `gap_floor` is the information-theoretic floor (the residual gap a *perfect* observable-only
model still carries because observables are coarser than `θ`). This correctly deprioritises a
high-exposure gap that *cannot be closed anyway* in favour of one of similar exposure that *can*.
**But it is a refinement, not the primary function, and it is deliberately fail-toward-investigate:**
`gap_floor` is itself hard to estimate (§6), and *over*-estimating it would silently deprioritise a
genuinely closeable gap. So BUILD ships `priority = gap × exposure` **first** (crisp, mutation-
testable, `gap_floor = 0`), and only introduces `gap_floor` per-pair once it is independently
estimated — and where `gap_floor` is unknown it defaults to **0** (rank the full gap → over-invest,
the safe direction), never to the gap itself (which would zero the priority — the unsafe direction).

---

## 2. THE DELIBERATE CIRCULARITY — bootstrap, don't deadlock

**The circularity, stated plainly.** To rank fidelity investments by value-at-risk, the company needs
a **value model** (the exposure decomposition above). But that value model is *built from the very
cascade fidelity it is meant to rank* — `P(regime)` needs atom D's `L`, `κ` needs B/C's covariance,
`s` and `π` need the populated archetypes. The thing that decides what to build depends on what has
been built. A naive reading calls this a chicken-and-egg deadlock. It is not — it is a **fixed-point
iteration**, and resolving it is *why the value cycle is Epoch 2 itself*.

### 2.1 The bootstrap — a minimal, honestly-provisional exposure proxy (`exposure_v0`)

`exposure_v0` is computable **today from committed artefacts**, wrong in magnitude but usable in
*ordering*:

```
exposure_v0(a, g)  =  accounts_v0(a)  ×  s_v0(a)  ×  P_v0(g)  ×  κ_v0(a, g)
```

- **`accounts_v0`** = `π · N` from the current fixed cast (`simulation/segments.py`) — provisional,
  labelled (the real fix is W2_2, §6). Ordering across archetypes is already meaningful.
- **`s_v0`** = a **crude constant per archetype** — e.g. annual bill × a flat at-risk fraction, or the
  cost-to-serve band the break-even assessor already computes. Flagged **asserted** (R10). Wrong in
  £, but A1's bad-debt exposure > A5's cleanly-paying exposure is already the right *sign*.
- **`P_v0`** = the **naive marginal** regime frequency (independent product, `L = 1`) — deliberately
  the *pessimistic-for-the-proxy* choice: it under-rates the correlated tail, which the loop then
  corrects upward as atom D lands (§2.2). Labelled provisional.
- **`κ_v0`** = a **flat severity** (or the qualitative harm rank from the COUPLED_TRIAD harm-matrix
  placeholders) — improved to the D3 covariance `E[Δvol·spot]` as B/C and D land.

`exposure_v0` need only be good enough to get the **ordinal** answer roughly right (*which* corner is
expensive), not the **cardinal** £. **Ordinal correctness bootstraps far faster than cardinal** — you
do not need the exact £-at-risk to know that a failing household in a crisis outranks a comfortable
one in a calm market. That is the crux: the loop *starts* from a proxy that is admittedly wrong in
magnitude but right in rank.

### 2.2 The converging loop (not a deadlock)

```
   ┌───────────────────────────────────────────────────────────────────────┐
   │  exposure model (v_n)                                                   │
   │        │  ranks →                                                       │
   │        ▼                                                                │
   │  fidelity-investment queue  ──►  build the top item  ──►  cascade       │
   │                                     fidelity improves:                  │
   │        ▲                              • better L  (atom D)  → P(regime)  │
   │        │  feeds back                  • better covariance   → κ          │
   │        │                              • populated archetypes→ s, π       │
   │  exposure model (v_{n+1}) ◄──────────────────────────────────────────────┘
```

Each cascade-fidelity improvement **feeds back into a better exposure model**, which **re-ranks** the
queue, which **directs the next investment**. The exposure model and the fidelity it ranks improve
*together* — a fixed point approached iteratively, not a chicken-and-egg standstill. **Why it cannot
deadlock:** `exposure_v0` is computable before *any* cascade improvement (§2.1), so the loop has a
starting point that needs nothing it is waiting on. **Monotone-improvement claim (the honest
version):** as each input sharpens (`L` replaces the naive marginal, covariance replaces flat
severity, real £ replaces the constant), the ranking's **regret** — the count of mis-ordered
investments vs the true value ordering — is *expected* to fall; it is not *proven* to fall (§2.3).

### 2.3 Convergence caveat (R4 honesty — do not tune it away)

The loop is **endogenous**: closing a gap in one corner can change the *relative* exposure landscape
(a fixed corner is no longer at risk, so another rises to the top). This risks **oscillation** — a
queue that thrashes cycle-to-cycle. Two honest disciplines, not a suppression:

- **Re-rank on a cadence, not on every measurement** — per-digest, matching COUPLED_TRIAD's existing
  transition cadence — so a single noisy gap does not reorder the whole queue.
- **Monitor rank-stability across cycles.** A *thrashing* queue is a **FINDING** (R4: diagnose the
  mechanism — is it noise from the small cast? genuine endogeneity? a mis-scaled term?), **never** a
  cue to damp the ranking toward a stable-but-wrong order (that would be goal-seeking rank-stability,
  R12). There is no guarantee of a unique fixed point; the honest output is *"the queue is stable"*
  or *"the queue is thrashing — here is why."* Setting the static-vs-thrashing threshold needs a real
  multi-cycle run's noise floor (§6), exactly as COUPLED_TRIAD's static-gap threshold does.

---

## 3. "CHOOSING TO BE WRONG" — formalised (and kept strictly out of the score)

The director: *"it may choose to be wrong in one area more than another … being materially wrong
where wrongness is cheap is a correct allocation, not a defect."* Formalised:

### 3.1 The "do-not-invest" output state

Define an **investment threshold `τ`** (a £ floor). A cell/pair with:

```
priority(gap)  =  gap × exposure  <  τ
```

is labelled **"ACCEPTABLY WRONG HERE — DO NOT INVEST"**: the value-at-risk from being this wrong is
below the cost of closing it. This is a **first-class, explicit output** of the ranking — a legitimate
allocation decision, **not** a failure and **not** a defect. The ranking must be *able* to emit it
(and BUILD must surface it as an explicit state, never as a silent omission from the queue — an
omitted item is invisible; a "do-not-invest, priority £X < τ" item is an auditable decision).

### 3.2 The load-bearing reconciliation with atom A's worst-cell rule (the two must NOT be conflated)

Atom A §1.4 already drew this line — *"scoring says how wrong we are everywhere; value says which
wrongness to buy down first"* — and F must honour it exactly, because conflating them is the
anti-pattern that would corrupt the fidelity score:

| | **SCORING (atom A — worst-cell MAX)** | **VALUE (atom F — exposure-weighted queue)** |
|---|---|---|
| **Question** | *How wrong are we, everywhere?* (capability honesty) | *Where do we spend to get less wrong?* (allocation) |
| **Weight** | every in-grid cell counts **equally**; `π`/exposure **excluded** (A §1.4) | cells weighted by **exposure** = `π × s × P × κ` |
| **A cheap-corner blindness** | **stays RED in the worst-cell surface** — capability is not for sale | **can sit at the bottom of the queue** (correctly deprioritised for spend) |
| **Owns** | the fidelity SCORE (`MAX` gap) | the fidelity-work QUEUE (spend order) |

The critical discipline: **"acceptably wrong here — do not invest" is a statement about the
INVESTMENT QUEUE, NEVER about the FIDELITY SCORE.** A cheap-corner gap the ranking chooses not to fix
**stays visible and red** in atom A's worst-cell surface, the digest, and the Proof door. Value
removes it from the *spend* ranking; it does **not** suppress the *score*. So "choosing to be wrong"
must NOT count against the fidelity score inappropriately — and it doesn't, because the score is atom
A's, **computed blind to exposure**. This is the requirement's exact clause satisfied structurally.

### 3.3 The two axes can disagree — and that is fine (publish both)

Worst-cell scoring (A) and value-ranking (F) can even name **different** cells as "the one to look
at": A says *"our worst-explained cell is A2@G3"* (the biggest gap — capability truth); F says *"our
top fidelity investment is A1@G2"* (the biggest `gap × exposure` — value truth). **No conflict —
different axes, both published.** The director sees both surfaces and reads them together: *"we are
this wrong here (A), and we are choosing to fix that one first because it is expensive, and to
tolerate this other one because it is cheap (F)"* — an explicit, auditable allocation.

### 3.4 The anti-pattern this guards (stated for BUILD)

**Using "value says it's cheap" to silence a red cell in the score** — declaring the hard cells cheap
to make the worst-cell number look good. **Forbidden.** The score is atom A's, computed *blind to
exposure*; F only orders the *fixing* and publishes *both* surfaces. A ranking that fed its "do-not-
invest" verdict back into the *score* (dropping the cell from the `MAX`) would be goal-seeking the
score (R12) and is exactly the FAIL-OPEN defect atom A §3.4 already forbids. F reads the score; it
never writes it.

---

## 4. CANDIDATE MECHANISM / INVARIANTS (R10-class, R15-failable, NO code)

Stated in the class-failing style. **No level claimed; provenance: proposal.**

> **INVARIANT F-1 (the queue is ranked by exposure-weighted gap, re-derived each cycle from the LIVE
> gap ledger + a LIVE exposure model — never by raw gap).** The fidelity-work queue's order must be a
> function `priority = gap × exposure` computed **fresh each cycle** from (a) the current
> `coupled_gap_ledger.json` gaps and (b) the current exposure model (`π`, `s`, `P(regime)` incl. atom
> D's `L`, `κ`). A queue whose order is **invariant to exposure** — i.e. reproduces the raw-gap
> ordering — **FAILS.** (Class: *any* ranking that ignores value-at-risk mis-prioritises a cheap-
> corner gap above an expensive one — the exact defect requirement 2 forbids. An instance fix — "we
> re-ordered these two" — does not close it; the invariant makes the whole class fail, R10.)

> **INVARIANT F-2 (an UNMEASURED gap with HIGH exposure ranks as a TOP INVESTIGATE — fail-closed).** A
> cell/pair whose gap is *unmeasured* but whose *exposure* is high must rank at the **TOP** of the
> queue as *"investigate — measure this gap first,"* **NEVER** drop out for lack of a gap number.
> `gap = untested` in a high-exposure cell → `priority = exposure × gap_max` (a top-severity gap
> placeholder). This mirrors atom A §3.4's unmeasured-cell FAIL-OPEN guard, lifted to value: *a
> missing measurement in an expensive corner is the most dangerous state* — you do not know how wrong
> you are exactly where it is most expensive to be wrong — so it must **fail toward investigation**,
> not toward silent omission. (Directly relevant today: atom A's **A3 export/self-gen** cells are
> unmeasured — no coupling registered — and a prosumer's feed-in liability is real £ exposure; F-2
> ranks them TOP-investigate, not zero.)

**R15 — the ranking is a control that must be able to FAIL (mutation directions, designed not coded):**

- **The killer mutation (F-1's named defect).** Construct two candidate gaps: `gap_A = 0.9` in a cheap
  corner (`exposure ≈ ε`) and `gap_B = 0.2` in an expensive corner (`exposure ≈ big`). A **raw-gap**
  ranker puts A above B (the bug — it sends fidelity budget to the cheap corner). The **exposure-
  weighted** ranker puts B above A (`priority_B = 0.2·big > priority_A = 0.9·ε`). **That divergence
  IS the R15 proof** the control fires on its named defect ("ranks by gap size, ignores exposure").
  BUILD ships it as F's mutation test. Symmetric mutation: mark the high-exposure cell "untested" and
  confirm F-2 lifts it to the TOP (the fail-closed guard fires), not drops it.
- **TAUTOLOGY guard.** `exposure` is computed from **independent** inputs (population draw, billing £,
  weather-record `P(regime)`, the harm-matrix) — **never read back from the gap it weights**, and
  never from a stored "designed rank." A ranker that derived exposure *from* the gap (so `priority ∝
  gap²`) is a tautology and fails independence. (F consumes the ledger gap read-only; it never
  recomputes `θ`/`b`.)
- **FAIL-OPEN guard.** A **missing** exposure input (no `π`, no `s`, NaN `P(regime)`) must **NOT**
  default the cell to **zero** priority — that would silently drop an expensive corner. It must fail
  toward **TOP-investigate** (F-2). Zero/empty/missing/malformed exposure → top of queue, not bottom.
- **FAIL-SILENT guard.** If the gap ledger **or** the exposure model is **unavailable**, the ranking
  is a **FAILED** computation (surfaced as such), **never** a stale-but-green queue — an unavailable
  ranker is a failed ranker.

A single reusable `priority = gap × exposure` + a single reusable mutation ("strip exposure → the
cheap corner floats to the top → the control fires") is the mechanised core the whole value cycle
rests on.

---

## 5. WALL / CURRICULUM (R13, requirement 5) + portability

### 5.1 Exposure is the company's OWN model — and mis-judging it is itself a gap (the reflexive point)

The company estimates its **own** value-at-risk from **observables only** — its own book, its own
bills, its own inferred regime probabilities. It does **not** read the SIM's true exposure. A supplier
that **under-estimates its own tail exposure** — believes a corner is cheap when it is actually
expensive, e.g. prices its volume-error at *average* spot and so erases the D3 covariance and *thinks
G3 is cheap* (the exact B/C §3 anti-pattern) — **mis-ranks its own fidelity investments and under-
invests precisely where it will be killed.** That mis-estimation is a **second-order coupled gap**:
belief-vs-truth on *exposure itself*, not just on the underlying physics. So **F is itself
couple-able** — SIM-true exposure (harness-side) vs company-believed exposure (observable-side), and
the delta is a score. This is the deep reflexive reason the value cycle is Epoch 2 itself: *the
company's value model is one more thing it discovers imperfectly through the wall.* Registered as a
candidate coupled pair for BUILD (§6).

### 5.2 The harm-weighting of "expensive" is a DIRECTOR values/curriculum call (R13) — do not invent it

What makes a corner "expensive" — the £ weight on **customer-harm vs company-loss**, the `τ`
"do-not-invest" threshold, the relative weight of a vulnerable-customer harm vs a margin loss — is
**not a physics fact.** It is a values decision about *what the company is FOR* (one-way-door
category 6, director-reserved). It is the **same class** as the COUPLED_TRIAD harm-matrix `C[q, q̂]`
(already flagged director-authored, versioned) and atom A's harm-weighted-vs-equal-cell open question.
**Do not invent the weights.** The split, precisely:

- **The exposure STRUCTURE** — the factorisation `π × s × P × κ`, and the *estimation* of `π`, `s`,
  `P(regime)` — is the **company's** to build and to get wrong (§5.1). Baseline: `π`, `s`, `P` are
  estimated from reality (or the SIM record), decided **blind to company P&L**, changed only for
  fidelity reasons (R12/R13).
- **The harm WEIGHTS inside `κ`** and the `τ` threshold — the numbers that turn a physical loss into a
  "how much we care" — are the **director's**, because the agent controls both sides of the wall:
  agent-set harm weights would let the agent goal-seek its own value ranking (declare the cells it
  cannot fix "cheap"), which R13 forbids. Ship the ranking **with placeholder weights and a director
  sign-off gate**; the £-severity of harm faces the director exactly because the estimator is shared.

### 5.3 Portability / scale

- **Function-keyed, not GB-keyed.** `priority = gap × exposure` carries no GB or fuel-specific term; a
  second market re-derives its own `π`, `s`, `P(regime)` behind the same four-term structure. `τ` and
  the harm weights are per-regime director curriculum, not hardcoded.
- **Percentile-keyed regimes** (inheriting atom A/D): `P(regime)` uses tail quantiles of the realised
  distribution, so a second geography re-derives its own corners without absolute £/°C/m·s⁻¹.
- **C-S2 (idempotent replay).** The ranking is a **pure function** of (ledger snapshot, exposure-model
  snapshot) — re-running a cycle on the same inputs reproduces the identical queue; no wall-clock, no
  unseeded draw in the ranking itself. The re-rank cadence (§2.3) is event-driven (per-digest), not a
  hidden timer.
- **SIMPLICITY GUARD.** This is a ranking *function over two existing data surfaces* (the gap ledger +
  an exposure model), not an architecture — no ranking-engine cathedral. It reads the map/ledger and
  emits an ordered list, the same "read, don't invent" pattern the Proof-door `_coupled_gaps` helper
  already uses.

---

## 6. OPEN QUESTIONS / what BUILD needs (unresolvable here — network / data / director)

1. **The £-at-stake-per-account model `s(a)` (the biggest data gap).** Real bill sizes, bad-debt
   exposure per affordability band (A1), **feed-in liability** (A3), cost-to-serve mis-attribution
   (A2/A4). Needs billing data + the archetype populations — and atom A §5.3 **S3** flags that A2/A3
   are *not yet populated by the SIM cast*, so their `s` is a scoring-slot awaiting a population.
   Route via the discovery-agent at BUILD; **fabricate no figure** meanwhile.
2. **`P(regime)` with atom D's joint-tail lift `L`.** Depends on D's estimated `L` per link, itself
   blocked on the **capacity-weighted GB wind-output series** and the **price-engine ~10× SSP
   recalibration** (D §7, B/C §6). Until then `P(regime)` is the **naive marginal** (`L = 1`), labelled
   provisional; the *direction* (correlated tail is under-rated) is robust, the *magnitude* waits.
3. **Severity `κ` = the D3 covariance `E[Δvol·spot]`.** Blocked on the same upstream (price-engine
   miscalibration + `sim/hedging.py`'s single-`hedge_price` collapse of the forward book, B/C §6). The
   £ size of the volume×price interaction is a BUILD output, **reported not tuned** (R12).
4. **The harm weights inside `κ` and the `τ` "do-not-invest" threshold — DIRECTOR values call (R13,
   one-way-door category 6).** Placeholder weights + a sign-off gate only; the agent must not invent
   them (§5.2). Mirrors the COUPLED_TRIAD harm-matrix and atom A's equal-vs-harm-weighted open
   questions — the **same** director decision, surfaced once.
5. **The `gap_floor` refinement (§1.4).** Estimating the irreducible, wall-imposed floor per pair (the
   "gap cannot reach 0" bound, e.g. `W2_4 ⇄ C6`'s recorded non-recoverability) needs each pair's
   information-theoretic coarsening analysis. Ship `gap_floor = 0` first (over-invest = safe
   direction); introduce per-pair floors only once independently estimated; **never** default an
   unknown floor to the gap itself (would zero the priority — unsafe).
6. **Rank-stability / convergence monitoring (§2.3).** The endogeneity/oscillation risk needs a real
   multi-cycle run to observe; the static-vs-thrashing threshold needs the noise floor (R4, and it is
   the same small-cast power limiter COUPLED_TRIAD §6 and atom A §6 flag — the real fix is population
   volume via W2_2, not a ranking tweak).
7. **The second-order exposure coupling (§5.1) — a candidate NEW coupled pair for BUILD to register.**
   SIM-true exposure vs company-believed exposure. Needs the SIM-true exposure computable harness-side
   and a `loss(·)`/`g0` for the exposure-belief gap (a belief-error/TV form over the exposure vector is
   the natural first shape). Off-front until the director opens W1.
8. **`π` (population weight).** Currently the fixed ~31-account cast; the real fix is the population-
   draw atom **W2_2** (L0). Until then `π` is provisional/directional, labelled — the same limiter atom
   A §6.2 records.

---

*Sources read/reasoned this pass (no network): `docs/staging/in_progress/DIRECTOR_CAMPAIGN_EPOCH2_
COUPLED_WORLD_2026-07-19.md` (requirement 2 — value-as-arbiter, "choose to be wrong", the deliberate
circularity / "value cycle IS Epoch 2"; read directly); `docs/design/EPOCH2_COUPLED_WORLD_CAMPAIGN_
DECOMPOSITION.md` (atom F homing + deps: A frame, the gap ledger); `docs/design/EPOCH2_A_SCOPE_OF_
NEED_SCORING_FRAME_DISCOVER.md` (§1.4 — π reserved for F, exposure = π × harm-per-unit × gap, the
scoring-vs-value distinction; the worst-cell rule F reconciles with; A3-unmeasured / equal-weight
open questions); `docs/design/EPOCH2_D_CASCADE_CORRELATION_ESTIMATION_DISCOVER.md` (§5 — the L-based
severity handed to F; exposure(regime) ≈ P(joint) × severity × book-concentration; L load-bearing
twice; D1 decile L=2.34×; upstream blockers); `docs/design/EPOCH2_BC_PRICE_FORMATION_AND_SUPPLIER_
COST_DISCOVER.md` (§3 — the E[Δvol·spot] covariance as the severity object; the average-spot anti-
pattern that makes a supplier under-rate its own exposure; hedge-floor 0.85); `docs/design/COUPLED_
TRIAD_DESIGN.md` (§1.2 gap=raw_gap/g0 normalisation; §1.4 harm-matrix C[q,q̂] as director curriculum;
§5 digest + Proof-door reporting incl. the R15-failable _coupled_gaps panel and anti-decay counts —
F's publish surface); `docs/observability/coupled_gap_ledger.json` (the LIVE measured gaps F ranks:
W2_10/C12 attribution 0.516, W2_11/D5 detection 0.297, W2_4/C6 belief 0.606 [recorded non-
recoverable], W2_6/C8 0.475, W2_7/C9 0.128, W2_8/C10 0.309, W2_9/C11 0.229, W2_5/C7 0.008);
`tools/couple_w2_11_d5.py` (how a gap is measured/written — the read-only surface F consumes). Every
exposure magnitude is provisional, flagged for BUILD calibration; no £ or market figure fabricated
(Historical Ground Truth). R10/R12/R13/R15, COUPLED_TRIAD, one-way-door category 6, C-S2, SIMPLICITY
GUARD, portability, and the epistemic wall referenced inline. Provenance: proposal; no level claimed.*
