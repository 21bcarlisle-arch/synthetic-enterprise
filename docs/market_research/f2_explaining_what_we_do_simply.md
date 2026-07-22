# F2 — Explaining What We Do, Simply (DISCOVER)

**Track:** F2, Forward-Discovery Register (committed / legal duty × high).
**Status:** DISCOVER-only. No build, no new map atoms. Names a candidate control/atom as a *proposal* only.
**Date:** 2026-07-22. **Author:** autonomous worker (forward-discovery tick).

**Provenance & honesty (R9).** Written without live network access (autonomous run). The regulatory
and plain-language **standards** cited below are author domain knowledge, recalled — labelled
`[recall, validate]` where no independent repo source corroborates them, and must be checked against
the named primary source before any figure or clause is used in a build. Two claims are already
corroborated by **independent already-fetched repo sources** (not SIM ground truth) and marked
`[VALIDATED]`. The **"where the current site fails"** assessment (§4) is not recall — it is a direct
reading of the **live site copy in the repo** (`site/index.html`), quoted verbatim, so it stands on
its own evidence.

---

## 1. The gap, stated precisely

F2's purpose line is exact and worth restating: **comprehension is a legal duty, not a nicety** —
*consent that was not understood is not consent.* The track therefore is not "write nicer marketing";
it is: **does a lay reader come away able to say back what Poesys does with their data and their
money** — and if not, that is a defect against a real obligation, the same class of defect the
epistemic wall guards on the sim side.

Three facts frame the gap precisely:

1. **There is no real customer yet.** Poesys holds no household data and takes no household money
   (the volunteer programme, F3, "will not open until a security-posture review has completed").
   So F2 is *forward* discovery: the consent/explanation machinery a real pilot would need, plus a
   **testable bar** to hold it to, designed before any household is exposed. This is the honest
   scope — it ties directly to F3 (the consent machinery) and to the public site (the current
   explanation surface).

2. **The current public explanation is written for the wrong reader.** The live front door
   (`site/index.html`) explains the project to **domain experts and investors** — its "Where to go"
   doors are literally keyed *"Energy CEO / COO"*. That audience choice is correct for the pitch's
   actual job (raise/partner — see `docs/vision/pitch.md` §10, "not raising capital at this stage
   … domain stress testing / translation partners / capital"). But it means **no surface today
   answers the lay-household question** F2 is about. The gap is not that the site is bad; it is that
   the *customer-comprehension surface does not exist yet*, and the nearest thing (the front door)
   fails a lay-reader bar by construction.

3. **"Data" and "money" are two distinct legal halves**, each with its own real standard (§2). A
   single "About us" paragraph cannot discharge both; the bar has to test both explicitly.

**The defect is not a wall violation and not a live-consent breach (no data is held).** It is a
**missing, testable comprehension surface** — and, until F3 opens, a **standard** the pitch/site can
already be measured against so the gap is visible rather than discovered at first-customer.

---

## 2. The real standards this bar must anchor to (two halves)

### 2a. The DATA half — "what we do with your data"

- **UK GDPR Article 12(1)** — a controller must provide information on processing *"in a concise,
  transparent, intelligible and easily accessible form, using clear and plain language."*
  Article 13/14 fix *what* must be said (identity, purposes, lawful basis, retention, rights,
  recipients). `[recall, validate against ICO "Right to be informed" guidance]`
- **Lawful basis + revocation + data minimisation** are already named as F3's design content
  ("GDPR lawful basis, revocation, data minimisation … Design the consent machinery; hold no data").
  F2 supplies the *comprehension* test over F3's *machinery*.
- **In-repo corroboration `[VALIDATED, independent source]`:** the data-consent terrain for exactly
  this business is already researched in `docs/market_research/smart_meter_hh_data_consent_2026.md`
  — it distinguishes **default-on smart-mode data flow** from **opt-in settlement-purpose HH
  consent** and flags that "settlement purposes" ≠ "actual consent given" (its §"genuine research
  gap"). That distinction *is* the comprehension trap F2 must test for: a household that cannot say
  back *which* data is shared, for *what* purpose, has not consented, regardless of a ticked box.

### 2b. The MONEY half — "what we do with your money"

- **Ofgem SLC 0 / Standards of Conduct** — information to domestic customers must be *"complete,
  accurate and not misleading"* and given in *"plain and intelligible language."* Billing/statement
  clarity sits under the billing SLCs. `[recall, validate against Ofgem SLC 0 + Consumer Standards
  (Dec 2023)]`
- **In-repo corroboration `[VALIDATED, independent source]`:** `company_customer_comms.md`
  independently records the SLC-driven notice/annual-statement regime (SLC 22A/22B/31B: end-date,
  roll-over tariff, exit-fee status, "cheaper deals prompt") — i.e. the money facts a real supplier
  is *already obliged* to make intelligible. A Poesys money-explainer inherits this floor.
- **Licence-readiness `[VALIDATED, independent source]`:** `ofgem_licence_readiness.md` records the
  ongoing licence conditions and **customer-credit-balance ring-fencing** — the single most
  reassuring "what happens to your money" fact a household would want said plainly ("your credit
  balance is protected, here is how"). The explainer's money half should surface exactly this.

### 2c. The comprehension-TESTING standard (the part that makes it a *bar*, not a wish)

- **FCA Consumer Duty, consumer-understanding outcome (PRIN 2A)** — the register names it directly.
  Energy retail is Ofgem-regulated, **not** FCA, so this is a **precedent to borrow, not a binding
  rule here** (state that honestly). Its transferable teeth: communications must be *likely to be
  understood* by the target audience, and firms are expected to **test, monitor and adapt** them
  (comprehension testing), not merely publish and assume. `[recall, validate against FCA PRIN 2A.5
  / FS22/8]`
- **Plain-language readability floor** — GOV.UK / GDS content design targets a **reading age of ~9**
  for public-facing content; the Plain English Campaign "Crystal Mark"; mechanical proxies
  Flesch–Kincaid grade / reading-ease. `[recall, validate against GDS "content design: planning,
  writing and managing content" + GOV.UK style guide]`
- **CMA precedent** — the CMA Energy Market Investigation (2016) remedies turned on customers being
  *able to understand and compare*; behavioural-remedy practice treats comprehensibility as an
  outcome to be evidenced. `[recall, validate against CMA EMI Final Report 2016]`

---

## 3. The testable bar (the register's explicit ask)

The register asks for *"a **testable bar** — can a lay reader say back what Poesys does with their
data and money."* Proposed operationalisation — a **teach-back (say-back) test**, the same
instrument clinicians and Consumer-Duty testers use, made mechanical:

> **The F2 comprehension bar.** After reading the plain explainer *once*, a lay reader (no energy or
> tech background) can correctly say back, unprompted, all four:
> 1. **Data —** *what data of mine Poesys takes, and what it uses it for* (and that it currently
>    holds none / is a simulation).
> 2. **Money —** *what happens to money I pay* (incl. that credit balances are protected) *and how
>    my bill is worked out at a level I can check.*
> 3. **Commitment —** *what I am agreeing to, and how I stop / leave / withdraw consent.*
> 4. **Who's accountable —** *that a human is accountable, not "an AI decides"* — the pitch already
>    says this up front ("a fully autonomous licensed supplier will not be permitted — a licence
>    needs accountable humans"); the bar checks the *lay reader* actually took it away.

**Two-tier, so it can FAIL (R15).** A comprehension control that always passes is theatre:
- **Tier 1 — mechanical floor (automatable now):** readability of the explainer text —
  Flesch–Kincaid grade ≤ ~6 (≈ reading age 9), no un-glossed jargon from a **banned-terms list**
  drawn from the live copy (§4). This is a real gate that *fails on its own named defect* (feed it
  today's front-door prose → it must go red).
- **Tier 2 — human/LLM-judge say-back (outcome-tested, per R15's LLM-judge clause):** N lay readers
  (or a lay-persona judge panel, distinct personas, majority vote) attempt the four say-backs;
  the surface passes only if ≥ some threshold recover all four. A judge whose "passes" a later real
  reader fails is a bad judge — measure it.

This bar is deliberately **audience-relative** (FCA Consumer Duty's own framing): the *pitch* passing
for a CEO says nothing about the *explainer* passing for a household. They are different surfaces with
different bars — which is the core §1 finding.

---

## 4. Where the current site/pitch fails the bar — direct evidence (not recall)

Assessed against the **live front-door copy in the repo** (`site/index.html`, lines 100 & 103–113),
quoted verbatim. This is the closest thing to a public "what we do" statement today.

**Quoted, live:**
> "An energy company built and run by AI — to find *the cheapest tonne of carbon left*."
> "An **enterprise simulator** for a UK energy supplier … it **settles half-hourly** against real
> **Elexon and NESO** market data since 2016 … discovers its world only the way a real supplier
> would … never the simulation's own internals. The mission is **carbon abatement through
> personalisation, measured in £ per tonne of CO₂ saved**."

Failures against the §3 bar:

| Bar item | Current state on the live front door | Verdict |
|---|---|---|
| **Audience** | "Where to go" doors keyed *"Energy CEO / COO"*; register/journey framing throughout | **Wrong reader** — no lay-household entry point exists |
| **Jargon (Tier-1 floor)** | "enterprise simulator", "settles half-hourly", "Elexon and NESO", "the simulation's own internals", "£/tCO₂", "epistemic wall" (elsewhere) | **FAIL** — ≥6 un-glossed domain/tech terms in the lede alone |
| **Data half** | *No plain statement of what data is taken or used* (correct — none is held — but also unsaid for a lay reader) | **Absent** |
| **Money half** | *No plain statement of what happens to money / how a bill is worked out / credit-balance protection* | **Absent** |
| **Commitment / leaving** | N/A on front door (no product to join yet) | **Absent (expected pre-F3)** |
| **Accountability** | *Present and good:* "a fully autonomous licensed supplier will not be permitted — a licence needs accountable humans — and we say so up front" | **PASS (kept)** |

**Honest read:** the front door is not *failing at its job* — its job is the expert pitch, and for
that reader it is dense-but-correct. It fails the **F2 lay-reader bar** because **that bar's surface
does not exist yet.** The one lay-facing virtue already present — the up-front accountability line —
should be *preserved* verbatim into any future explainer. (Note: `site/simplified/` is **not** this
surface — it is the internal register of *engineering* simplifications, a different artefact despite
the name.)

---

## 5. Independence & validation

- **Independent of SIM ground truth (required).** F2 touches no sim internals; there is no ground-
  truth series to leak. The relevant independence discipline is instead: the *comprehension standards*
  are validated against **external regulators/standards bodies** (ICO, FCA, Ofgem, GDS, CMA), and the
  *"where it fails"* judgement is validated against the **actual live site text**, quoted — never
  against a self-authored score of how good we think the copy is.
- **Validated now (independent already-fetched repo sources, §2):** the **data-consent trap**
  (smart-mode-on vs settlement-opt-in; "settlement purposes" ≠ consent) via
  `smart_meter_hh_data_consent_2026.md`; the **money-disclosure floor** (SLC 22A/22B/31B notice +
  annual-statement obligations) via `company_customer_comms.md`; **credit-balance ring-fencing** via
  `ofgem_licence_readiness.md`. These are the parts a build could rest on today.
- **Still `[recall, validate]` (fetch-gated):** the *comprehension-testing* standards — FCA
  Consumer Duty PRIN 2A wording, GDS reading-age-9 target, Plain English Crystal Mark, UK GDPR
  Art. 12(1) verbatim, CMA EMI comprehension remedies. None has an independent corroborating source
  in the repo corpus; register them in `ASSUMPTIONS.md` on graduation, exactly as F5 prescribes for
  its unverified figures. **These are wording/citation validations, not structural risks** — the
  *shape* of the bar (teach-back + readability floor, two-tier so it can fail) is well-established and
  low-risk.
- **Exhaustive-corpus verification (2026-07-22, second forward-discovery tick).** The "no independent
  repo corroboration" claim above was re-tested by an **exhaustive** case-insensitive sweep of the
  corpus (`docs/market_research/`, `docs/domain_artefact_library/`, `docs/vision/`, all `ASSUMPTIONS.md`,
  `company/compliance/`) across all six standards and multiple phrasings ("reading age", "Flesch",
  "Crystal Mark", "plain and intelligible", "PRIN 2A", "Article 12", "consumer understanding", …).
  **Result: confirmed — zero independent source documents corroborate the plain-language / comprehension
  content of any of the six.** Two adjacent classes of hit exist and are *not* corroboration: (a) the
  simulated company's own **compliance code** names Consumer Duty and an internal `CONSUMER_UNDERSTANDING`
  outcome (`company/compliance/consumer_duty.py`, `obligations_register.py` cites "Ofgem SLC 0" — but
  attached to the PSR-vulnerability obligation, and quoting **none** of the plain-language wording) —
  an internal artefact, not a fetched source; (b) the three already-`[VALIDATED]` research files
  (`smart_meter_hh_data_consent_2026.md`, `company_customer_comms.md`, `ofgem_licence_readiness.md`)
  corroborate *adjacent machinery* (consent regime, SLC 22A/22B/31B notice floor, credit-balance
  ring-fencing) only — exactly the scope §2 already claims. **Consequence:** no non-network path can
  close these six; they are closable only by a **live fetch of the primary sources** (or superseded if
  the director graduates F2 and they enter `ASSUMPTIONS.md` at build). This negative result is recorded
  so a future tick does not re-run the same sweep. F2 is **DISCOVER-complete** pending live fetch or
  graduation — no further autonomous DISCOVER increment is available on this track without network.

---

## 6. Candidate graduation shape (PROPOSAL ONLY — not map-registered)

If the director graduates F2, the natural minimal build is **a control before a page** (comprehension
is measured, not asserted):

- **HARNESS first (the bar):** a two-tier comprehension control — Tier-1 readability/banned-jargon
  gate over any customer-facing explainer text (automatable, R15-mutation-provable: today's
  front-door prose must fail it); Tier-2 lay-persona say-back judge over the four bar items
  (outcome-tested). This is the *durable* artefact — it outlives any single page and makes the legal
  duty *checkable*.
- **SITE second (the surface):** one plain "What Poesys does with your data and your money"
  explainer, written to pass the Tier-1 gate, preserving the existing accountability line verbatim,
  filling the two absent halves (§4) — the data half keyed to F3's consent machinery, the money half
  to the SLC/credit-balance floor (§2b).
- **Ties:** feeds **F3** (the say-back test is the acceptance gate on F3's consent screens — no
  household is enrolled through a screen that hasn't passed the bar) and repays the **P-4 visible-
  surface** discipline (a lay entry point the site currently lacks).

No atom is opened here. BUILD-open is a director/twin call.

---

## 7. One-line finding

**Explaining-what-we-do fails on the reader, not the writing:** the live public surface is a correct
expert pitch (doors keyed "Energy CEO / COO", ≥6 un-glossed domain terms in the lede) and **no
lay-household comprehension surface exists** — so the legal-duty question "can a reader say back what
we do with their **data** and **money**" is currently unanswerable. The data-consent trap, the SLC
money-disclosure floor and credit-balance ring-fencing are already validated against independent repo
sources; the missing piece is a **testable comprehension bar** (teach-back + a readability floor,
two-tier so it can fail per R15) built *before* the explainer it gates — which in turn gates F3's
consent screens. The one lay-facing line the site already gets right — up-front human accountability —
must be preserved.
