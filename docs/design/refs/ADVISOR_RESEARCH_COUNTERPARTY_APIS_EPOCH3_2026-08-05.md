# [ADVISOR-RESEARCH] — Real counterparty surfaces for the Epoch-3 adapter set (2026-08-05)

**Type:** [RESEARCH — empowerment, not instruction]. What actually exists on the other side of the wall, per counterparty: access class, concrete surface, and what it implies for each adapter. Sources: live web verification 2026-08-05 (marked ✓) and advisor knowledge (marked ~, verify before build). CC decides all mechanisms. The strategic payoff is in §The build order.

## Electricity settlement & market data — Elexon (OPEN NOW)
✓ The Insights Solution (`bmrs.elexon.co.uk`) is the single platform: ALL BMRS datasets via website, REST API, IRIS (real-time push service), and a Data Archive. Interactive API docs on each dataset page; developer docs maintained on GitHub (`elexon-data/insights-docs`). Indicative settlement prices land ~15 minutes after each settlement period with a D+1 refresh; "Settlement messages" give early warnings on calculation accuracy. The SIM already consumes SSP — the full catalogue (imbalance volumes, pricing stacks, dynamic BMU data, demand) is the same open door.
✓ Current awareness: ECVN submission (trading notifications to ECVAA) is consulting on an API route with planned launch June 2027 — until then trading submission is legacy channels. REMIT inside-information gains direct API submission to Insights from Nov 2026. The trading adapter should be shaped as swappable transport.

## Carbon — NESO (OPEN NOW)
~ Carbon Intensity API (`carbonintensity.org.uk`): free, no key, national + regional actual/forecast gCO2/kWh. The carbon lane's 10KB can grow against a real feed from day one; regional intensity × half-hourly usage is the abatement ledger's ground truth.

## Smart metering — DCC (GATED) with a real proxy route (SANDBOX NOW)
~ Direct DCC access requires SEC accession, SMKI certification, and CIO/UIT testing; service requests are DUIS SRVs (e.g. read billing registers). No public sandbox. This adapter stays mocked until accession — model it AS DUIS service-request/response shapes so the swap is transport-only.
✓ The proven pre-accession route: **DCC Other Users** (n3rgy, Hildebrand/Glow) operate registered adapters and expose consumer-consented APIs. n3rgy runs live AND sandbox services (auth by IHD MAC/CIN, registration by MPAN/MPRN). Fidelity gold verified: the supplier pull is once daily per meter, returning a midnight index read plus a half-hourly usage file — the real cadence and failure surface (missing days stay missing unless re-requested) the SIM should reproduce.

## Switching — CSS under the REC (GATED)
✓ Switching-adjacent APIs are administered through RECCo (Retail Energy Code Company) under the REC Data Access Matrix — eligibility confirmed by the REC Code Manager before access. Gas-side confirmation: Supply Point Switching API access runs through RECCo. Electricity-side CSS (operated by DCC) follows the same REC qualification pattern. Adapter stays mocked; shape it to REC message flows.

## Gas — Xoserve/CDSP (GATED, with named APIs)
✓ UK Link is the CDSP system suite under the UNC; access via the Data Services Contract / UK Link User Agreement. REAL named APIs exist: Supply Point Switching, Supply Point Enquiry, Meter Asset Enquiry (via RECCo), Supply Point Quantities (Shippers only, via Xoserve). The Gas Enquiry Service portal sits in the Xoserve Services Portal; the UK Link DPM is the register of which user types may access which data items. Fidelity nuggets verified: meter read classes 1–4 (daily to annual cadences); UIG — unidentified gas per LDZ per gas day — is a real reconciliation residue the SIM's gas plumbing should be able to produce; Project Trident is mid-flight modernisation, so expect surface churn.

## Payments — Bacs (GATED direct, SANDBOX NOW via bureau)
~ Direct Bacs: Service User Number via a sponsoring bank + Bacstel-IP submission — heavy, post-go-live only. The report set that IS the unhappy-path spec: ADDACS (mandate amendments/cancellations), ARUDD (returned unpaids with reason codes), AUDDIS (instruction lodgement failures), AWACS (account switches) — each report a generator of SIM events.
✓ Bureau route usable TODAY: GoCardless — full free sandbox (`manage-sandbox.gocardless.com`), mandate + payment lifecycle via Billing Requests, webhook events for confirmations, failures, cancellations; UK collection confirms ~4–5 working days after charge creation (the 3-day Bacs cycle plus processing) — the real timing physics for the meter-to-cash chain. The DD adapter can run against this sandbox end-to-end before any bank relationship exists.

## Regulatory & cost stack — Ofgem, networks (OPEN, spreadsheet-shaped)
~ Price cap: Ofgem publishes cap levels and the full annex model as spreadsheets each period — the tariff engine's external anchor. Network charges are published, not API'd: DNO DUoS via CDCM tariff spreadsheets, TNUoS via NESO publications, BSUoS reformed under NESO. These feed the non-commodity cost stack (the £4.9M reconciliation-gap territory) — adapters here are file-ingest parsers with schema-drift tolerance, not REST clients.

## The build order (the point of all this)
Three tiers fall out by access class, and they order Epoch-3:
1. **Integrate now, real data:** Elexon Insights + IRIS, Carbon Intensity, Ofgem/network published files. Zero accession cost.
2. **Integrate now, real sandbox:** GoCardless (payments), n3rgy sandbox (metering shapes). The wall's most failure-rich adapters — money and meters — can be exercised against real external systems long before go-live.
3. **Mock until accession:** DCC DUIS, CSS/REC flows, UK Link. Shape mocks AS the real message formats so go-live is transport swap, not redesign — the wall doctrine made concrete.
Every gated counterparty above also names its qualification path (SEC, REC/RECCo, DSC/UUA, sponsor bank), which is the Epoch-5 checklist writing itself.

— Advisor research, 2026-08-05. ✓ = verified by live search this date; ~ = advisor knowledge, verify current before build.
