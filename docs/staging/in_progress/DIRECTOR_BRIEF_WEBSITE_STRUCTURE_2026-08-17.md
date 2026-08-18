> **[IN PROGRESS — ruled and minted 2026-08-18; Step 0 of 8 BUILT; brief REVISED under it the same day]**
>
> **Open sub-item:** WORK THIS CREATES items 1–6 and 8, plus the four remaining §7 controls.
>
> **Done:**
> - §9.5 ("proposal before build") — `docs/design/SITE_STRUCTURE_PROGRAMME_PROPOSAL_2026-08-17.md`:
>   the sequence (Steps 0–7), a blast-radius assessment per step, six evidence-backed corrections to
>   this brief, and four open questions with recommendations attached.
> - **The director ruled all four, 2026-08-18** —
>   `docs/staging/done/DIRECTOR_RULING_SITE_STRUCTURE_PROGRAMME_ACCEPTED_2026-08-18.md`. All four
>   recommendations accepted; **§3's "`proof` is deleted, not moved" is overturned by his own word**
>   (deletion would have pointed five live 301s at a 404); one condition attached to publishing the
>   director record.
> - **The commitment set is minted:** `SITE4`–`SITE11` in `docs/design/maturity_map.yaml`, one atom
>   per Step 0–7, chained in the ruled order.
> - **Step 0 (`SITE4`) is built:** `site/ia_register.py` — the three-state IA register (ADVERTISED /
>   INTERNAL / RETIRED), every page's nav rendered from it (`tools/render_site_nav.py`), §7 control
>   #1 landed in its failable C3 form, and the six real orphans red-listed as shrink-only debt.
>   Controls + R15 mutations: `site/test_ia_register.py`.
>
> **The one thing waiting on the director:** the rendered `/director/` page, before Step 5 makes it
> crawlable. Registered under reserved class 3; **silence does not release this one**, by his word.
>
> **THE BRIEF WAS REVISED UNDERNEATH THIS PROGRAMME on 2026-08-18** (advisor, `e48d22639` /
> `357dbe0b3`), after `SITE4` was built and while its commit was in the gate. Its own words:
> *"If work has already begun from the earlier version, nothing built is invalidated — these
> are additions and one reframing, not reversals."* That holds for `SITE4`, which is
> structural and reader-invisible. **It does not automatically hold for `SITE5`–`SITE11`,
> which were minted against the pre-revision text** — the autopoiesis reframing of Home, the
> interface/curtain inventory in Capabilities, the method/lanes/levels and codebase-tracking
> additions to Harness, and the Harness jargon exception all land inside atoms already
> written. **Each of those atoms is re-read against this text before it is drawn**, and the
> `gain` field is corrected where the revision moved the target. Not done yet; nothing has
> been drawn since the revision.
>
> **Do not bulk-archive this file.** It is the canonical spec for a multi-draw programme that has
> delivered two draws of eight.

---

# [DIRECTOR-BRIEF] — The website: structure, content, and the end-to-end customer traversal (2026-08-17)

**Type:** [BRIEF — problem, requirements and non-negotiables. Design, mechanism, sequencing and implementation are the worker's. Nothing here prescribes markup, framework, file layout, or component structure.]

**REVISED 2026-08-18 after this document entered in_progress.** Changes: Home reframed around the project's own claim (autopoiesis — self-production and self-maintained boundary; the wall/boundary correspondence is structural, not analogical); Capabilities gains the interface/curtain inventory and the go-live seam; Harness gains the method, lanes and levels, the discovery-to-knowledge loop, observability including its own blind spots, and separate SIM/Company codebase tracking; the no-jargon rule gains its single Harness exception. If work has already begun from the earlier version, nothing built is invalidated — these are additions and one reframing, not reversals.

**Status of this document:** director-reviewed before staging. Supersedes no prior site instruction; the SITE2 door-renaming work and the unblocked `one_node_to_depth_with_charts` mint both sit inside this brief rather than beside it.

---

## 1. The problem, measured

Read at HEAD on 2026-08-17 by the advisor, from the committed site sources:

- **The nav reaches four areas; eight exist.** `customers`, `method`, `evidence`, `glossary`, `knowledge`, `director` are not in the top nav. Published areas with no route to them — the project's own no-caller class, on the public surface.
- **Six identical link labels on the homepage.** "Evidence behind this stage →" appears six times, word for word. No link tells a reader where it goes.
- **Four pages carry no heading structure at all.** `company/index.html` is 64KB with zero `<h1>`–`<h4>`. Same for `method`, `glossary`, `director`. Nothing is skimmable.
- **The evidence page is a machine dump.** Per node, the same three blocks repeat: "Artefacts cited by the map / Tests / Level record (R16)". It exposes the internal ontology instead of answering the reader's question.
- **`knowledge` is a 5.7KB stub.**
- **Brand tokens are applied inconsistently.** Some pages consume the shared palette; `customers` and `director` still carry their own raw-hex `:root` blocks.

**The single diagnosis:** the site is organised around the machine's ontology — stages, atoms, levels, doors, R16 — rather than around a reader's questions. Everything else follows from that.

---

## 2. Purpose and audience

The site exists so that an intelligent stranger can **understand the project, believe it, interrogate it, and follow its progress** — without learning our vocabulary.

Three audiences, in priority order:
1. **An informed outsider** (energy industry, investor, technically literate generalist) meeting the project for the first time.
2. **A returning reader** who wants to know what has changed since last time.
3. **A sceptic** who wants to check whether a specific published claim is true.

Non-audience: the machine, and us. Internal state belongs in the repo, not on the public surface. Where internal detail is genuinely useful it sits behind a drill-down, never as the default view.

---

## 3. Navigation — five tabs, in a ruled order

**Home · Knowledge · Capabilities · Explore · Harness**

`method`, `glossary` and **`proof`** are **deleted, not moved**. `director` is **folded into Harness** as a section.

**On the order, which is a deliberate editorial choice, not a default.** The site is written for the patient reader who wants to *believe* what has been done — not for capturing an impatient one. Knowledge sits second because domain competence is the credibility signal for the primary audience (the GB energy industry): a reader who sees the market described correctly will trust the simulation that follows. Explore sits fourth, after the reader knows enough for it to mean something. Optimising the order for a first-time skimmer would invert this; we are explicitly not doing that.

**On deleting Proof.** Once every claim is checkable where it is made, a separate proof area quarantines evidence away from the thing it supports — the same warehousing mistake as the glossary. Therefore: every published figure carries its provenance inline (§6.5), and the honest limitations list lives in **Harness** as "what we know is wrong". Nothing is lost; the verification banner, the claims-and-checks framing and the open limitations all survive, re-homed to where they are actually read.

**Rationale for the deletions, since they are the contentious part:** a glossary is a confession that the writing failed. If a page needs "SVT" explained, that page should say "standard variable tariff — the default price you are on if you never switched" the first time it uses the phrase. Deleting the glossary makes plain language structural rather than aspirational. Method and Harness are the same subject — how we work — told twice.

**Sequencing constraint (non-negotiable):** Knowledge must carry real content **before** glossary and method are deleted. Deleting three areas and pointing at a stub replaces one hole with three.

---

## 4. What each tab is for, and what it must contain

### Home — *what is this, and why should I care?*
The tab stays named Home (the convention a reader expects); the page opens with the claim, not a welcome.

**The claim must be the PROJECT's, not the simulated company's.** The current headline states the simulated supplier's mission ("an energy company built and run by AI, to find the cheapest tonne of carbon left"). That is the mission of the thing being grown, not the experiment being run, and a reader currently meets the exhibit without being told what it is an exhibit of. Required framing, in this order:

- **The question:** to what extent can software be *grown* rather than written — and more precisely, can a software system produce and maintain itself?
- **The name, and it is the thesis:** *autopoiesis* (Maturana and Varela) — a system that continuously produces and maintains its own components and thereby its own organisation. Contrast with allopoiesis: ordinary code generation makes a thing other than itself. The claim under test is whether this harness is doing something closer to the former.
- **The experiment:** an autonomous harness; a synthetic GB energy world built on nearly ten years of real settlement data; a simulated supplier inside it; a human whose role is to decide, not to build.
- **Why energy:** the fitness function is the cheapest tonne of carbon abated, and the domain is complex enough that faking it is immediately visible to anyone who knows it.
- **What is being measured:** features, value, code, data — or, honestly, at minimum the learnings.
- **The honest frame, stated plainly:** a proof of concept for learning, not a product and not a pitch.

**Two structural claims that belong on Home because they are the evidence, not decoration:**
- **Self-production:** the system builds the controls that judge its own work, finds them unable to fail, rebuilds them, and mints the law that prevents the next instance. That is the autopoietic claim in operational terms, and the Harness tab is where it is evidenced.
- **Self-maintained boundary:** in the theory, an autopoietic system defines and maintains its own boundary. Here that is the epistemic wall — enforced by the system on itself, with crossings measured and driven down by its own hand. This is a structural correspondence, not an analogy, and should be stated as such once, on Home, then demonstrated in Explore.

Home should also carry, as now: three live figures with date and provenance, a route into Knowledge as the next step for a patient reader, a short dated "latest" strip, and the model diagram at the foot as the whole-thing-on-one-page payoff.
- The claim in plain English, first screen, no diagram before the idea lands.
- Three live figures with their date and provenance: book size, margin, carbon.
- One hero route into **Explore** — a named household, not an abstraction.
- A short "latest" strip: three most recent changes, dated, in plain sentences.
- **The model-on-one-page diagram stays** — moved to the foot of the page as the payoff for readers who want the whole architecture at once. It is a good artefact in the wrong position, not a bad artefact.

### Knowledge — *the domain, explained properly*
- Depth pages on how the GB market actually works: wholesale price formation, what the cap does and does not do, settlement and its clocks, the non-commodity cost stack, metering and reads.
- **Every page carries a last-reviewed date**, and flips to a visible "review due" state past a threshold. Staleness must be visible on the page, not discovered by a reader.
- Built first, per §3.

### Capabilities — *how far along is this, really?*
- SIM and Company **side by side**, each in two columns: **now** and **next**.
- Honest about what does not exist yet. Absence stated plainly is credibility, not weakness.
- This page doubles as the roadmap; it should make a separate pitch document unnecessary.
- **The interface inventory — where the curtain lives.** A named section listing every seam between the world and the company: which are typed doorways today, which are still the world handing data over directly, and which real counterparty each would swap to at go-live (settlement and metering data, the smart-meter network, gas industry systems, payment collection). State the wall's own measured position — crossings remaining, and the trend. This is the strongest architectural claim the project has, because **the wall is the go-live seam**: switching from simulated endpoint to real endpoint is the launch, not a rewrite. The *inventory* belongs here; the *experience* of the boundary belongs in Explore (§5).

### Explore — *follow one customer, end to end*
The interactive centre of the site, and the strongest available demonstration of the epistemic wall. Specified in full in §5.

**Presentation bar, and it is a real bar:** Explore must feel like an operator's working screen, not a six-part essay. The earlier CRM-style view set the standard — a customer selector, both fuels side by side, a life-event timeline, real data visualisation, and **real artefacts**: an actual rendered bill, an actual meter read history, an actual direct debit schedule. The six stages in §5 are the *spine the reader navigates*, not six prose sections stacked vertically. If the finished page reads as an article rather than a system, it has missed.

### Harness — *how it runs itself, and what we are learning*
- The two-seat model, bounded work sessions, the rules and gates, in plain English.
- **The method itself**: how work is chosen and sequenced, what the lanes and the work-item map are, how levels of maturity are claimed and proven, and how a claim is refused when its evidence is missing. This is the operating system of the experiment and it should be legible to an outsider.
- **How discovery feeds knowledge**: the loop by which the machine's own investigations become domain understanding — a finding, a measurement, a repair, and where that lands as a Knowledge page. The link between the two tabs should be visible, because a self-producing system that also produces its own domain knowledge is a stronger claim than either alone.
- **Observability**: what the system can see about itself, what it alarms on, and — honestly — the classes of blindness it has discovered in its own instruments.
- **Codebase tracking, for SIM and Company separately**: modules, tests, coverage of what ships, wall crossings over time, orphaned work, and the split between what was built new and what was repaired. This is not housekeeping on a public page: it is the direct measurement of the growth being claimed. "Here is what was grown, and here is the shape of the growth" is the evidence a serious reader will want, and its absence would be conspicuous.
- **What the process is teaching us**: the named failure classes, the laws minted, the honest count of what broke and why. This is the methodology casebook and it is the part with the most outside value.
- **The director window, folded in as a section**: the record of what a human actually decided. "Here are the decisions a human made in a fortnight; everything else was autonomous" is a striking exhibit and it belongs here.
- A running progress log: what changed this week, what is being worked on, what is known broken.

### (Proof — deleted; its three jobs re-homed)
- **Claims-and-checks** → inline, wherever a figure is published: we say X, here is how it is checked, here is when it last passed.
- **The verification banner** (verified when, which run, which commit) → stays on every live-data surface, at the top, as now.
- **Known limitations, stated openly** → a named section in **Harness**: the rate tables extrapolated past 2024, the small book, the shared-elasticity simplification, and anything else standing. Weakness stated is credibility earned, and it belongs beside the account of how we work.
- Machine detail (atoms, levels, ledger records) stays available behind a "show the underlying record" control, never a default view.

---

## 5. Explore — the end-to-end traversal

**The requirement:** a reader picks one customer and follows them through the whole chain, seeing at every stage both what the world knew and what the company believed.

**Six stages, each with its own clock and its own question.** The change of clock between stages is not an inconvenience to be smoothed away — it is the industry education, and it should be explicit on screen.

**1. PRICED — why does this tariff cost what it costs?**
Clock: a moment, months before supply starts.
Show: the wholesale curve on the day it was priced; the hedge taken; the stack built up — energy, network, policy and levies, standing charge, margin — as one waterfall in p/kWh; the cap beside it as a ceiling.
Wall: what the company *assumed* about this customer's consumption when pricing.

**2. CHOSEN — why did this customer take it?**
Clock: a moment.
Show: what was available in the market that day; what this household is like; what actually drove the decision — price position, inertia, a life event, a channel; the alternatives, with the chosen one marked.
Wall: the company knows only that they signed. It does not know why. Make that asymmetry explicit rather than implied.

**3. USED — how much, and when?**
Clock: **two views, and the switch between them is the point.** Gas across the year, weather-shaped, heating-dominated. Electricity across one day, half-hourly, showing the evening peak.
Show: the home's fabric and heating system; the weather that drove demand; the resulting shape.
Wall: true consumption against what meter reads actually told the company — estimated, late, or absent.

**4. BILLED — what were they charged?**
Clock: the billing period.
Show: consumption × unit rate + standing charge, VAT, the bill as issued and as a customer would receive it; estimated versus actual reads flagged on the face of it.
Wall: bills built on belief, and corrected later when truth arrives.

**5. PAID — did the money arrive?**
Clock: cash over time.
Show: the direct debit as set; balance drifting into credit or debt; the seasonal swing; any arrears activity.
Wall: whether the company noticed a problem building, and when.

**6. JUDGED — was it the right choice, for them and for us?**
Clock: retrospective, whole-life, on **three settlement clocks: billed, settled, banked.**
Show two verdicts side by side. **Them:** what they paid against the best alternative available and against the cap. **Us:** margin after cost-to-serve, bad debt and settlement true-up, and lifetime value.
Wall: what the company believed this customer was worth, against what they turned out to be worth.

**Running throughout:** one persistent element showing world-truth against company-belief, so the gap is visible at every stage rather than explained once at the start. That element is the thesis made concrete.

**Honest constraint:** with a book of ~20 customers, Explore will show a small number of real lives. That is fine, and better than synthetic illustration. It should say so rather than imply a larger book.

---

## 6. Cross-cutting rules

1. **Every page states its purpose in its first sentence.**
2. **No internal vocabulary on public pages** — no atoms, levels, doors, stages, R16, lane names, rung names. If a concept genuinely needs a name, name it in the reader's language.
   **Single exception: Harness.** There, the method *is* the subject, so its vocabulary is legitimate — but every term is defined in plain English at first use on the page, and none of it is permitted to leak onto Home, Knowledge, Capabilities or Explore. This exception is what replaces the deleted glossary for method terms, exactly as Knowledge replaces it for domain terms.
3. **Every link says where it leads.** No label used more than twice across a page.
4. **Depth by drilling, not by dumping.** Summary first; detail on request.
5. **Every published figure carries its date and provenance** where it is shown, not only on Proof.
6. **Freshness is visible.** Anything that can go stale states when it was last reviewed or generated.
7. **Plain English is a design constraint, not a style preference.** It is what replaces the glossary.

---

## 7. Controls (mechanism the worker's; the properties are required)

These exist so the structure cannot silently rot back:
- A published area with **no route from the nav** fails.
- A published page with **no heading structure** fails.
- A link label used **more than twice on a page** fails.
- A knowledge page **past its review threshold** renders as review-due rather than silently stale.
- Internal-vocabulary terms appearing on a public page fail, against a named list — **scoped to exclude Harness**, per the §6.2 exception, and to require first-use definition within Harness itself.

Each must be provably failable and fail closed, consistent with the publish-surface gate landed today.

---

## 8. What this brief does not decide

Markup, framework, component structure, file layout, build pipeline, chart library, page-generation approach, and sequencing beyond the Knowledge-before-deletion constraint in §3. All the worker's.

**Proportionality:** this is a substantial multi-draw programme, not one landing. It should be minted as its own commitment set with the traversal (§5) as the largest piece, and it should not interrupt the publish-gate wiring or the PB3 growth path already in flight.

---

## WORK THIS CREATES (canonical, in-document)
1. The five-tab structure in the ruled order (Home, Knowledge, Capabilities, Explore, Harness), with method, glossary and proof deleted and director folded into Harness — sequenced after Knowledge carries real content.
2. Knowledge built out with real domain pages and visible review dates.
3. Explore: the six-stage end-to-end traversal, wall visible throughout, clocks explicit.
4. Capabilities: SIM and Company, now and next, side by side.
5. Harness: the methodology account, the learning, and the director record.
6. Proof dissolved: claims-and-checks inline at every published figure; limitations re-homed to Harness as a named section.
7. The five structural controls in §7.
8. Home reordered and reframed around the project's own claim — autopoiesis, the experiment, the honest proof-of-concept framing — with the diagram retained and re-positioned.
9. The interface/curtain inventory as a named section of Capabilities, with the wall's measured position and the go-live seam stated.
10. Harness extended to carry the method, the discovery-to-knowledge loop, observability including its own blind spots, and separate codebase tracking for SIM and Company as the measurement of growth.

— Director brief, 2026-08-17. Reviewed by the director before staging. See-and-correct applies to everything except the epistemic wall's treatment in §5, which is the exhibit's whole purpose.

---

## 9. How this lands (non-negotiable, because the site is live)

The public surface publishes roughly every half hour on a pipeline that was unwedged the same day this brief was written. The migration must therefore be non-destructive by construction. Five rules:

1. **Nothing is deleted until its replacement is live.** `glossary`, `method` and `proof` are removed only once Knowledge carries real content and inline claims-and-checks exist on the surfaces that publish figures. Deleting first replaces one hole with three.
2. **One tab at a time, each independently publishable.** No intermediate state in which the nav routes to a page that does not exist, or a page exists with no route. Every step leaves the site coherent for a visitor.
3. **Controls land with the thing they govern, never up front.** The five controls in §7 are per-surface: each arrives with the tab it polices. Landing them as a block before the migration would red the entire site mid-transition — a self-inflicted freeze of exactly the kind we spent three days clearing.
4. **This brief does not jump the queue.** The publish-gate wiring and the PB3 ADD path are in flight and outrank it. This draws as capacity allows, as its own commitment set. Interrupting in-flight work to start a large new programme is how the orphan class is fed.
5. **Proposal before build.** The first draw is not construction: it is the worker returning a proposed sequence, a blast-radius assessment per step, and any part of this brief it judges wrong — for the director to veto or accept. The brief states outcomes; the ordering and the mechanism belong to the party that can read the code.

**Rollback expectation:** each step is a normal reversible landing with receipts. If a step degrades the live surface, the correct response is to revert that step, not to push forward through a red site.

**Success test for the whole programme:** a reader who has never seen the project can arrive, read Knowledge, understand what was built from Capabilities, follow one real customer end to end in Explore, and come away able to say what is proven and what is not — without ever meeting an internal term or a dead link.
