# EP6 — what the nine dependent atoms actually need from the wall protocol

**DISCOVER only. Level stays 0, `loop_stage` stays idle. No BUILD code, no protocol designed.**
EP6 is epoch-3 BUILD-gated on director-reserved curriculum sequencing (R13);
`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1 makes DISCOVER/FRAME available while BUILD is not.

**Measured at HEAD `65b26e4e4`, 2026-08-18.** Live artefact `docs/reports/run_output_latest.json`
(mtime 2026-08-18 15:56, 4,154,361 bytes, 93 top-level keys) parsed in full. Shipped modules read
as they sit on disk; nothing monkeypatched, nothing regenerated, no network.
Every claim below is `observed-with-evidence` unless labelled **inferred** (R9).

**This pass answers open question (1) of `EP6_WALL_PROTOCOL_TYPING_DISCOVER.md` (2026-08-17):**
*"whether channel D's async gap is load-bearing for all nine EP7–EP15 atoms or only some, resolved
by reading each atom's own real-world-analogue claim, not done here."* It is now done here, and the
answer refutes the recommendation that raised it.

---

## 0. The prior pass's claim, stated so it can be wrong

`EP6_WALL_PROTOCOL_TYPING_DISCOVER.md` §"SIMPLICITY GUARD READING" recommended, verbatim:

> "Channel D is the one place the guard does NOT counsel restraint: EP7/EP8/EP9/W5_1's own
> real-world analogues … name genuine asynchrony as the fidelity claim, so building the protocol
> there is the one thing nine dependent atoms actually need."

That claim has two halves — *asynchrony is the binding requirement*, and *it binds all nine*. This
pass reads each atom's own `name:`/`origin_note:` (the director-ruling curriculum text, rehomed to
`docs/design/simplifications/<atom>.yaml` under `map_notes:`) and finds **both halves false**.

## 1. Method — three properties, not one

"Asynchrony" was doing too much work as a single word. Separated into what a message shape must
actually carry, it is three independent properties:

| | property | what a shape must have | what fails without it |
|---|---|---|---|
| **P1** | **time separation** | a response that is its own event, arriving after the request returns | a single logical operation that cannot complete in one call frame |
| **P2** | **vintage stamp** | as-of / valid-time / schema-version on the message itself | two observations of the same fact are indistinguishable |
| **P3** | **unsolicited inbound** | a message with no request at all | the counterparty cannot tell you something you did not ask for |

P1 is narrower than it looks. "The answer isn't available for 15 minutes" does **not** require P1 —
a synchronous call returning `NOT_KNOWABLE_YET` followed by a re-poll represents it exactly. P1 is
required only where the answer arrives on the *counterparty's* initiative or where one logical
operation provably cannot close in one frame.

Each atom is judged against **its own text**, not against domain knowledge, except where marked
**inferred**.

## 2. The audit

| atom | P1 async | P2 stamp | P3 unsolicited | the atom's own words that decide it |
|---|---|---|---|---|
| **EP7** Elexon Insights | no | **yes** | **yes** | "IRIS real-time **push**"; "indicative prices land ~15 min after each SP with a **D+1 refresh**" — two vintages of one fact (P2); the 15-min lag is a poll-plus-status, not P1 |
| **EP8** DCC DUIS | **yes** (inferred) | **yes** | no | "mocked AS the real DUIS **request/response** message formats"; SEC schema releases version the messages. Async is inferred from DUIS being a Service Request/Service Response protocol — **not stated in the atom text or the advisor research** |
| **EP9** n3rgy | no | **yes** | no | "the supplier **pull** is ONCE DAILY PER METER"; "**missing days STAY MISSING** unless re-requested" — needs a coverage stamp and a representable absence, both P2-shaped; a pull is not P1 |
| **EP10** UK Link | **yes** (inferred) | **yes** | no | "**Project Trident** is mid-flight modernisation, so expect surface churn — **schema-drift tolerance is a requirement**" (P2, explicit); UIG arriving after its gas day is P1 by inference from batch file exchange, not from the text |
| **EP11** GoCardless/Bacs | **yes** | **yes** | **yes** | "collection confirms **~4–5 working days after** charge creation" (P1); "**webhook** events for confirmations, failures, cancellations" + "each report a generator of SIM events" (P3) |
| **EP12** CSS/REC | **yes** (inferred) | **yes** | **yes** (inferred) | "**erroneous transfers, objections and failed switches** are the substance" — an objection arrives in a window and an erroneous-transfer notice is unbidden; both inferred from REC process, not stated |
| **EP13** Carbon Intensity | no | **yes** | no | "the **forecast/actual split** is the fidelity prize — the company acts on the FORECAST and is settled against the ACTUAL". Two observations of one half-hour: the bitemporal case, pure P2. A free REST GET has no P1 |
| **EP14** cost stack | no | **yes** | no | "a published spreadsheet whose **columns move between periods** is the normal case"; "**fail-LOUD** on an unparseable publication (R15)". P2 plus an ERROR status. File ingest is synchronous by definition |
| **EP15** forecast feed | no | **yes** | no | "a forecast is a **POINT-IN-TIME ARTEFACT**: what was forecast, **as of when**, with its error unknown at the time". This atom *is* P2 |

**Tally — P2: 9 of 9. P1: 4 of 9, and three of those four by inference. P3: 2 of 9 stated (a third inferred).**

**Both halves of the prior claim fail.** Asynchrony is not what the nine need — it binds fewer than
half, and for EP13/EP14/EP15 it is not implicated at all. The one property that is *unanimous* is
the vintage stamp, which no EP6 pass has named as the requirement and which the atom family never
argues for directly — each atom asks for it in its own vocabulary (refresh, coverage, schema drift,
forecast-vs-actual, as-of) and no one had put those five words in one column before.

## 3. What is already on disk — and the second inversion

Re-measured this pass rather than inherited:

**The vintage stamp is present in the type and absent from the wire.** `WallRequest` carries
`schema_version`/`as_of`/`emitted_at`; `WallResponse` carries `schema_version`/`observed_at`/
`valid_time` (`interface/contracts/wall_envelope.py:86-127`). On today's published artefact, all of
`schema_version`, `correlation_id`, `observed_at`, `as_of`, `valid_time`, `_cache_meta` occur
**zero** times across 93 top-level keys. The 9-of-9 property has no presence on anything published.

**Correction to the 2026-08-17 pass's port count.** It recorded five W4_1 ports carrying
`schema_version` fields. Measured: **three of five** — `meter_read_port.py`, `contact_centre_port.py`,
`acquisition_funnel_port.py` have it (8 references each); `credit_bureau_port.py` and
`market_data_port.py` have **none**, not even a structurally-present-but-unpopulated field. Channel
D is weaker on the unanimous property than the prior pass credited it with.

**Channel C already has P1 and P3, deliberately.** `WallResponse`'s own docstring
(`wall_envelope.py:95-105`) states the response is "a SEPARATE event in time", matched "ONLY by
`correlation_id`", "so a consumer that has never seen (or has since forgotten) the original request
can still process this response correctly on arrival". Verified at the consumer:
`PaymentObservationConsumer.observe()` (`company/billing/payment_observation_consumer.py:416-431`)
takes a `WallResponse` and keeps **no request registry** — it dedups by `correlation_id` and never
checks that a request was made. An unsolicited counterparty message is therefore already
representable; nothing in the shipped shape requires a prior request.

**Which inverts the build order for EP11.** EP11 has the strongest P1+P3 claim of the nine — and is
the atom *most already served by shipped code*. Its named unhappy-path payloads exist at the payment
seam today: `AddacsAdvice`, `AuddisReport`, `BacsArruddOutcome` (`interface/contracts/
payment_observable_seam.py:182-222`), with ADDACS/ARUDD/AUDDIS at 17/42/23 non-test references
across `interface/ company/ simulation/ sim/`. No prior EP6 pass noticed that the seam whose payload
family *is* EP11's named report set had already been built under W4_4/W5_1.

**And it surfaces the one real hole.** Of EP11's four named Bacs reports — ADDACS, ARUDD, AUDDIS,
**AWACS** — the fourth has **zero occurrences in any Python file in the repository** (case-insensitive,
whole tree). AWACS exists only in prose: this atom's own `name:`, the advisor research, and
`EP19_COUNTERPARTY_QUALIFICATION_REGISTER.md`. AWACS is the report that says the customer's bank
account has moved — precisely the "cancelled mandate the company has not yet heard about is an
arrears record that is **false at source**" mechanism EP11's `origin_note` names as the reason the
atom outranks a happy-path payments adapter. Three quarters of the unhappy path is built; the
quarter that is missing is the one the atom was justified by.

## 4. Recommendations — recorded, not asked (NEVER_ASK_WITHOUT_RECOMMENDING)

1. **Retire "channel D async migration" as EP6's first BUILD move.** It was justified by a 9-of-9
   claim that measures 4-of-9, three of them inferred. This does not make channel D wrong — EP8/EP10/
   EP11/EP12 do need P1 — it makes it a *minority* requirement that cannot carry the atom.
2. **EP6's first BUILD move is the vintage stamp reaching the wire.** It is the only unanimous
   requirement, it already exists as fields on both envelope shapes, and it is absent from every
   published key. This is a populate-and-prove task, not a design task — consistent with all four
   prior passes concluding EP6's honest first move is conformance rather than design.
3. **Re-scope EP11 from "build an adapter" to "conform an existing seam + build AWACS."** Doing this
   before the director opens epoch 3 would be BUILD, so it is *not* done here; recorded as the
   scoping the atom needs when it opens.
4. **Do not build P3 machinery.** It exists and is load-bearing for two atoms that already reach it
   through channel C. Building a separate notification shape would be adapters-for-future-adapters
   (SIMPLICITY GUARD).
5. **Resolve the three inferred P1 verdicts (EP8, EP10, EP12) before they are relied on.** They rest
   on domain knowledge, not on the atoms' text or the advisor research — the same evidence class this
   pass just refuted a recommendation for.

## 5. Open questions after this pass

- **(carried, OQ6)** identity of the 93rd published key. Still open, and now with a stated reason: the
  2026-08-15 census recorded the **denominator (92) but not its members**, and the artefact has not
  been committed since 2026-07-29, so there is no vintage to diff against. A census that records a
  count without its key set cannot be re-diffed — worth fixing in the census, not in this pass.
- **new** whether AWACS's absence is a deliberate scope cut recorded somewhere, or an omission. Not
  found in the payment-seam modules this pass read; resolved by reading W4_4/W5_1's own records.
- **new** whether the vintage stamp's absence from the published artefact is a *serialisation* gap
  (channel C messages are in-process objects that never reach the report) or a *population* gap
  (fields left at defaults). The distinction decides whether recommendation 2 is a plumbing task or a
  correctness task, and this pass did not separate them.
- **(carried, unchanged)** OQ2–OQ5 of `EP6_WALL_PROTOCOL_TYPING_DISCOVER.md`.
