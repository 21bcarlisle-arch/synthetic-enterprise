# BUILD PROPOSAL — F1 Simulating conversations — the message→behaviour coupled triad

**Status:** PROPOSAL, returning through the twin/director gate. **This artefact opens no BUILD atom and
moves no map level.** It is the propose-half deliverable of the R17 class fix (director ruling 2026-07-23,
work order §3.1): a BUILD-gated item's ungated proposal step is always-drawable work, and writing this
proposal drains the F1 propose-half rung (`supervisor.py::_proposal_written_ids` globs
`docs/design/proposals/F1_*.md`).

**Provenance chain.**
- DISCOVER: `docs/market_research/f1_simulating_conversations.md` (DISCOVER-complete 2026-07-22, both
  open items closed against primary sources — Energy Ombudsman 2024 category mix, Citizens Advice rating
  methodology, Ofgem complaint-handling research).
- FRAME: `docs/design/frame/F1_conversations_coupled_triad_FRAME.md` (graduated to FRAME by the director,
  console 2026-07-22: *"design the SIM-response / company-generator / harness-gap coupled triad,
  reconciled with the segmentation schema (channel/trust as conversation-revealed traits). Build proposal
  comes back through the gate."*).
- This BUILD PROPOSAL is that build proposal. It restates the FRAME's §10 as a decision-ready,
  atom-by-atom build plan and adds what a gate needs: file_scopes, level targets, R15-provable exit
  tests, sequencing under the coupled-triad binding rules, the C-S scale constraints wiring, and the
  explicit values-calls the director must (or may defer) settle.

---

## 1. What the gate is being asked to approve

Open **three candidate atoms** as a coupled triad (SIM depth → COMPANY copes-through-the-wall → HARNESS
measures the gap), target **L2**, disjoint file_scopes so they build in parallel per lane. Concretely,
the ask is:

1. **Approve the triad shape and its three exit tests** (§4) as the build contract.
2. **Settle (or explicitly defer) the two values-calls** in §7 — the curriculum default and the L3
   network-gated residual. Neither blocks L1/L2; both are needed before L3.
3. **Confirm the L2/L3 line** (§5): L2 is the proposed autonomous build target; **L3 stays
   director-reserved** (inbound complaint *arrivals* keyed to the Energy-Ombudsman category mix — a
   curriculum surface).

Nothing here is a one-way door: this is simulation code in version control (PROCEED_BY_DEFAULT). The
gate is asked for the **triad shape + values-calls**, not per-atom approval — once the shape is blessed,
the atoms build to their exit tests under the standing campaign-authorization model.

## 2. The one mechanism the triad is built around

> **response = f( message, {FramingSusceptibility, ToneSusceptibility}, channel-preference,
> engagement-archetype, situation-state ) → action + reply**

The per-customer susceptibility scalars **scale** the DISCOVER-benchmarked nudge uplift (debt-letter tone
+3 to +10pp; framing 10–35%; anchoring 8–20% — magnitudes are mostly cross-domain imports, so a build
**samples magnitude from a distribution, R10**, never a point estimate). The company **never sees the
scalars** — it sees only `action + reply`. That asymmetry is the whole atom: it is the missing loop
between the engagement-axis *traits* already estimated in the segmentation work and actual *behaviour
change*.

**External grounding (all independent of SIM ground truth, DISCOVER-cited):** Which? 2025 shows a **~6×
complaint-ratio spread** on the same regulated product (Octopus 261 vs large-supplier avg 1,525
complaints/100k) — tone/handling IS a real differentiator. Citizens Advice outcome weights
(**customer-service 55% / complaints 35% / commitments 10%**) set the harness outcome score's weighting —
it is CS-heavy, not equal-weighted.

## 3. The three atoms

### F1a — SIM customer response model *(behind the wall, allowed to hold truth)*
- **Lane / file_scope:** SIM — `sim/**` plus the company-facing seam side of `company/interfaces/sim_interface.py`
  (typed event types live at the seam; the wall IS the go-live seam, typed-flow-seam preference).
- **Inputs:** a typed inbound `Message{situation, channel, tone, framing, offer?, product}` event.
- **State per customer (never crosses the wall):** hidden `{FramingSusceptibility, ToneSusceptibility}`
  (independent latent draws, **reuse `nudge_physics.py` — do NOT re-draw**; no demographic cross-tab per
  DISCOVER §2.3), plus trust, budget-stress, and *true intent* (e.g. considering-switch).
- **Output:** a typed `Response{action ∈ {reply, no-reply, click, pay, miss, switch, complain},
  channel-chosen, latency}` event. Action probability = a situation base rate **modulated by
  `susceptibility × benchmarked-uplift`, saturating (no probability > 1)**.
- **Scale discipline (load-bearing, not decoration):** own **named RNG substream** (C-S2 — a conversation
  draw never shifts another subsystem's outputs); response is a **separate event in time** from the
  message (C-S3 async — never same-step resolution); idempotent reply processing (C-S2); message→response
  lag is a **declared parameter** (C-S5 time-scale invariance).

### F1b — COMPANY comms: generator + belief estimator *(in front of the wall, allowed to be wrong)*
- **Lane / file_scope:** COMPANY — `company/**` (generator + estimator + the company-side belief store).
- **Generator:** keyed to `(segment-BELIEF, situation-trigger)`. Situations = the DISCOVER Q1 trigger
  table (renewal 42–49d per SLC 22A, tariff-change 30d, missed-payment, bill-shock, inbound-complaint,
  win-back, welcome, annual-statement). Channel is **segment-gated** (SME 60–70% TPI/broker; PSR needs
  accessible formats; residential digital-first) — the generator may **not** assume one channel.
- **Estimator:** a **per-customer Bayesian belief** over each susceptibility, updated **only on observed
  replies/actions/latency**, never the true scalar. Channel-preference and trust are **conversation-
  revealed** — estimable only because the company watches which messages land. This is the exact
  "conversation-revealed trait" reconciliation the ruling asked for, reconciled with the segmentation
  joint structure (`segmentation_joint_structure.md`).
- **Explicitly permitted to diverge from truth** — that divergence is the score.

### F1c — HARNESS conversation gap *(measures, never helps either side)*
- **Lane / file_scope:** HARNESS — `tests/**` / harness modules + the digest/gap-ledger surface it feeds.
- **Reports three things:**
  1. **Belief-vs-truth susceptibility gap** per customer (company posterior mean vs SIM true scalar) —
     the coupled-triad GAP, reported per digest and on the Proof door.
  2. **Did the conversation improve the outcome** vs a no-message / neutral-message control, scored on
     the **Citizens-Advice weighting (55/35/10)**, not equal-weighted.
  3. **R15 intent-leak control (mandatory):** a company whose action correlates with the true hidden
     trait **beyond what its observed replies justify** is an intent-leak — a named defect the harness
     must *catch*.

## 4. Exit tests — the gate (each R15-provable)

| atom | exit test (must PASS to reach L2) | R15 mutation that must FAIL it |
|---|---|---|
| **F1a** | typed message→response over the wall; susceptibility scales benchmarked uplift within published bands; response is a distinct-in-time event | inject a shared-RNG variant → the C-S2 independence test fails (a new conversation draw shifts another subsystem's output) |
| **F1b** | generator fires the correct situation-keyed, **segment-gated** message; Bayesian belief updates on replies ONLY; **epistemic-verifier PASS on the diff** | inject a belief-update that reads the true scalar → epistemic-verifier FAILS (the wall catches it) |
| **F1c** | reports belief-vs-truth gap + CA-weighted outcome uplift; the gap lands on the digest/Proof-door surface | inject a **peeking company variant** (F1b that reads the true scalar) → the **intent-leak control FIRES**. Without this passing test the wall is theatre (R15 doctrine) |

**Definition of done (triad):** the gap is reported per digest; the intent-leak mutation test passes; no
epistemic-wall violation on the company diff; the outcome score is customer-service-weighted (55/35/10).

**Coupled-triad binding (A6):** no SIM/world part of F1a reaches L3 until the company (F1b) has been
tested against it and the gap measured; no company capability is complete until it has faced a
conversation that can defeat it. The gate approves the *shape*; the binding governs *promotion*.

## 5. Level decomposition & the L2/L3 line

- **L1** — types + **one situation (missed-payment)** end-to-end: SIM responds, COMPANY generates +
  updates a belief, HARNESS logs the gap. Single channel. Susceptibility sampled from the published
  distribution. *(Proves the loop closes.)*
- **L2 (proposed autonomous target)** — the **full Q1 situation/trigger set**; **segment-gated channel**;
  the **CA-weighted outcome score**; the **intent-leak control with its passing mutation test**.
- **L3 (director-reserved)** — inbound complaint *arrivals* keyed to the **Energy-Ombudsman category mix**
  (billing 58% → sub-taxonomy: disputed usage 22% / disputed balances 8% / back-billing), latency-by-
  channel belief, win-back curves. This is a **curriculum surface** (which conversations the company must
  face) → director's by right (R13). It also needs the modern per-lever tone magnitude (§7 residual), so
  **L3 is explicitly gated**.

## 6. Dependencies, sequencing & reuse

- **Reuses (do not rebuild):** `nudge_physics.py` (the two latents already exist), the segmentation joint
  structure (segment belief + observable proxies), the typed-flow seam, the append-only event-log (C-S4
  persistence behind an interface). **New only:** the message/response event types, the generator, the
  belief estimator, the three harness scores. No new billing engine, no new RNG framework — SIMPLICITY
  GUARD.
- **Two-way-door filter:** does not depend on any unresolved upstream question → passes.
- **Sequencing (parallel-safe, disjoint scopes):** F1a and F1b can start concurrently against the agreed
  event-type contract (define the `Message`/`Response` types at the seam FIRST — a small interface-steward
  step — then the two sides build to it). F1c starts once F1a emits a truth scalar and F1b emits a belief;
  its intent-leak mutation test needs a peeking F1b variant, so F1c lands last but its **spec is written
  test-first**. Suggested order: seam types → {F1a ∥ F1b} → F1c.

## 7. Values-calls for the director (do NOT block L1/L2; needed before L3)

1. **Curriculum (R13):** which conversation scenarios the company must face first. **Proposed default —
   the eight real-world triggers at population base rates** (a "steady-state" curriculum), no adversarial
   tone-war until the director authors one. A tone-war / complaint-surge scenario is a named, versioned,
   director-authored artefact — never agent-tuned toward a company outcome.
2. **The one network-gated L3 residual:** a modern (post-2020) UK-energy *per-lever* tone effect size
   would lift L3's magnitudes above cross-domain-import confidence. Until it exists, **L3 samples from the
   distribution and labels it R10**. Flagging, not blocking (residual `[recall, validate]`).

## 8. Portability & scale lenses (applied, not deferred)

- **Portability:** a `Message` carries a **`product` dimension wherever fuel is one** (a second product =
  new situation types, not a new engine). No counterparty hardcoding — the generator keys on
  situation+segment-belief, not "Ofgem". GB-specific trigger dates (SLC 22A 42–49d) are **config, not
  baked**. Any break surfacing at build is logged to `PORTABILITY_DEBT.md`, never fixed speculatively.
- **Scale (C-S1..C-S5):** C-S3 async request/response and C-S2 named-RNG-substream are load-bearing here
  (messages/replies arrive singly, late, out of order — C-S1; processing a reply twice is harmless —
  C-S2 idempotency). C-S4 persistence via the event-log abstraction. C-S5 declared message→response lag.
  No horizontal-scale infrastructure — constraint, not infrastructure.

## 9. Anti-goal-seek discipline (R12)

The message→behaviour magnitudes are a **diagnostic, never a target**. The belief-vs-truth gap is the
score to *measure*, never to *minimise by tuning*. A company that "reads intent" (its action tracks the
true trait beyond what replies justify) is the named defect F1c must catch — success is the harness
catching the leak, not the gap being small.

## 10. What this proposal explicitly does NOT do

Open any atom, write any BUILD code, or touch the maturity map. It is a proposal for the twin/director
gate, per the 2026-07-22 graduation ruling and the 2026-07-23 R17 class-fix work order §3.1. On approval,
the three atoms open at L1 and build to their §4 exit tests under standing campaign authorization; the
values-calls in §7 gate only L3.

— Forward-discovery propose-half draw, R17 class-fix work order §3.1, 2026-07-23.
