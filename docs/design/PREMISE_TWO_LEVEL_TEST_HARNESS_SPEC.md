# PREMISE TWO-LEVEL TEST — harness spec (doc-only)

**Status:** FRAME output, deliverable 3 of `docs/staging/ADVISOR_DISCOVERY_PREMISE_FABRIC_PHYSICS_2026-08-03.md`.
Companion: `docs/design/PREMISE_FABRIC_PHYSICS_DISCOVER.md`. Target atom: `H_GAP_fabric_belief_truth_gap`.
**No test code is written by this pass.** This specifies what the tests must assert, what makes each
one failable, and what it is anchored to.

---

## 0. Purpose, guarantees, and why (OPS1 standard — state these first or delete the mechanism)

**Purpose.** Make "are these premise traces realistic?" a *falsifiable, standing, automated*
question, so an Expert Hour can **fail** it, instead of a question a director has to answer by eye
once and then re-answer six months later.

**Guarantee.** If the premise generator produces traces that are too smooth at the individual level,
insufficiently diverse at the crowd level, or unable to represent an empty house, this suite goes
red and names which of the two levels failed and on which statistic.

**Why it is needed and why now.** `observed-in-code` — the existing premise-demand controls
(`simulation/premise_demand.py`: `reconciliation_residual`, `aggregate_reconciles`,
`noise_is_unbiased`) are all **level-and-sum** controls. They are genuine and R15-failable, and they
are all blind to texture, timing, trough behaviour and diversity. `W1_5_premise_demand_shape`
consequently sits at **L3** while failing both levels of a test a director applied by eye
(`observed-in-report`, 2026-08-03). The controls were not wrong; the control *set* had a hole
exactly the shape of this defect.

**The birth condition, and it is the most important sentence in this spec:**
**this suite must be landed RED against the current generator.** A control introduced already-passing
has demonstrated nothing (R15). Every threshold below is stated with the currently-observed value
alongside it, so the first run's failure is predicted, specific and checkable. If any statistic
below unexpectedly *passes* on the current generator, that statistic is mis-specified — fix the
statistic, do not celebrate the pass.

---

## 1. Level 1 — individual homes must be spiky

Scope: a single premise's half-hourly trace, evaluated per commodity, over at least one full year.

| # | Statistic | Definition | Current value (`observed-in-report`) | Requirement | Anchor |
|---|---|---|---|---|---|
| L1.1 | **Half-hourly texture** | median \|x[t] − x[t−1]\| ÷ mean(x), per home per year | **0.008–0.012 kWh on a ~0.7 kWh mean ≈ 1.5%** | materially higher; **target band to be pinned from SERL/LCL before the test is asserted** — `domain-knowledge` puts real individual-home electricity in the tens of percent, order 20–40%, *not* 1.5% | SERL published statistics; LCL fallback |
| L1.2 | **Day-to-day shape correlation** | Pearson r between consecutive days' 48-vectors, normalised to daily total (so the test is about *shape*, not weather-driven level); report the median over the year | **0.97** | materially below; band from anchor. Must remain **seasonally conditioned** — winter days legitimately correlate more than shoulder days | SERL / LCL |
| L1.3 | **Trough behaviour** | min half-hour per day; count of days per year with a sustained low block (≥ 6 consecutive periods below a low-usage threshold) | **no half-hour below 0.05 kWh in ten years; zero away-days** | an empty house must be **representable and present** — a non-zero count of away/holiday days per year | ONS/BEIS holiday-taking `domain-knowledge`; SERL absence statistics |
| L1.4 | **Weekday/weekend distinguishability** | a classifier (or simple shape distance) must separate weekday from weekend days above chance | not reported; `inferred` — currently driven only by the PC1 (season, day-type) column, so it is *present but identical for every home in the country* | present **and varying between homes** | SERL |
| L1.5 | **No repeating rescaled fractions** | count of distinct values of `x[t] ÷ daily_total` across the year, and the maximum multiplicity of any single value | **repeating values observed** — the signature of one deterministic base shape | multiplicity must fall to near-1; this is a **structural** check, not a statistical one | none needed — it is a self-evident artefact detector |

**L1.5 is the sharpest control in the suite** and deserves its own note: it detects the *mechanism*
of the defect rather than its symptom. Any generator that rescales a fixed base shape by scalars
will produce a small set of repeated normalised fractions no matter how much level noise is added.
It therefore cannot be passed by sprinkling noise on the current architecture — only by actually
generating shape per home. It is cheap, deterministic, and near-impossible to game.

---

## 2. Level 2 — crowds must smooth

Scope: aggregates of N premises drawn from the population, for N across at least
{1, 3, 10, 30, 100, 300, 1000}.

| # | Statistic | Definition | Current value (`observed-in-report`) | Requirement | Anchor |
|---|---|---|---|---|---|
| L2.1 | **Smoothing curve** | aggregate peak÷mean as a function of N | **5.9 at N=3 vs 5.7 at N=1 — aggregation smooths nothing** | must fall **monotonically and materially** with N and flatten toward the published class average at large N | Elexon PC1 GAD as the large-N limit (independent: it is no longer a generator input) |
| L2.2 | **Between-home correlation** | pairwise Pearson r between homes' traces, distribution across pairs | **C8–C9 = 0.95 (near-clones)** | median pairwise r must be far lower; weather-driven common mode is legitimate, so the test measures r on the **weather-conditioned residual**, not the raw trace | SERL diversity statistics |
| L2.3 | **Timing diversity** | dispersion of each home's heating-start and evening-peak half-hour across the population | **identical block timing (`HEATING_PERIOD_WEIGHTS` is one national constant — `observed-in-code`)** | a genuine distribution with material spread, not a point mass | SERL |
| L2.4 | **Between-home scale spread** | distribution of annual kWh across the population; report the interquartile ratio and the P10/P90 ratio | **annual totals within 8% of each other (11.8–12.8k kWh)** | must span the real UK range across property types and household sizes | **NEED** (EPC-linked actual metered annual consumption) |
| L2.5 | **Aggregate still reconciles** | the existing `premise_demand.aggregate_reconciles` invariant | passes | **must continue to pass** — this is the regression guard on the work already done at W1_5 | existing control, retained |

L2.5 exists to make the trade-off explicit and enforced: **added realism must not cost aggregation
consistency.** A new generator that produced beautiful individual traces but broke the national
reconciliation would be a regression, and the suite must say so rather than leaving it to judgement.

---

## 3. Gas — held to daily-resolution targets

Per `PREMISE_FABRIC_PHYSICS_DISCOVER.md` §3.1: **half-hourly by construction, daily by evidence.**

| # | Statistic | Requirement | Anchor |
|---|---|---|---|
| G.1 | Annual level and its spread by property type × age band × floor-area band | within anchor band | **NEED** |
| G.2 | Winter/summer ratio | `observed-in-report` — currently ~4.6× for dual-fuel homes and **already good**; must not regress | existing + NEED |
| G.3 | HDD-response gradient (kWh per degree-day, per home) | must **vary between homes** with fabric — today it is one national constant (`GAS_HEATING_KWH_PER_DEGREE_DAY = 8.0`, `observed-in-code`) | NEED / RdSAP cross-check |
| G.4 | Day-to-day variability of daily totals | non-degenerate; consistent with anchor | NEED / published daily gas profiles |
| G.5 | Half-hourly gas texture | **NOT asserted — registered as an unvalidated simplification** on the atom | *(none available; claiming it would be unfalsifiable)* |

G.5 is a deliberate, recorded refusal to claim fidelity without an anchor, not an oversight.

---

## 4. R15 — how each control is proven able to fail

No statistic above counts as evidence until a **mutation test** proves it fires on its own named
defect. The named mutations:

| Control | Mutation that MUST make it fire |
|---|---|
| L1.1 texture | replace the generated trace with its own 7-day rolling mean (smooth it) |
| L1.2 day-to-day correlation | replay a single day's shape for the whole year, rescaled by daily total |
| L1.3 troughs | floor every period at a small positive value (removes the empty house) |
| L1.4 weekday/weekend | shuffle day-types |
| L1.5 rescaled fractions | **the current generator itself is the mutation** — this control's first run against the shipped path is its own mutation test |
| L2.1 smoothing curve | give every home an identical shape (clone one home N times) |
| L2.2 between-home correlation | as L2.1 |
| L2.3 timing diversity | collapse all heating-start times to one value (i.e. reinstate `HEATING_PERIOD_WEIGHTS`) |
| L2.4 scale spread | set every home's annual total to the population mean |
| L2.5 reconciliation | perturb one region off-manifold (existing mutation, already proven) |

**Three fail-open patterns to defend against explicitly** (R15 doctrine), because this suite is
statistical and therefore unusually exposed to all three:

1. **FAIL-OPEN on empty input** — a statistic computed over zero homes, zero days, or a
   missing/short trace must **FAIL**, never pass vacuously. Every statistic asserts its own input
   sufficiency first (minimum home count, minimum day count) and errors if unmet.
2. **NaN-blindness** — comparison guards are NaN-blind (a known class in this codebase). Every
   statistic must **reject non-finite values FIRST**, before any threshold comparison. A trace
   containing NaN is a failure, not a pass.
3. **TAUTOLOGY** — no statistic may be computed against a reference derived from the generator's
   own inputs. This is why PC1 moves from generator *input* to validation *target* (§L2.1): as an
   input it made the check tautological; as an output-only anchor it is independent. Any future
   change that reintroduces PC1 as a per-home input silently re-tautologises L2.1 and must be
   caught at review.

---

## 5. Reporting and thresholds

- **Every threshold is a DIAGNOSTIC BAND, never a target (R12).** A statistic drifting toward its
  band edge triggers R4 (diagnose the mechanism), never a tuning pass on the generator to bring
  the number back inside. This warning is not decorative: this suite is unusually *easy* to
  goal-seek, because injecting noise moves L1.1 without making anything more real. **L1.5 is the
  structural guard against exactly that** — it fails a noise-injected fake even when L1.1 passes.
  If L1.1 passes while L1.5 fails, the correct reading is "someone tuned the number", and the
  suite should say so in those words.
- Bands are **calibrated blind to company P&L** (R13). This is baseline fidelity work.
- Report per-statistic: value, band, anchor, and pass/fail — **worst-cell**, not average. An
  average across homes would hide the exact clone-cluster the test exists to find.
- Output lands in the coupled-gap ledger alongside the other coupled-triad gap metrics, so the
  fabric belief-vs-truth gap (`PREMISE_FABRIC_PHYSICS_DISCOVER.md` §5) is reported next to it.

---

## 6. Expected first result (the prediction this spec is accountable to)

Run against today's generator, this suite should fail **L1.1, L1.2, L1.3, L1.5, L2.1, L2.2, L2.3
and L2.4**, and pass **L2.5** and **G.2**. If it does not fail in roughly that pattern, the
spec is wrong and gets fixed before any generator work starts.

---

*Doc-only. No test code written, no map level moved.*
