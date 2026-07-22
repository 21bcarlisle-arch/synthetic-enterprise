# Forward-Discovery Register — thinking ahead, ranked

**Established:** 2026-07-21 (DIRECTOR_STEER_FORWARD_DISCOVERY_REGISTER_2026-07-21).
**Class:** OPTIONAL / PREEMPTIBLE (resource-aware scheduling). These tracks soak spare capacity and
**yield instantly to core campaign work** — thinking-ahead never competes with building.
**Discipline:** DISCOVER only. No builds, no new map atoms beyond a track's own register entry, until a
track **graduates by explicit director steer**. Independence + no-personal-data rules apply throughout.

## The ranking principle — certainty × mission-criticality

Thinking ahead is worth fidelity budget only for futures ranked high on **both** axes. Classes (director's):
- **Certain** — every possible world contains it (EV/heat-pump growth, smart-meter completion, warming winters). *W1_10 was this, done right.*
- **Committed** — legislated, dated, live programme (e.g. market-wide half-hourly settlement).
- **Mission-required** — capabilities the ratified purpose cannot function without.
- **Contingent policy** — may never happen (zonal pricing, further cap-reform shapes) → **watching brief only, one line, never a build.**

| rank | track | class | criticality | status |
|---|---|---|---|---|
| **F1** | Simulating conversations | mission-required | **highest** — the pitch's core abatement mechanism | DISCOVER pass done 2026-07-22 |
| **F2** | Explaining what we do, simply | committed (legal duty) | high — comprehension = valid consent + trust | DISCOVER pass done 2026-07-22 |
| **F3** | Volunteer programme mechanics | mission-required | high — critical path to any real household | skeletal, this pass |
| **F4** | International expansion probe | aspirational | medium — tests the "global by design" claim | skeletal, this pass |
| **F5** | Simulated competitor field | mission-required | high — pricing/retention are meaningless unopposed | skeletal, this pass |
| — | *Watching briefs (contingent policy)* | contingent | low | see bottom |

---

## F1 — Simulating conversations *(highest)*

**Purpose.** The pitch's core claim is that **tone, timing and channel ARE the abatement mechanism** — yet
the sim has no conversations: customers don't respond to messages, the company doesn't generate them. Both
sides need designing. This is the missing loop between the engagement-axis *traits* (already estimated in the
segmentation work) and actual *behaviour change*.

**Key DISCOVER questions.**
- What real UK supplier↔customer conversation looks like: contact rates, complaint taxonomies, CSS / Ofgem
  complaints-handling benchmarks, tone-of-voice evidence, channel mix by segment.
- How a message→behaviour response could be modelled against the engagement axes already estimated
  (channel preference, trust, engagement capacity — conversation-revealed traits).
- The epistemic wall here: **the company observes replies and outcomes, never true intent.** A modelled
  customer has an internal state; the company only ever sees what it says/does. Getting this wall right is
  the whole point (a supplier that "reads intent" is a leak).

**Initial scaffolding (not findings — no research run yet).** Two designs are needed: (a) a *company* message
generator keyed to segment + situation; (b) a *customer* response model mapping (message, trait, state) →
action + reply. Anchor generation to real contact/complaint data; validate against an **independent** source
(never SIM ground truth). **Directly serves segmentation:** channel-preference and trust are conversation-revealed.

**Tag:** mission-required × highest. **Status:** DISCOVER pass done (2026-07-22) —
`docs/market_research/f1_simulating_conversations.md`.

**Finding (2026-07-22 tick).** The pitch's premise is **externally corroborated**: Which? 2025 shows a **~6×
complaint-ratio spread** across suppliers on the same regulated product (Octopus 261 vs 1,525 complaints/100k) —
tone/handling IS a real differentiator, not a nicety. The message→behaviour edge already has a benchmark library
(`NUDGE_PHYSICS_BENCHMARKS.md`: debt-letter **tone +3 to +10pp**, framing 10–35%, anchoring 8–20%), wired to the
two hidden conversation traits **FramingSusceptibility / ToneSusceptibility** (`nudge_physics.py`, independent
per-customer draws — no demographic cross-tab exists, §2.3, so susceptibility is an irreducible latent). The
**epistemic wall** is the whole point: SIM holds true susceptibility, COMPANY may only hold a **Bayesian belief
updated on observed replies** (a conversation adds message-response/latency-by-channel as the new observable
stream); a company whose action correlates with the true trait beyond what replies justify is an **intent-leak
the harness must catch (R15 mutation lever)**. Direction validated across **three disjoint sources** — Which?
complaint spread, behavioural-economics causal effects, Ofgem CSAT Wave 20 payment-channel×satisfaction (DD 82% /
prepay 80% / std-credit 76%) — none SIM ground truth; **magnitudes are mostly cross-domain imports** (only Opower
+ UK switching are energy-native), so a build samples magnitude from a distribution (R10 simplification), not a
point estimate. Candidate graduation = the **SIM-response / COMPANY-generator+estimator / HARNESS-gap coupled
triad**; **no atom opened** (director/twin BUILD-open call). Two open items are **network-gated** (`[recall,
validate]`): complaint-**category** taxonomy (Energy Ombudsman / Ofgem league tables) and a UK-energy tone→outcome
study — recorded so they are not re-searched fruitlessly. **No further autonomous DISCOVER increment on F1 without
network** — next tick should draw F3 or F4 (both still skeletal) or await director graduation.

## F2 — Explaining what we do, simply

**Purpose.** Comprehension is a **legal duty** (consent that wasn't understood isn't consent — Consumer Duty),
not a nicety, and a trust mechanism. Feeds F3 (volunteer) and the site.

**Key DISCOVER questions.** Plain-language standards (CMA/FCA Consumer Duty comprehension-testing practice,
energy-sector precedents); a **testable bar** — can a lay reader say back what Poesys does with their data and
money; where the current site/pitch fails that bar.

**Tag:** committed (legal) × high. **Status:** DISCOVER-complete (2026-07-22) —
`docs/market_research/f2_explaining_what_we_do_simply.md`. The one open item (validate the six
comprehension-testing standards) was re-tested by an exhaustive corpus sweep on the second 2026-07-22
tick and confirmed **not closable without a live fetch** (no independent repo source exists); recorded
so it is not re-run. **No further autonomous DISCOVER increment on F2 without network** — next tick
should draw another track (F1/F3/F4) or await director graduation.

**Finding (2026-07-22 tick).** F2 fails on the **reader, not the writing**: the live public surface
(`site/index.html`) is a correct *expert* pitch — "Where to go" doors keyed *"Energy CEO / COO"*,
≥6 un-glossed domain terms in the lede ("enterprise simulator", "settles half-hourly", "Elexon and
NESO", "£/tCO₂") — and **no lay-household comprehension surface exists**, so the legal-duty question
"can a reader say back what we do with their **data** and **money**" is currently unanswerable. No
live-consent breach (Poesys holds no household data — F3 gates that); this is *forward* discovery of
the **testable bar** the register asked for. Proposed bar = a **teach-back / say-back test** over four
items (data / money / commitment-and-leaving / human-accountability), **two-tier so it can FAIL
(R15)**: Tier-1 mechanical readability + banned-jargon floor (today's front-door prose must go red),
Tier-2 lay-persona say-back judge (outcome-tested). The **data-consent trap**
(`smart_meter_hh_data_consent_2026.md`), the **SLC money-disclosure floor** (`company_customer_comms.md`)
and **credit-balance ring-fencing** (`ofgem_licence_readiness.md`) are **validated** against independent
already-fetched repo sources; the comprehension-testing *standards* (FCA Consumer Duty PRIN 2A, GDS
reading-age-9, UK GDPR Art. 12(1), CMA EMI) remain `[recall, validate]` pending a live fetch. Candidate
graduation = **harness bar before site page**, gating F3's consent screens; **no atom opened** (director/
twin call). The one lay-facing line the site already gets right — up-front human accountability — must be
preserved.

## F3 — Volunteer programme mechanics

**Purpose.** The pitch makes "will not open until a security-posture review has completed" a public gate — but
no atom exists behind it. This is the **critical path to any real household**.

**Key DISCOVER questions.** What that security review must cover; consent + data-handling design (GDPR lawful
basis, revocation, data minimisation); the smallest honest volunteer pilot. **Design the consent machinery;
hold no data.**

**Tag:** mission-required × high (gated on the security review). **Status:** skeletal.

## F4 — International expansion probe

**Purpose.** The pitch asserts "global by design"; §13 admits transfer is unproven. Produce **evidence for or
against** the transferability claim — not a market-entry plan.

**Key DISCOVER questions.** Pick ONE candidate second market; enumerate concretely what varies (market
structure, settlement, tariff regulation, data availability, consumer protection); assess which variations the
architecture's parameters absorb vs which break assumptions. (Ties to the standing portability constraints.)

**Tag:** aspirational × medium. **Status:** skeletal.

## F5 — Simulated competitor field

**Purpose.** Already flagged as an Epoch-2 gap: pricing/retention decisions currently face **no opposition**, so
they're not yet meaningful.

**Key DISCOVER questions.** The minimum competitor model that makes pricing/retention meaningful
(tariff-following vs strategic entrants), anchored to **real switching-market behaviour**.

**Tag:** mission-required × high. **Status:** DISCOVER pass done 2026-07-22 — `docs/market_research/f5_simulated_competitor_field.md`.

**Finding (2026-07-22 tick).** The competitor field is a **scalar, not a field**: best-alternative rate
is a fixed historical series (`simulation/market_switching_propensity.py::MARKET_SAVINGS_BY_YEAR`,
company-side `market_conditions.py::MARKET_SWITCHING_MULTIPLIER_BY_YEAR`), so pricing/retention face a
*non-reactive* opponent. The observable-tariff wall is already correct (`company/market/tariff_benchmarking.py`,
public sources only) — the missing piece is a *response edge*. Minimum useful model = a cap/wholesale-endogenous
**tariff-follower band** + 1–3 **regime-gated strategic archetypes** (Era A challenger-boom vs Era B
post-consolidation). Candidate coupled-triad shape proposed in the artefact; **no atom opened** (BUILD-open is a
director/twin call). Market **structure** figures (29 failures / ~4M / ~£2.7bn SoLR / post-2023
re-fixing) **validated** on the 2026-07-22 tick against ≥3 independent already-fetched repo sources
(not SIM ground truth); only per-supplier **% shares** remain `[recall, validate]` pending a live Ofgem
*State of the Market* fetch.

---

## Watching briefs — contingent policy (one line each, never a build)

- **Zonal / locational marginal pricing (REMA).** REJECTED in reality — DESNZ chose Reformed National Pricing
  on 2025-07-10; zonal is a declined counterfactual. GB single-national-price baseline already matches the
  decided regime. **Only ever a director-authored R13 curriculum scenario, never a baseline.** Atom
  `W1_8_zonal_locational_pricing` closed 2026-07-21. Evidence: `docs/market_research/REMA_ZONAL_PRICING_DISCOVER.md`.

*(Add contingent-policy items here as one-liners; add forward tracks above on the same certainty × criticality
test. The director invites additions.)*
