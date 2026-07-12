# COLD_EYES_PROTOCOL — Fresh-Context Regulatory/Legal Review
**Persona:** General Counsel / Head of Regulatory Compliance, UK energy supplier
**Reviewer state:** No prior knowledge of codebase, build history, or internal docs — live-site observation only
**Date:** 2026-07-12
**Site reviewed:** https://poesys.net/

---

## 1. Stated Priors (committed BEFORE fetching anything)

1. **VAT** — UK domestic energy VAT is 5%, not the standard 20%. Any bill/tariff shown against a domestic/residential customer at 20% VAT is a red flag. SME/business consumption can legitimately carry 20% VAT (subject to de minimis/usage-type rules), so correctness depends on the customer segment displayed.
2. **Back-billing cap** — Ofgem SLC back-billing rules cap look-back to 12 months where the supplier was at fault for the billing delay/error. If the site claims billing-law compliance, I expect this cap referenced or demonstrably respected somewhere.
3. **Licensing claims** — A real UK domestic supplier must hold an Ofgem supply licence. If this site presents itself anywhere as an actual licensed supplier (rather than clearly labelled fictional/simulated), that's a serious misrepresentation risk. I expect either no such claim, or an explicit "this is a simulation" disclaimer.
4. **Complaints handling / Energy Ombudsman** — SLC requires signposting to the Energy Ombudsman after 8 weeks (56 days) or deadlock. Expected on any complaints-facing content if the site holds itself out as a live supply operation.
5. **Vulnerable customer protections** — Priority Services Register (PSR) or equivalent should be referenced if the site claims to model a full-service supplier.
6. **Consumption/tariff plausibility** — UK domestic electricity ~2,700–3,300 kWh/yr (Ofgem TDCV), gas ~11,500–12,000 kWh/yr; SME figures meaningfully higher (MWh range). Wildly outside these bands = doubt.
7. **Data protection** — a site handling "customer" records (even synthetic) would normally carry a privacy notice / ICO reference if presented realistically.
8. **Copyright/entity footer** — should name a real or clearly-labelled trading-style entity, and given this is a public non-gated domain showing synthetic customer/billing data, I'd expect a clear "research/simulation, not a real regulated business" disclaimer somewhere prominent.
9. **robots.txt** — expect boilerplate; nothing suggesting admin/internal panels are exposed; consistent entity naming.

---

## 2. Findings by Page

### https://poesys.net/ (home)
**Observed:** Entity name in footer: `© 2026 Poesys Platforms. All rights reserved.` Header brand "Synthetic Enterprise" / "Poesys". Nav: Home, SIM, Supplier, Customers, Platform, Method, Project, Simplified. Promotional-register language: **"A UK energy supplier that builds and runs itself,"** references to **"could go live,"** a **"shadow-live track record"** against real Elexon market data since 2016. Also contains the self-qualifying line **"it can never see inside the simulation it runs in"** and **"Not a model of a company; a running one."** No Ofgem licensing claim. No pricing/tariff/savings claims. No terms-of-service or privacy-policy links anywhere on the page.

**Why it triggered doubt:** Phrases like "could go live" and "shadow-live track record" sit in the same register a real supplier would use to describe genuine trading history and go-live readiness. The qualifying language ("it can never see inside the simulation it runs in") is written in the project's own internal epistemic vocabulary — accurate to an insider, but not a plain-English disclaimer a lay visitor or regulator skim-reading the homepage would necessarily parse as "this is fictional, not a real licensed business." There is no blunt, unambiguous banner (e.g., "SIMULATION — not a real, licensed energy supplier") on the page as fetched.

**Classification:** Reads-ambiguous / **genuine gap in plain-English disclaimer**, not a fabricated compliance claim. Low actual risk today (no licence number, no real pricing, no solicitation of real customers) but the promotional register is a communications risk if screenshotted/quoted out of context.

### https://poesys.net/customers/
**Observed:** Page fetched as an HTML shell/nav only — no individual customer records, account numbers, tariffs, consumption figures, VAT rates, or segment labels (household/SME) were retrievable. Footer copyright consistent with home page.

**Limitation, stated plainly:** This page is evidently a JavaScript-rendered single-page app. WebFetch converts static HTML to markdown and does not execute JavaScript, so the actual rendered customer/bill data (the content most relevant to VAT-rate, back-billing, and consumption-plausibility priors #1, #2, #6) **could not be observed or verified in this review**. I am not able to confirm or deny correctness of any customer-facing figures on this page. This is a tooling limitation, not a finding that the page is empty or compliant — a follow-up check with a JS-capable browser tool is needed before any conclusion about VAT/back-billing/consumption correctness on this specific page can be drawn.

### https://poesys.net/supplier/
**Observed:** Same JS-shell limitation — page returned "Loading…" / "Loading dashboard data…" and an "Ask the Data" prompt, no substantive content. No references to billing accuracy, back-billing, complaints handling, Energy Ombudsman, vulnerable-customer/PSR provisions, hedging/margin figures, or compliance statements were retrievable — **because the page did not render**, not because they are confirmed absent.

**Limitation, stated plainly:** Same as above — cannot confirm or deny priors #2, #4, #5 from this fetch. Needs a JS-capable check.

### https://poesys.net/project/
**Observed:** Explicitly frames the whole exercise as a simulation: *"Poesys is not building a model of an energy supplier; it is building a running autonomous energy business"* running against *"real Elexon/NESO half-hourly settlement data (2016-2025)."* States *"It is also a company that can die. Insolvency and licence revocation are terminal states here, not exceptions designed away."* **No claim to holding an Ofgem licence.** Lists real external data sources used for calibration (Ofgem published rates, DESNZ/BEIS figures, National Grid ESO fuel-mix data) alongside 62 named "regulatory modules" (Renewables Obligation, Climate Change Levy, FIT Levy, Guaranteed Standards of Performance, Ofgem Supply Return, FRA capital ratios, Fuel Mix Disclosure). Contains an honesty disclaimer: *"every headline figure on this site is PROVISIONAL until it lands"* and *"Not yet written — honestly empty rather than a placeholder pretending otherwise."* No independent audit/certification claimed.

**Why this is reassuring:** This is the clearest and most explicit disclaimer page found on the site — it directly addresses priors #3 (no licensing claim) and is transparent about provisional/incomplete data. **Classification: internally correct, and reads correctly too** — this page would satisfy a compliance reviewer on the licensing-misrepresentation question, on its own.

**Residual concern:** This disclaimer is one click deep (Project page), not on the homepage or on the customer/supplier pages themselves (which, per above, could not be confirmed to carry any disclaimer given the JS-rendering limitation). A visitor who lands directly on `/customers/` or `/supplier/` via a shared link or search result may never see the Project page's disclaimer.

### https://poesys.net/sim/
**Observed:** Frames content explicitly as synthetic ("simulated customer," internal states "the company layer cannot see"). Cites real external references (Elexon NIV/SSP, National Grid weather baseline, "2021–22 crisis…forced 29 UK suppliers to exit the market"). Notably contains the phrase **"56-day Ombudsman SLC window."**

**Cross-check against prior #4:** 56 days = 8 weeks, matching my stated prior for the Energy Ombudsman escalation window under SLC. **This is internally correct and matches real regulatory practice** — a positive finding, not a defect. It confirms the underlying model has the right complaints-window figure encoded somewhere, even though I could not find the customer-facing complaints/Ombudsman signposting text itself (the Supplier page didn't render, see above).

### https://poesys.net/robots.txt
**Observed:** Blocks AI-training crawlers (GPTBot, ClaudeBot, Google-Extended, CCBot, Applebot-Extended, PerplexityBot, Bytespider) while explicitly allowing user-directed AI fetch (Claude-User, Claude-SearchBot) and a wildcard allow for everything else (standard search indexing). No disallowed paths suggesting exposed admin/internal panels were reported.

**Why checked:** Consistency check — nothing here contradicts entity naming elsewhere, and no obviously sensitive internal paths are being inadvertently disclosed via a `Disallow:` list (a common way admin surfaces leak). No compliance concern.

### https://poesys.net/privacy/ (guessed conventional path)
**Observed:** HTTP 404 Not Found.

**Why this matters:** No privacy policy exists at the conventional path, and none was linked from the homepage. Given the site publicly displays (or claims to display, pending the JS-rendering caveat above) synthetic "customer" records, a real production supplier site would carry a privacy notice regardless of whether the data is synthetic, if only to avoid visitor confusion about what's collected on the visitor's own visit (analytics, cookies, etc. — not verified either way here). **Classification: genuine gap**, low severity for a clearly-labelled research/demo site, but a real deficiency if this site is ever intended to be shown to external stakeholders as a production-representative artifact.

---

## 3. Cross-Check Against Stated Priors — Summary Table

| Prior | Verified on live site? | Result |
|---|---|---|
| #1 VAT rate correctness | Not verifiable (SPA didn't render) | Unresolved |
| #2 Back-billing 12-month cap | Not verifiable (SPA didn't render) | Unresolved |
| #3 No false Ofgem-licence claim | Verified | **Pass** — no licence claim found anywhere |
| #4 Ombudsman/complaints signposting | Partially verified | "56-day Ombudsman SLC window" language found on /sim/; not confirmed on customer-facing /supplier/ page |
| #5 Vulnerable customer / PSR reference | Not found on any fetched page | Gap (not confirmed present anywhere) |
| #6 Consumption plausibility | Not verifiable (SPA didn't render) | Unresolved |
| #7 Data protection / privacy notice | Checked, absent | **Gap** — /privacy/ 404s, none linked |
| #8 Disclaimer of simulated/non-real status | Verified, but only on /project/ and /sim/ | Present but not uniformly surfaced site-wide |
| #9 robots.txt sanity | Verified | **Pass** — boilerplate, consistent, no leaked admin paths |

---

## 4. Tooling Limitation (stated plainly, per instructions)

WebFetch was available and used throughout, but it converts fetched HTML to markdown without executing JavaScript. The `/customers/` and `/supplier/` pages are evidently client-rendered single-page apps that load their substantive content (customer records, tariffs, VAT, consumption, dashboard figures) after page load. As a result, **the single most compliance-relevant content class — actual customer/bill data — could not be observed or checked against priors #1, #2, and #6 in this review.** I am reporting this limitation rather than guessing or fabricating what that content might contain. A follow-up pass with a JS-capable browser tool (e.g., a headless browser) against `/customers/` and `/supplier/`, ideally drilling into any individual customer/bill detail view, is needed to close out those priors.

---

## 5. Findings Ranked (Genuine Defect vs. Reads-Wrong-But-Correct)

1. **[Reads-ambiguous, low-current-risk]** Homepage promotional register ("could go live," "shadow-live track record," "A UK energy supplier that builds and runs itself") is not accompanied by a blunt, plain-English "this is a simulation, not a real licensed supplier" statement on the same page — the actual disclaimer exists but is one click away on /project/. Recommend a persistent, unambiguous disclaimer banner site-wide, not just on /project/.
2. **[Unresolved — needs JS-capable follow-up, not a confirmed defect]** Could not verify VAT rate, back-billing cap adherence, or consumption-figure plausibility on any actual customer/bill record, because `/customers/` and `/supplier/` render via client-side JS that WebFetch cannot execute. This is the highest-value gap to close next, since it's the exact content class Ofgem SLC exposure would hinge on.
3. **[Genuine gap, low severity]** No privacy policy/terms page exists at the conventional `/privacy/` path and none is linked from the homepage footer, despite the site displaying (or appearing to display) customer-level data.
4. **[Positive finding]** No false or implied Ofgem-licensing claim found anywhere on the site — the /project/ page is explicit and clear that this is a simulation with no licence held.
5. **[Positive finding]** The "56-day Ombudsman SLC window" figure found on /sim/ matches the real 8-week Ofgem SLC complaints-escalation rule — correct, and consistent with my stated prior.
6. **[Unconfirmed, not found]** No Priority Services Register / vulnerable-customer-protection reference was found on any page fetched — worth a targeted check once the SPA content is reachable, since regulatory modules are otherwise claimed as extensively wired on /project/.
