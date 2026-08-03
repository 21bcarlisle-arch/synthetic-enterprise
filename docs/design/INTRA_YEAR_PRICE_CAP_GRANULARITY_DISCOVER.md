# DISCOVER — Intra-year Ofgem price-cap granularity (`expert_hour:W3_1_price_cap_binding`)

> ## STATUS 2026-08-03 — BUILT (`W3_1b_intra_year_price_cap_granularity`, L0→L2)
>
> The recommendation in §0/§5 was taken: the cap-window table is built and both clamps are re-threaded.
> Sourcing artefact: `docs/market_research/ofgem_cap_windows.md`. Tests:
> `tests/company/pricing/test_intra_year_cap_window.py` (15) + 3 rewritten in
> `tests/simulation/test_hedged_settlement.py`; 8 mutations each fire their own named test.
>
> **THREE ERRORS IN THIS DOC WERE FOUND BY BUILDING IT.** They are corrected inline below and recorded
> here because the pattern is now recurring (cf. `SP2_1_working_day_calculator`, whose closed DISCOVER
> undercounted its callers and specified its interval backwards): **a closed DISCOVER doc is a
> hypothesis, not a specification.**
>
> 1. **§1b named ONE binding site; there are TWO.** `simulation/run_phase2b.py:1115` also clamps resi
>    *fixed* terms, on `int(term_start_str[:4])` — the same year-keyed defect. Building to this doc alone
>    would have left half the class open, which is precisely what R10 forbids. Both are now re-threaded
>    and a source-scan control forbids either regressing.
> 2. **§2/§Sources cited `pricecaprates.co.uk` as the schedule source. Its effective dates are wrong.**
>    It dates cap changes to 1 Jul 2019 and 1 Feb 2021 that Ofgem dates to 1 Apr 2019 and 1 Apr 2021, and
>    it omits the Oct-2019 (£1,179) and Oct-2020 (£1,042) levels entirely. `utilitymatchmaker.co.uk`
>    reproduces the same wrong dates, so their agreement is *not* independence. The build sourced the
>    window boundaries from Ofgem's own default-tariff-levels enumeration instead.
> 3. **§3a's impact table understated the problem by scoping it to timing.** Measuring every window
>    against the old annual blend showed the annual table is *also systematically mis-levelled* — 10 to
>    80 £/MWh BELOW the published cap in nearly every non-crisis period (2025 elec 190.0 vs a real
>    248.6–270.3). The re-thread therefore moves the ceiling **down** in the crisis window (as §3
>    predicted) and **up** almost everywhere else (which §3 did not predict). Both toward the source.
>
> §2b's finding — that `_PRICE_CAP_QUARTERLY` puts the Apr-2022 step at calendar Q1 — is **confirmed**,
> and is broader than stated: the offset is systematic across the whole 2019–Sep-2022 six-monthly era
> (`2022-Q3` likewise carries the Oct-2022 level). That table serves `PriceCapBook` compliance
> reporting, not the clamp, so it is left as registered debt on `W3_1` rather than edited here.

**Type:** self-drawable DISCOVER half of RUNG-7 planner mint
`PLANNER_MINTED_intra_year_price_cap_granularity_2026-07-28.md`. Design/enumeration only — **no
production code changed, no git run**. Walls honoured: **R13** (cap values are external Ofgem reality,
sized blind to company P&L) and **R12** (cap accuracy is fidelity-vs-source, never tuned to margin).

---

## 0. VERDICT + RECOMMENDATION (top)

**Verdict:** the gap is REAL and confirmed in code. The deemed/SVT clamp
(`simulation/hedged_settlement.py::run_deemed_term`) keys the cap on `current_date.year` alone
(annual granularity), so a **Jan–Mar 2022** deemed resi customer is clamped against the **full-year-2022
blend** (elec 305 £/MWh, gas 95 £/MWh) instead of the **pre-Apr-2022 cap that actually applied**
(elec ≈208 £/MWh, gas ≈41.7 £/MWh — the cap set at Oct-2021 ran through 31 Mar 2022). The ~54% Apr-2022
step (£1,277→£1,971 typical dual-fuel bill) is blended away — the exact crisis dynamic this atom exists
to model. The gap is **NOT** currently a *declared + measured-bound* simplification: it is logged in
W3_1's notes as "granularity debt / QUEUED", but with **no sized £ bound** — which is what DISCOVER now
supplies.

**Sized impact (upper bound, per deemed resi customer, Jan–Mar 2022 window, fully-binding cap):**
- **Electricity deemed term:** ~**£87** over-billed (0.90 MWh × 97 £/MWh over-clamp)
- **Gas deemed term:** ~**£256** over-billed (4.8 MWh × 53.3 £/MWh over-clamp)
- **Dual-fuel customer:** ~**£343** over-stated revenue / over-optimistic margin for the quarter
- Population impact = £343 × N, where N = deemed resi customers with a Jan–Mar 2022 out-of-contract
  period (N not knowable without a sim run; the per-customer bound is the DISCOVER deliverable).
- Direction: the annual blend sets the in-sim ceiling **too loose** for Jan–Mar 2022, so in-sim revenue
  is **too high** and crisis margin is **less negative than reality** — it softens the very squeeze the
  atom was built to reproduce.

**Recommendation: BUILD the sub-annual (cap-window) table — this is worth the complexity**, with
declare-and-bound as the credited fallback if the director declines the gated BUILD. Rationale:
1. The impact (~£343/dual-fuel customer/quarter) lands **precisely in the crisis window this atom exists
   to model** and directly serves DIRECTOR_AXES #3 Believability — an annual blend erases the defining
   feature (the mid-year step).
2. A quarterly cap table **already exists** in-repo (`company/regulatory/price_cap.py::_PRICE_CAP_QUARTERLY`)
   — most data-sourcing is done; build cost is a window-lookup + re-thread + ground-truth regen.
3. **BUT that existing table has its own boundary defect** (see §2b): it places the Apr-2022 step at
   calendar-Q1 (Jan). A naive re-thread to it would STILL mis-clamp Jan–Mar 2022. The BUILD must key on
   the **real cap-change windows** (6-monthly Oct/Apr through Sep-2022, then quarterly), not calendar
   quarters. This defect should be corrected regardless of whether the full re-thread ships.

**If BUILD is declined** (it is director-gated — `blocked_on: director_level_up`, and re-threading
regenerates `run_output_latest.json` ground truth): register the measured bound above as a **declared +
measured-bound simplification** in W3_1's `simplifications:` — a credited, argued outcome per the mint's
"Legitimate alternative outcome" (§3), NOT a silent closure.

---

## 1. CURRENT-CODE ANALYSIS

### 1a. The clamp is keyed by `current_date.year` alone (annual granularity)

`company/pricing/ofgem_price_cap.py` (full file read) keys the cap on integer year only:

```python
_ELEC_CAP_GBP_PER_MWH: dict[int, float] = {
    2019: 165.0, 2020: 157.0, 2021: 183.0,
    2022: 305.0,   # Apr 2022 ~28p/kWh; EPG Oct 2022 ~30p/kWh equivalent
    2023: 265.0, 2024: 210.0, 2025: 190.0,
}
_GAS_CAP_GBP_PER_MWH: dict[int, float] = {
    2019: 26.0, 2020: 25.0, 2021: 35.0,
    2022: 95.0,    # ~7-10p/kWh crisis peak; EPG in effect Q4
    2023: 70.0, 2024: 55.0, 2025: 52.0,
}

def get_cap_unit_rate_gbp_per_mwh(fuel: str, year: int) -> float | None:
    ...
    if fuel == "electricity":
        return _ELEC_CAP_GBP_PER_MWH.get(year, _ELEC_CAP_FALLBACK)
    if fuel == "gas":
        return _GAS_CAP_GBP_PER_MWH.get(year, _GAS_CAP_FALLBACK)
```

The module **docstring's declared simplifications** (lines 8–17) are: *"Source: Ofgem quarterly cap
publications + Energy Price Guarantee (Oct 2022–Jun 2023). **Simplified to annual averages. Rich's
direction: 'ballpark + components right, not year-on-year precision.'** … All values in £/MWh (excluding
standing charge, excluding VAT). Electricity typical unit rate: Ofgem p/kWh × 10 = £/MWh."* The declared
simplification is the **year-on-year ballpark** — the intra-year (off-by-period) blend is NOT among the
declared simplifications; the comment `2022: 305.0  # Apr 2022 …; EPG Oct 2022 …` explicitly averages two
different sub-year regimes into one number.

### 1b. The binding site (`simulation/hedged_settlement.py::run_deemed_term`, line ~305)

```python
uncapped_rate_gbp_per_mwh = spot_price * (1.0 + deemed_premium)
billed_rate_gbp_per_mwh = uncapped_rate_gbp_per_mwh
if segment == "resi":
    _cap = get_cap_unit_rate_gbp_per_mwh(commodity, current_date.year)   # <-- YEAR ONLY
    if _cap is not None:
        billed_rate_gbp_per_mwh = min(uncapped_rate_gbp_per_mwh, _cap)
```

`current_date` advances per settlement day inside the loop, so the lookup is evaluated per-day — but only
`.year` is used, so every day of 2022 (Jan through Dec) receives the identical 305/95 blend. The
Expert-Hour verdict already flagged this: *"cap-year lookup evaluated per-day … correctly handles a
deemed term spanning a calendar-year boundary"* — correct on the year boundary, silent on the intra-year
step.

### 1c. W3_1's simplifications list does NOT declare this gap as a measured bound (mint confirmed)

`docs/design/maturity_map.yaml`, atom `W3_1_price_cap_binding` (line 606, `level_current: 2`,
`loop_stage: harden`). Its `simplifications:` array (line 617) contains four entries:
- **2026-07-11 BUILT** — the binding-constraint build (the clamp itself).
- **2026-07-11 HARDEN Expert Hour** — logs the gap as text: *"the cap table's ANNUAL granularity doesn't
  capture the real Ofgem cap's 2-4x/year updates … the real ~54% Apr 2022 jump … granularity debt on an
  already-working mechanism, tracked for a future intra-year cap-table pass"*. **Logged, not sized.**
- **2026-07-27 / 2026-07-28 RULE-0 HARDEN re-verifies** — both restate it as *"the one still-open gap …
  the already-adjudicated annual-vs-quarterly cap granularity … stays QUEUED as a fidelity-widen BUILD"*.

So the mint's claim is accurate: the list records the build + Rule-0 re-verifies and **acknowledges** the
gap as queued debt, but there is **no declared+measured-bound simplification** — no £ figure closes it.
That is the deliverable this DISCOVER produces (§3).

The 07-27 note also records the key architectural fact used below: *"quarterly cap data DOES already
exist in `company/regulatory/price_cap.py::_PRICE_CAP_QUARTERLY`"*.

---

## 2. THE CITED REAL OFGEM SUB-ANNUAL CAP SCHEDULE

**Cadence (cited):** the Default Tariff Cap launched 1 Jan 2019 and updated **6-monthly (Apr / Oct)**
through Sep 2022, then moved to **quarterly (Jan / Apr / Jul / Oct)** from Oct 2022. Every figure below
carries a citation; unverified figures are marked **UNVERIFIED**.

| Cap window (effective) | Typical dual-fuel DD bill (£/yr) | Elec unit rate (p/kWh) | Gas unit rate (p/kWh) | Source |
|---|---|---|---|---|
| 1 Oct 2021 – 31 Mar 2022 | **£1,277** | ~20.8 | ~4.0 | pricecaprates.co.uk (2021-Q3 £1,277); MoneySavingExpert ("winter 2021 … £1,277") — elec/gas p/kWh from in-repo 2021-Q4 (20.8 / 4.17) |
| 1 Apr 2022 – 30 Sep 2022 | **£1,971** (+54% step) | ~28.3 | ~7.4 | House of Commons Library CBP-9714 ("rose by 54% in the April 2022 price cap"); £1,277×1.54≈£1,966≈£1,971; p/kWh from in-repo 2022-Q2 (28.34 / 7.37) |
| 1 Oct 2022 – 31 Dec 2022 | Ofgem cap **~£3,549**; **EPG capped bills at £2,500** | ~34 (EPG-equiv) | ~10.3 (EPG-equiv) | Commons Library ("+27% in the October 2022 cap"); EPG £2,500 (Ofgem/HMG); Ofgem 1-Jan-2023 letter |
| 1 Jan 2023 – 31 Mar 2023 | Ofgem cap **~£4,279**; **EPG £2,500** | ~34 (EPG-equiv) | ~10.3 (EPG-equiv) | Ofgem "Default Tariff Cap Letter for 1 January 2023"; EPG £2,500 (bill people actually paid) |
| 1 Apr 2023 – 30 Jun 2023 | Ofgem cap **£3,280 (all-time peak)**; **EPG £2,500** | ~30.1 | ~8.5 | pricecaprates.co.uk ("all-time Ofgem cap peak £3,280"); Ofgem "1 April 2023" letter; in-repo 2023-Q2 (30.11 / 8.55) |
| 1 Jul 2023 – 30 Sep 2023 | **£2,074** (EPG ends, cap < EPG) | ~29.4 | ~7.4 | pricecaprates.co.uk (2023-Q3 £2,074); BBC ("bills drop … winter"); in-repo 2023-Q3 (29.42 / 7.42) |

**EPG override note (cited):** between **Oct 2022 and Jun 2023** *"no one paid the full amount under the
Price Cap, as prices were discounted under the Energy Price Guarantee (EPG)"* — a typical dual-fuel DD
bill was held at **£2,500** to 31 Mar 2023 (House of Commons Library CBP-9714). Any high-fidelity BUILD
covering Oct-2022→Jun-2023 must apply **min(Ofgem cap, EPG)** for resi, not the raw Ofgem cap — the EPG is
the binding ceiling in that window. (For the specific Jan–Mar 2022 gap this finding targets, EPG is
irrelevant — it post-dates the window.)

### 2b. DEFECT found in the *existing* in-repo quarterly table (`_PRICE_CAP_QUARTERLY`)

The already-present quarterly table places the Apr-2022 step at **calendar Q1**, not the real cap window:

```
"2021-Q4": {... elec 20.80, gas 4.17, annual_typical_gbp 1277}   # correct: Oct-Dec 2021
"2022-Q1": {... elec 28.34, gas 7.37, annual_typical_gbp 1971}   # WRONG: Jan-Mar 2022 real cap
                                                                 #  = £1,277 / 20.8p (Oct-2021 cap
                                                                 #    ran through 31 Mar 2022)
"2022-Q2": {... elec 28.34, gas 7.37, annual_typical_gbp 1971}   # correct: Apr-Jun 2022
```

The real cap did **not** step up on 1 Jan 2022 — it stepped up on **1 Apr 2022**. So `2022-Q1` should
carry the Oct-2021 level (£1,277 / elec 20.8 / gas ~4.0), matching `2021-Q4`. **A BUILD that naively
re-threads the clamp to `_PRICE_CAP_QUARTERLY` by calendar quarter would still over-clamp Jan–Mar 2022 by
the full step** — reproducing the very gap it set out to fix. The BUILD must therefore key on **real
cap-change windows** (§4), and the `2022-Q1` row should be corrected to £1,277 / 20.8p / ~4.0p regardless.

---

## 3. £ IMPACT MEASUREMENT (arithmetic shown)

### 3a. Unit conversion and the three 2022 sub-windows (elec, £/MWh; docstring: p/kWh × 10)

| Window | Real elec cap | Real gas cap | In-sim annual blend | Elec over-clamp | Gas over-clamp |
|---|---|---|---|---|---|
| **Jan–Mar 2022** (pre-step) | 20.8p → **208** | 4.17p → **41.7** | elec 305 / gas 95 | **+97** (blend too loose) | **+53.3** (too loose) |
| Apr–Sep 2022 (post-step) | 28.34p → 283.4 | 7.37p → 73.7 | elec 305 / gas 95 | +21.6 | +21.3 |
| Oct–Dec 2022 (EPG era) | ~34p → 340 | ~10.3p → 103 | elec 305 / gas 95 | −35 (blend too *tight*) | −8 (too tight) |

The blend is worst (most over-loose) exactly in **Jan–Mar 2022**, the pre-step crisis window — the target
of this finding. (It is even mildly over-*tight* in Q4, but Q4 is EPG-governed and a distinct concern.)

### 3b. Per-customer over-billing bound, Jan–Mar 2022 (when the cap binds)

Consumption basis (Ofgem TDCV typical resi, sim uses per-customer EPC/HH shapes — these are the standard
typical values): **elec 3,100 kWh/yr, gas 12,000 kWh/yr**. Winter-quarter weighting (Jan–Mar is
heating-heavy): elec ≈29% of annual, gas ≈40% of annual.

```
Elec Jan-Mar 2022 volume  = 0.29 × 3,100 kWh ≈ 900 kWh  = 0.90 MWh
Elec over-billing (upper) = 0.90 MWh × 97 £/MWh          ≈ £87

Gas  Jan-Mar 2022 volume  = 0.40 × 12,000 kWh ≈ 4,800 kWh = 4.80 MWh
Gas  over-billing (upper) = 4.80 MWh × 53.3 £/MWh          ≈ £256

Dual-fuel per-customer per-quarter (upper bound) ≈ £87 + £256 ≈ £343
```

**Why "upper bound":** the difference only realises when the clamp actually binds, i.e.
`spot×(1+premium) > cap`. Three regimes per period:
- `uncapped > 305` (blend) → full over-clamp bites (£97/MWh elec, £53.3/MWh gas).
- `208 < uncapped ≤ 305` → in-sim bills up to `uncapped`, reality clamps to 208 → *partial* over-billing.
- `uncapped ≤ 208` → cap non-binding either way → **£0 difference**.

Through Jan–Mar 2022 spot was elevated (gas-crisis), so many periods sit in the first regime, but not all
— hence £343 is the **defensible upper bound** for a fully-capped dual-fuel deemed customer, and the true
figure is ≤ that, scaled by the fraction of periods where the cap binds. Population impact = per-customer
bound × N deemed resi customers with a Jan–Mar 2022 out-of-contract period (N requires a sim run;
`run_deemed_term` is called per out-of-contract term in `run_phase2b.py` line ~1675 with
`deemed_premium` default 0.20).

### 3c. Unit-rate + standing-charge structure the cap actually uses (relevant note)

The real Ofgem cap has **two components**: a unit rate (p/kWh) **and** a standing charge (pence/day) — the
`_PRICE_CAP_QUARTERLY` table carries both (e.g. `standing_elec_ppd`, `standing_gas_ppd`). The in-sim
clamp (`ofgem_price_cap.py`) is a **unit-rate ceiling only** — standing charges are excluded (docstring:
*"excluding standing charge, excluding VAT"*). This is a separate, pre-existing simplification and is
**out of scope** for this finding (which is about the intra-year *timing* of the unit-rate cap, not adding
the standing-charge leg). Note only: the standing charge itself also stepped materially (elec ~25 ppd in
2021 → ~45 ppd in 2022), so if the standing leg is ever added, it inherits the same window-granularity
requirement.

---

## 4. BUILD SKETCH (design only — gated, no code here)

**Goal:** clamp each settlement period against the cap for the **real cap window that contains that
period's date**, portable (keyed by a window schedule, not hardcoded to 2022).

**4a. Add a window-keyed lookup** in `company/pricing/ofgem_price_cap.py` alongside (not replacing) the
annual one — forward-only, so existing annual callers are untouched:

```
# Cap-window schedule: list of (effective_from, effective_to, elec_gbp_per_mwh, gas_gbp_per_mwh)
# Windows follow the REAL cap cadence (6-monthly Apr/Oct to Sep-2022, then quarterly), NOT calendar Qs.
_CAP_WINDOWS = [
    ("2021-10-01", "2022-03-31", elec=208.0, gas=41.7),   # Oct-2021 cap, runs THROUGH 31 Mar 2022
    ("2022-04-01", "2022-09-30", elec=283.4, gas=73.7),   # +54% Apr-2022 step
    ("2022-10-01", "2022-12-31", elec=min(cap,EPG), gas=min(cap,EPG)),  # EPG binds
    ...
]

def get_cap_unit_rate_for_date(fuel: str, on_date: date) -> float | None:
    # binary/linear search the window containing on_date; None before 2019-01-01
```

- Source the elec/gas £/MWh from the **corrected** `_PRICE_CAP_QUARTERLY` (fix the `2022-Q1` row per §2b
  first), or re-key it into windows directly.
- **EPG:** for windows Oct-2022→Jun-2023, the ceiling is `min(Ofgem_cap, EPG)` for resi (§2 note).
- **Portability (mint requirement):** the schedule is a data table of `(from, to, rate)` tuples — no
  `if year == 2022`. A second market / regime supplies its own window list behind the same accessor.

**4b. Re-thread the binding site** (`hedged_settlement.py::run_deemed_term`, line ~305): replace
`get_cap_unit_rate_gbp_per_mwh(commodity, current_date.year)` with
`get_cap_unit_rate_for_date(commodity, current_date)`. One-line change; the `min(uncapped, cap)` clamp and
`segment == "resi"` guard are unchanged (both already R15-proven load-bearing, per W3_1's 07-28 note).

**4c. Blast radius (why it's gated):** re-threading changes ground-truth settlement output, regenerating
`docs/reports/run_output_latest.json`. This is `blocked_on: director_level_up` (R16) and must run the full
sim cycle — not a bounded HARDEN tick. Values are external Ofgem reality (**R13**), sized blind to P&L
(**R12**): the table is corrected to match the source, never to move margin.

**4d. R15 MUTATION TEST shape (the control must be able to FAIL):**

```
test_deemed_jan_mar_2022_clamps_against_pre_apr_cap:
    settle a resi deemed period dated 2022-02-15 with spot forcing uncapped >> cap
    ASSERT billed_rate == 208.0  (elec pre-Apr-2022 window), NOT 305.0 (annual blend)

test_deemed_may_2022_clamps_against_post_step_cap:
    settle a resi deemed period dated 2022-05-15, uncapped >> cap
    ASSERT billed_rate == 283.4  (elec Apr-Sep-2022 window), NOT 208.0 and NOT 305.0

MUTATION (must FIRE):
    revert get_cap_unit_rate_for_date -> get_cap_unit_rate_gbp_per_mwh(..., date.year)  # annual blend
    => the Feb-2022 test sees 305.0 not 208.0 -> test FAILS (control proven load-bearing)
    Second mutation: swap the _CAP_WINDOWS Jan-Mar row to the Apr rate (the §2b calendar-Q defect)
    => Feb-2022 test sees 283.4 not 208.0 -> FAILS (proves the window-boundary, not just the year, is
       load-bearing)
```

Both mutations independently fire → neither TAUTOLOGY (asserted values 208/283.4 come from the Ofgem
source, independent of the clamp under test), FAIL-OPEN, nor FAIL-SILENT (a missing window returns None →
uncapped, which the pre-2019 test already covers; add a "date inside a defined window returns non-None"
assertion so a dropped window can't silently pass).

---

## 5. RECOMMENDATION (restated, evidence-backed)

**BUILD the sub-annual cap-window table** — primary recommendation. It is the reason W3_1 exists (model
the 2021–22 crisis), the data mostly exists in-repo, the impact (~£343/dual-fuel customer/quarter, up to
£87 elec + £256 gas for Jan–Mar 2022) is material and lands in-window, and it serves Believability (#3).
The one-line re-thread is cheap; the corrected window schedule (§2b/§4a) is the real work.

**Fallback if the gated BUILD is declined:** register a **declared + measured-bound simplification** in
W3_1's `simplifications:` reading approximately — *"2022 (and each pre-Oct-2022 year) cap is an annual
blend; the real cap stepped mid-year (~54% at 1 Apr 2022). A Jan–Mar 2022 deemed resi customer is clamped
against the 305/95 £/MWh blend vs the true Oct-2021-cap ≈208/41.7 £/MWh — an upper bound of ~£87 (elec) +
~£256 (gas) ≈ £343 over-stated revenue per dual-fuel customer for that quarter (blend too loose → crisis
margin less negative than reality). Not built: re-threading regenerates run_output ground truth (gated).
Bound sized in `docs/design/INTRA_YEAR_PRICE_CAP_GRANULARITY_DISCOVER.md`."* This is a credited, argued
outcome per the mint's §3, not a silent closure.

**Independent of the BUILD/declare decision:** the `_PRICE_CAP_QUARTERLY` `2022-Q1` row (§2b) should be
corrected to the Oct-2021 level (£1,277 / elec 20.8p / gas ~4.0p) — it is a factual error against the
Ofgem source, and it would silently defeat any calendar-quarter re-thread.

---

## Sources
- [Gas and electricity prices during the 'energy crisis' and beyond — House of Commons Library CBP-9714](https://commonslibrary.parliament.uk/research-briefings/cbp-9714/) — 54% Apr-2022 / 27% Oct-2022 steps; EPG £2,500 held Oct-2022→31 Mar 2023; "no one paid the full Price Cap under EPG".
- [Ofgem Energy Price Cap History — priceCapRates.co.uk](https://www.pricecaprates.co.uk/history) — £1,277 (Oct-2021), £1,971 (Apr-2022), £2,500 (Oct-2022 EPG), £3,280 all-time peak (Apr-2023), £2,074 (Jul-2023).
- [What is the Energy Price Cap? — MoneySavingExpert](https://www.moneysavingexpert.com/utilities/what-is-the-energy-price-cap/) — winter 2021 typical bill £1,277.
- [Ofgem — Default Tariff Cap Letter for 1 January 2023](https://www.ofgem.gov.uk/sites/default/files/2022-11/Default%20Tariff%20Cap%20Letter%20for%201%20January%202023.pdf) — Jan-2023 cap level letter.
- [Ofgem — Default Tariff Cap Letter for 1 April 2023](https://www.ofgem.gov.uk/sites/default/files/2023-02/Default%20Tariff%20Cap%20Letter%20for%201%20April%202023.pdf) — Apr-2023 (all-time peak) cap level letter.
- [Ofgem — energy price cap standing charges and unit rates by region](https://www.ofgem.gov.uk/information-consumers/energy-advice-households/get-energy-price-cap-standing-charges-and-unit-rates-region) — component (unit rate + standing charge) structure.
- In-repo cross-check: `company/regulatory/price_cap.py::_PRICE_CAP_QUARTERLY` (elec/gas p/kWh + standing charges per quarter, 2019-Q1 → 2025-Q1) — used to source the p/kWh figures; **note the `2022-Q1` boundary defect flagged in §2b**.
