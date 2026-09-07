**Severity:** BLOCKING · **Lane:** F_risk_compliance · **Epoch:** unassigned · **Atom:** `unminted`

# The CM levy artefact's stated derivation does not reproduce its own 2018 row

`docs/domain_artefact_library/regulatory/capacity_market_supplier_levy.json` states its own
derivation in `basis.derivation`:

> "Annex 9 publishes GBP per customer per year at a 3.1 MWh benchmark consumption; these figures
> are that divided by 3.1"

Run that statement against the file's own rows — the per-customer figure is in each row's `note`
— and it reproduces eight of nine. It does not reproduce 2018:

| OY | £/cust/yr (row note) | ÷ 3.1 | `gbp_per_mwh` (row) | implied divisor |
|---|---|---|---|---|
| 2017 | 3.41 | 1.10 | 1.10 | 3.100 |
| **2018** | **11.36** | **3.66** | **3.67** | **3.095** |
| 2019 | 14.85 | 4.79 | 4.79 | 3.100 |
| 2020 | 18.18 | 5.86 | 5.86 | 3.102 |
| 2021 | 14.49 | 4.67 | 4.67 | 3.103 |
| 2022 | 10.44 | 3.37 | 3.37 | 3.098 |
| 2023 | 17.61 | 5.68 | 5.68 | 3.100 |
| 2024 | 22.54 | 7.27 | 7.27 | 3.100 |

(2016 is `estimated` and carries no per-customer figure, correctly.)

**This is not a changing benchmark.** The obvious innocent explanation would be that Ofgem's
typical domestic consumption value moved during the window, so a single divisor cannot be right
for every year. It does not survive the column on the right: every other year's implied divisor
rounds to 3.100 and only 2018's does not. It is one row, and one of its two numbers is wrong.

## Which one, and I cannot say

Either the per-customer figure should be £11.38 (3.67 × 3.1 = 11.377) or the levy should be
£3.66. Settling it needs Ofgem Annex 9 v1.8, sheet "1b Historical level tables", CM row, read at
2018/19 — which is the one thing not in this repo. **An honest gap with a named reason, not a
number picked because a number was needed.** Do not resolve this by choosing whichever figure
makes a control green.

**The error predates the commons.** `docs/market_research/capacity_market_levy_2016_2024.md`
line 13 has carried `| 2018/19 | £11.36 | **£3.67** |` since Phase 30a, and the artefact was
created from that note by a51 on 2026-09-07. So this is not an a51 transcription slip — it is the
Phase 30a research note's own internal inconsistency, promoted into the regulation commons intact
and now, since this turn, load-bearing in BOTH lanes rather than one.

## What it is worth

£0.01/MWh on obligation year 2018/19, which is **0.27% of that year's CM rate**. On the current
book the 2018 CM line is £505.57 (`docs/reports/run_output_latest.json`), so the exposure here is
of order £1.38 — negligible, and said plainly rather than inflated. It is filed BLOCKING for the
reason clause 2 gives and not for its size: an artefact in the regulation commons whose own
stated derivation does not reproduce its own row is an untrustworthy instrument, and it is
untrustworthy for all nine rows until someone reads Annex 9, because the reader has no way to
know 2018 is the only one. At the 5 TWh supply scale this module is written to price, the same
£0.01/MWh is £50,000/yr.

## How it was found, including the prediction that was wrong

Found by the poison round on the control this turn added
(`test_the_sim_cm_levy_reader_serves_the_commons`, in
`tests/architecture/test_year_keyed_rate_table_census.py`), not by reading the artefact.

**The prediction was: "edit a figure in the commons and the equality leg fires." It did not.**
Recorded here beside the result rather than quietly revised. It cannot fire, and the reason is
structural: after this turn both `simulation/policy_costs.py` and
`company/regulatory/capacity_market.py` load that file, and so does the control, so all three
read the same bytes and agree by construction. That is an EQUIVALENCE, not a missing test at
that seam — it is what the load is FOR — but it has a consequence worth stating: **wiring the
second lane to the commons doubled the blast radius of a wrong figure in it.** Before today a
bad row in the artefact was wrong in one lane and disagreed with the other; now it is wrong in
both, silently, and the annual report's live reconciliation of the two readings would show
nothing. That is the correct trade (one law beats two, and the RO incident cost £486,458.88 to
learn it), but it moves where the remaining risk lives, and it moves it onto this file.

Chasing that is what surfaced the 2018 row: with no control able to check the artefact's values,
the only check available is the artefact's own stated derivation, so I ran it.

## What is next

1. **Fetch Annex 9 v1.8 sheet "1b", CM row, 2018/19** and settle which of £11.36 / £3.67 is the
   transcription. Correct the artefact AND `docs/market_research/capacity_market_levy_2016_2024.md`
   — they are the same slip in two places and fixing one leaves the other to be re-promoted.
2. **Then pin the derivation as a control, not as a comment.** Move the per-customer figure out
   of each row's prose `note` into a structured `gbp_per_customer_year` field, and assert
   `gbp_per_mwh == round(gbp_per_customer_year / 3.1, 2)`. That is the CCL shape — the commons
   holds the publisher's own unit and the control performs the conversion, so the divisor is
   under test rather than assumed — and it is the only leg that could have caught this without a
   human noticing. It would go red on 2018 today, which is why it is step 2 and not step 1.
3. It does **not** need the sim/company wiring to be undone. Both lanes serving one wrong number
   is strictly better than two lanes serving two different numbers, one of which was also wrong.
