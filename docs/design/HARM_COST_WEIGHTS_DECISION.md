# HARM-COST WEIGHTS — a single decision for the director

**Status:** DECISION FRAMING (doc-only). Prepared per `docs/staging/JUDGING_THE_JUDGES.md`
Part 2 (P1) and the atom **A7 harm-weights-decision**. This document FRAMES a decision;
it does not make it. The numbers are the director's.

**What this decides:** the harm-cost matrix `C[q, q̂]` in `COUPLED_TRIAD_DESIGN.md` §1.4(a) —
the weights that turn the belief-vs-truth **gap** of the can't-pay/won't-pay 2×2 (W2_7 ⇄ C9)
into a **score**. These are **R13 CURRICULUM, not baseline**: they encode how much the
director cares about vulnerable-treated-as-strategic versus the reverse. Per R13 and
DIRECTOR_TWIN Law B they must be **director-authored, named, versioned** — never agent-tuned
toward a gap number. **Nothing in this doc has been calibrated against any gap output.** The
recommended ratio below is derived from the asymmetry of *real-world consequences* and an
explicit values-uplift, and from nothing else. Placeholders stay until the director signs.

---

## 0. The thing being weighted (the 2×2, restated)

One account is in arrears. Hidden truth is its quadrant on ABILITY × WILLINGNESS. For the
collections *action* choice only two states matter; collapse to them:

- **True CAN'T-pay** — genuinely cannot pay (income shock, essential-cost floor breached).
- **True WON'T-pay** — able but unwilling (strategic non-payer).

The company chooses **PURSUE** (aggressive collections: DCA, CCJ, warrant PPM, disconnection
threat) or **FORBEAR** (ability-to-pay repayment plan, hardship support, paused collection).
Two of the four cells are the *correct* action and cost ≈ 0 (pursue a true won't-pay = debt
recovered; forbear a true can't-pay = right thing, debt was unrecoverable anyway). The two
error cells are what we weight:

| | true CAN'T-pay | true WON'T-pay |
|---|---|---|
| **PURSUE** | **HARM** = `H` | 0 (correct: recovered) |
| **FORBEAR** | 0 (correct: appropriate) | **LOSS** = `L` |

- **HARM (`H`)** — aggressive collections against someone who genuinely cannot pay:
  ability-to-pay-rule breach (SLC 27.8), Consumer Duty breach, vulnerability harm,
  complaints, redress, Ofgem enforcement, **licence tail risk**.
- **LOSS (`L`)** — soft treatment of a strategic non-payer: bad debt, moral hazard,
  revenue leakage.

The single number the director sets is the **ratio** `R = H / L`.

---

## 1. Anchor set — HARM side (real consequences, from the repo)

Anchored to `docs/market_research/company_debt_management.md` §3 (the 2023 PPM-warrant
scandal) and `docs/design/CHARTER_W2_AFFORDABILITY.md` (OVO self-disconnection settlement).
These are the real face of "pursued someone who couldn't pay."

| Real consequence | Figure | Source (in repo) |
|---|---|---|
| British Gas PPM-warrant settlement | **£20m to Ofgem redress fund + £70m debt written off** for vulnerable customers (£90m total) | `company_debt_management.md` §3 |
| Industry warrant installs under scrutiny | **94,000 PPMs installed under warrant 2018–2023** (British Gas, Scottish Power, OVO ≈ 70%) | same |
| All-supplier response | **All major suppliers paused warrant PPM installs, Feb 2023** — a regulator-forced industry-wide halt | same |
| Cost of the *forced* forbearance that followed | **≈ £25m/month additional bad debt (Feb–Sep 2023)** during the moratorium | same |
| Live enforcement precedent | **Ofgem investigation + settlement with OVO** for failing to support self-disconnecting PPM customers | `CHARTER_W2_AFFORDABILITY.md` §W2_8 |
| Who is exposed | 47% of PPM customers in lowest income quintile; 23% have a disability/long-term health condition | `company_debt_management.md` §3 |

**Why the harm weight must exceed the directly-monetised figure.** The £90m British Gas
number is *settled redress + write-off only*. It does not price: (i) the **licence tail** —
enforcement can run to a licence revocation, an existential event, not a line-item cost;
(ii) the **industry-wide moratorium** a scandal triggers (≈£25m/month borne by everyone,
including compliant suppliers); (iii) **unmonetised vulnerability harm** to a disabled or
fuel-poor household left without supply. A weight set only to the settlement figure
systematically *under*-weights harm.

> **[DIRECTOR / NETWORKED-CHECK NEEDED — placeholder H1]** A clean **per-wrongful-case**
> redress figure (settlement ÷ number of genuinely-wrongful cases) and a **licence-loss tail
> probability** are not derivable from the repo. The £90m is an aggregate over years and an
> unknown wrongful-case count. Do not invent the per-case number — it needs a live external
> source or the director's own figure.

---

## 2. Anchor set — LOSS side (real consequences)

Anchored to `company_debt_management.md` §1/§5 and ASSUMPTIONS.md. This is the real face of
"went soft on someone who could have paid" — and it is **also lethal**.

| Real consequence | Figure | Source |
|---|---|---|
| National domestic energy debt stock | **£4.43bn (June 2025)**, up 71% since 2023 | `company_debt_management.md` §5 |
| Share with no repayment plan | **~75% of that £4.43bn** sits with customers on no plan | ASSUMPTIONS.md (Citizens Advice/Ofgem) |
| Ultimate write-off | **£1.1–1.7bn/yr (~⅓ of stock)**; blended ultimate loss ~30–35% of aged receivables (historic normal 5–10%) | `company_debt_management.md` §1/§5 |
| Bad-debt rate by channel | ~1% (DD) vs ~6% (standard credit) of bills | ASSUMPTIONS.md; `company_debt_management.md` §5 |
| Average arrears (no plan, elec) | **£1,773**; on-plan average £799 | `company_debt_management.md` §7 |
| **The lethal endpoint** | **~30 UK suppliers failed in 2021–22** — bad debt + unhedged exposure central | Well-established public fact (2021–22 UK retail crisis) |

**Why the loss weight can never be zero.** A supplier that forbears universally converts its
entire arrears book to bad debt. At a ~30% ultimate loss rate on a rising national stock,
this is not a rounding error — it is the **2021–22 failure mode**. ~30 suppliers died of
exactly this (compounded by unhedged wholesale exposure). If `L` is set so low that pursuit
is never worthwhile, the company dies of the *other* cause. Both deaths are real.

---

## 3. The decision rule and the flip-point (derived analytically)

Let `p = P(account is genuinely CAN'T-pay | observables)` — the classifier's posterior.
Expected costs:

```
E[cost | PURSUE ]  = p·H + (1−p)·0 = p·H
E[cost | FORBEAR]  = p·0 + (1−p)·L = (1−p)·L
```

**Optimal policy — PURSUE iff `E[cost|PURSUE] < E[cost|FORBEAR]`:**

```
p·H < (1−p)·L   ⟺   p/(1−p) < L/H   ⟺   p < 1/(R+1)          where R = H/L
```

So there is a single **pursue threshold on classifier confidence**:

> **PURSUE an account only if `p < p* = 1/(R+1)`** — i.e. only if the classifier is at least
> `R/(R+1)` confident the account is a *strategic* (won't-pay) non-payer. Otherwise FORBEAR.

### 3.1 THE FLIP-POINT (the interesting number)

Hold an account's confidence `p` fixed and ask: *at what ratio `R` does its optimal action
flip from PURSUE to FORBEAR?* Set `p = 1/(R*+1)` and solve:

```
R*(p) = (1 − p) / p          — the ODDS the account is a strategic non-payer
```

**The headline number: for the genuinely-ambiguous account (`p = 0.5`), `R* = 1`.** Above a
mere **1:1** harm:loss weighting, *every account you cannot classify better than a coin-flip
should be forborne.* Pursuit must be **earned by classifier confidence** — it is never the
default once harm outweighs loss even slightly. This is the single most decision-relevant
fact in the pack: the interesting action is not "how hard do we chase" but "how sure must we
be before we chase at all," and that bar is set entirely by `R`.

The flip is per-account (it is a function of `p`), which is exactly the trade-off the
director's cat-and-mouse amendment demands — closing the harm gap (raise `R`) opens the loss
gap (more won't-payers forborne), and where the company sits on that frontier **is** its
strategy.

**Assumptions behind the flip-point (stated, per the task):**
1. Two-state collapse (can't/won't); the two "will-pay" quadrants resolve on their own and
   carry ≈0 action cost.
2. Correct-action cells cost ≈0 (recovered debt nets the collection cost; appropriate
   forbearance on a true can't-pay loses nothing recoverable). Relaxing this shifts `p*`
   slightly but not the *shape*.
3. `H` and `L` are per-account expected costs in the same units. The whole result is a pure
   function of their **ratio** `R`, so the director need only set one number, not two.
4. A single account, risk-neutral expected-cost minimisation. Portfolio/tail-risk aversion
   (a licence event is ruin, not a cost) would push the effective `R` *higher* still — an
   argument for the recommended asymmetry, treated in §5.

---

## 4. Policy at the extremes (what each ratio BECOMES)

| Ratio `R = H/L` | Pursue threshold `p* = 1/(R+1)` | The optimal policy becomes… |
|---|---|---|
| **R → 0** (harm ignored) | `p* → 1` | **Pursue everyone.** The 2018–2023 warrant-PPM regime. Lethal via redress/enforcement/licence (British Gas £90m; industry moratorium). |
| **R = 1** (symmetric) | 0.50 | Pursue any account more-likely-than-not strategic. Coin-flip bar. Already forbears every truly ambiguous case. |
| **R ≈ 5–10** (recommended, §5) | 0.09–0.17 | **Forbear unless confidently strategic** — pursue only ~top-decile-confidence won't-payers. The defensible Consumer-Duty-era frontier. |
| **R → ∞** (harm infinite) | `p* → 0` | **Never pursue anyone.** Bad debt → 100% of arrears; the 2021–22 insolvency mode (~30 suppliers). Lethal via the *other* cause. |

The advisor's stated shape holds mechanically: **infinite `R` is a death**, not a safe choice.
A weighting that makes one of the two real deaths impossible has removed a truth from the world.

---

## 5. Recommended ratio (advisor's recommendation — director decides)

**Recommend a central `R ≈ 8 : 1` (harm : loss), within a defensible band of ~5:1 to ~10:1.**
Rationale, in two honest layers:

1. **Directly-monetised layer (derivable, ~1:1 to ~3:1).** Per-case redress+write-off on the
   harm side and per-case bad-debt write-off on the loss side are the *same order of
   magnitude* (£1k–£2k arrears write-off vs a per-case redress that placeholder **H1** leaves
   open but is plausibly single-digit-thousands). On *directly-monetised numbers alone* the
   ratio is only mildly asymmetric.
2. **Values-uplift layer (the director's call).** The recommended ratio sits **above** the
   directly-monetised ratio to price what the settlement figure omits: the **licence tail**
   (ruin, not a cost line), the **industry-moratorium externality**, and **unmonetised
   vulnerability harm**. Lifting ~1–3:1 up to ~8:1 is a *values* decision — R13 curriculum,
   the director's by right — not a calculation. It is deliberately **not infinite**: at
   `R ≈ 8`, `p* ≈ 0.11`, i.e. *"pursue only when ≥89% confident the account is strategic; else
   forbear,"* which chases the clearest strategic non-payers while forbearing everyone
   genuinely in doubt — and keeps the loss death on the table.

**This is not tuned to any gap value.** If `R = 8` produces an "ugly" gap number for W2_7 ⇄ C9,
that is a finding about the company's classifier, not a reason to move the weight (R12/R13).

---

## 6. Sensitivity table (the pursue bar as `R` moves)

`p* = 1/(R+1)`; "confidence to pursue" = `R/(R+1)`.

| `R = H/L` | Pursue threshold `p*` | Must be this confident it's strategic to pursue |
|---:|---:|---:|
| 1 | 0.500 | 50% |
| 2 | 0.333 | 67% |
| 4 | 0.200 | 80% |
| **6** | **0.143** | **86%** |
| **8** (recommended) | **0.111** | **89%** |
| **10** | **0.091** | **91%** |
| 15 | 0.063 | 94% |
| 20 | 0.048 | 95% |
| 50 | 0.020 | 98% |
| 100 | 0.010 | 99% |

The bar climbs steeply then flattens: most of the harm-avoidance is bought by the first move
from `R=1` to `R≈8` (50% → 89% confidence bar); pushing `R` from 20 to 100 barely moves the
bar (95% → 99%) while it quietly removes the loss death entirely. This is the concrete case
for **heavily asymmetric but bounded**.

---

## 7. The single decision

> **Set `R = H / L`, the harm:loss ratio for the can't-pay/won't-pay collections 2×2.**
> Advisor recommends **≈ 8:1** (band 5:1–10:1). This fixes the pursue bar at
> `p* = 1/(R+1)` — at 8:1, *pursue only when ≥89% confident an account is a strategic
> non-payer, else forbear.* Both failure modes stay lethal by construction (`R` finite and
> `> 0`). The matrix `C[q, q̂]` then encodes `C[cannot, won't] = H`, `C[won't, cannot] = L`,
> diagonal = 0, feeding `COUPLED_TRIAD_DESIGN.md` §1.4(a) and the W2_7 ⇄ C9 gap.

**Open items requiring the director or a networked check (placeholders, not invented):**
- **[H1]** Per-wrongful-case redress figure and licence-loss tail probability (§1) — needed
  to firm up the directly-monetised layer of §5; repo has only the £90m aggregate.
- **[R]** The ratio itself (§5) — R13 curriculum, director-authored and versioned.

Until the director signs, `C[q, q̂]` ships **formula-with-placeholder-weights** (the recommended
`R≈8` as a labelled provisional), never invented final weights, and is never moved to flatter a
gap number.

---

*Sources: `docs/market_research/company_debt_management.md`; `docs/design/CHARTER_W2_AFFORDABILITY.md`;
`docs/market_research/ASSUMPTIONS.md`; `docs/design/COUPLED_TRIAD_DESIGN.md` §1.4(a);
`docs/staging/JUDGING_THE_JUDGES.md` Part 2; `docs/staging/THE_COUPLED_TRIAD.md`. Governed by
R12 (anti-goal-seek), R13 (baseline/curriculum split), DIRECTOR_TWIN Law B. Doc-only; no code,
no maturity_map.yaml, no CLAUDE.md, no supervisor touched.*
