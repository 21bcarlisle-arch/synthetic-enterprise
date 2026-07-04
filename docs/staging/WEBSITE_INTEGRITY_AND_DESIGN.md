[PROJECT] Website: professional corporate quality + permanent freshness. Data integrity first -- the site currently contradicts itself on one page.

EVIDENCE (advisor fetch of poesys.net/shadow/, generated 2026-07-04T08:35): one page shows THREE data vintages simultaneously --
- Header: "Phase OL | 15,148 tests" (days stale; current is QB / 15,319+)
- 10-Year Totals: CORRECT current data (net GBP1,445,258, 1,605 bills, 14 retention offers)
- Executive Summary directly below: CONTRADICTS the same page -- "Net margin -GBP8,317 (0.0% of revenue)", "Hedging added GBP0", "0 bill shock events", "1,117 bills", "service quality 0.000/1.0", "risk committee 323 interventions, 0 in crisis". These are zeroed/stale insight-generator outputs sitting next to correct totals.
Rich's verdict on the live site: out-of-date info, homegrown feel, not professional corporate software. He is right, and the contradiction above is worse than ugly -- it destroys trust in every number on the site.

PART A -- DATA INTEGRITY (do this first, it is the actual disease):
1. SINGLE SOURCE OF TRUTH: every surface (live SPA sections, shadow pages, dashboard JSON, exec summary/insights) renders from ONE canonical run artifact per run, stamped with run_id + generated_at + phase + test_count. No surface may mix vintages. If the insight generator reads a different file than the totals generator, that ends now.
2. FIX THE EXEC SUMMARY: diagnose why insights emit zeros/-8,317 while totals are correct (reading an old run_output? empty field defaults? separate stale file?). Fix at root, not by hiding the section.
3. CONSISTENCY GATE: after site generation, an automated check compares headline numbers (net margin, bills, retention, interventions, phase, tests) ACROSS surfaces (dashboard vs shadow vs PROJECT_STATE.txt vs exec summary). Mismatch = generation fails loudly / NTFY, never ships silently.
4. FRESHNESS STAMP: every page footer shows run_id + generated_at + phase. Stale-vintage headers (e.g. "Phase OL") regenerate from the canonical artifact, never hardcoded.
5. CONTENT AUDIT: sweep all four sections for dead/stub/hardcoded/old-phase content; everything either regenerates per run or is explicitly marked static-by-design.

PART B -- PROFESSIONAL DESIGN SYSTEM (after A):
6. One coherent design system across all four sections + customer portal: consistent nav, typography, spacing, palette, components (KPI cards, tables, RAG chips), responsive. Target feel: enterprise SaaS / corporate energy supplier -- clean, restrained, data-dense, boring-in-a-good-way. Not a hackathon dashboard. CC chooses the implementation (static generation preferred for reliability); consistency matters more than framework.
7. CUSTOMER PORTAL to proper billing/CRM standard: per-fuel presentation everywhere -- electricity and gas as SEPARATE legs (C4 and C4g each with own consumption, tariff, invoices, P&L) with combined view as an optional roll-up, never the only view. Invoice history, payment history, arrears status per account from billing_ledger.json.
8. Shadow mirror stays in lockstep: same canonical data, same generator pass, plain HTML.

PART C -- PERMANENT FRESHNESS:
9. Every run regenerates ALL surfaces from the canonical artifact as one pipeline step; the consistency gate (A3) runs every time; freshness stamps visible everywhere. This is standing infrastructure, not a one-off polish.

ACCEPTANCE (per consumer-verified-done rule): advisor fetches shadow pages + state JSONs and confirms all headline numbers agree with each other and with PROJECT_STATE.txt, freshness stamps current, exec-summary contradiction gone. Rich reviews the live site visually for the corporate standard. Report with URLs + the consistency-gate output, not a done claim.
