# F3 — Volunteer programme mechanics — first DISCOVER pass

**Track:** Forward-Discovery Register F3 (mission-required × high; gated on the security-posture review).
**Class:** OPTIONAL / PREEMPTIBLE — yields instantly to any core atom next cycle.
**Discipline:** DISCOVER only — no BUILD code, no new map atoms, **hold no data**. Anchor to already-fetched
repo sources, validate against an INDEPENDENT source (never SIM ground truth), honour the epistemic wall.
**Pass:** 2026-07-22 (scheduled forward-discovery tick; core + idle-advance lanes empty/gated; F1 and F2
DISCOVER-exhausted without network, so the register directs the next increment to F3/F4 — F3 ranks higher).
**Network:** none this pass (autonomous, no interactive user — standing memory `no-network-in-autonomous-runs`).
All figures re-cited from sources fetched by prior passes, not re-fetched. Every unfilled item is labelled a
genuine gap `[recall, validate]`, never presented as fact.

---

## What F3 is, and the honesty facts it must keep true

The pitch's third discipline is *validation against reality*: "consenting volunteers would keep their own
supplier and share their data, we would run a parallel personalised bill against their actual consumption, and
publish the difference — **including where we were wrong**" (`docs/vision/pitch.md` §4). Today this exists as "a
plan and a walled interface built to receive it. **No volunteer has been approached and no real household data
has entered the system**" (ibid.). PURPOSE_PITCH_V4 makes the load-bearing honesty claims explicit and dated:
*"no external person has yet seen this work", "no household data has entered the system", "no volunteer has been
approached"* (§ time-sensitive facts). F3 must not falsify any of these — **DISCOVER designs the machinery; it
does not run it.**

The public gate the pitch commits to: the programme *"will not open until a security posture review has
completed."* PURPOSE_PITCH_V4 §4 flags the defect this pass exists to work: *"That is a public commitment. No such
review exists as an atom. It should be registered as a real gate, not an aspiration."* So F3's critical path is
two director-reserved artefacts — a **security-posture review** and the **consent machinery** — neither of which
the agent may open to BUILD (one-way doors #5 safety-posture and #7 real customer both apply).

---

## Q1 — What the security-posture review must cover

Assembled from the repo's own security-profile doctrine and UK data-protection law already cited in-repo — not
re-derived from a live standard. The review is the gate; its scope is the deliverable of this DISCOVER pass.

1. **DPIA first (UK GDPR Art. 35).** The processing is *systematic profiling of household circumstances* — the
   four-dimensional model infers economic trajectory, life events and emotional state (`docs/vision/pitch.md`
   §2c.1–2c.2: a new baby, reduced hours, "overwhelmed"). That is high-risk profiling, so a Data Protection
   Impact Assessment is **mandatory, not optional**, and must precede any data ingest. *(Which processing sits on
   the ICO's statutory DPIA-mandatory list is `[recall, validate]` pending a live ICO fetch — but the high-risk
   *class* is clear from the pitch's own description.)*
2. **Lawful-basis register — and the third-party trap (the key finding, see Q2).** Poesys is **not the
   volunteer's supplier**, so the contract-necessity basis that lets a real supplier read HH data by default
   **does not apply**. The only available Art. 6 basis is **explicit consent (Art. 6(1)(a))**; inferred
   vulnerability may pull the processing into **special category (Art. 9)**; automated personalised-bill/risk
   inference engages **Art. 22 profiling safeguards**. The review must state each basis and its safeguard.
3. **Data-minimisation spec.** The minimum field-set a parallel bill mathematically *needs* is HH consumption +
   the volunteer's actual tariff + payment method — **not** name/address/DVLA/EPC-by-name. The rich four-dimensional
   profile is the SIM's synthetic construct; for a real volunteer, ingest only what the bill arithmetic requires,
   pseudonymised at ingest.
4. **Storage & access posture — the Hardened profile.** CLAUDE.md already names this: *Hardened (Pattern C+:
   container, unreadable creds, audit, RBAC — an Epoch-5 go-live NFR blocker)*. Real household data may only land
   behind that profile: encrypted at rest and in transit, credentials unreadable to the process, RBAC, an audit
   log. The current Developer profile (secrets in a working tree, app-level egress allowlist) is **not sufficient**
   to hold real household data — the review's job is to prove the gap is closed before opening.
5. **Consent lifecycle.** Granular consent capture, a **say-back comprehension gate** (F2's teach-back test is the
   named acceptance gate on these screens — `f2_explaining_what_we_do_simply.md` §Ties), **revocation as easy as
   grant (Art. 7(3))** wired to *verified deletion*, and a stated retention limit. A consent flow whose "withdraw"
   button does not actually trigger deletion is an R11 orphan-transition defect.
6. **Breach response (Art. 33).** 72-hour notification path, defined before ingest.
7. **Channel security for the approach itself.** The first volunteer contact is an untrusted channel in both
   directions (`docs/design/PHONE_ACT_CHANNEL_THREAT_MODEL.md`: an added authority/contact channel is a
   trust-model change requiring provable, out-of-band identity binding). A volunteer approach must be authenticable
   both ways so neither Poesys nor the household can be spoofed — designed, not assumed.

---

## Q2 — Consent + data-handling design (and the third-party lawful-basis finding)

**Source A (independent, Ofgem/DESNZ):** `smart_meter_hh_data_consent_2026.md`. Its headline distinction is the
crux for F3. In the *supplier↔own-customer* relationship, HH billing reads flow to the supplier **by default, on
the performance-of-contract basis, with no opt-in step** (~90% of installed meters in smart mode, DESNZ Q4 2024);
the only genuine opt-in regime is the narrow **settlement-purpose** one (Ofgem *Decision for access to half-hourly
electricity data for settlement purposes*, 25 Jun 2019: domestic opt-in / microbusiness opt-out).

**The finding this pass contributes:** *none of that default-flow basis reaches Poesys.* A volunteer **keeps their
own supplier** (pitch §4) — so Poesys has **no supply contract** and therefore **no contract-necessity basis** to
read anything. Every byte Poesys receives rests on **explicit consent alone**, and the consent must be specific,
informed, freely given and revocable. This inverts the domestic-supplier intuition: the very fact that flows are
"default-on" for a real supplier is *why* a third-party validation partner must be **default-off, consent-gated,
minimised**. This is the discovery — the wall between "the supplier bills by right" and "we may only look by
permission" is exactly what makes the volunteer programme honest.

**Source B (independent, UK GDPR via F2):** `f2_explaining_what_we_do_simply.md` cites **UK GDPR Art. 12(1)**
(processing information "concise, transparent, intelligible") and the FCA Consumer-Duty comprehension bar. Consent
that was not *understood* is not consent — so F2's say-back test is not decoration; it is the legal validity gate
on F3's consent screen.

**Source C (independent, channel security):** the PHONE_ACT threat model — disjoint from both the data-protection
and the consumer-comprehension families — supplies the both-ways-authenticable-channel requirement for the
approach and any ongoing contact.

Three disjoint source families (data-access law · data-protection/comprehension law · channel-security), none SIM
ground truth, agree on the same direction: **consent-first, minimised, revocable, out-of-band-authenticated.**

---

## Q3 — The smallest honest volunteer pilot

Designed to cross the SIM/reality wall for the first time at the **smallest** footprint that still yields the
pitch's promised artefact (the published gap, errors included):

- **N = 1 to a handful.** The goal is a *located missing factor in a real household* (pitch §4: "discovery rather
  than embarrassment"), which one or a few volunteers already delivers; scale is not the point of the pilot.
- **Volunteer keeps their supplier — no switch, no money, no market crossing.** This deliberately stays clear of
  one-way-door #7 in its *transactional* sense: there is no real supply, no real billing, no real-money commitment
  — a shadow/parallel bill only. (The *data* crossing is still real and is what the security review gates.)
- **Consent-first, say-back-gated.** The F2 teach-back test over {data / money / commitment-and-leaving /
  human-accountability} is the acceptance gate; a volunteer who cannot say back what happens to their data does
  not proceed.
- **Minimised ingest, pseudonymised.** HH consumption + actual tariff + payment method only; no name needed for
  the bill maths.
- **Publish-the-gap-including-errors** as the standing honesty contract — the error is the finding.
- **Revocable → verified deletion** at any time, honouring the load-bearing "no data held without live consent."
- **Gate:** opens only after the DPIA + security-posture review (Q1) are **complete and proven** — not before.

---

## Epistemic wall — where the leak would be

The volunteer's real household is ground truth Poesys must *not* read except through the consent-gated, minimised,
revocable channel above. Two specific leaks the harness would have to catch if this ever built:
- **Inference beyond consent.** If the model infers vulnerability/life-events (Art. 9/Art. 22 territory) from
  consumption the volunteer consented to share *for billing comparison only*, that is a purpose-creep leak — the
  same class of intent-leak F1 flags on the SIM side, here with real legal teeth.
- **Retention/deletion theatre.** A "withdraw" control whose release triggers nothing is an R11 orphan transition;
  the harness must mutation-prove (R15) that revocation actually deletes.

The forward-discovery value: F3 is the point where the project's abstract "epistemic wall" becomes a **concrete
legal-and-security boundary** with a named owner (the director) and a named gate (the security review) — and this
pass converts the pitch's one-line public commitment into a **reviewable scope** (Q1's seven items).

---

## Candidate graduation & open items

**Candidate graduation shape** (proposal only — *no atom opened*; BUILD-open here is **doubly director-reserved**,
one-way doors #5 safety-posture and #7 real customer):
1. Register the **security-posture review as a real gate-atom** (PURPOSE_PITCH_V4 §4: "registered as a real gate,
   not an aspiration"), scoped to Q1's seven items — a *review* atom, holds no data.
2. A **consent-machinery design atom** (screens + lifecycle + deletion), buildable to a walled/dry state that
   **holds no real data**, gated by F2's say-back test and this review.

**Open items `[recall, validate]` (network-gated — recorded so they are not re-searched fruitlessly):**
- The **DCC "Other User" / Data Access Framework** accreditation route by which a *non-supplier third party* may
  lawfully receive HH data (Smart Energy Code / DCC live fetch).
- Whether the **ICO's statutory DPIA-mandatory list** explicitly names this processing class (live ICO fetch).
- Any **energy-sector precedent** for a third-party parallel-billing / shadow-tariff pilot and its consent basis.

**No further autonomous DISCOVER increment on F3 without network** — the remaining questions are all live-fetch or
director-gated. Next tick should draw **F4** (International expansion probe, still skeletal) or await director
graduation.

---

## Increment — 2026-07-22 (network-restored tick): the three open items, worked against live sources

Network was available on this scheduled tick (the standing `no-network-in-autonomous-runs` assumption did not
hold — a live probe returned real HTTP, and WebSearch/WebFetch returned substantive content), so the register's
network-gated open items were worked directly. **This did NOT lower the bar — the headline finding raises it.**
Every claim below is graded `observed-with-evidence` (a source was fetched or returned in search) or
`[recall, validate]` (still needs a primary-source confirm); none is SIM ground truth.

### Finding A (material — corrects a load-bearing prior conclusion). A non-supplier third party may NOT receive HH smart-meter data on bare consent — there is a **named regulatory accreditation gate**.

The first DISCOVER pass concluded "every byte Poesys receives rests on **explicit consent alone**" (Q2). That
identifies the right *lawful basis* but understates the *access mechanism*. The live sources show a concrete,
regulated route with its own accreditation:

- **DCC "Other User" role.** Organisations authorised by the customer can access smart-meter data via the DCC as
  an *"Other User"*; that permission **is renewed annually**, and access is only ever with the customer's
  permission. `observed-with-evidence` (WebSearch summary of Smart Energy GB / Icebreaker One / DESNZ *Review of
  the Data Access and Privacy Framework*, 2024).
- **Smart Energy Code (SEC) signatory route.** A third party that is a SEC signatory *"can access smart meter data
  of any granularity — via opt-in consent only, with regular reminders of that consent, and based on confirmation
  that the request for the third-party service comes from the individual."* To retrieve data at all, a business
  must **become a DCC User in its own right or contract with one**, and DCC Users *"must demonstrate that they
  meet regulated privacy and security requirements on an ongoing basis."* `observed-with-evidence`
  (openenergy.org.uk fetch + WebSearch summary).
- **Consent-tier structure of the Data Access & Privacy Framework.** Opt-in consent is required before any
  supplier *or* third party can access consumption data at sub-daily (below one-day) granularity; monthly is the
  default, daily is opt-out, **half-hourly is opt-in** — the same tier structure a supplier faces, but a third
  party additionally carries the accreditation above. `observed-with-evidence` (WebSearch summaries; the primary
  DESNZ 2024 DAP-framework review PDF and the Fieldfisher legal summary are named but 403'd this pass —
  `[recall, validate]` for the exact tier wording and the annual-renewal cite from a primary source).

**Why this matters for F3.** The correction does not weaken the epistemic/consent argument — it **strengthens the
security-review scope (Q1)**. Consent is still the only Art. 6 basis available to a non-supplier (Finding A does
not touch the lawful-basis finding of Q2); but *on top of* consent, receiving HH data from the DCC requires SEC
signatory + DCC User accreditation and a demonstrated, audited privacy-and-security posture — i.e. a named
external instantiation of exactly the **Hardened profile** Q1.4 already demanded. So Q1 gains an eighth review
item: **regulatory-access accreditation** (SEC/DCC-Other-User status, or an accredited intermediary) is a
precondition of any at-scale ingest, not an afterthought.

**And it sharpens the smallest-honest-pilot (Q3).** There is a data path that avoids the accreditation regime
entirely at N=1: the **volunteer supplies their own data** (their supplier's midata download / their own DCC
Other-User grant / an exported bill + consumption file), handing it to Poesys directly rather than Poesys
reaching into the DCC. That keeps a handful-scale pilot clear of the SEC/DCC accreditation surface (the volunteer
is exercising their *own* access right), while making explicit that **any move beyond volunteer-mediated
hand-over triggers the accreditation gate** — a clean, honest scale boundary the pilot design should state
up front.

### Finding B (validates and names the criteria). ICO DPIA is confirmed **mandatory**, on named triggers.

The first pass asserted a DPIA is mandatory from the high-risk *class*; the ICO framework confirms it on specific
triggers. Art. 35(3)(a) automatically requires a DPIA for *"systematic and extensive evaluation of personal
aspects based on automated processing, including profiling, on which decisions are based that produce legal or
similarly significant effects."* The ICO's own high-risk criteria add **profiling/evaluation**, **vulnerable data
subjects**, and **innovative use of new technology**; meeting **two or more** criteria means a DPIA is required.
F3's processing (systematic profiling of household economic/vulnerability circumstances inferred from HH
consumption, using a novel modelling stack, on a potentially vulnerable population) meets **at least three** —
DPIA-mandatory is now `observed-with-evidence`, not merely inferred. Sources: ICO *When do we need to do a
DPIA?* and *Examples of processing 'likely to result in high risk'* (Art. 35(4) list) + EDPB UK Art. 35(4) list
(WebSearch summaries; the ICO high-risk-examples page itself 403'd this pass — the *exact* enumerated Art. 35(4)
items remain `[recall, validate]` against a primary fetch, but the mandatory verdict does not depend on them).

### Finding C (the missing precedent, now located — with a caveat). The energy-sector precedent is **midata**.

The first pass could not find an energy-sector precedent for third-party access to consumption data. It is
**midata in energy**: the consent-based electronic transfer of a customer's consumption + account data from a
supplier to a third party (e.g. a price-comparison site) via API, delivered through **Ofgem supply-licence
conditions** under powers in the **Enterprise and Regulatory Reform Act 2013**; opt-in consent is required for
sub-daily granularity, and the customer must be offered at least an ongoing-access option and a
specified-frequency option. `observed-with-evidence` (GOV.UK *Implementing midata in the energy sector* +
Ofgem midata materials, WebSearch summaries). **Caveat, honestly stated:** the most concrete Ofgem update I could
fetch (2020) records midata as **paused for 2020/21**, and the current live framework is the **DESNZ 2024 Review
of the Data Access and Privacy Framework** plus a 2024 *Consumer and Third-Party Access to Energy Data* call for
evidence — so midata is the closest *structural* precedent (consent-based, licence-mandated, third-party access
to energy consumption data), but its *current operational status* is `[recall, validate]` pending a
post-2023 primary source. Either way it corroborates the direction: third-party access to energy consumption
data is a **regulated, consent-gated, licence-instrumented** activity, not a free-consent free-for-all.

### Net effect on the candidate graduation and the honesty facts

- The two director-reserved graduation artefacts are unchanged in shape (a security-review gate-atom; a
  holds-no-data consent-machinery atom), but the **review gate-atom's scope grows an accreditation item**
  (SEC/DCC-Other-User, or accredited-intermediary, or volunteer-mediated-only) — a stronger, more concrete gate.
- The load-bearing honesty facts remain true and untouched: **no volunteer approached, no household data held.**
  DISCOVER designed the machinery against live law; it ran nothing.
- **Open items now mostly closed.** DCC "Other User" route: `observed-with-evidence` (annual-renewal + SEC/DCC
  accreditation confirmed). Energy-sector precedent: **located** (midata). ICO DPIA-mandatory: **confirmed** on
  named triggers. Residual `[recall, validate]` (need a primary fetch, minor): the *exact* Art. 35(4) enumerated
  list wording, the primary DESNZ-2024 tier wording, and midata's *current* operational status. These are
  refinements, not open questions of direction — **F3 is DISCOVER-complete to the depth this lane warrants.**
