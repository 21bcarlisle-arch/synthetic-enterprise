**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `W1_9_dsr_flex_markets`

# FINDING — the Capacity Market price has two homes that disagree by 4.7×, and it dwarfs the DFS leg

Found while fixing the DFS rate (`f9c647f4c`, promoted `1c0a19b2b`). **Not fixed here**, because
fixing it needs the published T-4/T-1 auction record and this pass has just finished documenting why
a partial correction to this exact formula is worse than the defect.

## The disagreement

| where | value | comment in the source |
|---|---|---|
| `company/market/flexibility_potential.py:36` | `_CAPACITY_MARKET_GBP_PER_KW_YR = 75.0` | `# T-4 auction 2023` |
| `company/market/ic_flexibility_revenue.py:43` | `_CM_DELIVERY_GBP_PER_KW_YR[2023] = 15.97` | sourced: "NESO auction results + `capacity_market_levy_2016_2024.md`" |

**One concept, two homes, 4.7× apart, and one of them cites a source for the year the other one
prices differently.** The sourced table runs 2016–2025 (6.44 to 22.50); `75.0` is above every entry
in it by 3.3× to 11.6×.

## Why no control caught it

`tests/architecture/test_a_domain_constant_carries_its_origin.py` has exactly the gate for this —
`test_no_concept_is_declared_in_more_than_one_module` — and it is blind here. It keys on the concept
name after stripping unit/period suffixes, so `CAPACITY_MARKET` and `CM_DELIVERY` are two concepts,
not one. **The gate that just forced the DFS duplicate off `KNOWN_CONCEPT_DUPLICATES` cannot see this
one, because the two homes disagree about the NAME as well as the value.** An abbreviation defeats it.

`tools.domain_constant_origins --list` separately reports `_CAPACITY_MARKET_GBP_PER_KW_YR` as
carrying **no origin at all** — a bare `75.0` with a comment, not a citation.

## Why it matters more than the thing I just fixed

`_estimate_capacity_revenue(flex_kw) = flex_kw * 75.0`, per household per year, unconditionally —
no auction outcome, no delivery-year lookup, no participation, no derating.

| EV + battery household, 12.4 kW rated | £/household/year |
|---|---|
| CM leg at `75.0` | **£930.00** |
| CM leg at the repo's own sourced 2023 price (15.97) | £198.03 |
| DFS leg, after this turn's correction (2024/25) | £6.22 |

**The CM leg is 150× the DFS leg and carries the less-sourced number.** I spent this turn on a
constant that was 737× wrong and moved £6; the constant next to it moves £930 on a value that
disagrees with the same repository's own sourced table.

There is also a **units/product question underneath the arithmetic**, which is why this is a research
item and not an edit: `_CM_DELIVERY_GBP_PER_KW_YR` is an availability price for a *derated,
auction-cleared, obligated* CM unit, and `_estimate_capacity_revenue` applies its stand-in to a
household's *rated* asset power with no derating factor and no auction. Even at 15.97 the formula
would be crediting a household with a CM agreement it never won. **The same rated-vs-delivered error
this turn established for DFS is live in the CM leg, and unlike DFS it has had no pass at all.**

## What done looks like

1. The published T-4/T-1 clearing price record, per delivery year, in **one** home — the sourced
   table in `ic_flexibility_revenue.py` is the candidate, and `dfs_published_record.py` is the shape.
2. A **derating factor** and an **agreement-won condition**, or an explicit refusal saying the model
   does not represent CM participation for domestic assets.
3. Widen `_concept()` in the duplicate gate so an abbreviation (`CM` ↔ `CAPACITY_MARKET`) does not
   split one concept into two — or accept that it cannot and say so in the gate's own docstring,
   because right now the gate reads as covering this and does not.

## What is NOT claimed

That `75.0` is wrong rather than mis-labelled. It may be a real figure for something else — a T-4
price in a different unit, a DSR-specific rate, or an aggregator's gross before derating. **Nothing
in `docs/market_research/` establishes it**, and its own comment names an auction year the repo
prices at 15.97. Which of those it is, is the research question.
