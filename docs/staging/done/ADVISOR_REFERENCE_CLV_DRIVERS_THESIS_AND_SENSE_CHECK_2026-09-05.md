
**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** unminted

*Header applied AUTOMATICALLY by `background/staging_watcher` on arrival, because an unclassified staging document refuses every lane's commit and an arriving document must never block a landing. Severity RECORDED: carried through from the author's own words. Lane A_strategy_governance is the default for an externally-authored instruction and says what KIND of document this is, not what it is about — correct it if it belongs to a lane. Not one word of the author's text is altered.*

**Severity:** RECORDED · **Lane:** knowledge layer / discovery · **Type:** REFERENCE — not canon, not a first sample, a sense check that may be wrong · **Proportionality:** reversible / narrow — parallel discovery-class work

# [ADVISOR-STAGED] CLV drivers thesis and reference model — a sense check for the portfolio-draw approach (2026-09-05)

**Director's framing, verbatim:** *"I want this thesis and then the numbers and examples that test this hypothesis. Maybe disprove it in places or at least quantify in size and scale, but let's assume about right based on my decades of experience."* And on status: *"Not canon as might be wrong but a sense check."*

This document is the advisor's working model, built in the advisor channel this afternoon with the director, and staged **as a reference for the machine to measure against** — in parallel with the three phase-1 rulings staged today, as knowledge/discovery work, **not** as a sample and **not** as authority. §8 says what to do with it.

---

# What drives a customer's value — the thesis, the ranges, and how to test it

*Advisor working draft, 5 September 2026 (v3: contribution basis, merit order, explicit-cash-flow reference model). **REFERENCE, NOT CANON.** A sense check the machine measures against, that may be wrong. Where a figure is anchored, the anchor is named; where it is the advisor's estimate from experience, it says so. The purpose is to fix the shape of the argument before the machine tests it on real draws.*

---

## 1. What "CLV" means here, and the one external check

**Contribution basis.** A customer's value is the net present value of the revenue they bring less every cost they *cause* — energy, network and policy costs, metering, the contacts and collections they generate, the debt they leave, the forecasting and hedging error their consumption creates, the working capital they tie up — survival-weighted by their own churn, ten years, 8%. **Fixed overhead is not charged to the customer.** It is a company-level hurdle: the book's total contribution must clear it, and that is the minimum-viable-scale question, not a per-customer one.

**Gross margin is not consumption.** Gross margin = volume × unit margin, per fuel, plus standing-charge margin. Unit margin (p/kWh) depends on the tariff the customer is on (a discounted fixed deal, the SVT at the cap) and on how well the hedge matched outturn — it can be negative for a year, as it was for fixed-price customers in 2021–22. Volume amplifies whatever sign the unit margin has: the biggest house in the book is the biggest profit on the SVT and the biggest loss on a mispriced fixed deal. They are separate drivers with an interaction, and the model keeps them separate.

**The market's price is the check.** OVO paid £500m for SSE's 3.5m customers in January 2020 (~£143 each); E.ON is reported to be paying up to £600m for OVO's ~4m in 2026 (~£150 each). A buyer pays contribution NPV less its own capitalised overhead: the typical customer below has a contribution NPV of ~£690 before acquisition cost, and a buyer running £100–130 of overhead per customer per year over a four-to-five-year payback would price that at £150–200. It reconciles, at the level of accuracy this exercise can claim.

## 2. The per-customer contribution, typical dual-fuel household

| Line | £/yr | Basis |
|---|---:|---|
| Electricity gross margin: 2,700 kWh × 2.5p | 68 | TDCV medium; unit margin of cap order (EBIT + variable opex allowance per kWh); estimate |
| Gas gross margin: 11,500 kWh × 0.6p | 69 | as above, gas |
| Standing-charge margin (dual fuel) | 90 | SC revenue less fixed network, DCC (£19 + £14) and metering; TCR 2023 moved fixed cost here; estimate |
| **Gross margin** | **226** | ≈ 12% of an £1,860 bill — inside the 8–14% real-supplier range in the knowledge map |
| Variable cost to serve (billing, contacts, collections) | −40 | contacts £5–12; 1–2 a year |
| Bad debt | −25 | DD ~1% of bill; cap debt allowance order £25–40 |
| Forecast and volume risk | −15 | imbalance, hedge-shape error, fixed-tariff volume risk; estimate |
| Working capital | 0 | DD credit balances earn, arrears cost; nets to ~0 for a typical DD customer |
| **Contribution** | **146** | |

Churn 12% (the market rate) → expected life ~8 years → **contribution NPV ~£690 before acquisition cost, ~£540 after** (PCW + onboarding £150, the project's anchor).

## 3. The drivers, one at a time — typical, plausible low and high, and the tail

Each driver swung alone, others typical. Swing = NPV difference low→high; tail = the one-in-twenty case. The tail for unit margin is a crisis year and is shown as if it persisted; read it as a one-year hit of roughly a tenth of the figure.

| Driver | Low | Typical | High | Tail | NPV swing | Tail effect | Anchor / basis |
|---|---:|---:|---:|---:|---:|---:|---|
| Churn (apathy vs engagement) | 3% | 12% | 28% | 40% | **£515** | −£360 | disengaged 3–5%; market 12–16%; engaged 25–30%; renter + engaged |
| Bad debt | £5 | £25 | £110 | £300 | £495 | −£1,290 | DD ~1%; SC ~6%; SC + stress 10–15% |
| Cost to serve, variable | £20 | £40 | £110 | £400 | £425 | −£1,690 | contacts, collections, disputes; ombudsman case in tail |
| Unit margin, gas (p/kWh) | 0.15 | 0.6 | 0.9 | −3.0 | £405 | −£1,950 (≈ −£195 one-year) | discounted deal / cap / cap+ / under-hedged crisis |
| Unit margin, electricity (p/kWh) | 0.5 | 2.5 | 3.5 | −8.0 | £380 | −£1,330 (≈ −£133 one-year) | as above |
| Standing-charge margin | £40 | £90 | £120 | £20 | £375 | −£330 | fixed-cost recovery; low for single-fuel / prepay |
| Gas volume (kWh) | 6,000 | 11,500 | 17,000 | 35,000 | £310 | +£660 | TDCV; NEED pre-1919 detached tail |
| Electricity volume (kWh) | 1,600 | 2,700 | 4,100 | 8,000 | £295 | +£620 | TDCV; all-electric heating tail |
| Forecast and volume risk | £5 | £15 | £60 | £150 | £260 | −£635 | grows with weather gradient × volatility |
| Acquisition cost (one-off) | £30 | £150 | £250 | £350 | £220 | −£200 | referral / PCW / paid |
| Value-add direct income | £0 | £0 | £40 | £120 | £190 | +£565 | flex share, install margin amortised |
| Shape (peak vs off-peak) | −£15 | £0 | +£15 | +£100 | £140 | +£470 | £20–40/MWh spread; EV + battery tail |
| Working capital | −£10 | £0 | +£15 | +£40 | £120 | −£190 | credit balances vs arrears |
| Loyalty effect of value-add / accurate billing | 0 | 0 | −4 pts | −8 pts | £100 | +£225 | HYPOTHESIS |

**The volume × unit-margin interaction**, contribution NPV, gas only:

| Gas unit margin | 6,000 kWh | 11,500 kWh | 17,000 kWh | 35,000 kWh |
|---|---:|---:|---:|---:|
| −3.0p (under-hedged crisis, if persistent) | −£630 | −£1,410 | −£2,180 | −£4,720 |
| 0.15p (deep-discount deal) | £257 | £296 | £334 | £461 |
| 0.6p (cap) | £384 | £539 | £694 | £1,202 |
| 0.9p (cap, well hedged) | £468 | £701 | £934 | £1,696 |

Volume is a lever on margin, not margin. The big house is worth £1,200 or −£4,700 depending entirely on the unit margin — which is a pricing and hedging decision, not a property of the house. The house decides the *size* of the bet.

## 4. Drivers move together — bundles

| Bundle | GM £/yr | Contribution £/yr | Life (yrs) | NPV |
|---|---:|---:|---:|---:|
| Sits and pays: disengaged owner, SVT at cap, DD, average house | 257 | 209 | 25 | **+£1,153** |
| Engaged switcher on a discounted fixed deal | 135 | 75 | 3.6 | +£70 |
| Big old house, passive, SVT | 392 | 282 | 10 | +£1,266 |
| Big old house, fixed deal, crisis year (one-year hit) | −964 | −1,149 | — | ≈ −£1,150 that year |
| Standard credit + income stress | 226 | −164 | 5.6 | **−£786** |
| Same household, smart meter, PAYG switch permitted | 226 | 52 | 5.6 | +£50 |
| Big house + value-add delivered (loyalty on) | 335 | 285 | 20 | +£1,561 |
| EV + battery, permission given, off-peak shape | 296 | 346 | 17 | **+£1,856** |
| PV only, no battery | 204 | 109 | 10 | +£398 (vs £539 without PV) |
| Small flat, private renter, active | 116 | 61 | 2.9 | ≈ £0 |
| Vulnerable, PSR, prepayment | 226 | 64 | 17 | +£223 |

What the bundles show:

1. **Apathy is the single biggest driver of value once margin is real.** The "sits and pays" household is the third most valuable case, on an ordinary house, purely by staying 25 years at cap margin with almost no cost to serve. Per year they look unremarkable; in NPV they are the engine. The director's instinct is right about the year and the bundle corrects it for the lifetime: the right treatment is restraint.
2. **Debt is the biggest destroyer, and smart metering's value is collectability.** The stressed standard-credit household is −£786; a smart meter that permits a move to pay-as-you-go (no vulnerability flag, won't-pay not can't-pay) recovers ~£840 and brings them to about break-even. The smart-versus-dumb *cost* difference is tens of pounds either way; this is hundreds.
3. **The crisis tail is a one-year event that outweighs a decade.** One under-hedged year on a big house costs more than that house contributes in ten. Hedging and forecasting quality is the largest single risk to any customer's value, and it scales with the customer's volume and weather gradient — which is the housing and weather work's contribution to CLV.
4. **Value-add earns through loyalty and through shape, not through income.** Direct value-add income is small; the loyalty effect adds ~£300 on a big house; EV + battery with permission is the top case because shape value and loyalty compound. PV alone reduces value (less volume, worse shape) — from £539 to £398 — unless paired with a battery or a tariff that captures the shape.
5. **The engaged switcher is roughly worthless and the small renter is exactly worthless**, on contribution, after acquisition cost. Serving them costs little and earns little; the error would be spending acquisition or retention money on them.


## 4b. The merit order (director's rule, tested)

Value is contribution multiplied by survival. That multiplication makes the drivers **lexicographic**, not additive:

1. **Pays?** If contribution is negative, a longer life multiplies the loss: churn becomes a *benefit* and value-add becomes *harmful* (the loyalty effect lengthens a negative stream). Tested: the stressed standard-credit household is −£786 at 18% churn, −£517 at 40%, −£410 at 60%; the same household with value-add and its loyalty effect is *worse*, not better. For a non-payer the rational treatment is minimise exposure, move to pay-as-you-go where the rules permit, and do not retain.
2. **Stays?** Engagement and elasticity travel together — the mechanism that makes people leave makes them take the discounted deal — so "amazing margin, high churn" barely exists. A big house on a discounted deal at 30% churn is worth £258; a loyal typical house at cap margin at 4% is £762. Restraint toward the apathetic is a policy, not an accident.
3. **How big is the margin bet, and is it hedged right?** Volume × unit margin. The house decides the size; pricing and hedging decide the sign; the weather gradient and physics decide whether the hedge matches the shape.
4. **Value-add, only then** — and only where there is a controllable asset with permission (shape) or a loyalty effect to earn. Big house that pays and stays: £1,133 without, £1,621 with. The same house that doesn't pay: −£332 with the identical value-add.

The company's inference problem has the same order, and so do its observables: payment behaviour arrives within months, engagement at the first renewal, physics from the meter over a winter.

## 4c. The method — a proper NPV, not a lifetime factor

The earlier shortcut (constant contribution × survival-weighted annuity) undervalues loyalty: a terminal value adds 41% to a 4%-churn customer and 2% to a 28%-churn one, so truncation at ten years biases against exactly the customers the thesis says are the engine. The reference method:

- **Explicit yearly cash flows, ten years**, per customer: revenue less energy, network and policy at that year's prices and hedge outturn; contacts, collections, debt movement and write-offs in the year they occur; one-offs (acquisition, install margin, back-billing) when they land; the house and household changing underneath. **The SIM already produces every one of these per customer** — CLV is a read of its own ledger, not a formula on top.
- **Survival from a tenure-dependent hazard**: high in the first renewal window, falling with years stayed, reset by a bill shock or a move. The reference uses a placeholder multiplier shape (1.6 in year 1 falling to 0.6 by year 9); the SIM's own churn mechanics supply the real curve.
- **Terminal value at year ten**: a decaying perpetuity of year-ten contribution for the surviving fraction, at the discount rate plus the then-churn rate — using the customer's own churn rather than a market multiple. *Director's choice pending.*
- **Discount rate** 8% — *advisor placeholder; director curriculum value pending.*
- **Two CLVs, one formula.** The company computes it on its beliefs and acts on that; the SIM computes it on truth and the tournament scores on that. The gap is the company's inference error, priced.

## 4d. Reference results (explicit cash flows, hazard, terminal value)

| Case | 10-yr NPV after CAC | Terminal value | Total | Payback year |
|---|---:|---:|---:|---:|
| Typical | £400 | £135 | £535 | 2 |
| Sits and pays (SVT cap, disengaged, DD) | £1,004 | £637 | £1,641 | 1 |
| Engaged switcher (discount deal) | £-14 | £6 | £-8 | never |
| Big old house, passive, SVT | £1,012 | £349 | £1,362 | 1 |
| Big old house, crisis in year 3 (under-hedged fixed) | £133 | £316 | £449 | 1 |
| Big house + VA installed year 2 (loyalty on) | £1,298 | £632 | £1,930 | 1 |
| Standard credit + stress, write-off year 3, then leaves | £-416 | £1 | £-415 | never |
| Same, smart, PAYG switch permitted in year 2 | £17 | £52 | £70 | 9 |
| EV + battery, permission, off-peak | £1,584 | £777 | £2,361 | 1 |
| PV only | £300 | £135 | £435 | 2 |
| Small flat, private renter, active | £-68 | £2 | £-66 | never |
| Vulnerable, PSR, prepayment | £23 | £76 | £99 | 8 |

Read against §4: the loyal cases gain most from the terminal value; the crisis year on the big house wipes two years' value and recovers only by year eight; the standard-credit case never pays back; PAYG permission turns it from −£415 to +£70.

## 5. The thesis, as testable claims

Each claim names the SIM measurement that would confirm, refute or size it. Assumed about right on experience; the point of the machine is to put numbers on them.

- **H1 — Debt dominates the downside.** Across a sample drawn for difference, bad debt plus its induced cost to serve explains more of the variance in fully costed CLV than any other driver. *Test:* variance decomposition of CLV on real draws; expect debt + collections > 40% of downside variance.
- **H2 — Consumption dominates the upside, and it is house physics.** House size, fabric and heating fuel explain most of the positive tail. *Test:* the housing phase-1 sample's contribution to CLV variance versus the people sample's, level only.
- **H3 — Engagement is a multiplier, not an addend.** The value of low churn scales with net contribution; on low-net customers it is irrelevant. *Test:* interaction term churn × net in the decomposition; expect it to exceed either main effect.
- **H4 — Value-add earns through loyalty more than through income.** Direct value-add income is < £50/yr for > 90% of customers; the churn reduction it causes is worth more than the income on any customer netting > £100/yr. *Test:* the SIM's offer→response→churn mechanic, with the loyalty parameter measured, not assumed; report the break-even net at which loyalty exceeds income.
- **H5 — Accurate forecasting and billing at premise level is worth as much as value-add, possibly more.** Right-sized direct debits, no bill shocks, correct shape in the hedge: lower churn, lower contacts, lower debt, lower volume risk. *Test:* run the same book with a supplier that forecasts on profile averages against one that forecasts on premise physics; expect the gap to show in forecast/volume risk, bill-shock churn and arrears, not in gross margin.
- **H6 — The apathetic are the quiet engine; the right action is restraint.** Disengaged customers on cap margin with low cost to serve are among the highest-NPV customers; disturbing them costs more than any upsell earns. *Test:* NPV rank of the disengaged archetype on real draws; and the churn response to unsolicited offers by archetype.
- **H7 — Controllable assets with permission are the only large value-add upside.** EV and battery with a permission to control create shape value in the £60–120/yr range; PV alone is negative to the supplier. *Test:* shape value per asset class from half-hourly draws against the settlement price spread; expect PV-only negative, EV+battery positive, sign robust across weather cells.
- **H8 — Natural shape is worth a little, not a lot.** Gas cooking, low heating, even weekday/weekend and off-peak usage are worth £10–20/yr. *Test:* distribution of shape value on real draws; expect the interquartile range inside ±£15.
- **H9 — Smart metering pays through collectability and shape, not through cost.** Net metering cost difference is tens of pounds either sign; the PAYG-switch option on won't-pay accounts is worth hundreds. *Test:* bad-debt loss by meter type, holding payment method and stress constant, on real draws; and the vulnerability-flag rate that gates it.
- **H10 — The average reconciles to the market.** A book drawn in population proportion has a mean contribution NPV of roughly £600–700 before acquisition cost, which nets to the market's £150 per customer after a buyer's capitalised overhead. *Test:* the weighted mean of CLV on a representative re-weighting of the sample; if it does not land near £150, the cost stack is wrong before the drivers are.

## 6. What this changes in the three rulings staged today

- **People phase 1** should carry credit risk and payment method (in), **engagement archetype** (forward from phase 2), **expected length of stay** (add), **contact propensity** (forward) — as stated: **the four items are anchored or anchorable and every one of them is a merit-order gate.
- **Housing phase 1** should add **forecastability** as an output per house: the weather gradient and its predictability, because H5 lives there.
- **Weather phase 1** is unchanged; its gradient feeds H5.
- The **run-mix** set the director will ratify should include a population-proportional re-weighting purely for H10.

## 7. What is proxy and what is anchored

Anchored (published or in the project's registers): the cap cost stack and EBIT allowance; the 8–14% gross-margin range; TDCV bands; the DD share and standard-credit bad-debt ratio; the engagement mix; the market price per customer (two transactions); DCC charges; the acquisition-cost anchor. Advisor's estimates from experience, to be replaced by the machine's measurements: the unit margins per fuel and the standing-charge margin; third-party per-meter costs beyond DCC; contact costs and rates; forecast/volume-risk magnitudes; shape values; value-add income and install margins; every loyalty effect (a hypothesis by construction). Nothing in this document should enter a register until it has been measured.


---

## 8. What the machine does with this

**Status: REFERENCE, discovery-class, parallel to the three phase-1 rulings. Not canon. Not a first sample. May be wrong.**

1. Build the CLV computation from the SIM's own ledger per §4c, per customer, on real draws, on both sides of the wall (truth and belief).
2. Reproduce the tables in §3, §4 and §4d on real draws. Where the real draws disagree with this reference, **the disagreement is a finding to explain — the mechanism, the anchor, or this reference is wrong — never a number to converge to (R12).**
3. Size and, where possible, disprove the ten hypotheses in §5.
4. Present the two pending director values (discount rate; terminal-value method) with a recommendation.
5. Register the results as a knowledge page: what a customer is worth, what drives it, and in what order — with this reference cited as the sense check it was, struck through where it was wrong.

## Appendix — the reference model (Python, runnable, placeholders marked)

```python
"""CLV REFERENCE MODEL v3 -- explicit yearly cash flows, tenure-dependent churn hazard,
10-year horizon + terminal value (decaying perpetuity), contribution basis (no fixed overhead).
REFERENCE / SENSE CHECK ONLY. Not canon. Placeholders flagged. Where the SIM's own ledger
disagrees with this, that is a finding to explain, never a target to converge to (R12)."""
import json
R = 0.08            # discount rate -- ADVISOR PLACEHOLDER, director curriculum value pending
YEARS = 10
TENURE_FACTOR = [1.6, 1.3, 1.1, 1.0, 0.9, 0.8, 0.7, 0.7, 0.6, 0.6]   # hazard multiplier by year of tenure (placeholder shape)

def base():
    return dict(elec=[2700]*YEARS, gas=[11500]*YEARS, um_el=[2.5]*YEARS, um_gas=[0.6]*YEARS,
                standing=[90]*YEARS, cts=[40]*YEARS, debt=[25]*YEARS, fvr=[15]*YEARS, wc=[0]*YEARS,
                shape=[0]*YEARS, va=[0]*YEARS, oneoff=[0]*YEARS, cac=150, churn=0.12, loyalty=[0]*YEARS)

def run(c):
    npv = -c["cac"]; surv = 1.0; rows = []; cum = -c["cac"]
    for t in range(YEARS):
        contrib = (c["elec"][t]*c["um_el"][t] + c["gas"][t]*c["um_gas"][t])/100 + c["standing"][t] \
                  - c["cts"][t] - c["debt"][t] - c["fvr"][t] - c["wc"][t] + c["shape"][t] + c["va"][t] + c["oneoff"][t]
        h = min(0.95, max(0.005, (c["churn"] + c["loyalty"][t]) * TENURE_FACTOR[t]))
        surv_mid = surv * (1 - h/2)                     # alive on average through the year
        pv = contrib * surv_mid / (1+R)**(t+1)
        npv += pv; cum += pv; surv *= (1-h)
        rows.append(dict(year=t+1, contrib=round(contrib), hazard=round(h,3), survival=round(surv,3), pv=round(pv), cum=round(cum)))
    h10 = min(0.95, max(0.005, (c["churn"] + c["loyalty"][-1]) * TENURE_FACTOR[-1]))
    c10 = rows[-1]["contrib"]
    tv = c10 * surv / (1+R)**YEARS / (R + h10)          # decaying perpetuity of year-10 contribution, surviving fraction
    payback = next((r["year"] for r in rows if r["cum"] >= 0), None)
    return dict(npv10=round(npv), tv=round(tv), total=round(npv+tv), payback=payback, rows=rows)

def make(**mods):
    c = base()
    for k,v in mods.items():
        if isinstance(v, list): c[k] = v
        elif k in c and isinstance(c[k], list): c[k] = [v]*YEARS
        else: c[k] = v
    return c

cases = {
 "Typical": make(),
 "Sits and pays (SVT cap, disengaged, DD)": make(um_el=3.0, um_gas=0.75, cts=25, debt=8, churn=0.04),
 "Engaged switcher (discount deal)": make(um_el=0.8, um_gas=0.2, cts=35, debt=10, churn=0.28),
 "Big old house, passive, SVT": make(elec=3800, gas=25000, um_el=3.0, um_gas=0.75, fvr=45, churn=0.10),
 "Big old house, crisis in year 3 (under-hedged fixed)": make(elec=3800, gas=25000, um_el=[2.5,2.5,-8.0]+[2.5]*7, um_gas=[0.6,0.6,-3.0]+[0.6]*7, fvr=[15,15,120]+[15]*7, churn=0.10),
 "Big house + VA installed year 2 (loyalty on)": make(elec=3800, gas=25000, oneoff=[0,300]+[0]*8, va=[0,0]+[40]*8, loyalty=[0,0]+[-0.05]*8, fvr=25, churn=0.10),
 "Standard credit + stress, write-off year 3, then leaves": make(cts=[150]*3+[40]*7, debt=[120,200,450]+[25]*7, wc=25, churn=[0.18]*YEARS and 0.18, loyalty=[0,0,0]+[0.4]*7),
 "Same, smart, PAYG switch permitted in year 2": make(cts=[150,90]+[60]*8, debt=[120,60]+[15]*8, wc=[25,10]+[0]*8, churn=0.18),
 "EV + battery, permission, off-peak": make(elec=5500, shape=90, va=40, churn=0.10, loyalty=-0.04),
 "PV only": make(elec=1800, shape=-15, churn=0.10),
 "Small flat, private renter, active": make(elec=1700, gas=6000, um_el=0.8, um_gas=0.2, cts=30, debt=10, churn=0.35),
 "Vulnerable, PSR, prepayment": make(cts=140, debt=12, wc=-5, churn=0.06, standing=60),
}
out={}
print(f"{'case':56}{'10y NPV':>9}{'TV':>7}{'total':>8}{'payback':>9}")
for n,c in cases.items():
    r=run(c); out[n]=r
    print(f"{n:56}{r['npv10']:>9}{r['tv']:>7}{r['total']:>8}{str(r['payback']):>9}")
json.dump(out, open("reference_results.json","w"), indent=1)

```
