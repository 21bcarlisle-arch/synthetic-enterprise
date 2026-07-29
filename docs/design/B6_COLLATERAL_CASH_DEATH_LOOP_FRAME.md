# B6 — Collateral → cash death loop: dying on the BANKED clock while surviving on the SETTLED one

**Atom:** `B6_collateral_cash_death_loop` (lane `E_finance_treasury`, value_stream `close_to_learn`, epoch 3,
`provenance: proposal`, `loop_stage: idle`, `dial_inherited: 3`, `depends_on: [SPINE_3_gas_storage_crisis_regime]`).

**Stage:** DISCOVER (L0→L1) + FRAME (design only). **NO BUILD CODE WRITTEN.** Per EPOCH_GATING_AND_ATOM_AUTHORSHIP
Rule 1 this atom is parked for BUILD; DISCOVER/FRAME is available now. Nothing under `company/`, `sim/`, `saas/`,
`simulation/` or `background/` is created or modified by this pass. The only artefacts are this document and the
atom's map entry.

**Provenance chain:** `docs/design/BACKLOG.md` B6 (Wave B, lines 105-116) → registered into `maturity_map.yaml`
2026-07-29 → coupled by COUPLED-TRIAD law to `SPINE_3_gas_storage_crisis_regime` (the world half). This FRAME
builds directly on `docs/design/SPINE_3_GAS_STORAGE_CRISIS_FRAME.md` (commit `52fc590bb`) and in particular on
its §2.7, which already states the supply contract SPINE_3 owes B6.

**Evidence discipline (R9).** Every factual claim below is labelled `observed-with-evidence` (read from a named
file at a named line, or executed this pass) or `inferred`. Nothing is recalled.

**Inherited from SPINE_3 and NOT re-assumed** `observed-with-evidence` (`SPINE_3_GAS_STORAGE_CRISIS_FRAME.md`
§1.2, §1.3, §1.8): the 2021/22 inversion is **replayed real history** in `sim/gas_data/nbp_sap.csv`, not a script;
the one hardcoded crisis trajectory `sim/scenario/curriculum/crisis_2021_22.yaml` is **unratified, out of rotation
and read by no generator** — an inert path. **This FRAME therefore hangs no margin call on a scripted crisis.**
Every design below is defined against a *replayed real price path* and, where a shock is needed, against SPINE_3's
single exogenous pipeline-supply term whose magnitude is director-reserved curriculum.

---

## 1. DISCOVER (L0 → L1) — what actually exists today

### 1.0 The headline: the atom description is materially STALE, in both directions

`observed-with-evidence`. The atom name reads as though nothing exists ("level 0 → 3", `file_scope:
[saas/treasury, ...]`). That is wrong in **two opposite ways**, and both matter for BUILD:

1. **Substantial collateral/variation-margin machinery ALREADY EXISTS and is LIVE in the production run.** A
   BUILD fork that starts from "level 0 = absent" would rebuild it.
2. **The one thing B6 is actually *for* — the DIVERGENCE between cash and accounting P&L — is not merely absent,
   it is structurally impossible**, because the live run holds cash and P&L as *literally the same variable*
   (§1.3). A BUILD fork that starts from "margin exists, so wire it up" would wire a margin call into a cash line
   that cannot diverge from the P&L line, and would produce a green test that proves nothing.

The atom's declared `file_scope` is also wrong: `saas/treasury` **does not exist** (`ls saas/` this pass returns
no `treasury` entry) and neither does `tests/saas/test_collateral_death_loop.py`. All real machinery lives in
`company/finance/`, `company/risk/`, `company/trading/` and `simulation/run_phase2b.py`. A BUILD drawing this atom
on its stated scope would create a *second*, duplicate treasury in the wrong layer.

### 1.1 What EXISTS and is LIVE in the production run

`observed-with-evidence`. Two live pieces, both in `simulation/run_phase2b.py`:

| # | Artefact | Where it runs | What it does |
|---|---|---|---|
| 1 | `company/finance/margin_call_book.py::build_margin_calls_from_mtm` | `run_phase2b.py:99` (import), `:2533` (call) | Derives the variation margin the company must POST from its own ISDA-netted MtM: `variation_margin = max(0, −netted_mtm)` (`margin_call_book.py:194`). Idempotent by `call_id = VM-<cp>-<date>` (`:197`). |
| 2 | `company/risk/collateral_death_test.py::breaking_strain_sweep` (MC-2) | `run_phase2b.py:618-731` (`_mc2_collateral_death_test`), `:2562` (call) | Marks ONE live book at TWO observable point-in-time forwards (a calm origination mark, the real 2021-12-31 stressed mark) and sweeps doses 0.8/1.0/1.2/1.5× of the observed price *move*, reporting the dose at which `facility + cash − call < 0`. |

Also live and real: `company/finance/margin_call_book.py:68 book_scaled_credit_facility_gbp` — the committed
facility is derived ONCE from the book's own gross marked exposure at origination
(`FACILITY_COVERAGE_MULTIPLE = 1.5`, `FACILITY_MIN_GBP = 250_000.0`, `:64-65`) and held fixed across the sweep
(`collateral_death_test.py:141-143`). This is a genuine, director-ruled design (MC-2 §3) and B6 must not undo it.

**These are not toys.** The most recent published run carries a real, non-trivial margin book
(`docs/reports/run_output_latest.json`, read this pass):

```
"margin_call_book": { "total_calls": 7, "outstanding_calls": 7,
                      "total_outstanding_gbp": 1392351.10,
                      "credit_facility_gbp": 2537361.39,
                      "headroom_gbp": 1145010.29,
                      "is_liquidity_stressed": false, "stress_events": 1 }
"final_treasury_gbp": 3898728.857800693     "administration_event": null
```

### 1.2 What exists as CODE but is DEAD (test-only — no production caller)

`observed-with-evidence`, by sweep (`grep -rn <symbol> --include=*.py .` excluding `tests/` and
`.claude/worktrees/`): **four** substantial modules have **zero** production callers.

| Module | Lines | Status |
|---|---|---|
| `company/trading/otc_margin_book.py` (`OTCMarginBook`) | 178 | **test-only.** Full CSA VM model incl. `MarginCallDirection.CALL/RETURN`, `cash_impact_gbp` (`:65-69`), T+1 overdue (`:57-62`). Its docstring `:8-10` describes the exact 2022 failure B6 wants. Nothing calls it. |
| `company/trading/initial_margin_register.py` (`InitialMarginRegister`) | 174 | **test-only.** Its docstring `:14-19` names the direction-agnostic amplifier ("clearing houses issued margin calls to INCREASE initial margin"). Nothing calls it. |
| `company/risk/liquidity_stress_test.py` (`LiquidityStressTestBook`) | 191 | **test-only.** Has `initial_margin_shock_pct` (`:41`) and a 4-state outcome enum incl. `INSOLVENT` (`:28-38`). Nothing calls it. |
| `company/risk/capital_adequacy.py` | — | **test-only.** `_MARGIN_CALL_BUFFER_MIN_PCT = 10.0` (`:36`). Referenced by name only in `obligations_register.py:626`. Nothing calls it. |

`company/finance/treasury.py` (96 lines: `working_capital`, `treasury_health`, `MCR_PER_ACCOUNT = 130.0`) and
`company/finance/working_capital.py` (a full `CashFlowType`/`DailyCashPosition` daily cash model **including
`CREDIT_FACILITY_DRAWDOWN`/`REPAYMENT`**, `:15-16`) are likewise not on the run path — they read a management-pack
dict, not the live loop.

`inferred`, and it is the single most useful thing this DISCOVER can tell BUILD: **B6 is not short of components.
It is short of a SPINE that connects them to cash.** The dead modules are close to the right shapes.

### 1.3 THE CENTRAL DEFECT: cash and accounting P&L are the SAME VARIABLE

`observed-with-evidence`. `simulation/run_phase2b.py:1922-1924`, inside the per-settlement-period loop:

```python
rec["net_margin_gbp"] = round(rec["net_margin_gbp"] - _bad_debt, 6)
treasury += rec["net_margin_gbp"]
rec["treasury_cash_balance_gbp"] = treasury
```

The quantity called `treasury_cash_balance_gbp` **is the running cumulative sum of accounting net margin.** It is
not a bank balance. Nothing else adds to or subtracts from it in the loop.

And the death test is taken off that same number, `run_phase2b.py:1938`:

```python
if is_administration_triggered(treasury) and administration_event is None:
```

with `sim/risk_engine.py:180-187`:

```python
def is_administration_triggered(treasury_balance_gbp: float) -> bool:
    return treasury_balance_gbp <= 0
```

**Therefore the only mortality path in the simulation today is a P&L path wearing the word "treasury".** The
company can only die by accumulating enough negative accounting margin to drive the sum below zero. `inferred`,
and this is B6's entire reason to exist: *the divergence B6 is defined by — dead on cash, alive on paper — is not
merely unmodelled, it is arithmetically unrepresentable, because there is exactly one number.* No amount of
wiring margin calls into a second report can produce it; the run must gain a **second, independent balance on a
different clock**.

### 1.4 The margin book never touches the cash line

`observed-with-evidence`, three independent confirmations:

1. `_margin_call_summary` is assigned at `run_phase2b.py:2536` and used at **exactly one** other place —
   `:2635`, the report dict. Sweep of `grep -n "_margin_call_summary" simulation/run_phase2b.py` returns
   `2440, 2536, 2635` and nothing else. It is a **report**, not a cash flow.
2. `MarginCallBook.settle_call` (`margin_call_book.py:102`) has **no production caller** anywhere in the tree
   (sweep excluding `tests/`). Calls are raised and never settled, never paid, never returned.
3. The published run (§1.1) shows £1,392,351.10 of margin **outstanding** against a treasury of £3,898,728.86
   that is unaffected by it. The two numbers coexist in the same JSON and never meet.

Also: `run_phase2b.py:2533-2534` builds the margin book **once**, at `as_of_date=effective_end` — the end of the
whole run. There is no path, no trajectory, no cumulative posting: a single terminal snapshot.

### 1.5 MC-2 is a POST-HOC two-point measurement, not a time path

`observed-with-evidence`, `run_phase2b.py:618-697`:

- It runs **after** the settlement loop has finished (call site `:2562`, well past the `administration_event`
  loop at `:1938`), so nothing it computes can affect the run's own life or death.
- It marks the book at exactly **two** dates: `origination_date = min(c.term_start for c in live)` (`:664`) and
  `stressed_date` (`:652-655`, the real 2021-12-31 anchor or the run's own peak-exposure sample). Doses
  interpolate linearly between them (`collateral_death_test.py:59-81`).
- **`available_cash_gbp` defaults to `0.0`** (`run_phase2b.py:625`) and is **never passed** at the call site
  (`:2562-2568`). The run's own treasury — the only cash number that exists — is not even supplied to the
  liquidity test. The module says so itself at `:723-726`: *"treasury at a PAST point-in-time is not
  reconstructable in this feed."*
- **C-S3 is violated at the source:** `:696` passes `settlement_deadline=stressed_date`, i.e. **the call date and
  the payment deadline are the same day.** Zero payment latency. `inferred`: the timing asymmetry that IS the
  death loop cannot be expressed by a mechanism whose call and settlement are the same instant.

### 1.6 The one existing collateral-death measurement is DROPPED before it is published

`observed-with-evidence`. `simulation/run_phase2b.py:2638` puts `"mc2_collateral_death_test":
_mc2_death_test_summary` into the run's return dict. The report reducer,
`saas/reporting/annual_report.py::extract_report_data` (`:168`), forwards `"margin_call_book"` at **`:655`** — and
`grep -c "mc2_collateral_death_test" saas/reporting/annual_report.py` returns **`0`**.

Confirmed downstream: `docs/reports/run_output_latest.json` (git-committed 2026-07-29 17:09) contains
`margin_call_book` and `wholesale_credit_exposure` but **no `mc2_collateral_death_test` key** (verified by a
recursive key search this pass). `tools/generate_dashboard_data.py:491-492` reads `wholesale_credit_exposure` and
`margin_call_book`; it reads nothing MC-2.

`inferred`: this is a **fail-silent orphan** in the exact R11 "no orphan transitions" sense — the only
death-by-collateral measurement the project owns computes correctly, is wrapped in a `try/except Exception` that
prints a warning and continues (`:2570-2573`), and is then discarded at the reducer. If it ever fired
`death_cause="collateral_while_solvent"`, **no surface would show it.**

### 1.7 There is no survival ledger and no survival score

`observed-with-evidence`.

- `background/run_manifest.py:147-168` defines `RunOutcomes` with exactly the right fields: `survived`,
  `death_cause`, `death_date`, `liquidity_headroom_min_gbp`, `collateral_cover_min`, and a `validate()` that
  refuses a death without a cause (`:166-168`).
- `LEDGER_PATH = docs/observability/run_ledger.jsonl` (`:60`). **That file does not exist** (`ls` this pass:
  "No such file or directory"). No run has ever written a row.
- `RunManifest(` is constructed at exactly one place, `run_manifest.py:234`, inside the module's own builder. No
  simulation or background caller emits one.
- The blended **survival SCORE** (§6 of `RUN_LEDGER_AND_SCORES_BUILD_2026-07-25`) is explicitly
  **director-session gated and unbuilt** — stated in `collateral_death_test.py:28-34`, which deliberately builds
  "NO blended survival score, authors NO curriculum value, and emits NO ledger row itself."

So B6's DoD clause *"the mortality is recorded by the survival score"* currently has **neither the ledger row nor
the score** behind it. `inferred`: this is a genuine dependency B6 must name rather than assume, and part of it
(the score) is **director-reserved**, not agent-buildable.

### 1.8 There is no BANKED clock on the money that matters

`observed-with-evidence`. The project already owns the R14 clock vocabulary and uses it correctly elsewhere:
`company/finance/bad_debt_reconciliation.py:101-102` (`PROVISION_CLOCK = "billed"`, `REALISED_CLOCK = "settled"`),
`tools/generate_company_data.py:24` ("No number is emitted without a `clock` field"), `saas/reporting/
css_statement.py:525-528` ("**banked** = cash collected"), `tools/generate_dashboard_data.py:259,270` (net margin
labelled `"clock": "settled"`).

But `treasury_cash_balance_gbp` — the number the death test reads — is an accumulation of **settled-clock** net
margin (§1.3). `inferred`: **there is no banked-clock balance anywhere on the run path.** R14 says a basis-less
number is a defect; here the defect is sharper — a number carrying the *wrong* basis for the decision taken on
it. An insolvency test is a BANKED-clock question and it is currently answered on the SETTLED clock.

### 1.9 Initial margin is identically zero, so the spike-direction drain cannot exist

`observed-with-evidence`. `margin_call_book.py:175-178`: *"variation margin at a single mark = the amount by
which the company is out-of-the-money, `max(0, -netted_mtm)` … **Initial margin is modelled by the
credit/observation step, so it is 0 here.**"* Confirmed at `:203`: `initial_margin_gbp=0.0` on every constructed
call. `InitialMarginRegister` (the module that would carry it) is dead (§1.2).

`inferred`, and it interlocks with a live diagnosis the code already makes: `collateral_death_test.py:23-26`
records that *"a pure long hedge book goes IN-the-money on a price spike and posts NO variation margin, so it
cannot die to collateral — `any_name_posted_margin=False`"*. That is correct VM physics. But it means the current
model can only ever kill on a price **FALL**. The direction-agnostic channel — a CCP raising IM multiples because
*volatility* rose, which drains cash on the spike too — is exactly what `initial_margin_register.py:14-19`
describes and is **identically zero today**. A B6 that models only VM inherits a one-directional death.

### 1.10 R15 fail-open, verified empirically this pass (not inferred)

`observed-with-evidence` — executed, not reasoned. A single non-finite mark walks straight through the live
margin machinery and returns **"survived"**:

```
$ python3 -c "... nan = float('nan') ..."
max(0.0, -nan)                       = 0.0
max(250000.0, 1.5*nan)               = 250000.0     # facility silently floors
nan < 0.0                            = False
build_margin_calls_from_mtm({'CP1': {'netted_mtm_gbp': nan}}, ...)
  -> calls: 0   outstanding: 0   facility: 250000.0
breaking_strain_sweep({'CP1': 0.0}, {'CP1': nan})
  -> survived: True   death_cause: None   peak_call: 0   any_name_posted_margin: False
```

Three compounding fail-opens, each at a named line:

- `margin_call_book.py:194` `max(0.0, -netted)` — `max` is NaN-blind, so a NaN mark becomes **£0 margin**, then
  `:195` `if variation_margin <= 0.0: continue` **skips the counterparty entirely**.
- `margin_call_book.py:87` `max(FACILITY_MIN_GBP, 1.5 * gross)` — a NaN gross silently returns the **floor**.
- `collateral_death_test.py:160` `is_dead = net_liquidity < 0.0` — a NaN comparison is `False`, i.e. **alive**.

And the worst part is the *misdiagnosis*: the NaN path emits `any_name_posted_margin=False`, which the module's
own docstring (`:23-26`) instructs the reader to interpret as the **benign** §4 "hedge cover masking the
exposure" finding. **A corrupted mark is indistinguishable from a healthy long book.** This is precisely the class
memory records twice already (the E5 carbon ledger returning `nan` as a rate, git `83ccb913c`; the D5 ledger
non-finite hardening) — and a margin calculation, being a chain of subtractions on marked prices, is exactly that
shape. Registered here as a finding, **not fixed on sight** (SELF_INTERRUPT_DISCIPLINE: queue, don't patch).

### 1.11 DISCOVER verdict

**EXISTS and live:** VM-from-netted-MtM (one terminal snapshot), a book-scaled committed facility fixed at
origination, a post-hoc two-point breaking-strain sweep with a correct `collateral_while_solvent` vs
`collateral_insolvent` distinction, and a real `£1.39m` outstanding margin figure in the published run.
**EXISTS but dead:** OTC VM book with direction + T+1, initial-margin register, liquidity stress book, capital
adequacy, daily cash-position model with facility drawdown — five modules, ~800 lines, zero callers.
**DOES NOT EXIST:** any cash balance distinct from accumulated accounting margin; any margin posting that moves
cash; any settled/unsettled call lifecycle; any payment lag between call and payment; any daily mark path; any
initial margin; any banked clock on the run path; any `run_ledger.jsonl` row; any survival score; any published
surface for the one death measurement that does compute.

---

## 2. FRAME (design — nothing built)

### 2.0 The governing statement

> **B6's deliverable is not a margin calculator. It is a SECOND BALANCE ON A DIFFERENT CLOCK, and the seam
> between the two.** The margin calculator already exists (§1.1). What does not exist is a bank balance that can
> hit zero while the P&L is positive, because today there is one number serving both roles (§1.3).

Everything below follows from that. A BUILD that adds more margin machinery without splitting the balance has
built nothing B6 needs.

### 2.1 The four clocks, named, with the quantity each governs (R14)

Every quantity below carries its clock. A B6 figure published without one is a defect.

| Quantity | Symbol | **Clock** | When the number becomes true |
|---|---|---|---|
| Netted mark-to-market of the hedge book | `MtM_t` | **MARK** (daily observable forward close) | The moment the forward prints. Not cash. Not P&L. |
| Variation margin *called* | `VM_t` | **MARK** (call raised on day *t*'s mark) | Same instant as the mark. An obligation, not yet a payment. |
| Variation margin *paid* | `VM^paid_{t+δ}` | **BANKED** | `δ` = CSA settlement lag (T+1 standard, `otc_margin_book.py:57`). Cash physically leaves. |
| Initial margin held | `IM_t` | **BANKED** (posted at inception, returned at maturity) | Locked cash. Re-called upward when the CCP raises the multiple. |
| Wholesale energy cost | `C_settled` | **SETTLED** (half-hourly settlement) | The existing `net_margin_gbp` limb. |
| Customer revenue billed | `R_billed` | **BILLED** (bill issue date) | The invoice exists. No cash. |
| Customer revenue collected | `R_banked` | **BANKED** (DD collection date) | `= R_billed` shifted by billing + collection lag, minus non-payment. |
| Bank balance | `Cash_t` | **BANKED** | **The new variable. Does not exist today.** |
| Accounting net margin | `P&L_t` | **SETTLED/accrual** | Today's `treasury` accumulation (§1.3), which keeps its meaning — renamed, not repurposed. |

**The rename is load-bearing and is the first BUILD step.** `treasury_cash_balance_gbp` (`run_phase2b.py:1924`)
must become `cumulative_net_margin_gbp` — a settled-clock P&L accumulation, which is what it has always been —
freeing the name `cash` for the genuine banked-clock balance. Until that rename, every reader of that field is
being told a basis that is not true.

### 2.2 The death loop, in three sentences

1. The company is naturally **long** commodity forward (it buys ahead to cover fixed-price retail sales), so when
   the forward **falls** its netted MtM goes negative and its counterparties call variation margin equal to the
   *whole remaining tenor's* loss, payable in cash at T+1.
2. That cash leaves the bank as a **step** on the BANKED clock, while the offsetting benefit — cheaper energy for
   the remainder of the customers' terms — accrues as a **ramp** on the SETTLED clock over months and only
   becomes cash later still, after billing and DD collection.
3. Because the hedge is held against a matched forecast supply obligation, the MtM loss does **not** hit the
   accounting P&L (it is deferred against the unrecognised gain on the supply obligation), so the company can
   reach `Cash_t + Facility_undrawn < VM^paid` — dead — while `P&L_t` is positive and rising.

### 2.3 The timing asymmetry, made arithmetic

This is the quantity BUILD must actually compute. For a book of `Q` MWh covering a remaining tenor of `T` days,
against a forward move `ΔF < 0` on day `t`:

```
Cash OUT (BANKED, day t+1):   VM^paid = Q · |ΔF|            ... the WHOLE tenor's loss, in one payment
Cash IN  (BANKED, day t+1):   0
Cash IN  (BANKED, over T):    Σ_{s=t..t+T} (Q/T)·|ΔF| · 1[s + λ_bill + λ_collect]
P&L      (SETTLED, day t):    ≈ 0                           ... deferred hedge, matched obligation
```

Three named lags, each of which must be a real parameter and not a constant folded to zero:

- `δ` — **CSA variation-margin settlement lag.** T+1 is the market standard (`otc_margin_book.py:57` already
  encodes it). Today it is **zero** (`run_phase2b.py:696`, call date == deadline).
- `λ_bill` — **billing lag**: consumption settles, then a bill is issued. The BILLED clock.
- `λ_collect` — **collection lag**: bill issued, then the DD is presented and clears. The BANKED clock.

`inferred`, and this is the whole mechanism in one line: **the outflow is `Q·|ΔF|` at `t+δ`; the inflow is the
same total spread over `T` and delayed by `λ_bill + λ_collect`. The company's peak cash deficit is therefore of
order `Q·|ΔF|·(1 − (λ_bill+λ_collect)/T)` even when the trade is perfectly hedged and P&L-neutral.** If a BUILD
collapses any of `δ`, `λ_bill`, `λ_collect` or `T` to zero, the peak deficit collapses with it and the death loop
disappears — silently, with a green suite.

### 2.4 The two channels, and why B6 needs both

**Channel A — variation margin on a FALLING forward (the primary, and the one SPINE_3 §2.7.2 already commits to
supply).** Direction-specific: a long book posts only when the mark falls. The killer sequence is SPINE_3 §1.7c —
2022-08 £186.54 → 2022-10 £55.47, **−70.3% in two months**, computed there from the real on-disk record — against
a book bought at the peak. SPINE_3's acceptance leg D (`≤ −50%` two-month fall) exists for exactly this and is
not optional.

**Channel B — initial margin re-called on RISING VOLATILITY (the direction-agnostic amplifier).** A CCP raises
the IM multiple because volatility rose, not because the price moved a particular way, so IM drains cash on the
**spike** as well. This is why the code's own §4 note (`collateral_death_test.py:23-26`) that a long book "cannot
die to collateral" is true *only because IM ≡ 0 today* (§1.9). `inferred`: **without channel B, B6 can only ever
kill on the collapse leg, and a run whose window ends before 2022-08 can never be killed at all.** `IM_t` must
become a function of an observable volatility proxy, sized to a stressed holding period
(`initial_margin_register.py:10` already names the 5-day convention).

**What B6 must NOT do:** invent a third channel to make the death arrive. R12 and MC-2 §4 are explicit — if the
company survives, DIAGNOSE (R4), never shrink the facility or inflate a multiplier.

### 2.5 The minimum mechanism (five pieces, in dependency order)

Deliberately small. SIMPLICITY GUARD: no repository-over-JSON, no adapters-for-future-adapters. Four of the five
pieces are *connections between things that already exist*.

1. **Split the balance.** Rename `treasury_cash_balance_gbp` → `cumulative_net_margin_gbp` (settled clock, meaning
   unchanged), and introduce `cash_banked_gbp` as a genuinely separate accumulator fed only by banked-clock
   events. `is_administration_triggered` moves to read `cash_banked + facility_undrawn`, not the P&L sum.
   **Nothing else in B6 works until this lands.**
2. **A daily (or per-settlement-window) mark path**, replacing the single terminal snapshot at
   `run_phase2b.py:2533`. Marks come from the *existing* observable resolver
   (`CompanyTariffEngine.get_forward_price`, already used at `run_phase2b.py:2553-2560`). No new price source.
3. **A call → payment lifecycle with real latency (C-S3).** `MarginCallEvent` already carries
   `settlement_deadline` and a `SETTLED`/`DEFAULTED` status (`margin_call_book.py:7-11`) and `settle_call`
   already exists (`:102`) with **no caller**. B6 gives it one: a call raised on day `t` becomes a cash outflow
   on day `t+δ` — two separate events in time, never same-step resolution. `OTCMarginBook.cash_impact_gbp`
   (`otc_margin_book.py:65-69`) already models both directions incl. margin RETURN.
4. **Initial margin as a live term** (§2.4 channel B), reviving `initial_margin_register.py` sized off an
   observable volatility proxy.
5. **A revenue-to-cash conversion with `λ_bill` + `λ_collect`**, so `R_banked` is a lagged, leaky function of
   `R_billed`. The payment machinery to hang this on already exists on the run path
   (`run_phase2b.py:1907 _payment_triad.record_period`).

Scale-readiness: **C-S1** — a call arriving singly, late or out of order must be harmless (the `call_id`
idempotency at `margin_call_book.py:197-199` already gives this; extend it to the payment leg). **C-S2** — no RNG
in the margin path; replay reproduces `Cash_t` byte-identically. **C-S3** — §2.5.3 IS this constraint. **C-S4** —
the cash balance is derived from an append-only event sequence, not a mutable running float held in a loop
variable. **C-S5** — the lags `δ`, `λ_bill`, `λ_collect` are day-indexed; re-basing the clock requires rescaling
all three, so **time-scale invariance must be DECLARED FALSE** and registered as a named simplification.

### 2.6 The epistemic wall — what the company can and cannot see

**The company CAN see (observables, all of which already cross a real seam or are its own records):**

- Its **own trade blotter** and the observable forward prices it marks against
  (`company/interfaces/sim_interface.py:320-322 get_forward_price`).
- Its **own margin calls** — a call is a document a counterparty sends you. This is the purest observable in the
  whole atom: the company learns the size of its problem *by being told to pay*.
- Its **own bank balance**, its own bills, its own DD collections, its own committed facility and drawn amount.
- Published market data (spot, and per-tenor forwards once B4/`WVC_2` lands).

**The company CANNOT see, ever:**

- SPINE_3's storage state `S_t`, the pipeline-shock parameters, or anything that would let it anticipate the
  forward. Its hedge decisions must be taken on information available *before* the move.
- Its counterparties' internal IM models. It observes the *call*, never the model that produced it.
- Any future mark. `run_phase2b.py:642-644` already establishes the correct pattern — the price resolver reads
  only spot history *before* the mark date and raises `ValueError` on insufficient history, which the caller
  turns into "unmarked" (`:2559-2560`). B6 must preserve that failure mode, not paper over it.

**The company is ALLOWED to be wrong, and allowed to DIE.** `inferred`, and it is the point of the atom: a real
supplier in 2021/22 could not see the storage balance either. It hedged on a positive-winter belief
(`sim/forward_curve.py:88 GAS_MONTH_SEASONAL_MULTIPLIER`, a static dict which SPINE_3 §1.5 shows **cannot change
sign**), was structurally wrong, and several died. A B6 that quietly gives the company enough foresight to
survive has destroyed the finding.

**One design question flagged, not resolved:** SPINE_3 §3 Q3 asks whether the company receives a lagged published
storage feed. B6 inherits that ruling — it changes how early the company can see the crisis coming and therefore
how survivable the death loop is. **Do not resolve it here; it is director curriculum.**

### 2.7 The coupled triad

**SIM (SPINE_3 + B4).** Supplies a world that can defeat the capability. Per SPINE_3 §2.7, the contract is:
(1) a **daily per-tenor forward mark**, not just spot — VM is computed against a moving forward for the tenors
actually held, so a spot-only series gives B6 nothing to mark against; (2) the **collapse** leg, not only the
spike (acceptance leg D, `≤ −50%` over two months); (3) **speed** as a first-class quantity — the death is driven
by `ΔF/Δt`, not `F`; (4) daily emission cadence with the payment lag owned by B6; (5) parameterisable to a milder
shock so survival is also reachable. **SPINE_3 alone is necessary but not sufficient — B6 also needs
`B4_traded_product_ladder`** (SPINE_3 §3 Q4 raises exactly this ordering question and it is still open).

**COMPANY (this atom).** Discovers its own liquidity crisis through §2.6's observables: it sees its bank balance
falling and its margin calls arriving, and must decide — unhedge (crystallising the loss and losing cover), draw
the facility (finite), or fail. Its belief that winter > summer is structurally unable to invert (SPINE_3 §1.5),
so it will be wrong in a specific, mechanical, predictable way.

**HARNESS.** Three gaps, reported per digest into `docs/observability/coupled_gap_ledger.json`:

1. **The clock-divergence gap (the headline).** `P&L_t (settled)` minus `Cash_t (banked)`, tracked daily through
   the crisis window. In a healthy world it oscillates around zero; in the death world it fans out. **This single
   series IS the B6 score** — the gap is not a proxy for the finding, it is the finding.
2. **Liquidity-runway belief gap.** The company's own forecast days-of-cash (from
   `cash_flow_forecast.py`/`working_capital.py`, revived) versus realised. Measures how *late* it sees it coming.
3. **Margin-anticipation gap.** The VM the company provisioned for versus the VM actually called.

**What "DEFEAT" means numerically** — the triad law requires this to be a number, not a word. The world defeats
the company when, on the same run:

| | criterion | on which clock |
|---|---|---|
| (a) | `min_t (Cash_t + Facility_undrawn_t) < 0` — the company cannot meet a call even fully drawn | **BANKED** |
| (b) | `P&L_t > 0` at that same `t` — solvent on paper as it dies | **SETTLED** |
| (c) | the call that killed it arose **from a price move alone** — no injected loss at the cash line | MARK |
| (d) | `death_cause == "collateral_while_solvent"`, never `"collateral_insolvent"` | ledger |

(a)∧(b)∧(c)∧(d) is the acceptance shape. The distinction at (d) already exists and is already correct
(`collateral_death_test.py:186-189`) — B6 does not reinvent it, it makes it reachable from a *live run* rather
than a post-hoc sweep. **And per B6's own DoD the test must prove BOTH directions**: a milder shock must produce
survival with `min_t(Cash + Facility) > 0`. A world that always kills is as useless as one that never does.

**Neither atom reaches L3 alone.** SPINE_3 may not reach L3 until the company has been run against it and these
gaps measured; B6 may not be called complete until it has faced that world.

### 2.8 R13 — the baseline / curriculum split

**BASELINE — fidelity-to-reality, agent-buildable, decided blind to company P&L.** These are how real
counterparties actually operate, not difficulty settings:

1. **CSA variation-margin mechanics**: the OTM party posts, netting is per-ISDA-master, VM equals the netted
   replacement cost, VM is *returned* when the mark moves back. Already half-built (`otc_margin_book.py`).
2. **The T+1 settlement convention** `δ` — a market standard, externally anchored.
3. **Initial-margin convention**: posted at inception, sized to a stressed holding period (~5 days), re-called
   when the CCP raises the multiple, returned at maturity.
4. **Haircuts and eligible-collateral rules** — cash vs non-cash, and the haircut applied. Real CSA terms.
5. **Cleared vs bilateral treatment.** Partially present already:
   `wholesale_credit_exposure.py:60 _CLEARED_EXPOSURE_HAIRCUT = 0.10`.
6. **Billing and DD collection lags** `λ_bill`, `λ_collect` — calibrated to real UK supplier practice.
7. **The facility sizing rule** — already director-ruled at MC-2 §3 and **must not be re-opened by B6**
   (`margin_call_book.py:38-65`). `FACILITY_COVERAGE_MULTIPLE`/`FACILITY_MIN_GBP` are a named R10 simplification
   pending an external RCF-to-book anchor; **shrinking the facility to force a death is an R12 breach.**
8. The gap-measurement machinery, the oracle, and the R15 mutations (§2.9).

**CURRICULUM — DIRECTOR-RESERVED. The agent must NOT set these:**

1. **Which crisis the company lives through** — SPINE_3's shock magnitude, onset, ramp, persistence.
2. **The company's starting cash and committed facility *as a difficulty setting*.** Note the fine line: the
   facility *sizing rule* is baseline (7 above); a hand-set starting cash chosen to make the company die is
   curriculum. If a BUILD finds itself choosing an opening balance, it has crossed.
3. **Whether the company gets a lagged published storage feed** (SPINE_3 §3 Q3).
4. **The survival SCORE's weighting** — how mortality-by-collateral is weighed against other outcomes is a values
   decision about what the company is FOR (one-way door #6), and is already director-session gated
   (`collateral_death_test.py:28-34`). **B6 supplies the raw fields; it must not blend them into a scalar.**
5. **Whether the company is permitted to unhedge under duress**, and any policy limit on facility drawdown — a
   real board decision, i.e. a world-fact about governance, not a physical constant.

`inferred`, the sharpest ownership line: **the MECHANISM of dying is baseline; the SEVERITY of the world and the
SCORING of the death are the director's.** This FRAME chooses no severity.

### 2.9 R15 obligations at BUILD

No control counts as evidence until a mutation test proves it fires on its own named defect. The three killer
patterns, named concretely for this atom:

**TAUTOLOGY.** The trap here is subtle and specific: **`Cash_t` and `P&L_t` must be computed from independent
event streams.** If `Cash_t` is derived as `P&L_t + adjustments`, then "cash diverged from P&L" re-asserts the
adjustment term and **cannot fail while the code compiles** — the exact shape of SPINE_3's T2. Enforced
mechanically: a test asserting that the cash accumulator's inputs are banked-clock events only, and that the
module computing `Cash_t` does not import the module computing `P&L_t`. Second tautology to refuse: an acceptance
test that asserts `VM = Q·|ΔF|` where the generator computed `VM` as `Q·|ΔF|`. The oracle must be **external** —
built from `sim/gas_data/nbp_sap.csv` (the real replayed record, which the margin code neither reads nor writes)
and the book's own declared volumes, by a function that imports neither the margin book nor the run module.

**FAIL-OPEN.** Every one of these must be a **FAILED** check, never a silent pass:

- **Non-finite, checked FIRST, before any comparison.** §1.10 proves the live path fails open on NaN today at
  three separate lines. The rule (memory, twice-earned): reject non-finite *before* comparing, because `max`,
  `min` and `<` are all NaN-blind. Any of `netted_mtm`, `ΔF`, `VM`, `Cash`, `Facility` non-finite ⇒ hard fail.
- Empty or absent mark series; a mark path with fewer than 2 points (a one-point "path" is the current defect).
- `δ = 0`, `λ_bill = 0`, `λ_collect = 0`, or `T = 0` — a zero lag silently deletes the mechanism (§2.3), so a
  zero lag must be a **loud** failure, not a default.
- A facility of zero, or `available_cash_gbp` defaulting to `0.0` and being *taken as real* (the live default at
  `run_phase2b.py:625` is currently honest-but-inert; wired to the real balance it must never silently mean
  "cash is zero" when it means "cash is unknown").
- Missing `clock` label on any published B6 figure (R14 gate).

**FAIL-SILENT.** Two live instances to fix, both already observed (§1.5, §1.6):

- The bare `except Exception` swallows at `run_phase2b.py:2537-2540` and `:2570-2573` print a warning and
  continue. **An unavailable death test is a FAILED death test**, not a skipped one.
- The reducer drop at `annual_report.py:655` (§1.6) — the death measurement must reach a published surface, and a
  test must assert it does (R11: verify to the rendered value).

**Named defects and their required mutations** (each must go **RED**):

| id | named defect | mutation | must go RED on |
|---|---|---|---|
| **B1** | **Cash is still the P&L** (the split is cosmetic) | Feed the cash accumulator from `net_margin_gbp` instead of banked events | (a)∧(b): death and paper-solvency can no longer co-occur |
| **B2** | **No payment latency** (C-S3 collapsed) | Set `δ = 0` (call and payment same day) | the peak-deficit criterion |
| **B3** | **Revenue is instant cash** | Set `λ_bill = λ_collect = 0` | (a): the deficit closes |
| **B4** | **The mark path is a snapshot** | Replace the daily path with a single terminal mark (today's behaviour) | (a): a snapshot cannot produce a trajectory of calls |
| **B5** | **Margin never leaves the bank** | Raise calls but never settle them (today's behaviour, §1.4) | (a) |
| **B6** | **Initial margin is inert** | Set `IM ≡ 0` (today's behaviour, §1.9) | the spike-direction death only |
| **B7** | **Non-finite walks through** | Inject one NaN mark | Must FAIL, not return `survived=True` (§1.10 shows it currently returns survived) |
| **B8** | **The control cannot distinguish worlds (bidirectionality)** | Run against the baseline `history_replay` world and a milder shock | Must **PASS** (survive) there — a test that kills in every world is not a control |
| **B9** | **The finding is invisible** | Drop the B6 fields from the report reducer (today's behaviour, §1.6) | a published-surface assertion (R11) |

**Where R15 does not reach**, stated rather than papered over: the hedge-accounting deferral in §2.2 sentence 3
(*why* the MtM loss does not hit P&L) is a **modelling assumption about accounting treatment**, not a mechanism a
mutation test can falsify. It should be stated as a named R10 simplification with its real-world basis cited, and
its alternative (full fair-value through P&L, under which cash and P&L would move together and the divergence
would shrink) recorded as the thing that would falsify it.

---

## 3. Open questions (none block DISCOVER/FRAME; all block BUILD)

- **Q1 — Ordering with B4.** B6 needs a daily **per-tenor** forward mark (§2.7). Today only a single synthetic
  forward exists. Does `B4_traded_product_ladder` open before or alongside B6? SPINE_3 §3 Q4 asks the same
  question from the other side and it is still unanswered — **the two atoms are now both blocked on one ruling.**
- **Q2 — Does B6 own the survival ledger, or inherit it?** `run_ledger.jsonl` has never been written (§1.7) and
  the survival SCORE is director-session gated. B6's DoD says the mortality is "recorded by the survival score".
  Is B6 authorised to emit `RunManifest` rows (the raw fields only), or does it wait? **The scalar score itself is
  director-reserved either way (§2.8 curriculum item 4).**
- **Q3 — Does the MC-2 post-hoc sweep survive B6, or is it superseded?** Once the run has a live cash line, the
  two-point sweep becomes a second, weaker measurement of the same thing. Keeping both risks two numbers
  disagreeing on a published surface; deleting a director-ruled artefact is not the agent's call. **Recommend:
  keep the sweep as a *breaking-strain* diagnostic (its stated purpose) and let the live run own *mortality* —
  but the boundary needs the ruling.**
- **Q4 — Storage feed (inherited).** SPINE_3 §3 Q3, restated because it directly sets B6's survivability.
- **Q5 — `file_scope` correction.** The atom declares `saas/treasury` + `tests/saas/test_collateral_death_loop.py`,
  neither of which exists (§1.0), while the real surface is `simulation/run_phase2b.py`,
  `company/finance/margin_call_book.py`, `company/finance/treasury.py`, `company/trading/otc_margin_book.py`,
  `company/trading/initial_margin_register.py`, `company/risk/collateral_death_test.py`. Correcting a `file_scope`
  is also a **concurrency** matter (it is what the multi-atom disjointness gate reads), so it is proposed here and
  left for the orchestrator/map-writer rather than edited by a DISCOVER fork.

**Real-world figures BUILD must FETCH, not assume** (`observed-with-evidence` that they are unsourced today):
published UK-supplier RCF-to-book ratios (already registered as forward-discovery at `margin_call_book.py:55-58`);
real CSA variation-margin settlement conventions and eligible-collateral haircuts for GB energy OTC; the actual IM
multiples ICE/EEX applied to gas and power futures through 2021-22; typical UK domestic billing and DD collection
lags. **None of these may be filled from recall at BUILD.**

---

## 4. Level and saturation

**Proposed: `level_current` 0 → 1 (Skeletal). `level_current` is NOT edited by this pass — the cell is HELD at 0
and the move is a PROPOSAL.**

**Why L1 and not 0.** The L1 bar is *"Exists, simplified past realism"* / *"been BUILT in any form"*
(`MATURITY_MAP.md:50`). The atom's own headline capability — *"a hedge book that posts variation margin against a
moving forward"* — **is built in a skeletal form and is live in the production run**: real VM derived from real
ISDA-netted MtM at real observable forwards, a book-scaled committed facility, a breaking-strain sweep with the
correct `collateral_while_solvent` distinction, and £1.39m of outstanding margin in the published output (§1.1).
Holding the cell at 0 would mis-state the tree as empty and would send a BUILD fork to rebuild it.

**Why emphatically NOT L2.** The L2 bar is *"Mechanically real — genuine artefacts, happy path"*. Three of those
words fail: the margin never moves cash (§1.4), the divergence the atom is *defined* by is arithmetically
impossible because cash and P&L are one variable (§1.3), the sole death measurement is dropped before publication
(§1.6), and a single NaN returns `survived=True` (§1.10, executed, not inferred). "Simplified past realism" is
exactly right; "mechanically real" is not.

**The level is not moved here.** `tools/level_promotion_gate.py` refuses any unauthorized `level_current`
increase at commit time (MATURITY_MAP.md §0: the agent proposes with evidence and never moves a cell; R16 forbids
`--no-verify` on a `level_current` change; `MATURITY_MAP.md:138` — L1→L2 is the advisor's ratification, L3+ the
director's). This pass records the proposal in the atom's `simplifications` and in this document. **Precedent
followed:** `SPINE_3_gas_storage_crisis_regime` and `H29_import_time_env_capture_test_isolation`, which both
completed DISCOVER+FRAME, **held `level_current`**, and closed their re-draw treadmill by promoting the FRAME to a
real artefact rather than by bumping a level.

**Saturation.** This document is listed in the atom's `evidence:` list. `supervisor._atom_has_frame_doc`
(`background/supervisor.py:814`) marks an idle atom FRAME-saturated only when an `evidence` entry under
`docs/design/` with `FRAME` in its **filename** resolves to a real non-empty file — **an inline FRAME in the map's
`simplifications` list is a YAML string and does NOT saturate**, so an inline-only FRAME would re-hand this atom
to the idle draw every tick forever. **Only this atom's own FRAME is cited.** A sibling's FRAME is never listed:
on 2026-07-29 exactly that fail-silent defect was found and fixed on this atom (see the evidence-line comment in
the map). The mechanism's own docstring states the assumption: *every non-canonical `*_FRAME.md` is owned by
exactly ONE atom.* This one is owned by `B6_collateral_cash_death_loop`.

The atom leaves the idle DISCOVER/FRAME pool and re-enters via the BUILD draw when its gate opens (`loop_stage`
flips off `idle`, `depends_on: SPINE_3` satisfied). No orphan transition, no permanent hold.

---

## 5. Findings registered, deliberately NOT fixed on sight (SELF_INTERRUPT_DISCIPLINE)

Four live defects found this pass. Per SELF_INTERRUPT_DISCIPLINE the default is QUEUE, not patch — none is
blocking the machine, and all four fall inside B6's own future BUILD scope, so fixing them here would be building
under an idle gate.

1. **NaN fail-open in the live margin path**, three lines, empirically demonstrated (§1.10). Same class as the
   E5 carbon-ledger and D5 ledger incidents. `margin_call_book.py:87,194-195`; `collateral_death_test.py:160`.
2. **The MC-2 death measurement never reaches a published surface** (§1.6) — computed at `run_phase2b.py:2562`,
   dropped at `annual_report.py:655`. R11 orphan.
3. **Two bare `except Exception` swallows around the collateral machinery** (`run_phase2b.py:2537-2540`,
   `:2570-2573`) — an unavailable check reported as a warning and passed over. R15 fail-silent.
4. **`treasury_cash_balance_gbp` carries a false basis** (§1.3, §1.8) — a settled-clock P&L accumulation named as
   a banked-clock cash balance, with the insolvency test taken off it. R14.
