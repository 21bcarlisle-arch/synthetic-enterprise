**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `the-companys-churn-belief-is-flat-across-the-book-where-the-world-responds-nine-fold`) · **Class:** measurements_that_mirror

# RESULT — the company's churn belief is flat in household size, exactly where the world's response is steepest

The drawn item's four lines reproduce exactly on this tree at `fcd9857e9`:
`enriched_churn_estimate(250.0, 280.0, 3.0, eac, segment="resi")` returns **0.166000** for
eac ∈ {1500, 3100, 6000, 12000} — byte-identical — and **0.436833** at 25,000.

Instrument: `tools/churn_belief_size_response.py` → `docs/observability/churn_belief_size_response.json`.
Control: `tests/tools/test_churn_belief_size_response.py`, one function over the whole partition,
mutation record in its docstring.

---

## 1. Where the step is, and what makes it

`estimate_churn_probability` touches `annual_consumption_kwh` in exactly one place
(`company/crm/churn_model.py:314-315`):

```python
prev_annual_bill_gbp = old_rate_gbp_per_mwh * annual_consumption_kwh / 1000.0
bill_stress = bill_stress_sens * max(0.0, prev_annual_bill_gbp / bill_stress_threshold - 1.0)
```

**It is an absent term, not a band with wrong edges and not saturation.** The item offered three
readings and only one survives:

- *Not saturation.* The estimate moves freely with price at every consumption — the item's own
  offer sweep established that, and a saturated term would flatten both axes.
- *Not a mis-placed band edge.* That is the flattering reading, because it implies a tuning fix.
  `bill_stress` is a financial-**distress** term and the module says so in terms: *"a customer who
  spent £11,000/year last year at crisis prices is under more financial stress than rate % alone
  shows"*. Distress above a threshold is a different quantity from household size. The model has
  **no size term at all**; moving the edge would not give it one, it would only move where
  distress starts.
- *Not an equivalence.* The world genuinely responds to size across this book (§3), so the
  flatness is a real difference the belief cannot express.

Below the threshold `max()` returns exactly `0.0`, so ∂(belief)/∂(consumption) is **exactly** zero,
not merely small.

### The step is in POUNDS, and the item's "above 12,000 kWh" is rate-specific

12,000 kWh is where the knee sits *at £250/MWh only*. Derived by bisection from the estimator
itself, at three rates this book was actually billed across:

| old rate | knee (kWh) | knee (prev annual bill) |
|---|---|---|
| £150/MWh | 20,000 | **£3,000.1** |
| £250/MWh | 12,000 | **£3,000.0** |
| £400/MWh | 7,500 | **£3,000.3** |

One bill, three consumptions — a **2.67× spread in kWh**. A control keyed to 12,000 kWh would go
red the next time the price deck moved and stay green while the mechanism rotted, so the control
keys to the property (*the knee is a bill*) and reports the constant only as a cross-check.

### The threshold's own position is unsourced

`BILL_STRESS_THRESHOLD_GBP = 3000.0` appears in `tools.domain_constant_origins --list` — this
repository's own register of domain constants carrying no origin — and the docstring justifies it
as *"the threshold where empirically customers start actively switching"* while citing nothing.
**Reported, not repaired.** The knee's position is not what this measures, and re-picking an
unsourced number replaces one invention with another. It is a finding in its own right.

---

## 2. The book, and the one thing that could not be established

**The 154 settled billing accounts behind `site/data/value_arms.json` have no per-account rows on
disk.** `value_cycle_ab_s1_three_arm_20260918.json` carries `book_identity` *counts* and mentions
`phase2b.all_records` only inside prose strings; the records themselves are never written out.
Reconstructing them means re-running the arms. This is stated rather than smoothed over —
`generate_value_arms_data` already refuses to bound the 09-18 arms with a 164-account family for
exactly this reason, and substituting one book for the other silently would be that same defect.

So the distribution is measured on the book this tree **does** hold per-account,
`site/data/customers.json` — 164 billing accounts, 244 supply legs:

| | |
|---|---|
| legs **below** the knee | **235** |
| legs **above** the knee | **9** (7 resi, 2 SME) |
| share below | **96.3%** |
| leg annual bill | min £9 · p10 £394 · p50 **£739** · p90 £1,631 · max £13,175 |
| leg annual kWh | min 35 · p10 1,623 · p50 3,760 · p90 12,976 · max 41,576 |

The knee sits at **4.1× the median leg's annual bill**. Each leg's bill here is its whole annual
revenue with the standing charge *included*, while the model takes the standing charge back out —
so this **overstates** the model's input and can only move legs *into* the above-knee set. The
load-bearing claim is the count below, and overstating is the direction that cannot flatter it.

**One of the nine is the argument in miniature.** `PROS-2024-0197` consumes **3,567 kWh/yr** — a
small flat, below this book's own median — and clears the knee on a £4,380 bill, because it was
billed at a crisis-era rate. Meanwhile `PROS-2016-0098` at **11,488 kWh** sits barely above and
238 larger-than-median households sit below. A term that admits a 3,567 kWh household and excludes
most 6,000 kWh ones is not sorting households by size; it is sorting them by bill. That is the
distress reading of §1, arriving from the data rather than from the docstring.

Whether the 154-account book fell differently against the knee is **NOT ESTABLISHED**.

---

## 3. The world, over the same book

`churn_position_multiplier(0.12, bill_scale_for(segment, bill))` across this book's own households:

| | |
|---|---|
| min | 1.0 |
| p10 | 1.2 |
| p50 | 1.6 |
| p90 | 2.7 |
| max | 11.7 |
| **spread** | **11.57×** |

The world scales the price differential by each household's **own** annual spend, on published
evidence (Ofgem/BMG *Understanding Consumers' Energy Tariff Choices*, n=3,235: consumers value
savings in absolute pounds, not as a share of their bill).

### The asymmetry is exact, and it is sharper than "the belief is flat"

`bill_scale_for` returns the household's own bill for **domestic** supply and `None` — the
market-average scale — for every non-domestic segment. That is deliberate and documented: a
domestic switching curve run on a 4 GWh chemical plant returned a churn multiplier of ×599.6.

So the world is flat in size for SME/I&C **by construction**. And the company's belief is the
mirror image:

| | world varies with size? | belief varies with size? |
|---|---|---|
| resi, below £3,000 (235 of 242 legs) | **yes** (1.36 → 8.60 across the probe) | **no** — 0.166 at both |
| resi, above £3,000 (7 legs) | yes | yes |
| SME, either side | **no** — 2.232 at both | **yes** — 0.166 → 0.437 |

**The one segment where the company's belief varies with size is the segment where the world's
does not, and it is deaf to size exactly where the world listens hardest.**

---

## 4. What this says, and what it does not

A per-customer belief that is constant in the dimension the world reacts to is **a flat rule
wearing a per-customer name in that dimension** — which is precisely the baseline the thesis has
to beat. This is an account of why the selection leg has nothing to show, and it cost one
invocation and no run.

It does **not** price the gap. It does **not** instruct anyone to make the belief vary; R12 stands,
outputs are diagnostics and never targets. And no wall moves either way — a real supplier meters
its own customers, which is why the world's own `churn_position_multiplier` calls consumption
*"something the company can legitimately act on"*.

One thing this sharpens rather than restates: `renewal_rule_price_response.json` already lists
`eac_kwh` under `inputs_that_reach_the_price`. That row is true, and it is true through the
**volume** channel of the value objective. It says nothing about the churn belief, and reading it
as "consumption is heard" is the misreading this result closes.

---

## 5. Landed

- `tools/churn_belief_size_response.py` — the producer
- `tests/tools/test_churn_belief_size_response.py` — one control over the whole partition, six
  mutations run against injected module copies (four caught, two equivalences, baseline silent)
- `docs/observability/churn_belief_size_response.json` — the artefact
- `background/process_run_complete.py` — wired to regenerate **immediately after**
  `site/data/customers.json`, the book it counts. Generated against the previous run's book it
  would publish a census of a population the company no longer holds, which is the defect
  `WORKER_FINDING_THE_AB_ARTEFACT_CANNOT_NAME_THE_BOOK_IT_RAN_ON_2026-08-26` names one artefact over.

**Owed, and not done in this invocation:** the block on the arms page beside the selection leg.
`tools/generate_value_arms_data.py` and `site/data/value_arms.json` were held by a concurrent lane
(`the-republished-seed-price-carries-an-unbounded-count-in-every-artefacts-own-bytes`) with a
`surgical_land --merge origin/main` running against those exact paths while this was built, and the
generator's own architecture is that it **reads** artefacts and never measures — so the measurement
had to exist as an artefact first regardless. The feed block and the page render are the next
increment and the artefact they read is now on disk.
