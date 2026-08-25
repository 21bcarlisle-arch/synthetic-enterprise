# What a GB domestic supplier is allowed to earn — the price cap's EBIT allowance

**Regulation commons.** The regulatory TEXT is shared and readable by every lane; each lane's
READING of it is independently owned (`REGULATION_COMMONS_DOCTRINE`). This file is the TEXT and
the published numbers. The company's reading lives in `company/pricing/` and may be wrong.

**Why it was fetched.** Director, 2026-08-25: *"there has to be a baseline to beat. Average
behaviour is the control — the same book run by a supplier applying flat rules with no
per-customer view. Without that comparison, 'it performed well' means nothing."* The control in
`tools/couple_value_based_pricing.py` is this company's own flat rule, `TARGET_MARGIN_GBP_PER_MWH
= 2.00`. Whether that flat rule is anywhere near AVERAGE BEHAVIOUR was an open question and could
not be settled from inside the tree — nothing under `company/` or `saas/` reads any external
figure for what a supplier earns. The Default Tariff Cap contains one, published, and it is the
regulator's own answer to exactly that question.

**Sources, fetched not recalled** (HARNESS may fetch published sources; the bytes become
documentation and, through this commons, a reading the company owns — never a runtime input it
reads directly):

- Ofgem, *Price Cap — Decision on amending the methodology for setting the Earnings Before
  Interest and Tax (EBIT) allowance*, published **25 August 2023**.
  <https://www.ofgem.gov.uk/sites/default/files/2023-08/Price%20Cap%20-%20Decision%20on%20amending%20the%20methodology%20for%20setting%20the%20Earnings%20Before%20Interest%20and%20Tax%20(EBIT)%20allowance.pdf>
- Ofgem, *Amending price cap methodology for Earnings Before Interest and Tax (EBIT) allowance —
  decision* (landing page).
  <https://www.ofgem.gov.uk/decision/amending-price-cap-methodology-earnings-interest-and-tax-ebit-allowance-decision>

---

## A. What the allowance IS, in the regulator's words

> "The default tariff cap ("the cap") protects customers under a standard variable tariff (SVT)
> by ensuring that customers pay no more than is necessary for an efficient supplier to recover
> its costs **and earn a reasonable level of profit**." — Decision, cover page

> "This decision concerns the profit margin allowed for in the price cap, known as the Earnings
> Before Interest and Tax (EBIT) allowance. Our decision sets an EBIT allowance that we consider
> is **high enough for a notional supplier to finance its activities, but where customers pay no
> more than necessary**." — Executive Summary

That is the sentence that makes this usable as a baseline: it is a regulator's estimate of what a
*notional efficient supplier* earns per customer, published, and independent of anything in this
tree.

## B. The old methodology — 1.9%, and what it was 1.9% OF

> "When the cap was developed in 2018, Ofgem incorporated the **CMA's 1.9% EBIT estimate** as a
> separate allowance within the cap. This percentage is applied to the sum of the cap allowances
> for **wholesale costs, network costs, policy costs, operating costs, payment method uplift, and
> an adjustment allowance**. This broadly means that the allowance scales with overall cap levels
> (**excluding headroom, VAT and the EBIT allowance itself**). The EBIT allowance level is updated
> quarterly when changes to the cap are announced." — §1.2

> "The EBIT allowance was introduced as part of the price cap to deliver a normal rate of return
> for an efficient supplier serving standard variable tariff (SVT) customers. It was based on the
> **Competition and Markets Authority's (CMA) 2016 analysis** of what a normal rate of return
> should be in the retail market." — §1.1

**The base matters and is a live trap.** 1.9% is not 1.9% of the bill: it excludes headroom, VAT
and EBIT itself. Quoting "1.9% of the bill" overstates it.

## C. The decided methodology, from 1 October 2023

> "The revised EBIT allowance is calculated based on the multiplication of two components:
> **capital employed and cost of capital**. We have set capital employed at **£358 per customer**
> for the upcoming cap, for a household with typical consumption. This is the sum of fixed
> assets, working capital and collateral. We have set cost of capital at **12.3%** … In
> combination, this leads to an indicative **EBIT allowance of £44 per customer (annualised) for
> cap period 11a**. This compares with a **£34 for the same period under the previous
> methodology**." — Executive Summary

> "This decision confirms our proposal for altering the EBIT allowance methodology such that is
> has a **fixed component, that does not change when the cap is updated, and a variable component
> that scales with the overall cap level**. … resulting in the share of the EBIT allowance within
> the cap **falling as prices increase**." — Executive Summary

> "The scope of decision includes setting the methodology for calculating the EBIT allowance in
> the cap, which is used for calculating the allowance **from 1 October 2023 onwards**." — §1.3

### The decided numbers (Appendix 3, Table 13 — "Decision value" column, at Benchmark Consumption)

| Parameter | Decision value |
|---|---|
| Capital employed | **£368.29** |
| — of which working capital | £102.30 |
| — of which collateral | £176 |
| — of which fixed assets | £90 |
| — of which RO ringfencing | £71.16 |
| Cost of capital | **12.26%** |
| Dual-fuel annual bill at benchmark consumption in 11a (**ex. EBIT, headroom and VAT**), Direct Debit | **£1,817** |
| **Fixed return** | **£19.76** |
| **Variable component %** | **1.3975%** |
| **Variable return in 11a** | **£25.40** |

**Read the table, do not re-derive it.** The four "of which" rows sum to £439.46, not to the
£368.29 above them; the decision does not present them as an addition and this file does not
turn them into one. The published components are recorded as published.

**Total allowance for 11a: £19.76 fixed + £25.40 variable = £45.16 per customer per year**,
against a dual-fuel benchmark bill of £1,817 excluding EBIT, headroom and VAT — **about 2.5%**.
The £44 in the Executive Summary is the same figure before the Appendix-3 updates.

The variable component's 1.3975% is described as "**Proportion of capital employed which is fixed
assets**" — it is a share of the cap level, not a margin on revenue, and calling it a margin
would misstate what it scales with.

## D. The fidelity gap this opens against the tree

| | the regulator | this company |
|---|---|---|
| profit allowance per customer per year | **£45.16** (dual fuel, benchmark consumption, DD, 11a) | **£6.20** (`TARGET_MARGIN_GBP_PER_MWH = 2.00` × 3.1 MWh, electricity only) |
| how it scales | fixed £19.76 **plus** 1.3975% of the cap level | purely per-MWh |
| basis | capital employed × cost of capital | none stated |

**The comparison is not like-for-like and the difference is named rather than adjusted away.**
The £45.16 is DUAL FUEL at benchmark consumption; this book is predominantly electricity-only, and
a single-fuel customer's capital employed — collateral, working capital, fixed assets — is lower
than a dual-fuel customer's. The decision does not publish a single-fuel split at this level, so
none is invented here. What survives the caveat is the ORDER: even on the most conservative
single-fuel reading, the flat control earns a fraction of what the regulator allows an efficient
supplier to earn, and the gap is large enough that the shape of the answer does not depend on the
split.

**Why that matters more than it looks.** `tools/couple_value_based_pricing.py` scores a
value-based pricing arm against that flat rule and reports it moving the median bill by +52%. If
the control is charging well under the regulated allowance, then a large part of that +52% is the
arm walking the control UP TO NORMAL — not inference beating average behaviour. The director's
frame requires a baseline that is genuinely average; this file is the external evidence that the
current one is not.

## E. What this file does NOT license

- **It is not a target.** R12: this is a published external figure for what a notional supplier is
  allowed to earn, and it must not become a number the company's own margin is tuned toward. It
  belongs in a CONTROL ARM — "what would an average supplier have charged" — where it is a
  comparator, never in the live pricing path as a goal.
- **It is not this company's cap.** The Default Tariff Cap applies to standard variable and
  default tariffs. A fixed-term contract a customer actively chooses is a different instrument,
  and the EBIT allowance is an input to the cap's construction rather than a limit on any
  supplier's margin.
- **It is not a per-fuel figure.** See §D.
- **It is 11a (Oct–Dec 2023).** The allowance is recalculated as the cap moves; the fixed
  component does not, the variable one does. Any use in the tree must carry its period (R14: no
  financial figure without its clock).
