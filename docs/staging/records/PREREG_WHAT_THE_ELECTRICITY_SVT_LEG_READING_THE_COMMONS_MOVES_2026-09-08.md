**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a-scalar-copy-of-one-row-of-a-published-series-is-invisible-to-every-census

# Pre-registration: what the electricity SVT leg reading the commons moves, and what it must not

**Written 2026-09-08, Lane 0 delivery, BEFORE any measurement.** Claim:
`the-electricity-svt-leg-reads-the-commons-and-the-epg-rows-move-alone`.

Predecessor: `docs/staging/SEAT_RESULT_THE_ELECTRICITY_SVT_TABLE_IS_A_SECOND_HOME_2026-09-08.md`,
whose "what is next, in order" item 1 asked for exactly this and asked for this file first.

---

## I am not doing what the item asked first, and this says why before the answer is known

The drawn item says: *move the three EPG rows (2022-10, 2023-01, 2023-04) ALONE first as the
one-variable version.* That would set the electricity SVT reference to **34.0p/kWh** across
Oct-2022–Jun-2023, because that is what the commons returns as the *binding* instrument and it is
what an SVT household was charged.

**It is what the household was charged and it is not what the supplier received.** The Energy Price
Guarantee did not lower supplier revenue; it lowered the customer's bill and HM Treasury paid the
supplier the difference. This tree already holds that fact, in its own words:

> `company/regulatory/epg_reconciliation_register.py`, lines 6–12: *"Suppliers applied the EPG rates
> to all bills … HM Treasury paid suppliers the difference between EPG rates and their [actual
> rates]"*.

**That register has no production caller.** Grepped this worktree: the only importer is its own test
module. So the world has no HMT receipt leg. Setting the rate `simulation/svt_product.py` bills at
to 34.0p, with no subsidy leg behind it, would take roughly half the unit revenue out of the
company's Oct-2022–Jun-2023 book and call it fidelity. It is the opposite: a real GB supplier was
made whole in exactly those quarters, and that is the single most load-bearing window in the whole
2016–2025 record.

**The defect is one level up from the three rows: the accessor answers two different questions with
one number.** `get_svt_elec_rate_gbp_per_mwh` is read as *the published cap* by
`competitor_reference` (its own docstring: *"`simulation/svt_rates.py` is the published cap series
and is the anchor and the ceiling here"*), as *what the supplier bills* by `svt_product`, and as
*what a switching household compares against* by `customer_events`. Outside Oct-2022–Jun-2023 those
three are the same number, so nothing had to choose. Inside it they differ by 33p/kWh. This is
CLAUDE.md's *"before measuring a thing, say what it is"* shape, and the rule it carries — **the
cause split follows from the definition, never the reverse** — is why the definition is settled here
and the EPG rows are NOT moved in this increment.

## What I am doing instead

**The electricity leg reads the commons on the OFGEM CAP row** — the published `elec` level per
window — for every date the cap has existed, exactly as the gas leg reads the commons, with the
pre-2019 years staying a table because there was no cap to read. The three EPG rows keep the cap,
because the cap is the question this accessor answers, and the module says so in words for the first
time.

This is chosen over the alternative because **it changes no consumer's meaning**. Every call site
already believes it is reading the published cap. The EPG/household-charged question becomes a
named, filed gap with the orphan register as its evidence, instead of an implicit answer nobody
wrote down.

---

## Predictions

### P1 — arithmetic, provable without the book, and stated so it can be wrong

The accessor changes value on **exactly** these spans and no others, across 2016-01-01..2029-12-31:

| Span | from (p/kWh) | to (p/kWh) | why |
|---|---|---|---|
| 2020-01-01 .. 2020-03-31 | 17.81 | 17.85 | table is quarterly, the window was six-monthly |
| 2023-01-01 .. 2023-03-31 | 67.00 | 67.47 | transcription |
| 2023-04-01 .. 2023-06-30 | 30.10 | 50.60 | the Jul-2023 cap sat in the Apr-2023 slot |
| 2023-07-01 .. 2023-09-30 | 30.10 | 30.11 | transcription |
| 2023-10-01 .. 2023-12-31 | 27.40 | 27.35 | transcription |
| 2024-01-01 .. 2024-03-31 | 27.40 | 28.62 | a window late |
| 2026-01-01 .. 2026-12-31 | 26.00/25.50/25.00/25.50 | 27.69/24.67/26.11/26.32 | extrapolated over a published series |
| 2027-01-01 .. 2029-12-31 | 25.00 declining to 22.50 | 26.32 throughout | the standing instrument stands |

**Unchanged, and this is the half that can refute me:** every date in 2016, 2017, 2018, 2019, 2021,
2022, 2025, and 2024-04-01..2024-12-31, and 2020-04-01..2020-12-31. If ANY of those moves, the
delegation is not doing what I think it is.

### P2 — the direction of the money, which I do not have a number for

Two of the eight moves are large and both are **upward**: 2023-04 by +20.50p/kWh over one quarter,
2024-01 by +1.22p/kWh over one quarter. I predict:

* **Revenue rises**, concentrated in Q2-2023, because `svt_product` bills SVT households at this
  rate directly.
* **Churn falls slightly in Q2-2023**, because a higher cap raises the competitor reference and the
  company's own rate is clamped at that ceiling, so the company looks relatively cheaper.
* **2016–2019 is bit-for-bit identical.** This is the one prediction that does not depend on any
  mechanism, only on causality: nothing before 2020-01-01 reads a value that moved.
* **2024 and 2025 move and I cannot attribute them.** Eight rows change at once and the book is
  path-dependent through churn and renewal composition. Writing that down now is the point: if I
  report a 2025 figure after the fact and reason backwards to which row caused it, that reasoning is
  invalid and this paragraph is the evidence I knew it in advance.

### P3 — the one that worries me, registered so it cannot be quietly dropped

2023-04 moving from 30.10 to 50.60 takes the number **further** from the 34.0p an SVT household
actually paid. For the household-facing consumers (`customer_events._price_differential_vs_market`,
the churn reference) that is worse, not better. **I claim it is still right**, because 30.10 was the
wrong window's cap and its nearness to 34.0 is a coincidence, not a mitigation — a wrong number that
happens to land near a right one is this project's most expensive recurring shape and is not a
reason to keep it. But the EPG gap at those consumers is now larger and named rather than
accidentally masked, and if the book measurement shows Q2-2023 churn moving materially on this, that
is evidence the household-charged accessor is urgent rather than merely correct.

### What this increment does NOT do, stated so nothing reads as done

* No HMT reconciliation leg is wired. `EPGReconciliationRegister` stays an orphan.
* No consumer is re-pointed at a household-charged rate. That accessor is not added here.
* **The book is not measured in this turn.** A `--fast` full run was started at HEAD and reached
  2016-02-29 in four minutes: the decade is ~4 hours, twice over for before/after, and it does not
  fit. It is handed on as the next increment and it is the reason P2 is a prediction rather than a
  result.
