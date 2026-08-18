# EP9 — consented metering via a DCC Other User: DISCOVER

**Atom:** `EP9_adapter_n3rgy_consented_metering` · lane `W4_the_wall` · epoch 3 · level 0 → 3 ·
`loop_stage: idle`
**Draw:** 2026-08-18 scheduled tick, LANE 3 (DISCOVER/FRAME only). **No BUILD code written** — no
adapter, no schema, no client, nothing in `file_scope` (which is `[]`). The atom is epoch-3
BUILD-gated (`block_reason`: director-reserved curriculum sequencing, R13); EPOCH_GATING_AND_ATOM_
AUTHORSHIP rule 7 makes DISCOVER/FRAME available on a parked atom and forbids BUILD.
**Level: HELD at 0.** No map level move made or recommended by this pass.

**Measured at:** HEAD `4e79c4c8f` (2026-08-18T15:51:52+01:00). Live artefacts read and parsed in
full, not sampled: `docs/reports/run_output_latest.json` (4,154,361 bytes, mtime 2026-08-18 15:56:22)
and `company/data/registry.db` (20,480 bytes, 19 rows). Shipped modules read as they sit on disk.
No network was used and none was attempted. Every claim is **observed-with-evidence** unless
labelled **inferred** (R9).

**Read `docs/design/EP8_ADAPTER_DCC_DUIS` first** — i.e. the 2026-08-15 DISCOVER record inside
`docs/design/simplifications/EP8_adapter_dcc_duis.yaml`. It is the sibling pass and it is
authoritative for the *seam* questions (message-model cut, granularity, comms-failure encoding).
This pass does not re-derive them. It answers the questions that pass explicitly left to this
atom's own draw, and it **corrects one of that pass's findings** (§5).

---

## 1. The atom's single cited evidence path was dead — repaired this draw

`map_records.evidence` cited `docs/staging/ADVISOR_RESEARCH_COUNTERPARTY_APIS_EPOCH3_2026-08-05.md`.
That path does not exist (`ls`: No such file or directory). The document is alive at
`docs/design/refs/ADVISOR_RESEARCH_COUNTERPARTY_APIS_EPOCH3_2026-08-05.md`, 36 lines, read in full
for this pass. This is the known moved-path class (the same repair EP8's pass made for its own copy
of the same citation on 2026-08-15, recording that EP9's remained unrepaired and belonged to this
draw). Repaired in `docs/design/simplifications/EP9_adapter_n3rgy_consented_metering.yaml` in the
same commit as this document.

---

## 2. ACCESS CLASS: the atom says "SANDBOX NOW", and it is not drawable now by this agent

The atom's `name:` field records the access class as **SANDBOX NOW**, and EP8's origin note leans
on exactly that: EP9 "is the pre-accession route that CAN be exercised for real — build them as one
message model with two transports, or the mock has no oracle." Two observations, both on disk:

**(a) No n3rgy host is reachable.** `background/egress_allowlist.py` enumerates 13 hosts:
`elexon.co.uk`, `elexonportal.co.uk`, `github.com`, `githubusercontent.com`, `nationalgrideso.com`,
`neso.energy`, `npmjs.org`, `ntfy.sh`, `open-meteo.com`, `pypi.org`, `pythonhosted.org`,
`registry.npmjs.org`, `taila062fa.ts.net`. The string `n3rgy` does not appear in that file. So the
sandbox is not reachable from this machine as configured, and **widening the allowlist is a change
to this agent's own sandbox profile** — the one real-world control CLAUDE.md keeps
director-console-only, which the agent may never widen for itself. This is not a blocker to be
worked around; it is a wall, and it is the *correct* wall.

**(b) The credential is a real household's.** The advisor research (verified 2026-08-05) records
n3rgy auth as **IHD MAC/CIN** with registration by **MPAN/MPRN** — the credentials printed on a
physical in-home display in a real home, granting access to that home's consented consumption data.
Obtaining one is contacting a real person and handling their data: reserved classes 2 and 4.

**What this means for the atom, stated plainly because it changes EP8's plan as well as this one:**
"SANDBOX NOW" is true of the *world* and false of *this lane* — the access class describes
n3rgy's public offering, not a capability this repo can exercise. EP8's oracle argument therefore
does not hold: EP9 cannot serve as EP8's live oracle without a director-console egress change AND a
real consented premise. EP8's own pass already reached this conclusion from the credential side
(its finding 5d) and recommended the published DUIS specification as EP8's oracle instead; this
pass confirms it independently from the egress side and extends it — **EP9's own exit criteria must
be satisfiable offline too.**

**RECOMMENDATION (recorded and acted on by recording it, not asked — NEVER_ASK_WITHOUT_RECOMMENDING):**
EP9's L1–L3 exit criteria should be **contract-shaped, not connection-shaped** — the adapter is
graded against the *documented* n3rgy response contract (once-daily-per-meter; midnight index read
plus a half-hourly usage file; missing days stay missing unless re-requested), reproduced as a
fixture, with a conformance test that fails when the SIM smooths any of those three properties away.
A live call is then an *optional* confirmation the director can authorise at Epoch-3, never the
thing the level rests on. The alternative — deferring the atom until real access exists — hands the
whole atom to a reserved class and parks it indefinitely; the value the atom names (the missing-day
failure surface) is documentary and is available now.

---

## 3. The registration key: 18 of 19 MPANs cannot be registered, and 6 accounts have no MPAN at all

n3rgy registers a supply point **by MPAN/MPRN**. So the MPAN is not decoration in this atom — it is
the adapter's primary key. Measured against `company/data/registry.db` (19 rows, 19 distinct MPANs):

The industry MPAN core is 13 digits, the 13th being a check digit over the first 12 (weights
3,5,7,13,17,19,23,29,31,37,41,43; sum mod 11 mod 10). Applying it to every live MPAN:

```
MPANs: 19   check-digit VALID: 1   INVALID: 18
example  C1 -> 1000000000116   expected check digit 0, actual 6
```

One passes, which is what chance gives you at 1-in-10 — **inferred**: not a designed valid one.
The generator is `company/crm/customer_registry.py::_mpan`:

```python
def _mpan(account_id: str) -> str:
    """Synthetic MPAN (Meter Point Administration Number) — 13 digits."""
    seed = sum(ord(c) for c in account_id)
    return f"1{seed:012d}"[:13]
```

Digit-count only; no check digit. (Note also that `sum(ord(c))` collides on any anagram of an
account id — not a live defect, all 19 are distinct, but it is why the numbers are dense in
`10000000001xx`.)

**Nothing checks it.** `company/billing/meter_points.py::validate_mpan` exists and is a regex on
length: `"""Return True if mpan is a valid 13-digit MPAN string."""` — it returns True for all 19,
including the 18 no real system would accept. Its name states the property; its subject is the digit
count. And it has **zero non-test callers** repo-wide (grep over all `*.py` excluding `tests/`:
the only hits are its own definition and unrelated `meter_points` locals in `saas/reporting/
css_statement.py`, `company/billing/moa_charges.py`). So the validator both cannot fail on the
defect its own name describes and never runs. **Queued as a finding, not fixed here** —
`docs/staging/WORKER_FINDING_THE_REGISTRATION_KEY_FOR_A_REAL_COUNTERPARTY_IS_INVALID_IN_EIGHTEEN_OF_NINETEEN_ACCOUNTS_2026-08-18.md`
(SELF_INTERRUPT_DISCIPLINE queues a worker's own findings by default; the fix is a change to a live
CRM generator and a live billing module, which a LANE-3 doc-only draw does not carry).

**And six metered accounts have no MPAN in existence.** The published `meter_read_log` carries 19
customer ids; the registry carries 19 account ids; **they overlap on 13**:

```
in the read log, absent from the registry:  C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4, SYN-2021-001
in the registry, absent from the read log:  C1_2, C2_2, C3_2, C4_2, C5_2, C6_2
```

The MPAN lives only in the registry. So for 6 of the 19 customers this atom's adapter would have to
serve, there is no identifier to register them with — not an invalid one, none. (The six registry
rows with no reads are successor accounts, `successor_of` — a different question, not chased.)

**Why this matters to EP9 specifically and not merely as hygiene:** a synthetic identifier is a
perfectly reasonable simplification for a simulation, right up until the atom whose whole premise is
"address a real external system by this key" is drawn. At that moment the key becomes load-bearing,
and the honest position is that today's book cannot be registered.

---

## 4. Who is addressable is answered twice, and the two answers disagree

n3rgy serves **smart** meters. So "which of our customers can this adapter serve?" is the first
question the adapter asks, and the tree answers it twice:

| source | smart |
|---|---|
| `registry.db.customers.smart_meter` | **3** of 19 accounts (C7, C8, C9) |
| published `meter_read_log.meter_type` | **1,227** of 1,600 messages, across **11** of 19 customers |

Per customer, six disagree outright — the registry says not-smart while every read in the log is
smart:

```
cust   reg_smart   log smart   log trad
C1     0                  72          0   <- disagree
C2     0                 111          0   <- disagree
C4     0                  96          0   <- disagree
C1g    0                  72          0   <- disagree
C2g    0                 111          0   <- disagree
C4g    0                  96          0   <- disagree
C7     1                 114          0
C8     1                 111          0
C9     1                 108          0
C_IC1  ABSENT            102          0
...
```

**The mechanism, inferred but with a named cause:** the registry flag is a static column written at
account creation; the log's `meter_type` rides a smart-meter penetration curve over time
(`saas/smart_meter_rollout.py`, named in `simulation/meter_reads.py`'s own anchor block). A customer
who acquires a smart meter part-way through the decade is smart in the log and 0 in the registry
forever. That is a *reasonable* thing for the world to model and an *unreasonable* thing for the
company to be unaware of — a real supplier knows which of its supply points are smart, because that
is what determines whether it can pull data at all.

**Consequence for the atom:** the adapter's addressable population is undefined. Whichever source
EP9's BUILD picks, it is wrong about 6 customers in one direction or 8 in the other, and there is no
third source to adjudicate. **RECOMMENDATION, recorded:** EP9's first FRAME output should be a
single company-side answer to "is this supply point smart, as at date D" — time-indexed, derived
from what the company has observed arriving (the read log is company-observable; the rollout curve
is a simulation internal it may not read), with the registry column either fed from it or deleted.
That is a prerequisite to the adapter, not part of it.

---

## 5. Both halves of the daily n3rgy response land on DARK consumers — correcting EP8 finding 5(a)

n3rgy's daily pull returns **two** things: a midnight index read, and a half-hourly usage file. They
have different destinations in this tree, and this pass measured both.

**The HH usage file has a written destination that has never run.**
`company/billing/smart_meter_analytics.py` defines exactly the right shape — `HHReading(customer_id,
read_datetime, kwh)` with `settlement_period`, peak classification and `SmartMeterAnalytics.ingest`.
Non-test importers of that module, grep over all `*.py` excluding `tests/`: **zero**. It is built and
dark.

**The index read's consumer is also dark — and EP8's pass said otherwise.** EP8's DISCOVER finding
5(a) states: *"THE COMPANY-SIDE CONSUMER ALREADY EXISTS AND IS WIRED … `company/billing/
smart_meter_reconciliation.py` … Non-test importers: 1 (`company/billing/monthly_bill_assembly.py`),
verified this pass."* Re-measured at today's HEAD, that is **false**, and it was false when written.
The two hits in `monthly_bill_assembly.py` are lines 197 and 222 and both are **comments**; line 197
says so in terms:

```
# company/billing/smart_meter_reconciliation.py's `is_material`, kept as its
# own named constant here rather than imported since that module models a
# different real mechanism ...
```

`grep -nE "^(from|import) "` on that file returns no smart-meter/reconciliation import. Checked at
EP8's own measurement HEAD `0f2fab3c5` as well (`git show 0f2fab3c5:company/billing/
monthly_bill_assembly.py`): the same two comment lines, the same absent import. So this was a
grep-hit counted as an import, not a regression since — stated that way because R9 requires the
direct check before asserting a cause, and the direct check exonerates the intervening commits.

**Why the correction matters rather than being a pedantry:** EP8 concluded from 5(a) that *"the risk
is changing the shape under a live consumer rather than lacking one."* With both consumers dark, the
risk is exactly inverted — **an EP9 adapter could deliver wrong data, or no data, and nothing in the
running system would notice**, because nothing running consumes either half. That is the fail-open
shape EP8's own origin note was written to guard against, arriving by a different door. Any exit
criterion for this atom that rests on "the consumer reconciles" is resting on a module that does not
execute.

---

## 6. "Missing days stay missing" — the atom's named fidelity gold still has nowhere to live

The atom's `origin_note` calls this "the valuable part and the part most likely to be smoothed away."
EP8's finding 3 already established why it cannot be represented today and this pass does not
re-derive it: the seam carries one message per customer per **billing period** (1,600 messages over
19 customers and 119 distinct `period_end` values), and a monthly message has no day that can be
missing; the only latency carrier is a single `delay_days` scalar.

What this pass adds is the search for the **re-request**, which is the second half of the contract
and the half nobody has looked for: grep across `company/`, `simulation/` and `tools/` for
`backfill|re-request|rerequest|missing_day|gap_fill` returns **no hit on any meter-data path** (the
eight `backfill` hits are all `company/compliance/*` regulatory `effective_from` backfilling, an
unrelated sense of the word). So there is no notion anywhere of the company noticing a hole and
asking again — which is precisely the behaviour the origin note says a real supplier gets wrong.
There is nothing to be wrong with yet.

**Recorded for FRAME, not built:** the missing-day surface needs three things this tree has none of
— a per-meter-per-day record that can be absent, a company-side notion of "I have a hole", and a
re-request action with its own cost and latency. §4's smart-as-at-date register is the natural
carrier for the first.

---

## 7. FRAME — what a level move on this atom would have to show

Not a promotion request; the level stays 0. Written so the opening BUILD draw does not have to
re-derive it, and so each criterion is falsifiable offline (§2's recommendation):

- **L1** — the documented n3rgy response contract exists as a fixture in the repo (daily cadence;
  index read + HH file; a day that is absent stays absent), with the source citation on each
  property. Falsifier: delete a property from the fixture and the conformance test must go red.
- **L2** — a company-side "is this supply point smart, as at date D" register exists and is the
  single answer (§4), keyed by a registration identifier that a real system would accept (§3), and
  covering all metered accounts (§3's six absentees). Falsifier: the registry-vs-log disagreement
  count above must be reproducible as a test that is red today and green after.
- **L3** — the adapter delivers both halves into consumers that actually execute (§5), the
  missing-day hole is representable and the company can be observed being wrong about it (§6), and
  the COUPLED TRIAD gap between what the company believes it has and what the world sent is measured
  per the triad rule. Falsifier: suppress N days of a meter's file and the measured gap must move.

**Prerequisites owned by other atoms, named so this one does not silently inherit them:** the
message-model cut (EP8 finding 1 — estimation must move company-side before any transport swap is
"transport-only") and the granularity change (EP8 finding 3). EP9 cannot reach L3 before either.

---

## What this pass did NOT do, so the next draw is not misled

No adapter, no client, no fixture written; no network call attempted and no egress change proposed
beyond naming that one would be director-console-only (§2). The n3rgy response contract was **not**
fetched — this lane has no route to it and no n3rgy specification text exists in the repo (checked);
§6's contract statement is the advisor research's verified wording, not a primary source, and L1
above is written to require the citation the fixture would need. The MPAN defect is **queued, not
fixed** (§3) and the §4 addressability contradiction is **recorded, not resolved** — both are
changes to live company code. The gas/MPRN side (4 of 19 rows carry an MPRN) was not examined.
Whether the six successor accounts `C1_2..C6_2` *should* have reads was not chased. EP8's findings 1,
3 and 4 were read and cross-referenced but not re-measured; its finding 2 is recorded there as
BLOCKING and appears to have been fixed since (commit `60fc315da`), which this pass noted but did
not verify.
