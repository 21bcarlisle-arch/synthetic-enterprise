# EP11: Direct Debit against a real sandbox. DISCOVER + FRAME

**Atom:** `EP11_adapter_gocardless_bacs` · lane `W4_the_wall` · epoch 3 · level 0 → 3 · `loop_stage: idle`
**Draw:** 16 Nov 2026 worker tick, LANE 3 (DISCOVER/FRAME only). **No BUILD code was written.**
**Level: HELD at 0.** The atom delivers an adapter, and this document is about the adapter, not the adapter
itself. That follows the precedent of EP10 (13 Aug) and EP12 (14 Aug).

"Observed" means the claim was run against HEAD (8954e9103a) on this pass. External facts carry the date of
their source. No network was used: an autonomous tick has none, so nothing here is new research.

---

## 0. What the atom says it is

- **Title:** "Direct Debit against a real sandbox."
- **`gain`:** "The money path (mandates, collections, failures) runs end to end against an external system
  before any bank relationship exists."
- **`origin_note`:** the four Bacs reports are "the highest-value part": "a cancelled mandate the company has
  not yet heard about is an arrears record that is false at source". It also notes: "sandbox yes, sponsoring
  bank no."
- **Evidence:** `docs/design/refs/ADVISOR_RESEARCH_COUNTERPARTY_APIS_EPOCH3_2026-08-05.md`, tier 2,
  "Integrate now, real sandbox".

The atom has two halves, and this document separates them. The first is **the transport**: a real external
endpoint. The second is **the unhappy-path spec**: the four Bacs reports as generators of world events. The
world-to-company path can deliver the second today. It cannot deliver the first by any autonomous route (§2).

---

## 1. DISCOVER: the rails, the seam and the wire already exist. One report of the four is entirely missing

**Observed.** These are file counts of each report name in `*.py`, outside `tests/`:

| report | what it carries | world (`sim/`, `simulation/`) | company (`company/`, `saas/`) | seam (`interface/`) |
|---|---|---|---|---|
| AUDDIS | mandate lodgement: confirmed or rejected | 3 | 3 | 1 |
| ADDACS | mandate amendments and cancellations | 10 | 6 | 2 |
| ARUDD | returned unpaid collections, with reason code | 8 | 5 | 1 |
| **AWACS** | **the payer moved their account to another bank** | **0** | **0** | **0** |

What is built:
- **The world's rails:** `simulation/bacs_rails.py` (315 lines; W5_1). It covers the 3-working-day cycle, the
  AUDDIS confirmation lag (2 working days), the ADDACS lag (1 working day), and the ARUDD return lag (up to 2
  working days after collection). It deliberately decides timing only: whether a payment fails is
  `simulation/arrears_engine.py::payment_outcome()`. `simulation/bacs_processing_day.py` lands a DD on a Bacs
  processing day.
- **The seam:** `interface/contracts/payment_observable_seam.py` (656 lines; W4_4). It has the typed payment
  observables, with the ARUDD reason code on the wire from v3.
- **The wire:** `company/interfaces/wall_protocol.py` (EP6). The payment crossing already has a named
  counterparty, `PAYMENT_SEAM_SENDER = "BACS-BUREAU-01"`, with a credential in
  `simulation/payment_seam_adapter.py`. **The company already receives Bacs observations from a bureau-shaped
  counterparty, as bytes, through a codec.** That is the half of EP11 that EP6 built.
- **The company's door for collection instructions:** `company/interfaces/dd_collection_instructions.py`
  (the KNIFE cut of B4), operated by `company/billing/dd_collections_desk.py`.

The gaps, all observed:
1. **AWACS is absent everywhere.** When a payer switches bank account, the old bank sends AWACS and the
   mandate transfers. The supplier must update the account details it holds, or the next collection goes to a
   dead account. The world never draws a bank switch, so the company never sees one. The arrears belief has
   no event for "the mandate moved but our record did not".
2. **ARUDD reason codes are sourced for 0 to 2 only on the seam.** `ARUDD_REASON_CODE` maps three of nine
   categories. The other six each carry a named gap in `ARUDD_REASON_CODE_GAP`, because the Bacs rulebook is
   members-only. `bacs_rails.ARUDD_REASON_CODES` also holds code 3 "Account Transferred", which no seam
   category maps to. That is the ARUDD side of the missing AWACS event.
3. **The ADDACS payer cancellation reuses the AUDDIS code table** (`bacs_rails.py:132`,
   `reason=AUDDIS_REASON_CODES[ADDACS_PAYER_CANCELLED]`). The text "Instruction Cancelled By Payer" is right,
   but one report's vocabulary is carrying another's. This is recorded here, not fixed: it is BUILD.
4. **The timing physics disagree at first sight, but not in fact.** The evidence says a GoCardless charge
   confirms "~4 to 5 working days after charge creation". `bacs_rails` models 3 working days from submission
   to collection, plus up to 2 for ARUDD. Bureau confirmation is the collection plus the window in which no
   return arrived, so the two agree. *Inferred; the advisor marked the bureau figure ✓ on 5 Aug.* A
   GoCardless-shaped counterparty should therefore report **"confirmed" only after the ARUDD window
   closes**, never on collection day. That is the one piece of timing physics the bureau shape adds.

---

## 2. Why "against a real sandbox" cannot be reached autonomously

There are three independent walls, any one of which is sufficient:

1. **The company has no route to the real world (W6).** `company/` and `saas/` may never open a socket. An
   adapter that calls `manage-sandbox.gocardless.com` cannot live on the company side at all. It would be a
   harness-side transport whose bytes the company reads. W6 says such bytes are "never a runtime input the
   company reads".
2. **The egress allowlist does not admit `gocardless.com`.** Observed: `background/egress_allowlist.py` admits Elexon, NESO,
   Open-Meteo, the project's tailnet, GitHub and the package registries. It does not admit `gocardless.com` or
   `bacs.co.uk` (see also the EP19 register, B5 row). Widening it is director-console-only.
3. **A sandbox account is a real-world commitment under Poesys's name.** Signing up accepts a real company's
   terms. That is a G5 class, "real-world commitments: legal, contractual". The atom's own note already put the
   sponsoring bank behind the same line.

So the level-3 target as named is the director's call, not the machine's. That has been raised in
`for_the_director` with a recommendation (§5).

---

## 3. FRAME: what level 3 can honestly mean without the sandbox

Read the `gain` as the test: does the money path run end to end against **a counterparty the company cannot
tell from a real bureau**? EP6's claim is the same: "a mock counterparty and a real one are indistinguishable
to the company." The wire already exists, so this can be tested.

| level | done means | measured by |
|---|---|---|
| 1 | Each of the four reports is a named world event, with sourced timing, a reason vocabulary, and a GAP named where a code is unsourced. **AWACS exists.** | each report has at least one world generator, and a test that can fail per report |
| 2 | The company reads all four from the bureau counterparty over the EP6 wire, and the desk acts on each one: re-lodge, update bank details, stop collecting, or re-collect. | an AWACS that the company ignores makes the next collection fail on the page (a mutation-proven row) |
| 3 | The bureau shape: Billing-Request-style mandate and payment lifecycle states. "Confirmed" comes only after the ARUDD window closes. Webhook-shaped events are delivered out of order and at least once, and the company handles duplicates. | the coupled triad: the world can defeat the company on a late, duplicated or reordered report |
| (4, director only) | The same codec against the real GoCardless sandbox, as a harness-side transport swap | not reachable; see §2 |

The **unhappy-path value is all in levels 1 to 3.** The real sandbox would test the *transport*, and EP6
already owns the transport property. It would add almost nothing to what the `origin_note` calls the
substance: the arrears belief being wrong at source.

**The first build increment (once BUILD is ungated): AWACS as a world event.** It is the only report with no
code at all. It couples directly to the D-lane's arrears belief and to the blocking level-DD finding's
"arrears are the account's balance". Before any code goes in, K8 requires the knowledge page first: amend
`docs/market_research/payments_and_direct_debit_2026-10-25.md` with what AWACS carries, its lag, and its
base rate. **Base rate: GAP.** No sourced figure for how often UK payers switch bank account per year was
found in the repo. The Current Account Switch Service publishes its switch volumes, which is the published
place to look. Until that is read, the code carries `None` with that reason.

---

## 4. What this document does not do

- It changes no level. EP11 stays at 0.
- It writes no code. The epoch gate (EPOCH_GATING_AND_ATOM_AUTHORSHIP Rule 1) forbids BUILD on this draw.
- It does not fix gap 3 (the ADDACS code reusing the AUDDIS table). That fix is BUILD, and is the first line of
  the level-1 increment.

---

## 5. Raised for the director

The atom is titled "against a real sandbox" and carries `provenance: director_ruling`. Reaching that target
needs the allowlist widened and a sandbox account, and both are his. **Recommendation:** keep the real sandbox
as a later, director-only rung. Define level 3 as the bureau-shaped counterparty over the EP6 wire (§3), which
delivers the whole unhappy-path spec without crossing any wall. Raised via `background.director_concerns`.
