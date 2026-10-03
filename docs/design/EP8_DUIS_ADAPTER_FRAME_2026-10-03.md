# EP8 — the DUIS adapter FRAME, consolidated: DISCOVER pass 6

**Atom:** `EP8_adapter_dcc_duis` · lane `W4_the_wall` · epoch 3 · `level_current: 0` ·
`level_target: 3` · `loop_stage: idle` · `block_reason: null` (LIFTED by
`DIRECTOR_CANON_RERANKING_THE_ARC_2026-09-04` §4; the atom is drawable for DISCOVER/FRAME under
`EPOCH_GATING_AND_ATOM_AUTHORSHIP` rule 1 while BUILD stays epoch-3 gated).

**DISCOVER/FRAME ONLY — no BUILD code.** Level stays at **0**. Five prior passes on this exact
atom (2026-08-15, 08-17, 08-18, 08-19, 09-07 — commits `5768bb537`, `b031b695c`, `1aa4a3d7a`,
`00ae34c95`, plus the untracked-store-conflict pass recorded only as a design doc) already fetched
and parsed the DUIS specification, the DUIS XML Schema, the MMC (Message Mapping Catalogue), and
SEC Appendix E, and answered five of six open questions off those sources. **This pass does not
re-fetch or re-derive that ground.** Its job, and the reason it exists as a sixth pass rather than a
seventh independent re-reading, is three things the prior record does not yet do in one place:

1. **Consolidate** the five passes' answers into the single shape this draw's brief asks for — a
   named SRV set, an envelope field mapping, a transport-seam statement, and an explicit-gaps list —
   so a BUILD session does not have to reconstruct it from five documents and a 19-entry store.
2. **Re-check the dependency.** Pass 5 closed with *"no large piece remains behind this atom… EP6's
   channel-D asynchronous contract"* as the one open gate. **That gate is now closed, and with a
   specific, checkable shape this pass did not have to invent** — §3 below.
3. **Hold the line the prior passes set**: never invent a DUIS field name, response code, or SRV
   number. Every concrete token below is either quoted from the prior passes' `observed-with-evidence`
   findings (themselves traced to the fetched SEC Appendix AD/AF text) or is a name read directly off
   a file in this tree. Where a prior pass marked something `inferred` or unobtained, it stays marked
   that way here — this pass adds no new confidence to any of it.

**Primary sources, not re-fetched this pass, cited by the prior pass that obtained them:**
SEC Appendix AD (DUIS v5.3) + DUIS XML Schema v5.1 (pass 1, `5768bb537`); SEC Appendix AF (MMC v5.4)
+ embedded MMC XSD + SEC Appendix E (pass 3, `b031b695c`); the repo's own `meter_read_log` artefact
and MPAN minters (pass 4, `1aa4a3d7a`); `company/billing/monthly_bill_assembly.py`'s read-arrival
seam (pass 5, `00ae34c95`). Full citation chain: `docs/design/simplifications/EP8_adapter_dcc_duis.yaml`.

---

## 1. The wall never crosses, and this atom never widens that

Restated because it binds every line below, not because it is in doubt: `company/` and `saas/` may
not open a socket, ever, directly or transitively (CLAUDE.md, "The walls"). The DUIS adapter this
atom frames is a **mock** today and stays one until SEC accession, SREPT/SMKI issuance, UEPT, and
the User CIO's security/privacy assessment all clear (pass 3 FINDING 2's corrected four-step chain —
not the atom brief's original three). Nothing in this note, and nothing a BUILD pass on this atom
should write, makes an outbound connection. The mock lives entirely inside `company/`/`saas/`'s
existing in-process seam, behind `company/interfaces/sim_interface.py`'s discipline.

---

## 2. The SRV set this company actually needs — four, not one

The atom brief's own parenthetical ("e.g. read billing registers") names a *choice*, not a request
(pass 1 FINDING 1(d)): "read billing registers" spans at least seven SRVs in the DUIS matrix. Of
those, four are what this company's own billing and arrears modelling actually consumes, decided
against two things: what the real exchange costs (access class, latency, payload shape — pass 2/3)
and what `company/billing/` already models and would have something to feed (prepayment debt and
emergency-credit registers exist and are live: `company/billing/ppm_debt_loading.py`,
`company/billing/ppm_warrant_register.py`, `company/billing/ppm_emergency_credit_register.py`).

| SRV | Name | Role here | Security class / target latency | Status |
|---|---|---|---|---|
| **4.6.1** | RetrieveImportDailyReadLog | **Primary.** Body is a repeated `LogEntry` group, up to 31 timestamped cumulative register values per request (pass 2 FINDING 3/4, T1 Table 69) — this is what a real supplier bills from, and it is the SRV `monthly_bill_assembly`'s read-arrival seam should eventually be shaped around. | Non Critical, 30 s SMETS2+ / 16 s SMETS1 (pass 3 FINDING 2, T3) | **Recommended** (pass 3 FINDING 4) |
| **4.1.1** | ReadInstantaneousImportRegisters | Cheapest request in the book — one register value at one instant, no log (pass 1 FINDING 1(d)). Useful as the on-demand "check now" case, not as the billing source: to bill a month from it the supplier must store and difference its own reads. | Non Critical, 30 s SMETS2+ / 16 s SMETS1 | Reference case, **not** recommended as primary |
| **4.4.4** | RetrieveBillingDataLog (PaymentBasedDebtPayments) | The DUIS-side counterpart of `ppm_debt_loading.py`'s debt recovery schedule — a smart PPM meter's own record of debt payments taken at the meter. | Header-level only; body detail **not read** by any prior pass | **Open — body not yet fetched/parsed** |
| **4.4.5** | RetrieveBillingDataLog (PrepaymentCredits) | The counterpart of `ppm_emergency_credit_register.py` — top-up/emergency-credit events at the meter. | Header-level only; body detail **not read** by any prior pass | **Open — body not yet fetched/parsed** |

**Explicitly excluded, with the reason stated (not silently dropped):** 4.4.3
`RetrieveBillingCalendarTriggeredBillingDataLog` is the *meter's own* billing-calendar snapshot, not
the supplier's bill (pass 3 FINDING 4) — considered and rejected. 4.8.1
`ReadActiveImportProfileData` (half-hourly profile, up to 19,056 `LogEntry` rows, 5,600 s target) is
not recommended because the company has no half-hourly consumer on this seam today (pass 3 FINDING 4
closing note) — if that changes, it is a fifth SRV, not a replacement for 4.6.1. **The gas/MPRN side
of every one of these four is untouched by every pass to date** (pass 4 §7, pass 5 §7) and is not
resolved here either.

**What is NOT established about 4.4.4/4.4.5, stated plainly rather than guessed:** no prior pass
fetched the MMC body shape for either (only 4.6.1's and 4.1.1's bodies were read at field level, per
pass 2 FINDING 1/pass 3 T1 Tables 68-75). The recommendation to include them is a *fit* argument (the
company has a live consumer for the concept) — it is not yet a *specified* adapter the way 4.6.1 is.
A BUILD pass on the prepayment pair owes the same T1/T2 extraction pass 2 did for 4.6.1 before
writing any field name for it.

---

## 3. The dependency re-check: EP6 is closed, and it closed with the DCC case named

`EP8_adapter_dcc_duis` `depends_on: ['EP6_wall_protocol_typing']` (`docs/design/maturity_map.yaml`
line 852). That atom is **not** in the live map — it is in `docs/design/maturity_map_closed.yaml`,
`level_current: 2` == `level_target: 2` (fully built to its own target). The dependency is satisfied.

More than that: `interface/contracts/wall_envelope.py` — the "ONE shared request/response shape for
every crossing of the sim/saas seam" EP6 built — now has **four** primitives, not the two pass 1
found and the three pass 3 recommended against:

- `WallRequest[P]` (`:73`) — leg 1, the Service Request.
- `WallInterim[IT]` (`:148`, landed `21c286c15`) — a **non-terminal** leg, mandatory `payload`, no
  `status`. Its own docstring names the exact shape this atom needs: *"the reviewer's own examples
  were **DCC request/ack/response/alert**"* (`:150-153`) — DCC is the worked example this primitive
  was built against, not an analogy reached for after the fact.
- `WallResponse[R]` (`:98`) — the terminal Service Response, `OK`/`ERROR`/`TIMEOUT`/
  `NOT_KNOWABLE_YET`, bitemporal (`observed_at`/`valid_time`).
- `WallNotification[N]` (`:270`, landed `131b86df7`) — **unsolicited inbound**, no `correlation_id`,
  no `status`, mandatory `payload`, `sender` + `sequence` for gap/reorder detection, `notification_id`
  as the idempotency key for at-least-once delivery.

**This is pass 3's recommended fit, now proven rather than argued.** Pass 3 FINDING 3 recommended
riding the existing envelope and said the one genuine gap was an unsolicited-inbound shape for
Device/DCC Alerts — "one dataclass, not a protocol layer." `WallNotification` is exactly that
dataclass, and `WallNotification`'s own at-least-once/sequence contract matches DUIS §2.4's published
behaviour ("the User may receive DUPLICATE Service Responses, Device Alerts and DCC Alerts") field
for field: idempotency key (`notification_id`), gap detection (`sequence`), no request behind it
(`RequestID` is `N/A` on an Alert per pass 1 FINDING 1(b)).

**What is still open, and is correctly still EP8's own BUILD work, not EP6's:** the envelope's
*primitives* exist; a DUIS-specific *payload* type for any of them does not. Nobody has written
`DuisServiceRequest`, `DuisServiceResponse` or `DuisAlert` as a payload class, and nobody has wired a
company-side or simulation-side module to construct or receive one. **Q3 ("who runs the Receive
Response Service in the SIM") is answered at the shape level — `WallInterim`'s ack, `WallResponse`'s
later answer, `WallNotification`'s alert — and unanswered at the wiring level: no module is named.**
That wiring is BUILD, and it is now unblocked rather than gated on a primitive that does not exist.

---

## 4. The envelope mapping — DUIS/MMC fields onto the four primitives that exist today

Stated as a mapping, not a design, because nothing here is new: every DUIS/MMC-side field name is
pass 1/2's `observed-with-evidence` reading; every envelope-side field name is read off
`interface/contracts/wall_envelope.py` as it sits in this tree.

| Wall primitive | Field | DUIS/MMC counterpart | Source |
|---|---|---|---|
| `WallRequest` | `correlation_id` | `RequestID` = `BusinessOriginatorID:BusinessTargetID:OriginatorCounter` (EUI-64:EUI-64:counter), **verbatim** — pass 3's own recommendation, so the eventual swap re-keys nothing | pass 1 FINDING 1(a); pass 3 FINDING 3 |
| `WallRequest` | `request_type` | `ServiceReference` + `ServiceReferenceVariant`, e.g. the string `"4.6.1"` | pass 1 FINDING 1(a) |
| `WallRequest` | `schema_version` | the DUIS `schemaVersion` XML **attribute**, `required` on both `Request` and `Response` — a field the real counterparty cannot omit | pass 1 FINDING 1(a) |
| `WallRequest` | `payload` | the Body's chosen request element (one of 130 in the `xs:choice`) plus the mandatory `ds:Signature` | pass 1 FINDING 1(a) |
| `WallInterim` (leg 2) | `payload` | the synchronous **Acknowledgement** from the Send Command Service | pass 1 FINDING 1(b) |
| `WallResponse` (OK) | `payload` | MMC Output Format body: for 4.6.1, `RetrieveImportDailyReadLogRsp` — the naming law is *"Service Request name + suffix 'Rsp'"*, confirmed present in the parsed MMC XSD | pass 3 FINDING 1 |
| `WallResponse.payload` (4.6.1 body) | — | repeated `LogEntry`: `ElecActiveImportRegisterConsumption` (`xs:integer`, Wh, **Encrypted**), `GasActiveImportRegisterConsumption` (`xs:decimal`, m³, mult 1/div 1000, **Encrypted**), `Timestamp` (`xs:dateTime`, UTC, **Encrypted**) | pass 3 FINDING 1, T1 Table 69 |
| `WallResponse` | `error` | `ResponseCode` (189 enumerated values) when non-OK | pass 1 FINDING 1(a) |
| `WallNotification` | `payload` | `DeviceAlertMessage` (or `DCCAlertMessage`) body | pass 1 FINDING 1(b); pass 3 FINDING 1 |
| `WallNotification` | `sender` / `sequence` / `notification_id` | DUIS §2.4's named at-least-once, possibly-duplicated Alert stream — no DUIS field name is quoted for these three by any prior pass, so this row is a **structural fit claim, not a cited field mapping** | §3 above; not independently sourced |
| — | success/failure | `MessageSuccess` boolean **attribute** on `SMETSData` — no carrier on any wall primitive today | pass 3 FINDING 5(a) |

**One caution this mapping does not paper over, stated rather than left implicit.** Pass 3 FINDING 5(d)
quotes the MMC spec against itself: *"the default within the MMC XML Schema is for items to be
optional… whilst some items are optional within the schema, the item may be mandatory within the
business process."* A mock validated only against the XSD validates clean while omitting everything
the business process actually requires — the schema is permissive by its own admission, so XSD
validation is a **fail-open control on this seam** unless paired with a presence assertion. That
pairing is not built; recording it here so a BUILD pass does not ship the XSD check alone and call it
done.

---

## 5. The transport seam — what the mock stands in for, and what does not become transport-only

The atom's own origin note promises the swap at accession is **transport-only**. Pass 3 FINDING 2
and the 2026-08-15 staging finding (`WORKER_FINDING_THE_MATCHING_BILLS...`, §99: *"EP8's own `name:`
promises that the mock is shaped so 'the eventual swap is transport-only'"*) both establish that this
promise does not hold in full, and this pass does not soften that:

**What the mock cannot have, and the swap therefore adds, not just replaces:**

1. **A valid `ds:Signature`.** No SMKI Organisation Certificate pre-accession means a mock request is
   structurally complete and cryptographically void. The swap adds a signing step and a certificate
   store — a real addition, not a transport replacement.
2. **Any real EUI-64 Device ID.** Addressing is to real installed meters; the company has no carrier
   for this identifier type anywhere today (§6 below, Q5).
3. **Any real GBCS payload byte-encoding.** The mock can be exactly right at the MMC Output Format
   layer (§4) — that ceiling moved up one document from where pass 1 first drew it (pass 2 FINDING 1)
   — but the GBCS bytes underneath the MMC-parsed fields stay an explicit, named, unmodelled layer.
4. **Live DCC behaviour.** Appendix E publishes *target* response times (§2's table); the *achieved*
   distribution is in no document any pass obtained, and inventing it would be worse than today's
   `delay_days` scalar (pass 3 FINDING 2's own refusal, restated, not relaxed).

**What genuinely is transport-only, and is the honest scope of "mocked AS the real format":** the
message shape — field names, types, units, the repeated-log structure, the required `schemaVersion`,
the request/ack/response/alert choreography (§3/§4) — all validate against the real published schema
independent of signing or addressing. That is a real and checkable claim; it is narrower than the
atom's own origin note states, and this pass's correction to that note is: **replace "transport-only"
with "message-shape-only, plus a named list of what the swap must separately add."**

**DCC Boxed is not a usable substitute for a public sandbox.** It is sold, to SEC Parties only, at
undisclosed pricing (pass 1 FINDING 2) — gated on accession *and* a purchase, i.e. reserved class 1
(real money) as well as the access gate the atom brief already names. No change to that reading.

---

## 6. What is NOT established — named, not glossed

Carried forward from the prior passes, restated as a checklist so a BUILD pass sees it in one place
rather than across five documents:

- **GBCS byte-level encoding/decryption.** `SMETSData` (post-decrypt) vs `GBCSData` (pre-decrypt)
  per-data-item classification (`Encrypted`/`Unencrypted`) is specified (pass 3 FINDING 1 caveat) but
  not modelled. The decrypt step is a real company-owned choice the BUILD must make, not a gap to
  silently fill.
- **Achieved DCC latency distribution.** Only targets are published (SEC Appendix E); no achieved
  figures were obtained by any pass. `delay_days: int` cannot carry even the *target* contract today
  (sub-day targets, a SMETS1/SMETS2+ inversion, and a (service × role × device-generation) index —
  pass 3 FINDING 2) — this is a live message-shape gap, not merely an unmeasured one.
- **Schema version currency.** The obtained DUIS schema is v5.01 against a v5.3/v5.4-dated
  specification text; SEC's Appendix AD listing suggests a later revision exists and was not fetched
  (pass 1 FINDING 4(a), `inferred`). Validating against v5.01 is still a real, failing-capable
  control — it is dated, and the date belongs on the fixture.
- **No XSD validator is installed on this machine** (`xmllint` absent, `lxml` does not import, pass 1
  FINDING 4(c)). The falsifiable mock-validation control this atom owes (§4's one caution) needs a
  dependency this repo does not currently have.
- **The addressing bridge, leg 1 and leg 3 of 3 (Q5, pass 4).** Leg 2 — supply point → EUI-64 device
  ID — is this atom's own BUILD scope and has no carrier anywhere yet. Leg 1 — customer → supply point
  (MPAN) — is a **live, already-filed defect** in `company/crm/customer_registry.py`,
  `tools/generate_customer_data.py` and `company/billing/meter_points.py::validate_mpan` (filed:
  `docs/staging/WORKER_FINDING_THE_REGISTRATION_KEY_FOR_A_REAL_COUNTERPARTY_IS_INVALID...` and
  `docs/staging/done/WORKER_FINDING_THE_LIVE_SITE_PUBLISHES_TWO_CONTRADICTORY_MPANS...`) — **not
  re-filed here**, and not EP8's to fix. Leg 3 — the DCC's own acceptance of the requesting User
  against Registration Data — is `inferred`, not sourced from a quoted clause, and is correctly not a
  company-side decision to model at all.
- **The message re-cut `ReadArrival` needs (Q4, pass 5) is sized small but not done.**
  `company/billing/monthly_bill_assembly.py`'s `ReadArrivalFeed`/`ReadArrival` protocol currently
  returns the supplier's *conclusion* (`status`, `estimated_consumption_kwh`,
  `consecutive_estimated_count`) rather than a DUIS-shaped *observation* (did a read arrive, here is
  its timestamped cumulative index). Pass 5 measured that two of three fields are already company-held
  state round-tripped through the world and the third is a 3-point mean over company history — a
  small relocation — but it is unbuilt, and one branch (the first-period bootstrap, pass 5 §4) cannot
  be written at all once the cut lands, which is filed as a live world-fidelity defect
  (`docs/staging/SEAT_FINDING_THE_WORLD_ESTIMATES_A_NEW_CUSTOMERS_CONSUMPTION_AT_EXACTLY_THE_TRUTH...`),
  not re-filed here.
- **4.4.4/4.4.5 (prepayment) body shapes** — named in §2 as recommended, not yet fetched at field
  level by any pass. Do not write a field name for either until that extraction happens.
- **Gas/MPRN addressing and the gas SRV bodies** — untouched by every pass, this one included.
- **`WallNotification`'s `sender`/`sequence`/`notification_id` as a DUIS-field mapping** (§4's last
  table row) is this pass's own structural-fit reading, not a quoted DUIS clause. It should be
  checked against T1/T2's Alert-stream text before a BUILD pass relies on it.

---

## 7. What this pass did and did not do

**Did:** read all five prior DISCOVER passes and the atom's simplifications store in full; checked
`EP6_wall_protocol_typing`'s current map status (closed, level 2/2) and read `wall_envelope.py` as it
sits in this tree today, which neither pass 3 (which recommended the gap `WallNotification` fills)
nor pass 5 (which still called EP6's contract the one open gate) had open at once; confirmed by
`git log -S` that `WallInterim`/`WallNotification` landed 2026-08-21, before pass 4/5, so this is a
reading the prior passes could have had and did not state — recorded as a finding about the record,
not a defect in any one pass; checked `company/billing/` for a live prepayment consumer to ground the
4.4.4/4.4.5 recommendation in §2 (`ppm_debt_loading.py`, `ppm_warrant_register.py`,
`ppm_emergency_credit_register.py` — all present, none DUIS-aware). Wrote this consolidation.

**Did not:** fetch any new external source; parse the DUIS/MMC schemas afresh (every field name above
traces to a prior pass's extraction, not a new one); write any adapter code, payload dataclass, or
company-/simulation-side wiring; vendor any schema into the repo; resolve the MPAN defects, the
estimation cut, the gas side, or the 4.4.4/4.4.5 body shapes — each is named above as owed, not paid;
move `level_current` past 0, or touch anything under `company/`, `sim/`, `simulation/`, `saas/`,
`tools/`, `interface/` or `background/`.

**No new `WORKER_FINDING` filed (SELF_INTERRUPT_DISCIPLINE).** The EP6-closure observation in §3/§7
is recorded here, on this atom's own record, rather than minted as a defect against EP6 or against
the prior passes — nothing in it says a control failed; it says a dependency this atom had already
named is now satisfied, and says so with the evidence rather than by assertion.
