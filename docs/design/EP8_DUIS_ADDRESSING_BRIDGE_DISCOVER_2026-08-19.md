# EP8 — the addressing bridge (Q5): DISCOVER pass 4

**Atom:** `EP8_adapter_dcc_duis` · lane `W4_the_wall` · epoch 3 · level 0 → 3 · `loop_stage: idle`
**Draw:** 2026-08-19 worker tick, LANE 3 (DISCOVER/FRAME only). **No BUILD code written** — the atom is
epoch-gated (`block_reason`: director-reserved curriculum sequencing, R13), and
EPOCH_GATING_AND_ATOM_AUTHORSHIP Rule 1 permits DISCOVER/FRAME on a parked atom and forbids BUILD.
**Level:** **HELD at 0.** Same call as passes 1–3 and as the sibling adapters EP10/EP12: this document is
*about* the adapter, not the adapter.

**Measured at:** HEAD `e9cdef112`. Live artefacts read and parsed in full, not sampled:
`docs/reports/run_output_latest.json` (4,154,361 B) and the 19 files under `site/data/customers/`.
Every claim is **observed-with-evidence** unless labelled **inferred** (R9).

**Why this record is a design doc and not a store append.** `docs/design/maturity_map.yaml` carries
another lane's *complete* staged atomic write at draw time (`H27_payment_belief_gap`
`simplifications_count: 45 → 46` plus its staged store file). A store append requires moving this
atom's count in that same file, which would either strand or hijack that write. Precedent is
`33c456c7e`, which took the same draw shape and made no map or store edit for the same reason.
So: **`simplifications_count` unchanged, no store append, nothing under `company/`, `sim/`,
`simulation/`, `saas/`, `tools/`, `interface/` or `background/` touched.**

---

## 0. What this pass was for

Passes 1–3 (2026-08-15, 08-17, 08-18) closed Q1, Q2 and Q6 off the DUIS specification and left the
open-question ledger with two live items. **Q5 — the addressing bridge — is answered here**, and it is
answered off the repo, which no prior pass had measured: every earlier pass read the counterparty's
specification and inferred what the company would need. This one asks what the company *has*.

The answer is worse than "a mapping table is missing", and it is worse in a way that matters before
any DUIS work starts.

---

## 1. The seam carries no meter identity at all

`run_output_latest.json::meter_read_log` — the 1,600 messages this atom is about — has **exactly one
key set** across all 1,600:

```
consecutive_estimated_count, customer_id, delay_days, estimated_consumption_kwh,
forced_catch_up, meter_type, period_end, status, true_consumption_kwh
```

There is no MPAN, no meter serial, no device identifier. The seam is keyed by **customer**. A DUIS
Service Request is addressed to a **device** (`ra:EUI`, "One EUI-64 value", pass 3 FINDING 1). So the
request the adapter exists to emit cannot be constructed from what crosses the wall today — not
because a field is unpopulated, but because no field of that kind exists on the message.

**`EUI` has no carrier anywhere in `company/`, `simulation/`, `interface/` or `saas/`.** The only
occurrences in the repo are this atom's own prior notes and `site/data/simplified.json`, which
republishes them.

### 1a. A measurement trap, recorded because it would silently defeat any census of this

A naive `grep mpan` over the published artefact returns **440 hits. All 440 are the substring inside
the word "company"** (`co-mpan-y`), which is this repo's single most common token. Word-boundary count
of `mpan` in the same 4.15 MB file: **zero**.

```
naive "mpan" count: 440    inside "company": 440    word-boundary mpan: 0
```

Any control, census or discovery pass keyed on that substring is measuring the wrong thing here and
will report the identifier as abundantly present when it is entirely absent.

---

## 2. What the publication actually says

**S5** (fetched this pass, HTTP 200): Wikipedia, *Meter Point Administration Number*. The primary
Elexon knowledge-base pages returned 403 and 404 under a browser user-agent this pass, so the primary
source was **not** retrieved — this is a **secondary** source and is labelled as such.

> "The MPAN core is the final 13 digits of the MPAN, and uniquely identifies an exit point. It
> consists of a two-digit Distributor ID, followed by an eight-digit unique identifier, then two
> digits and a single check digit."

> "The final digit in the MPAN is the check digit, and validates the previous 12 (the core) using a
> modulus 11 test … Multiply the first digit by 3 … the next prime number (5) … Repeat this for each
> digit (missing 11 out …) … The check digit is the sum modulo 11 modulo 10."

with `{3, 5, 7, 13, 17, 19, 23, 29, 31, 37, 41, 43}`, reproduced there in four independent language
listings. The same page gives the Distributor ID range (10–23 over fourteen DNO areas) and states the
**MTC is a three-digit code**.

**The headline finding does not depend on resolving this source.** The repo's own
`tools/generate_customer_data.py` docstring independently calls its algorithm "the published Elexon
modulus-11 check-digit algorithm" while computing it over a *different span* (below). Under **either**
reading, an identifier carrying **no check digit at all** is invalid — and that is what the company
mints.

---

## 3. Three implementations of one identifier, none agreeing with any other

| # | Site | Shape | Check digit |
|---|------|-------|-------------|
| 1 | `company/crm/customer_registry.py::_mpan` | 13 digits, `f"1{seed:012d}"[:13]`, `seed = sum(ord(c))` | **none computed** |
| 2 | `tools/generate_customer_data.py::_mpan` | 11-digit `bottom_line` (DNO 2 + core 8 + check 1) + 7-digit `top_line` | over **8** digits with **8** weights |
| 3 | `company/billing/meter_points.py::validate_mpan` | `^\d{13}$` | **not checked** |

Run against all 20 live accounts, with the published algorithm as the independent referee:

```
company/crm mint: validate_mpan accepts 20/20;  published algorithm accepts  0/20
tools/      mint: validate_mpan accepts  0/20;  published algorithm accepts  0/20
validator's own test fixture 1012345678901 -> invalid (expects check digit 3, carries 1)
```

Three things follow, each stated separately so none carries the verdict alone.

**(a) The validator is inverted.** It accepts every one of the 20 structurally empty identifiers and
rejects every one of the 20 from the minter that at least *attempts* a check digit — because #2's
correct-length output is 11 digits and the regex demands 13. If this control were ever wired up it
would reject the better identifier and pass the worse one.

**(b) The control cannot fail on its subject.** `validate_mpan`'s docstring asserts validity; its
subject is the digit count. Its own certifying fixture is itself check-digit-invalid, so "valid" is
defined by the same regex that checks it — an R15 **tautology**, and fail-open on the whole defect
class.

**(c) The second minter mis-states its own source.** #2 is the closer of the two — it has DNO
selection over a real ID range, a top line, and a genuine modulus-11 computation — but its docstring
claims the published Elexon algorithm while applying 8 weights to the 8-digit unique reference rather
than 12 weights to the first 12 of the 13-digit core, and emits an 11-digit core. Its `top_line` is
7 digits (PC 2 + MTC **2** + LLFC 3) where the published structure is 8 (MTC is three digits). A
reader auditing this repo would find a named, cited, plausible implementation that is wrong in three
independent ways.

### 3a. None of the three is wired to anything

Production (non-test) importers, by AST census over every `.py` outside `tests/`:

```
company/billing/meter_points.py          0    (tests only)
company/crm/customer_registry.py         0    (tests only)
company/market/dcc_meter_registration.py 0    (tests only)
```

The third is the module that models the exact DCC registration lifecycle this atom needs — SEC
registration deadlines, retries, 90-day orphans, SLC 21B returns. It is dead code, and it keys on
`mpan` + `meter_serial` with **no device identifier**, so even revived it does not reach DUIS
addressing.

---

## 4. Q5, answered

> *Q5 — addressing bridge: how does a customer become a device the DCC will accept a request for?*

**It does not, and the gap is three legs deep, not one.**

1. **customer → supply point.** The identifier exists in two mutually contradictory implementations,
   neither valid under the published algorithm, and it never reaches the seam.
2. **supply point → device.** No carrier anywhere. EUI-64 is absent from every company-side module.
   This leg has not been started.
3. **device → "the DCC will accept it".** Real-world, this is not the company's to invent: the DCC
   checks the requesting User against Registration Data to confirm it is the responsible supplier for
   that meter point. The company *learns* the mapping (via installation and the Smart Metering
   Inventory); it does not mint it. **inferred** from the access-class reading in pass 2, not from a
   clause quoted this pass.

**FRAME consequence, recorded as a recommendation and acted on by recording it
(NEVER_ASK_WITHOUT_RECOMMENDING):** leg 2 is the adapter's problem and belongs inside this atom's
BUILD. **Leg 1 is not** — it is a live CRM/billing defect that exists today, on a published surface,
independent of whether EP8 is ever built, and folding it into EP8's BUILD would hide a current defect
inside a parked epoch-3 atom. It is filed separately (§5). The right sequence is: fix leg 1 in its own
lane; build leg 2 here; never model leg 3 as a company-side decision.

---

## 5. Filed, not fixed (SELF_INTERRUPT_DISCIPLINE)

**This is partly a second instance of an already-registered class, and is recorded as one rather than
re-minted.** `docs/staging/WORKER_FINDING_THE_REGISTRATION_KEY_FOR_A_REAL_COUNTERPARTY_IS_INVALID_IN_EIGHTEEN_OF_NINETEEN_ACCOUNTS_2026-08-18.md`
(filed out of the EP9 draw, still queued) already has: the company/crm minter, the check-digit
algorithm, the 18/19 invalid count, and `validate_mpan` as a length regex with zero non-test callers.
That ground is not re-filed here.

**What is new, and is filed** as
`docs/staging/WORKER_FINDING_THE_LIVE_SITE_PUBLISHES_TWO_CONTRADICTORY_MPANS_PER_CUSTOMER_2026-08-19.md`:
the *second* minter, its false source claim, and the fact that both minters' output is **published on
the live site** — 14 of 19 customer files carry both, all 14 disagree, 0 of 28 are valid. The 08-18
finding measured the internal registry; this measures a public surface.

---

## 6. Open-question ledger after this pass

| | | |
|---|---|---|
| Q1 | which SRV | ANSWERED (pass 3) — 4.6.1 |
| Q2 | MMC or stop at the blob | ANSWERED (pass 3) — model the MMC Output Format |
| Q3 | who runs Receive Response | STILL EP6's. Unchanged; do not answer it privately |
| Q4 | where does the estimate go | **OPEN — now the only large piece behind this atom** |
| Q5 | addressing bridge | **ANSWERED this pass — three legs, §4** |
| Q6 | does the mock emit Alerts | SHARPENED (pass 3) — `DeviceAlertMessage` |

---

## 7. What this pass did not do, so the next draw is not misled

No adapter, no message re-cut, no schema vendored, no BUILD code. **No map edit and no store append**
(§ preamble) — so this atom's `simplifications_count` still reads 3 and this pass is the fourth; a
reader reconciling the two will find the reason above, not a miscount. The MPAN defects are
**measured and filed, not repaired** — the repair touches a live CRM generator, a live billing module
and a live site generator, which a LANE 3 doc-only draw does not carry. The primary Elexon source was
not retrieved (403/404); §2 rests on a secondary source and says so. Leg 3 of §4 is **inferred** from
pass 2's access-class reading, not from a clause quoted this pass. The gas/MPRN side is untouched —
`_mprn` was read but not audited, and the same page states there is no public MPRN checksum standard,
so it may have no referee at all. `dcc_meter_registration.py`'s revival is not designed here. Q4 is
untouched by this pass and remains where pass 3 left it.
