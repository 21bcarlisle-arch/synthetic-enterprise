**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 2 · **Atom:** `SITE1_expert_doors`

# The Expert Hour on the live doors fails: published net margin runs to 55% and the arrears count reads the EBSS credit as debt (2026-11-11)

**What ran.** SITE1's done-means is "a genuine Expert Hour across all doors". The only Hour on record was
29 Jul, against a 19-account I&C-heavy book and a site IA that has since been folded. So this tick ran a
fresh one against the live site only. It was a blind fork with no repo, no build context and no earlier
verdict. Persona: 25-year UK domestic retail veteran. Priors before pixels. independence: false. It covered
eleven doors: the front, capabilities, harness, code, knowledge, explore and the five /model/ sheets. The
constitution's doors 3–8 URLs now 404, so "all doors" is read as the live nav.

**Verdict: FAIL.** 3 BLOCKER, 8 MAJOR, 5 MINOR. The full battery is in
`docs/design/simplifications/SITE1_expert_doors.yaml` under `map_records.expert_hour_findings` (the items dated 2026-11-11). The level
stays at 2.

**Why BLOCKING.** Two published figures are wrong, and the seat re-read both from the live feeds:

1. **Net margin.** `https://poesys.net/data/dashboard.json` gives `financial.annual[].net_margin_pct` of
   25.59, 19.82, 18.46, 29.81, 35.01, 2.01, −15.45, **54.91**, 29.09 and 18.7 for 2016–2025. The
   site's own /knowledge/price-cap/ says supply EBIT is "low single digits", and the reviewer's prior was
   −5% to +3%. `company.json` already names the likely root: £966,312 of non-commodity cost is "absorbed
   with no revenue recognition". The open standing-charge findings of 14 Oct and 9 Nov sit on the same
   seam. Read those before minting anything new.
2. **Arrears.** `https://poesys.net/data/company.json` gives `arrears.in_arrears` as 705 of 1,293 (54.5%),
   on `clock: billed_minus_banked`. That clock counts the £400 EBSS scheme credit as debt. In the
   reviewer's 150-account sample, 12% have a positive ledger balance, against 49% on this clock. Before
   any build, the measure needs defining (CLAUDE.md, "before measuring a thing, say what it is"). The
   published /knowledge/debt-and-collections/ page already quotes Ofgem's own definition. The producer is
   `tools/generate_company_data.py`.

**Routing for the rest (no new atoms minted; everything below stays with SITE1 unless named).**
- Book size that cannot be reconciled across four sources (B2), 2025 shown as a full year (M11), and
  counts that drift between doors (m12) stay on **SITE1_expert_doors** itself. SITE_EH3 (figure
  reconciliation and periods) would be their natural home, but it closed at its own target (L1 of 1), so
  re-opening it would be a new decision. Corrected before landing: an earlier draft called it parked.
- The publish-failing status shows only on /harness/ (B3). That is a site-lane fix: one status line on
  every door, naming the refused run.
- Build-state labels disagree across doors (M6), and no page renders data/company.json (M7). Both are
  site lane.
- Knowledge pages carry no primary-source hyperlinks (M8). Knowledge lane; K8 pages should link Ofgem,
  Elexon and NESO.
- `/code/` draws `simulation.customer_events → company.crm.churn_model` going round the wall (M9).
  This is not a new leak: the crossing is registered at `docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md`
  (the customer_events group, around line 312). What is new is that /model/wall/ reads "Live" with no
  pointer to it. That is a site-lane wording fix.
- The remaining findings are in the store record: M5, the seeded 2% bad debt; M10, an SVT label on a
  fixed tariff and 2017 bills low; m13–m16.

**Credited as strong.** Grid carbon by year falls inside the reviewer's prior. Crisis-year cap, EPG and
EBSS are right. Bills and ledgers reconcile. Refunds equal the credit held in the sample. The payment-method
mix is realistic. The knowledge pages are expert-grade. Failures are published rather than hidden.

**Figures 1 and 2 done (2026-11-11, the delivery lane).** Net margin is defined (supply revenue less
every cost the supplier bears, over that revenue) and WITHHELD: every `net_margin_pct` the dashboard
producer publishes is null beside `financial.net_margin_pct_status`, whose reason the page can print.
The annual rate divided the settlement net (no cost to serve) by the ledger's revenue, two books. The
management accounts' full-cost rate is a quantity, but it reads 20-31% in normal years against a
published 2-5%. It rests on the standing-charge seam (findings of 14 Oct and 9 Nov), which W3_3 holds
paused. The insights headline published the same two-book rate (22.9%) and is withheld too. Arrears now
uses Ofgem's definition: a bill still owed more than 91 days past its due date, read from each bill's
own `outstanding_gbp`, so the EBSS credit is never owed. That gives 50 of 1,293 on the 0a6391d18 ledger,
against the old 705. The control is
`tests/tools/test_the_published_margin_rate_and_arrears_count_are_defined_or_withheld.py`. It reds on
the feeds as they stood. The live site changes at the next publish. BLOCKER-2, BLOCKER-3 and the
remaining items stay open on SITE1.

**What retires this.** The published net margin and in_arrears either sit inside a stated plausibility
band with a named definition, or are withheld with the reason on the page. After that, a fresh blind Hour
on the live doors returns no BLOCKER.

## Reverse

Delete this file, and revert the SITE1 map row's two lines and the store's two appended keys.
