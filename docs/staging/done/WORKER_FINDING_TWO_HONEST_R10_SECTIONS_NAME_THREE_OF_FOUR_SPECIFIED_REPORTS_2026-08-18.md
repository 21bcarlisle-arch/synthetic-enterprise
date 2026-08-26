# WORKER FINDING — two R10-disclosed BUILD passes each call their Bacs report set honest, and neither names the fourth report their own spec asked for

**Severity:** LATENT · **Lane:** W4_the_wall · **Disposition:** QUEUED (not fixed on sight)

**Found:** 2026-08-18, during an EP6 DISCOVER pass resolving whether AWACS's absence was a recorded
scope cut or an omission (`docs/design/EP6_AWACS_SCOPE_AUDIT_DISCOVER.md`).
**Class:** a disclosure section that names some of its simplifications and is silent on one it should
have named, found by comparing the disclosure against the spec it was implementing.
**Measured at:** HEAD `171439629` (full `1714396299d764df5d419c4da1f164e2b959df8b`). Everything below is
`observed-with-evidence` (R9).

## The measurement

Three director-curriculum documents (`docs/design/simplifications/EP11_adapter_gocardless_bacs.yaml`,
`docs/design/refs/ADVISOR_RESEARCH_COUNTERPARTY_APIS_EPOCH3_2026-08-05.md`,
`docs/design/EP19_COUNTERPARTY_QUALIFICATION_REGISTER.md`) all independently name the same four-report
Bacs unhappy-path spec: ADDACS, ARUDD, AUDDIS, AWACS.

The seam that actually implements three of the four
(`interface/contracts/payment_observable_seam.py`, built under atom `W4_4`, wrapped by the generator
adapter under atom `W2_11`) was landed in three 2026-07-18 entries. Two of the three carry an explicit
disclosure section under the heading this project uses specifically to register a simplification openly
rather than hide it:

* `W4_4_payment_observable_seam.yaml` entry 2, **"HONEST simplifications (R10, disclosed not hidden)"**
  — lists three items: coarse ARUDD/ADDACS reason-code tables, `valid_time` not forced to
  `payload.value_date`, `CollectionRequest` correctly not wall-scrutinised.
* `W2_11_payment_behaviour_source.yaml` entry 3, **"Honest R10:"** — lists two items: ARUDD is
  return-only (no fabricated SUCCESS line), `CANCELLED_OTHER`→`INSTRUCTION_CANCELLED` kept single (no
  unsourced fan-out).

Neither list contains "AWACS not modelled" or any equivalent. The landing commit messages
(`0b17f7d114`, `e6ce3882f`) enumerate "Bacs ARUDD/ADDACS/AUDDIS" with no bracketed exclusion, matching
the yaml. The shipped code's own closed enumeration
(`OBSERVABLE_RESPONSE_PAYLOAD_TYPES`, `payment_observable_seam.py:269-276`) has six members and no
incompleteness marker. Two design documents most likely to host a scoping decision this size
(`WALLED_INTERFACES_SKETCH.md`, `GO_LIVE_SEAM_AND_INTERNAL_SEAMS_DESIGN.md`) have zero hits for "AWACS".
Repo-wide, case-insensitive, tracked files (`git grep -il "awacs"`): four hits, all prose, zero in any
Python module.

This project's own convention for a genuinely disclosed cut is visible right next to the gap: the same
`W4_4` entry discloses the ARUDD-reason-code coarseness in the same sentence as the payload it belongs
to, and `W5_1_banking_payment_rails.yaml` entry 10 names its deliberately-unmodelled UK-bank-holiday
calendar in the same sentence as the fix it sits beside. AWACS got none of that treatment.

## Why this is filed rather than fixed

`SELF_INTERRUPT_DISCIPLINE`. Fixing the gap in the SEAM means adding a payload type
(`AwacsNotice` or equivalent) to a HARDENED, BUILD-gated payment seam under an atom (`EP11` /
possibly a touch to `W4_4`'s own family) this DISCOVER pass has no authority to build against. Fixing
the gap in the RECORD (adding a sentence to two 2026-07-18 yaml entries admitting the omission) is also
not done here: those entries are append-only history per this store's own convention
(`tools/simplifications_store.py`, "It never rewrites an existing note") — the correction belongs in a
NEW entry on whichever atom picks this up, not a rewrite of the old one.

## Why it matters, stated at its real size and no larger

**It does not indict the work that was actually done.** What `W4_4`/`W2_11` built (three payload types,
the generator mapping, reason-code and lag-window physics) matches what their own disclosure sections
say they built, field for field — verified independently in
`docs/design/EP6_AWACS_SCOPE_AUDIT_DISCOVER.md` §5. This is not a claim that the shipped code is wrong.

**What it costs:** a reader who trusts a "HONEST simplifications, disclosed not hidden" section as a
complete list of what is missing from a build — which is the entire point of that heading — would not
find AWACS there, and would have to independently notice (as this pass did, five DISCOVER passes into
the same atom) that the report the spec calls the atom's own justification is the one report never
built and never named as missing. The disclosure convention this project relies on to make gaps visible
without a fresh audit each time did not catch its own most consequential gap.

**And it names the shape of a class, not just an instance.** A disclosure section is written by the
same pass that does the build, from the same vantage point that could not see what it did not build —
structurally the hardest gap for a self-disclosure to catch, and the reason a spec-vs-shipped diff
(what this finding's own DISCOVER pass did) is a different, necessary check from "did the build pass
disclose its own simplifications honestly."

## Suggested shape, recorded not asked (`NEVER_ASK_WITHOUT_RECOMMENDING`)

1. **When `EP11_adapter_gocardless_bacs` opens for BUILD, its first payment-seam task is AWACS** — add
   the payload type, wire the generator side, and this time record in the SAME entry both that AWACS was
   built and that it was the report two prior atoms' disclosures had missed, closing the record gap
   without rewriting history.
2. **Do not treat this as reason to distrust `W4_4`/`W2_11`'s other disclosures** — spot-checked in the
   DISCOVER doc and found accurate for what they cover; the finding is a coverage gap in the disclosure,
   not a falsity within it.
3. **General control worth naming for a future R10 sweep** (not built here, this is a single-instance
   finding, not a class-fix per R10's own rule against instance-fixing an absurdity class): a disclosure
   section that claims completeness against a *named upstream spec* (a `map_notes.name`/`origin_note`
   enumerating specific items, as EP11's does) is checkable by diff — the spec names N items, the
   disclosure + the shipped enumeration should account for all N. No such automated diff exists today;
   this finding was produced by a human/agent read, not a control, and would recur silently on the next
   atom with the same shape (EP12's REC transfer-reason set is the obvious next candidate to check by
   the same method, not attempted in this pass).
