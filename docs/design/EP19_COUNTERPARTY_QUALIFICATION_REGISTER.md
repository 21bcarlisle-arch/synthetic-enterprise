# EP19 — Counterparty Qualification Register (Part B: the industry-systems side)

**Atom:** `EP19_counterparty_qualification_paths` · lane `F_risk_compliance` · epoch 5 · level 0 → 2 · `loop_stage: idle`
**Draw:** 2026-08-13 worker tick, LANE 3 (DISCOVER/FRAME only). **No BUILD code written.** The atom is
epoch-gated (`block_reason`: director-reserved curriculum sequencing, R13); EPOCH_GATING_AND_ATOM_AUTHORSHIP
Rule 1 permits DISCOVER/FRAME on a parked atom and forbids BUILD.
**Level this pass:** 0 → **1**. This document IS the L1 deliverable. The atom's own `origin_note` states
its ceiling in terms of this artefact — *"deliberately a REGISTER and not an action… the atom's whole
value is that the qualification paths are known and costed before anyone commits"* — so the register is
the thing the atom is, not discovery *about* something else. (Contrast `EP10_adapter_uk_link_xoserve`,
held at 0 this same day: there the deliverable is an adapter and the doc is only DISCOVER about it.)

## The one-register rule

The atom's `origin_note` requires that this and `F5_ofgem_licence_readiness` **"share one register rather
than grow two."** That is honoured here as **one register in two parts, with no row restated in both**:

- **Part A — the licence itself:** `docs/design/F5_LICENCE_READINESS_REGISTER.md` (11 rows: SLC 4A/4B/4C,
  Minimum Capital Requirement, milestone assessments, CCB ring-fencing, application process).
- **Part B — the industry systems:** this file (the rows below).

Rows are **not** duplicated across the two files, deliberately: a copied row is a second mirror, and one
mirror always ends up pinned while its sibling drifts. Part A is the **root** of Part B — see
[§ The paths are a graph](#the-paths-are-a-graph-not-a-checklist) — so the two are read together, not merged.

## How to read this register

**Access class** partitions *every* counterparty the wall faces, not just the gated ones — a "gated
counterparty" checklist with no denominator cannot tell you what fraction of the wall is actually blocked:

- **OPEN** — no qualification of any kind; usable today.
- **SANDBOX** — a real external system exercisable today without qualifying, via a named proxy route.
- **GATED** — access requires completing a named qualification path.

**Source marker**, per R9 (`observed-with-evidence` vs `inferred`):

- **✓** — verified by live web search on 2026-08-05 by the advisor and recorded in
  `docs/design/refs/ADVISOR_RESEARCH_COUNTERPARTY_APIS_EPOCH3_2026-08-05.md`.
- **~** — advisor knowledge as recorded in the same document, explicitly flagged there as *"verify current
  before build"*. Not independently confirmed.
- **inf** — `inferred` by this pass from the repo's own code or from the named sources' structure. Stated
  as inference, never as a finding.

**No claim in this file was verified live this pass.** Autonomous runs have no network, so this is a
consolidation of an existing dated source plus direct reads of this repo — the same standing this
project's Part A register has. The 2026-08-05 verification date is the freshness of every ✓ row.

## Register — Part B

| # | Counterparty / system | What it gates | Named qualification path | Access class | Pre-qualification route | Company-side status |
|---|---|---|---|---|---|---|
| B1 | **DCC** (Data Communications Company) — smart metering | DUIS service requests (e.g. read billing registers) against smart meters | **SEC accession** (party to the Smart Energy Code) → **SMKI** certification (Smart Metering Key Infrastructure) → **CIO/UIT** testing ~ | **GATED** ~ | **Yes** — *DCC Other Users* (n3rgy, Hildebrand/Glow) operate registered adapters and expose consumer-consented APIs; n3rgy runs live **and** sandbox services, auth by IHD MAC/CIN, registration by MPAN/MPRN ✓ | No DCC adapter and no accession. Nothing published depends on one. |
| B2 | **CSS / REC** — switching (electricity CSS operated by DCC; gas Supply Point Switching) | Switching-adjacent APIs, administered through **RECCo** under the **REC Data Access Matrix** | **REC eligibility confirmed by the REC Code Manager** before access ✓ | **GATED** ✓ | **None named** — the advisor's sweep found no sandbox or proxy route for REC-administered APIs | `company/market/css_performance_register.py` already models CSS 5WD/ET KPI reporting — i.e. it models the **post-qualification** world. Zero non-test importers (verified this pass), so no published figure rests on the unheld qualification. |
| B3 | **Xoserve / CDSP** — UK Link (gas) | Supply Point Switching, Supply Point Enquiry, Meter Asset Enquiry (via RECCo), Supply Point Quantities | **Data Services Contract (DSC) / UK Link User Agreement**; entitlement per user type set by the **UK Link DPM** (the register of which user types may access which data items) ✓ | **GATED** ✓ | **None named**. Note *Project Trident* is mid-flight modernisation — expect surface churn ✓ | `company/market/shipper_code_register.py` models shipper codes + LDZ authorisations; `company/crm/supply_point_register.py` likewise. Zero non-test importers each (verified this pass). See `EP10_adapter_uk_link_xoserve`. |
| B4 | **Xoserve — Shippers-only surface** (subset of B3) | **Supply Point Quantities**, restricted to Shippers ✓ | B3's DSC/UUA **plus** shipper status: UNC accession + transportation agreements + per-LDZ authorisation **inf** (from `shipper_code_register.py`'s own docstring, not from the advisor source) | **GATED** ✓ | None | Same as B3. The shipper prerequisite is a **repo-side inference** and is one of the open items below. |
| B5 | **Bacs** — direct submission | Direct Debit collection submitted by the company itself; the ADDACS / ARUDD / AUDDIS / AWACS report set | **Sponsoring bank** → **Service User Number (SUN)** → **Bacstel-IP** submission ~ | **GATED** ~ | **Yes** — bureau route: GoCardless full free sandbox (mandate + payment lifecycle, webhooks); the DD adapter can run end-to-end **before any bank relationship exists** ✓ | No bank relationship; none required. Reserved-class boundary: a sponsoring bank is a real organisation and real money (classes 1 and 2). |
| B6 | **Elexon** — settlement & market data (Insights, IRIS, Data Archive) | Nothing. All BMRS datasets are open via website, REST API, IRIS push and archive ✓ | — | **OPEN** ✓ | n/a | Already consumed (SSP). |
| B7 | **Elexon** — *trading* notification (ECVN → ECVAA) | Submission of energy contract volume notifications | **Not named by the source.** The advisor records only that an API route is consulting with planned launch **June 2027**, and that submission is legacy channels until then ✓. BSC party accession + an ECVNA is the expected shape **inf** | **GATED** ✓ (path **inf**) | None | No trading submission path. **This is the one gated counterparty whose qualification path this register cannot name** — see open items. |
| B8 | **NESO** — Carbon Intensity API | Nothing; free, no key ✓ | — | **OPEN** ✓ | n/a | Available to the carbon lane today. |
| B9 | **Ofgem / DNOs / NESO** — published cost-stack files (price cap annex model, CDCM DUoS, TNUoS, BSUoS) | Nothing; published as spreadsheets, not API'd ~ | — | **OPEN** ~ | n/a | File-ingest parsers with schema-drift tolerance, not REST clients. |
| B10 | **Ofgem** — the supply licence itself | Holding a supply licence at all | **Part A** — `F5_LICENCE_READINESS_REGISTER.md`. Not restated here. | **GATED** | n/a | See Part A. |

## The paths are a graph, not a checklist

The atom's source sentence — *"every gated counterparty names its own qualification path, so the Epoch-5
checklist is writing itself"* — is true and understates the structure. The paths **depend on each other**,
and a flat checklist hides the ordering:

```
  B10  Ofgem supply licence (Part A)
   │      the licensed-supplier status the industry codes are written around
   ├──► B2  REC eligibility (REC Code Manager)  ──► CSS + gas Supply Point Switching
   │          │
   │          └──► B3's Meter Asset Enquiry is administered *via RECCo* ✓
   ├──► B3  DSC / UK Link User Agreement  ──► UK Link surfaces
   │          └──► B4  shipper status (UNC)  ──► Supply Point Quantities
   ├──► B1  SEC accession ──► SMKI ──► CIO/UIT  ──► DCC DUIS
   └──► B5  sponsoring bank ──► SUN ──► Bacstel-IP  ──► direct Bacs
```

Two consequences that the flat list does not give you:

1. **B2 is on more than one path.** Meter Asset Enquiry is a UK Link surface *administered via RECCo* ✓ —
   so REC eligibility gates part of B3, not only B2. REC is the most load-bearing single qualification here.
2. **B1 is the only serial chain.** SEC → SMKI → CIO/UIT is three sequential qualifications, each with its
   own counterparty. Its lead time is therefore not comparable to a single accession, and it is the one
   most likely to set the go-live date — **if** the ~ marker on it survives verification.

## The finding that matters for sequencing: two of five gated paths have a bypass, three do not

| Gated counterparty | Exercisable before qualifying? |
|---|---|
| B1 DCC | **Yes** — DCC Other Users, live + sandbox ✓ |
| B5 Bacs | **Yes** — bureau/GoCardless sandbox ✓ |
| B2 CSS/REC | **No route named** |
| B3/B4 UK Link | **No route named** |
| B7 ECVN/ECVAA | **No route named**, and no path named either |

The two adapters the advisor calls *"the wall's most failure-rich — money and meters"* are precisely the
two with real pre-qualification routes. **The critical path to go-live is therefore REC/RECCo, DSC/UUA and
the trading channel** — the three that can only ever be mocked until a real qualification completes. That
is a sequencing statement about the register; it is **not** a recommendation to begin any of them.

## The company already models the post-qualification world (latent, not live)

`observed-with-evidence`, this pass, by import check at HEAD (non-test importers, excluding each module's
own file):

| module | models | non-test importers |
|---|---|---|
| `company/market/css_performance_register.py` | CSS 5WD compliance, ET rates, quarterly Ofgem submission | **none** |
| `company/market/shipper_code_register.py` | shipper code, LDZ authorisations, transportation agreements | **none** |
| `company/crm/supply_point_register.py` | supply points | **none** |

Each presupposes a qualification (B2, B3/B4) the company does not hold. Because none has a non-test
importer, **no published figure asserts the qualification** — the assumption is latent, not a live
falsehood, and this register is the right place for it to be visible rather than a defect to fix now.
This is the same population as the 2026-08-13 finding *"the gas industry-systems layer is eleven modules
and no callers"*; that finding measured the wiring, this row records **why** the wiring should stay absent
until B2/B3 are real.

## What this register deliberately does not do

Acting on any row above means **contacting a real organisation and spending real money** — reserved
classes 1 and 2 (`background/one_way_door.py`). The atom's `block_reason` writes that boundary in
explicitly: *"this atom's ceiling is the register, never the application."* Accordingly:

- No row carries an "apply", "start", "contact" or "submit" action, and no row has a target date.
- The register records **what would be required**, not what should be begun.
- Nothing here is a proposal to unblock the atom. Pull-forward is proposal-only per
  `DIRECTOR_RULING_FUTURE_COMMITMENT_SETS_2026-08-08` §3 and is not exercised.

## Open items — named, not dropped (R10)

1. **The atom's own `gain` is not met by this pass.** It reads *"go-live stops being a date and becomes a
   list of named qualifications **with owners**."* This register has the qualifications and **no owners,
   no costs and no lead times** — the three things that would make it a plan. That is the single largest
   gap between L1 and the atom's L2 target, and it is a genuine one: none of the three is derivable from
   the existing source.
2. **B7's qualification path is unnamed.** The source records the ECVN/ECVAA channel and its June-2027 API
   consultation ✓ but never its accession requirement. BSC party accession + an ECVNA is `inferred` here
   and must not be treated as found.
3. **B1 and B5 rest on ~ markers.** SEC/SMKI/CIO-UIT and sponsoring-bank/SUN/Bacstel-IP are advisor
   knowledge, flagged in the source itself as needing current verification. The SEC → SMKI → CIO/UIT
   *ordering* asserted above inherits that status.
4. **Whether REC accession subsumes the older MRA/DCUSA obligations is unknown** — not addressed by the
   source, not inferable from the repo.
5. **The 2026-08-05 verification date is the freshness ceiling on every ✓ row**, and the source's own note
   that *Project Trident* is mid-flight means B3's surfaces are the rows most likely to have moved. No
   row was re-verified this pass (no network in autonomous runs).

Items 1 and 2 are the specific next DISCOVER steps should this atom be reopened for research; item 1 is
the L2 blocker.

## Cross-references

- `docs/design/F5_LICENCE_READINESS_REGISTER.md` — **Part A**, the licence side of this one register.
- `docs/design/refs/ADVISOR_RESEARCH_COUNTERPARTY_APIS_EPOCH3_2026-08-05.md` — the sole external source
  consolidated here.
- `docs/design/EP10_UK_LINK_XOSERVE_DISCOVER_FRAME.md` — the B3/B4 adapter atom's own DISCOVER/FRAME.
- `docs/design/maturity_map.yaml` — `EP19_counterparty_qualification_paths`; `EP20_go_live_cutover_analysis`
  `depends_on` this atom.
- `company/market/css_performance_register.py`, `company/market/shipper_code_register.py`,
  `company/crm/supply_point_register.py` — the post-qualification modules counted above.
