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
