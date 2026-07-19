# Epoch-2 atom D — CASCADE CORRELATION ESTIMATION methodology (DISCOVER pass, doc-only)

**Status:** DISCOVER, doc-only. Provenance: **proposal**. No level claimed. Writes **no**
`sim/`/`company/`/`harness/` code, edits neither `maturity_map.yaml` nor any engine, touches only
`docs/design/`. **W1 BUILD stays CLOSED** (Epoch-3 BUILD-gated per `EPOCH_GATING_AND_ATOM_AUTHORSHIP`
Rule 1; this campaign proceeds through DISCOVER/FRAME until the director opens it). Isolated worktree;
no push; one commit.

**Source of task:** `docs/staging/in_progress/DIRECTOR_CAMPAIGN_EPOCH2_COUPLED_WORLD_2026-07-19.md`
requirement 4 — *"correlations and dependence structures must be ESTIMATED from data — mathematics and
statistics, not hand-set constants … the joint tail behaviour matters more than the marginal … where a
relationship is asserted rather than estimated, say so honestly and register it as a simplification."*
Homed as atom **D** in `docs/design/EPOCH2_COUPLED_WORLD_CAMPAIGN_DECOMPOSITION.md`.

**No network this session.** No real series is pulled and **no market figure is fabricated** (Historical
Ground Truth). The only empirical numbers cited are the already-committed 4-point-proxy anchors from
`W1_3_NATIONAL_WEATHER_JOINT_REGIME_DISCOVER.md` (decile joint-tail lift **2.34×**; winter temp/wind corr
**+0.507** vs all-year **−0.06**), quoted as *directional anchors, verify against the capacity-weighted GB
series at BUILD*. External data anchors are flagged **`[recall — verify at BUILD]`**. Statistical methods
named below are standard extreme-value / copula theory (definitions, not empirical claims); where a
literature attribution is from memory it is flagged.

**This atom SYNTHESISES the landed discovery.** It does not re-derive the cascade (owned by
`W1_COUPLED_WEATHER_CASCADE_DISCOVER.md`), the weather entry shock (`W1_3_…`), or the price/cost physics
(`EPOCH2_BC_PRICE_FORMATION_AND_SUPPLIER_COST_DISCOVER.md`). **It owns the thing none of them own: the
METHOD for estimating the *nature* and *strength* of every dependence in the coupled cascade, with
joint-tail emphasis — and the single portable statistic that makes every link comparable and every
coupling control R15-mutation-testable.** W1_3 supplies the WORKED example (one link, one estimator); this
doc generalises that estimator into a reusable protocol for the whole chain.

---

## 1. The dependence inventory — every link whose correlation must be estimated

The cascade is not one correlation; it is a *chain of couplings*, and a supplier dies where several of
them fire **at once**. Each row names the observables, the **tail corner** that matters (lower = both low,
upper = both high), and **why its JOINT TAIL — not its average — is the killing quantity**. "Average"
methods (row-by-row Pearson) are green on almost every one of these while the joint tail is lethal.

| # | Link | Observables (≥2) | Tail corner that kills | Why the JOINT tail, not the average, is the danger |
|---|---|---|---|---|
| **D1** | **temp ⊥ wind** (weather entry) | national daily `temperature_mean`, `wind_speed_mean` | **lower-lower** (cold ∧ still) | The supplier-killing corner. All-year Pearson ≈ 0 (`−0.06`) says "no relationship"; the winter lower tail is strongly co-moving (`+0.507`, decile lift `2.34×`). Sample independently → under-populate the corner by ½–⅔. **The worked example (W1_3).** |
| **D2** | **residual-demand ↔ price** | `residual_demand_mw` (D−G_wind−G_solar), wholesale/SSP print | **upper-upper** (tight ∧ dear) | Price is a convex power of tightness (`P=gas_floor·(RD/margin)^γ`). Average correlation understates how tightly price locks to residual *in the tight tail* where the margin denominator collapses. Cascade link D→E. |
| **D3** | **short-volume ↔ cash-out price** (the supplier-cost covariance) | book imbalance volume `Δvol = demand − hedged`, SSP/SBP cash-out (stress premium ×1.2) | **upper-upper** (short ∧ spiking) | **The single most important financial dependence.** The cost of the increment is `E[Δvol · spot]` — a **covariance term**. Price volatility on the fixed book is inert (BC-2); the money is lost only where short-volume and spike **coincide**. Average-spot pricing of volume error erases exactly this. Cascade link F; B/C §3. |
| **D4** | **demand ↔ temperature** | national/premise demand, `temperature_mean` | **lower-temp / upper-demand** | Heating load is convex below a threshold — a cold *tail* lifts demand far more than a linear fit predicts. The nonlinearity lives in the tail; a Pearson slope fit on all temperatures under-reads the cold-snap demand plateau. Cascade link B. |
| **D5** | **wind-output ↔ wind-speed** | `G_wind`, `wind_speed` | **lower-lower** (still ∧ zero-output) | Deterministic (power curve) but **tail-amplifying**: cubic ramp near cut-in means a small speed drop in the still tail is a large output collapse. The coupling *stretches* the wind tail *before* it enters residual demand — so D5's convexity compounds D1's lift. Cascade link C. |
| **D6** | **cross-link cascade seams** | (residual, price), (price, imbalance), (national regime, regional field) | joint upper along the chain | The seams *between* links — where "each link is individually right but the chain is decoupled" hides. Guarded by W1-CASC1/2/3. The compounding is multiplicative: end-to-end lift ≈ **product** of per-link lifts, not any one. |
| **D7** | **interconnector relief ↔ GB tightness** | IC net import, GB residual demand | **relief fails in the upper tail** | A *negative-when-you-need-it* dependence: a cold∧still event is frequently European-wide, so import relief is weakest exactly when GB is tightest. Average IC flow looks helpful; the tail conditional (relief \| GB tight ∧ EU tight) is near zero. `[recall — verify at BUILD]` B/C §1.1. |
| **D8** | **temporal persistence** (auto-dependence, not cross-sectional) | each variable's own lag-1..k | multi-day spell | Not a pair-correlation but a *self*-dependence: lag-1 autocorr temp `~0.78`, wind `~0.57` (W1_3 §1.4). A memoryless model prices a 5-day spell as `p^5` (vanishing) and teaches zero hedge. Persistence is what turns a joint tail into a *sustained* drawdown (W1-CASC3). |

**The inventory's shape:** D1 is the entry; D4/D5 are the two first-order weather→system couplings; D2 is
where they combine and convex-amplify; D3 is where the system tail becomes a **£ covariance** on the
company's book; D6 is the compounding across seams; D7 is a tail-*sharpening* (relief withdrawn in the
tail); D8 is the temporal axis that runs orthogonally through all of them. Every one must be given a
*nature* (sign, which tail, asymptotically-dependent-or-not) and a *strength* (magnitude), estimated —
not hand-set.

---

## 2. Why marginal/average methods FAIL here — and the joint-tail methods that don't (the heart of the atom)

### 2.1 Why the default statistics erase exactly the coincidence that kills

| Method | What it measures | Why it FAILS on this cascade |
|---|---|---|
| **Pearson linear correlation `ρ`** | average linear co-movement over the *whole* distribution | Dominated by the dense bulk; a handful of joint-tail days barely move it. Worse, it is **not marginal-free** — a convex marginal (heating demand, `(·)^γ` price) distorts `ρ` regardless of the true dependence. On D1 the pooled `ρ=−0.06` actively **lies** (the winter tail is `+0.507`). A single number for a relationship that *switches on in the tail* is the wrong object. |
| **Averaging / expectation over the series** | central tendency | The killing quantity is a *coincidence in the corner*, contributing almost nothing to the mean. Pricing volume error at *average* spot (B/C caveat) drops the covariance `E[Δvol·spot]` — the whole D3 risk. |
| **Gaussian copula (single fitted `ρ`)** | dependence with the marginals stripped out, BUT | **The canonical trap.** The Gaussian copula has **zero asymptotic tail dependence** (`λ = 0`): however high you fit `ρ`, the probability of *joint* extremes → the independent product as you go deeper into the tail. It structurally *thins* the exact corner the cascade lives in. Fitting a Gaussian copula to cold∧still is the parametric form of the pooling error. |
| **Pooling across regimes/seasons** | more sample, "more power" | Annihilates a *conditional* dependence. D1's coupling is winter-localised; pool it with summer and it washes to zero (the decisive W1_3 §1.3 finding). More data, *wrong* data. |

**The through-line:** every default method answers "what is the *average* relationship?" The cascade
question is "**when A is extreme, how much more likely / severe is B extreme — and does that get *stronger*
deeper in the tail?**" A different class of statistic is required.

### 2.2 The joint-tail methods that DON'T fail — nature vs strength

Split the job into **nature** (is there tail dependence at all, in which tail, and does it persist into
the limit?) and **strength** (how much). Use a diagnostic first, then a magnitude.

**A. Diagnosing the NATURE of the tail dependence (do this FIRST):**

- **χ and χ̄ diagnostics** (Coles–Heffernan–Tawn family `[recall — verify formulae at BUILD]`). Two
  companion functions of the threshold `u`:
  - **χ(u) = P(Y > q_u \| X > q_u)** — the conditional exceedance probability. Its limit `χ = lim_{u→1} χ(u)`
    is the **tail-dependence coefficient λ** (below). `χ > 0` ⇒ **asymptotically dependent** (extremes truly
    co-occur in the limit — the dangerous class).
  - **χ̄ ∈ (−1, 1]** classifies *which regime you are in*: **χ̄ = 1 ⇒ asymptotic dependence** (use χ/λ to
    size it); **χ̄ < 1 with χ = 0 ⇒ asymptotic *in*dependence** (co-occurrence weakens in the limit but may
    still be strong at finite tails — size it with χ̄ and finite-`u` exceedance, not λ).
  - **Why it matters here:** it answers "is cold∧still a genuine tail-dependent pair (χ̄≈1) or a strongly
    *asymptotically-independent* one (χ̄<1)?" — a real open question (§7) that decides whether the SIM needs
    a tail-dependent copula (t/Clayton) or whether a rich enough latent-regime model suffices. **Plot χ(u)
    and χ̄(u) against `u`; a *rising* χ(u) toward the tail is the signature the whole atom cares about.**

- **Exceedance / threshold-conditioned correlation `ρ(u)`**: `corr(X, Y \| X > q_u ∧ Y > q_u)` as a
  function of threshold `u`. Plain to read: if `ρ(u)` **rises** as `u → tail`, dependence *strengthens* in
  the corner (the cascade signature); if it falls toward zero, the bulk correlation was an artefact.
  W1_3's `−0.06`(all) → `+0.507`(winter) is the *regime-conditioned* cousin of this; the threshold-
  conditioned version is its continuous form. Use it as the intuitive, presentation-friendly diagnostic
  alongside χ.

**B. Sizing the STRENGTH — the tail-dependence coefficient `λ`:**

- **Tail-dependence coefficient** `λ_L = lim_{u→0⁺} P(X ≤ F_X⁻¹(u) \| Y ≤ F_Y⁻¹(u))` (lower tail; `λ_U`
  the upper analogue). **Plain terms:** "given one variable is in its extreme `u`-tail, what is the
  probability the *other* is too, as the tail shrinks to nothing?" `λ = 0` = independent extremes (Gaussian);
  `λ → 1` = they always co-extreme. **This is the scalar the cascade wants** — but it is a *limit*, hard to
  estimate from 21 days, so in practice estimate a **finite-`u` version** and report it *with its `u`*. The
  portable statistic in §4 is exactly a finite-`u`, scale-free form of λ.

**C. Copula families — pick one that ADMITS tail dependence (nature drives the choice):**

By Sklar's theorem any joint law = marginals + a copula; the copula *is* the pure dependence. The family
choice is a *nature* decision:

- **Gaussian** — `λ = 0`. **Forbidden as the cascade dependence baseline** (thins the tail); named as the
  anti-pattern.
- **Student-t** — symmetric tail dependence `λ_U = λ_L > 0`, governed by correlation *and* degrees-of-
  freedom (low df ⇒ fat joint tails). A defensible **default** where the tail dependence is roughly
  symmetric and a single family must cover a link.
- **Clayton** — **lower-tail** dependence (`λ_L > 0`, `λ_U = 0`). Natural for **D1 cold∧still** (both *low*)
  and any "joint crash" corner.
- **Gumbel** (and **survival-Clayton**) — **upper-tail** dependence (`λ_U > 0`). Natural for **D2/D3**
  (tight∧dear, short∧spiking — both *high*).
- **Mixture / vine copulas** — for the *multi-link* chain (D6), a **vine** (pair-copula construction)
  composes bivariate copulas along the cascade so each seam can carry its own tail behaviour without
  forcing one global family. The honest heavy-machinery option; declare as a simplification if deferred.

**D. Marginal-tail machinery (needed before any joint statistic is trustworthy):**

- **Peaks-over-threshold (POT) → Generalised Pareto (GPD)** for each variable's *own* tail, and
  **block-maxima → GEV** as the alternative. You cannot characterise a *joint* tail on top of mis-fit
  *marginal* tails; POT/GPD gives each variable a defensible tail before the copula couples them.
  Multivariate EVT (spectral/angular measure, Pickands dependence function) is the joint-tail generalisation
  `[recall — verify at BUILD]`; likely heavier than needed at current data volumes — declare if used.

**E. The generative alternative — latent common-cause (the SIM's own route):**

W1_3's authoritative mechanism carries tail dependence **structurally** via a latent regime chain (a
common cause driving all links), *not* by fitting a copula. This is the **SIM-side** answer: it produces
tail dependence and persistence together, and is `C-S2`-replayable. The estimated `λ` / copula fits are
then the **validation target** the generator must reproduce — not the generator itself. This keeps the
anti-marking-own-homework wall (fit the estimator on the *record*; the generator is validated *against* it).

**Selection heuristic:** diagnose nature with **χ/χ̄ + exceedance-correlation curves** → if asymptotically
dependent, size with **λ** and pick the tail-matching copula (Clayton lower / Gumbel upper / t symmetric);
if asymptotically *independent*, report finite-`u` χ̄ and do **not** impose a spurious `λ>0` family. The
SIM realises the dependence with a **latent-regime** generator and the estimators become its exit test.

---

## 3. The estimation protocol — from an observed series to a defensible (nature, strength)

A repeatable recipe applied identically to every inventory link, so results are comparable and auditable.

1. **CONDITION before you estimate (the anti-pooling step — non-negotiable).** Restrict to the regime in
   which the coupling is claimed to live *before* computing anything. For weather links: winter (DJF) — the
   `+0.507`-vs-`−0.06` lesson is that pooling is not a smaller effect, it is a **sign-and-existence** error.
   State the conditioning set and *why* (D1: heating season; D3: winter short-book regime). "Winter = DJF"
   is a configurable cold-season parameter, not a hardcoded `{12,1,2}` (portability, §6).

2. **CHOOSE the tail quantile `u` and DECLARE it.** Decile (`u=0.10`, severe, ~21 winter days on the 4-pt
   record) vs quintile (`u=0.20`, ~65 days, more power). Every statistic is reported **with its `u`** — a
   λ-like number without its `u` is meaningless. Report the *curve* over `u` (§2.2 diagnostics) where
   possible; a single `u` is a summary of it.

3. **DIAGNOSE nature, then SIZE strength** (per §2.2): χ(u)/χ̄(u) and exceedance-correlation curve first
   (asymptotically dependent or not, which tail, does it rise into the tail); then the finite-`u`
   joint-tail statistic **L** (§4) and/or `λ`, and a tail-matching copula fit if the SIM needs a parametric
   form.

4. **QUANTIFY uncertainty — and respect the tiny effective sample.** 21 decile days is small, and worse,
   **autocorrelated** (temp lag-1 `~0.78`): the *effective* independent sample is far below the nominal `n`,
   so naive CIs are far too tight. Protocol:
   - **Block bootstrap** (moving/stationary block, block length ≳ the persistence scale) for CIs on L / λ /
     exceedance-corr — resample *spells*, not days, so the CI honours D8's autocorrelation.
   - **Profile-likelihood CIs** for parametric copula / GPD parameters (better small-sample coverage than
     Wald).
   - **Borrow strength across `u`** (fit the copula on the fuller conditioned sample, read λ from the fitted
     family) when the raw decile count is too thin for a nonparametric λ — but then the number inherits the
     *family assumption*, which must be stated.
   - **Report the CI, always.** A wide CI on a small tail sample is the honest answer and is itself a
     finding (drives the §7 "need capacity-weighted series" ask).

5. **CROSS-VALIDATE against an INDEPENDENT anchor** (anti-marking-own-homework). Fit / estimate on one
   series (the weather record); validate the implied joint-tail against a *different* published
   characterisation (NESO low-wind-and-cold stress stats, documented blocking-high spells) — never
   re-derive the validator from the generator. `[recall — verify at BUILD]`.

6. **The HONESTY RULE (R10) — asserted ≠ estimated.** Where a link's (nature, strength) is *not* estimated
   from data — because the series is unavailable this session, because the sample is too thin to resolve
   nature (χ̄ CI straddles 1), or because it is a structural assumption — **register it as a named
   simplification** in the invariant/simplification library, stating: *what is asserted, why, what its
   assumed value/sign is, and precisely which real series + statistic would ground it.* An asserted
   dependence dressed as an estimated one is the exact defect requirement 4 forbids. Every §7 open item is a
   pre-registered simplification of this form.

**What "nature AND strength" means concretely, per link:** *nature* = {sign; which tail (upper/lower);
asymptotically-dependent (χ̄≈1) vs asymptotically-independent; conditioning regime; functional form
(convex/threshold)}; *strength* = {L at declared `u`, or λ, or exceedance-corr, each with a block-bootstrap
CI}. A link is "estimated" only when both are produced with a CI and an independent-anchor check, or
explicitly registered as asserted (R10).

---

## 4. The single reusable statistic — joint-tail lift `L` (the portable spine)

Mirror W1_3's measure and make it the **one statistic every link reports**, so the whole cascade is
comparable on a single axis and any coupling control is R15-mutation-testable.

> **`L(u) = P(A in tail_u ∧ B in tail_u) / [ P(A in tail_u) · P(B in tail_u) ]`** — the **joint-tail lift**:
> observed joint-corner mass ÷ the mass the *independence* assumption would give it, at declared tail
> quantile `u`, computed on the conditioned (e.g. winter) sample.
>
> - `L = 1` ⇒ extremes are independent (the null / a broken coupling). `L > 1` ⇒ the corner is **fatter
>   than independent** — the killing signature (D1 decile `L = 2.34×`). `L < 1` ⇒ *anti*-coupled in the tail
>   (e.g. D7, relief withdrawn — a value ≪ 1 is itself a hazard flag).
> - **Scale-free and marginal-free** (it is a ratio of probabilities at matched quantiles), so **the same
>   number is comparable across every link** — a weather corner, a residual/price corner, a volume/price
>   corner — which a raw correlation is not.
> - **Relation to the tail-dependence coefficient:** with `p_A = p_B = (1−u)` in the upper tail,
>   `λ ≈ L·(1−u)` (i.e. `L = λ/(1−u)`); `L` is the finite-`u`, small-sample-friendly form of `λ` that
>   survives 21 days where the `u→1` limit does not. Report `L(u)` *with* its `u`; the `L(u)`-vs-`u` curve
>   is the χ(u) diagnostic in lift units.
> - **Multi-link (D6):** define the **end-to-end lift** `L_end` as the terminal-quantity (imbalance cost /
>   price) joint-tail mass ÷ its mass under **independently-fit marginals with the cross-couplings removed**.
>   The compounding claim (cascade §2) is then one testable inequality: `L_end ≥ ∏ L_link ≥ L_A` — the chain
>   *amplifies* the tail, never thins it.

**Why `L` is the right portable choice (over λ or a copula parameter):** (a) it degenerates to a crisp,
mutation-testable **null of 1.0** (a copula parameter has no such universal null); (b) it needs only
counting in a corner — computable on any link with a threshold, no family assumption; (c) it is already the
committed W1_3 statistic, so the whole cascade inherits one comparable measure; (d) it feeds the value
ranking (§5) directly as a multiplier.

**R15 — `L` makes every coupling control able to FAIL.** The killer mutation for *any* link is **break its
coupling** (replace the joint draw with two independent marginal draws; draw price independently of
residual; draw the short-volume independently of the spike; decouple regional from national). Then **`L → 1`
(or `L_end → 1`) and the control MUST fire.** Guards, per the R15 doctrine:
- **TAUTOLOGY:** the checker recomputes `P_joint`, `P_A`, `P_B` **independently** from the generated series
  and compares to an **independent** real-record anchor — never reads back a stored "designed lift"
  parameter (which would always pass).
- **FAIL-OPEN:** an empty conditioned subset, all-equal series, a NaN, or a zero denominator must **fail
  loud**, never pass on a degenerate run.
- **FAIL-SILENT:** if the real-record anchor or the generated series is unavailable, the check is a
  **FAILED** check, never skipped-green.
A single reusable `L` + a single reusable mutation ("cut one link → L collapses → check fires") is the
mechanised core the whole cascade's correlation-fidelity rests on.

---

## 5. Tie to the scoring frame (atom A) and the value/exposure ranking (atom F)

**Why the estimated dependences are what make the worst cell dangerous.** Atom A's fidelity metric is the
**worst-explained cell**, not the population average; the archetype×regime grid's most dangerous regime is
**G3 cold∧still** precisely because *several dependences fire together there*. The estimated **strength** of
each link is the quantitative reason G3 is worst: it is where `L(D1) · L(D5-convexity) · L(D2) · L(D3)`
compound. A grid scored on marginal fidelity would rate G3 "explained"; the joint-tail estimate is what
exposes it as the worst cell. **Estimated dependence strength is thus an *input to the scoring frame's own
severity axis*, not a separate workstream.**

**How strength-of-dependence feeds atom F (value / exposure ranking).** F ranks measured belief-vs-truth
gaps by **value-at-risk**, not gap size. The exposure of a regime factorises, and `L` supplies the middle
term:

> **exposure(regime) ≈ P(joint regime) × severity(covariance in the corner) × book-concentration**

- **P(joint regime)** — the corner mass, `≈ L·P_A·P_B` (the estimated lift *raises* this above the naive
  independent product — G3 is `2.34×` more probable than a marginal model believes).
- **severity** — the £ covariance `E[Δvol · spot]` in the corner (D3), whose *tail* magnitude is exactly
  what average-spot pricing erases.
- **book-concentration** — from the archetype grid (a cold-region-skewed book takes more than national-
  average; W1_4).

So a link's estimated `L` is **load-bearing twice** in F: it scales the *probability* of the dangerous
regime and (via D3's covariance) its *severity*. A link with a high, well-estimated `L` and a large book
exposure ranks **above** a link with a bigger raw gap but a rare, cheap regime — which is precisely F's
"rank by value-at-risk, not gap size" mandate. **The correlation-estimation method is the numerical
supplier to the value ranking**; without it F would rank on gap size (wrong) for lack of a severity weight.

---

## 6. Wall / curriculum (R13, requirement 5) + portability

**The double life of this methodology across the wall — the key framing.** Correlation estimation is used
on **both sides of the epistemic wall, on different information, and the difference IS the gap:**

- **SIM-truth side (HARNESS):** the *true* dependence lives in the SIM's generating process — the latent
  regime chain / copula that produces the cascade — and is **hidden**. The harness may read SIM ground truth
  and estimate the *true* `L` per link (the validation target for the invariants, §4).
- **Company-observable side:** the company **never reads** the generator. It estimates its **own**
  dependence structure from **observables only** — its metered volumes, the published SSP/SBP it is charged,
  purchasable weather outturns/forecasts, its own struck-price ledger — with a **smaller sample, no regime
  label, and every temptation to pool** (the cheapest estimator is a pooled Pearson, which returns `≈0` for
  D1 and drops the D3 covariance). **The company's estimation *error* — believing `L ≈ 1` (independent
  extremes) when the truth is `L = 2.34×` — IS the coupled-triad gap** (`gap_cascade`, cascade §3). This
  atom's methodology is therefore simultaneously (a) the harness's ground-truth measurement tool and (b) the
  *thing the company does imperfectly*, and the delta between the two estimates is the score. A company that
  adopts a joint-tail estimator (this protocol) *closes* its own gap; one that stays on pooled marginals
  carries a large, quantified, persistent gap — the honest finding.

- **Baseline vs curriculum (R13).** The *existence, sign, tail, and strength* of every dependence — the
  `L` values, the winter localisation, the persistence — is **baseline**: estimated from reality, decided
  **blind to company P&L**, changed only for fidelity-to-reality reasons (R12/R13). If the company loses
  money because a faithfully-estimated `L=2.34×` corner showed up, that is a **finding**, never a licence to
  soften the estimate. `L_min` floors and copula-family choices are **baseline-fidelity constants, not
  difficulty dials.** **Which** correlated regimes the company lives through — a 2010-style two-week
  blocking high, a back-to-back dunkelflaute ensemble — is **director-authored, named, versioned
  curriculum**, never agent-tuned toward a gap number. The agent controls both sides of the wall, so the
  *severity diet* must face the director exactly because the estimator is shared.

- **Portability / scale.** Everything is **percentile/quantile-keyed** (tail_u of the conditioned
  distribution), never absolute °C/m/s/£, so a second geography or shifted-climate world re-derives its own
  corners. The statistic `L` is **function-keyed** (any pair of observables with a threshold), carrying no
  GB or fuel-specific term. Cold-season months are a configurable parameter (portability debt if hardcoded).
  **C-S2:** every estimate must be reproducible under deterministic replay — the coupling lives in the
  deterministic latent structure, **not** a shared RNG stream (coupling-via-shared-RNG is the forbidden
  anti-pattern that would make `L` an untestable side effect). **C-S5:** the statistics here are **daily**;
  any L3 claim declares the daily-vs-half-hourly basis as a named simplification (R10).

---

## 7. Open questions / what BUILD needs (unresolvable without network / data / a director call)

1. **Which real series (the biggest one).** Every joint-tail estimate needs, and this fork has none of:
   the **capacity-weighted GB wind-output series** (not the 4-point wind-*speed* proxy — the true `L(D1)`
   is likely **≥** 2.34× since capacity-weighting concentrates the fleet, W1_3 §5.1); real **SSP/SBP**
   cash-out; national **demand + wind + solar** output; **interconnector flows** (D7); and — for D3 — the
   **historical forward-purchase ledger** (struck prices + volumes) and the **metered-vs-hedged-volume**
   series. Route via the discovery-agent against Ofgem/Elexon/NESO/DESNZ at BUILD; **fabricate no figure**
   meanwhile. Each unresolved link is pre-registered as an R10 simplification (§3 step 6).

2. **Sample size / statistical power — the honest limiter.** 21 decile winter days, autocorrelated
   (`~0.78`), gives a tiny *effective* sample; nonparametric `λ` may be unresolvable and CIs wide. BUILD
   calls: block length for the bootstrap; decile-vs-quintile as the *primary* corner (power vs severity);
   whether to borrow strength via a parametric copula (and own the family assumption) or stay nonparametric
   and report wide CIs. The fuller capacity-weighted series (item 1) directly relieves this.

3. **Method-selection call: is cold∧still asymptotically DEPENDENT or strongly asymptotically INDEPENDENT?**
   The χ̄ diagnostic decides whether the SIM needs a tail-dependent copula (t/Clayton) or whether a rich
   latent-regime generator alone reproduces the observed finite-`u` lift. This changes the generator design
   and is unresolvable without the real series — a genuine open modelling question, not a preference.

4. **Copula family / vine per link.** Symmetric-t default vs tail-specific (Clayton lower for D1/D5, Gumbel
   upper for D2/D3) vs a full vine for the multi-link chain (D6). A scope/complexity call under the
   SIMPLICITY GUARD — start with the latent-regime generator + `L` validation, escalate to explicit copulas
   only if `L_end ≥ ∏ L_link` cannot otherwise be met. Declare whichever is deferred as an R10 simplification.

5. **`L_min` / `ρ_min` floors and whether any is a promotion GATE.** The exact fidelity floors per link are
   BUILD calibration decisions against the real series; whether any is an *exit gate* (vs a reported
   diagnostic) is the director/twin's BUILD-open call (Epoch 3). They are baseline-fidelity constants (R13),
   not dials.

6. **Upstream blockers inherited (do not re-discover).** The price-engine SSP recalibration (~10× over,
   carbon term missing — W1_6 / B/C §6) gates the *magnitude* of D2/D3 estimates on generated price; the
   `sim/hedging.py` single-`hedge_price` collapse gates the D3 struck-price ledger. Both are named upstream
   blockers, not new findings — D's *direction* is robust to them; D's *magnitudes* wait on them.

7. **Coupled-triad registration (a BUILD act).** No weather/cascade/cost pair is yet in
   `background/coupled_triad.py::_AUTHORITATIVE_COUPLING`; BUILD registers the pair(s) and adds a
   `coupled_gap_ledger.json` row so the Proof-door panel renders the estimated-`L`-based gap. Off-front until
   the director opens W1.

---

*Sources read/reasoned this pass (no network): `docs/staging/in_progress/DIRECTOR_CAMPAIGN_EPOCH2_COUPLED_WORLD_2026-07-19.md`
(req 4/5, read directly); `docs/design/EPOCH2_COUPLED_WORLD_CAMPAIGN_DECOMPOSITION.md` (atom D homing, deps B/C/W1-cascade);
`docs/design/W1_3_NATIONAL_WEATHER_JOINT_REGIME_DISCOVER.md` (the worked single-link estimator: L=p_joint/(p_a·p_b), decile
2.34×, winter +0.507 vs all-year −0.06, the anti-pooling lesson, persistence 0.78/0.57 — all 4-point-proxy directional
anchors); `docs/design/W1_COUPLED_WEATHER_CASCADE_DISCOVER.md` (the cascade chain, compounding, W1-CASC1/2/3, gap_cascade);
`docs/design/EPOCH2_BC_PRICE_FORMATION_AND_SUPPLIER_COST_DISCOVER.md` (price-as-output, the E[Δvol·spot] covariance as the
key statistical object, BC-1/2/3, hedge-fraction dial); `docs/design/WEATHER_PHYSICS_HIERARCHY_DESIGN.md` §1.4/§3 (latent-
regime mechanism + joint-tail-coverage exit test — cited, not re-derived). Statistical methods (χ/χ̄ tail diagnostics,
tail-dependence coefficient λ, Gaussian/t/Clayton/Gumbel/vine copulas, POT-GPD / block-maxima EVT, block bootstrap,
profile-likelihood CIs) are standard extreme-value / copula theory; any specific literature attribution is from recall and
flagged for BUILD-time verification of exact formulae. All external market/data anchors flagged `[recall — verify at BUILD]`;
no market figure fabricated (Historical Ground Truth). R10/R12/R13/R15, COUPLED_TRIAD, C-S2/C-S5, epistemic wall referenced
inline. Provenance: proposal; no level claimed.*
