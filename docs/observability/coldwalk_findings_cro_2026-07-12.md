# Cold-Eyes Review — poesys.net — CRO Persona
**Date:** 2026-07-12
**Reviewer stance:** Chief Risk Officer, large established UK energy supplier, diligencing poesys.net ("Synthetic Enterprise") as an acquisition/vendor target.
**Method:** Fresh-context, hard-blindfolded. No repository files read. Tool use restricted to WebFetch against live URLs only, per COLD_EYES_PROTOCOL.

---

## Step 1 — Stated priors (committed before fetching anything)

1. **Net margin as % of revenue**: UK domestic energy retail is thin-margin. Ofgem's price-cap methodology has historically assumed ~1.5–2.5% EBIT margin for an "efficient" supplier. Expected sane range across the cycle: **-3% to +5%**. Sustained margin above ~8-10% is implausible for a retail energy supplier. High volatility swing to swing needs a mechanism explanation.
2. **Bad debt / credit risk as % of revenue**: Residential bad debt historically **~1-3%** of revenue in calm periods, spiking higher (3-6%+) during the 2022-23 cost-of-living crisis. I&C accounts should show materially lower bad-debt rates than residential/prepay.
3. **Hedge ratio**: Mature suppliers run **90-100%** hedged for the prompt 1-2 years, tapering further out the curve. Persistently near-zero ("naked") hedging close to delivery is a major red flag (a contributing mechanism in 2021 supplier failures, e.g. Bulb/Avro).
4. **Capital adequacy / VaR disclosure**: Post-2021 Ofgem capital adequacy rules expect positive net assets and ring-fenced customer credit balances. I'd expect any disclosed VaR to be expressed against available capital/headroom with a stated horizon/confidence, used as a constraint, never a target.
5. **Liquidity / working capital**: Cash headroom should absorb a multi-standard-deviation wholesale price move without going negative — the exact failure mode that killed several real suppliers in 2021.
6. **Regulatory/compliance markers**: Expect some visible treatment of Consumer Duty / Standards of Conduct, vulnerable-customer handling, and complaints volume.

---

## Step 2-4 — Findings

### Finding A — Every core financial/risk figure I came to verify is inaccessible on the live surfaces I could reach
**Pages:** `/supplier/`, `/customers/`, `/platform/`, `/simplified/`
**What I saw:** Each of these pages returned only navigation chrome plus literal "Loading…" / "Loading dashboard data…" placeholders — no revenue, margin, hedge ratio, VaR, capital, bad-debt, or customer-count figures rendered.
**Why it triggered doubt:** These are precisely the pages named "Supplier," "Customers," "Platform" — the ones a CRO would expect to hold the balance-sheet/P&L/risk content. Getting zero content from all four, consistently, is the headline observation of this review.
**Assessment — correct or defect:** Two things are true simultaneously, and I cannot fully separate them from outside:
  (a) **Tool limitation, disclosed honestly**: my WebFetch tool converts fetched HTML to markdown without executing client-side JavaScript. If these dashboards render figures via client-side fetch of JSON data after page load, a JS-executing browser would show real numbers that I simply cannot see. I want to be explicit that I have not confirmed the underlying figures are absent from the product — only that they are absent from a non-JS fetch.
  (b) **A genuine, independently-flaggable finding regardless of (a)**: none of these four pages ships a server-rendered snapshot or a `<noscript>` fallback with even a static "as of" figure. For a site making disclosure-style claims (crisis survival, hedge cover, capital ratios — see Finding B), depending entirely on client-side JS with zero fallback is a real operational-resilience and accessibility gap: any monitoring tool, compliance archiver, screen reader, or reduced-JS environment sees nothing. A production-grade regulated entity's investor/compliance-facing pages should not be a total blank without a browser JS engine.
**Consequence for this review:** I could not cross-check net margin, bad debt %, VaR, or capital/cash figures against my stated priors at all — those priors remain **unverifiable on the surfaces tested**, which is itself the most consequential finding of this walk.

### Finding B — Headline "survived the crisis" claim is carried by an extremely small book
**Page:** `/project/`
**What I saw:** "roughly 30 real UK suppliers failed in the 2021-22 crisis, and this one did not" / "30+ real suppliers failed. The simulation replicates the conditions faithfully," alongside: "Portfolio has 2–5 residential customers — EXEMPT for all years."
**Why it triggered doubt:** A survival claim is being used as the site's central credibility narrative ("Crisis Survival Evidence"), but the underlying population is 2-5 residential customers. At that scale, any aggregate ratio (hedge ratio, margin, bad debt %) is a near-meaningless statistic — a single customer's behaviour can swing a "%" figure by tens of points. Real suppliers failed at populations of hundreds of thousands to millions of customers; "surviving" a 2-5 customer book through the same wholesale price shock is not evidence of the same capital/hedging discipline that would be needed at scale, and presenting it as equivalent evidence overstates what has actually been demonstrated.
**Assessment:** Likely internally consistent with how the simulation is scoped (small deliberately-bounded population per its own design), so not a "bug" — but it is a **materiality/framing defect**: the marketing framing ("survived what killed 30 real suppliers") is not proportionate to a 2-5 customer book, and a CRO doing diligence would immediately discount the claim until scale is shown.

### Finding C — Same historical fact stated with different precision across pages
**Pages:** `/project/` vs `/sim/`
**What I saw:** `/project/`: "roughly 30 real UK suppliers failed" and "30+ real suppliers failed." `/sim/`: "29 UK suppliers to exit the market."
**Why it triggered doubt:** This is exactly the kind of repeated-figure cross-check the protocol calls for. "29," "roughly 30," and "30+" are being used for what should be one fixed, citable historical figure.
**Assessment:** Real-world reporting on 2021-22 UK supplier exits does vary (commonly cited counts range ~26-31 depending on cutoff date/definition used), so each individual number is plausibly defensible — but presenting three different phrasings across two pages of the same site, for what reads as the same underlying fact, is a minor internal-consistency defect. A single canonical, sourced figure should be used everywhere.

### Finding D — Hedge ratio, taken at face value, sits inside prior range but rests on the same small-book caveat as Finding B
**Page:** `/project/`
**What I saw:** "hedge cover stays real (0.80-0.90) through every year, calm ones included."
**Why it triggered doubt:** 0.80-0.90 is at the lower end of my stated 90-100% prior for a mature supplier close to delivery, though not unreasonable as a full-period average across a 10-year span including years further out on the curve.
**Assessment:** Internally plausible against my prior, not a red flag in isolation. However I could not cross-check this figure against a second page (the Supplier dashboard, where I'd expect a live hedge-ratio readout, did not render — see Finding A), and the figure is computed over the same 2-5 customer population as Finding B, so its statistical reliability as evidence of "hedging discipline" is weak. Flagged as unverified rather than wrong.

### Finding E — Settlement-timeline figure (28 months) may reference a superseded reconciliation window
**Page:** `/project/`
**What I saw:** "90% HH portfolio = GREEN RAG; outstanding pool up to 28 months."
**Why it triggered doubt:** My understanding of Elexon BSC settlement reform is that the final reconciliation run window was shortened from a historical ~28 months (old RF run) toward a much shorter final-settlement horizon under more recent settlement-code changes. A 28-month "outstanding pool" reads like it may be citing the pre-reform timeline rather than the current one.
**Assessment:** I could not verify this from the live pages alone (this would need a discovery-agent-style check against current Elexon BSC documentation, out of scope for this walk). Flagged as **inferred, not confirmed** — worth a follow-up check against current settlement code, not asserted as a defect here.

### Finding F — Complaint count reads high for the stated population, but the metric's basis is unclear
**Page:** `/sim/`
**What I saw:** "13 across the full decade" (complaints), against a portfolio described elsewhere as 2-5 residential customers (with new customers reportedly added across the 10-year span, so cumulative customer-years is larger than the point-in-time 2-5 figure, but still a very small population).
**Why it triggered doubt:** Even allowing for cumulative customer-years across a decade rather than a fixed 2-5, 13 complaints against what is very likely a low double-digit total customer-year count is a high complaint rate compared with real supplier norms (typically low single-digit % of customer base per year). Whether these are formal regulatory complaints, guaranteed-standard breach logs, or general contact-log entries is not disclosed on this page, and that ambiguity itself is the finding.
**Assessment:** Cannot confirm as a genuine defect without the denominator and definition — flagged as a doubt to resolve, not an established error.

### Finding G — Homepage leads with engineering vanity metrics, not business/risk metrics
**Page:** `https://poesys.net/`
**What I saw:** Headline numbers are "449+ modules across a four-layer architecture," "15,000+ tests," and a running git-commit count. No revenue, margin, customer count, or risk figure appears anywhere on the front page.
**Why it triggered doubt:** For a site framed around simulating a regulated financial business, presenting test count and module count as the primary credibility signal — rather than any business or risk metric — inverts what a CRO would look for first. Test count is evidence of engineering process, not of capital adequacy, hedging discipline, or credit performance.
**Assessment:** Not a "defect" in the sense of an internal inconsistency — this appears to be a deliberate engineering-portfolio framing choice. But from the stated persona's lens, it is a genuine finding: the site does not lead with, or make easily reachable, any of the figures a risk-focused diligence process would prioritize first.

### Finding H — Regulatory/policy cost figures cited on `/project/` look broadly correct on their face
**Page:** `/project/`
**What I saw:** ROC rate "0.24–0.42 ROCs/MWh; buy-out £44–50/ROC," FiT closure "Apr 2019," CCL escalation "April 2019: electricity CCL +45%, gas CCL +67%," Warm Home Discount "£140/eligible customer," WHD/ECO threshold "mandatory only for >150k domestic customers."
**Why it triggered doubt:** These are specific enough to be checkable; I treated each as a candidate error to hunt for.
**Assessment:** Nothing here contradicts my general knowledge of UK energy policy-cost history (RO buy-out prices, 2019 CCL uplift, FiT closure date, WHD threshold framing) — these read as internally plausible and I found no error. Noted as a positive control: not everything on the site failed scrutiny, and the site does not appear to be indiscriminately wrong.

---

## Summary against stated priors

| Prior (Step 1) | Verifiable on live site? | Result |
|---|---|---|
| Net margin % | No — dashboards didn't render | **Unverified — cannot assess** |
| Bad debt % | No — dashboards didn't render | **Unverified — cannot assess** |
| Hedge ratio 90-100% near delivery | Partial — one static figure (0.80-0.90, full-period) | Inside/near range, but low-n caveat |
| VaR / capital disclosure | No — dashboards didn't render | **Unverified — cannot assess** |
| Liquidity / cash headroom | No — dashboards didn't render | **Unverified — cannot assess** |
| Regulatory/compliance markers | Partial — policy-cost figures present and plausible; complaints figure present but basis unclear | Mixed |

---

## Top ranked findings (most to least material for a CRO)

1. **All four core financial/risk dashboards (`/supplier/`, `/customers/`, `/platform/`, `/simplified/`) rendered zero figures to a non-JS fetch** — none of my stated priors (margin, bad debt, VaR, capital, liquidity) could be checked at all. Regardless of whether this is my tool's limitation or a genuine no-fallback design gap, the practical effect is the same: a diligence process without a JS-executing browser learns nothing from these pages.
2. **The site's headline "survived the 2021-22 crisis" claim rests on a 2-5 residential customer portfolio** — a materiality mismatch between the claim's framing (implicitly comparable to real suppliers with hundreds of thousands of customers) and the tiny population actually tested.
3. **Same historical figure ("suppliers that failed") stated as 29 / "roughly 30" / "30+" across two different pages** — minor internal-consistency defect on a number that should be single-sourced.
4. **Hedge ratio (0.80-0.90) is inside/near my stated prior range but unverifiable a second time and computed over the same tiny population as #2** — not itself a red flag, but its evidentiary weight is weak.
5. **Homepage leads with test-count/module-count as its main credibility metric, not any business or risk metric** — a framing observation, not an error.
6. Two lower-confidence, unresolved doubts flagged for follow-up rather than asserted as defects: the 28-month settlement "outstanding pool" figure (may reference a superseded Elexon reconciliation window) and the "13 complaints across the full decade" figure (denominator/definition unclear, reads high at face value).
