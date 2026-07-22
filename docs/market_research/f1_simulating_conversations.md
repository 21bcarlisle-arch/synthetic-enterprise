# F1 — Simulating conversations — first DISCOVER pass

**Track:** Forward-Discovery Register F1 (mission-required × highest). **Class:** OPTIONAL / PREEMPTIBLE.
**Discipline:** DISCOVER only — no BUILD code, no new map atoms; anchor to already-fetched repo sources,
validate against an INDEPENDENT source (never SIM ground truth), honour the epistemic wall.
**Pass:** 2026-07-22 (scheduled forward-discovery tick, core + idle-advance lanes empty/gated).
**Network:** none this pass (autonomous, no interactive user — per standing memory `no-network-in-autonomous-runs`);
all figures are re-cited from sources fetched by prior passes, not re-fetched. Absence of a finding below is
labelled a genuine gap `[recall, validate]`, never presented as fact.

---

## Why this track ranks highest

The pitch's core claim is that **tone, timing and channel ARE the abatement mechanism** — yet the sim has no
conversations: customers don't respond to messages, the company doesn't generate them. F1 is the missing loop
between the engagement-axis *traits* (already estimated in the segmentation work) and actual *behaviour change*.
This pass answers the register's three Key DISCOVER questions from the evidence already in `docs/market_research/`.

---

## Q1 — What real UK supplier↔customer conversation looks like

**Source:** `company_customer_comms.md` (Ofgem SLC 22A/22B, Consumer Standards Dec 2023, Energy UK, Citizens
Advice, Which? 2025) — a body of consumer-protection/consumer-body evidence, disjoint from the behavioural-
economics library used in Q2.

**Complaint volume — the spread that proves the pitch.** Which? 2025: **Octopus 261 complaints/100,000 customers
vs a large-supplier average of 1,525/100,000** — a ~6× spread. Same regulated product, same price cap; the
difference is *how the supplier converses*. This is the single most direct external corroboration of F1's premise
that tone/handling is a real differentiator, not a nicety.

**Channel mix & cost-per-contact** (the "channel" half of the abatement mechanism):

| Channel | Cost/contact (UK benchmark) | Note |
|---|---|---|
| Phone / agent | £5–£12 | Consumer Standards Dec 2023 mandates extended hours; avg wait 7min (2022) → 2min (mid-2024) |
| Webchat / email | £2–£5 | Multi-channel incl. webchat now mandatory |
| Self-serve (app/web) | £0.10–£0.50 | Kraken/digital-native 10–15× lower cost-per-contact than legacy |

**Channel mix by segment** (the register asked for this explicitly): SME/micro-business — **60–70% of contracts
via TPI/broker, not digital**; residential increasingly digital-first; **PSR sub-population** (Ofgem est. 40% of
households eligible, most unregistered) requires a distinct comms model (large-print/braille/audio bills, nominee/
proxy, password scheme, priority routing). So a message generator cannot be one-size: channel is segment-gated.

**Conversation triggers — the "situations" a company message generator must key to** (mandatory + good-practice
contact points a real outbound engine fires on):

| Situation | Trigger | Regulatory / practice basis |
|---|---|---|
| Renewal | 42–49 days pre-expiry (domestic, SLC 22A); 60–120 days (SME) | statutory notice |
| Tariff change (variable) | 30 days (SLC 22B) | statutory notice |
| Missed payment | after 2 consecutive monthly / 1 quarterly | Consumer Standards Dec 2023 mandatory outreach |
| Bill shock | usage spike / large bill (smart-meter pre-billing alert) | Energy UK good practice |
| Inbound complaint / billing query | treat as churn signal; resolve + retain in same contact | Energy UK good practice |
| Win-back | 30/60 days + ~6 months post-churn | market practice (~5–15% first-wave conversion) |
| Welcome | within 5 working days of supply start (SLC 23) | statutory |
| Annual statement | once/year (SLC 31B), carries cheaper-deals prompt | statutory |

**Honest gaps (`[recall, validate]`, not fabricated):**
- The repo has complaint *volume* benchmarks and contact *triggers*, but **no complaint-CATEGORY taxonomy**
  (billing / switching / customer-service / meter / PSR-failure split — Energy Ombudsman and Ofgem publish this
  by category). A conversation model wanting realistic *inbound* complaint arrivals needs that category split;
  it is not in `docs/market_research/` and was not fetchable this pass.
- **Tone-of-voice evidence is indirect** — the 6× complaint-ratio spread *implies* tone matters, but no measured
  UK-energy tone→outcome study is in the repo. Q2 supplies the quantified tone effect from a cross-domain source.

---

## Q2 — Modelling message→behaviour against the engagement axes already estimated

**Source:** `NUDGE_PHYSICS_BENCHMARKS.md` (behavioural-economics literature) — methodologically disjoint from Q1's
consumer-protection evidence. The message→behaviour edge already has a benchmark library:

| Mechanism (conversation lever) | Effect | Confidence | Relevance to F1 |
|---|---|---|---|
| **Debt-collection letter tone/framing** | **+3 to +10pp** additive payment-response uplift | M (cross-sector) | the most directly conversational: message *tone* → payment *outcome* |
| Loss-aversion offer framing | 10–35% acceptance uplift | H phenom / M magnitude | renewal/win-back message framing |
| Anchoring in tariff presentation | 8–20% acceptance uplift | H / M | how a rate is *said*, not just its value |
| Defaults / status-quo (auto-renewal) | 15–35% switch-prob reduction | H / M | silence-is-a-message (no-contact path) |
| Social norms / neighbour comparison (Opower) | 1.4–3.3% usage reduction | H (energy-specific) | proactive engagement message |
| Friction / "sludge" per step | 5–10%/step completion decay | M / L | channel-choice consequence |
| Present bias (payment timing) | β ∈ [0.6, 0.85] | H / L | timing of a payment-plan message |

**Wiring to the engagement axes.** `segmentation_joint_structure.md` confirms the two hidden conversation traits —
**FramingSusceptibility and ToneSusceptibility** — live in `nudge_physics.py`, **sampled per-customer from the
published range as an independent draw** (no cross-axis correlation to Need/demographics found in any repo source,
§2.3). So the response edge is:

> **response = f( message, {FramingSusceptibility, ToneSusceptibility}, channel-preference, engagement-archetype,
> situation-state ) → action + reply**, where the per-customer susceptibility scalars the benchmark uplift above.

This is exactly the register's "conversation-revealed trait" loop: **channel preference and trust are only
observable through which messages get replies/action** — you cannot know a customer's preferred channel or trust
level except by conversing and watching what lands.

**Honest caveats:**
- NUDGE_PHYSICS itself flags that **only Opower (usage) and the UK switching trend are energy-sector-specific**;
  the rest are cross-domain imports (tax debt, savings products, retail pricing, lab tasks) — magnitudes carry
  M/L confidence. A built model must therefore **sample susceptibility from a distribution** (population-anchoring
  convention), never a point estimate, and register the cross-domain import as a named R10 simplification.
- No published cross-tab links susceptibility to any demographic/Need axis (§2.3, confirmed genuine "not found",
  not an access failure on that pass). This means susceptibility must be an **independent latent**, not a
  demographically-predictable one — which is, correctly, the hardest case for the company to learn (Q3).

---

## Q3 — The epistemic wall: replies and outcomes, never intent

The modelled customer has an internal state (susceptibility scalars, trust, budget stress, *true intent*). The
company sees **only what the customer says or does**: reply / no-reply, click, switch, pay / miss, complaint,
channel chosen, response latency. **A supplier that "reads intent" is a leak** — getting this wall right is the
whole point of the track.

**Observable proxies a real supplier legitimately has** (`segmentation_joint_structure.md` §3b.3):
- payment history → reliability / `organisation` latent
- smart-meter usage shape → Need
- complaint / switching behaviour → engagement
- **NEW observable stream a conversation adds:** message-response events — open / reply / action, and their
  *latency by channel*. This is how channel-preference and trust become estimable at all.

**Traits with NO real-world observable proxy** (green stance, framing/tone susceptibility, CO₂ salience): these
must stay **hidden-truth-only**. The company may *estimate* a susceptibility as a **Bayesian belief updated on
observed replies**, but must never read the true scalar. That belief-vs-truth distance is precisely the
**coupled-triad GAP**: SIM holds the true trait, COMPANY estimates it from replies (allowed to be wrong), HARNESS
scores the gap.

---

## Proposed coupled-triad shape (NO atom opened — director/twin BUILD-open call)

Per COUPLED_TRIAD_DESIGN, F1 is naturally a 3-loop. Sketch only:

- **SIM (customer response model).** `(message, hidden traits, state) → action + reply`; susceptibility scalars
  the nudge-benchmark uplift; own RNG substream (C-S2 discipline); typed message/response events over the wall
  (C-S3 async request/response as separate events, typed-flow-seam preference).
- **COMPANY (message generator + estimator).** A generator keyed to `(segment-belief, situation-trigger)` from the
  triggers in Q1, plus a **response-history estimator** that updates a per-customer susceptibility *belief* from
  observed replies **only** — never the true trait.
- **HARNESS (the gap).** Measures (a) belief-vs-truth susceptibility gap per customer, and (b) whether the
  company's tone/channel choice actually improved the outcome vs a no-message / neutral-message control.
  **R15 mutation lever:** a company that "reads intent" (whose action correlates with the true hidden trait beyond
  what its observed replies justify) must be *caught* by the harness — an intent-leak is a named defect the control
  fires on. Without that mutation test the wall is theatre.

---

## Validation against independent sources (never SIM ground truth)

Three methodologically disjoint sources triangulate the same conclusion — **how you contact (channel + tone)
measurably moves satisfaction / complaint / payment outcomes**:

1. **Which? 2025** complaint-ratio spread (261 vs 1,525 /100k) — consumer-body, complaint-volume lens.
2. **Behavioural-economics literature** (NUDGE_PHYSICS: debt-letter tone +3 to +10pp, framing 10–35%) — academic,
   causal-effect lens.
3. **Ofgem/Citizens Advice CSAT Wave 20** (payment-channel × satisfaction: DD 82% / prepayment 80% / standard
   credit 76%, re-cited via `segmentation_joint_structure.md` §2.2) — regulator survey, channel × satisfaction
   cross-tab.

None is SIM output. The **direction is corroborated across all three**; the **magnitudes are mostly cross-domain
imports** (only Opower + UK switching are energy-native), so the conclusion for BUILD is: model the *presence and
sign* of the effect with confidence, sample the *magnitude* from a distribution, and label the cross-domain import
as an R10 simplification.

---

## Status & open items

- **Status:** DISCOVER pass done (2026-07-22). Register row moves skeletal → DISCOVER-complete.
- **Candidate graduation:** the coupled-triad above. **BUILD-open is a director/twin call — no atom opened, no map
  write** this pass (DISCOVER-only discipline).
- **Open `[recall, validate]` (pending a live fetch, not re-searchable this pass):**
  1. Complaint-**category** taxonomy (Energy Ombudsman / Ofgem complaint league tables by category) — needed for
     realistic *inbound* complaint arrivals in any SIM response model.
  2. A UK-energy-specific **tone→outcome** study, to lift the nudge magnitudes above cross-domain-import confidence.
- **Next autonomous tick:** if no live fetch is available, draw another track (F3 volunteer mechanics or F4
  international probe are both still skeletal) rather than re-running F1 — the two open items above are network-
  gated, recorded here so they are not re-searched fruitlessly.

*Forward-discovery pass, 2026-07-22. Every external figure re-cited from a prior fetched source in
`docs/market_research/`; no SIM ground truth read; no fabricated numbers; gaps labelled honestly (R9).*
