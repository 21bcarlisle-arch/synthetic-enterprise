# POESYS MATURITY MAP — v1.1
### The full-grown company, the world it lives in, the loop that makes depth honest, and the dials that set our speed
**Drafted by the advisor for the director, 2026-07-10. Supersedes v1.0 (same lanes & levels; adds the hardening loop, the Expert Hour, the capability data model, lane charters, and the simplifications register).**
**Ownership: director + advisor own the map (lanes, levels, dials, the Expert Hour bar). The agent proposes level-ups with evidence; it never moves a cell itself.**

---

## 0. What this is, in one paragraph

A single, canonical, machine-readable picture of (a) everything a fully-grown, at-scale UK energy supplier is and does, (b) everything the simulated world must be to exercise it, (c) an honest maturity mark for each capability, (d) the loop every capability must pass through to move up a level — so depth is earned, not claimed — and (e) a dial per lane so the director sets velocity like a graphic equaliser. Phases name the cells they move; progress is cells moving; the website renders it so anyone can see what's done, what's in flight, and what's next.

---

## 1. The canonical test: **the Expert Hour**

> *If a veteran of this function — someone with decades in a real supplier — spent an hour poking around the website: would they recognise what they saw, find no major gaps or flaws, and come away quietly impressed?*

This is the bar the whole map answers to, and it has **two components, both required**:

- **Substance** — the capability genuinely works the way the real function works (the mechanics, the failure modes, the numbers in plausible ranges).
- **Legibility** — the veteran can *find* it, *navigate* it, and *understand* it: surfaces, explanation, benchmark context ("here is our trading tab; here is what a real trading desk shows"). Half of being impressed is what we built; half is how we show, explain and navigate it. A brilliant capability with an illegible surface fails the Hour. So does a beautiful page over a hollow mechanism.

**Mapping to levels:** L3 = the veteran says *"this is real"* (recognition, no major flaws). L4 = the veteran says *"this is good"* (impressed; would ask to borrow ideas). The veteran's *one-year* findings — the things only deep tenure would catch — are not pretended away: they live in the **simplifications register** (section 5), visible and honest.

**How it's tested without a veteran on tap:** the HARDEN stage (section 2) simulates the Hour — the local skeptic prompted as a named-function veteran walks the actual deployed surfaces; plus benchmarking against the real-platform survey (what does Kraken/Gorilla/Gentrack show for this function that we don't?). Periodically, the director *is* the veteran — his C6 bill catch and trading-tab catch were Expert Hours avant la lettre, and both beat the entire automated stack. The map institutionalises what he was already doing.

---

## 2. The Hardening Loop — how a cell earns a level

**No capability moves up a level without passing the loop.** Levels are claims; the loop is the burden of proof. This is the PDLC made explicit, and it is the depth mechanism — the answer to "a quick bit of research now" masquerading as a function that took real firms decades.

| Stage | What happens | Cheap/parallel? |
|---|---|---|
| **DISCOVER** | Research how the real function actually works: best-practice literature, regulatory texts, the platform survey, practitioner accounts. Output: distilled findings + named references + anchors registered in ASSUMPTIONS.md. | Yes — background lane, Qwen-heavy, zero collision risk |
| **FRAME** | Write/update the lane charter (section 4): mission, sub-capabilities, target-level definitions *specific to this lane*, roadmap, known simplifications. | Yes — document work |
| **BUILD** | Implement against the frame. | Foreground build lane |
| **VERIFY** | 0b evidence on a deployed surface + tests + invariants + population stats. "It works." | Mixed |
| **HARDEN** | The Expert Hour simulation: veteran-skeptic walks the surfaces; benchmark vs real platforms; adversarial cases; simplifications register updated. "It survives inspection." | Yes — background lane |

**Parallelism falls out of the loop**: lanes at different stages pipeline naturally (B in DISCOVER while D is in BUILD while F sits in HARDEN), separated by *both* file scope and stage type. This is the safe version of "more in parallel" — concurrency from separation, not from racing on shared files. The agent's parallel-lanes proposal must design against this structure.

---

## 3. Levels (unchanged from v1.0, now with the loop attached)

| Level | Name | Meaning | To enter, a capability must have... |
|---|---|---|---|
| **L0** | Absent | Doesn't exist | — |
| **L1** | Skeletal | Exists, simplified past realism | been BUILT in any form |
| **L2** | Mechanically real | Genuine artefacts, happy path | passed DISCOVER-lite + VERIFY |
| **L3** | Faithful | Lives in time, fails like reality, anchored, epistemically clean | passed the **full loop** incl. HARDEN; Expert Hour: *"this is real"* |
| **L4** | Self-improving & governed | Measures itself, feeds the learn-loop, runs under the company's own controls | full loop + governance artefacts; Expert Hour: *"this is good"* |
| **L5** | At-scale & live-ready | 50k+ scale, behind a typed adapter with a named real twin; tournament-survivor | full loop at scale + adapter + tournament evidence |

---

## 4. Lane charters — fractal depth, budgeted by the dials

Every lane eventually needs its own strategy, best-practice distillation and roadmap at 2-3 levels more detail than this map. Doing all twelve at once is the exponential trap. **Rule: a lane earns its charter when its dial reaches 3+** (and keeps it evergreen thereafter). The charter is FRAME's output and lives beside the map (`docs/design/charters/<lane>.md`): mission; sub-capability tree; what L2/L3/L4 mean *in this lane's terms*; the named best-practice references; the lane roadmap; the simplifications register. Depth-on-demand: the equaliser governs not just build speed but how deeply we've bothered to think.

---

## 5. The simplifications register — honesty about the corners

Per lane, a living list of the conscious gaps between us and the real function: *"no gas shipper arrangements"*, *"single GSP group"*, *"no FX/credit desk"*, *"complaints ombudsman stage stubbed"*. Three rules: every HARDEN pass updates it; nothing may be simplified *silently* (an unlisted simplification found later is an R10-class defect); the register is **visible on the website** — the veteran being able to see we *know* what we've simplified is itself part of passing the Hour. This is what separates a distilled function from a naive one.

---

## 6. The data model — capability as the atom, views as toggles

The canonical store is **data, not prose** (`docs/design/maturity_map.yaml`), so the site can render it, the supervisor can draw work from it, and the matrix-vs-value-stream question dissolves into view toggles — as the director guessed, it's a data-mapping problem.

```yaml
# schema (one entry per capability)
- id: D3_catchup_rebilling
  name: "Estimated billing & catch-up rebilling cycle"
  lane: D_billing_metering            # function view (org-familiar)
  value_stream: price_to_bill        # cycle view: wholesale_to_price |
                                     # price_to_bill | meter_to_cash | close_to_learn
  epoch: 2
  level_current: 0
  level_target: 3
  loop_stage: discover               # discover|frame|build|verify|harden|idle
  dial_inherited: 4                  # from lane; may be overridden per-capability
  evidence: []                       # links: commits, surfaces, tests (fills as it moves)
  simplifications: []                # conscious corners cut, per section 5
  expert_hour: {status: not_attempted, last: null, findings: []}
  real_world_twin: "supplier billing ops + Elexon NHH profiling"
  depends_on: [W1_reveal_over_time, D2_register_billing]
```

**Views (all renderings of the same YAML, toggleable on the Project tab):**
1. **Function matrix** — lanes x levels (the org-familiar grid, section 8).
2. **Value-stream flow** — the four cycles the director named, each showing its capabilities' maturity in sequence.
3. **Campaign view** — capabilities grouped by epoch.
4. **Activity view** — what is in DISCOVER / BUILD / HARDEN *right now*, and what each lane does next: the "what it's done and what it's going to do" the director asked to see.

---

## 7. The lanes (positions restated from v1.0, unchanged this revision)

**Company:** A Strategy & Governance (L2) - B Commercial: pricing/trading/hedging (L2; competitors L0) - C Customer Operations (L2→L3; discovery layer L0) - D Billing & Metering (L2; three-clocks L0) - E Finance & Treasury (L1→L2) - F Risk & Compliance (L3 — most mature) - G Data & Learning (L2).
**World & Wall:** W1 Market & Weather engine (L1; generation-past-history L0) - W2 Customer & Society generator (L1→L2; population-draw L0; competitor field L0) - W3 Industry Systems (L1) - W4 The Wall (L1) - W5 Banking & Payment Rails (L0, new 2026-07-11, THE_VALUE_CYCLE_FRAMING.md M2).
**Harness:** H (L3).
*Full per-lane definitions and evidence as in v1.0 sections 2-4; they carry over verbatim and will live in the YAML.*

---

## 8. The equaliser (proposed settings, director to turn)

| Lane | Level now | Dial | Loop stage now | Rationale |
|---|---|---|---|---|
| W1 Market & Weather | L1 | **4 hot** | DISCOVER | Epoch-2 spine, half 1: reveal-over-time, rederive history, generate futures |
| D Billing & Metering | L2 | **4 hot** | FRAME | Epoch-2 spine, half 2: three clocks ride the reveal engine; M2 entry-gate audit joins now |
| B Commercial | L2 | 3 | DISCOVER | Margin bridge + point-in-time market data (kills the foresight class) |
| C Customer Ops | L2→3 | 3 | BUILD | Segment layers landing; discovery-through-interfaces queued behind W1 |
| E Finance & Treasury | L1→2 | 3 | FRAME | Ledger-first accounting now; accrual/restatement rides the spine |
| W2 Customer Generator | L1→2 | 3 | BUILD | Archetype layers now; population-draw with the spine |
| W4 The Wall | L1 | 3 | FRAME | Typed adapters; verifier extended to timing |
| A Strategy & Governance | L2 | 2 | idle | Learn-loop chair comes with the close cycle |
| G Data & Learning | L2 | 2 | idle | Event log shared with the spine |
| W3 Industry Systems | L1 | 2 | idle | Settlement timetable enters with the three clocks |
| W5 Banking & Payment Rails | L0 | 2 | idle | New M2 lane; build waits on the entry-gate audit verdict + M1 exit test |
| F Risk & Compliance | L3 | **1 maintain** | HARDEN | Ahead; let it prove itself over time |
| H Harness | L3 | **1 maintain** | HARDEN | Serve the lanes; no more harness-for-its-own-sake |

Supervisor self-refill draws work from lanes proportional to dials, respecting loop-stage pipelining (a hot lane in DISCOVER generates background research tasks, not build tasks).

---

## 9. Operating rules

1. Canonical home: `docs/design/maturity_map.yaml` + this document; **rendered on the Project tab with the four view toggles** — the map the director can see.
2. Cells move only at phase close, only with evidence, only having passed the loop for that transition. The agent proposes; the director ratifies level-ups at L3+; L1→L2 may be ratified by the advisor.
3. Dials: director turns at will; advisor may propose. Structure (lanes/levels/loop): epoch boundaries only.
4. Every staged phase names its capability id(s). No phase without a cell is staged. (Advisor enforces.)
5. Silent simplification = R10-class defect.
6. The Expert Hour is run per lane at every L3/L4 claim, and opportunistically by the director whenever he pleases — his catches feed the register and the invariants library.

---

*Sources: DESTINATION_VISION.md - FOUR_SECTION_VISION.md - the epoch arc - EPOCH2_EVIDENCE.md (six verdicts) - SaaS estate coverage map - competitor platform survey - PRIORITIES.md @ 2026-07-10 - director decisions 2026-07-06→10 (compliance principles, three clocks, pricing organ, customer pillar, population draw, rederive-history, Expert Hour bar).*
