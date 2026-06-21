# UK Energy Supplier Customer Communications and Renewal Lifecycle — Research Findings

Sources: Ofgem SLC 22A/22B, Ofgem Consumer Standards Dec 2023, Energy UK, Citizens Advice, KPMG CLV

## 1. Renewal Cycle: Regulatory Notice Requirements

| Trigger | Required notice window | Mandatory content |
|---------|----------------------|-------------------|
| End of domestic fixed-term | **42–49 days before end** (SLC 22A) | End date, roll-over tariff, exit fee status |
| End of micro-business fixed-term | **60–120 days before end** | Renewal rates, switching rights |
| Tariff change on variable rate | **30 days** (SLC 22B) | New unit rate, standing charge |
| Missed payment (monthly DD) | Contact after **2nd consecutive miss** | Support offer, repayment plan options |
| Missed payment (quarterly) | Contact after **1st miss** | Same |
| New customer welcome pack | Within **5 working days** of supply start (SLC 23) | Principal terms, cooling-off rights |
| Annual statement | Once per year (SLC 31B) | Usage, tariff, estimated cost, cheaper deals prompt |
| Exit fee | **Banned** in 42–49 day notice window | N/A — customer can switch cost-free |
| Auto-rollover to new fixed | **Banned** for domestic customers | Must default to evergreen/SVT (cheapest evergreen, not any SVT) |

**Typical supplier practice (beyond legal minimum):**
- "Soft" engagement letter at 90 days (not mandatory, but common)
- Formal statutory notice at 42–49 days
- Follow-up at 30 days if no response

## 2. Renewal Offer Mechanics

**Pricing framework:** Price cap eliminated most of the pre-cap "loyalty penalty" (gap once >£300/year). As of 2025-26:
- Exit fees (~£50/fuel) on new acquisition tariffs; no exit fees on renewal/"Loyal Octopus" style tariffs
- Gap between best new-customer rate and renewal rate is much narrower than pre-cap

**Personalisation:** Not typically individual-level. Dominant practice: segment-level differentiation:
- High-usage/high-value customers: may receive a phone call or sharper rate
- Low-usage customers: standard letter
- Smart meter data beginning to enable ToU recommendations at renewal (emerging)
- KPMG CLV analysis: top-quintile customers generate disproportionate margin → worth differentiated retention spend

**Roll-over default:** Customer who takes no action → supplier's cheapest evergreen tariff (SVT/default). Supplier sends a post-contract-end notice confirming new rate.

## 3. Churn Prevention Triggers (Beyond Scheduled Renewal)

| Trigger | What supplier does |
|---------|-------------------|
| Bill shock event (usage spike, large bill) | Proactive outreach; smart meter data enables pre-billing alert |
| Inbound complaint or billing query | Treat as churn signal; resolution + retention offer in same contact |
| 2 consecutive missed monthly payments | Mandatory contact (Consumer Standards Dec 2023) |
| Price cap change announcement | Supplier-wide outbound campaigns |
| 30-day price change notice | Loyalty prompt (Energy UK good practice) |
| 60–90 days pre-renewal | Proactive soft engagement |

**Market context:** 3.21 million UK households switched in 2024 (up 38% on 2023 — ElectraLink). High switching velocity when fixed deals expire.

## 4. Win-Back Campaigns

- **Timing:** First contact 30–60 days post-churn (after 5-day switching window closes)
- **Second wave:** ~6 months post-churn
- **Channels:** Direct mail, email, SMS; outbound calls for high-value churned customers
- **Offers:** Cashback £50–£125 (2024-25 market range), below-market fixed rate, or loyalty credit
- **Conversion rate:** No published UK energy figure; cross-sector win-back typically 5–15% on first wave
- **Constraint:** 5-day switching window allows competitors to match instantly

## 5. Priority Services Register (PSR) Communications

**Who qualifies (Ofgem estimate: 40% of households eligible, but most unregistered):**
- Pensionable age, chronic illness/long-term medical condition, disability
- Children under 5, mental health conditions, communication needs

**Mandatory additional protections:**
- Large print, braille, or audio bills (on request)
- Nominee/proxy arrangement (carer or trusted person receives all communications)
- Password scheme for doorstep/phone verification
- Advance outage notice from network operators
- Priority emergency routing to trained agent

**Data sharing:** From 2024, mandatory PSR data sharing between suppliers and network operators when customer switches. No single national PSR register yet (2026) — customers must register separately with each party.

**Proactive identification:** Ofgem Consumer Vulnerability Strategy 2025 requires suppliers to use data (including means-tested benefits crossover) to identify eligible customers who haven't self-registered.

## 6. Proactive Bill Support

**Mandatory trigger (Consumer Standards Dec 2023):** Contact customer after 2 consecutive missed monthly payments OR 1 missed quarterly payment. Offer: support options, affordable repayment plan, payment holiday if appropriate.

**Detection methods:**
- Payment pattern analysis (DD delays, reduced payments, failed collections)
- Smart meter data (self-disconnection, consumption rationing on PPM)
- Welfare crossover (Ofgem/government initiative to share means-tested benefits data)
- Frontline agent identification during contact

**Supplier hardship funds:** >£500m pledged across 15 suppliers for Winter 2024-25.

## 7. Digital vs Non-Digital: Cost per Contact

| Channel | Cost per contact (UK benchmark) |
|---------|-------------------------------|
| Phone / agent-handled | £5–£12 |
| Webchat / email | £2–£5 |
| Self-serve (app / web) | £0.10–£0.50 |

**Opex context:** Ofgem cap allowance £97/customer/year (2025 decision, down ~£8 from prior). Digital-first suppliers target 30–40% below that benchmark.

**Digital-native advantage:** Octopus (Kraken platform): 10–15× lower cost-per-contact vs. legacy systems. Which? (2025): Octopus complaints = 261/100,000 customers vs. 1,525/100,000 large supplier average.

**SME digital adoption:** Much lower than residential — 60–70% of micro-business contracts sold via TPI/broker (not digital). Most SME renewals via broker or phone.

**Consumer Standards requirement (Dec 2023):** Multiple contact channels mandatory including webchat; extended call centre hours (evenings and weekends). Average call wait time fell from ~7 min (2022) to ~2 min (mid-2024).

## Implications for Simulation

| Gap | Priority | Fix |
|-----|----------|-----|
| 42-day renewal notice obligation not modeled | Medium | Company CRM should flag customers 49 days before expiry; formal notice fires at 42 days |
| No distinction between active renoters and passive SVT rollers | High | Model ~35% actively renew (take a new fixed deal); ~65% roll to SVT by default |
| Payment-miss state not tracked | High | After 2 missed monthly payments → "At Risk" flag; mandatory outreach |
| PSR customer sub-population | Low | Model ~10–15% of residential base as PSR-registered; different churn/comms model |
| Win-back not modeled | Medium | Win-back campaign at 30d and 90d post-churn; ~8% conversion rate first wave |
| Digital vs phone channel cost | Medium | Cost-to-serve should differentiate by contact channel; ~12× cost difference |
| SME 60–120 day renewal window | Medium | SME renewal notices currently not differentiated from residential timing |

## Key Regulatory Numbers

| Metric | Value |
|--------|-------|
| Domestic renewal notice window | 42–49 days before expiry (SLC 22A) |
| SME renewal notice window | 60–120 days before expiry |
| Tariff change notice (variable) | 30 days (SLC 22B) |
| Exit fee free window | Final 49 days of fixed contract |
| Missed payment contact trigger (monthly) | After 2nd consecutive miss |
| Welcome pack | Within 5 working days of supply start |
| Price cap (Apr–Jun 2026) | ~£1,568/year typical dual-fuel DD |
| Active renewer proportion | ~35% (take new fixed deal) |
| Passive SVT roller proportion | ~65% (default on contract expiry) |
| UK household switches in 2024 | 3.21 million (up 38% vs 2023) |
| Win-back conversion rate | ~5–15% (cross-sector benchmark) |
