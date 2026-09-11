# [WORKER FINDING] Every customer's first direct debit is set from half a month, so every first year demands a ~100% increase

**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** unminted
**Found:** 2026-09-01, by the delivery seat, following the director's cause (b) into our own DD register.
**Knowledge:** `docs/market_research/satisfaction_drivers_and_the_three_bill_shocks.md`, Part 2(b).

## The symptom, against a published band

`annual_dd_review` over the record: 806 reviews, 522 increases, **431 flagged `large_increase`**,
average variance **+106.2%**.

| | Ofgem, Feb–Apr 2022 (the worst quarter in the GB record) | our world, whole record |
|---|---:|---:|
| DD increases above **100%** | **8%** of SVT customers | **31.0%** (162 of 522) |

Ofgem required every supplier that raised a DD by more than 100% to re-review it. **Over 900,000
direct debits** fell into that exercise; it produced twelve compliance engagements and an
enforcement order. Our world produces those increases at roughly **four times that rate, as its
steady state.**

## It is not the energy crisis, and the years say so

| year | n | median var% | mean var% | increases >100% |
|---|---:|---:|---:|---:|
| 2017 | 80 | **+74.1** | **+222.3** | 35 of 65 |
| 2019 | 72 | +12.7 | **+232.0** | 7 of 55 |
| **2022** (the crisis) | 100 | **+32.6** | +111.3 | 20 of 91 |
| 2023 | 99 | +80.9 | +95.4 | 38 of 96 |
| 2025 | 85 | −21.2 | +33.1 | 5 of 12 |

**2017 and 2019 — ordinary years — are worse than 2022.** If this were price volatility, the crisis
would dominate. It does not.

## It is the FIRST review, entirely

| review window | n | median var% | increases >100% | median standing DD |
|---|---:|---:|---:|---:|
| **0 (first)** | 222 | **+102.1** | **111 of 195 (57%)** | **£23.13** |
| 1 | 162 | +18.2 | 14 of 118 | £47.50 |
| 2 | 109 | +7.8 | 3 of 64 | £55.00 |
| 3 | 85 | +4.5 | 7 of 41 | £53.00 |
| 4 | 66 | −3.4 | 3 of 24 | £53.00 |

After the first correction the mechanism is well behaved — windows 2–4 sit inside ±8%, which is
about the SLC 27B ±5% tolerance. **The entire defect is the number the DD starts at.** At window 0
the median standing DD is **£23.13** against a median recommendation of **£50.50**.

*(Window 6 spikes to +92.5%, and that one IS the crisis: window 6 for the 2016-acquired cohort is
2023. Two real effects, and the first one dominates.)*

## The root cause, in one line

`company/billing/dd_review_runner.py:155`

    standing_dd = seq[0][1]  # initial estimate = first issued bill

**The initial direct debit is one month's bill — and 85% of first bills are not a month.**

| | |
|---|---|
| first bills covering **fewer than 28 days** | **213 of 251 — 84.9%** |
| median first-bill period | **16 days** |
| median first bill | **£25.55** |
| median full-month bill | **£60.66** |

£25.55 against £60.66 is a factor of **2.37**, which is almost exactly the window-0 gap (£23.13
against £50.50, **2.18**). **The initial DD is set to roughly half a month's cost, so every
customer's first annual review demands a doubling.**

### Seasonality is a real second-order effect on top of it

Because a monthly bill is seasonal, *which* month you were acquired in also matters — but it is the
smaller term, and every month is positive, which is what identifies the stub as the first-order
cause:

| acquisition | n | median window-0 variance |
|---|---:|---:|
| **Summer (May–Aug)** | 84 | **+155.6%** |
| **Winter (Nov–Feb)** | 65 | **+71.8%** |

Worst single months are August (+280.8%) and September (+229.5%) — a first bill taken at the bottom
of the demand curve, then billed through a winter.

## Why this is exactly the director's cause (b)

His words: *"a direct debit set too low so the account slides into debit and the fix is a big
increase, which is a supplier failure the customer experiences as a price rise."*

Our world does this **to every customer, in their first year, at roughly twice the magnitude of the
worst quarter in the published GB record** — and routes none of it into their experience, because
`bill_shock_pct` is computed from bill totals and 71% of the book pays a level DD. So the world
commits the failure, records it in a register, flags it `large_increase`, and the household never
notices.

## CORRECTION — the mechanism above is WRONG, and a practitioner caught it (director, 2026-09-01)

> *"There's no such thing as a half-month direct debit — an annualised plan divides estimated annual
> cost by twelve whatever the start date. You read a first billing period of half a month and
> treated it as the DD amount."*

**He is right, and the title of this document is wrong.** Everything above stays.

### What survives

The measurements. `dd_review_runner.py:155` really does read `standing_dd = seq[0][1]`. The first
review really is the whole story: median +102.1%, 111 of 195 increases above 100%, windows 2–4
inside ±8%. 85% of first bills really do cover fewer than 28 days, median 16.

### What does not

**The frame.** I treated "a DD set from half a month" as a coherent object that is simply too small
by a factor of two. It is not an object at all. **A direct debit is an annualised plan: estimated
annual cost ÷ 12, whatever the start date.** A supplier does not set your monthly payment to your
first bill, and it certainly does not set it to a stub. So the code is not setting a DD *badly* —
**it is not setting a DD.** "Off by a factor of 2.37 because the first period is half a month" reads
as a calibration error in a real mechanism, and there is no real mechanism there to mis-calibrate.

**And the seasonality reading goes with it.** Summer acquisitions +155.6% against winter +71.8% is a
true statement about what this code does, and it is *not* evidence about how DD-setting behaves,
because the thing it measures the seasonality OF does not exist. It must not be carried forward as a
finding about the world. I presented it as "a real second-order effect on top", which claimed
exactly that.

### What the real defect is, per the director

> *"The DD is only as good as the estimated annual consumption behind it: when that estimate is
> wrong the account drifts into credit or debit, and the correction arrives later as a change the
> customer didn't expect."*

That is a different and better defect, and it is the one worth modelling. The chain is
**EAC error → balance drift → an unexpected correction**, and each link is a thing a supplier
observes and a customer experiences. Our world has none of it: no EAC behind the DD, so no drift
that means anything, so a "correction" that is an artefact of a first-bill placeholder rather than a
consequence of a wrong estimate.

Note that the repair this document proposed — 1/12 of an estimated annual cost, from the EAC the
company already holds — happens to be right. **It was right for the wrong reason.** I proposed it as
a fix to a magnitude; it is actually the introduction of the mechanism.

### How this got past knowledge-first, which is the part worth keeping

The published research was real, the code reading was correct, and the arithmetic checked out. What
was missing is that **no published source writes down that a half-month direct debit does not
exist** — it is too obvious to anyone in the industry to be worth publishing. Published evidence
tells you what is established; discovery tells you what our code does; **neither tells you what is
obvious to a practitioner.** When a reading is odd against how the industry actually works, that is
the moment to say so and ask, not to build on it. Recorded as a standing habit in `CLAUDE.md`.

## The repair, anchored rather than invented

Ofgem's published expectation, already on the knowledge page: *"where a consumer account is in a
debit position, suppliers commonly add this amount to the Direct Debit and smooth the cost over the
next 12 months"* — the DD is set from an **annual** estimate, to return the account to zero over
twelve months. Not from one bill, and certainly not from a part-month stub.

So the initial DD should be **1/12 of an estimated annual cost** — and the company already holds an
EAC per customer, which is exactly the quantity a real supplier uses for this. That makes the repair
a re-wiring to an existing observable, not a new constant.

**Not done here.** It moves every DD figure, the arrears and bad-debt pipeline downstream of them,
and — once DD4b routes `large_increase` into churn — the book. It needs its own pre-registration and
a one-variable run, and it must not be bundled with the bill-shock baseline change landed today
(`259f5ae00`) or neither can be attributed.

## What this finding does not claim

Not that the review logic is wrong — it is well behaved from window 1 onward and cites SLC 27B. Not
that anyone was careless: the comment on line 155 says "initial estimate", so the author knew it was
a placeholder. The claim is that the placeholder is off by a factor of two for 85% of customers, that
this is the single largest driver of a published-band breach, and that the correct quantity is one
the company already has.
