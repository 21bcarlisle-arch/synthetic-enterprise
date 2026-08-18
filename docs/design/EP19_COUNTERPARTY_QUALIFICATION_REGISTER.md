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

> **Superseded 2026-08-18.** Both sentences above were wrong about this machine. Autonomous runs **do**
> have network; what they have instead is an **egress allowlist** that admits `elexon.co.uk` and none of
> the other hosts here (§ Why only one row is priced). Rows verified live on that date are marked
> **✓2026-08-18** and carry that freshness; every other ✓ still carries 2026-08-05. The paragraph is left
> standing rather than rewritten because it is the claim the correction is about.

## Register — Part B

| # | Counterparty / system | What it gates | Named qualification path | Access class | Pre-qualification route | Company-side status |
|---|---|---|---|---|---|---|
| B1 | **DCC** (Data Communications Company) — smart metering | DUIS service requests (e.g. read billing registers) against smart meters | **SEC accession** (party to the Smart Energy Code) → **SMKI** certification (Smart Metering Key Infrastructure) → **CIO/UIT** testing ~ | **GATED** ~ | **Yes** — *DCC Other Users* (n3rgy, Hildebrand/Glow) operate registered adapters and expose consumer-consented APIs; n3rgy runs live **and** sandbox services, auth by IHD MAC/CIN, registration by MPAN/MPRN ✓ | No DCC adapter and no accession. Nothing published depends on one. |
| B2 | **CSS / REC** — switching (electricity CSS operated by DCC; gas Supply Point Switching) | Switching-adjacent APIs, administered through **RECCo** under the **REC Data Access Matrix** | **REC eligibility confirmed by the REC Code Manager** before access ✓ | **GATED** ✓ | **None named** — the advisor's sweep found no sandbox or proxy route for REC-administered APIs | `company/market/css_performance_register.py` already models CSS 5WD/ET KPI reporting — i.e. it models the **post-qualification** world. Zero non-test importers (verified this pass), so no published figure rests on the unheld qualification. |
| B3 | **Xoserve / CDSP** — UK Link (gas) | Supply Point Switching, Supply Point Enquiry, Meter Asset Enquiry (via RECCo), Supply Point Quantities | **Data Services Contract (DSC) / UK Link User Agreement**; entitlement per user type set by the **UK Link DPM** (the register of which user types may access which data items) ✓ | **GATED** ✓ | **None named**. Note *Project Trident* is mid-flight modernisation — expect surface churn ✓ | `company/market/shipper_code_register.py` models shipper codes + LDZ authorisations; `company/crm/supply_point_register.py` likewise. Zero non-test importers each (verified this pass). See `EP10_adapter_uk_link_xoserve`. |
| B4 | **Xoserve — Shippers-only surface** (subset of B3) | **Supply Point Quantities**, restricted to Shippers ✓ | B3's DSC/UUA **plus** shipper status: UNC accession + transportation agreements + per-LDZ authorisation **inf** (from `shipper_code_register.py`'s own docstring, not from the advisor source) | **GATED** ✓ | None | Same as B3. The shipper prerequisite is a **repo-side inference** and is one of the open items below. |
| B5 | **Bacs** — direct submission | Direct Debit collection submitted by the company itself; the ADDACS / ARUDD / AUDDIS / AWACS report set | **Sponsoring bank** → **Service User Number (SUN)** → **Bacstel-IP** submission ~ | **GATED** ~ | **Yes** — bureau route: GoCardless full free sandbox (mandate + payment lifecycle, webhooks); the DD adapter can run end-to-end **before any bank relationship exists** ✓ | No bank relationship; none required. Reserved-class boundary: a sponsoring bank is a real organisation and real money (classes 1 and 2). |
| B6 | **Elexon** — settlement & market data (Insights, IRIS, Data Archive) | Nothing. All BMRS datasets are open via website, REST API, IRIS push and archive ✓ | — | **OPEN** ✓ | n/a | Already consumed (SSP). |
| B7 | **Elexon** — *trading* notification (ECVN → ECVAA) | Submission of energy contract volume notifications | **CVA Qualification** (BSCP70 testing). **An ECVNA is *not* a BSC Party** and *"you will not need to join the BSC"* ✓2026-08-18. Testing may be **waived** against an existing Qualified system with a signed letter from its owner; it cannot be opted out of ✓2026-08-18. Entry is expression-of-interest → meeting → Elexon Kinnect ✓2026-08-18. The advisor's June-2027 API-launch consultation note still stands ✓2026-08-05 | **GATED** ✓ | **Yes — appoint someone else's ECVNA.** *"BSC Parties must appoint an ECVNA to submit the ECVN on behalf of them and their counterparties… many Trading Parties are ECVNAs in their own right"* ✓2026-08-18. Not a sandbox: appointing one is contracting with a real organisation (class 2). It removes a **qualification**, not the counterparty | No trading submission path. **Cost: £0** — *"There are no costs as a ECVNAs are not a BSC Party"* ✓2026-08-18 |
| **B11** | **Elexon — the BSC itself** (accession as a Party) *(row added 2026-08-18)* | Being a Trading Party at all: energy imbalance exposure, Trading Charges, the right to appoint/act as an ECVNA | **BSC accession**, plus **CVA Qualification + SVA Qualification** for a Supplier. Enduring MHHS SVA process from **1 Apr 2026**: Pre-Qualification Survey → Qualification Readiness Assessment (replaces SAD/QAD) + Qualification Test Framework; **Placing Reliance** allows re-use of another party's test evidence ✓2026-08-18 | **GATED** ✓ | None named | No accession. **See § Priced, for the only path in this register with published costs.** This row did not exist before 2026-08-18 — see § The hole this register had. |
| B8 | **NESO** — Carbon Intensity API | Nothing; free, no key ✓ | — | **OPEN** ✓ | n/a | Available to the carbon lane today. |
| B9 | **Ofgem / DNOs / NESO** — published cost-stack files (price cap annex model, CDCM DUoS, TNUoS, BSUoS) | Nothing; published as spreadsheets, not API'd ~ | — | **OPEN** ~ | n/a | File-ingest parsers with schema-drift tolerance, not REST clients. |
| B10 | **Ofgem** — the supply licence itself | Holding a supply licence at all | **Part A** — `F5_LICENCE_READINESS_REGISTER.md`. Not restated here. | **GATED** | n/a | See Part A. |

## Owner, per row — derived, not assigned (added 2026-08-15)

The atom's `gain` asks for *"named qualifications **with owners**"*. The owner was never an external
fact to be researched: in this company exactly two parties can perform anything, and which one owns an
act is decided by the reserved-class enumeration in `background/one_way_door.py` (CLAUDE.md: the **SOLE**
enumeration). Each row's owner below is the verdict of running `classify_action` on that row's act —
`observed-with-evidence`, 2026-08-15, re-runnable.

| row | the act | verdict | **owner** |
|---|---|---|---|
| B1 | SEC accession + fee | `real_money` | **Director** — reserved class 1 |
| B1 | SMKI certificates, CIO/UIT testing | `real_world_commitment` | **Director** — reserved class 2 |
| B2 | Ask the REC Code Manager to confirm eligibility | `real_world_commitment` | **Director** — reserved class 2 |
| B3 | Sign the DSC / UK Link User Agreement | `real_world_commitment` | **Director** — reserved class 2 |
| B4 | Accede to the UNC as a shipper | `real_world_commitment` | **Director** — reserved class 2 |
| B5 | Sponsoring bank + Bacs SUN | `real_world_commitment` | **Director** — reserved classes 1 and 2 |
| B7 | Accede to the BSC, appoint an ECVN agent | `real_world_commitment` | **Director** — reserved class 2 |
| B6, B8, B9 | Fetch/download published open data | `PROCEED` | **The company lane that consumes it** (settlement, carbon, cost-stack) |
| B10 | See Part A | — | Part A |
| **B11** | Accede to the BSC and pay the £500 accession fee | `real_money` | **Director** — reserved class 1 |
| **B11** | Complete CVA Qualification testing with Elexon under BSCP70 | **`PROCEED`** ⚠ | **Director** — reserved class 2. **The classifier is wrong here; see below.** |
| **B7** | Appoint an existing ECVNA to submit ECVNs on the company's behalf | **`PROCEED`** ⚠ | **Director** — reserved class 2. **The classifier is wrong here; see below.** |

**⚠ The derivation rule is disclaimed for the two rows above, and the disclaimer is the finding.** Re-run
2026-08-18, the two acts this pass newly discovered both come back `PROCEED` — yet each means engaging a
real organisation (Elexon; a third-party agent), which is reserved class 2 on CLAUDE.md's plain reading.
The 2026-08-15 repair required *an acting verb beside a named real body*, and neither "complete testing
with Elexon" nor "appoint an ECVNA" has that shape. So this is a **third** instance of the same fail-open,
found the same way the second was — by insisting the column stay re-runnable instead of assigned.

The owners above are therefore **read off CLAUDE.md, not off the classifier**, for these two rows only.
That is a deliberate break in the derivation: a column that quietly wrote *"the company lane owns
appointing an ECVNA"* because a control said `PROCEED` would be this register laundering a defect into a
permission — the exact failure the 2026-08-15 correction exists to prevent. Queued, not fixed, at
`docs/staging/WORKER_FINDING_THE_DOOR_RELEASES_THE_ONE_CONTROL_CLAUDE_MD_CALLS_A_WALL_2026-08-18.md`.
**Until that lands, this column is a mixed instrument** — nine rows derived, two asserted — and it must
not be described as exhaustive-by-construction without that caveat.

*(Qualified 2026-08-18 by the ⚠ note above: two of eleven rows are now asserted from CLAUDE.md rather than
derived, because the classifier fails open on them. The two claims below hold for the derived nine.)*

Two things this column is, that an assigned column would not be. It is **exhaustive by construction** —
every row gets a verdict because the classifier answers for any act — and it is **falsifiable**: the
derivation only says anything true because the wall it reads was repaired this same pass. Run against the
pre-2026-08-15 classifier, all seven gated rows would have come back agent-owned, which is exactly the
defect `EP19_QUALIFICATION_ACTS_AND_THE_WALL_DISCOVER.md` records and
`tests/background/test_one_way_door.py` now pins in both directions.

What this column deliberately does **not** contain is an internal name or team. There is no org chart
here to draw one from, and inventing one would be the fabrication this register exists to avoid.

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
| B7 ECVN/ECVAA | ~~**No route named**, and no path named either~~ → **corrected 2026-08-18: both are named.** The path is CVA Qualification (no BSC accession, £0), and the route around it is to **appoint an existing ECVNA** rather than become one |
| B11 BSC accession | **No route named** |

The two adapters the advisor calls *"the wall's most failure-rich — money and meters"* are precisely the
two with real pre-qualification routes.

**Corrected 2026-08-18.** The first cut of this section concluded: *"The critical path to go-live is
therefore REC/RECCo, DSC/UUA and the trading channel — the three that can only ever be mocked until a real
qualification completes."* **The trading channel does not belong in that list.** A BSC Party may appoint
somebody else's ECVNA, so B7 is not a qualification this company must hold at all; what it must hold is
B11, which the register did not have a row for when that sentence was written. The corrected critical path
is **REC/RECCo, DSC/UUA and BSC accession**. Appointing an ECVNA is still a real contract with a real
organisation (reserved class 2) — the correction is about which *qualifications* are on the company's own
checklist, not about what may be done. It remains a sequencing statement, **not** a recommendation to begin
any of them.

## Priced — the one path with published costs (added 2026-08-18)

`observed-with-evidence`, live fetch 2026-08-18 from `www.elexon.co.uk` (the **only** host in this register
on `background/egress_allowlist.py`; see § Why only one row is priced):
`/bsc/market-entry/becoming-supplier/`, `/bsc/market-entry/becoming-an-energy-contract-volume-notification-agent/`,
`/bsc/market-entry/sva-qualification/`.

| row | item | published figure |
|---|---|---|
| B11 | BSC **accession fee** | **£500** (*"covers the administrative costs of entering the market"*) |
| B11 | **Base monthly charge** | **£250 + VAT**, flat |
| B11 | CVA Metering charge | £50 per Registered CVA Metering System / month |
| B11 | **SVA Metering System Charge** | **£0.00757** per SVA Metering System / month — *scales with the customer book* |
| B11 | CVA BM Unit Charge | £0 (was £50) |
| B11 | Base BM Unit Charge | £0 (was £100) |
| B11 | Additional BM Unit Charge | £60 |
| B11 | Notified Volume Charge | £0.0005/MWh of Gross Contract Volume |
| B11 | Participant Test Service | £999 + VAT per half-day test slot |
| B11 | SVA Qualification | **£0** — *"costs are recovered centrally through Elexon's funding mechanisms"* |
| B11 | Credit Cover | **Elexon does not specify it** — *"it is up to the Party to decide"*, from its own trading characteristics |
| B7 | ECVNA status | **£0** — *"There are no costs as a ECVNAs are not a BSC Party"* |

**Lead times are not published on any of these pages** — the enduring process names its *stages*
(PQS → QRA + QTF) and no calendar duration, service level or typical elapsed time. Nothing is inferred
into a lead-time column here; a guessed elapsed time is exactly the corruption this register exists to
prevent. **Costs: 1 of 5 gated paths closed. Lead times: 0 of 5.**

These are **published prices, not budget lines.** No row carries a decision to pay one.

## The hole this register had (added 2026-08-18)

Before this date, **neither part of the one register carried the BSC accession** — the qualification every
GB electricity supplier must hold. Part A (`F5_LICENCE_READINESS_REGISTER.md`) contains no occurrence of
"BSC", "Elexon" or "accession", checked 2026-08-18. Part B named Elexon twice, at B6 and B7, and both rows
classified it by its **data surfaces** (open settlement data; the trading-notification channel).

The register's own framing claims *"Access class partitions **every** counterparty the wall faces"*. The
hole was at the counterparty this project reads from more than any other, and it opened because every row
was written to answer **"what does this counterparty serve us?"** and none asked **"what must we be, to
it?"**. A counterparty can be OPEN as a data publisher and GATED as a club in the same breath — B6 and B11
are the same organisation. Any future row should be checked against both questions before its access class
is set.

## Why only one row is priced (added 2026-08-18)

Not for want of a networked pass. `background/egress_allowlist.py` admits `elexon.co.uk` and `neso.energy`
and **none** of `smartenergycodecompany.co.uk`, `smartdcc.co.uk`, `recportal.co.uk`, `xoserve.com`,
`bacs.co.uk`, `gocardless.com` or `ofgem.gov.uk` — and CLAUDE.md makes the allowlist director-console-only:
*"the agent may never widen its own."* So B1, B2, B3/B4, B5 and Part A's B10 are **unreachable by any
autonomous tick**, at any hour, on any runner — a wall, not a scheduling gap. Full working:
`EP19_THE_ALLOWLIST_IS_THE_CONSTRAINT_AND_ELEXON_IS_INSIDE_IT_DISCOVER.md`.

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

**Correction, 2026-08-15.** The first cut of this section said the reserved boundary was *"HELD, not just
cited"*. That was true of this **document** — no row carries an action, by construction, and still does
not — but it was **false of the mechanism the atom points at**. Every one of the seven gated acts above
classified as PROCEED in `background/one_way_door.py` until this date, while the *sentence* describing the
boundary (`block_reason`, containing "spending real money") classified as a door: the wall fired on the
prose and not on the population. It is now mechanised and R15-proven in both directions —
`EP19_QUALIFICATION_ACTS_AND_THE_WALL_DISCOVER.md`.

## Open items — named, not dropped (R10)

1. **The atom's own `gain` is not met by this pass.** It reads *"go-live stops being a date and becomes a
   list of named qualifications **with owners**."* This register has the qualifications and **no owners,
   no costs and no lead times** — the three things that would make it a plan. That is the single largest
   gap between L1 and the atom's L2 target, and it is a genuine one: none of the three is derivable from
   the existing source.
   **UPDATED 2026-08-15 — one third closed, and the search was in the wrong place.** *Owners* are now
   derived per row (see the section above): they were never an external fact, so no source could have
   held them; they follow from the reserved-class enumeration, and deriving them is what exposed the
   fail-open wall that this atom's `block_reason` had been relying on. **Costs and lead times remain
   open and are now the entire L2 gap.** Both are live external facts and autonomous runs have no
   network, so neither was inferred — the next step is one *networked* DISCOVER pass to price the five
   gated paths and record their published lead times. The level therefore stays at 1
   (`EP19_QUALIFICATION_ACTS_AND_THE_WALL_DISCOVER.md` § The level).
   **UPDATED 2026-08-18 — the stated reason was wrong, and the next step it named could never happen.**
   *"Autonomous runs have no network"* is false: this tick reached the internet from the worker seat on
   the first try, and neither prior pass had tested the premise it published. The real constraint is the
   **egress allowlist**, which the agent may never widen (CLAUDE.md, director-console-only) — so a
   "networked DISCOVER pass" is not a step any tick can take for B1, B2, B3/B4, B5 or B10. Costs are now
   closed for **1 of 5** gated paths (B7/B11, the one host on the allowlist) and lead times for **0 of 5**;
   Elexon publishes its process and not its durations. The corrected next step, and the recommendation
   between the two routes that exist, are in
   `EP19_THE_ALLOWLIST_IS_THE_CONSTRAINT_AND_ELEXON_IS_INSIDE_IT_DISCOVER.md` § 6. Level still 1.
2. ~~**B7's qualification path is unnamed.**~~ **CLOSED 2026-08-18**, and the inference it warned against
   was half wrong. The path is **CVA Qualification**, published by Elexon; **BSC accession is not part of
   it** (*"Unlike other BSC Parties you will not need to join the BSC"*), the cost is **£0**, and the
   company may **appoint** an existing ECVNA instead of becoming one. What the inference got right was
   that a qualification exists; what it got wrong was attaching BSC accession to the wrong row — the
   accession is real but belongs to **B11**, which this register had no row for at all until the same
   pass. One residue, not inferred either way: whether an ECVN submitted by an appointed third-party
   ECVNA carries the same obligations for the appointing Party as one it submits itself is not addressed
   by Elexon's market-entry pages.
3. **B1 and B5 rest on ~ markers.** SEC/SMKI/CIO-UIT and sponsoring-bank/SUN/Bacstel-IP are advisor
   knowledge, flagged in the source itself as needing current verification. The SEC → SMKI → CIO/UIT
   *ordering* asserted above inherits that status.
4. **Whether REC accession subsumes the older MRA/DCUSA obligations is unknown** — not addressed by the
   source, not inferable from the repo.
5. **The 2026-08-05 verification date is the freshness ceiling on every ✓ row**, and the source's own note
   that *Project Trident* is mid-flight means B3's surfaces are the rows most likely to have moved. No
   row was re-verified this pass (no network in autonomous runs).
   **UPDATED 2026-08-18:** B7 was re-verified live and now carries ✓2026-08-18, as does the new B11. Every
   remaining ✓ row still stands at 2026-08-05 — not for want of network but because its host is off the
   allowlist, so B3/Project Trident, the row most likely to have moved, is also among the rows that cannot
   be re-checked from this seat.

Items 1 and 2 are the specific next DISCOVER steps should this atom be reopened for research; item 1 is
the L2 blocker.

## Cross-references

- `docs/design/F5_LICENCE_READINESS_REGISTER.md` — **Part A**, the licence side of this one register.
- `docs/design/refs/ADVISOR_RESEARCH_COUNTERPARTY_APIS_EPOCH3_2026-08-05.md` — the sole external source
  consolidated here.
- `docs/design/EP19_QUALIFICATION_ACTS_AND_THE_WALL_DISCOVER.md` — the 2026-08-15 pass: the seven
  qualification acts read PROCEED at the wall this register's boundary cites, the repair, and the
  derivation of the Owner column.
- `background/one_way_door.py` / `tests/background/test_one_way_door.py` — the wall itself and the
  three tests that pin these acts in both directions.
- `docs/design/EP10_UK_LINK_XOSERVE_DISCOVER_FRAME.md` — the B3/B4 adapter atom's own DISCOVER/FRAME.
- `docs/design/maturity_map.yaml` — `EP19_counterparty_qualification_paths`; `EP20_go_live_cutover_analysis`
  `depends_on` this atom.
- `company/market/css_performance_register.py`, `company/market/shipper_code_register.py`,
  `company/crm/supply_point_register.py` — the post-qualification modules counted above.
