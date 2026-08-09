# ADVISOR FINDINGS — the EPC register in this simulation is never wrong, only absent or vague, and the absence carries no information

**Staged 2026-08-09 at the Director's instruction, from a lab session that ran the committed premise generator directly (repo cloned to the advisor seat; `simulation/premise_population.draw_premise_population`, n=2,000 and n=2,000 x 5 seeds, `as_of=2022-06-30`). Nothing was written to the tree by that session.**

**Proportionality, per item.** §2a (certificate wrongness) is contract-touching — implement with the mitigations named in §5. §2b (absence correlation) is narrow and reversible — just do it. §2c (the property-type side door) is a **wall** item and takes `[ACT]` first: it is truth crossing to the company side without an interface.

---

## 1. What was found

The design canon names three ways the EPC register misleads a supplier: the certificate is **absent**, it is **stale**, or it is **wrong**. `company/pricing/thermal_inference.epc_prior` says so in its own docstring — "Handles all three register error sources explicitly". Measured against the committed code, one of the three is inert, one carries no information, and one is not modelled at all.

### 1a. Where a certificate exists, it is right by construction

`tools/couple_fabric.py::_certificate_for` builds the register record from the simulation's own household object, and passes `insulation=household.insulation.value` — the SIM's own truth field, unmodified. The certificate therefore cannot disagree with the world about fabric. It can only be old.

This is already declared as an honest simplification in `simulation/premise_population.py` ("The EPC letter band reaches the company only through `insulation`... the register misdescribes fabric through its U-value assumptions rather than through a wrong band"). It is named here because the consequence is larger than the note implies: the third error source in the docstring above has no mechanism behind it.

### 1b. Staleness widens the company's error bars and never moves them

In `epc_prior`, the prior's centre (`hlc`) is computed from the certificate fields with **no age term at all**. Age enters only the spread, at `EPC_STALENESS_SD_PER_YEAR = 0.02`, in quadrature with the `EPC_MODELLING_RELATIVE_SD = 0.30` floor:

| certificate age | prior spread | prior centre |
|---|---|---|
| 0 years | 30.0% | unchanged |
| 5 years | 31.6% | unchanged |
| 10 years (expiry) | 36.1% | unchanged |

Across the entire ten-year validity window, staleness moves the company's uncertainty by **six percentage points and its best estimate by nothing**. An old certificate in this world is vaguer than a new one. It is never *wrong* in a direction.

### 1c. Certificate absence is a coin flip, uncorrelated with the home

`_draw_epc_lodgement` draws from a substream keyed on the premise id alone, and returns `None` if `rng.random() >= EPC_COVERAGE_SHARE`. It reads nothing about the property. Lodgement dates are drawn uniformly over the ten years before `as_of`, also independent of the home.

Measured on 2,000 drawn premises (seed 20260809), the 41% with no certificate are statistically indistinguishable from the 59% that have one, on every axis tested:

| axis | largest gap (pp) | chi-square p | Cramer's V |
|---|---|---|---|
| build era | 2.1 | 0.68 | 0.039 |
| true EPC band | 3.3 | 0.39 | 0.051 |
| heating system | 1.4 | 0.56 | 0.039 |
| meter cadence | 1.6 | 0.72 | 0.018 |

Sampling noise alone is ±3.3–4.5pp at these group sizes, so every gap sits inside it. Repeated across five further seeds the largest gap on any axis wanders between 0.8 and 4.1pp in random directions. Mean certificate age is 4.8–5.4 years in **every** build era.

The register's own comment in `premise_population.py` says coverage is "~60% of stock, transaction-biased"; `PREMISE_FABRIC_PHYSICS_DISCOVER.md` says it twice more. The 60% is implemented. The bias is not.

**What this does to the company.** Because absence is completely at random, the homes the company cannot see are a perfect random sample of the homes it can. Its fallback — a stock-class average — is therefore *correct in expectation* for exactly the population it is applied to. The register withholds data without withholding information.

### 1d. The mask leaks: property type crosses the wall without an interface

`couple_fabric.py` line 349 passes `property_type_hint=_EPC_PROPERTY_TYPE[household.property_type]` into the company's inference call **unconditionally** — computed from the simulation's household object, outside the `certificate is None` branch. So for the 41% with no certificate, the company is still handed the property type straight off the truth, and `epc_prior` uses it to select the stock prior's centre and floor area.

The consequence is that a live failure path is dead. `epc_prior` raises `InsufficientObservationError("no certificate and no property type — the company has no fabric prior for this premise at all")` — the honest case. In the coupling run it can never fire, because the hint is always supplied.

---

## 2. The problem to solve

Three separable problems, stated as problems. The mechanisms are the agent's to choose; it knows the tree better than this seat does.

### 2a. A certificate must be able to be wrong, and older must mean more wrong

**Director ruling, 2026-08-09: the older a certificate is, the more wrong it is — not merely the more uncertain.** This is a mean shift, not a variance widening, and §1b shows the code currently has only the latter.

Requirements:

- The register's stated fabric must be able to disagree with the simulation's truth for a home that **has** a certificate.
- The magnitude of that disagreement must grow with the certificate's age.
- The **direction** must be anchored before the magnitude is chosen. Direction is the whole finding; a symmetric error would only reproduce the widening we already have under a new name.
- The anchor must be independent of the fabric generator (the standing rule: SAP parameterises, NEED and SERL judge). RdSAP is the generator's own input and cannot be used to validate this.

**`domain-knowledge`, to be verified by an agent with network access, NOT to be built on as stated:** GB drift over a certificate's life is probably improvement-dominated — the ECO obligation and its predecessors, cavity and loft programmes, and owner improvement shortly after the transaction that triggered the lodgement in the first place. If that holds, an old certificate is biased **pessimistic**: it describes a worse home than the one that exists. Note also that certificates lodged under earlier RdSAP methodology versions were produced by a different model, which is a second, separable source of age-correlated error. Both need a real published source.

If the direction is pessimistic, the commercial consequence is concrete and is the reason this is worth building: the company over-forecasts consumption for old-certificate homes, over-collects on direct debit, accumulates credit balances, and targets efficiency advice at households that have already done the work.

### 2b. Absence must correlate with the truth, because it shares a cause with staleness

Requirements:

- Whether a premise has a certificate must depend on the premise, not on a coin.
- The correlate must be anchored, and the anchor must be published.
- **The three defects are not independent and must not be modelled as three knobs.** Absence, certificate age, and age-driven wrongness all descend from one unobserved fact about a property: how long since it last transacted. A design that sets them separately will produce a register that is incoherent in ways the company could in principle detect and exploit — for instance, homes with old certificates and homes with none would carry unrelated fabric profiles, when in life they are the same kind of home seen at two points on the same clock.

**`domain-knowledge`, to be verified:** lodgement is transaction-driven (sale or new let), so the un-certificated stock is disproportionately long-tenure owner-occupied — older, less recently improved, worse fabric. If that holds, the company's fallback prior is currently biased optimistic about exactly the homes it cannot see, and today's simulation hides that entirely.

### 2c. The company must not be handed property attributes off the truth object

**Director ruling, 2026-08-09: suppliers today are very bad at knowing anything about the property, at billing and at premise-level forecasting.** The current side door gives the company more than a real supplier has.

Requirements:

- Anything the company knows about a premise must arrive through a declared interface, with the coverage and error rate of the real-world source it stands for.
- Where the company genuinely has nothing, the "no prior at all" path must be reachable and exercised, not unreachable by construction.
- The go-live test applies: could a real UK supplier know this, and through what? If the answer is "from the simulation's household object", it does not cross.

**Advisor correction, logged.** In chat on 2026-08-09 I told the Director that the property-type side door was "arguably defensible — a real supplier usually does know property type from address data". The Director corrected this from twenty years of industry domain knowledge, and the correction is the ruling above. My original claim was `inferred` and was not checked against any source; it should have been labelled as such at the time and was not. The requirement in this section follows the ruling, not my original framing.

---

## 3. Decided vs open

**Decided (Director, 2026-08-09):**

1. Older certificate = more wrong, as a mean shift.
2. Suppliers know very little about the property; the company must not be given more.
3. The population stays stock-representative. Selecting the book to homes the register describes was proposed and rejected in the same session: it would delete a permanent feature of a real book, and it re-introduces a selected panel with the register as the selector.
4. EPC stays on the company's side of the wall as a noisy observation, never as the simulation's truth. Generating from EPC and validating against EPC is the tautology the independence rule exists to prevent.

**Open, for the agent or a discovery pass:**

1. The direction and magnitude of age-driven certificate error, and its published anchor.
2. Whether RdSAP version change is a separable channel worth its own treatment.
3. The published anchor for lodgement coverage by tenure or transaction recency.
4. What a real supplier actually holds at premise level, and through which interface — this determines the honest fallback and is the substance of §2c.
5. Whether SERL published statistics reach far enough to judge the result, or whether the named LCL fallback is needed.

---

## 4. What this does NOT touch

No change to the population composition, the truth traces, the weather chain, or the fabric physics. This is entirely the observation layer — what the company is told and what it is told wrongly. The simulation's ground truth is unchanged throughout.

---

## 5. Risk

**Blast radius.** Every committed fabric gap number moves, and all three changes push in the same direction: the company gets worse. Any report, case study or site surface quoting a gap figure becomes stale on the same commit. That is the finding working, not a regression — but it should be expected and the stale surfaces found before, not after.

**Probable failure mode 1 — an invented constant becomes the answer.** A certificate bias with an unanchored magnitude makes the headline gap a function of a number someone chose. Mitigation: anchor direction first and treat magnitude as declared-unanchored under the existing simplification discipline, so the ranking survives even if the level does not.

**Probable failure mode 2 — the new error is absorbed and the test goes quiet.** If the company's inference is tuned until it recovers the truth through the new bias, the channel exists and measures nothing. Mitigation: report the gap **split three ways** — no certificate, old certificate, fresh certificate — so the new channel is visible as a difference between groups rather than buried in a single average.

**Probable failure mode 3 — the shared cause gets lost.** Three independent knobs is the easy build and the wrong one (§2b). Mitigation: whatever carries the shared cause should be one thing, and it should be possible to show that switching it moves all three observables together.

**Standing constraint.** NEED and SERL stay on the judging side and are not touched by any of this. If any part of this work ends up parameterised by the same source that judges it, the check is theatre and should be rejected.

---

## 6. What I could not check from this seat

- I ran the generator, not the full coupling run — `tools/couple_fabric.py` needs the real Open-Meteo archive and I did not attempt it. All claims about that file are from reading it, not from running it.
- I cannot say whether the committed gap figures were produced under this exact code state.
- Everything marked `domain-knowledge` above is unverified from here and is flagged for a pass with network access before any build relies on it.
