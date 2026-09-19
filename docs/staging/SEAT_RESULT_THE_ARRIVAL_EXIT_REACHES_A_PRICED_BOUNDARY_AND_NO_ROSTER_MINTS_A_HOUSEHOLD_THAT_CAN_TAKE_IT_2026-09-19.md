**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, "can the world's new SVT exit reach a priced boundary at all"

# The arrival-exit reaches a priced boundary, and no roster mints a household that can take it

*Nothing is broken. The question had two layers and they answer opposite ways: the arm's funnel
WOULD admit a household that took the new exit, and the world cannot produce one. Read as a single
question it collapses to the flattering half either way round — "the guard stops it" understates
what was built, "it can be priced" overstates what will happen.*

**Delivery seat, Lane 0, 2026-09-19.** Claim
`can-the-worlds-new-svt-exit-reach-a-priced-boundary-at-all`. No world was run for this and no
second `run_value_cycle_ab` was started; the floor run holds the box (PID 3432960, 12 seeds, since
2026-09-18). Everything below is the code path read at HEAD `7ea0d952a`, plus one schedule build on
the cached SSP feed that touches no shared artefact.

**Premise, re-measured before starting.** Both cited commits — `05684780e` (the arrival-exit) and
`209f26be4` (the refusal census) — are ancestors of `origin/main`. The draw flagged that as
possibly-spent work. It is not: this item cites them as *established facts to build on*, not as
work to land. The premise is intact and the item was workable as written.

---

## 1. The question, and the answer in one line each

> Can a household that takes the new arrival-exit land at a boundary where this supplier strikes a
> rate — all three membership conditions true — or does a guard stop it first?

**Conditional on taking the exit: IT CAN. No guard stops it.** Its first fixed term arrives at
`term_index = 4`, carrying `tariff_type="fixed"` and a struck rate, and clears every stage of
`company/pricing/value_based_renewal.margin_arm_uplift`.

**In a live run: NO HOUSEHOLD TAKES IT.** The guard is upstream of the arm and is not a guard at
all in the funnel's sense — it is `simulation/run_phase2b.resolved_tariff_type`, line 624,
`return record.get("tariff_type") or "fixed"`, standing over rosters in which every record carries
`tariff_type: None`.

So the item's operative conclusion is the one it anticipated — *no amount of compute will move
107* — but the reason is not the one it anticipated, and the difference is the whole value here.
The world does not owe "another edge". **The edge exists and is correct. What the world owes is a
producer of default-tariff arrivals.** §5.

---

## 2. The membership rule, and the four guards that could have refused

`tools/decisions_that_existed.STAGE_PRESENTED_A_DECISION` puts a renewal in the population when all
three hold: this supplier sells the fuel; a prior term existed; the supplier struck a rate for this
household. Each is a named stage in `margin_arm_uplift`
(`company/pricing/value_based_renewal.py:1300-1335`). Traced in the order they fire:

| # | Guard | Line | SVT-origin household's first fixed term | Verdict |
|---|---|---|---|---|
| 1 | `locked_unit_rate is None` → `no_locked_rate` | `value_based_renewal.py:1306` | struck rate `111.62` GBP/MWh, from `request_renewal_offer` | passes |
| 2 | `term_index < MIN_TERM_INDEX_FOR_UPLIFT` (=1) → `acquisition_term` | `value_based_renewal.py:1309` | `term_index = 4` | **passes — see §3** |
| 3 | `commodity not in UPLIFTABLE_COMMODITIES` → `not_the_arms_commodity` | `value_based_renewal.py:1313` | electricity | passes |
| 4 | `tariff_type not in UPLIFTABLE_TARIFF_TYPES` (`{"fixed","pass_through"}`, `company/crm/customer_profitability.py:316`) → `product_not_upliftable` | `value_based_renewal.py:1317` | `"fixed"` | passes |
| 5 | `observed_account_state(...) is None` → `no_observed_history` | `value_based_renewal.py:1332` | a full cap year of settled rows in the 1-year window | passes — see §4 |

Past stage 5 the renewal is **in the population by construction**: `STAGE_NO_OBSERVED_HISTORY`,
`STAGE_DECLINED` and `STAGE_PRICED` are the three members, and the household lands in one of them.

---

## 3. The guard that should have stopped it, and the reason it does not

The obvious failure mode — and the one worth writing down, because it is what I expected before
reading — is that a household arriving on the cap and converting at its first anniversary reaches
that conversion as **term 0**, and dies at `acquisition_term`: the stage that already refuses 227
renewals on the live book, with the reason *"term 0. This is the household's FIRST term with us."*

It does not, and the mechanism is two lines in a different module:

```
simulation/run_phase2b.py:1875    term_index = term_indices[cid]
simulation/run_phase2b.py:1876    term_indices[cid] += 1
```

`term_indices` increments on **every term in `all_terms`**, with no branch on `tariff_type`. A cap
segment consumes an index exactly as a fixed term does. So the arrival household's cap stint spends
indices 0..N-1 before its first fixed term is reached, and that term is `N`.

Measured rather than argued, on the cached SSP feed (2016-06-01 → 2023-12-31), one resi household
acquired 2016-10-01, built both ways through `simulation.renewals.build_renewal_schedule`:

```
tariff_type='fixed'  (the live shape)          tariff_type='svt'  (the new arrival-exit)
 idx=0 2016-10-01 fixed  99.25                  idx=0 2016-10-01 svt    140.0
 idx=1 2017-10-01 svt   140.0                   idx=1 2017-01-01 svt    140.0
 idx=2 2018-01-01 svt   152.5                   idx=2 2017-04-01 svt    140.0
 idx=3 2018-04-01 svt   152.5                   idx=3 2017-07-01 svt    140.0
 idx=4 2018-07-01 svt   152.5                   idx=4 2017-10-01 fixed  111.62   <-- FIRST FIXED
 idx=5 2018-10-01 fixed 145.00  <-- post-SVT    idx=5 2018-10-01 fixed  145.00
```

`term_index = 4 >= 1`. The guard is passed with three indices to spare, and it would be passed by
any arrival whose cap stint contains at least one segment — which every stint does, because a cap
period is at most a year and the stint is a year.

**This is a property, not today's answer.** The thing that makes it true is that `term_indices` is
keyed to *terms the builder appended*, not to *terms the arm would price*. A future edit that made
the index skip indexed tariffs — which looks like a tidy-up — would silently drop every post-SVT
conversion, on the rolled route as well as this one, into `acquisition_term`. That is a control
worth having and this repo does not have one. Filed as owed in §6.

---

## 4. Why stage 5 is not the quiet refusal, and the evidence needs no run

`observed_account_state` (`value_based_renewal.py:1406`) filters settled rows by billing account,
by commodity, and by `settlement_date < term_start` inside a one-year window
(`OBSERVATION_WINDOW_YEARS = 1`, line 1141). **It has no tariff filter.** A cap year settles —
`simulation/hedged_settlement.py` branches on `"deemed"` and `"flex"` and never on `"svt"` — so the
window is full.

The decisive evidence is that **this boundary kind already exists in the live book and is already
priced.** A household that ROLLS onto the cap mid-tenure (C1b, controlled since 2026-08-30) reaches
a fixed term after a cap stint by exactly the same route; that is `idx=5` in the left-hand column
above, and it is in the live run today. On the published feed
(`site/data/value_arms.json`, `run_generated_at 2026-09-18T05:43:40Z`), `no_observed_history`
counts **zero**:

```
2,824 offered = 2,490 product_not_upliftable + 227 acquisition_term + 104 priced + 3 declined
decisions_that_existed = 107   priced_share = 0.972
```

The arithmetic closes exactly, so no fifth stage fires at all. Every boundary that cleared guards
1–4 had observed history, including the post-cap conversions already in the book.

The arrival-exit therefore introduces **no new KIND of boundary.** It produces one more instance of
a boundary the arm already prices. That is the strongest form the answer can take, and it is why it
does not need a run to settle.

*(Kept apart, as the direction required: the `inference_claim` population of 54 and the 104 scored
decisions are two censuses of different things. Nothing above differences them.)*

---

## 5. And yet: nothing in this world can take the exit

`resolved_tariff_type` is the only route by which a `tariff_type` reaches
`build_renewal_schedule`'s SVT branch (`simulation/renewals.py:131`):

```
simulation/run_phase2b.py:624    return record.get("tariff_type") or "fixed"
```

Measured at HEAD, over the live rosters:

```
CUSTOMERS            226 records   tariff_type: None x226   ->  resolved: fixed x226
SUCCESSOR_CUSTOMERS    6 records   tariff_type: None x  6   ->  resolved: fixed x  6
```

**232 of 232.** No roster record carries `"svt"`, `DrawnCustomer.tariff_type` defaults to `None`
(`simulation/population_draw.py:257`), and the only producer of the string is
`build_svt_schedule` itself. The arrival-exit is reachable code guarded by an unreachable input —
which is precisely what `05684780e`'s own message said it was, and this measurement confirms it
still holds twelve commits later rather than assuming it does.

So the two layers are:

- the **arm** would admit an arrival household's conversion, and needs no change;
- the **world** has no producer of an arrival household, and that is the whole of the gap.

---

## 6. Pre-registration, filed before the answer can be known

Both halves are falsifiable and neither has been measured against a run that does not yet exist.

**P1 — the one the direction asked for.** The next completed `run_value_cycle_ab` on the current
roster will report `decisions.decisions_that_existed = 107` and
`priced_share_of_the_decisions_that_existed = 0.972`, **unmoved by `05684780e`**. The arrival-exit
contributes exactly zero boundaries because no household enters it.

*What would make P1 wrong, and none of these would refute the trace above:* a roster change landing
a record with `tariff_type` set; the acquisition funnel winning accounts that shift the book's
product mix (this moves 107 for reasons unrelated to SVT); a different seed or window; another lane
changing `MIN_TERM_INDEX_FOR_UPLIFT`, `UPLIFTABLE_TARIFF_TYPES` or the `term_indices` increment. If
107 moves, **read the funnel's stage counts before attributing it to this edge** — the honest
attribution needs `product_not_upliftable` and `acquisition_term` read together, because a move in
107 with `acquisition_term` also moving is the term-index mechanism of §3, not a new arrival.

**P2 — the conditional half, and the only one an experiment could settle cheaply.** Give one
roster record `tariff_type: "svt"` and re-run: that household's conversions appear in `priced` or
`declined`, **not** in `acquisition_term`, and `no_observed_history` stays at zero.

*What would make P2 wrong:* `term_indices` not counting cap segments (refuted by measurement in
§3); the cap stint failing to settle; a guard between `decide_renewal_rate` and `margin_arm_uplift`
that I did not find — the arithmetic in §4 closes to the unit, so there is no room for one, but an
unfired guard is a missing test until it fires.

**P2 is not a change I am making.** Whether the drawn book should carry default-tariff arrivals is
a fidelity determination, and it must be decided blind to what it does to 107 (R13). This
pre-registration exists so that, when it is decided, the prediction was already on the record.

---

## 7. What is owed, in priority order

1. **A control on the term-index property.** Nothing asserts that a cap segment consumes a term
   index. The `run_phase2b.py:1876` increment is what puts every post-SVT conversion past
   `acquisition_term`, on the rolled route that is live today as much as on the arrival route, and
   a tidy-up that skipped indexed tariffs would pass every existing test while silently emptying
   the population of its conversions. One control over the partition — a schedule containing a cap
   stint yields a post-stint fixed term whose index is `>= MIN_TERM_INDEX_FOR_UPLIFT` — keyed to
   the property and not to `4`.
2. **A producer of default-tariff arrivals**, if and when the fidelity determination admits one.
   `docs/design/DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` is where that question lives. A
   SoLR intake and an acquired default book are both real GB events and both mint exactly this
   record.
3. **Nothing on the arm.** `UPLIFTABLE_TARIFF_TYPES` is correct, the SVT refusal is correct, and
   `SEAT_DECISION_AN_SVT_HOUSEHOLD_IS_NOT_A_DECISION_THIS_ARM_DECLINES_2026-09-07.md` §3 stands
   unchanged. This finding does not reopen it.

---

## 8. Evidence

- HEAD `7ea0d952a`. Premise commits `05684780e`, `209f26be4` both ancestors of `origin/main`.
- Guards: `company/pricing/value_based_renewal.py:1306,1309,1313,1317,1332`;
  `company/crm/customer_profitability.py:316,354`.
- Index mechanism: `simulation/run_phase2b.py:1875-1876`. Arm call site for every term:
  `simulation/run_phase2b.py:1894-1919` (`decide_renewal_rate`, outside the `term_index >= 1`
  branch at line 2198, which is why the funnel carries all 2,824 boundaries).
- Arrival branch: `simulation/renewals.py:131-160`. Upstream gate:
  `simulation/run_phase2b.py:624`.
- Schedule build: cached SSP 2016-06-01 → 2023-12-31, 132,943 records, resi, `eac_kwh=3100`.
  Read-only; no artefact written.
- Funnel counts: `site/data/value_arms.json`, `run_generated_at 2026-09-18T05:43:40Z`.
