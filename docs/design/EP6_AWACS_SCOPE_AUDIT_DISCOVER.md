# EP6 — is AWACS's absence a recorded scope cut or an omission: DISCOVER

**Atom:** `EP6_wall_protocol_typing` · lane `W4_the_wall` · epoch 3 · level 0 → 3 · `loop_stage: idle`
**Draw:** 2026-08-18 worker tick, LANE 3 (DISCOVER/FRAME only). **No BUILD code written, no protocol
designed, no adapter started** — the atom is epoch-3 BUILD-gated (`block_reason`: director-reserved
curriculum sequencing, R13); `EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1 permits DISCOVER/FRAME on a
parked atom and forbids BUILD. **Level held at 0.** No map level move made or recommended.
**Measured at:** HEAD `171439629` (full `1714396299d764df5d419c4da1f164e2b959df8b`). Live artefact
`docs/reports/run_output_latest.json` (mtime 2026-08-18 17:49:15, 4,154,361 bytes) not re-parsed this
pass — this question is about build/design records and shipped code, not the published artefact.
Every claim is `observed-with-evidence` unless labelled **inferred** (R9).

## 0. The question this pass answers

The 2026-08-18 (fifth) DISCOVER pass on this atom
(`docs/design/EP6_DEPENDENT_ATOM_PROPERTY_AUDIT_DISCOVER.md`) found that of EP11's four named Bacs
reports — ADDACS, ARUDD, AUDDIS, AWACS — the first three are shipped at the payment seam
(`interface/contracts/payment_observable_seam.py`) and AWACS has **zero occurrences in any Python file
in the repository**. It left this as an open question: *"whether AWACS's absence is a deliberate scope
cut recorded somewhere, or an omission... resolved by reading W4_4/W5_1's own records."* That reading is
done here.

## 1. Where AWACS is named — the spec side

Three documents name AWACS as part of the intended report set, all on the prose side, none of them a
build record for the seam that was actually shipped:

* `docs/design/simplifications/EP11_adapter_gocardless_bacs.yaml` `map_notes.origin_note` — *"the four
  Bacs reports... ADDACS/ARUDD/AUDDIS/AWACS are exactly the events that make that belief wrong in
  reality"* — and `map_notes.name` — *"the Bacs report set IS the unhappy-path spec -- ADDACS...ARUDD...
  AUDDIS...AWACS (account switches)."* EP11 itself has **no `simplifications:` entries at all** — it has
  never been DISCOVERed or BUILT under its own atom id; this is director-authored curriculum text, not a
  build decision.
* `docs/design/refs/ADVISOR_RESEARCH_COUNTERPARTY_APIS_EPOCH3_2026-08-05.md` — names the same four-report
  set as *"the report set that IS the unhappy-path spec."*
* `docs/design/EP19_COUNTERPARTY_QUALIFICATION_REGISTER.md` row B5 — names the same four-report set under
  the direct-Bacs counterparty row.

So the SPEC is unambiguous and consistent across three independent documents: four reports, AWACS
included, and AWACS is specifically the one whose real-world mechanism (*"a cancelled mandate the
company has not yet heard about is an arrears record that is false at source"*) is EP11's own stated
justification for outranking a happy-path payments adapter.

## 2. Where the seam was actually built — the three records that would carry a disclosed cut

Three build-record entries, all dated 2026-07-18, are the entire history of the payload family that
implements three of the four reports. Each is exactly the kind of entry this project's own convention
uses to disclose a deliberate simplification (the `"HONEST simplifications (R10, disclosed not
hidden)"` / `"Honest R10:"` phrasing appears in two of the three). Quoted in full for the relevant
clause, not paraphrased:

**`W4_4_payment_observable_seam.yaml`, entry 1 (FRAME, 2026-07-18):**
> "real Bacs services: ARUDD = returned-unpaid-DD, ADDACS = amendment/cancellation, AUDDIS =
> instruction/mandate status" — three services named, in the same sentence that introduces the payload
> family. No fourth is named and no sentence says one was cut.

**`W4_4_payment_observable_seam.yaml`, entry 2 (BUILD LANDED, 2026-07-18):**
> "6 inbound observable payloads RemittanceAdvice/BacsArruddOutcome/AddacsAdvice/AuddisReport/
> PaymentNotification/SettlementConfirmation." Then, under its own **"HONEST simplifications (R10,
> disclosed not hidden)"** heading — the exact mechanism this project uses to register a deliberate
> scope cut — three items (a), (b), (c) are listed: coarse ARUDD/ADDACS reason-code tables, `valid_time`
> not structurally forced to `payload.value_date`, and `CollectionRequest` correctly not wall-scrutinised.
> **None of the three is "AWACS/account-switch not modelled."** A section whose whole purpose is to
> disclose every simplification made discloses three and is silent on the fourth report named in the
> spec it is implementing.

**`W2_11_payment_behaviour_source.yaml`, entry 3 (ADAPTER LANDED, 2026-07-18):**
> "fills the W4_4 WallResponse from the generator -- success->RemittanceAdvice, DD failure->
> BacsArruddOutcome(reason CODE), non-DD failure->no-response (blind spot), dispute->
> NOT_KNOWABLE_YET." Then its own **"Honest R10:"** clause: *"ARUDD is return-only so no SUCCESS line
> fabricated; CANCELLED_OTHER->INSTRUCTION_CANCELLED kept single (no unsourced fan-out)."* Again a
> named, disclosed simplification section, again silent on AWACS or account-switch entirely.

**`W5_1_banking_payment_rails.yaml`** (the SIM-side rails simulator these adapters wrap) names
*"AUDDIS-style mandate setup, ARUDD-style failure returns with reason codes, ADDACS amendments"* across
its five entries — three services, the same three, in a lane whose entire subject is Bacs rails
mechanics and which ran two Expert Hour reviews (2026-07-12) explicitly hunting for undisclosed gaps.
Neither review's findings (both read in full for this pass) mentions AWACS, a bank-account-switch event,
or a fourth report.

## 3. The commit record agrees with the yaml record

The commit that landed the contract states the same three-report set in its own message, not just the
retrospective yaml note:

```
0b17f7d114  W4_4 BUILD LANDED: payment-observable seam contract (interface/) -- typed/versioned/
            bitemporal WallRequest/WallResponse, observables-only (Bacs ARUDD/ADDACS/AUDDIS +
            remittance/card/SO/settlement), async C-S3, rail-keyed portability...
e6ce3882f   W4_4 BUILD: payment-observable seam contract (interface/) -- typed/versioned/bitemporal,
            observables-only (Bacs ARUDD/ADDACS/AUDDIS + remittance/card/SO/open-banking + settlement)...
```

Both messages enumerate exactly the same three Bacs services as the yaml, at the point of landing, with
no bracketed exclusion note (e.g. no "(AWACS deferred)" of the kind this project's commit-message
convention would normally carry for a stated cut — compare `W5_1`'s own entry 10, which names its
deliberately-unmodelled UK-bank-holiday calendar in the same sentence as the fix it belongs beside).

## 4. The shipped code agrees — a closed enumeration with no incompleteness marker

`interface/contracts/payment_observable_seam.py:266-276`:

```python
# Every observable payload type this seam is permitted to carry in a
# WallResponse[ObservableResponsePayload]. Enumerated explicitly so a
# future payload addition is forced to pass the same field-level scrutiny.
OBSERVABLE_RESPONSE_PAYLOAD_TYPES: tuple[type, ...] = (
    RemittanceAdvice,
    BacsArruddOutcome,
    AddacsAdvice,
    AuddisReport,
    PaymentNotification,
    SettlementConfirmation,
)
```

This tuple is the load-bearing artefact the wall's own epistemic-verifier scrutiny is anchored to (per
the BUILD LANDED entry: "the wall test is load-bearing... enumerated over
OBSERVABLE_RESPONSE_PAYLOAD_TYPES so future payloads are forced through the same scrutiny"). It is a
closed, six-member enumeration with a docstring describing what it is FOR, not what it deliberately
excludes. Grepped repo-wide, case-insensitive, tracked files only (`git grep -il "awacs"`): four hits,
all prose (`EP19_...md`, the `ADVISOR_RESEARCH_...md`, `EP11_...yaml`, and this atom's own two prior
DISCOVER docs) plus three rendered site JSON files that echo the yaml prose — **zero in any Python
module, test, or docstring anywhere in the tree.** No `# AWACS not modelled` comment, no `TODO`, no
`NotImplementedError` branch, nothing.

Two design documents that would be the natural place for a scope decision this size were also checked
and are silent: `docs/design/WALLED_INTERFACES_SKETCH.md` and
`docs/design/GO_LIVE_SEAM_AND_INTERNAL_SEAMS_DESIGN.md` — zero occurrences of "AWACS" in either.

## 5. Verdict

**AWACS's absence is an omission, not a recorded, deliberate scope cut.** Every site that would carry a
disclosure — the two build passes' own "HONEST/Honest R10" sections (§2), the landing commit messages
(§3), the closed payload enumeration's docstring (§4), and both design documents most likely to host a
scoping decision (§4) — is silent. This is not an absence-of-evidence-is-evidence-of-absence stretch:
this project's own convention (illustrated by the ARUDD-return-only and UK-bank-holiday-calendar
examples quoted above) is to name a cut in the same sentence or the same disclosure block as the work it
sits beside, specifically so a reader never has to infer one. That convention was followed for every
other simplification in this family and skipped for exactly one — the one report the spec itself calls
out as the reason the atom exists.

This does not indict the two 2026-07-18 passes' actual work: what they built (three payload types, the
generator mapping onto them, the reason-code and lag-window physics) matches what their own disclosure
sections say they built, field for field. The gap is between what got disclosed and what the spec they
were implementing asked for, not between what got disclosed and what got built.

## 6. Recommendations, recorded not asked (`NEVER_ASK_WITHOUT_RECOMMENDING`)

1. **Do not build AWACS from this atom.** EP6 is a protocol-typing atom; AWACS is a payload, and its
   home is EP11 (`Adapter for Direct Debit collection: GoCardless bureau route`), consistent with the
   2026-08-18 pass's own recommendation 3 ("re-scope EP11 from 'build an adapter' to 'conform an
   existing seam + build AWACS'"). This pass narrows that recommendation with the evidence it needed:
   AWACS is not merely undone, it is undisclosed-undone, which changes it from a known backlog item to
   a genuine gap between two atoms' records and the tree.
2. **File this as a WORKER_FINDING** (§7) rather than fix it here — fixing it means adding a payload
   type to a BUILD-gated, HARDENED payment seam, which is BUILD work this DISCOVER pass may not do.
3. **When EP11 opens, its AWACS work should include closing this specific disclosure gap**, not just
   adding the payload: the two 2026-07-18 entries' "Honest R10" sections are the historical record and
   should stay as they are (append-only, per this store's own convention), but EP11's own build entry
   should say explicitly that AWACS was the missing quarter and name why it was missed, so a future
   reader of the payment-seam family sees the full picture across both atoms rather than needing this
   audit again.

## 7. WORKER_FINDING filed (`SELF_INTERRUPT_DISCIPLINE`)

`docs/staging/WORKER_FINDING_TWO_HONEST_R10_SECTIONS_NAME_THREE_OF_FOUR_SPECIFIED_REPORTS_2026-08-18.md`
— QUEUED, not fixed on sight. Distinct from every finding already referenced in this atom's yaml: those
concern the wall's conformance CONTROL (import-shaped, channel D's silent schema_version default, the
artefact's missing `_cache_meta`); this one concerns the DISCLOSURE convention itself (R10) failing on
its own terms inside two PASS-graded, HARDENED build entries.

## 8. Open questions, status after this pass

* **OQ6** (identity of the 93rd published key): unchanged, still open, not touched by this pass — this
  question was about build/design records, not the artefact.
* **NEW-2** (2026-08-18 pass): whether the vintage stamp's absence from the published artefact is a
  serialisation gap or a population gap. **Still open** — not addressed by this pass, which took NEW-1
  instead. Named here so the next DISCOVER draw on this atom does not have to re-read five prior passes
  to find it: it needs a live call-path trace from a `WallRequest`/`WallResponse` construction site
  (`simulation/payment_seam_adapter.py`, `simulation/conversation_response.py`, or `sim/flex_dispatch.py`)
  through to whatever, if anything, ever writes envelope fields into `run_output_latest.json` — and the
  2026-08-15 second pass's own finding ("channel F is two wires wearing one name") is the reason to
  expect the honest answer may be "neither wire reaches it," which would itself be worth stating plainly
  rather than forcing a serialisation/population binary that does not apply.
* OQ2–OQ5 of the 2026-08-17 pass: carried unchanged, not touched by this pass.

## 9. Record

Level held at 0; no map level move, no `file_scope`, no BUILD code. This document, the queued
WORKER_FINDING, and one `simplifications` entry recorded via `tools.simplifications_store.append_for_atom`
are the whole output of this pass.
