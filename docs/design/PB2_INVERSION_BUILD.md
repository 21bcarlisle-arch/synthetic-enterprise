# PB2 BUILD step 3 — the inversion: the book is now a measured subset of a world it lost most of

**Atom:** `PB2_opening_book_won_not_assigned` (lane `W2_customer_generator`, epoch 2).
**Level:** 1 → **3**. **Predecessors:** `PB2_OPENING_BOOK_DISCOVER.md` (the size and its anchor),
`PB2_UNWON_REMAINDER_FRAME.md` (the design, steps 1–4), `PB2_JOIN_KEY_BUILD.md` (step 1).
**Source ruling:** `docs/staging/in_progress/DIRECTOR_RULING_POPULATION_AND_BOOK_GROWTH_2026-08-11.md`.

This pass executes the FRAME's **steps 3 and 4** and closes the atom. Step 2 (the prospect
seam's observable set) is addressed in §6 as a bounded finding, not silently skipped.

---

## 1. What step 1 left, in its own words

`PB2_JOIN_KEY_BUILD.md` §4 was explicit about what it had not done, and it was right on every
count:

> **(b) the book ARRIVES BY ACQUISITION — won, never assigned** — **NOT met, and this is the
> gap.** The claim is a seeded shuffle over the stock, not a funnel outcome. …
> **(d)** … **met as a mechanism, not yet as a property of the running company.** `subset_verdict`
> is proven to fire on all five clauses, but nothing in the shipped run path calls it yet.

Read at this pass's HEAD, both statements had gone half-stale in an interesting direction, and
the diff between what step 1 predicted and what was actually there is the whole of §2.

## 2. What had changed underneath, and the defect that had not

**Exit (b) had been closed by a different atom.** PB3's net-new campaign landed between the two
passes: `simulation/net_new_acquisition.py::plan_growth_campaign` issues quotes against a
capital budget the company sets, resolves each one through the five-stage funnel with a real
credit check and the statutory cooling-off window, books the spend whether or not the quote
wins, and puts only survivors on the book. Measured on the shipped run: **930 quotes, 66 wins,
£112,740 spent**. That is a won book by any reading of the ruling's word, and it was already
live.

**Exit (d) was not closed, and was further from closed than step 1's note implies.** The
campaign that wins 66 accounts was *minting* a dwelling for every prospect it invented:

```
iter_prospects  ->  _draw_one(..., premise_joint=...)  ->  _draw_dwelling(customer_id, ...)
```

which is step 1's own false join key, arriving through the door step 1 had just closed on the
trickle. So the run's book had **68 domestic accounts at 68 premises named after those 68
accounts**, and there was no set any of them had been drawn out of. Measured before this change:

```
SYN-2021-001  premise = SYN-2021-001
SYN-2025-001  premise = SYN-2025-001
PROS-2016-0003 premise = PROS-2016-0003          (and 65 more)
book ∩ any stock = 0
```

The world contained exactly the homes the company had already acquired and not one more. **A
supplier that cannot lose a home it never approached has not won the ones it holds** — there was
nothing a subset control could have been pointed at, which is why nothing pointed at it.

## 3. What landed

### 3.1 The stock, drawn per year (`simulation/net_new_acquisition.py`)

`year_premise_stock(year, *, base_seed, n)` — the homes addressable in that year, drawn from
`premise_population.draw_premise` onto the same three published England housing-stock marginals
the premise population always used. Ids are namespaced `PSTK-{year}-{i:04d}`.

**Per-year is a fidelity requirement, not an implementation convenience,** and this is the
design decision in the pass. `draw_premise` reads `as_of` twice: the meter cadence is drawn
against `smart_read_share(as_of.year)` and the EPC lodgement uniformly over the ten years
before it. One stock drawn once at 2016 would model a decade in which no meter ever got smarter
and no certificate was ever re-lodged — **strictly less faithful than the per-acquisition mint
it replaces**, which is the one direction R13 forbids. Proven, not asserted:
`test_a_years_stock_is_drawn_at_that_years_as_of` measures the smart share at each end of the
decade and requires 2025 > 2016.

The id namespace is load-bearing for the same reason step 1's `foreign_world` clause exists:
`draw_premise_population` mints `P0000..P{n-1}` for every seed and every `as_of`, so a bare
`P0007` names a **slot**, not a dwelling. Year-scoping makes the ten-year union a genuine stock
rather than ten overlapping ones.

### 3.2 The claim, positional (`iter_prospects`, `iter_acquisition_events`)

Both drawn streams gained a claim into that stock. Prospect `i` of year `Y` is a home **at**
slot `i - 1` of `Y`'s stock; acquisition `i` of year `Y` likewise, via the new per-year
`premise_stock_fn`.

**Positional, deliberately, and not shuffled.** Stock members are exchangeable — each is an
independent draw from the same raked joint keyed on its own id — so slot `i` is already a
uniform sample and a shuffle buys nothing. It would cost something real, and step 1 said so:

> **2026-08-24 — book membership is not stable under stock growth.** … the shuffle is seeded on
> the stock size, so growing the stock re-rolls which premises were won. … The resolution is not
> a cleverer shuffle, it is **step 3**.

That debt is **paid**: `test_membership_is_stable_when_the_stock_grows` shows `PROS-2019-0007`
sits at `PSTK-2019-0007` whether the stock is 100 homes or 4,000, and asserts the CONTRAST —
that step 1's flat shuffled claim does *not* have the property — so the test cannot quietly stop
testing what it says it tests.

The two claim shapes are **mutually exclusive and raise if both are supplied**. They are one
mechanism with two shapes, not two mechanisms.

### 3.3 The wiring (`simulation/live_population.py`)

- `world_premise_stock(seed)` — the union across `CAMPAIGN_YEARS`, 4,400 homes.
- Each year's stock is split once: the campaign claims `[0, PROSPECTS_PER_YEAR)`, the Profile-B
  trickle claims the reserved tail. **The two streams cannot claim the same home by
  construction**, and `test_the_two_streams_never_claim_the_same_home` pins the arrangement
  because the two slices are computed in different functions and could drift apart.
- `_drawn_trickle(seed)` — ONE accessor replacing three identical `draw_population(...)` call
  sites (`live_population`, `_pre_growth_book`, `live_premises`) that had to agree on every
  argument or the run would hold dwellings for accounts not in its own book. The campaign memo's
  own comment records paying for exactly that class of drift once already.
- `book_subset_verdict(seed)` and `_record_subset_verdict` — the control **called on the shipped
  path**, its verdict published to `docs/observability/book_subset_verdict.json` for readers in
  a later process, counts only (the remainder's *membership* is what the wall forbids leaking).

### 3.4 The measured result

```
ok                 True        failures           []
n_stock            4400        n_book_domestic    68
n_remainder        4332        realised_take_rate 0.0155
n_founders         18          double_won         []
```

Sixty-eight homes won out of four thousand four hundred the world offered. **1.5% take rate**,
and 4,332 households this supplier never signed.

### 3.5 The blast radius, bounded and checked

The claim reads a pre-drawn sequence and never touches either stream's `rng` (C-S2), and the
funnel is seeded on the prospect's own id and date. So:

- segment, commodity, band, EAC, payment method, region and the in-market date are
  **byte-identical** with and without the stock (`test_the_stock_claim_does_not_perturb_the_prospect_stream`);
- **the same 66 prospects win** (`test_the_same_prospects_win_with_and_without_the_stock`);
- the book is still 86 accounts and the campaign record is unchanged.

What changed is which house each of them lives in. Every figure measured before this change was
measured on the same world.

## 4. The controls, and the one my own change broke

Twenty-nine tests in `tests/simulation/test_opening_book_subset.py` (13 new) and two new seam
controls in `tests/simulation/test_live_population_seam.py`.

**The load-bearing falsifier is `test_the_shipped_control_reds_without_the_stock`**: it runs the
same predicate against the seam as it shipped *before* this step — real generators, one argument
dropped at each of two call sites — and requires `ok=False, failures=['outside_stock']`. If it
ever goes green the control has stopped testing subset and started testing that two sets exist.

Fail-open and fail-closed both proven: the verdict REDs on `draw_inactive` when the population
draw is off (a control reporting green on "nothing to check" would have read green on every run
this atom ever made), and both the prospect pool and the trickle reserve **raise** rather than
truncate when the stock cannot cover the draw.

### 4.1 An invariant that was true only because of the defect

`simulation/household.py::make_household` carried a guard reading *"drawn household X handed to
customer Y — one home, one id"*, and this change made it raise on **22 tests** across
`test_run_phase2b_event_log.py`, `test_value_chain_credit_feed_wiring.py` and
`test_run_phase2b.py`.

The guard was correct. Its independence was not. `draw_premise` builds its household with
`customer_id=premise_id`, so comparing the household's label against the customer id was
independent evidence **only while premise_id == customer_id** — that is, only because of the
false join key this atom exists to remove.

Repaired, not weakened, at the seam that holds both facts: `live_drawn_households()` now
relabels each household to the customer it belongs to, which is what the field is named after.
The cross-path property the guard could no longer see from inside `make_household` — that
`live_premises()` and `live_population()`, two independent re-draws, agree on which accounts
exist — is asserted **directly** in
`test_every_account_in_the_book_has_exactly_one_dwelling_of_its_own` rather than inferred from
an id collision.

### 4.2 A HEAD red this pass inherited and fixed

`test_resolve_book_flag_on_additively_carries_syn_cohort` (×3 parametrisations) was **already
failing at clean HEAD** — verified in a detached worktree at `e79ee6f96`, not inferred. It
asserted every added account id starts with `SYN-`; PB3's campaign had since started adding
`PROS-` wins, so it described a book with one drawn half after the second half shipped. Fixed
to accept both prefixes while keeping the SYN cohort a separate assertion, which is what makes
the test able to fail on its own named mutation.

## 5. The per-premise draw price, measured

`PB1_POPULATION_TARGET_AND_ITS_PRICE.md` §(b) and this atom's FRAME §5 both record that **no
measured price for a drawn premise existed anywhere in the repo**, and both correctly refused to
infer one from the 860 bytes AO12 measured for a *customer*. This pass needed the number and so
measured it:

| n | wall time | RSS delta | per premise |
|---|---|---|---|
| 200 | 0.01 s | 256 KB | — (below noise) |
| 1,000 | 0.04 s | 384 KB | 393 B |
| 4,400 | 0.16 s | 1,792 KB | **417 B** |

The shipped stock is 4,400 premises: **0.16 s and 1.8 MB per run**. This does not resurrect the
withdrawn affordability verdict — that verdict was about the *book* reaching `settlement_build`,
and the frame's structural claim stands: the stock can be large precisely because an unwon
premise never reaches the expensive stage. What it does is replace an UNKNOWN with a number, at
this scale, from an instrument rather than a ratio.

## 5a. Exit (a), and the size the director has since named

Exit (a) — *a proposed opening size with its plausibility case anchored to something external* —
was discharged by the DISCOVER pass at **3,217**, anchored to Ofgem's £130-per-domestic-customer
Minimum Capital Requirement and the company's own opening treasury, with **465** as the
fail-closed interim from AO12's measured `settlement_build` ceiling. Nothing in this pass changes
that document.

What has changed is that the director has since named a number himself (2026-08-24 console):
*"Grow residential toward 200, earned through the funnel as you've just built it."* **That is a
curriculum value and it is his (R13)** — it supersedes the agent's proposal as the operative
target, and this pass neither adjusts anything toward it nor treats it as a gate (R12: a target
is not a dial on the mechanism).

The shipped book is **86**, and the reason it is not ~200 is on the record and is not commercial:
the campaign's own notes say *"600.0 customer-years is THIS MACHINE's budget (60% of the 465
measured in AO12's scale probe), not a commercial limit. The book below is smaller than the
supplier's balance sheet supports."* Four of the ten years are settlement-bound. That is the
first bullet of §6.

## 6. Findings raised, not fixed (SELF_INTERRUPT_DISCIPLINE)

- **FRAME step 2 — the prospect seam's observable set — is NOT built, and the wall is currently
  held by a stronger rule than the one step 2 proposed.** §2.1 proposed arguing which premise
  attributes a supplier may see before it quotes (region, cadence, EPC band yes; `nssec`, tenure,
  the `Cohort` never). Today the company sees **none** of them: a prospect crosses only as
  `to_customer_dict()`, which omits `premise` and `cohort` by construction, and the funnel's
  outcome is drawn rather than modelled on the household. That is safe but less faithful — a real
  supplier does target. It needs the fidelity-oracle check §2.1 asked for before anything is
  exposed, and it belongs to whoever builds targeting.
- **The union over-counts distinct homes.** A house in the market in 2016 and again in 2019 is
  two members of the stock, because nothing carries a dwelling's identity across years. This is
  the same simplification `iter_prospects` already made and it is visible in the remainder as a
  slight over-count. Fixing it needs a persistent dwelling register.
- **The book is settlement-bound, not market-bound, from 2022.** The campaign's own record says
  so in four separate notes: *"600.0 customer-years is THIS MACHINE's budget … not a commercial
  limit."* The director named this exactly on 2026-08-24 — *"if our own code binds growth rather
  than the simulated economics, say so on the site and fix it if it's cheap"* — and it is the
  reason the book is 86 rather than the ~200 the balance sheet supports. **Surfacing it on the
  site is the next thing this lane owes**, and the record it needs is already published.
- **A test wrote a mutant's verdict to the repo's published record.** `_record_subset_verdict`
  fires whenever a campaign resolves for the first time in a process, so the falsifiers in this
  pass — which deliberately resolve WRONG worlds — overwrote
  `docs/observability/book_subset_verdict.json` with `ok=false` and all 66 winners listed as
  `outside_stock`. Caught by reading the file rather than by a control. Fixed here by redirecting
  the path in the fixtures, but the general shape is not fixed: **any test that resolves a
  campaign writes to a published path**, and the same is true of `book_growth_campaign.json`.
  A run-artefact writer that a test can reach is a published figure a test can author.
- Preconditions carried forward from the DISCOVER pass, still owed and untouched here: the draw
  saturates silently above `lambda ≈ 745`; the `SYN` key set diverges from the static roster; the
  curriculum-arms-from-disk / code-arms-at-HEAD asymmetry.

---

— Worker tick, 2026-08-24. BUILD draw on `PB2_opening_book_won_not_assigned`, FRAME steps 3–4.
