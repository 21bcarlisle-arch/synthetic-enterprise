**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `the-annual-report-publishes-one-shock-field-a-hundredfold-apart-and-ignores-the-split-that-supersedes-it`

# PRE-REGISTRATION — the annual report's bill-shock field, its band, and its RAG

**Filed: 2026-09-02, delivery seat, BEFORE any of the measurements below were run.** RECORDED
rather than BLOCKING: the MAJOR defect this pre-registers against — one stored field published a
hundredfold apart in one document — was repaired and landed in the same stretch, and the graded
results are below. This document is the experiment's design, kept because a prediction filed after
the answer is not a prediction.
**Subject:** `saas/reporting/annual_report.py` — `_section_service_quality`,
`_section_bill_shock_analysis`, `_year_narrative`, `_year_operational_lines`.

---

## What is already established (no prediction needed — read off the artefacts)

1. `data["years"][yr]["avg_bill_shock_pct"]` (annual_report.py:630) is a **FRACTION**. The served
   `site/data/dashboard.json` says so in its own sibling field
   (`avg_bill_shock_pct_population`: *"It is also a FRACTION despite the `_pct` name"*).
2. The published `docs/reports/ANNUAL_REPORT.md` renders that one field two ways, 1,176 lines
   apart: `Worst bill shock: **2022** (0.58%)` (line 2447, no scaling) and
   `| 2022 | 57.5% | ... |` (line 3613, ×100). A hundredfold apart, same run, same document.
3. `docs/market_research/BILL_SHOCK_EVENT_TYPES_ANCHORS.md` §3, verbatim: *"Formal Ofgem 'bill
   shock' definition — does one exist? **Confirmed: no.** Multiple targeted searches … returned no
   formal Ofgem definition of 'bill shock' as a term, threshold, or comparison basis."*
   The report attributes a three-band RAG to Ofgem anyway (line 2430) and calls Ofgem a monitor of
   bill shock (line 3607). **Our own commons refutes both attributions.** This is not a prediction;
   it is a citation, and it settles defect (iii) without a research pass.
4. `tools/generate_dashboard_data.py:1475` records the frame that supersedes the mixed mean:
   `SHOCK_DEFINITION_POPULATION = "bill"` — standard credit is *the only* population for whom the
   difference between two bills is the quantity the definition names. `"payment"` (level DD, ~74%
   of GB) is `UNMEASURABLE_SHOCK_POPULATION`: its bill-to-bill difference is published under its
   own name and **explicitly not as a shock**.

## The predictions (answers not known when this was written)

**P1 — reachability of the shock RAG on the MIXED quantity.** Against the ten-year real series,
`ServiceQualitySnapshot.bill_shock_rag` fed the mixed `avg_bill_shock_pct` returns **RED in all ten
years**. Its GREEN and AMBER branches are unreachable on this book, so the verdict carries no
information. *Refuted if any year is GREEN or AMBER.*

**P2 — reachability on the CORRECTLY DEFINED (`bill`, standard-credit) population.** Against the
same band, the `bill` population's own mean is **not** RED in all ten years — at least one year
falls below the 0.20 AMBER edge, and at least one is at or above the 0.30 RED edge. That is, the
band's other branch IS reachable once the quantity is the one the definition names. *Refuted if the
`bill` population is also single-valued across the decade.*

**P3 — the two published figures reconcile.** `0.58` (the mixed fraction) × 100 equals the
`mixed_all_population.avg_pct` the dashboard publishes for 2022, to within rounding. If they do not,
the two renderings are reading different populations as well as different units, and the units
repair alone would not close it. *Refuted if they differ by more than 0.1pp.*

**P4 — the `or 0.0` defaults are reachable on this book.** At least one year × population cell has
no computable shock, so the `or 0.0` at lines 7123 and 9020 would publish a measured zero for an
unmeasured cell. *Refuted if every year of the real series has a computable shock in every
population — in which case the defect is latent, not live, and I will say so rather than claim a
catch.*

## What I will do with each answer

- P1 confirmed → the shock leg is **withdrawn** from the service-quality RAG, said so on the page,
  not silently dropped. P1 refuted → keep it and record that I was wrong here.
- P2 confirmed → the band is reachable in both directions *on the right quantity*, so the report
  publishes the `bill` population's mean against it, with its n and its bootstrap interval, and the
  band is labelled **as this project's own working band with no regulator behind it**.
  P2 refuted → the band is withdrawn entirely and the report publishes the figure unbanded.
- P3 refuted → stop, and re-scope: the defect is larger than units.
- P4 either way → the defaults fail closed regardless (an unmeasured cell prints `n/a (n=0)`), and
  the prediction records whether that repair was live or precautionary.

---

## GRADED, 2026-09-02, after the measurement and before the fix landed

Subject: `docs/reports/run_output_88eec0eed_20260902T002118Z.json` — **the artefact the published
`docs/reports/ANNUAL_REPORT.md` was rendered from**, identified by matching its stored figures to
the published ones (2018 `0.30915…` → "30.9%"; 2022 `0.57518…` → "57.5%" and "0.58%"). The
committed `docs/reports/run_output_latest.json` is a *different, older* run and its bills carry no
`payment_channel` or `bill_shock_population` at all — every population reads `unknown` — so it
cannot test P2. That is recorded because it nearly produced a wrong grade: run first against
`run_output_latest.json`, P2 came back "unmeasurable" and P1 came back **refuted** (mixed RAG AMBER
in 2025, RED in the other nine). Both were artefacts of grading against the wrong run.

| | Verdict | Evidence |
|---|---|---|
| **P1** — mixed RAG constant | **CONFIRMED** | RED in all ten years. GREEN and AMBER both unreachable. |
| **P2** — band reachable on the `bill` population | **CONFIRMED** | 2018 → 16.9% (within band), 2020 → 24.7% (ELEVATED), the other eight → HIGH. Both directions, as predicted. |
| **P3** — the two published figures reconcile | **CONFIRMED** | 2022: `0.5751884…` × 100 = 57.5188, vs the dashboard's `mixed_all_population.avg_pct` of 57.5. Within rounding. The defect is units, not populations. |
| **P4** — `or 0.0` defaults live on this book | **CONFIRMED** | `out_of_scope` n=0 in all ten years; `unknown` n=0 in five (2021–2025). Fifteen live cells would publish a measured zero and band as "below 20%". |

**One clause of P1 needs qualifying rather than claiming.** "RED in all ten years" is a property of
*this book*, not a theorem about the band: on the older `run_output_latest.json` the same band gave
AMBER for 2025. So the shock leg's other branches are not unreachable *in principle* — they are
unreachable on the record this report publishes. That is still enough to withdraw the leg (a
verdict that has never moved across a decade carries no information), but the reason stated in the
code and on the page is the one the evidence supports, not the stronger one.

**A second constant verdict was created by the fix and is disclosed, not hidden.** Removing the
constant-RED shock leg left a two-leg RAG that is GREEN in all ten years — clarity never below
0.82, complaints never above 5%. That is the same defect facing the other way and it would read as
an achievement. The report now computes whether its own verdict is single-valued across the years
shown and says so on the page when it is, and
`test_the_constant_verdict_note_is_absent_when_the_rag_actually_moves` holds the other direction so
the disclosure cannot become a hardcoded sentence.

## The control this earns

One mutation-proven test in `tests/saas/`, keyed to the **property** — *every bill-shock figure the
report renders is in the same units as the `%` sign next to it, and no rendered figure is the mixed
mean presented as a shock* — never to "2022 is the worst year" and never to today's numbers.
