# [PLANNER-MINTED] Emit the per-customer ARREARS-£ balance distribution (SIM-emission BUILD) (2026-07-24)

> **STATUS (2026-07-24, worker tick): BUILT — steps 1–4 landed; R11 live-pixel verify PENDING next publish.**
> The arrears-£ distribution is emitted as a sibling of cost-to-serve inside `company.json`
> (`tools/generate_company_data.py::_arrears_distribution`) — per-customer arrears = total billed − total
> banked from the company's OWN `billing_ledger.json` (through-the-wall observable, no sim internals),
> aggregated min/median/max + gross-exposure FLOOR + in-arrears/in-credit/square counts + by_segment /
> by_payment_channel / by_tenure, with RC7 floor-not-figure framing and a missing-lines enumeration.
> Rendered behind the `/company` finance drill-down (element `arrears-dist`, never a lead slot — RC7 wall).
> Wired automatically (the generator is already in `process_run_complete`'s regen cycle, line ~938).
> R15 both-ways + R11 render-harness tests: 9 generator-side (`tools/test_generate_company_data.py`) +
> 4 render-side (`site/company/test_company_door.py`) — all green (38 in the door suite, 326 in site/).
> R11 verify-to-the-rendered-value on the DEPLOYED surface remains pending the next publish.
>
> _(prior status:)_ **RULING-CHECKED CLEAN + FRAME sufficient — READY FOR NORMAL BUILD DRAW.**
> Ruling-checked against the 2026-07-24 rulings: RC7 / FRONT_MISSION_BLOCK respected (no cohort-£ leads; arrears
> appears only behind a /company or /proof drill-down with N + floor-not-figure framing + missing-lines) — this is
> the compliant sibling of the segment-efficiency-£ mint that was correctly closed NO-BUILD for leading. Serves a
> real, still-open named campaign item (SITE_MODEL_SPINE §C remainder). The step-1 FRAME (settlement→bill→payment→
> arrears chain; through-the-wall observable = Σ(bills issued) − Σ(payments received) per customer from the
> company's OWN ledger; diff vs the cost-to-serve emission) is complete in this doc. NOT built this tick: the BUILD
> is a real core SIM-emission increment (generator + regen wiring + site panel + R15/R11 tests) — a serial BUILD-
> lane draw, deliberately NOT opened at a site-lane tick's tail (no wide/tired build front). Left drawable in
> staging root for the next BUILD draw; the ruling-check need not be repeated.

**Type:** RUNG-7 planner mint (WORK_IS_THE_DEFAULT 2026-07-23, rung 7 — rungs 1–6 empty this tick). **Propose-then-proceed.** Minted from a ratified open-campaign remainder, ruling-checked against the 2026-07-24 rulings before minting (RC7 / FRONT_MISSION_BLOCK).

## Ratified goal / campaign follow-on served
- **`DIRECTOR_CAMPAIGN_SITE_MODEL_SPINE_2026-07-23.md` (in_progress), §C remainder — verbatim:** *"Only remainder: the §C arrears-£-per-customer DISTRIBUTION — a SIM-emission BUILD (threading an arrears-£ balance through the settlement→export→generator chain), which belongs in the normal BUILD draw."* This is the campaign's own named, still-open item — it does NOT live in the front-door fold (§A, discharged) and was explicitly deferred to a normal BUILD draw. This mint is that draw.
- **DIRECTOR_AXES §2 (Segmentation → Efficiency):** *"value per segment (cost-to-serve vs value; activity-based)."* Arrears exposure is a real cost-to-serve dimension that varies sharply by payment channel / tenure / segment (a real UK supplier's bad-debt provision is segment-structured). The existing cost-to-serve distribution (£219.95 / £505.43 / £4,218.12 min/median/max; by_segment / by_payment_channel / by_tenure — already live on /company) is the exact analogue and the template to mirror.

## Real-world fidelity gained
A real UK supplier carries a customer-level arrears/aged-debt ledger and provisions against it; bad debt is one of the largest cost-to-serve line items and is heavily segment-shaped (std-credit and pre-2-year tenure carry materially higher arrears than DD). The sim currently emits cost-to-serve per customer but **no arrears-£ balance distribution** (verified 2026-07-24: no `arrears` feed under `site/data/`; the campaign doc names it unbuilt). Emitting a per-customer arrears-£ distribution — from the company's OWN billed-vs-received ledger — makes the segmentation-efficiency picture whole and gives the veteran smell-test a number it expects to see.

## Scope (propose-then-proceed, reversible half proceeds)
1. **FRAME (draw now, doc-only):** name the settlement→bill→payment→arrears chain and the exact through-the-wall observable the company may use — arrears = Σ(bills issued) − Σ(payments received) per customer, from the company's own invoice + payment ledger (`tools/generate_invoice_data.py`, `tools/generate_payment_ledger_data.py`), NEVER from any sim-internal churn/hardship truth. State the diff vs the cost-to-serve emission (the working analogue, R4).
2. **BUILD (reversible):** a generator emitting `site/data/arrears_distribution.json` — per-customer arrears-£ balance, aggregated min/median/max + by_segment / by_payment_channel / by_tenure, mirroring the cost-to-serve schema; wired into the `process_run_complete` regen cycle.
3. **SITE render (reversible):** surface it as a /company (or /proof) drill-down panel — **RC7 WALL: no cohort-derived £ may LEAD any page** (`DIRECTOR_RULING_FRONT_MISSION_BLOCK` / `IDEA_FIRST_EXTERNAL_REGISTER`) — so it appears behind a drill-down with N, the floor-not-figure framing, and its missing-lines enumeration, never in a lead slot.
4. **R15 both-ways + R11 live-pixel:** render-harness test executes the page's real JS against the published JSON (assert the rendered arrears figures) + mutation flips a balance and the panel changes; verify on the DEPLOYED surface after the next publish (R11 — data stamp AND rendered value).

## Walls named (untouched — director-reserved)
- **R14:** every arrears figure carries its basis clock (billed vs settled vs banked) — a basis-less arrears number is a defect (`generate_dashboard_data.py` gate).
- **R12:** arrears is a DIAGNOSTIC, never a target — no tuning any parameter toward a plausible arrears band.
- **Epistemic wall:** the company reads only its own bills/payments ledger; no sim-internal hardship/churn truth crosses. Coupled-triad: this is the COMPANY's belief; the belief-vs-truth GAP vs the sim's true arrears is a separate HARNESS measure, out of scope here.
- **C-S4:** durable state behind the append-only ledger interface; storage form swappable.

## Propose-then-proceed window
Standard: this doc becomes RUNG-1 staged work the next tick draws. Steps 1–4 are fully reversible (new feed + new panel + tests; git reverts) → proceed under standing reversible authority per PROCEED_BY_DEFAULT; no wall in the list above requires a director act. Per the 2026-07-24 waiver precedent the director may waive the wait; absent that, the next draw takes it.

— RUNG-7 planner, 2026-07-24 worker tick.
