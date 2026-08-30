# A46 — the priced menu: what each publish interval buys, and the one column that does not move

*Delivery seat, 2026-08-30. `A46_book_depth_is_a_curriculum_question`.*

**Director, 2026-08-28 (P9):** *"Book depth bounds every comparison. Only 37 accounts carry five or
more renewals, so nothing can compound. Book age moves the P&L, which makes it curriculum and
therefore the director's — flagged, not delegated."*

This is the menu that ruling asked for, and **it is not the menu I expected to be writing.** The
atom was framed as "how much book depth does each publish interval buy" — a table of wall-clock
against renewals. It is that. But it has a second column, and the second column is flat:

> **At every publish interval on this menu, the number of accounts the method could actually price
> is ZERO.** Not small — zero, and zero for a structural reason that no ceiling reaches.

So the decision this menu supports is not the one it was commissioned to support, and saying that
plainly is the whole of its value. **My recommendation is at §6, and it is to change nothing about
the publish interval.**

---

## 1. How a ceiling turns into a book, which is the arithmetic everything below rests on

`SETTLEMENT_CUSTOMER_YEAR_BUDGET` is a budget in **customer-years of settlement**, and the
allocation rule that spends it (2026-08-29) is a single uniform sampling fraction:

    rate = (ceiling − opening book) / campaign demand          [clamped to 0..1]

Read live from `docs/observability/book_growth_campaign.json`, never restated here:

| quantity | value | what it is |
|---|---|---|
| opening book | **778.1 cy** | the founders, settled before the campaign gets a look in |
| campaign demand | **2,358.4 cy** | what settling all 505 funnel wins would cost |
| funnel wins | **505** | accounts the company actually won across 2016–2025 |
| full supply | **3,136.5 cy** | the ceiling at which `rate` reaches 1.0 |

**A ceiling above 3,136.5 buys nothing.** That figure has moved since it was last written down —
`SETTLEMENT_CEILING_REMEASURED_2026-08-29 §6` says ~2,780, computed against the 380 funnel wins of
the time. Change 1 took funnel wins to 505, so the top of the useful range rose with it. It is read
from the record here rather than quoted, which is why it is right.

The projection is **reconciled, not trusted** — and the reconciliation is in a *derived* artefact,
not in the measurement. `docs/observability/settlement_ceiling_slope_20260829.json` is the
measurement record and its top-level keys are `points / marginal / publisher / recommendation`;
there is no `menu` in it, and an earlier draft of this section cited one. The menu is computed by
`tools/settlement_ceiling_probe.py::menu` from that record's points and written to
`docs/observability/settlement_ceiling_menu_20260830.json`, whose
`menu.projection_reconciles_with_the_record` reads:

    {"at_budget": 1200.0, "projected_wins": 90, "record_wins": 90, "agrees": true}

A projection that had drifted from the rule it models would make every row below arithmetic about a
rule that is not running, and that field is what would catch it.

## 2. The menu

*Points measured by `settlement-ceiling-slope.service`, 2026-08-30, with the `sim_runner` hold
placed (see §8 for what the hold did and did not cover). `time_share` 0.9 of the interval;
`rss_share` 0.5 of a 24,032 MB guest. Reproduce — note the explicit `--json`, because the default
output path is `settlement_ceiling_probe.json` and re-running this without it overwrites a
different artefact:*

    python3 -m tools.settlement_ceiling_probe \
      --reanalyse docs/observability/settlement_ceiling_slope_20260829.json \
      --menu-intervals 1500 1800 3600 7200 14400 --time-share 0.9 --rss-share 0.5 \
      --json docs/observability/settlement_ceiling_menu_20260830.json

**Every cell below is marked M (measured on this box) or P (projected by arithmetic, no run).** The
table was built by running that command; the interval half came back undecidable and is reported as
it came back, not interpolated.

### 2a. What a ceiling buys

| ceiling (cy) | run wall clock | peak RSS | accounts booked | sample rate | marginal cost of the next cy | accounts the arm could price |
|---|---|---|---|---|---|---|
| **1,200** *(shipped)* | **928.6 s** (M, clean) | **3,952.4 MB** (M, clean) | **90** (M) · 90 (P) | 0.1789 (M) | *one clean point; no slope* | **0** (M) |
| **2,000** | 2,097.6 s (M, **contaminated**) | 6,784.5 MB (M, **contaminated**) | 261 (M, contaminated) · 262 (P) | 0.5181 (P) | *one clean point; no slope* | **0** (M) |
| **3,136.5** *(full supply)* | — | — | 505 (P) | 1.0 (P) | *one clean point; no slope* | **0** (M) |
| **above 3,136.5** | — | — | 505 (P) — **buys nothing further** | 1.0 (P) | n/a | **0** (M) |

**The 2,000 row is a single contaminated observation and is explicitly barred from the slope.** The
artefact's own words: `campaign_record_agrees: false` — *"another process wrote
book_growth_campaign.json during this run (it said 1195.4), so this point's committed customer-years
are not its own"*. It is reported because a contaminated point is still a valid single observation
of wall clock and RSS; it is not differenced against the 1,200 point, and no marginal cost is
interpolated from the pair. `marginal` in the artefact is `[]`.

The 3,136.5 row and the "above" row need **no run at all** — they are the funnel-supply arithmetic
of §1: opening book 778.1 cy + campaign demand 2,358.4 cy = 3,136.5 cy at which `rate` reaches 1.0
and all 505 funnel wins are settled. That is why they are the only projected rows worth having: they
bound the top of the range for free, which is why the third probe point at 2,800 was dropped.

### 2b. What a publish interval affords — and why this half is empty

| chosen publish interval | ceiling it affords | binding bound |
|---|---|---|
| 25 min (1,500 s) | **not decidable** | — |
| 30 min (1,800 s) | **not decidable** | — |
| 60 min (3,600 s) | **not decidable** | — |
| 120 min (7,200 s) | **not decidable** | — |
| 240 min (14,400 s) | **not decidable** | — |

Every row carries the same reason, verbatim from `menu.options[*].reason`:

> *"1 CLEAN point(s); a slope needs at least two. A contaminated point is still a valid single
> observation and is reported above — it is only barred from the slope."*

**This is a result about this box, not a missing table.** Turning a chosen interval into an
affordable ceiling needs a cost *per customer-year*, and a cost per customer-year needs two clean
points. We have one. The honest menu says so at every row rather than drawing a line through one
point and an asterisk.

It does not change the recommendation, and that is the thing worth noticing: §6 never rested on this
half of the table. It rests on the last column of §2a, which is **zero at every ceiling** for a
structural reason no interval reaches — and that column is measured, not projected.

## 3. The column that does not move, and why no ceiling reaches it

`site/data/value_arms.json` → `decisions.who_the_method_has_priced` — the arm's own published
verdict, read by the menu rather than argued in it:

> **The method has never priced a customer the company won.** Every renewal it priced belongs to one
> of 10 accounts the company was founded with; the other 158 accounts the world offered a renewal to
> have never had one reach the arm.

It is a **gate, not a book size**. A won or drawn electricity record carries `tariff_type` present
and `None`; the arm admits only `UPLIFTABLE_TARIFF_TYPES = {fixed, pass_through}`. The founding nine
pass only because their record *omits* the field and takes the `"fixed"` default. **No number of won
households changes what that guard reads**, so there is no ceiling at which the first one is priced —
which is exactly why this column is flat across every row of §2 while the account column rises.

**What is owed is not a relaxed guard.** The world has no standard-variable product, so a won
household's product was never *decided* rather than forgotten; the repair is that product, drawn
from the published domestic fixed/SVT split, and it makes the in-scope surface **smaller** as a share
of the book, not bigger (`DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md`, settled 2026-08-28).
That is a baseline-world change, which R13 puts on your side of the wall, not mine.

## 4. Which published comparisons stay bounded until it lands — and which the ceiling *does* free

This is the half of the menu that decides whether the interval is worth spending, so it is split
honestly rather than argued in one direction.

**Bounded by the GATE. No publish interval on this menu moves any of these.**

| comparison | its binding n today | what would move it |
|---|---|---|
| does the method rank value better than chance (`method_skill`) | **6 decisions, 5 accounts**; null interval **0.133–0.867**, p=0.47 | the SVT product |
| renewals the arm priced, of 1,369 offered | **20 (1.46%)** | the SVT product, and gas/term-0 scope |
| the arm's £ effect against its noise floor | spread **1.42×** the point estimate | more *priced* decisions, not more accounts |

**The method-skill row is the one that matters**, because it is the measurement of the thing the
enterprise value actually is. Six decisions cannot distinguish the method from a coin. Booking 400
more accounts leaves it at six.

**Bounded by the CEILING. These the menu can buy, and they are real.**

* **Year coverage.** Before the allocation fix nine of ten years booked zero and PB3's coupled-triad
  gap was scored on **n=1** with `gap = 1.0` — an identity, not a measurement. It is now scored on
  ten years at 0.830. Further ceiling buys *depth* within each year rather than years.
* **Book depth.** Accounts carrying five or more renewals: **43** today. Your P9 figure of 37 was
  taken before the allocation fix; the count is read from the run, not from that ruling.
* **Sample rate.** The published book is a **17.89% sample** of what the company won. Every
  per-account figure on the site is a sample statistic, and a higher rate narrows every one of them.

**The honest summary of the split: the ceiling buys PRECISION on comparisons that already exist.
It buys NOTHING on the comparison that decides whether the method works.**

## 5. What the interval costs, said in the terms the cadence is actually in

The time bound is a **choice, not a measurement**, and the reason is structural: the fallback
interval is `suite_duration_watch.PUBLISH_CADENCE_SECONDS`, which is *defined* as the median
inter-arrival of run-complete markers. Run duration sets marker inter-arrival. So a ceiling argued
against the measured cadence raises its own bound, in the flattering direction, and silences the
gate-speed alarm on the way past. Every row in §2b is therefore priced against a **chosen** interval,
and the menu carries `binding_bound_is_evidence` so a reader can tell a bound from a preference —
though on this run no row got as far as emitting it, because no row was decidable.

The memory bound is the one that is evidence — the guest's size is a fact this process cannot
influence. It is **not comfortable**: `oom_kills_total` on this box has gone 157 → **187** since the
2026-08-29 measurement, so the kernel has picked a victim thirty times in a day. A ceiling set near
the memory bound is a ceiling that buys OOM kills.

## 6. The recommendation

**Change nothing about the publish interval, and do not raise the ceiling on this evidence.** I am
recording this and proceeding; it is reversible in a line, and the reason to stop is not that the
menu is unclear.

Three reasons, in the order they bind:

1. **The interval buys precision, not the answer.** §4 is the whole argument. Doubling the interval
   to 60 minutes buys accounts and buys **zero** additional decisions the method can be scored on.
   Spending your only real budget — the cadence at which this company reports to you — on a column
   that does not move is the wrong trade at any price.
2. **The gate is the decision that unlocks the menu, and it is also yours.** The standard-variable
   product (`DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md`) is a baseline-world change. Until it
   lands, this menu's second column is zero at every row; after it lands, the menu is worth
   re-running and the interval question becomes a real trade with a real numerator. **That is the
   ruling I would ask you for next**, and it is filed, not asked here.
3. **Half the unpriced surface is not the gate at all.** Of the 1,349 renewals the arm did not
   price, **687 (51%) are deliberate scope** — term 0 has no prior term to price against, and the
   arm has never been fitted to gas. Opening the product gate reaches 662; it does not reach those.
   A ceiling decision taken as if the gate were the only constraint would over-buy.

**What I am doing without you:** leaving `SETTLEMENT_CUSTOMER_YEAR_BUDGET` at 1,200, keeping the
publish interval where it is, and putting the measured basis on the page in place of the
`NOT YET KNOWN` placeholder the book-growth page has been carrying. **What I am not doing:** touching
the product label, which is R13 curriculum and is yours.

If you disagree, the menu in §2 is the priced version of every alternative and the change is one
constant.

---

## 7. What I predicted and what happened

The four predictions were filed before any point was measured, in
`docs/staging/WORKER_PREREGISTRATION_WHAT_THE_CLEAN_CEILING_SLOPE_MUST_SHOW_2026-08-29.md`, and they
are marked **in that file, beside themselves**, right or wrong. The one worth repeating here is
**prediction 4**, which said the honest output would be *"not a new number but a table mapping chosen
interval → affordable ceiling, put in front of the director."* That held in form and was **too
generous to itself in substance**: I predicted a table of intervals and ceilings, and a table of
intervals and ceilings is exactly the artefact that would have let you spend the cadence for nothing.
What made this menu a decision rather than a table was the column I had not thought to put in it —
the one supplied by a *different* finding, landed the same night, about who the arm has ever priced.

**A menu is only priced if it carries the column that does not move.**

## 8. Contention, recorded because it bounds what these numbers are

The `sim_runner` hold was placed for both points, and **it held for only one of them**. The
artefact puts `campaign_record_agrees: false` on the 2,000 point — *"another process wrote
book_growth_campaign.json during this run (it said 1195.4), so this point's committed customer-years
are not its own"* — so that point is `clean: false` and barred from the slope, and one clean point
is not a slope. **No slope is reported anywhere in this document**; §2's marginal-cost column reads
*"one clean point; no slope"* for that reason.

Nor was the box quiet: another lane's regression suite was running throughout, so the absolute wall
clocks are upper bounds on a quiet box and should not be quoted as the cost of a run. The hold
covered the producer, which is the writer that contaminated the previous attempt — it was never a
claim that the box was idle, and on the 2,000 point it was not even a claim that the producer was
the only writer.
