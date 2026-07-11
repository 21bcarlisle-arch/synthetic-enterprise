# POESYS.NET — INDEPENDENT REDESIGN BRIEF
**RATIFIED by the director 2026-07-11 (in-conversation) after a three-way audit vs the live site. This is the site's constitution. Amendments from the audit are incorporated below (section 6b keep-list; section 4 additions marked NEW).**

---

## 1. The one-sentence job of the site

*Convince a sceptical expert — energy CEO/COO, CTO, or VC — in one unguided hour that this is a real autonomous energy company being grown in simulation toward go-live, by showing them the running company, the world testing it, and the proof discipline behind every claim.*

The current site fails this not through lack of content but through **organisation by internal architecture** (SIM / Supplier / Platform / Method mirrors our codebase) instead of **organisation by visitor question**. Experts don't arrive wondering what our modules are; they arrive with a persona-shaped question and leave when the site stops answering it.

## 2. Audiences and the question each must have answered

| Persona | Their question | Where they'll try to catch us |
|---|---|---|
| **Energy CEO/COO** | "Is this operationally real — would I recognise my company in it?" | One bill, one complaint journey, one bad-debt path, margin levels |
| **CTO / AI engineer** | "Is the architecture and method credible, or a demo with a good story?" | The wall, the harness, test discipline, how failures were handled |
| **VC / investor** | "Is there a thesis, a moat, and a number?" | The dual-ledger gap, break-even curve, comparables, what's defensible |
| **Domain expert / regulator-type** | "Do they know what they've simplified?" | VAT, settlement, back-billing, the corners we cut |
| **The director (Rich)** | "What is it doing, what's next, what needs me?" | Activity view, action-needed queue, dials |
| **The agent itself** | Evidence surfaces for rule 0b / pixel checks | Every page (machine-readable stamps) |

**Design consequence:** one front door, then persona-shaped paths through shared truthful surfaces — never separate marketing pages that could drift from the data.

## 3. Principles (the house style)

1. **Every claim links to its evidence.** A number links to its data file + generating commit; a capability claim links to its map cell + tests + surface. No orphan claims anywhere. (This is Claim=Pixel made into the visual language.)
2. **Every number carries its passport:** basis (billed/settled/banked), freshness stamp, PROVISIONAL badge where M4 applies. Ambiguity is a defect.
3. **Honesty is the aesthetic.** The simplifications register, open defects, incident retros, and adjudication ledger are *featured*, not buried — the visible-warts principle. Nothing builds expert trust faster than a company that publishes what's wrong with itself.
4. **Progressive disclosure:** headline → mechanism → artefact → code, on every topic. The CEO stops at layer 2; the CTO reads to layer 4; nobody drowns.
5. **The site is a rendering, never an author.** Every page is generated from repo data (maturity_map.yaml, dashboard/supplier/customer JSON, ledgers, registers). Hand-edited HTML is banned — it's how staleness happened.
6. **Live pulse over brochure.** The site's differentiator is that the company is *running*: lead with the heartbeat, not adjectives.

## 4. Information architecture — six doors + one private

### ⌂ FRONT DOOR (Home)
60-second job: what this is, that it's alive, and where to go.
- **The claim** (three sentences): an autonomous UK energy supplier — every commercial, financial and operational process executed by AI — evolved through simulated decades toward a stated go-live analysis. Not a model of a company; a running one.
- **The pulse strip** (live, generated): current sim date · book size · last bill issued (link to the actual bill) · latest prediction-vs-realised · treasury · EV [PROVISIONAL].
- **The thesis number**: the dual-ledger gap (true AI-native cost vs benchmark incumbent cost), one chart, one sentence.
- **Three doors**: "Inspect the company" (CEO/COO) · "Inspect the method" (CTO) · "Inspect the case" (VC). Plus a quiet fourth: "What we've simplified" — the honesty door.

### ① THE COMPANY — the supplier as a business (CEO/COO home turf)
A board pack, not a feature list. Sections mirror how a real exec reads a business:
- **Trading & risk**: hedge book, realised VaR, margin bridge (expected vs realised, decomposed), the pricing decisions log (ex-ante cost stacks + margin calls, versioned).
- **Finance on three clocks**: P&L billed/settled/banked side by side; the reconciliation bridge; break-even curve vs the governance floor; segment ROCE vs hurdle; concentration exceptions standing openly.
- **Customers & operations**: the book by segment; a *named household drill-down* (their bills incl. estimated/corrected ones, their complaint, their retention offer — the C6 lesson institutionalised); service levels vs GSOP; collections and debt path.
- **Compliance & controls**: the obligations register with risk tiers; exception queue (held bills!); adjudication ledger; internal-audit findings. *The immune system on display.*

### ② THE WORLD — the simulation and the wall (domain-expert turf)
- The two-sided page: **left, what the world contains** (market, weather, population archetypes, the difficulty rack/curriculum — director-authored scenarios listed by name); **right, what the company is allowed to see** — the wall drawn as an actual interface diagram, with the epistemic test stated: *"could a real supplier know this?"*
- The reveal-over-time principle explained once, well: two timestamps, as-of views, the hedge-bug story as the parable.
- Data provenance: every anchor (ONS/Ofgem/Elexon) listed with its register entry.

### ③ THE PROOF — track record & verification (everyone's second stop)
- **The predictions ledger**: shadow-live scorecard, pre-registered, misses kept. The centrepiece.
- **The verification stack**: tests (count + what they assert), invariants library, sanity daemon, evaluator verdicts, Expert-Hour walk findings — with the NEEDS_WORK history shown, not hidden.
- **Open defects & simplifications register**: what's wrong right now, what's consciously cut, each with status. 
- **Incident → rule timeline**: the doorbell saga, the injection scare, the stale graphs — each incident and the permanent rule it produced. (This page is secretly the method's best advert.)

### ④ THE METHOD — the casebook (CTO turf, product #1)
- The operating model: one human director, an advisor, an autonomous builder; the tiered governance; staging; the supervisor; hooks as law.
- The rules R1–R11 with the story behind each (linked from ③'s timeline).
- The harness architecture, honestly benchmarked against published best practice — where we converged independently, where we adopted, where we diverge deliberately.
- "Run this yourself" posture (even if aspirational): what the casebook product will be.

### ⑤ THE JOURNEY — map & trajectory (VC turf + Rich's public view)
- **The maturity map rendered**: lanes × levels matrix, value-stream toggle, epoch campaign view, **activity view** (in DISCOVER/BUILD/HARDEN now; next up). 
- The epoch arc with exit tests, current epoch highlighted; M4's "all numbers regenerate" stated plainly.
- The destination: go-live analysis, the tournament, geography/product expansion as parameters. The investor narrative lives here, evidence-linked.

### ⑥ SIMPLIFIED (the honesty door — small, permanent, linked everywhere)
The consolidated simplifications register, grouped by lane, each entry: what's cut, why, when it's due. The page an expert checks to decide whether to trust the rest. Cheap to build, disproportionate trust yield.

### ⑦ DIRECTOR (auth-gated)
Rich's console: action-needed queue, dials (equaliser UI), comment history + statuses, digest archive, curriculum rack. Not public; linked from nowhere.

## 5. Expert Hour paths (the killer feature)
For each persona, a **guided 10-stop tour** — a floating "Tour: Energy CEO" selector that walks them through the exact artefacts that answer their question (CEO: pulse → a real bill → margin bridge → a complaint journey → exception queue → break-even → simplifications → verdict). This operationalises the Expert Hour test as UX: we stop hoping experts find the good stuff and start walking them to it. Also our own HARDEN sweep uses the same paths — the daily walk and the visitor experience become one artefact.

## 6. What dies from the current site
Module inventories and capability lists (map replaces them) · duplicated epoch prose (Journey owns it) · any hand-written figure (rendering principle) · the SIM/Supplier/Platform split as top-level navigation (becomes World/Company/Method) · screenshots of things the live site can show directly.

## 6b. Keep-list (audit verdict: current site elements that BEAT the brief — absorb, never rebuild)
- The customer drill-down portal (C6-style: bill equations, statements, timeline, risk tabs) → becomes The Company's household view as-is.
- Sim tab depth (weather engine views, meter-read histograms, run data) → re-homed under The World unchanged.
- This week's Supplier additions (obligations register, exception queue, VaR, B2 taxonomy, benchmark ledger) → The Company's board-pack sections; ~60% of that door's content already exists — this is re-homing + passports, not rebuilding.
- The data-generation pipeline and freshness machinery (principle 5 is already the architecture).
- The terminal/observatory aesthetic and voice.

## 6c. Additions the audit exposed as missing from BOTH (build these)
- **THE THESIS CHART** — the dual-ledger gap (true AI-native cost vs lower-quartile incumbent benchmark) drawn as the property's headline visual: Front Door, one chart, per-year, evidence-linked. The single most important pixel on the site; currently exists only as data.
- **Glossary layer** — hover/tap definitions for domain jargon (MPAN, SLC14, EAC, TDCV, SVT...) site-wide; experts outside energy hit these cold.
- **Mobile pass** — the director reviews from a phone; every door and tour must pass a phone-width Expert Hour. Add to success criteria.
- **Periodic narrative** — a quarterly "state of the company" letter (generated + advisor/director edited), replacing the fossilised annual report; The Journey owns it.

## 7. Build approach (pragmatic, not big-bang)
The data layer already exists and is good (dashboard/supplier/customers JSON, maturity_map.yaml, ledgers, registers). This is a **presentation-layer restructure**: new IA + templates over the same generated data, migrated door by door (Front Door (incl. THE THESIS CHART) + Journey first — highest gap-to-value; Company second; Proof third, mostly assembling existing artefacts; Method/Simplified last). Pixel rule and freshness stamps throughout. Old URLs redirect. Comments box on every page carries the page's data-state automatically (already spec'd).

## 8. Success criteria
- Each persona tour completable with zero dead ends, every claim evidence-linked (evaluator-checked weekly).
- The director finds "what's happening & what needs me" in ≤2 clicks.
- The Expert Hour, run genuinely (Rich + skeptic-veteran per lane): verdict "this is real" on ①②③; "this is good" on ③④.
- No number without a passport; no claim without a link; staleness alarms, never discoveries.