# Domain Artefact Library — index

**Instruction:** `docs/staging/DOMAIN_ARTEFACT_LIBRARY.md` (advisor-staged, director-decided,
2026-07-10, amended 2026-07-11). Background-lane discovery: mine external published prior
art (UK market specs, regulatory codifications, open-source domain models, process
taxonomies) rather than reinvent, feeding the invariant library, ASSUMPTIONS.md lineage, and
Epoch 2/3/4 framing.

**Genuinely multi-session scope.** This index and the entries linked from it are built
incrementally across passes, not delivered as one closed survey — each pass adds real,
evidence-backed entries and is honest about what remains un-surveyed.

## Provenance tags (from the instruction, non-negotiable)

- `company-knowable` — passes the "could a real UK supplier know this?" test; may inform
  organs inside the wall.
- `generator-anchor` — may shape SIM generation.
- `validator-anchor` — may feed the invariant library / sanity daemon / population tests.

`generator-anchor` and `validator-anchor` are mutually exclusive per source (no
marking-own-homework). `company-knowable` may combine with `validator-anchor`. The
company's runtime must never consume generator- or validator-tagged material.

## Non-negotiables carried into every entry

- R9: every entry cites source, URL, version/date — no narrative claims without fetched
  evidence.
- No dependency adoption: schemas, data models, enumerations, and design patterns are in
  scope to borrow; adopting external code as a runtime dependency is out of scope (separate
  proposal required). Licence recorded for anything whose design is borrowed.

## Entries (Pass 1, 2026-07-11 — CLOSED, real evidence landed)

| Source | Provenance tag | Verdict | Entry |
|---|---|---|---|
| PowerTAC 2020 competition/game specification | generator-anchor | ADAPT (tariff rate-type taxonomy, tariff lifecycle state machine); SKIP (default-broker, tournament/replay — too thin, SSRN blocked automated fetch) | [powertac_2020.md](powertac_2020.md) |
| Kill Bill (billing/subscription platform) | none cleanly applies — see tag-scheme gap below | ADAPT (dunning-ladder shape); SKIP (invoice lifecycle, entity split) | [killbill_lago.md](killbill_lago.md) |
| Lago (billing/subscription platform) | none cleanly applies — see tag-scheme gap below | SKIP (draft-invoice lifecycle has no analogue in a programmatically-generated bill) | [killbill_lago.md](killbill_lago.md) |
| TigerBeetle (double-entry ledger) | validator-anchor | ADOPT — already followed by `bitemporal_event_log.py`'s append-only design | [tigerbeetle_xtdb.md](tigerbeetle_xtdb.md) |
| XTDB (bitemporal database) | validator-anchor | ADOPT — already followed; terminology confirmed aligned | [tigerbeetle_xtdb.md](tigerbeetle_xtdb.md) |

**Tag-scheme gap found this pass:** the three-tag scheme (company-knowable /
generator-anchor / validator-anchor) is built for DATA sources crossing the SIM/company
wall. It has no clean home for an external SOFTWARE-DESIGN reference (Kill Bill, Lago —
neither a data anchor nor a company-observable fact). Flagged, not resolved unilaterally —
registered for the instruction's own maintainer to decide whether a fourth tag or an
explicit "design-reference, no runtime tag" category is warranted; every entry above states
its own best-fit reading in the meantime.

**Real, cited follow-ups these entries themselves registered** (not started this pass):
PowerTAC's two ADAPT verdicts (rate-type taxonomy, tariff lifecycle) have not yet been
checked against this project's actual `company/billing/contract.py`; Kill Bill's dunning
ladder has not yet been compared against `arrears_engine.py`'s real collections logic.

**PowerTAC follow-up completed** (2026-07-12): [powertac_2020_followup.md](powertac_2020_followup.md)
— rate-type taxonomy 5/7 already covered (missing: sign-up incentives, consumption-tiered/block
rates, latter low real-world value for GB domestic); lifecycle finding is fragmentation, not a
missing state — at least 3 mutually-unaware `ContractStatus`-style enums exist across
`company/billing/contract_manager.py`, `company/crm/contract_exposure_register.py`,
`company/crm/customer_registry.py`, none wired to the live pricing path
(`company/billing/contract.py`/`simulation/renewals.py`, which itself has no status field at
all); concrete adoption candidate registered: consolidate onto one small closed lifecycle
(PowerTAC-shaped) and build the currently-absent supplier-initiated tariff-withdrawal +
forced-successor-migration mechanism.

## Still un-surveyed (registered, not started)

UK market specs: REC / Energy Market Data Specification / DTC flow catalogue; MHHS
Programme baselined design artefacts (TOM, interface catalogues, method statements); Elexon
BSC + BSCPs; Smart Energy Code / DCC DUIS; CSS switching schedules.

Regulatory process codifications: Ofgem SLCs (bill content, back-billing, debt path, PSR);
Complaints Handling Standards Regulations; Bacs DD failure/cancellation reason-code sets;
Ofgem price cap model (published cost stack); Consolidated Segmental Statements and
challenger Companies House accounts as comparator benchmarks.

Open-source domain models still open: ERPNext / Odoo (GL, AR/AP, reconciliation); open
CRM/ticketing (complaints/contact-centre entity design).

Process taxonomies: APQC PCF (utilities); TM Forum eTOM.

## Required outputs (from the instruction) — status after Pass 1

- (a) The tagged library itself, in-repo, with an index — BUILT (this file + 3 entry files).
- (b) Anchor candidates promoted into ASSUMPTIONS.md lineage — NOT done this pass. Pass 1's
  ADOPT verdicts (TigerBeetle/XTDB) validate already-built code rather than producing a new
  anchor value to promote; the two ADAPT verdicts (PowerTAC) need the real code-comparison
  follow-up above before anything is promotable.
- (c) Adapter-schema candidates registered as WALLED_INTERFACES inputs — NOT done this pass.
  None of Pass 1's 3 sources produced an adapter-schema candidate specifically (that's more
  the REC/DTC/MHHS/Elexon/SEC survey's territory, still un-surveyed).
- (d) Invariant-library extension candidates (validator-tagged sources only) — NOT done this
  pass. TigerBeetle/XTDB are validator-anchor but validate an EXISTING mechanism rather than
  suggesting a new invariant to add.
- (e) Coverage-gap report (module tree vs external taxonomies) — NOT started; needs the APQC
  PCF/eTOM survey first (still un-surveyed).
- (f) Per-source adopt/adapt/skip verdict table — DONE for Pass 1's 3 sources (table above).

## Open question registered, not answered (per the instruction's own item 4)

Whether the go-live company runs real open-source corporate machinery (ERP/CRM) behind the
wall versus bespoke organs shaped like them. Logged here for the WALLED_INTERFACES framing —
not decided in this pass.
