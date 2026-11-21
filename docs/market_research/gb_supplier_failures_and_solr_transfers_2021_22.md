# The GB supplier failures of July 2021 to May 2022, dated, and where their customers went

**Knowledge:** suppliers-accounts-and-capital

*Delivery seat, 21 Nov 2026. This is the knowledge step (K8) for direction item
`world-plays-the-2021-22-supplier-failures-and-solr-customer-intake`, which comes from the customer-voice theme map
(`customer_voice_theme_map_gb_energy_2026-11-21.md` §3, row "Supplier failure and SoLR 2021–22"). The world held
only the mutualisation levy (`simulation/policy_costs.py`). It had no failing rival and no customers moved by a
Supplier of Last Resort (SoLR) appointment. This page records what happened before the world is made to replay it.
Companion page: `why_gb_suppliers_failed_or_survived_2021_22.md` covers why the suppliers failed. This page covers
when they failed, how many customers each had, and which supplier took them.*

## Sources, and how far each can be trusted

| Id | Source | What it gives | Grade |
|---|---|---|---|
| NAO | National Audit Office, *The energy supplier market*, HC 68, 22 Jun 2022 (PDF fetched 21 Nov 2026, text extracted locally): §1.13 with its note 3, Figure 4 and Figure 5 | totals; customers each of the ten SoLRs received; domestic and non-domestic split of the total | primary (auditor, from Ofgem data) |
| OX | Oxera for Ofgem, *Review of Ofgem's regulation of the energy supply market*, May 2022, Table 3.1 (PDF on ofgem.gov.uk, text extracted locally) | **month** of failure for the 26 failures from September 2021 onwards | primary for the month (Ofgem's own commissioned review; it dates failures from Forbes, 18 Feb 2022) |
| USE | utilitysavingexpert.com/failed-energy-companies (fetched 21 Nov 2026) | customers per failed supplier and the SoLR appointed. It gives the year only, no date | **secondary.** It says its counts are "Ofgem's approximate totals at the point each supplier stopped trading". It is used here **only because it reconciles with NAO Figure 5** (below) |

Ofgem's own pages could not be read: the SoLR listing returned 403, the "gone bust" page 404, and the web archive is
blocked from this machine. The Citizens Advice *Market Meltdown* PDF returned 404.

## The totals the record states (NAO)

- "during the period between July 2021 and May 2022, **29 energy suppliers failed**, affecting nearly four million
  households" (NAO landing page and summary).
- "Since July 2021, Ofgem has transferred **nearly 2.4 million customers of 28 failed energy suppliers** to alternative
  providers through its SOLR process" (§1.13). Bulb, with "approximately 1.6 million customers", went into special
  administration (SAR) instead, on 24 November 2021.
- NAO §1.13 note 3: of the 28, "15 supplied solely domestic customers; three supplied solely non-domestic customers; and 10
  either supplied a mixture of both or the split was not specified. This represented **2.0 million domestic customers;
  59,000 non-domestic customers; and 318,000 customers where the type of customer was not specified**."
- NAO Figure 5, customers received by each of the ten SoLRs (all customer types, rounded to 1,000): British Gas 680,000;
  Octopus 580,000; Shell Energy Retail 536,000; E.ON Next 248,000; EDF 232,000; Scottish Power 70,000; Pozitive 41,000;
  Utilita 6,000; Yü 3,000; SmartestEnergy 300.

## The dated list

Month of failure from OX, except where marked. Customers and SoLR from USE. Business-only firms are marked **B**. Every
other firm's domestic count is **not published per firm** (GAP). Only the total, 2.0m domestic plus 318k unspecified, is
known.

| Month | Failed supplier | Customers (all types) | SoLR |
|---|---|---|---|
| Jul–Aug 2021 (GAP: month) | Hub Energy | 15,000 | E.ON Next |
| Sep 2021 | PFP Energy | 82,000 | British Gas |
| Sep 2021 | MoneyPlus Energy | 9,000 | British Gas |
| Sep 2021 | People's Energy | 350,000 | British Gas |
| Sep 2021 | Utility Point | 220,000 | EDF |
| Sep 2021 | Avro Energy | 580,000 | Octopus Energy |
| Sep 2021 | Green Supplier | 255,000 | Shell Energy |
| Sep 2021 | ENSTROGA | 6,000 | E.ON Next |
| Sep 2021 | Igloo Energy | 179,000 | E.ON Next |
| Sep 2021 | Symbio Energy | 48,000 | E.ON Next |
| Oct 2021 | Pure Planet | 235,000 | Shell Energy |
| Oct 2021 | Colorado Energy | 15,000 | Shell Energy |
| Oct 2021 | Daligas | 9,000 | Shell Energy |
| Oct 2021 | GOTO Energy | 22,000 | Shell Energy |
| Nov 2021 | Bluegreen Energy Services | 5,900 | British Gas |
| Nov 2021 | Omni Energy | 6,000 | Utilita |
| Nov 2021 | MA Energy (**B**) | 300 | SmartestEnergy |
| Nov 2021 | Zebra Power | 14,800 | British Gas |
| Nov 2021 | AmpowerUK | 2,600 | Yü Energy |
| Nov 2021 | CNG Energy (**B**) | 41,000 | Pozitive Energy |
| Nov 2021 | Neon Reef | 30,000 | British Gas |
| Nov 2021 | Social Energy Supply | 5,500 | British Gas |
| Nov 2021 | Orbit Energy | 65,000 | Scottish Power |
| Nov 2021 | Entice Energy | 5,400 | Scottish Power |
| Dec 2021 | Zog Energy | 11,700 | EDF |
| Jan 2022 | Together Energy | 176,600 | British Gas |
| Feb 2022 (USE search snippet, 18 Feb; not OX) | Whoop Energy (50 domestic, 212 business) | 262 | Yü Energy |
| Feb 2022 (as Whoop; not OX) | Xcel Power (**B**) | 270 | Yü Energy |
| Nov 2021 (OX; SAR 24 Nov per NAO) | **Bulb Energy**: special administration, not SoLR | c. 1.6m (NAO) | none in the window |

### Why the secondary counts are trusted: they reconcile with NAO Figure 5, SoLR by SoLR

| SoLR | Sum of USE rows above | NAO Figure 5 |
|---|---|---|
| British Gas | 673,800 | 680,000 |
| Octopus | 580,000 | 580,000 |
| Shell | 536,000 | 536,000 |
| E.ON Next | 248,000 (with Hub) | 248,000 |
| EDF | 231,700 | 232,000 |
| Scottish Power | 70,400 | 70,000 |
| Pozitive | 41,000 | 41,000 |
| Utilita | 6,000 | 6,000 |
| Yü | 3,132 | 3,000 |
| SmartestEnergy | 300 | 300 |
| **Total, 28 firms** | **2,390,332** | "nearly 2.4 million", 28 firms |

The reconciliation also settles the window's membership. **Hub Energy falls inside July 2021 to May 2022**: E.ON Next
reaches 248,000 only with Hub, and Hub is absent from OX's table of failures "since September 2021", so it failed in July
or August 2021. **Green Network Energy and Simplicity** (EDF and British Gas, early 2021) fall **outside** it: adding them
breaks the EDF and British Gas totals. **UK Energy Incubator Hub (Neo, to Octopus, 2022)** also falls outside: adding its
3,000 breaks Octopus's 580,000. Three business-only firms (MA, CNG, Xcel) match NAO's "three supplied solely non-domestic".

## What happened to a customer who was moved (NAO Figure 6 and §2.4–2.5)

- **The tariff.** The customer arrives on the SoLR's **default tariff**, which sits under the price cap. "When customers
  are moved from a failed supplier to a SOLR they are likely to experience an increase in their energy bills if moving
  from a non-default to a default tariff. Citizens Advice has estimated the average price rise to be **£30 per customer
  per month** for the remainder of the duration of their original contract." Ofgem treats this as "within the rules".
- **Credit balances are protected** but delayed. Customers "experienced delays in receiving their final bills, and in
  the transfer of credit refunds", chiefly "because of delays in receiving data from the failed supplier or
  administrator".
- **Debt repayment plans** can be cancelled. "There is no obligation for the SOLR to honour a repayment plan but the SOLR
  does have to take account of the customer's ability to pay."
- **Direct debits.** In May 2022 the Secretary of State announced compliance action "against suppliers who increased
  direct debits beyond what was required" (account C2's "promised DD not taken but taken").
- **The opening read (C2's estimate after a transfer).** The SoLR starts supply with no read history from the failed
  supplier ("delays in receiving data"). Its opening register is therefore deemed unless the customer supplies a read.
  **GAP:** the share of moved customers who supplied an opening read is not published in any source read. The world
  carries it as `None`, and the C2 path takes the gaining supplier's first actual read from the meter's ordinary read
  cycle (`simulation/meter_reads.gaining_supplier_first_read`, which already cites SLC 21B.4 and BSCP504 s.4.5.2).

## What this means for the world, and what it does not

1. **These are dated events, not a scenario** (CLAUDE.md, *Historical ground truth*). A household in the world that was
   not the company's customer could have been with one of these firms. The chance that a given GB domestic account was
   moved by SoLR in a month is that month's moved customers over the published account count
   (`gb_domestic_switching_rate.json`, `accounts_millions`, DESNZ QEP 2.7.1). Two mismatches are declared, not fixed: the
   numerator counts customers of all types and both fuels, while the denominator counts domestic electricity accounts.
   The domestic share of the total is bounded, not known: from 2.0m/2.39m (domestic only) to 2.318m/2.39m (domestic plus
   unspecified).
2. **None of the ten SoLRs is the company.** The company is synthetic. Whether it could have bid for and won a SoLR
   appointment is a **supplier capability** (Ofgem's SoLR guidance, bid and appointment criteria: **unread**). It is not a
   world fact, and it is handed on separately.
3. **Bulb is not a SoLR transfer.** Its 1.6m customers stayed with Bulb under SAR through the window, so it moves nobody
   here.
4. **Does a SoLR transfer count as a switch in the DESNZ series?** **GAP: not established.** If it does, the 2021 and
   2022 switching rates already contain these 2.4m moves, and the world must not add them to switching again. The module
   built from this page does not touch the switching rate.

## Gaps

- The day of each failure and of each SoLR appointment (Ofgem's decision pages could not be fetched; the month is OX's).
- Hub Energy's month (July or August 2021).
- Domestic customers per firm. Fuel split per firm.
- The share of moved customers who supplied an opening read; how long the first bill after a transfer took.
- Whether DESNZ QEP 2.7.1 counts SoLR transfers as electricity transfers.
- Ofgem's SoLR appointment criteria (the supplier-side question).
