# Population Coverage — Stage 4: The Value Frontier (coverage → value)

**Track:** DIRECTOR_STEER_COVERAGE_STAGE4_VALUE_FRONTIER_2026-07-20 (learning loop, DISCOVER/FRAME)
**Stage:** 4 of the loop — *how many segments is enough, when the question is VALUE not coverage.*
**Status:** ANALYSIS + committed structure only. **NO generator change** (director-reserved — see §7).
**No new fetch. No microdata.** Everything derives from the committed stage-2/3 open aggregates.

> Committed machine-readable structure (all in `docs/market_research/population_coverage/`):
> `value_outcome_model.json` (**values-call (a)** — what makes variance *valuable*, ASSERTED),
> `critical_groups.json` (**values-call (b)** — what makes a group *critical*, ASSERTED),
> `value_frontier.json` (the curves, both constructors, the knees, robustness),
> `build_value_frontier.py` (the deterministic builder — seed 20260720, no network, no microdata).

---

## 0. Headline for the director (read this first)

1. **The value knee is ~12 segments.** `price_sensitivity × tenure` (3×4) captures **78% of the
   valuable variance**. The next 200+ segments buy the remaining 22% — a textbook knee. This is a
   *different* answer to a *different* question than the banked **N=200 coverage knee**: that one is
   *households to draw*; this one is *segments to define*. Different axes, not comparable in units. **§3.**
2. **The two constructors converge exactly on the variance frontier.** The director's "build from the
   modal customer outward" and the "worst-cell-greedy" alternative land on the **same curve**: both hit
   0.44 at 3 segments (price sensitivity) and **0.784 at 12 segments** (price × tenure), identically.
   They differ only in how they *spend segments past the knee* — which is exactly where it stops
   mattering. So the intuition is confirmed. **§4.**
3. **The two objectives genuinely do NOT co-move — which is why a blended metric would have lied.**
   Valuable variance is bought by a few *coarse main-effect* splits. Critical-group protection is bought
   by *targeted conjunctive carve-outs* (the stage-3 named-worst-cell mechanism), which add ≈0 variance
   but full tail protection. Neither greedy-variance nor modal-outward protects the critical tail
   efficiently on its own. **Keeping them separate surfaced this; blending would have buried it.** **§5.**
4. **The recommended minimum-segment design: ~31 segments.** A 12-cell commercial core
   (`price_sensitivity × tenure`) **plus a cross-cutting protected overlay** (the 5 critical groups,
   run as a PSR/fuel-poor-style list, not intersected with the commercial cells) →
   **78.7% valuable variance + 100% critical-group coverage in 31 segments.** **§5, §6.**
5. **The knee is robust to the values-call; the *leading dimension* is not.** Under the default and a
   pure-P&L weighting, `price_sensitivity × tenure` leads (78–84% at 12 segments). Under a net-zero
   tilt, `tenure` leads and `heating_fuel` climbs into the top 3 — but it is still ~2 dimensions to the
   knee. So the *number* of segments to the knee survives re-weighting; *which* two dimensions depends on
   what the director says value IS. **§3.4.**
6. **One tension to flag (couples stage-3 to stage-4): the highest-value split is the least
   observable.** `price_sensitivity` — the top variance lever — is exactly a dimension the stage-3
   fusion gate forced to **`assumed`** (no open joint, residual unmeasurable). The most valuable
   segmentation axis is the one we can least honestly place. **§6, push-back.**

---

## 1. The question stage 4 answers

Stage 3 answered **coverage**: does every important cell *appear* → N=200. Stage 4 answers the
director's actual question:

> *"How much valuable variance and critical small groups can we cover with minimum number of
> segments. So we want both volume of covers and scope of features/complexity."*

This is a **value-vs-cost frontier**: maximise what matters, minimise segments spent. The deliverable
is the **curve** of value-captured vs segment-count and its **knee**.

**Two objectives, kept deliberately separate** (a blended metric trades them silently):

1. **Valuable variance** — volume-weighted between-segment variance (`eta²` / `R²`) of an asserted
   *business-value* outcome. Large groups behaving *distinctly enough to change a decision*.
2. **Critical small groups** — the protected set (fuel-poor off-gas, vulnerable prepayment) covered
   **regardless of size**. Barely registers on variance; carries regulatory and mortality weight.

**A segment is justified if it adds material valuable-variance OR captures a critical group.**

---

## 2. The two values-calls (proposed ASSERTED — director confirms)

Same claim-status discipline as the tail-lift threshold: proposed as **CHOSEN/asserted**, explicit and
changeable in committed structure. The frontier rebuilds deterministically from them.

### 2(a) What makes variance "valuable" — `value_outcome_model.json`

The outcome the design optimises toward, as a weighting over four business outcomes (weights are over
the **z-scores** of each, so they read directly as relative importance and no £-scale dominates):

| Outcome | Sign | **Default weight** | Rationale |
|---|:--:|:--:|---|
| Gross margin / cost-to-serve | + | **0.40** | the primary commercial lever |
| Retention (churn cost) | − | **0.25** | reacquisition + lost-margin exposure |
| Bad debt | − | **0.20** | affordability stress in £ |
| Carbon abated (value) | + | **0.15** | decarbonisation as a real but, today, un-priced overlay |

Two alternatives are offered in the file: `pure_pnl` (carbon = 0) and `net_zero_tilt` (carbon = 0.35).
The per-level effect sizes (e.g. price-sensitive −£22 margin / +0.16 churn; off-gas oil +£22 bad debt /
+2.0 tCO₂ abatable) are **directionally anchored to UK-energy domain sense, not calibrated to company
P&L** — they exist to *rank* segments, never to forecast money (R12).

### 2(b) What makes a group "critical" — `critical_groups.json`

The protected set surviving regardless of size, as predicates over the 12 open dimensions (proxies,
exactly the honest-proxy discipline stage-3 used for its named worst cells):

| Group | Family | Predicate (proxy) | Prevalence in sample |
|---|---|---|:--:|
| `fuel_poor_offgas` | affordability/mortality | off-gas fuel · low class · rented | 3.35% |
| `vulnerable_assisted` | vulnerability (PSR) | assisted channel · low class | 5.997% |
| `electric_flat_renter` | affordability | electric · flat · rented | 1.48% |
| `offgrid_rural_low_income` | affordability | oil/LPG · Wales/SW/East · low class | 0.90% |
| `high_needs_prepay_proxy` | regulatory | social rent · assisted/phone · price-sensitive | 2.58% |

Coverage = fraction of the protected set **isolatable** at purity ≥ 0.60 (so the business can treat
them distinctly without sweeping in unrelated customers). The first three map directly onto stage-3's
named worst cells.

---

## 3. The value frontier and its knee

### 3.1 The curve (constructor B, modal-outward — the legible read)

Dimensions added in main-effect-variance order, from the modal customer outward. Segment count is the
running product of level counts.

| Step | + dimension | segments | **valuable variance** | critical coverage |
|---:|---|---:|:--:|:--:|
| 0 | (everyone = 1 segment) | 1 | 0.000 | 0.05 |
| 1 | price_sensitivity | 3 | 0.441 | 0.06 |
| 2 | **tenure** | **12** | **0.784** ← **KNEE** | 0.21 |
| 3 | accommodation | 59 | 0.797 | 0.23 |
| 4 | nssec | 224 | 0.842 | 0.29 |
| 5 | EV | 411 | 0.900 | 0.29 |
| 6 | channel_pref | 1,111 | 0.957 | 0.50 |
| 7 | cars | 2,741 | 0.958 | 0.50 |
| 8 | heating_fuel | 7,992 | 0.996 | **1.00** |

**Read it:** 12 segments capture 78% of valuable variance. Steps 3→8 spend **665× more segments**
(12 → 7,992) to add the final 22%. The knee is at step 2 — unambiguous.

### 3.2 The modal customer (constructor B's centre)

Recovered as the highest-volume profile: **owns outright · semi-detached · 1 car · intermediate class ·
mains gas · South East · neutral-green · medium price-sensitivity · digital · no solar/EV/battery.**
Close to the director's "DD, owner-occupier, online, no-debt simplest customer" — the frontier expands
outward from here by the dimension that most changes business value (price sensitivity), then tenure.

### 3.3 The value knee vs the coverage knee

| | **Coverage knee (stage 3)** | **Value knee (stage 4)** |
|---|---|---|
| Question | does every important cell *appear*? | is each *segment* worth having? |
| Axis | **households drawn** (N) | **segments defined** (K) |
| Answer | **N = 200** | **K ≈ 12** (variance) → **31** (with critical overlay) |
| What the knee buys | completeness (every target hit ≥ req) | 78% of valuable variance |
| Beyond the knee | statistical mass / redundancy | fine-grained variance (diminishing) |

They are **different axes and not directly comparable in units** — a point worth stating plainly so the
two "knees" aren't conflated.

### 3.4 Is the knee robust to the values-call? (yes for the count, no for the lead dimension)

| Weighting | leading dim | 2nd dim | variance @ 2 dims (~12 seg) | top-3 |
|---|---|---|:--:|---|
| **default** | price_sensitivity | tenure | 0.784 | price, tenure, accommodation |
| **pure_pnl** | price_sensitivity | tenure | 0.837 | price, tenure, nssec |
| **net_zero_tilt** | **tenure** | price_sensitivity | 0.595 | tenure, price, **heating_fuel** |

The **~2-dimensions-to-the-knee** result survives all three weightings. *Which* two dimensions depends
on what the director says value IS — and under a carbon tilt, `heating_fuel` climbs into the top 3,
which conveniently is also the dimension that protects the critical groups (§5). So a net-zero-weighted
company gets more of its critical protection for free inside its variance core.

---

## 4. Do modal-outward and worst-cell-greedy converge? (yes, on the variance frontier)

The director asked whether centre-out expansion and worst-cell-greedy land on the same frontier. They
do, through the knee — which is where it matters:

| segments | constructor A (variance-greedy leaf-split) | constructor B (modal-outward) |
|---:|:--:|:--:|
| 3 | 0.441 (split: price_sensitivity) | 0.441 (price_sensitivity) |
| 12 | **0.784** (splits: price → tenure) | **0.784** (price × tenure) |
| >12 | stays *more* segment-efficient (splits selectively) | multiplies out whole dimensions |

They are **identical to the knee** and diverge only *past* it: greedy A keeps ~0.87 variance at ~50
selective leaves where B needs hundreds of full-cross cells for the same, because A only splits where
the variance is. So: **use modal-outward for the legible story (it names dimensions in order), trust
the greedy for the efficient frontier past the knee.** Both agree on the answer to "how many segments."

**Where they do NOT converge: the critical-group half.** Neither pure constructor protects the critical
tail efficiently — greedy-variance ignores tiny cells, and modal-outward only isolates them by accident
once `heating_fuel` multiplies the cross out to ~8,000 cells. That non-convergence is the signal that
critical protection is a *different mechanism*, not a *deeper cross* — §5.

---

## 5. The two objectives don't co-move — the load-bearing stage-4 finding

Plotting critical coverage against variance capture shows they pull apart:

- **Variance** is 78% captured at 12 segments and 99.6% at ~8,000.
- **Critical coverage** is still only **0.21** at the 12-segment variance knee, and only reaches 1.0 at
  ~8,000 segments *if you rely on the cross to isolate the tail*.

A single blended "value" number would have averaged these and hidden the trade entirely. Kept separate,
the mechanism is obvious: **critical groups are defined by conjunctions** (off-gas fuel *and* low class
*and* rented) that a variance-led splitter never reaches and a modal cross only reaches by brute force.
You protect them the way stage 3 did — **carve the specific cell**, as a targeted overlay.

### The recommended minimum-segment design (§6 for the numbers)

**A small commercial variance core + a cross-cutting protected overlay.** The overlay is the 5 critical
groups run as a PSR/fuel-poor-style list (as a real supplier does), *not* intersected with the
commercial cells:

| design | segments | valuable variance | critical coverage |
|---|:--:|:--:|:--:|
| variance core only (`price × tenure`) | 12 | 0.784 | 0.21 |
| **core + protected OVERLAY** | **31** | **0.787** | **1.00** |
| core + overlay, `× nssec` core | 67 | 0.812 | 1.00 |
| core INTERSECT carve (overlay × commercial) | 83 | 0.828 | 1.00 |
| `price × tenure × fuel` INTERSECT carve | 266 | 0.860 | 1.00 |

**31 segments** buys 78.7% of valuable variance *and* 100% critical-group protection. Pulling the
protected households into an overlay barely moves variance (0.784 → 0.787) because they are a small
*volume* — which is the whole point of protecting them on a non-volume basis.

---

## 6. What this says about "how many segments is enough"

- **For commercial variance: ~12 segments** (`price_sensitivity × tenure`). Everything past that is
  diminishing returns; the director's "minimum number of segments" instinct is vindicated hard — the
  business-relevant variance is coarse.
- **For the whole objective (variance + protected tail): ~31 segments** — the 12-cell core plus a
  ~19-segment protected overlay (collapsible toward ~5 group-segments if membership combinations are
  merged). This is the number to carry into the generator-wiring proposal.
- **The protected overlay is the stage-3 named-worst-cell mechanism, generalised** — which is a
  satisfying closure of the loop: stage 3's worst cells were exactly the right primitive for stage 4's
  critical-group half.

---

## 7. The handoff — generator wiring (DIRECTOR-RESERVED, proposed only, bring back as [ACT])

This steer authorised the **analysis**. Building it into the population generator is the reserved step.
Proposed wiring, **not applied**:

1. **Archetype ground truth gains a `value_segment` and a `protected_flags` field, not a finer grid.**
   The generator would tag each synthetic household with (a) its commercial segment
   `(price_sensitivity, tenure)` — 12 cells — and (b) a set of protected-group flags from
   `critical_groups.json`. The change is *two tags on the existing archetype*, not a re-partition of the
   population — cheap and reversible.
2. **The protected overlay is a lookup, not a new axis.** `critical_groups.json` predicates become a
   membership function evaluated at draw time; the population model does not need new dimensions.
3. **Delta to archetype ground truth:** today's archetypes carry the 12 factor dimensions (stage-3
   schema). The delta is the derived `value_segment` (a function of two existing dims) + `protected`
   (a function of existing dims). **No new source data, no new fused joint** — so it does not reopen the
   stage-3 fusion-gate work.
4. **Coupled-triad obligation (CLAUDE.md):** before any of this reaches L3, the *company* must be tested
   against a world segmented this way and the belief-vs-truth gap measured — the value segmentation is a
   SIM capability and needs its HARNESS gap. Flagged, not built.

**What I would NOT do without the director:** change the *effect model* or the *weighting* (values-call
(a)), or the *protected set* (values-call (b)) — those are his by right, and everything downstream
inherits them.

---

## 8. Push-back / what I'd surface

- **The highest-value dimension is the least observable.** `price_sensitivity` leads the variance
  frontier but is `assumed` (stage-3 fusion gate: no open joint, residual unmeasurable). So the single
  most valuable way to segment is the one we can least honestly place in the population. Two honest
  routes: (i) treat price-sensitivity as a *behavioural* segment the company *discovers* post-acquisition
  (switching response), not a *demographic* one it assigns at draw — which fits the epistemic wall
  better; (ii) if it must be assigned, carry it explicitly as a declared fidelity risk. **I lean (i).**
- **The knee's height depends on asserted effect sizes.** The *location* (~12 segments) is robust across
  all three weightings, but the *fraction captured* (78%) is a function of the asserted model. It is a
  ranking tool, not a forecast — do not let 78% harden into a claimed number.
- **`net_zero_tilt` changes the lead dimension to tenure and pulls fuel up.** If the director weights
  carbon as first-class, the segmentation genuinely changes shape (fuel-led). Worth an explicit choice.
- **Critical-group predicates are proxies.** `assisted channel → PSR`, `social rent → prepayment` etc.
  are asserted proxies over open dims, refutable exactly like stage-3's worst cells. A consented source
  that placed real PSR/prepayment flags would replace them; until then they are declared, not settled.
- **The overlay's ~19 raw segments collapse to ~5** if membership combinations are merged; whether to
  keep combinations distinct (a fuel-poor-AND-vulnerable household treated differently from either
  alone) is a small values-call the director may want to make.

---

*Stage 4, autonomous worker in isolated worktree, 2026-07-20. Analysis + committed structure;
**not pushed**. Director/advisor read & confirm the two values-calls; the generator wiring is the
reserved [ACT] step.*
