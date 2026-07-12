# Cold-Eyes Competitor Intelligence Review — poesys.net
**Persona:** Competitor Intelligence Analyst, rival UK energy supplier
**Date of review:** 2026-07-12
**Method:** Fresh-context, blindfolded — no repo access, WebFetch only against live URLs
**Tool caveat:** WebFetch converts HTML to markdown via a small model; it does not execute client-side JavaScript. Several pages/sections rendered as empty shells or "Loading…" placeholders. Where I could not reach the underlying data through the rendered page, I guessed likely JSON data-file paths (a real analyst would do the same via browser dev tools) and several resolved successfully — those are cited explicitly as "endpoint" evidence rather than "page" evidence, since the distinction matters for what a casual visitor vs. a determined analyst actually sees.

---

## 1. Stated priors (written BEFORE fetching anything)

- **Churn:** UK energy retail annual churn/switching typically ~15–20%/yr in a competitive market (lower in crisis years when switching effectively froze, 2022–23).
- **Net margin:** Thin. Ofgem's price-cap supplier-margin assumption is typically 1–3% of revenue in normal years; can be negative in crisis years (2021–22 wiped out ~30 suppliers on exactly this basis).
- **CLV:CAC:** A healthy ratio in a low-differentiation, thin-margin retail business is roughly 3:1–5:1. Anything double-digit should be treated as marketing fiction, not underwriting.
- **Customer concentration:** A retail supplier's book should be broad; >20–25% of revenue from a single account is a real risk-disclosure item, not a footnote.
- **Retention/save-rate:** Real retention-desk save rates run well under 100% — 30–60% is typical. A reported 100% save rate on every retention attempt is a red flag for either a toy sample size or a model that doesn't simulate genuine attrition pressure.
- **AI-built velocity claims:** I'd find credible: steadily increasing test counts over weeks/months, phases that sometimes fail or get reverted, visible defect/retraction history. I'd find suspicious: perfectly clean pass rates, no disclosed failures, round/inflated headline numbers, or numbers that move between "N" and "N+300%" depending which page you land on.
- **Internal consistency bar:** Any figure repeated on two+ surfaces (site pages, or the JSON feeding them) must match, or be reconcilably close (rounding, different as-of dates). A same-week same-metric figure that differs by an order of magnitude is a genuine, not cosmetic, defect.

---

## 2. Page-by-page findings

### https://poesys.net/ (homepage)
**Seen:** "449+ modules," "15,000+ tests," settlement against real Elexon/NESO data "since 2016," narrative that ~30 real UK suppliers failed in the 2021-22 crisis and this one "survived," self-description as "a running" company "built from first principles with AI as the company," claims of publishing predictions before results arrive and catching defects "the day it's introduced." No customer count, revenue, or margin disclosed here.
**Doubt:** "15,000+ tests" and "449+ modules" are exactly the kind of unverifiable, precision-flavoured-but-round headline numbers a rival would want to pressure-test against the underlying data feed (see §3 — they don't hold up well). The "we survived what killed 30 real suppliers" framing is a strong claim for a business that (per the data endpoints, below) has a book of ~11 customers.

### https://poesys.net/customers/
**Seen:** Nothing. Fetched page renders only nav chrome and copyright — no customer counts, churn, retention, CLV, or CAC content at all.
**Doubt / caveat:** This is the one page most directly relevant to the growth/CAC/CLV story, and it is the emptiest. I cannot be certain whether this is (a) a genuine gap — no server-rendered fallback for an investor-facing page, meaning bots, crawlers, screen readers, and share-preview generators see nothing — or (b) purely an artifact of WebFetch not executing the JS that populates it. I flag this as **unresolved but load-bearing**: a rival analyst using anything less than a full JS-rendering browser (many due-diligence/monitoring tools don't) would conclude this company discloses zero customer economics. Given the CLV/CAC story is central to the persona's brief, its complete invisibility to a standard fetch is itself the headline finding for this page, caveat included.

### https://poesys.net/method/ (+ #track-record, #retro-list)
**Seen:** Governance narrative (one human principal, two AI roles, tiered approval, R1-R6 rules), a retrospective cadence ("roughly every 50 phases or two weeks"), infrastructure stack (Claude Code orchestrator, qwen3:14b/Ollama local generation, consumer Intel/RTX hardware, Cloudflare Pages hosting), project start date 7 June 2026. The "Track Record" and "Forging Incidents" (retro-list) sections — the two sections that would actually contain falsifiable evidence (predicted-vs-realised grading, named incidents/defects) — both render as "Loading…" with no content delivered to a static fetch.
**Doubt:** The page's entire pitch is "radical transparency, verify us by our own failure log" — but the two sections that would let an outsider verify that pitch are exactly the ones that don't render. For a company whose marketing angle is "check our track record," having the track record itself be the least accessible content is a genuine irony a rival would use: "transparent" but the evidence trail requires a full browser and isn't linkable/quotable/archivable as a static artifact.
**Note on credibility of the stack claim:** consumer-grade hardware (i5-13400F/RTX 3060) + a small local model (qwen3:14b) doing "code generation" is at least an internally coherent, modest claim — this reads as more credible than a company claiming enterprise infrastructure, so I'd score the "how it's built" story as plausible on its own terms, not oversold.

### https://poesys.net/project/
**Seen:** Timeline claims (settlement data 2016-2025, FiT closure April 2019, CCL spike April 2019, 2021-22 crisis, post-2022 FRA capital rules), roadmap of three products (Method / Synthetic data / Platform), Epoch 2 in "four movements... M4 strictly last," explicit statement that **"every headline figure on this site is PROVISIONAL until [M4] lands,"** "62 regulatory modules... wired," "10 SLC domains," quarterly narrative letter described as "not yet written — honestly empty," M4 replay described as "genuinely not started." Crisis-survival narrative ("treasury drawdown, churn spike, and recovery") given with **no supporting numbers** on this page.
**Doubt:** The explicit "every headline figure... is PROVISIONAL" disclaimer is unusual to see stated this plainly, and it cuts both ways for a rival analyst: it's honest, but it also means the site is publishing marketing-facing "headline figures" (margin, test counts, module counts) while itself flagging them as not-yet-final — which undermines using any of them as decision-grade evidence in a competitive comparison. A rival would note this explicitly in a dossier: "subject's own site disclaims its published numbers."

### https://poesys.net/platform/
**Seen:** One quantified claim — "~20+ SaaS categories a real UK energy supplier assembles to run its business" (market-structure context, not a claim about this company). Financial/risk sections show "Loading…" placeholders; no hedge, margin, or portfolio data delivered to a static fetch.
**Doubt:** Same rendering gap as customers/track-record — the pages that should carry the platform's actual financial substance are JS-gated. Nothing to specifically doubt on content grounds since there was effectively no content delivered.

### https://poesys.net/sim/
**Seen:** 2016-2025 point-in-time market/weather data, UK Grid 15.5°C HDD base, named historical episodes (Rough storage closure 2017, "Beast from the East" Feb-Mar 2018, Dec 2022 crisis), customer behavioural model with four dimensions, switching-stress multipliers (LOW ×1.10, MODERATE ×0.85, HIGH ×0.65), bill-shock threshold (>20% unit-rate rise at renewal), **"Complaints in portfolio: 13 across the full decade."**
**Doubt:** 13 complaints across a full decade is a very low complaint volume for any real supplier, but is at least dimensionally consistent with a ~11-20 customer toy-scale book (see §3) — flagged as internally-plausible-given-scale rather than a standalone red flag.

### https://poesys.net/simplified/
**Seen:** No numbers at all — a plain-English positioning page: the company publishes "every known gap, cut corner, and deferred build decision" as a register, unfiltered, rather than curating for marketing.
**Doubt:** Consistent, on its face, with the "provisional headline figures" disclaimer found on /project/. Reads as intentional positioning rather than a defect.

### Data endpoints discovered by guessing likely paths (not linked directly from rendered pages, but resolve on the live host)
I attempted this because the rendered pages themselves were largely empty shells on the growth/financial questions central to the brief; a determined rival analyst would do the same (view-source / network tab). Results below feed the cross-check in §3.

- `/data/sim_data.json` — wholesale market data (not business metrics): monthly/annual/daily electricity price series 2016-2025, peak record €4,037.80/MWh (9 Sep 2021), crisis flag 2021-2022.
- `/data/system_status.json` — session/build-activity log: 27 sessions logged 11 Jun–9 Jul 2026, "158 unknown-restarted exits vs. 2 completion exits," longest session 4,754 minutes, daily "commit burn" 5–400 units, peak 400 (30 Jun).
- `/data/capabilities.json` — a phase-close snapshot (phase "TA," generated 2026-07-10T00:05:19Z): 12 dashboard modules/cards, 23 regulatory obligations tracked (18 green), 5 customer segments, **1,588 bills settled**, **11 active customer accounts (as of 2025)**, **5 churn events across the whole simulation run**, 26 bill-shock incidents in 2025 (worst case 80.4%), **12 retention offers made, all 12 retained**, **Net Margin £1,524,167**, **Gross Margin £6,431,113**, average hedge fraction 88% (2025), and a disclosed churn-model quality metric of **"recall 0%, precision 0%, F1 0%" in live operation** (60% at episode level).
- `/data/phases.json` — build-velocity data: **"Total Tests: 3,305 (as of 2026-07-12)"** as a summary figure, but the phase-by-phase table it's built from runs through **11,100 tests on the most recent row (phase KH, dated 2026-07-12 — the same date as the summary figure)**; 510 total phases; ~24 phases/day average over a 21-day window; peak 133 phases in a single day (26 Jun 2026); ~157 tests/day average growth rate.
- `/state/live_portfolio.json` — per-customer ledger: 11 active customers (6 residential electric, 2 residential dual-fuel, 4 I&C), **2025 net revenue £118,352.06**, **treasury £3,827,153.05**, largest single customer (C_IC1) contributing **£63,404.31** — roughly 54% of total 2025 net revenue from one account — I&C segment as a whole ~99.8% of 2025 net.
- `/data/agent_status.json` — a different financial snapshot entirely: **treasury £11,131.00**, **net margin −£8,317.21**, **enterprise value −£20,661.90**.

---

## 3. Cross-checks — figures appearing on more than one surface

| Metric | Surface A | Surface B | Surface C | Consistent? |
|---|---|---|---|---|
| Test count | Homepage: "15,000+ tests" | phases.json summary: "3,305" | phases.json's own latest table row (same date, 2026-07-12): 11,100 | **No.** Three different numbers, one of them (3,305) an order of magnitude below the homepage's headline claim, and the endpoint contradicts itself between its own summary stat and its own most recent table row. |
| Treasury (cash position) | capabilities.json (phase TA snapshot): not stated directly, but Net Margin £1,524,167 implies a healthy-margin business | live_portfolio.json: **£3,827,153.05** | agent_status.json: **£11,131.00** | **No.** A ~344x spread between the two explicit treasury figures, both apparently current as of early-mid July 2026. |
| Net margin | capabilities.json: **+£1,524,167** | agent_status.json: **−£8,317.21** | live_portfolio.json (2025 net revenue, not margin, but the closest comparable): £118,352.06 | **No.** Sign flips between two of the three surfaces; the third figure (revenue, not margin) is itself ~1.3% of the "gross margin" figure quoted on a different surface, and ~7.8% of the "net margin" figure quoted on the same date — revenue smaller than margin is not physically possible if these are describing the same book. |
| Customers who survived vs. book size | Homepage: framed against "30 real UK suppliers" failing in 2021-22 | capabilities.json / live_portfolio.json: **11 active customer accounts** | — | **Reads wrong even if internally correct.** A book of 11 customers is not the scale at which "surviving what killed 30 real suppliers" is a meaningful claim — this is the single biggest gap between narrative register and disclosed scale. |
| Retention / bill shock | capabilities.json: 26 bill-shock incidents in 2025 (worst case 80.4%) alongside 12/12 retention saves | — | — | **Internally implausible.** An 80.4% bill-shock event with a 100% save rate, across a book this small, is not consistent with any real-world switching/attrition behaviour I'd expect — either the retention-offer sample never overlapped with the worst bill-shock cases, or the churn model doesn't yet simulate genuine attrition pressure (which the site's own disclosed "F1 0%" churn-model metric supports). |
| "Every headline figure is PROVISIONAL" (/project/) vs. precise-to-the-penny figures published elsewhere | /project/: explicit disclaimer | capabilities.json, live_portfolio.json, agent_status.json: figures stated to the penny (e.g. £63,404.31, £11,131.00) | — | **Tension, not a hard contradiction** — but worth flagging: precision-to-the-penny reporting alongside a blanket "provisional" disclaimer is the kind of thing a rival would quote back as "which is it?" |

---

## 4. Comparison against stated priors

- **Churn (~15-20%/yr expected):** Cannot be tested at this population size. 5 churn events against an ~11-20 customer book over up to a decade is nowhere near a 15-20%/yr rate — the disclosed churn behaviour is far stickier than real UK retail energy, though the population is too small (n≈11) for the comparison to be statistically meaningful either way. Flag as "unrealistically low churn, but sample too small to be sure it's a modelling defect vs. just a tiny book."
- **Net margin (1-3% of revenue expected, UK Ofgem norm):** Cannot reconcile — the three margin/treasury figures I found don't agree with each other, let alone let me compute a margin-on-revenue ratio with any confidence. The one clean pairing I do have (live_portfolio.json: revenue £118,352 vs. capabilities.json: gross margin £6,431,113) implies gross margin >5,400% of revenue, which is nonsensical if both describe the same book — strongly suggests these are snapshots from different runs/scopes/dates being surfaced side-by-side without a shared as-of label a visitor can use to reconcile them.
- **CLV:CAC:** No CLV or CAC figure was disclosed anywhere I could reach (the one page that should carry it — /customers/ — was empty). Cannot assess against my 3:1-5:1 prior; the absence itself is the finding.
- **Customer concentration:** Confirmed as a real, disclosed issue — ~54% of 2025 net revenue from a single I&C account, ~99.8% from the I&C segment as a whole. Matches my prior expectation that this would be a legitimate risk-disclosure item, and it is at least present in the data (even if not surfaced narratively).
- **AI-build velocity claims:** The disclosed velocity (24 phases/day average, 133 in one peak day, ~157 tests/day) is fast enough that I'd want proof of review depth before crediting it as sustainable engineering rather than a metric that inflates its own denominator (e.g., what counts as a "phase"). Combined with the test-count self-contradiction above (3,305 vs. 11,100 vs. "15,000+"), I'd score the velocity/test narrative as **oversold relative to what its own data supports**, which matches the "suspicious" bucket in my priors rather than the "credible" one.

---

## 5. Internally-correct-but-reads-wrong vs. genuine defects

**Genuine defects (numbers actually contradict each other on the same subject, same rough date):**
1. Net margin sign flip and ~£1.53M swing between capabilities.json and agent_status.json.
2. Treasury figure off by ~344x between live_portfolio.json and agent_status.json.
3. Test-count figure appearing as 15,000+ (homepage), 3,305 (phases.json summary), and 11,100 (phases.json's own latest row) — three numbers, same claimed subject, overlapping dates.
4. Gross margin (£6.43M) vastly exceeding total disclosed revenue (£118k) for what appears to be the same book.

**Reads wrong but plausibly just a framing/scale mismatch, not a fabricated number:**
1. "Survived what killed 30 real suppliers" narrative next to an 11-customer book — the number itself may be accurate for a deliberately small/early-stage simulation population; the *narrative register* is what overclaims relative to that number, not the number itself.
2. 13 complaints across a decade — low, but plausible given the tiny population; not evidence of manipulation.
3. Precision-to-the-penny figures next to a "provisional" disclaimer — a genuine tension for messaging purposes, but not proof either figure is wrong.

**Unresolved (tool limitation, not a scored finding):**
1. /customers/, /platform/, and /method/#track-record all render empty/"Loading…" to a non-JS fetch. I cannot tell from here whether a real browser would show reconciling, consistent content, or whether the emptiness itself is the defect (no SSR fallback for investor-facing pages). Recommend a rival analyst (or the site's own operators) verify with a JS-executing browser before treating this as either exonerating or damning.

---

## 6. Top-line takeaway for a rival dossier

The single most usable line for a competitor to quote: **this site publishes at least three mutually-exclusive financial snapshots of the same company (net margin +£1.52m vs. −£8.3k; treasury £3.83m vs. £11.1k) without a shared as-of date reconciling them, and its own "total tests" headline figure (15,000+) is roughly 35% above the most recent number in its own underlying data feed (11,100) and over 3x its own summary stat (3,305) on the same page.** Everything else — the tiny/concentrated customer book, the 100%-save-rate-despite-80%-bill-shock churn story, the disclosed 0% F1 churn model — is corroborating colour, but the cross-page financial and test-count contradictions are the load-bearing finding: they're checkable facts, not interpretation, and they don't currently agree with each other.
