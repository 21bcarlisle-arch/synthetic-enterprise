# FRAME — F1 Simulating conversations — the message→behaviour coupled triad

**Provenance.** Forward-discovery track F1 (mission-required × highest), **GRADUATED to FRAME by the
director** (console 2026-07-22): *"design the SIM-response / company-generator / harness-gap coupled
triad, reconciled with the segmentation schema (channel/trust as conversation-revealed traits). Build
proposal comes back through the gate."* This is the FRAME artefact. It **opens no BUILD atom and moves
no map level** — the build proposal in §10 returns through the twin/director gate.

**DISCOVER basis.** `docs/market_research/f1_simulating_conversations.md` (both open items closed against
primary sources: Energy Ombudsman 2024 category mix, Citizens Advice rating methodology, Ofgem
complaint-handling research). Segmentation reconciliation: `segmentation_joint_structure.md`,
`nudge_physics.py` (FramingSusceptibility / ToneSusceptibility latents).

---

## 1. What this atom is & real-world grounding

The pitch's core claim is that **tone, timing and channel ARE the abatement mechanism**. Today the sim
has no conversations: customers don't respond to messages and the company generates none — so the
engagement-axis *traits* estimated in the segmentation work connect to no *behaviour*. F1 builds the
missing loop: a company that generates situation-keyed messages, customers who respond through hidden
susceptibility, and a harness that scores whether the company's belief about the customer tracks truth.

**External grounding (all independent of SIM ground truth, DISCOVER-cited):**
- **The spread that proves the premise:** Which? 2025 — Octopus 261 vs large-supplier avg 1,525
  complaints/100k, same regulated product → **~6× spread from how a supplier converses.**
- **The message→behaviour edge is quantified:** debt-letter tone **+3 to +10pp** payment uplift; offer
  framing 10–35%; anchoring 8–20% (NUDGE_PHYSICS, cross-domain → sample magnitude from a distribution,
  R10). Energy-native corroboration (Ofgem): tone/layout/personalisation → disengagement; **~1 in 2**
  complainants switched as a result of the *experience*.
- **The outcome axes reality scores (Citizens Advice):** customer-service 55% / complaints 35% /
  commitments 10% — the harness "did the message help" score is weighted to match, not equal-weighted.

---

## 2. The central mechanism — response is a function of message × hidden trait × state

The one equation the triad is built around (DISCOVER §Q2):

> **response = f( message, {FramingSusceptibility, ToneSusceptibility}, channel-preference,
> engagement-archetype, situation-state ) → action + reply**

where the per-customer susceptibility scalars *scale* the benchmarked nudge uplift. The company never
sees the scalars; it sees only `action + reply`. That asymmetry is the whole atom.

---

## 3. The three components

### 3a. SIM — the customer response model (behind the wall, allowed to hold truth)
- **Inputs:** a typed inbound `Message{situation, channel, tone, framing, offer?}` event.
- **State per customer:** hidden `{FramingSusceptibility, ToneSusceptibility}` (independent latent draws,
  no demographic cross-tab — DISCOVER §2.3), plus trust, budget-stress, and *true intent* (e.g.
  considering-switch). None of these crosses the wall.
- **Output:** a typed `Response{action ∈ {reply, no-reply, click, pay, miss, switch, complain},
  channel-chosen, latency}` event. Action probabilities = a base rate (from the situation) modulated by
  `susceptibility × benchmarked-uplift`, saturating (no probability > 1).
- **Discipline:** own **named RNG substream** (C-S2 — a conversation draw never shifts another
  subsystem's outputs); response is a **separate event in time** from the message (C-S3 async — never
  same-step resolution); typed-flow seam (the wall IS the go-live seam).

### 3b. COMPANY — message generator + belief estimator (in front of the wall, allowed to be wrong)
- **Generator:** keyed to `(segment-BELIEF, situation-trigger)`. Situations are the Q1 trigger table
  (renewal 42–49d, tariff-change 30d, missed-payment, bill-shock, inbound-complaint, win-back, welcome,
  annual-statement). Channel is **segment-gated** (SME 60–70% TPI/broker; PSR needs accessible formats;
  residential digital-first) — the generator may not assume one channel.
- **Estimator:** a **per-customer Bayesian belief** over each susceptibility, updated **only on observed
  replies/actions/latency** — never the true scalar. Channel-preference and trust are *conversation-
  revealed*: estimable at all only because the company watches which messages land. This is the exact
  "conversation-revealed trait" reconciliation the ruling asked for.
- **The company's belief is explicitly permitted to diverge from truth** — that divergence is the score.

### 3c. HARNESS — the gap (the score)
Two measured gaps + one adversarial control:
1. **Belief-vs-truth susceptibility gap** per customer (the company's posterior mean vs the SIM's true
   scalar) — the coupled-triad GAP.
2. **Did the conversation improve the outcome** vs a no-message / neutral-message control, scored on the
   Citizens-Advice weighting (**customer-service 55% > complaints 35%**), not equal-weighted.
3. **R15 intent-leak control (mandatory):** a company whose action correlates with the true hidden trait
   **beyond what its observed replies justify** is an intent-leak — a named defect the harness must
   *catch*. The mutation test: inject a company variant that peeks at the true scalar; the control must
   fire. Without that test the wall is theatre (R15 doctrine).

---

## 4. COUPLED TRIAD — the gap is the score (A6 binding rules)

| loop | owns | allowed to |
|---|---|---|
| **SIM** | true susceptibility, intent, response physics | be realistic; never expose internals |
| **COMPANY** | message generation, susceptibility *belief* | **be wrong** — learn only from replies |
| **HARNESS** | belief-vs-truth gap + outcome-uplift + intent-leak control | measure, never help either side |

Binding: no SIM/world part reaches L3 until the company has been tested against it and the gap measured;
no company capability is complete until it has faced a conversation that can defeat it. The gap is
reported per digest.

---

## 5. Level decomposition (target L2 first; L3 director-reserved)

- **L1** — types + one situation (missed-payment) end-to-end: SIM responds, COMPANY generates + updates a
  belief, HARNESS logs the gap. Single channel. Susceptibility sampled from the published distribution.
- **L2** — the full Q1 situation/trigger set; segment-gated channel; the Citizens-Advice-weighted
  outcome score; the **intent-leak control with its passing mutation test**.
- **L3** (director-reserved) — inbound complaint *arrivals* keyed to the Energy-Ombudsman category mix
  (billing 58% → sub-taxonomy), latency-by-channel belief, win-back curves. Needs the modern per-lever
  tone magnitude (one residual `[recall, validate]`), so L3 is explicitly gated.

---

## 6. Dependencies & sequencing
- **Reuses** `nudge_physics.py` (the two latents already exist — do not re-draw them), the segmentation
  joint structure (segment belief, observable proxies §3b.3), the typed-flow seam, the event-log.
- **New** only: the message/response event types, the generator, the belief estimator, the three harness
  scores. No new billing engine, no new RNG framework.
- **Does not depend on** any unresolved upstream question → passes the two-way-door filter.

## 7. Scale-readiness lenses (C-S1..C-S5)
Async request/response (C-S3) and named RNG substream (C-S2) are load-bearing here, not decoration:
messages and replies arrive singly, late, out of order (C-S1), and processing a reply twice must be
harmless (C-S2 idempotency). Persistence via the event-log abstraction (C-S4). Time-scale invariance
(C-S5): the message→response lag is a declared parameter, not a hardcoded step.

## 8. Portability lens
Product-first: a `Message` carries a `product` dimension wherever fuel is one (a second product =
new situation types, not a new engine). No counterparty hardcoding — the generator keys on
situation+segment-belief, not "Ofgem". Any GB-specific trigger dates (SLC 22A 42–49d) are config, not
baked. Debt logged, not fixed speculatively (PORTABILITY_DEBT.md if a break surfaces at build).

## 9. Curriculum note (R13 — baseline/curriculum split)
The **baseline** (susceptibility distributions, benchmarked uplift ranges) may change only for
fidelity-to-reality reasons, decided blind to company P&L. **Which conversations the company must face**
(a "tone war" scenario, a complaint surge) is the **director's curriculum** — named, versioned, never
tuned toward a company outcome, and never adjusted because the belief-gap looks wrong. The message→
behaviour magnitudes are a **diagnostic, never a target** (R12).

---

## 10. The build proposal (returns through the gate — no atom opened here)

Proposed as a **coupled triad of three atoms**, disjoint file_scopes (buildable in parallel per lane):

| candidate atom | lane / scope | exit test (the gate) |
|---|---|---|
| `F1a_sim_customer_response` | SIM (`sim/**` or `company/interfaces` seam side) | typed message→response over the wall; own RNG substream proven independent (a new draw doesn't move another subsystem — C-S2 mutation); susceptibility scales the benchmarked uplift within published bands |
| `F1b_company_comms` | COMPANY (`company/**`) | generator fires the correct situation-keyed, segment-gated message; Bayesian belief updates on replies ONLY; **belief never reads the true scalar** (epistemic-verifier PASS on the diff) |
| `F1c_harness_conversation_gap` | HARNESS (`tests/`/harness) | reports belief-vs-truth gap + CA-weighted outcome uplift; **intent-leak control fires on its mutation** (R15 — a peeking company variant is caught) |

**Definition of done (triad):** the gap is reported per digest; the intent-leak mutation test passes; no
epistemic-wall violation on the company diff; the outcome score is customer-service-weighted (55/35/10).

**Open values-calls for the director (do not block FRAME; needed before L3):**
1. **Curriculum:** which conversation scenarios the company must face first (default: the eight
   real-world triggers at population base rates — a "steady-state" curriculum, no adversarial tone-war
   until you author one).
2. **The one network-gated residual:** a modern (post-2020) UK-energy *per-lever* tone effect size would
   lift L3's magnitudes above cross-domain-import confidence; until then L3 samples from the distribution
   and labels it R10. Flagging, not blocking.

**What this FRAME explicitly does NOT do:** open any atom, write any BUILD code, or touch the maturity
map. The triad above is a proposal for the twin/director gate, per the ruling.
