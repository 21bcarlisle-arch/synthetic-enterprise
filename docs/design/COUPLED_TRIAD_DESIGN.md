# COUPLED_TRIAD — design (Lane-3, doc-only)

**Status:** DISCOVER/FRAME design output for `docs/staging/THE_COUPLED_TRIAD.md` (P1,
director-decided QUEUE-rank-high). This document designs the belief-vs-truth **gap
metric**, the affordability-cluster couplings (W2_4–W2_10), the **level-definition
amendment**, the **draw-coupling** mechanism, and **gap reporting** (digest + The Proof
door). It writes **no code**, edits neither `maturity_map.yaml` nor `supervisor.py` nor
`CLAUDE.md` — those are the orchestrator's/BUILD's landing acts. Everything below is
specified to be implementable against the *existing* three-lane draw and proof-door
pipeline, per the SIMPLICITY GUARD (add discipline, not architecture).

**Author's confidence tagging:** formulae and field names are proposals; where a design
choice is genuinely open (a normaliser, a harm weight) it is flagged in §6 Open Questions
rather than asserted as settled.

---

## 0. The idea in one paragraph (restated so this doc stands alone)

Every capability advances as a **three-part loop**: (1) the SIM adds depth (a hidden
mechanism — household budgets, life events, willingness, self-rationing, channel
migration); (2) the COMPANY must **discover and cope** with that depth **through the wall
only** — missed payments, broken plans, disclosure, observable behaviour — and it must be
**allowed to be wrong**; (3) the HARNESS measures the **gap** between the SIM's hidden truth
and the company's belief/action. **The gap is the score.** Depth nobody has to cope with is
scenery. A collections engine never shown a household that cannot pay is untested. This
design makes those two facts *structural* (level definitions + draw + a first-class metric),
not exhortations.

---

## 1. The belief-vs-truth GAP metric

### 1.1 General shape

For a **coupled pair** `(w, c)` — a world/SIM atom `w` and its company-response atom `c` —
evaluated at a point in the run over a population `P` of entities `i` (accounts, meter
points, businesses):

```
raw_gap(w, c) = (1 / |P|) · Σ_i  loss( θ_i , b_i )
```

- `θ_i` — the **hidden truth** for entity `i`, read SIM-side from `data_regime="synthetic"`
  ground state (`simulation/household.py`, `life_events.py`, `arrears_engine.py`,
  `household_segments.py`, …). This is the answer key.
- `b_i` — the company's **belief or action** for `i`, computed **only** from observables
  that crossed the wall (`company/interfaces/sim_interface.py`): payment history, plan
  adherence, disclosure, consumption analytics. Never a read of `θ`.
- `loss(·,·)` — a per-entity divergence appropriate to the pair (0/1 misclassification,
  absolute/relative error, set-membership miss, distribution distance).

### 1.2 Normalisation — make gaps comparable and trends meaningful

A raw gap in "cost units" or "£ of mis-attribution" is not comparable across pairs. Every
pair therefore reports a **dimensionless normalised gap** against a **no-skill baseline**
`g0(w)` — the gap a company using *only the population prior* (no per-entity
discrimination: predict the majority quadrant, assume the naive correlation, hold the prior
book mix, flag nobody) would score against the same hidden truth:

```
gap(w, c) = raw_gap(w, c) / g0(w)          # dimensionless
```

Reading convention, identical for every pair so a trend line means one thing everywhere:

- `gap = 0` → the company perfectly recovers the hidden truth. For any **wall-respecting**
  pair this must be **structurally unreachable** — reaching it means the observables leak
  `θ` (an epistemic-wall violation *in spirit*), and is itself a defect, not a triumph
  (matches the W2_7 charter's "100% classifier = defect" clause).
- `gap = 1` → the company does no better than the blind prior. It is not coping.
- `0 < gap < 1` → the company has **learned some, but not all**, of the hidden structure.
  This is the honest, expected steady state.
- `gap > 1` → the company is **worse than blind** (an actively harmful model). Flag red.

**Trend is the story, not the level:** `Δgap = gap(t) − gap(t−1)` over successive
measurements. **Falling → learning. Static → not adapting (a finding, per the staged doc).
Rising → regressing.** Because every pair is a fraction of its own no-skill baseline, a
falling trend on W2_7 and a falling trend on W2_10 mean the same *kind* of thing even though
their raw losses are unrelated.

### 1.3 Where each quantity lives (the wall, kept)

| Quantity | Layer | Path (illustrative) | May read `θ`? |
|---|---|---|---|
| Hidden truth `θ` | SIM | `simulation/**`, `data_regime="synthetic"` | is `θ` |
| Company belief/action `b` | COMPANY | `company/**`, via `company/interfaces/sim_interface.py` | **No** |
| The gap `gap(w,c)` | HARNESS | `harness/**` or `tools/generate_*` | **Yes — the only layer that sees both** |

The harness computes the gap by holding both `θ` (from the SIM answer key) and `b` (from the
company's observable-only output) side by side. **It never writes `θ` or the gap back into
`company/`.** The company never sees its own score — exactly as a real supplier never gets a
labelled answer key for who was really can't-pay vs won't-pay.

### 1.4 The four named gap formulae, concrete

**(a) Classification-accuracy gap — can't-pay vs won't-pay 2×2 (W2_7).**
Hidden `θ_i` = one of four quadrants ABILITY∈{can,cannot} × WILLINGNESS∈{will,won't}.
Company `b_i` = predicted quadrant `q̂_i` from observable engagement/plan-adherence/disclosure.
Use a **harm-cost matrix** `C[q, q̂]` (misclassification is asymmetric: cannot-pay→won't-pay
carries customer-harm + compliance breach; won't-pay→cannot-pay carries moral hazard + loss;
diagonal = 0):

```
raw_gap = (1/|P|) Σ_i C[ q_i , q̂_i ]
g0      = (1/|P|) Σ_i C[ q_i , argmax_q prior(q) ]     # always-predict-majority
gap     = raw_gap / g0
```

Also report the **two directional components separately** (per the charter's "two separate
test paths, not one accuracy score"): `fn_ability = Σ 1[q_i=cannot ∧ q̂_i=won't]/Σ 1[q_i=cannot]`
(vulnerable-treated-as-strategic → harm) and `fn_willingness` (the mirror → loss). The
headline `gap` is the cost-weighted scalar; the two directional rates ride alongside it.

**(b) Attribution-error gap — DD confound (W2_10).**
Harness computes the **true** channel-attributable effect controlling for the migration event
it can see in SIM ground truth: `δ_true = E[bad_debt | DD, do(channel)]`. The company computes
the **naive observational** effect from observables only: `δ_naive = E[bad_debt|DD] −
E[bad_debt|non-DD]`.

```
gap = | δ_naive − δ_true | / | δ_naive |     # fraction of the company's claimed effect that is confound
```

Reads directly as "the company's DD business case is X% artefact." `g0` here is the full
confound magnitude (`δ_naive` with zero correction), so `gap→1` = wholly naive, `gap→0` =
fully de-confounded (unreachable while the migration stays partly hidden).

**(c) Belief-error gap — population draw (W2_2 / archetype mix).**
Hidden `p` = the SIM's drawn archetype/segment probability vector over K segments. Company
`q` = the book composition it infers from observables. Use **total-variation distance**
(already ∈[0,1], no separate normaliser needed):

```
gap = TV(p, q) = ½ Σ_k | p_k − q_k |
```

`g0` = TV between `p` and the *national prior* the company would assume with zero
book-specific information; report `gap/g0` for cross-pair comparability, and raw TV alongside.

**(d) Detection-rate + false-negative-harm gap — self-rationing (W2_8).**
Hidden `S` = set of truly self-rationing accounts (SIM label: perfect payment record ∧
consumption below the shared `domain_invariants.py` TDCV floor). Company `D` = accounts it
flags (e.g. sets `VulnerabilityFlag.PPM_SELF_DISCONNECTED`). Two numbers, both reported, the
**harm-weighted one is the score**:

```
miss_rate = 1 − |S ∩ D| / |S|                                    # plain recall gap
gap       = Σ_{i ∈ S \ D} harm_i  /  Σ_{i ∈ S} harm_i            # fraction of detectable harm missed
```

where `harm_i` = severity of the missed case (e.g. TDCV-floor shortfall × duration below
floor). A missed severe case must cost more than a missed marginal one — hence the
harm-weighting, not a flat miss count. `g0` = the harm captured by flagging nobody (i.e.
gap=1 when D=∅).

---

## 2. The affordability-cluster coupling (W2_4–W2_10)

Each row: the world atom (SIM-side hidden truth) → the company-response capability that must
discover-and-cope through the wall → the gap that scores the pair. **Bold company atoms in
the "company response" column do not yet exist as maturity-map atoms** and are proposed for
registration in §2.1.

| World atom (SIM hidden truth) | Company response (the twin, through the wall) | Gap metric that scores it |
|---|---|---|
| **W2_4 household_budget** — hidden income band, essential-cost floor, discretionary margin, savings buffer, priority-of-debts stack (on `simulation/household.py`); arrears are the *output* of budget meeting a shock. | **`C6_affordability_inference`** *(new)* — infer ability-to-pay from missed payments, broken plans, disclosure only; never read the budget. Feeds collections/forbearance decisions. | **Belief-error** on inferred vs true discretionary-margin band (banded: TV or MAE over margin deciles), + downstream **classification** feeds (a) below. |
| **W2_5 life_event_stream** (L2, wired) — job loss/illness/divorce/retirement/new child on the shared `life_events.py` substrate; moves `income_stress`. | **`C7_life_event_detection`** *(new)* — wire the orphaned `company/crm/life_events.py` + `vulnerability_register.py` taxonomy to an observable detector (payment-pattern change, engagement drop, consumption anomaly). Never read the SIM event. | **Detection-rate + false-negative-harm** (formula d) on "did the company notice the life-event-driven distress the wall permitted it to notice." |
| **W2_6 sme_distress_twin** — sector-differentiated insolvency (bad debt **plus** lost supply point) + late-payment culture, `segment∈{SME,I&C}`. | **`C8_sme_credit_risk`** *(new)* — company-side SME credit-risk read: distinguish "slow payer" from "about to fail" from observables; a discrete-failure signature, not the gradual household one. | **Classification** (2×2-style: distressed-but-surviving vs failing) + **attribution** on write-off vs recovered-relationship. |
| **W2_7 willingness_classification** — hidden ABILITY×WILLINGNESS 2×2; same missed payment, four truths; company **cannot** observe the quadrant. | **`C9_cantpay_wontpay_classifier`** *(new — the charter's explicit "a C/F atom in effect")** — classify the quadrant under uncertainty from engagement/plan-adherence/disclosure. | **Classification-accuracy gap (formula a)**, cost-weighted, with both directional false-negative components. **This is the archetypal pair.** |
| **W2_8 self_rationing** — perfect payment record **while** consumption collapses below the TDCV floor; a vulnerability invisible in payment data. | **`C10_self_rationing_detection`** *(new)* — detection algorithm comparing consumption history to the TDCV floor filtered to clean-payment accounts; sets `PPM_SELF_DISCONNECTED`. Missed detection = harm event. | **Detection-rate + false-negative-harm gap (formula d)** — the named metric for this pair. |
| **W2_9 segment_debt_tnc** — statutory business late-payment interest vs domestic late-charge exclusion vs payment-conditioned tariff eligibility (segment-conditioned law). | **`C11_segment_debt_policy`** *(new)* — company-side **policy objects** (per-segment interest invariant, domestic-charge-exclusion invariant, DD-discount/good-payer gating with a fairness constraint) in `domain_invariants.py`. | **Compliance-error gap** — rate of policy applications that violate the segment-conditioned law the harness holds (e.g. a domestic late-charge object ever constructed = gap>0); + a **fairness gap** = extent the DD-discount prices off the *biased* signal W2_10 exposes. |
| **W2_10 dd_attribution_confound** — failing payers migrate off DD *before* they fail; the surviving DD cohort is clean by construction; SIM holds the migration event. | **`C12_channel_attribution_analytics`** *(new)* — the naive cost-to-serve / DD-discount business case built from observables, which **should be capable of being wrong**. | **Attribution-error gap (formula b)** — fraction of the company's DD effect that is confound. |

**Population-draw pair (cross-cutting, already named in the staged doc):**
`W2_2_population_draw` → **`C6_affordability_inference`**'s book-composition belief →
**belief-error gap (formula c, TV)**. W2_2 is the substrate the whole cluster varies over;
its gap is the company's book-mix belief error.

### 2.1 Company-side twins that do not yet exist as atoms (for the orchestrator to register)

Every "company response" above is currently **either absent or an orphaned module**. None is
a maturity-map atom. Proposed registrations (`provenance: proposal`, so DISCOVER/FRAME-workable
now, BUILD-gated until ranked — MATURITY_MAP §9 rule 8), lane `C_customer_ops` (or a new
`C_collections` sub-cluster at the orchestrator's discretion):

1. **`C9_cantpay_wontpay_classifier`** — the classifier under uncertainty (W2_7's explicit
   company twin). *Highest priority: it is the archetypal gap and the staged doc's lead
   example.*
2. **`C10_self_rationing_detection`** — the detection algorithm (W2_8's twin). Taxonomy slot
   (`VulnerabilityFlag.PPM_SELF_DISCONNECTED`) already exists and is orphaned; this atom is
   the missing detector, not new taxonomy.
3. **`C7_life_event_detection`** — wires the orphaned `company/crm/life_events.py` +
   `life_event_impact.py` + `vulnerability_register.py` to a real observable detector (W2_5's
   twin). *W2_5 is already L2, so under the new rules its L3 is blocked until this twin exists
   and its gap is measured — see §3.*
4. **`C6_affordability_inference`** — ability-to-pay inference from observables (W2_4/W2_2's
   twin); the collections/forbearance brain.
5. **`C12_channel_attribution_analytics`** — the naive DD business case (W2_10's twin).
6. **`C8_sme_credit_risk`** — the SME distressed-vs-failing read (W2_6's twin).
7. **`C11_segment_debt_policy`** — the segment-conditioned debt-policy objects (W2_9's twin);
   partly a `domain_invariants.py` extension, so may be scoped as a company-compliance atom
   rather than customer-ops.

The orchestrator (not this doc, not the supervisor) ranks and promotes these; they are
candidates. Ids are proposals — reconcile against the live `maturity_map.yaml` numbering at
registration.

---

## 3. Level-definition amendment (MATURITY_MAP.md)

The two binding rules become **level physics**, not prose. Precise wording to add:

### 3.1 To §3 (the levels table), amend the **L3** row's "To enter" cell

Add, for a **world/SIM-lane atom** (lanes `W1`–`W5`):

> **…and the coupling is closed:** a coupled company-response atom exists, has been run
> against this mechanism, and the belief-vs-truth **gap** for the pair has been computed and
> recorded (a non-null `gap` block on this atom, referencing the company atom by id). *A world
> mechanism that no company capability has yet been tested against cannot reach L3 — it is at
> most **L2 (mechanically real)**, however faithful in isolation. Depth nobody has to cope
> with is scenery, not physics.*

Add, for a **company-lane atom** (lanes `A`–`G`):

> **…and it has faced a world that can defeat it:** the atom has been evaluated against a
> coupled world atom at ≥L2 whose hidden truth it classified/acted on **through the wall**,
> with the pair's `gap` measured and non-degenerate (`gap>0` — a gap of exactly 0 is an
> epistemic-wall leak, not a pass). *Coverage without a defeating world is untested; the atom
> is capped one level below its target until the coupled gap exists.*

### 3.2 To §2 (the Hardening Loop table), add a stage note to **HARDEN**

> For a coupled atom, HARDEN includes **measuring the pair's gap** and recording its trend.
> A HARDEN pass that does not compute/refresh the gap of a coupled atom is incomplete.

### 3.3 New capability-schema fields (§6 data model)

Add two fields to the YAML schema (documented in §6, populated at registration/HARDEN):

```yaml
  couples_with: [C9_cantpay_wontpay_classifier]   # symmetric list of coupled atom ids ([] if solo)
  gap:                                            # null until first measured; the pair's score
    metric: classification_accuracy               # classification|attribution|belief|detection|compliance|fairness
    partner: C9_cantpay_wontpay_classifier
    value: 0.62                                   # normalised gap (fraction of no-skill baseline)
    baseline_g0: "cost of always-predict-majority"
    trend: falling                                # falling|static|rising|unmeasured
    last_measured: "2026-07-14"
    components: {fn_ability: 0.18, fn_willingness: 0.05}   # optional per-metric extras
```

`couples_with` is **symmetric** — both `w` and `c` name each other. `gap` is authored on
**both** atoms of the pair (same value; the world atom's L3 gate and the company atom's target
gate both read it), or on a single canonical side with the other referencing it — an
implementation choice for BUILD (§6 open Q).

---

## 4. Draw-coupling (supervisor)

Implementable against the existing `_maturity_map_draw_concurrent` / `_idle_discover_frame_draw`
structure. Three mechanisms, in order of how cheaply they mechanise the rules:

### 4.1 The L3-ceiling gate (mechanises binding rule 1 — the load-bearing one)

Add a pure helper, no new architecture:

```
_effective_level_target(atom, by_id):
    lt = atom["level_target"]
    if not atom.get("couples_with"):          # solo atom: unchanged
        return lt
    if lt < 3:                                 # only the →L3 step is gated
        return lt
    # gated: cap at 2 until the coupling is closed
    twin = by_id.get(atom["couples_with"][0])
    closed = (twin is not None
              and twin.get("level_current", 0) >= 2
              and atom.get("gap") is not None
              and atom["gap"].get("value") is not None)
    return lt if closed else 2
```

`_is_valid_candidate` computes `has_gap = level_current < _effective_level_target(a, by_id)`
instead of the raw target. **Effect:** a world atom builds *freely up to L2*; it stops
drawing further BUILD work toward L3 until its company twin exists (≥L2) **and** the pair's
gap is recorded. This *is* binding rule 1, as a mechanism (MAKE_IT_STICK: "convert policy to
mechanism, or accept it will evaporate"). It does not block thought — DISCOVER/FRAME on the
capped atom still draws via `_idle_discover_frame_draw`.

Symmetrically for company atoms: their effective target caps one level below `level_target`
until a coupled world atom ≥L2 with a measured gap exists (binding rule 2).

### 4.2 Coupling-aware co-draw (draw as pairs/triads)

Extend the greedy disjoint expansion already in `_maturity_map_draw_concurrent`: after the
dial-weighted primary pick, **prefer the primary's `couples_with` partner** among the
file-scope-disjoint remainder before other candidates. Coupled partners are disjoint **by
construction** — world = `simulation/**`, company = `company/**`, gap-measurement =
`harness/**`/`tools/**` — so the existing `_atoms_file_disjoint` check passes and the triad
(world mechanism + company response + gap measurement) is granted in one cycle, one fork each.
This is the MULTI_ATOM_DRAW mechanism reused, with coupling as a positive selection pull, not
new machinery.

### 4.3 Gap-measurement as drawable work

The gap computation is HARNESS work with its own file scope (`harness/**`/`tools/**`). Register
it as the third atom of each triad (or as a HARDEN-stage task on the world atom whose
`file_scope` includes the harness path). Because a coupled world atom cannot reach L3 without a
recorded gap (§3.1), the gap-measurement task is *automatically* the unblocking work the draw
surfaces once the world+company builds land — no separate scheduler needed.

**Failure contract:** identical to the existing draws — missing/malformed `couples_with` or
`gap` degrades gracefully (treat as solo/unmeasured), never crashes the draw. A world atom with
`level_target≥3` and no `couples_with` is a **registration defect** the phase-close skill should
catch (it can never reach its own target), surfaced as a finding, not a silent cap.

---

## 5. Gap reporting (digest + The Proof door)

### 5.1 Digest

Add a **"Coupled gaps"** section to the two existing digest sinks — the `**NAIVE ORGAN
asks:**`-style block in `docs/status/LATEST.md` (built by `background/naive_organ.py::
render_digest_section`, maintained by `process_run_complete.py`) and the `sanity_daemon.py`
daily NTFY digest (`_maybe_send_daily_digest`) — fired on the existing transition cadence (not a
new heartbeat). Per active coupled pair, one line:

```
W2_7 ⇄ C9  cant/wont classifier   gap 0.62  ↓ falling (was 0.71)   [learning]
W2_8 ⇄ C10 self-rationing detect  gap 0.80  = static  (3 checks)    [FINDING: not adapting]
W2_5 ⇄ C7  life-event detect      gap  —    unmeasured               [BLOCKS W2_5→L3]
```

Anti-decay metrics (MAKE_IT_STICK, alarmed every digest):
- **Pairs with a world atom ≥L2 but `gap=null`** → the binding-rule-1 violation made visible
  (depth with no measured coping). Target: zero un-measured among ≥L2 world atoms.
- **Static-gap pairs** → the staged doc's explicit finding ("a company with a static gap is
  not adapting"). Listed, not just counted.
- **Rising-gap pairs** → regression alarm.

### 5.2 The Proof door (`site/data/proof.json` + `site/proof/index.html`)

Add a `coupled_gaps` block to `proof.json`, built by `tools/generate_proof_data.py` (a new
`_coupled_gaps(atoms)` helper alongside `_verification_stack`), reading each atom's `gap`/
`couples_with` fields — the same "read the map, don't invent" pattern the existing verification
stack uses:

```json
"coupled_gaps": {
  "pair_count": 7,
  "measured": 4, "unmeasured": 3, "static_finding": 1,
  "pairs": [
    {"world_atom":"W2_7_willingness_classification","company_atom":"C9_cantpay_wontpay_classifier",
     "metric":"classification_accuracy","value":0.62,"trend":"falling",
     "history":[0.71,0.66,0.62],"last_measured":"2026-07-14",
     "blocks_l3":false,"components":{"fn_ability":0.18,"fn_willingness":0.05}}
  ]
}
```

Rendered as a new Proof-door panel — **"The gap between what the world knows and what the
company believes"** — one row per pair: pair name, current gap, a sparkline of the history, a
trend chip. Brand grammar (BRAND_CONSTITUTION): a **falling** gap earns the blue "verified/
learning" chip **only** once expert-hour-confirmed; **static** = amber (`~`, a finding);
**unmeasured/blocks-L3** = amber "untested depth"; **rising** = red (`!`). This is what turns
"the score is the gap" from a doc claim into a rendered pixel (R11): the director can watch the
company get less wrong. A gap that is null while its world atom sits ≥L2 renders as an explicit
amber "depth nobody copes with yet" — the failure mode made visible rather than hidden.

R14/basis note: a gap is a **ratio**, not a financial figure, so it carries no settled/billed/
banked clock — but each pair states its **measurement basis** (population, run, as-of date) so
a falling trend can't be an apples-to-oranges artefact of a changed population.

---

## 6. Ordered BUILD task list + open questions

This is the **tournament engine run at small scale now** (staged doc §"Why now"): the arms race
between a deepening world and a coping company, on the current ~31-account cast, so Epoch 4 is a
*scale-up of a loop already turning*, not a mechanism invented late. Small scale is a feature —
it exercises the metric/draw/report plumbing end-to-end before population volume exists.

### Ordered BUILD tasks

1. **Schema + one reference pair, end to end.** Add `couples_with`/`gap` to the YAML schema
   (§3.3). Register `C9_cantpay_wontpay_classifier` and couple it to `W2_7`. Build the
   classification-accuracy gap (formula a) in the harness. This is the thinnest closed loop
   (R4): one world atom, one company twin, one gap, one digest line, one Proof-door row.
2. **Draw mechanism.** Implement `_effective_level_target` + the L3-ceiling gate (§4.1) with
   its own tests (mirror the existing `_is_valid_candidate` tests byte-for-byte discipline).
   Then the coupling-aware co-draw (§4.2). Verify a coupled world atom stops drawing L3 BUILD
   until its twin+gap exist.
3. **Reporting plumbing.** `_coupled_gaps` in `generate_proof_data.py` + the Proof-door panel +
   the digest section (§5). Verify to the rendered pixel (R11).
4. **Level-definition amendment landed** in MATURITY_MAP.md (§3) — orchestrator's act.
5. **Fan the remaining six pairs** across the affordability cluster: register C6/C7/C8/C10/C11/
   C12, build each company twin + its gap, respecting file-scope disjointness so the triads draw
   concurrently. Order by staged-doc salience: W2_8/C10 (self-rationing, named example) and
   W2_10/C12 (DD confound, has a live adjudicated in-codebase instance) next, then the rest.
6. **CLAUDE.md** gains the two binding rules — orchestrator's act, explicitly reserved by this
   task's constraints, not done here.

### Open questions

- **Harm-cost matrix `C` and detection `harm_i` weights (formulae a, d)** — these are
  *curriculum*, not baseline: they encode how much the director cares about vulnerable-treated-
  as-strategic vs the reverse. Per R13 they must be **director-authored, named, versioned**, not
  agent-tuned toward a gap number. Flag for director sign-off before encoding; ship formula-with-
  placeholder-weights, not invented weights.
- **No-skill baseline `g0` definition per pair** — "always predict majority" / "national prior"
  is proposed; the exact prior for W2_2's TV baseline needs the population-draw atom's own
  distribution, which is L0. Until W2_2 builds, use the fixed-cast empirical prior and label it.
- **Gap authored on one side or both** (§3.3) — single canonical + reference vs duplicated value.
  BUILD choice; duplicated is simpler to read in the draw gate, single-canonical avoids drift.
- **Static-gap threshold** — how small a `|Δgap|` over how many measurements counts as "static
  = not adapting"? Needs a real run's noise floor to set honestly (R4: build the closed-loop
  test first, read the actual variance).
- **The 100%-gap-is-a-leak test** — each pair needs an assertion that `gap` cannot reach 0
  (observables don't leak `θ`), mirroring the W2_7 charter's "perfect classifier = defect"
  clause. This is an epistemic-wall check per pair, worth an explicit grep + a statistical bound.
- **Small-cast statistical power** — at ~31 accounts a gap is noisy; W2_2 population-draw (L0)
  is the real fix. Until then, gaps are directional signals, labelled provisional, not precise
  scores — consistent with the staged doc's "small scale now."

---

*Sources: `docs/staging/THE_COUPLED_TRIAD.md` (spec); `docs/design/MATURITY_MAP.md`
(levels/loop/draw rules); `docs/design/CHARTER_W2_AFFORDABILITY.md` + the W2_4–W2_10 atom
entries in `docs/design/maturity_map.yaml` (per-atom hidden truth + company-twin implications);
`background/supervisor.py::_maturity_map_draw_concurrent`/`_idle_discover_frame_draw`
(draw structure); `tools/generate_proof_data.py::_verification_stack` + `site/data/proof.json`
(Proof-door pipeline). R4/R10/R11/R12/R13/R14, MAKE_IT_STICK, EPOCH_GATING_AND_ATOM_AUTHORSHIP,
BRAND_CONSTITUTION referenced inline.*
